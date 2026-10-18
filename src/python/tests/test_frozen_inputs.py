"""Numerical reproduction consumes recorded inputs and never repairs them over the network."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from free_foundations.expanded import setup
from free_foundations.fernandez.characteristics import market_history
from free_foundations.panel import characteristics
from free_foundations.universe.sources import company_facts


def test_missing_frozen_inputs_fail_without_acquisition(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(FileNotFoundError, match="frozen industry"):
        setup.ensure_industry(tmp_path)
    with pytest.raises(FileNotFoundError, match="frozen SEC"):
        company_facts(tmp_path, 123, cached_only=True)
    with pytest.raises(FileNotFoundError, match="frozen Yahoo"):
        market_history("TEST", tmp_path)
    columns = pd.MultiIndex.from_tuples([("Close", "TEST")])
    market = pd.DataFrame([[100.0]], columns=columns, index=pd.to_datetime(["2025-12-31"]))
    market.to_parquet(tmp_path / "market-0.parquet")
    monkeypatch.setattr(characteristics, "SOURCE", tmp_path)
    monkeypatch.setattr(characteristics, "ROOT", tmp_path)
    with pytest.raises(FileNotFoundError, match="frozen Yahoo"):
        characteristics.markets()
    assert sorted(p.name for p in tmp_path.iterdir()) == ["market-0.parquet"]


def test_frozen_industry_is_unchanged(tmp_path: Path) -> None:
    path = tmp_path / "industry.csv"
    original = b"ticker,sic,classification_vintage\nTEST,1234,2026-10-16\n"
    path.write_bytes(original)
    setup.ensure_industry(tmp_path)
    assert path.read_bytes() == original


def test_expanded_manifest_uses_actual_project_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source, output = tmp_path / "cache", tmp_path / "expanded"
    source.mkdir()
    output.mkdir()
    (tmp_path / "manifest.json").write_text(json.dumps({"sha256": {"input": "recorded"}}))
    (source / "checkpoint.json").write_text(
        json.dumps({"repository": "test", "revision": "pinned", "filename": "weights.bin"})
    )
    (source / "weights.bin").write_bytes(b"test checkpoint")

    def version(_name: str) -> str:
        return "test-version"

    monkeypatch.setattr(setup, "version", version)
    setup.write_manifest(source, output)
    manifest = json.loads((output / "manifest.json").read_text())
    lock = Path(__file__).resolve().parents[1] / "uv.lock"
    assert manifest["python_lock_sha256"] == hashlib.sha256(lock.read_bytes()).hexdigest()
    assert "src/free_foundations/expanded/setup.py" in manifest["python_source_sha256"]


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
    setup.ensure_checkpoints(tmp_path, ("test",), write_catalogue=False)
    assert catalogue.read_bytes() == original
    provenance = json.loads((root / "provenance.json").read_text())
    assert provenance["sha256"]["weights.bin"] == hashlib.sha256(weights).hexdigest()
