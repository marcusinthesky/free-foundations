"""Shared filing records, JSON metadata, and the HTTPS factor-data reader."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from free_foundations.artifacts.atomic import atomic_bytes

if TYPE_CHECKING:
    from pathlib import Path


def write_json(path: Path, value: object) -> None:
    """Atomically replace metadata without writing through a restored DVC cache link."""
    payload = json.dumps(value, indent=2, allow_nan=False) + "\n"
    atomic_bytes(path, payload.encode("utf-8"))
