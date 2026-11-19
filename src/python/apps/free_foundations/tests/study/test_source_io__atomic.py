"""Source refreshes must replace DVC links without modifying their cached bytes."""

from __future__ import annotations

import gzip
import io
import json
import os
import zipfile
from typing import TYPE_CHECKING

import pandas as pd
import pytest

from free_foundations.study import bulk, factors, linkage, sec
from free_foundations.study.source_io import atomic_bytes, atomic_copy, atomic_output
from tests._strategies import compact_spec

if TYPE_CHECKING:
    from pathlib import Path


def _freeze(path: Path, cache: Path, kind: str) -> tuple[Path, bytes]:
    """Model DVC's read-only file objects using real POSIX hardlinks and symlinks."""
    cache.mkdir(parents=True, exist_ok=True)
    frozen = cache / f"{len(list(cache.iterdir())):04d}-{path.name}"
    before = path.read_bytes()
    frozen.write_bytes(before)
    frozen.chmod(0o444)
    path.unlink()
    if kind == "hardlink":
        os.link(frozen, path)
    else:
        path.symlink_to(frozen)
    return frozen, before


def _assert_preserved(frozen: list[tuple[Path, bytes]]) -> None:
    for path, before in frozen:
        assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_atomic_replacement_keeps_open_old_inode_and_cache_bytes(tmp_path: Path, kind: str) -> None:
    destination = tmp_path / "response.json"
    destination.write_bytes(b"old official response")
    frozen = _freeze(destination, tmp_path / "cache", kind)
    with destination.open("rb") as reader:
        atomic_bytes(destination, b"new official response")
        assert reader.read() == b"old official response"
    assert destination.read_bytes() == b"new official response"
    assert not destination.is_symlink()
    assert not destination.samefile(frozen[0])
    _assert_preserved([frozen])
    source = tmp_path / "source.json"
    source.write_bytes(b"another official response")
    frozen = _freeze(destination, tmp_path / "cache", kind)
    atomic_copy(destination, source)
    assert destination.read_bytes() == source.read_bytes()
    _assert_preserved([frozen])


def test_interrupted_write_keeps_destination_and_removes_temporary(tmp_path: Path) -> None:
    destination = tmp_path / "ledger.json"
    destination.write_bytes(b"complete old ledger")

    def interrupted_write() -> None:
        with atomic_output(destination) as temporary:
            temporary.write_bytes(b"incomplete new ledger")
            message = "interrupted"
            raise RuntimeError(message)

    with pytest.raises(RuntimeError, match="interrupted"):
        interrupted_write()
    assert destination.read_bytes() == b"complete old ledger"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_sec_metadata_resume_preserves_every_frozen_source_object(
    tmp_path: Path, kind: str
) -> None:
    root = tmp_path / "sec"
    source = {
        "metadata/sec-tickers.json": '{"0":{"ticker":"ABC","cik_str":42}}',
        "companyfacts/0000000042.json": '{"cik":42,"facts":{}}',
        "submissions/CIK0000000042.json": '{"cik":"42","filings":{"recent":{}}}',
    }
    refreshed = {
        "acquisition.json": "{}",
        "metadata/candidate-ciks.json": "[]",
        "metadata/metadata-phase.json": "{}",
        "metadata/filings.json": "[]",
        "metadata/company-index/CIK0000000042.json": "{}",
        "metadata/progress/CIK0000000042.json": "{}",
        "metadata/progress/metadata/CIK0000000042.json": "{}",
        "metadata/progress.json": "{}",
    }
    for name, value in {**source, **refreshed}.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(value)
    (root / "crosswalk.csv").write_text("old frozen crosswalk\n")
    paths = [root / name for name in [*source, *refreshed, "crosswalk.csv"]]
    frozen = [_freeze(path, tmp_path / "cache", kind) for path in paths]
    monthly = pd.DataFrame(
        {"permno": [1], "permco": [2], "ticker": ["ABC"], "date": ["2020-03-31"]}
    )
    result = sec.acquire_sources(monthly, root, None, offline=True, metadata_only=True)
    assert result["status"] == "metadata_ready"
    assert result["metadata_complete"]
    assert "candidate_only" in (root / "crosswalk.csv").read_text()
    for name in [*refreshed, "crosswalk.csv"]:
        assert not (root / name).is_symlink()
    for name in source:
        assert (root / name).samefile(frozen[list(source).index(name)][0])
    _assert_preserved(frozen)


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_linkage_refresh_preserves_frozen_parquet_csv_and_manifest(
    tmp_path: Path, kind: str
) -> None:
    monthly = pd.DataFrame(
        {"permno": [1], "permco": [2], "ticker": ["ABC"], "date": ["2020-03-31"]}
    )
    root = tmp_path / "sec"
    linkage.materialize_linkage(monthly, root)
    destination = root / "metadata/historical-linkage"
    paths = sorted(destination.iterdir())
    frozen = [_freeze(path, tmp_path / "cache", kind) for path in paths]
    changed = monthly.assign(ticker="DEF")
    result = linkage.materialize_linkage(changed, root)
    assert result["coverage"].iloc[0]["ticker"] == "DEF"
    for path, (cached, _) in zip(paths, frozen, strict=True):
        assert not path.is_symlink()
        assert not path.samefile(cached)
    _assert_preserved(frozen)


