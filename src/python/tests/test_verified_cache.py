"""Checkpoint and embedding integrity must hold independently of DVC stage freshness."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from free_foundations.representations import cache, checkpoints


def test_checkpoint_migration_verifies_bytes_and_never_rewrites_expected(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"independently verified fixture"
    record = {
        "repository": "owner/model",
        "revision": "pinned-revision",
        "files": ["weights"],
        "sha256": {"weights": hashlib.sha256(payload).hexdigest()},
    }
    inventory = tmp_path / "expected.json"
    inventory.write_text(json.dumps({"example": record}))
    monkeypatch.setattr(checkpoints, "INVENTORY", inventory)
    legacy = tmp_path / "models/example"
    legacy.mkdir(parents=True)
    (legacy / "weights").write_bytes(payload)
    resolved = checkpoints.resolve("example", tmp_path)
    path = Path(resolved["root"]) / "weights"
    assert path.parent.name == "pinned-revision"
    assert path.read_bytes() == payload
    path.write_bytes(b"changed")
    with pytest.raises(ValueError, match="verification failed"):
        checkpoints.resolve("example", tmp_path)
    assert json.loads(inventory.read_text())["example"] == record


def test_checkpoint_rejects_wrong_legacy_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        checkpoints,
        "expected",
        lambda _="example": {"repository": "owner/model", "revision": "expected"},
    )
    legacy = tmp_path / "models/example"
    legacy.mkdir(parents=True)
    (legacy / "provenance.json").write_text(
        json.dumps({"repository": "owner/model", "revision": "wrong"})
    )
    with pytest.raises(ValueError, match="provenance disagrees"):
        checkpoints.resolve("example", tmp_path)


def test_embedding_reuse_checks_identity_shapes_and_bytes(tmp_path: Path) -> None:
    contract = {
        "model": "fixture",
        "tickers": ["A", "B"],
        "readouts": ["late"],
        "source": "first",
        "runtime": "one",
    }
    path = cache.location(tmp_path, contract)
    values = {"late": np.arange(6, dtype=float).reshape(2, 3)}
    cache.save(path, contract, values)
    np.testing.assert_array_equal(cache.load(path, contract)["late"], values["late"])
    for change in ({"tickers": ["B", "A"]}, {"source": "second"}, {"runtime": "two"}):
        changed = contract | change
        assert cache.location(tmp_path, changed) != path
        with pytest.raises(ValueError, match="identity or checksum"):
            cache.load(path, changed)
    metadata = json.loads(path.with_suffix(".json").read_text())
    metadata["shapes"]["late"] = [1, 6]
    path.with_suffix(".json").write_text(json.dumps(metadata))
    with pytest.raises(ValueError, match="Invalid embedding shape"):
        cache.load(path, contract)
    cache.save(path, contract, values)
    path.write_bytes(path.read_bytes() + b"altered")
    with pytest.raises(ValueError, match="identity or checksum"):
        cache.load(path, contract)


def test_missing_embedding_metadata_is_not_silently_trusted(tmp_path: Path) -> None:
    contract = {"model": "fixture", "tickers": ["A", "B"], "readouts": ["late"]}
    path = cache.location(tmp_path, contract)
    path.parent.mkdir(parents=True)
    np.savez(path, late=np.ones((2, 3)))
    with pytest.raises(FileNotFoundError):
        cache.load(path, contract)


def test_actual_adapter_and_runtime_changes_invalidate_states(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from types import SimpleNamespace  # noqa: PLC0415 -- fixture only.

    from free_foundations.representations.encoding import Prepared  # noqa: PLC0415

    root = tmp_path / "src/free_foundations"
    for name in cache.SOURCES:
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("original adapter")
    (tmp_path / "uv.lock").write_text("locked dependencies")
    monkeypatch.setattr(cache, "__file__", str(root / "representations/cache.py"))
    package = SimpleNamespace(version="one", read_text=lambda _name="direct_url.json": "null")
    monkeypatch.setattr(cache, "distribution", lambda _name="torch": package)
    data = Prepared(
        np.ones((3, 2)),
        np.ones((2, 2)),
        np.ones(3),
        ("X", "Y"),
        ("S1", "S2", "S3"),
        ("A", "B"),
        2020,
        "prepared",
    )
    checkpoint = {
        "repository": "test/model",
        "revision": "pinned",
        "sha256": {"weights": "verified"},
    }
    monkeypatch.setattr(cache, "inference_device", lambda: "cpu")
    original = cache.identity(data, "tabpfn_full", checkpoint)
    monkeypatch.setattr(cache, "inference_device", lambda: "cuda")
    gpu = cache.identity(data, "tabpfn_full", checkpoint)
    assert cache.location(tmp_path, original) != cache.location(tmp_path, gpu)
    assert gpu["execution"]["device"] == "cuda"
    monkeypatch.setattr(cache, "inference_device", lambda: "cpu")
    (root / "representations/encoding.py").write_text("changed extraction")
    changed = cache.identity(data, "tabpfn_full", checkpoint)
    assert cache.location(tmp_path, original) != cache.location(tmp_path, changed)
    package.version = "two"
    updated = cache.identity(data, "tabpfn_full", checkpoint)
    assert cache.location(tmp_path, changed) != cache.location(tmp_path, updated)


def test_nonfinite_embedding_payload_is_rejected(tmp_path: Path) -> None:
    contract = {"model": "fixture", "tickers": ["A", "B"], "readouts": ["late"]}
    with pytest.raises(ValueError, match="Invalid embedding shape or values"):
        cache.save(
            cache.location(tmp_path, contract), contract, {"late": np.array([[1.0], [np.nan]])}
        )
