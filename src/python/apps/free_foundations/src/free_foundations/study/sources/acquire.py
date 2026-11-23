"""Acquire and promote verified study inputs."""

from __future__ import annotations

import logging
import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Any

import pandas as pd

from free_foundations.artifacts.atomic import atomic_copy, atomic_csv, sources_lock
from free_foundations.artifacts.inventory import inventory
from free_foundations.artifacts.metadata import write_json
from free_foundations.study.sources.crsp import build_crsp
from free_foundations.study.sources.factors import acquire_factors
from free_foundations.study.sources.linkage import acquire_identifier_sources, materialize_linkage
from free_foundations.study.sources.sec import acquire_sources
from free_foundations.study.spec import PARAMS, StudySpec, file_hash

LOGGER = logging.getLogger(__name__)


def contact_identity() -> str | None:
    """Prefer explicit SEC identity, otherwise use the manuscript's public author contact."""
    declared = os.environ.get("EDGAR_IDENTITY", "").strip()
    if declared:
        return declared
    manuscript = Path("src/latex/projects/free-foundations/src/metadata.tex")
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
    staging: Path,
    canonical: Path,
    params: Path = PARAMS,
    offline: bool = False,
    metadata_only: bool = False,
    existing_cache: Path | None = None,
) -> None:
    """Recover sources under an exclusive lock; preserve canonical bytes when staging."""
    with sources_lock(staging, exclusive=True):
        _seed_sources(csv, staging, canonical)
        _acquire(
            csv,
            script,
            output=staging,
            params=params,
            offline=offline,
            metadata_only=metadata_only,
            existing_cache=existing_cache,
        )


def _hardlink(source: str, destination: str) -> str:
    os.link(Path(source).resolve(strict=True), destination)
    return destination


def _seed_sources(csv: Path, output: Path, canonical: Path) -> None:
    destination = output / "sources"
    if destination.is_symlink():
        msg = "The source directory itself must not be a symlink; file cache links are supported."
        raise ValueError(msg)
    if canonical.resolve() in output.resolve().parents or output.resolve() == canonical.resolve():
        msg = "A staged output must be outside the canonical source directory."
        raise ValueError(msg)
    if destination.exists() or not canonical.exists():
        return
    with sources_lock(canonical.parent, exclusive=False):
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
    script: Path | None,
    *,
    output: Path,
    params: Path,
    offline: bool,
    metadata_only: bool,
    existing_cache: Path | None,
) -> None:
    spec = StudySpec.read(params)
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
        "population_sha256": spec.population_digest,
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
            name: file_hash(Path(__file__).parents[2] / name)
            for name in (
                "study/sources/acquire.py",
                "study/sources/sec.py",
                "study/sources/bulk.py",
                "study/sources/linkage.py",
                "study/sources/factors.py",
                "artifacts/atomic.py",
            )
        },
    }
    write_json(sources / "crsp-manifest.json", source_report)
    _recover_links(tables["monthly"], sources, offline=offline)
    LOGGER.info("Recovering SEC source evidence; successful downloads are resumable")
    acquire_sources(
        tables["monthly"],
        sources,
        contact_identity(),
        existing_cache=existing_cache,
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
            "files": inventory(sources),
        },
    )


def link(
    csv: Path,
    *,
    staging: Path,
    canonical: Path,
    params: Path = PARAMS,
    offline: bool = False,
) -> None:
    """Recover bounded historical issuer identities from public SEC ownership metadata."""
    output = staging
    with sources_lock(output, exclusive=True):
        _seed_sources(csv, output, canonical)
        spec = StudySpec.read(params)
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