def _factor_zip(columns: tuple[str, ...]) -> bytes:
    buffer = io.BytesIO()
    rows = ["Public research data", "," + ",".join(columns)]
    rows.extend(f"2001{month:02d}," + ",".join(["1"] * len(columns)) for month in range(1, 4))
    rows.append("")
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("research.csv", "\n".join(rows))
    return buffer.getvalue()


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_factor_refresh_preserves_frozen_zip_parquet_and_status(tmp_path: Path, kind: str) -> None:
    raw = [tmp_path / name for name in factors.FILES.values()]
    raw[0].write_bytes(_factor_zip(("Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF")))
    raw[1].write_bytes(_factor_zip(("Mom",)))
    derived = [tmp_path / "monthly.parquet", tmp_path / "quarterly.parquet"]
    for path in derived:
        pd.DataFrame({"old": [1]}).to_parquet(path, index=False)
    status = tmp_path / "status.json"
    status.write_text('{"status":"old"}')
    paths = [*raw, *derived, status]
    frozen = [_freeze(path, tmp_path / "cache", kind) for path in paths]
    spec = compact_spec("2001-01-01", "2001-03-31")
    assert factors.acquire_factors(tmp_path, spec, offline=True)
    assert len(pd.read_parquet(derived[0])) == 3
    assert len(pd.read_parquet(derived[1])) == 1
    assert json.loads(status.read_text())["status"] == "complete"
    for path, (cached, _) in zip(paths, frozen, strict=True):
        if path in raw:
            assert path.samefile(cached)
        else:
            assert not path.is_symlink()
            assert not path.samefile(cached)
    _assert_preserved(frozen)


@pytest.mark.parametrize("kind", ["hardlink", "symlink"])
def test_bulk_resume_installs_from_frozen_staging_without_copying_or_mutating_zip(
    tmp_path: Path, kind: str
) -> None:
    root = tmp_path / "sec"
    archive = root / "bulk/raw/companyfacts.zip"
    archive.parent.mkdir(parents=True)
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as snapshot:
        snapshot.writestr("CIK0000000042.json", '{"cik":42,"facts":{}}')
    bulk.extract_candidates(root, "companyfacts", [42, 17])
    paths = sorted(path for path in (root / "bulk").rglob("*") if path.is_file())
    frozen = [_freeze(path, tmp_path / "cache", kind) for path in paths]
    result = bulk.acquire_bulk(root, [42, 17], None, offline=True)
    assert result["archives"]["companyfacts"]["status"] == "installed"
    installed = root / "companyfacts/0000000042.json.gz"
    assert json.loads(gzip.decompress(installed.read_bytes())) == {"cik": 42, "facts": {}}
    for path, (cached, _) in zip(paths, frozen, strict=True):
        assert path.samefile(cached)
    _assert_preserved(frozen)
