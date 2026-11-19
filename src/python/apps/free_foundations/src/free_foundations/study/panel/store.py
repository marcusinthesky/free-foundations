"""Read verified panel artifacts."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pandas as pd

from free_foundations.artifacts.inventory import verify_inventory
from free_foundations.study.spec import PARAMS, StudySpec, frame_digest, panel_contract

if TYPE_CHECKING:
    from pathlib import Path


def inputs(prepared: Path, params: Path = PARAMS) -> tuple[StudySpec, dict[str, pd.DataFrame]]:
    """Restore and verify the exact same immutable observations for every analytical task."""
    spec = StudySpec.read(params)
    tables = {
        name: pd.read_parquet(prepared / f"{name}.parquet")
        for name in ("panel", "characteristics", "factors", "cohorts", "membership")
    }
    manifest = json.loads((prepared / "manifest.json").read_text())
    verify_inventory(prepared, manifest["files"])
    if manifest["master"] != panel_contract(tables["panel"], spec):
        msg = "Prepared master panel changed; regenerate all dependent stages."
        raise ValueError(msg)
    if manifest["cohorts_sha256"] != frame_digest(tables["cohorts"]):
        msg = "Formation cohorts changed after preparation."
        raise ValueError(msg)
    return spec, tables
