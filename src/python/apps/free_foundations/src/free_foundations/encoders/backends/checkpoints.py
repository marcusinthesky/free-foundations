"""Verify pinned checkpoint identities before acquisition, reuse, or loading."""

from __future__ import annotations

import hashlib
import json
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


def resolve(name: str, root: Path, *, download: bool = True) -> dict[str, Any]:
    """Use the revision-specific snapshot under ``root/name/revision``, verifying bytes.

    Hugging Face owns downloading and download metadata. The separately approved
    inventory owns identity, including when operating offline from existing weights.
    """
    record = expected(name)
    root = root / name / record["revision"]
    if any(not (root / filename).is_file() for filename in record["files"]):
        if not download:
            message = f"Missing pinned local checkpoint for {name}. Run raw fetch-checkpoints."
            raise FileNotFoundError(message)
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
