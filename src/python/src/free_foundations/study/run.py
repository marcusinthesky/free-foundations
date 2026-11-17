"""One frozen-source dependency chain for the matched quarterly CRSP study."""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from free_foundations.data import write_json
from free_foundations.study.crsp import build_crsp
from free_foundations.study.encoding import encode_panel, load_representations
from free_foundations.study.factors import acquire_factors
from free_foundations.study.features import build_features
from free_foundations.study.linkage import acquire_identifier_sources, materialize_linkage
from free_foundations.study.sec import acquire_sources
from free_foundations.study.source_io import atomic_copy, atomic_csv, atomic_parquet, sources_lock
from free_foundations.study.spec import ROOT, StudySpec, file_hash, frame_digest, panel_contract

LOGGER = logging.getLogger(__name__)
SPEC = ROOT / "study.json"


def _inventory(root: Path) -> dict[str, str]:
    return {
        str(path.relative_to(root)): file_hash(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json" and not path.name.endswith(".partial")
    }


def _verify_inventory(root: Path, expected: dict[str, str]) -> None:
    if _inventory(root) != expected:
        msg = f"Frozen artifact bytes changed in {root}; regenerate and record dependent stages."
        raise ValueError(msg)


def _originals_complete(sec: dict[str, Any]) -> bool:
    failed = {
        "no_native_facts",
        "parsed_partial",
        "index_not_acquired",
        "instance_documents_unavailable",
    }
    # 'filings' is the earlier name for the same completed original-document phase.
    return (
        sec.get("metadata_complete") is True
        and sec.get("phase") in {"originals", "filings"}
        and sec.get("status") == "initialized"
        and type(sec.get("originals_pending")) is int
        and sec.get("originals_pending") == 0
        and sec.get("metadata_only") is not True
        and not any(sec.get("filing_statuses", {}).get(status, 0) for status in failed)
    )


def _source_recovery(sources: Path, availability: pd.DataFrame) -> dict[str, Any]:
    def read(relative: str) -> dict[str, Any]:
        filename = sources / relative
        return json.loads(filename.read_text()) if filename.exists() else {}

    sec = read("sec/acquisition.json")
    factors = read("factors/status.json")
    identifiers = read("sec/metadata/identifier-acquisition.json")
    full_xbrl = _originals_complete(sec)
    reasons = []
    if not sec.get("metadata_complete", False):
        reasons.append("sec_metadata_incomplete")
    if not full_xbrl:
        reasons.append("original_xbrl_filings_incomplete")
    if factors.get("status") != "complete":
        reasons.append("factor_archive_incomplete")
    if identifiers.get("status") != "acquired":
        reasons.append("historical_identifier_archive_incomplete")
    unresolved = availability["reason"].fillna("").str.startswith("linkage_")
    if unresolved.any():
        reasons.append("historical_issuer_linkage_unresolved")
    return {
        "status": "complete"
        if not reasons
        else "metadata_only"
        if sec.get("metadata_only")
        else "incomplete",
        "complete": not reasons,
        "full_xbrl_complete": full_xbrl,
        "reasons": reasons,
        "unresolved_linkage_issuer_quarters": int(unresolved.sum()),
        "sec_phase": sec.get("phase", "not_evaluated"),
        "sec_status": sec.get("status", "not_evaluated"),
        "originals_pending": sec.get("originals_pending"),
    }


def contact_identity() -> str | None:
    """Prefer explicit SEC identity, otherwise use the manuscript's public author contact."""
    declared = os.environ.get("EDGAR_IDENTITY", "").strip()
    if declared:
        return declared
    manuscript = Path("src/latex/main.tex")
    if manuscript.exists():
        text = manuscript.read_text()
        match = re.search(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        if match and "Marcus Gawronsky" in text:
            return f"Marcus Gawronsky {match.group()}"
    return None


def acquire(  # noqa: PLR0913 -- source paths, vintage destination and acquisition mode.
    csv: Path,
    script: Path | None = None,
    *,
    output: Path = ROOT,
    spec_path: Path = SPEC,
    offline: bool = False,
    metadata_only: bool = False,
) -> None:
    """Recover sources under an exclusive lock; preserve canonical bytes when staging."""
    with sources_lock(output, exclusive=True):
        _seed_sources(csv, output)
        _acquire(
            csv,
            script,
            output=output,
            spec_path=spec_path,
            offline=offline,
            metadata_only=metadata_only,
        )


def _hardlink(source: str, destination: str) -> str:
    os.link(Path(source).resolve(strict=True), destination)
    return destination


def _seed_sources(csv: Path, output: Path) -> None:
    destination, canonical = output / "sources", ROOT / "sources"
    if destination.is_symlink():
        msg = "The source directory itself must not be a symlink; file cache links are supported."
        raise ValueError(msg)
    if canonical.resolve() in output.resolve().parents or output.resolve() == canonical.resolve():
        msg = "A staged output must be outside the canonical source directory."
        raise ValueError(msg)
    if output.resolve() == ROOT.resolve() or destination.exists() or not canonical.exists():
        return
    with sources_lock(ROOT, exclusive=False):
        frozen = canonical / "crsp.csv"
        if not frozen.exists() or file_hash(csv) != file_hash(frozen):
            return
        temporary = Path(tempfile.mkdtemp(prefix=".sources-seed-", dir=output))
        try:
            shutil.copytree(canonical, temporary, copy_function=_hardlink, dirs_exist_ok=True)
            temporary.rename(destination)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
        LOGGER.info("Seeded recovery sources from unchanged canonical CRSP using hardlinks")


def _acquire(  # noqa: PLR0913 -- locked implementation retains the public acquisition options.
    csv: Path,
    script: Path | None = None,
    *,
    output: Path = ROOT,
    spec_path: Path = SPEC,
    offline: bool = False,
    metadata_only: bool = False,
) -> None:
    spec = StudySpec.read(spec_path)
    sources = output / "sources"
    sources.mkdir(parents=True, exist_ok=True)
    frozen = sources / "crsp.csv"
    if frozen.exists() and file_hash(frozen) != file_hash(csv):
        msg = "A CRSP source vintage already exists; use a distinct output for replacement."
        raise ValueError(msg)
    if not frozen.exists():
        atomic_copy(frozen, csv)
    if script is not None:
        snapshot = sources / "extraction.py.txt"
        if snapshot.exists() and file_hash(snapshot) != file_hash(script):
            msg = "The staged extraction script differs from the archived CRSP source vintage."
            raise ValueError(msg)
        if not snapshot.exists():
            atomic_copy(snapshot, script)
    LOGGER.info("Validating the full CRSP archive and reconstructing formation cohorts")
    tables = build_crsp(frozen, spec)
    source_report: dict[str, Any] = {
        "study_sha256": spec.digest,
        "crsp_sha256": file_hash(frozen),
        "extraction_sha256": file_hash(sources / "extraction.py.txt")
        if (sources / "extraction.py.txt").exists()
        else None,
        "return_definition": "CRSP CIZ mthret, decimal total return; no second adjustment",
        "source_market_cap_units": "USD thousands",
        "analysis_market_cap_units": "USD",
        "rows": len(tables["monthly"]),
        "securities": int(tables["monthly"]["permno"].nunique()),
        "archive_first": str(tables["monthly"]["date"].min()),
        "archive_last": str(tables["monthly"]["date"].max()),
        "terminal_return_flags": "not exported; completeness not certified by this extract",
        "acquisition_implementation_sha256": {
            name: file_hash(Path(__file__).with_name(name))
            for name in ("run.py", "sec.py", "bulk.py", "linkage.py", "factors.py", "source_io.py")
        },
    }
    write_json(sources / "crsp-manifest.json", source_report)
    _recover_links(tables["monthly"], sources, offline=offline)
    LOGGER.info("Recovering SEC source evidence; successful downloads are resumable")
    acquire_sources(
        tables["monthly"],
        sources,
        contact_identity(),
        existing_cache=Path("research/universe/cache"),
        offline=offline,
        metadata_only=metadata_only,
        feature_start=spec.feature_start,
        prefer_bulk=True,
    )
    acquire_factors(sources / "factors", spec, offline=offline)
    write_json(
        sources / "manifest.json",
        source_report
        | {
            "files": _inventory(sources),
        },
    )


def link(
    csv: Path,
    *,
    output: Path = ROOT,
    spec_path: Path = SPEC,
    offline: bool = False,
) -> None:
    """Recover bounded historical issuer identities from public SEC ownership metadata."""
    with sources_lock(output, exclusive=True):
        _seed_sources(csv, output)
        spec = StudySpec.read(spec_path)
        monthly = build_crsp(csv, spec)["monthly"]
        sources = output / "sources"
        _recover_links(monthly, sources, offline=offline)


def _recover_links(monthly: pd.DataFrame, sources: Path, *, offline: bool) -> None:
    acquire_identifier_sources(monthly, sources / "sec", contact_identity(), offline=offline)
    frames = materialize_linkage(monthly, sources / "sec")
    destination = sources / "sec/metadata/linkage-evidence.csv"
    previous = pd.read_csv(destination) if destination.exists() else frames["evidence"].iloc[:0]
    if "evidence_type" in previous:
        previous = previous.loc[
            previous["evidence_type"].ne("bracketed_sec_ownership_in_continuous_crsp_segment")
        ]
    evidence = pd.concat([previous, frames["evidence"]], ignore_index=True).drop_duplicates()
    atomic_csv(destination, evidence)
    LOGGER.info(
        "Recovered %s bounded historical intervals from %s SEC observations",
        len(evidence),
        len(frames["observations"]),
    )


def _freeze_validation(staged: Path, current: Path, spec: StudySpec) -> dict[str, Any]:
    manifest = json.loads((staged / "manifest.json").read_text())
    _verify_inventory(staged, manifest["files"])
    report = json.loads((staged / "crsp-manifest.json").read_text())
    digest = file_hash(staged / "crsp.csv")
    if (
        manifest.get("study_sha256") != spec.digest
        or report.get("study_sha256") != spec.digest
        or manifest.get("crsp_sha256") != digest
        or report.get("crsp_sha256") != digest
    ):
        msg = "Staged source manifest, scientific specification or CRSP hash is inconsistent."
        raise ValueError(msg)
    if current.exists():
        previous = json.loads((current / "manifest.json").read_text())
        _verify_inventory(current, previous["files"])
        if (
            previous.get("study_sha256") != spec.digest
            or previous.get("crsp_sha256") != digest
            or file_hash(current / "crsp.csv") != digest
        ):
            msg = "Freeze cannot replace a different canonical study specification or CRSP vintage."
            raise ValueError(msg)
    sec = json.loads((staged / "sec/acquisition.json").read_text())
    if not _originals_complete(sec):
        msg = (
            "Freeze requires complete SEC metadata and the completed originals phase "
            "with no pending filings."
        )
        raise ValueError(msg)
    factors = json.loads((staged / "factors/status.json").read_text())
    identifiers = json.loads((staged / "sec/metadata/identifier-acquisition.json").read_text())
    if factors.get("status") != "complete" or identifiers.get("status") != "acquired":
        msg = "Freeze requires complete factor and historical identifier archives."
        raise ValueError(msg)
    return sec


def freeze(
    *, staging: Path = ROOT / "recovery", output: Path = ROOT, spec_path: Path = SPEC
) -> dict[str, Any]:
    """Validate and promote completed staged sources offline, retaining the old snapshot."""
    staged, current = staging / "sources", output / "sources"
    if (
        staged.resolve() == current.resolve()
        or staged.resolve() in current.resolve().parents
        or current.resolve() in staged.resolve().parents
        or staged.is_symlink()
        or current.is_symlink()
    ):
        msg = "Staged and canonical source directories must be distinct, disjoint real directories."
        raise ValueError(msg)
    with sources_lock(staging, exclusive=True), sources_lock(output, exclusive=True):
        sec = _freeze_validation(staged, current, StudySpec.read(spec_path))
        manifest_digest = file_hash(staged / "manifest.json")
        snapshots = output / "recovery/snapshots"
        snapshots.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        backup = snapshots / f"sources-{stamp}-{uuid.uuid4().hex[:8]}"
        had_current = current.exists()
        if had_current:
            current.rename(backup)
        try:
            staged.rename(current)
        except OSError as promotion_error:
            if had_current:
                try:
                    backup.rename(current)
                except OSError as rollback_error:
                    msg = (
                        "Source promotion and rollback both failed; "
                        "old sources remain in snapshots."
                    )
                    raise ExceptionGroup(
                        msg, [promotion_error, rollback_error]
                    ) from promotion_error
            raise
        receipt = {
            "status": "frozen",
            "sources": str(current),
            "previous_sources": str(backup) if had_current else None,
            "source_manifest_sha256": manifest_digest,
            "phase": "originals",
            "acquisition_phase": sec["phase"],
            "frozen_at": datetime.now(UTC).isoformat(),
        }
        write_json(output / "recovery/freeze-latest.json", receipt)
        LOGGER.info("Promoted completed sources; previous snapshot retained at %s", backup)
        return receipt


def prepare(*, output: Path = ROOT, spec_path: Path = SPEC) -> None:
    """Materialize the single analytical panel and the full source-availability ledger offline."""
    with sources_lock(output, exclusive=False):
        _prepare(output=output, spec_path=spec_path)


def _prepare(*, output: Path = ROOT, spec_path: Path = SPEC) -> None:
    spec = StudySpec.read(spec_path)
    sources = output / "sources"
    frozen_manifest = json.loads((sources / "manifest.json").read_text())
    _verify_inventory(sources, frozen_manifest["files"])
    source_manifest = json.loads((sources / "crsp-manifest.json").read_text())
    csv = sources / "crsp.csv"
    if file_hash(csv) != source_manifest["crsp_sha256"]:
        msg = "Frozen CRSP bytes changed after source acquisition."
        raise ValueError(msg)
    prepared = output / "prepared"
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
            ]
        ].rename(columns={"status": "xbrl_status", "reason": "xbrl_reason"}),
        on=["issuer_id", "quarter"],
        how="left",
        validate="one_to_one",
    )
    population["xbrl_available"] = population["xbrl_available"].fillna(value=False).astype(bool)
    population = population.sort_values(["quarter", "issuer_id"]).reset_index(drop=True)
    panel = population.loc[population["xbrl_available"]].reset_index(drop=True)
    atomic_parquet(prepared / "population.parquet", population)
    atomic_parquet(prepared / "panel.parquet", panel)
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
        "population_sha256": frame_digest(population),
        "history_sha256": frame_digest(tables["history"]),
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
        "files": _inventory(prepared),
    }
    write_json(prepared / "manifest.json", report)
    LOGGER.info(
        "Prepared %s analytical / %s population issuer-quarters", len(panel), len(population)
    )


