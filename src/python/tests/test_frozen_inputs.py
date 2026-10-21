"""Numerical reproduction consumes recorded inputs and never repairs them over the network."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from free_foundations.panel import characteristics
from free_foundations.representations import checkpoints, setup
from free_foundations.universe.sources import company_facts


def test_missing_frozen_inputs_fail_without_acquisition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(FileNotFoundError, match="frozen SEC"):
        company_facts(tmp_path, 123, cached_only=True)
    columns = pd.MultiIndex.from_tuples([("Close", "TEST")])
    market = pd.DataFrame([[100.0]], columns=columns, index=pd.to_datetime(["2025-12-31"]))
    market.to_parquet(tmp_path / "market-0.parquet")
    monkeypatch.setattr(characteristics, "SOURCE", tmp_path)
    monkeypatch.setattr(characteristics, "ROOT", tmp_path)
    with pytest.raises(FileNotFoundError, match="frozen Yahoo"):
        characteristics.markets()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["market-0.parquet"]


def test_shared_checkpoint_reuse_preserves_legacy_catalogue(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    catalogue = tmp_path / "checkpoints.json"
    original = b'{"legacy": "recorded"}\n'
    catalogue.write_bytes(original)
    root = tmp_path / "cache/models/test"
    root.mkdir(parents=True)
    weights = b"pinned checkpoint"
    (root / "weights.bin").write_bytes(weights)
    monkeypatch.setattr(setup, "CHECKPOINTS", {"test": ("test/model", "pinned", ("weights.bin",))})
    inventory = tmp_path / "expected.json"
    inventory.write_text(
        json.dumps(
            {
                "test": {
                    "repository": "test/model",
                    "revision": "pinned",
                    "files": ["weights.bin"],
                    "sha256": {"weights.bin": hashlib.sha256(weights).hexdigest()},
                }
            }
        )
    )
    monkeypatch.setattr(checkpoints, "INVENTORY", inventory)
    records = setup.ensure_checkpoints(tmp_path, ("test",), write_catalogue=False)
    assert catalogue.read_bytes() == original
    provenance = records["test"]
    assert not (root / "provenance.json").exists()
    assert provenance["sha256"] == {"weights.bin": hashlib.sha256(weights).hexdigest()}
