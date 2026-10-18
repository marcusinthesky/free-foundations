"""Verify pinned checkpoint identities before acquisition, reuse, or loading."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any

INVENTORY = Path(__file__).resolve().parents[1] / "checkpoints.json"


def expected(name: str) -> dict[str, Any]:
    """Trusted inventory, independently checked against immutable upstream revisions."""
    return json.loads(INVENTORY.read_text())[name]


def verify(path: Path, digest: str) -> None:
    """Fail on altered bytes; an observation never replaces an expected identity."""
    with path.open("rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    if actual != digest:
        message = f"Checkpoint verification failed for {path}: expected {digest}, got {actual}"
        raise ValueError(message)


def resolve(name: str, cache: Path, legacy: Path | None = None) -> dict[str, Any]:
    """Use a revision-specific snapshot, migrating old files only after verification.

    Hugging Face owns downloading and download metadata. The separately approved
    inventory owns identity, including when operating offline from existing weights.
    """
    record = expected(name)
    root = cache / "models" / name / record["revision"]
    old = legacy if legacy is not None else cache / "models" / name
    descriptor = old / "provenance.json"
    if descriptor.is_file():
        previous = json.loads(descriptor.read_text())
        if any(previous.get(key) != record[key] for key in ("repository", "revision")):
            message = f"Checkpoint provenance disagrees with the pinned identity: {descriptor}"
            raise ValueError(message)
    for filename, digest in record["sha256"].items():
        destination = root / filename
        candidate = old / filename
        if not destination.exists() and candidate.is_file():
            verify(candidate, digest)
            destination.parent.mkdir(parents=True, exist_ok=True)
            try:
                os.link(candidate, destination)
            except OSError:
                shutil.copy2(candidate, destination)
    if any(not (root / filename).is_file() for filename in record["files"]):
        from huggingface_hub import snapshot_download  # noqa: PLC0415

        snapshot_download(
            record["repository"],
            revision=record["revision"],
            token=False,
            allow_patterns=record["files"],
            local_dir=root,
        )
    for filename, digest in record["sha256"].items():
        verify(root / filename, digest)
    return record | {"root": str(root)}
