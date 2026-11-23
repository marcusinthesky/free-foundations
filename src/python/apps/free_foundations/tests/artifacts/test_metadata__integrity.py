"""Metadata updates must preserve immutable restored artifact bytes."""

import json
import os
from pathlib import Path

import pytest

from free_foundations.artifacts.metadata import write_json


@pytest.mark.parametrize("symlink", [True, False])
def test_metadata_replacement_preserves_cache_target(tmp_path: Path, *, symlink: bool) -> None:
    cached = tmp_path / "cached.json"
    cached.write_text('{"old": true}\n')
    restored = tmp_path / "restored.json"
    if symlink:
        restored.symlink_to(cached)
    else:
        os.link(cached, restored)
    write_json(restored, {"new": True})
    assert json.loads(restored.read_text()) == {"new": True}
    assert json.loads(cached.read_text()) == {"old": True}
    assert not restored.is_symlink()
    assert not list(tmp_path.glob("*.partial"))


def test_invalid_metadata_does_not_replace_previous_bytes(tmp_path: Path) -> None:
    target = tmp_path / "manifest.json"
    write_json(target, {"valid": True})
    previous = target.read_bytes()
    with pytest.raises(ValueError, match="Out of range"):
        write_json(target, {"invalid": float("nan")})
    assert target.read_bytes() == previous
