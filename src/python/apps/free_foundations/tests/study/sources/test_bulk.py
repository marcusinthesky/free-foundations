"""Tiny official-shape ZIP fixtures exercise selective bulk metadata ingestion."""

import gzip
import hashlib
import io
import json
import zipfile
from pathlib import Path

import httpx
import pytest

from free_foundations.study.sources import bulk, sec


def _archive(path: Path, members: dict[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, value in members.items():
            archive.writestr(name, json.dumps(value))
    return path


def test_selective_extraction_retains_zip_and_exact_member_hashes(tmp_path: Path) -> None:
    archive = _archive(
        tmp_path / "sec/bulk/raw/submissions.zip",
        {
            "CIK0000000042.json": {"cik": "42", "filings": {}},
            "CIK0000000042-submissions-001.json": {"accessionNumber": ["historic"]},
            "CIK0000000099.json": {"cik": "99"},
            "../CIK0000000042.json": {"cik": "42"},
        },
    )
    original = archive.read_bytes()
    registered = bulk.register_archive(archive, "submissions", headers={"ETag": "nightly-vintage"})
    manifest = bulk.extract_candidates(tmp_path, "submissions", [42, 17])
    assert manifest["status"] == "complete"
    assert manifest["present_ciks"] == [42]
    assert manifest["absent_ciks"] == [17]
    assert len(manifest["files"]) == 2
    assert registered["headers"]["etag"] == "nightly-vintage"
    assert archive.read_bytes() == original
    assert registered["sha256"] == hashlib.sha256(original).hexdigest()
    for receipt in manifest["files"]:
        saved = Path(receipt["file"])
        payload = gzip.decompress(saved.read_bytes())
        assert receipt["sha256"] == hashlib.sha256(payload).hexdigest()
        assert saved.read_bytes()[4:8] == b"\0\0\0\0"
    assert not (tmp_path / "CIK0000000042.json").exists()
    assert not list((tmp_path / "sec/submissions").glob("*"))


def test_install_preserves_existing_raw_cache_and_resolves_snapshot_absence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _archive(
        tmp_path / "sec/bulk/raw/companyfacts.zip",
        {"CIK0000000042.json": {"cik": 42, "facts": {}}},
    )
    bulk.extract_candidates(tmp_path, "companyfacts", [42, 17])
    existing = tmp_path / "sec/companyfacts/0000000042.json"
    existing.parent.mkdir(parents=True)
    existing.write_text('{"cik":42,"facts":{},"existing":true}')
    before = existing.read_bytes()
    installed = bulk.install_candidates(tmp_path, "companyfacts")
    assert installed["preserved"] == 1
    assert existing.read_bytes() == before
    _archive(tmp_path / "sec/bulk/raw/submissions.zip", {"CIK0000000099.json": {"cik": "99"}})
    bulk.extract_candidates(tmp_path, "submissions", [17])
    bulk.install_candidates(tmp_path, "submissions")

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("A validated bulk-snapshot absence triggered an API request.")

    monkeypatch.setattr(httpx, "get", forbidden)
    with sec.SECClient("test research contact@example.org") as client:
        filings, receipt = sec._metadata_cik(client, tmp_path / "sec", 17)  # noqa: SLF001 -- exercise bulk absence at the per-CIK metadata boundary.
    assert filings == []
    assert receipt["complete"]
    assert not receipt["companyfacts_available"]
    assert not receipt["submissions_available"]
    assert {record["status"] for record in client.records} == {"not_in_bulk_snapshot"}
    assert not (tmp_path / "sec/companyfacts/0000000017.json").exists()


def test_tampered_archive_and_staged_response_are_rejected(tmp_path: Path) -> None:
    archive = _archive(
        tmp_path / "sec/bulk/raw/companyfacts.zip", {"CIK0000000042.json": {"cik": 42}}
    )
    manifest = bulk.extract_candidates(tmp_path, "companyfacts", [42])
    staged = Path(manifest["files"][0]["file"])
    staged.write_bytes(gzip.compress(b'{"cik":99}', mtime=0))
    with pytest.raises(ValueError, match="Staged SEC bulk JSON"):
        bulk.install_candidates(tmp_path, "companyfacts")
    with archive.open("ab") as stream:
        stream.write(b"tampered")
    with pytest.raises(ValueError, match="recorded content hash"):
        bulk.extract_candidates(tmp_path, "companyfacts", [42])


def test_streamed_download_records_real_headers_without_buffering_whole_archive(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    content = io.BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        archive.writestr("CIK0000000042.json", '{"cik":42}')
    payload = content.getvalue()
    requests = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, content=payload, headers={"ETag": "official-vintage"})

    monkeypatch.setattr(bulk, "_pace", lambda: None)
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        archive = bulk.download_archive(tmp_path, "companyfacts", "Research contact", client=client)
        again = bulk.download_archive(tmp_path, "companyfacts", "Research contact", client=client)
    assert again == archive
    assert archive.read_bytes() == payload
    assert len(requests) == 1
    metadata = json.loads(archive.with_suffix(".zip.metadata.json").read_text())
    assert metadata["headers"]["etag"] == "official-vintage"
    assert requests[0].url == bulk.URLS["companyfacts"]
    assert not archive.with_suffix(".zip.partial").exists()


def test_failed_bulk_download_never_promotes_html_error_to_zip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(bulk, "_pace", lambda: None)
    with (
        httpx.Client(
            transport=httpx.MockTransport(lambda _request: httpx.Response(403, text="denied"))
        ) as client,
        pytest.raises(httpx.HTTPStatusError),
    ):
        bulk.download_archive(tmp_path, "submissions", "Research contact", client=client)
    archive = tmp_path / "sec/bulk/raw/submissions.zip"
    assert not archive.exists()
    assert json.loads(archive.with_suffix(".zip.error.json").read_text())["http_status"] == 403


def test_native_response_compression_preserves_parser_bytes_and_hash(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"<xbrl>exact SEC response bytes</xbrl>" * 20
    monkeypatch.setattr(sec, "_pace", lambda: None)
    destination = tmp_path / "sec/filings/0000000042/accession/instance.xml"
    with (
        httpx.Client(
            transport=httpx.MockTransport(lambda _request: httpx.Response(200, content=payload))
        ) as session,
        sec.SECClient("Research contact", client=session) as client,
    ):
        assert client.fetch("https://www.sec.gov/Archives/instance.xml", destination) == payload
        assert client.fetch("https://www.sec.gov/Archives/instance.xml", destination) == payload
    stored = destination.with_suffix(".xml.gz")
    assert not destination.exists()
    assert gzip.decompress(stored.read_bytes()) == payload
    assert stored.read_bytes()[4:8] == b"\0\0\0\0"
    metadata = json.loads(stored.with_suffix(".gz.metadata.json").read_text())
    assert metadata["sha256"] == hashlib.sha256(payload).hexdigest()
    assert metadata["stored_sha256"] == hashlib.sha256(stored.read_bytes()).hexdigest()
    assert client.records[-1]["status"] == "cached"


def test_compressed_current_facts_win_once_over_legacy_uncompressed(tmp_path: Path) -> None:
    folder = tmp_path / "sec/filings/0000000042/accession"
    folder.mkdir(parents=True)
    row = {"cik": 42, "concept": "dei:TradingSymbol", "value": "CURRENT", "accession": "a"}
    (folder / "facts.json").write_text(json.dumps([{**row, "value": "STALE"}]))
    (folder / "facts.json.gz").write_bytes(gzip.compress(json.dumps([row]).encode(), mtime=0))
    frame = sec.load_source_facts(tmp_path)
    assert len(frame) == 1
    assert frame.iloc[0]["value"] == "CURRENT"


def test_bulk_wrapper_offline_never_requests_missing_snapshots(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Offline bulk acquisition made a network request.")

    monkeypatch.setattr(httpx.Client, "stream", forbidden)
    result = bulk.acquire_bulk(tmp_path, [42], None, offline=True)
    assert result["status"] == "partial"
    assert {row["status"] for row in result["archives"].values()} == {"not_acquired_offline"}


def test_bulk_wrapper_reuses_cached_snapshots_and_installs_gzip(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for kind in bulk.URLS:
        _archive(tmp_path / "sec/bulk/raw" / f"{kind}.zip", {"CIK0000000042.json": {"cik": 42}})

    def forbidden(*_args: object, **_kwargs: object) -> None:
        pytest.fail("Cached official ZIP was fetched again.")

    monkeypatch.setattr(httpx.Client, "stream", forbidden)
    result = bulk.acquire_bulk(tmp_path, [42, 17], None, offline=True)
    assert result["status"] == "installed"
    assert (tmp_path / "sec/companyfacts/0000000042.json.gz").exists()
    assert (tmp_path / "sec/submissions/CIK0000000042.json.gz").exists()
    assert result["archives"]["companyfacts"]["absent_ciks"] == 1


def test_disk_reserve_stops_raw_write_without_creating_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sec, "_pace", lambda: None)
    monkeypatch.setattr(sec, "DISK_RESERVE_BYTES", 10**30)
    destination = tmp_path / "sec/filings/0000000042/accession/instance.xml"
    with (
        httpx.Client(
            transport=httpx.MockTransport(lambda _request: httpx.Response(200, content=b"raw"))
        ) as session,
        sec.SECClient("Research contact", client=session) as client,
        pytest.raises(OSError, match="free-space reserve"),
    ):
        client.fetch("https://www.sec.gov/Archives/instance.xml", destination)
    assert not destination.with_suffix(".xml.gz").exists()
    assert not destination.with_suffix(".xml.gz.partial").exists()
