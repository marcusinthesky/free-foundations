"""Shared filing records, JSON metadata, and the HTTPS factor-data reader."""

from __future__ import annotations

import json
import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path


def write_json(path: Path, value: object) -> None:
    """Atomically replace metadata without writing through a restored DVC cache link."""
    payload = json.dumps(value, indent=2, allow_nan=False) + "\n"
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.partial")
    try:
        temporary.write_text(payload)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)
