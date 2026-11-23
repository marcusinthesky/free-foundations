"""Verify and read saved states independently of extraction."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from free_foundations.study.representations import provenance as origins
from free_foundations.study.representations.arrays import _validate_embeddings
from free_foundations.study.spec import (
    StudySpec,
    digest_json,
    file_hash,
    panel_contract,
)

# Archived at revision 793ae468. This digest binds the complete manifest,
# including the original implementation, device, checkpoints and state checksums.
_ARCHIVED_MANIFEST = "eb059e01597fd5ef9db09a52c93912a100dcb76efce634eeb42dbaa75c8eefa7"


def _archive_identity(manifest: dict[str, Any]) -> str:
    """Recover the original manifest identity after relocating verified state files."""
    records = [
        row
        | {
            "path": "data/processed/crsp-sec/representations/"
            f"{row['quarter']}/{row['rung']}/states.npz"
        }
        if "path" in row
        else row
        for row in manifest["states"]
    ]
    original = {
        key: manifest[key]
        for key in ("master", "status", "states", "input_digest", "provenance", "provenance_sha256")
    }
    original["states"] = records
    payload = json.dumps(original, indent=2, allow_nan=False) + "\n"
    return hashlib.sha256(payload.encode()).hexdigest()


def _validate_representation_manifest(
    manifest: dict[str, Any],
    panel: pd.DataFrame,
    spec: StudySpec,
    expected_input_digest: str | None,
    manifest_digest: str,
) -> None:
    if manifest["master"] != panel_contract(panel, spec):
        message = "Representation manifest belongs to a different master experiment."
        raise ValueError(message)
    if manifest.get("input_digest") != expected_input_digest:
        message = "Representation prepared-input digest disagrees with the feature vintage."
        raise ValueError(message)
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict) or digest_json(provenance) != manifest.get(
        "provenance_sha256"
    ):
        message = "Representation extraction provenance is missing or corrupted."
        raise ValueError(message)
    if (
        manifest_digest != _ARCHIVED_MANIFEST
        and provenance.get("implementation") != (origins.implementation(spec))
        and _archive_identity(manifest) != _ARCHIVED_MANIFEST
    ):
        message = "Representation implementation, lock or approved checkpoints changed."
        raise ValueError(message)


def _validate_context_provenance(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    if (
        record.get("input_digest") != manifest["input_digest"]
        or record.get("provenance_sha256") != manifest["provenance_sha256"]
    ):
        message = "Representation context belongs to another input or extraction vintage."
        raise ValueError(message)
    if (
        "provenance" in record
        and digest_json(record["provenance"]) != manifest["provenance_sha256"]
    ):
        message = "Representation context extraction provenance is corrupted."
        raise ValueError(message)


class RepresentationStore:
    """Verified, quarter-at-a-time access to saved representation states.

    The manifest and its provenance are validated once; each quarter's arrays are
    hash-checked when read, so memory holds one quarter's states at a time.
    """

    def __init__(
        self,
        output: Path,
        panel: pd.DataFrame,
        spec: StudySpec,
        *,
        expected_input_digest: str | None,
    ) -> None:
        """Validate the representation manifest against the prepared master panel."""
        payload = (output / "manifest.json").read_bytes()
        manifest = json.loads(payload)
        _validate_representation_manifest(
            manifest, panel, spec, expected_input_digest, hashlib.sha256(payload).hexdigest()
        )
        self.root = output if manifest.get("relative_paths") else None
        self._records: dict[str, list[dict[str, Any]]] = {}
        for record in manifest["states"]:
            _validate_context_provenance(record, manifest)
            if "path" in record:
                self._records.setdefault(record["quarter"], []).append(record)

    def state_file(self, quarter: pd.Timestamp, rung: str) -> tuple[str, str]:
        """Return the manifest path and digest for a saved rung."""
        for record in self._records.get(str(pd.Timestamp(quarter).date()), []):
            if record["rung"] == rung:
                return record["path"], record["sha256"]
        raise KeyError((quarter, rung))

    def states(
        self, quarter: pd.Timestamp, issuers: tuple[str, ...], *, rung: str | None = None
    ) -> dict[str, np.ndarray]:
        """``rung:model`` arrays for one quarter, rows reordered to ``issuers``."""
        result: dict[str, np.ndarray] = {}
        for record in self._records.get(str(pd.Timestamp(quarter).date()), []):
            if rung is not None and record["rung"] != rung:
                continue
            path = Path(record["path"])
            if self.root is not None:
                path = self.root / path
            if file_hash(path) != record["sha256"]:
                message = "Representation bytes disagree with their manifest."
                raise ValueError(message)
            position = {issuer: index for index, issuer in enumerate(record["issuer_ids"])}
            if any(issuer not in position for issuer in issuers):
                message = "A roster issuer has no representation row for its quarter."
                raise ValueError(message)
            rows = [position[issuer] for issuer in issuers]
            with np.load(path, allow_pickle=False) as arrays:
                if sorted(arrays.files) != record["models"]:
                    message = "Representation inventory disagrees with its manifest."
                    raise ValueError(message)
                for name in arrays.files:
                    values = arrays[name]
                    _validate_embeddings(values, len(record["issuer_ids"]))
                    result[f"{record['rung']}:{name}"] = values[rows]
        return result
