"""Acquire and verify the four declared immutable model snapshots."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from free_foundations.data import write_json
from free_foundations.representations.checkpoints import expected, resolve

CHECKPOINTS = {
    name: (record["repository"], record["revision"], tuple(record["files"]))
    for name in ("tabpfn_full", "tabfm", "kumo", "limix")
    for record in (expected(name),)
}


def ensure_checkpoints(
    output: Path,
    models: tuple[str, ...] = ("tabpfn_full", "tabfm", "kumo", "limix"),
    *,
    write_catalogue: bool = True,
) -> dict[str, dict[str, object]]:
    """Verify pinned bytes before reuse; acquire missing revision-specific snapshots."""
    metadata: dict[str, dict[str, object]] = {}
    for name in models:
        repository, revision, files = CHECKPOINTS[name]
        record = expected(name)
        if (repository, revision, list(files)) != (
            record["repository"],
            record["revision"],
            record["files"],
        ):
            message = f"Checkpoint declaration differs from approved inventory: {name}"
            raise ValueError(message)
        metadata[name] = resolve(name, output / "cache")
    if write_catalogue:
        manifest = output / "checkpoints.json"
        previous = json.loads(manifest.read_text()) if manifest.exists() else {}
        write_json(manifest, previous | metadata)
    return metadata


def local_checkpoint(cache: Path, name: str) -> dict[str, Any]:
    """Verify immutable identity and file contents before every reuse."""
    records = ensure_checkpoints(cache.parent, (name,), write_catalogue=False)
    return records[name]


def checkpoint_catalogue() -> None:
    """Acquire pinned weights independently of financial estimation and publication."""
    records = ensure_checkpoints(
        Path("research/expanded"), tuple(CHECKPOINTS), write_catalogue=False
    )
    write_json(Path("research/model-checkpoints.json"), records)
