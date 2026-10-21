"""A valid numerical state must belong to the complete extraction and current cohort."""

import json
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import numpy as np
import pandas as pd
import pytest

from free_foundations.panel import run
from free_foundations.representations.encoding import Prepared


@pytest.fixture
def extraction(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(run, "YEARS", (2020,))
    monkeypatch.setattr(run, "SUPPORT_SIZES", (32,))
    monkeypatch.setattr(run, "STATES", tmp_path / "states")
    monkeypatch.setattr(run, "extraction_sources", dict)

    def empty_frame(*_args: object) -> pd.DataFrame:
        return pd.DataFrame()

    monkeypatch.setattr(run.pd, "read_parquet", empty_frame)
    monkeypatch.setattr(run, "history_view", empty_frame)
    monkeypatch.setattr(run, "labels", empty_frame)
    monkeypatch.setattr(run, "STUDY", SimpleNamespace(characteristics=(), history=5))
    data = Prepared(
        np.ones((2, 1)),
        np.ones((2, 1)),
        np.ones(2),
        ("X",),
        ("S1", "S2"),
        ("A", "B"),
        2020,
        "context",
    )

    def prepared_cohort(_year: int) -> tuple[SimpleNamespace, None]:
        return SimpleNamespace(tickers=("A", "B")), None

    def frozen_context(*_args: object, **_kwargs: object) -> Prepared:
        return data

    monkeypatch.setattr(run, "prepared", prepared_cohort)
    monkeypatch.setattr(run, "context", frozen_context)
    for path in (Path("src/python/uv.lock"), Path("research/model-checkpoints.json")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixed")
    states: dict[str, object] = {}
    for support in (256, 32):
        path = run.STATES / f"2020-{support}.npz"
        path.parent.mkdir(parents=True, exist_ok=True)
        names = sorted(run.FOUNDATION_READOUTS if support == 256 else run.PRINCIPAL)
        models = run.FOUNDATION_MODELS if support == 256 else run.FOUNDATION_MODELS[:4]
        contract = {
            "year": 2020,
            "support_rows": support,
            "representations": names,
            "tickers": ["A", "B"],
            "context_digest": "context",
            "model_contracts": {
                model: {
                    "tickers": ["A", "B"],
                    "support_ids": ["S1", "S2"],
                    "features": ["X"],
                    "context_digest": "context",
                }
                for model in models
            },
        }
        np.savez_compressed(path, allow_pickle=False, **{name: np.ones((2, 1)) for name in names})
        record = {
            "contract": contract,
            "sha256": run.digest_file(path),
            "shapes": {name: [2, 1] for name in names},
        }
        path.with_suffix(".json").write_text(json.dumps(record))
        states[str(path)] = record
        label = "histories" if support == 256 else "histories@support32"
        run.record_context(run.STATES / "contexts" / f"2020-{label}.json", data)
    return {
        "states": states,
        "models": list(run.FOUNDATION_MODELS),
        "source_sha256": {},
        "lock_sha256": run.digest_file(Path("src/python/uv.lock")),
        "checkpoint_catalogue_sha256": run.digest_file(Path("research/model-checkpoints.json")),
    }


def test_complete_extraction_is_accepted(extraction: dict[str, Any]) -> None:
    run.validate_extraction(extraction)


def test_truncated_manifest_is_rejected(extraction: dict[str, Any]) -> None:
    extraction["states"].pop(next(iter(extraction["states"])))
    with pytest.raises(ValueError, match="Incomplete canonical extraction"):
        run.validate_extraction(extraction)


def test_sidecar_must_agree_with_manifest(extraction: dict[str, Any]) -> None:
    path = run.STATES / "2020-256.json"
    record = json.loads(path.read_text())
    record["contract"]["tickers"] = ["B", "A"]
    path.write_text(json.dumps(record))
    with pytest.raises(ValueError, match="sidecar differs"):
        run.validate_extraction(extraction)


def test_relabeling_sidecar_and_manifest_cannot_change_the_cohort(
    extraction: dict[str, Any],
) -> None:
    path = run.STATES / "2020-256.npz"
    record = extraction["states"][str(path)]
    record["contract"]["tickers"] = ["B", "A"]
    path.with_suffix(".json").write_text(json.dumps(record))
    with pytest.raises(ValueError, match="prepared financial inputs"):
        run.validate_extraction(extraction)


def test_context_record_must_match_prepared_context(extraction: dict[str, Any]) -> None:
    path = run.STATES / "contexts/2020-histories.json"
    context = json.loads(path.read_text())
    context["digest"] = "different-context"
    path.write_text(json.dumps(context))
    with pytest.raises(ValueError, match="prepared financial inputs"):
        run.validate_extraction(extraction)