def inputs(
    output: Path = ROOT, spec_path: Path = SPEC
) -> tuple[StudySpec, dict[str, pd.DataFrame]]:
    """Restore and verify the exact same immutable observations for every analytical task."""
    spec = StudySpec.read(spec_path)
    prepared = output / "prepared"
    tables = {
        name: pd.read_parquet(prepared / f"{name}.parquet")
        for name in ("panel", "characteristics", "factors", "history")
    }
    manifest = json.loads((prepared / "manifest.json").read_text())
    _verify_inventory(prepared, manifest["files"])
    if manifest["master"] != panel_contract(tables["panel"], spec):
        msg = "Prepared master panel changed; regenerate all dependent stages."
        raise ValueError(msg)
    if manifest["history_sha256"] != frame_digest(tables["history"]):
        msg = "Historical return support changed after preparation."
        raise ValueError(msg)
    return spec, tables


def encode(*, output: Path = ROOT, spec_path: Path = SPEC) -> None:
    """Extract matched full-coverage states independently of financial estimation."""
    spec, tables = inputs(output, spec_path)
    manifest = json.loads((output / "prepared/manifest.json").read_text())
    unavailable = (
        {}
        if manifest["source_recovery"]["full_xbrl_complete"]
        else {"full_xbrl": "original_filing_recovery_incomplete"}
    )
    encode_panel(
        tables["panel"],
        tables["characteristics"],
        output / "prepared/broad",
        spec,
        output / "representations",
        input_digest=file_hash(output / "prepared/manifest.json"),
        unavailable_rungs=unavailable,
    )


def analyze(*, output: Path = ROOT, spec_path: Path = SPEC, replication_only: bool = False) -> None:
    """Estimate saved-state comparisons or the original core on the same master experiment."""
    from free_foundations.study.analysis import run_analyses  # noqa: PLC0415

    spec, tables = inputs(output, spec_path)
    states: dict[object, object] = {}
    if not replication_only:
        states.update(
            load_representations(
                output / "representations",
                tables["panel"],
                spec,
                expected_input_digest=file_hash(output / "prepared/manifest.json"),
            )
        )
    destination = output / ("replication" if replication_only else "measurement")
    run_analyses(
        tables["panel"],
        tables["characteristics"],
        tables["factors"],
        states,
        spec,
        destination,
        history=tables["history"],
        tasks="replication" if replication_only else "measurement",
    )


def report(*, output: Path = ROOT, spec_path: Path = SPEC) -> None:
    """Render publication assets from saved results only, never refit an estimator."""
    from free_foundations.study.publication import render  # noqa: PLC0415

    render(output, StudySpec.read(spec_path))
