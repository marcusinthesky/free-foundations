"""Digest and verify complete artifact inventories."""

from __future__ import annotations

from typing import TYPE_CHECKING

from free_foundations.artifacts.hashes import file_hash

if TYPE_CHECKING:
    from pathlib import Path


def inventory(root: Path) -> dict[str, str]:
    """Hash every payload relative to its artifact root."""
    return {
        str(path.relative_to(root)): file_hash(path)
        for path in sorted(root.rglob("*"))
        if path.is_file() and path.name != "manifest.json" and not path.name.endswith(".partial")
    }


def verify_inventory(root: Path, expected: dict[str, str]) -> None:
    """Verify the full file set and every saved payload digest."""
    if inventory(root) != expected:
        msg = f"Frozen artifact bytes changed in {root}; regenerate and record dependent stages."
        raise ValueError(msg)
