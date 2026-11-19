"""Validate and promote a completed CRSP-SEC source snapshot."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from free_foundations.artifacts.atomic import sources_lock
from free_foundations.artifacts.inventory import verify_inventory
from free_foundations.artifacts.metadata import write_json
from free_foundations.study.spec import PARAMS, StudySpec, file_hash

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)


def _freeze_validation(staged: Path, current: Path, spec: StudySpec) -> dict[str, Any]:
    manifest = json.loads((staged / "manifest.json").read_text())
    verify_inventory(staged, manifest["files"])
    report = json.loads((staged / "crsp-manifest.json").read_text())
    digest = file_hash(staged / "crsp.csv")
    if (
        manifest.get("population_sha256") != spec.population_digest
        or report.get("population_sha256") != spec.population_digest
        or manifest.get("crsp_sha256") != digest
        or report.get("crsp_sha256") != digest
    ):
        msg = "Staged source manifest, scientific specification or CRSP hash is inconsistent."
        raise ValueError(msg)
    if current.exists():
        previous = json.loads((current / "manifest.json").read_text())
        verify_inventory(current, previous["files"])
        if (
            previous.get("population_sha256") != spec.population_digest
            or previous.get("crsp_sha256") != digest
            or file_hash(current / "crsp.csv") != digest
        ):
            msg = "Freeze cannot replace a different canonical study specification or CRSP vintage."
            raise ValueError(msg)
    sec = json.loads((staged / "sec/acquisition.json").read_text())
    if sec.get("metadata_complete") is not True:
        msg = "Freeze requires complete SEC metadata and CompanyFacts."
        raise ValueError(msg)
    factors = json.loads((staged / "factors/status.json").read_text())
    identifiers = json.loads((staged / "sec/metadata/identifier-acquisition.json").read_text())
    if factors.get("status") != "complete" or identifiers.get("status") != "acquired":
        msg = "Freeze requires complete factor and historical identifier archives."
        raise ValueError(msg)
    return sec


def freeze(*, staging: Path, canonical: Path, params: Path = PARAMS) -> dict[str, Any]:
    """Validate and promote completed staged sources offline, retaining the old snapshot."""
    staged, current = staging / "sources", canonical
    if (
        staged.resolve() == current.resolve()
        or staged.resolve() in current.resolve().parents
        or current.resolve() in staged.resolve().parents
        or staged.is_symlink()
        or current.is_symlink()
    ):
        msg = "Staged and canonical source directories must be distinct, disjoint real directories."
        raise ValueError(msg)
    with sources_lock(staging, exclusive=True), sources_lock(canonical.parent, exclusive=True):
        sec = _freeze_validation(staged, current, StudySpec.read(params))
        manifest_digest = file_hash(staged / "manifest.json")
        snapshots = staging / "snapshots"
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
        write_json(staging / "freeze-latest.json", receipt)
        LOGGER.info("Promoted completed sources; previous snapshot retained at %s", backup)
        return receipt
