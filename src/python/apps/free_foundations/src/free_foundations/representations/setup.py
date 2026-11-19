"""Acquire and verify the four declared immutable model snapshots."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from free_foundations.data import write_json
from free_foundations.representations.checkpoints import expected, resolve

if TYPE_CHECKING:
    from pathlib import Path

CHECKPOINTS = {
    name: (record["repository"], record["revision"], tuple(record["files"]))
    for name in ("tabpfn_full", "tabfm", "kumo", "limix")
    for record in (expected(name),)
}


def ensure_checkpoints(
    root: Path, models: tuple[str, ...] = tuple(CHECKPOINTS)
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
        metadata[name] = resolve(name, root)
    return metadata


def local_checkpoint(root: Path, name: str) -> dict[str, Any]:
    """Verify immutable identity and file contents before every reuse."""
    return ensure_checkpoints(root, (name,))[name]


def checkpoint_catalogue(root: Path) -> None:
    """Acquire pinned weights under ``root`` and record their verified manifest."""
    write_json(root / "manifest.json", ensure_checkpoints(root))
