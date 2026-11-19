"""Prepare CRSP and SEC panel artifacts."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import pandas as pd

from free_foundations.artifacts.atomic import atomic_copy, atomic_parquet, sources_lock
from free_foundations.artifacts.inventory import inventory, verify_inventory
from free_foundations.artifacts.metadata import write_json
from free_foundations.study.panel.features import build_features
from free_foundations.study.sources.crsp import build_crsp
from free_foundations.study.spec import PARAMS, StudySpec, file_hash, frame_digest, panel_contract

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _source_recovery(sources: Path, availability: pd.DataFrame) -> dict[str, Any]:
    """Source completeness for the CompanyFacts study; linkage gaps are coverage counts.

    Original filing documents are acquired by the source stage but not required: the
    study's richest rung is CompanyFacts. Unresolved historical CRSP-SEC links leave
    issuer-quarters outside the analytical panel and are reported, not gated.
    """

    def read(relative: str) -> dict[str, Any]:
        filename = sources / relative
        return json.loads(filename.read_text()) if filename.exists() else {}

    sec = read("sec/acquisition.json")
    factors = read("factors/status.json")
    identifiers = read("sec/metadata/identifier-acquisition.json")
    reasons = []
    if not sec.get("metadata_complete", False):
        reasons.append("sec_metadata_incomplete")
    if factors.get("status") != "complete":
        reasons.append("factor_archive_incomplete")
    if identifiers.get("status") != "acquired":
        reasons.append("historical_identifier_archive_incomplete")
    unresolved = availability["reason"].fillna("").str.startswith("linkage_")
    return {
        "status": "complete" if not reasons else "incomplete",
        "complete": not reasons,
        "reasons": reasons,
        "unresolved_linkage_issuer_quarters": int(unresolved.sum()),
        "sec_phase": sec.get("phase", "not_evaluated"),
        "sec_status": sec.get("status", "not_evaluated"),
    }


def prepare(sources: Path, output: Path, params: Path = PARAMS) -> None:
    """Materialize the single analytical panel and the full source-availability ledger offline."""
    with sources_lock(sources.parent, exclusive=False):
        _prepare(sources, output, params)


def _prepare(sources: Path, prepared: Path, params: Path) -> None:
    spec = StudySpec.read(params)
    frozen_manifest = json.loads((sources / "manifest.json").read_text())
    verify_inventory(sources, frozen_manifest["files"])
    source_manifest = json.loads((sources / "crsp-manifest.json").read_text())
    csv = sources / "crsp.csv"
    if file_hash(csv) != source_manifest["crsp_sha256"]:
        msg = "Frozen CRSP bytes changed after source acquisition."
        raise ValueError(msg)
    prepared.mkdir(parents=True, exist_ok=True)
    tables = build_crsp(csv, spec)
    for name, frame in tables.items():
        atomic_parquet(prepared / f"{name}.parquet", frame)
    population = (
        tables["quarterly"].loc[tables["quarterly"]["quarter"].ge(spec.feature_start)].copy()
    )
    LOGGER.info("Building quarter-start feature vintages from frozen SEC evidence")
    features = build_features(
        population, tables["monthly"], sources / "sec", spec, destination=prepared
    )
    for name, frame in features.items():
        if name in {"broad", "facts"}:
            continue
        atomic_parquet(prepared / f"{name}.parquet", frame)
    availability = features["availability"]
    population = population.merge(
        availability[
            [
                "issuer_id",
                "quarter",
                "xbrl_available",
                "status",
                "reason",
                "cik",
                "native_scalar_count",
                "original_characteristics_available",
                "sic",
            ]
        ].rename(columns={"status": "xbrl_status", "reason": "xbrl_reason"}),
        on=["issuer_id", "quarter"],
        how="left",
        validate="one_to_one",
    )
    population["xbrl_available"] = population["xbrl_available"].fillna(value=False).astype(bool)
    population = population.sort_values(["quarter", "issuer_id"]).reset_index(drop=True)
    population["sic"] = population["sic"].astype("string")
    panel = population.loc[population["xbrl_available"]].reset_index(drop=True)
    atomic_parquet(prepared / "population.parquet", population)
    atomic_parquet(prepared / "panel.parquet", panel)
    # Contracts bind the stored bytes every later stage reads, not the in-memory frame.
    panel = pd.read_parquet(prepared / "panel.parquet")
    population = pd.read_parquet(prepared / "population.parquet")
    factors = sources / "factors/quarterly.parquet"
    if factors.exists():
        atomic_copy(prepared / "factors.parquet", factors)
    else:
        atomic_parquet(
            prepared / "factors.parquet",
            pd.DataFrame(columns=["quarter", "RF", "Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]),
        )
    contract = panel_contract(panel, spec)
    recovery = _source_recovery(sources, availability)
    report = {
        "master": contract,
        "population_table_sha256": frame_digest(population),
        "cohorts_sha256": frame_digest(tables["cohorts"]),
        "source_crsp_sha256": source_manifest["crsp_sha256"],
        "source_recovery": recovery,
        "population_issuer_quarters": len(population),
        "analytical_issuer_quarters": len(panel),
        "availability": population["xbrl_status"].fillna("not_evaluated").value_counts().to_dict(),
        "availability_reasons": population["xbrl_reason"]
        .fillna("not_evaluated")
        .value_counts()
        .to_dict(),
        "status": "prepared"
        if len(panel) and recovery["complete"]
        else "source_recovery_incomplete",
        "no_complete_case_selection": True,
        "quarterly_source": "three monthly CRSP total returns, compounded once",
        "files": inventory(prepared),
    }
    write_json(prepared / "manifest.json", report)
    LOGGER.info(
        "Prepared %s analytical / %s population issuer-quarters", len(panel), len(population)
    )
