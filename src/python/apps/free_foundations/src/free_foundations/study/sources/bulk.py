"""Official SEC nightly bulk snapshots, retaining archives and candidate-only JSON."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import re
import shutil
import struct
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from free_foundations.artifacts.atomic import atomic_bytes, atomic_output
from free_foundations.study.sources.sec import _json, _pace, source_root
from free_foundations.study.spec import file_hash

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

URLS = {
    "companyfacts": "https://www.sec.gov/Archives/edgar/daily-index/xbrl/companyfacts.zip",
    "submissions": "https://www.sec.gov/Archives/edgar/daily-index/bulkdata/submissions.zip",
}
MAX_ARCHIVE_BYTES = 10_000_000_000
_MEMBER = re.compile(r"CIK(\d{10})(-submissions-\d+)?\.json\Z")


def _kind(kind: str) -> str:
    if kind not in URLS:
        message = f"Unknown official SEC bulk snapshot: {kind}."
        raise ValueError(message)
    return kind


def _check_size(size: int, *, free: int | None = None) -> None:
    if size > MAX_ARCHIVE_BYTES or (free is not None and free < size * 2):
        message = "SEC bulk archive exceeds the size limit or available disk reserve."
        raise ValueError(message)


def _gzip_member(archive: Path, member: zipfile.ZipInfo, content: bytes) -> bytes:
    """Reuse verified SEC deflate bytes with a deterministic gzip header and CRC trailer."""
    if member.compress_type != zipfile.ZIP_DEFLATED:
        return gzip.compress(content, mtime=0)
    with archive.open("rb") as stream:
        stream.seek(member.header_offset)
        header = stream.read(30)
        if len(header) != 30 or header[:4] != b"PK\x03\x04":
            message = "SEC ZIP has an invalid local member header."
            raise ValueError(message)
        name_length, extra_length = struct.unpack("<HH", header[26:30])
        stream.seek(name_length + extra_length, os.SEEK_CUR)
        deflate = stream.read(member.compress_size)
    if len(deflate) != member.compress_size:
        message = "SEC ZIP has a truncated compressed member."
        raise ValueError(message)
    return (
        b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x00\xff"
        + deflate
        + struct.pack("<II", member.CRC, member.file_size & 0xFFFFFFFF)
    )


def register_archive(
    archive: Path, kind: str, *, headers: Mapping[str, str] | None = None
) -> dict[str, Any]:
    """Validate and hash a completed official ZIP, including externally streamed bytes."""
    record = _archive_record(archive, kind, headers=headers)
    _json(archive.with_suffix(".zip.metadata.json"), record)
    return record


def _archive_record(
    archive: Path, kind: str, *, headers: Mapping[str, str] | None = None
) -> dict[str, Any]:
    _kind(kind)
    normalized = {name.lower(): value for name, value in (headers or {}).items()}
    size = archive.stat().st_size
    if not 0 < size <= MAX_ARCHIVE_BYTES:
        message = "SEC bulk ZIP is empty or exceeds the explicit 10 GB archive limit."
        raise ValueError(message)
    expected = normalized.get("content-length")
    if expected is not None and int(expected) != size:
        message = "SEC bulk ZIP length differs from the HTTP response."
        raise ValueError(message)
    with zipfile.ZipFile(archive) as snapshot:
        members = len(snapshot.infolist())
        if not members:
            message = "SEC bulk ZIP has no members."
            raise ValueError(message)
    return {
        "url": URLS[kind],
        "status": "acquired",
        "http_status": 200,
        "retrieved_at": datetime.now(UTC).isoformat(),
        "file": str(archive),
        "bytes": size,
        "sha256": file_hash(archive),
        "members": members,
        "headers": normalized,
        "validation": "central-directory; selected members also checked by ZIP CRC and JSON parser",
    }


def download_archive(
    output: Path,
    kind: str,
    identity: str | None,
    *,
    client: httpx.Client | None = None,
    offline: bool = False,
) -> Path:
    """Stream one official ZIP to disk; failed partial responses never become snapshots."""
    _kind(kind)
    folder = source_root(output) / "bulk/raw"
    folder.mkdir(parents=True, exist_ok=True)
    archive = folder / f"{kind}.zip"
    if archive.exists():
        metadata = archive.with_suffix(".zip.metadata.json")
        if metadata.exists():
            record = json.loads(metadata.read_text())
            if record["sha256"] != file_hash(archive):
                message = "SEC bulk archive differs from its recorded content hash."
                raise ValueError(message)
        else:
            register_archive(archive, kind)
        return archive
    if offline:
        message = f"Official SEC bulk archive is unavailable offline: {kind}."
        raise FileNotFoundError(message)
    identity = (identity or os.environ.get("EDGAR_IDENTITY", "")).strip()
    if not identity:
        message = "SEC bulk downloads require a descriptive EDGAR identity."
        raise ValueError(message)
    owned = client is None
    session = client or httpx.Client(timeout=120, follow_redirects=False)
    record: dict[str, Any] = {"url": URLS[kind], "file": str(archive)}
    try:
        _pace()
        with (
            atomic_output(archive) as temporary,
            session.stream(
                "GET", URLS[kind], headers={"User-Agent": identity, "Accept-Encoding": "identity"}
            ) as response,
        ):
            record["http_status"] = response.status_code
            response.raise_for_status()
            expected = int(response.headers.get("content-length", "0"))
            _check_size(expected, free=shutil.disk_usage(folder).free)
            size = 0
            with temporary.open("wb") as stream:
                for block in response.iter_bytes(1024 * 1024):
                    size += len(block)
                    _check_size(size)
                    stream.write(block)
            record = _archive_record(temporary, kind, headers=response.headers)
        record["file"] = str(archive)
        _json(archive.with_suffix(".zip.metadata.json"), record)
    except (httpx.HTTPError, OSError, ValueError, zipfile.BadZipFile) as error:
        record.update(status="download_failed", error=type(error).__name__)
        _json(archive.with_suffix(".zip.error.json"), record)
        raise
    finally:
        if owned:
            session.close()
    return archive


def extract_candidates(
    output: Path, kind: str, candidate_ciks: Iterable[int], *, archive: Path | None = None
) -> dict[str, Any]:
    """Extract only candidate JSON, deterministically gzipped, into separate bulk staging."""
    _kind(kind)
    root = source_root(output)
    archive = archive or root / "bulk/raw" / f"{kind}.zip"
    record_path = archive.with_suffix(".zip.metadata.json")
    record = (
        json.loads(record_path.read_text())
        if record_path.exists()
        else register_archive(archive, kind)
    )
    if record["sha256"] != file_hash(archive):
        message = "SEC bulk archive differs from its recorded content hash."
        raise ValueError(message)
    ciks = {int(cik) for cik in candidate_ciks}
    if any(not 0 < cik < 10**10 for cik in ciks):
        message = "Candidate CIKs must be positive integers fitting ten digits."
        raise ValueError(message)
    folder = root / "bulk/extracted" / kind
    folder.mkdir(parents=True, exist_ok=True)
    files: list[dict[str, Any]] = []
    present: set[int] = set()
    seen: set[str] = set()
    with zipfile.ZipFile(archive) as snapshot:
        for member in snapshot.infolist():
            match = _MEMBER.fullmatch(member.filename)
            if match is None or int(match[1]) not in ciks:
                continue
            cik = int(match[1])
            if kind == "companyfacts" and match[2] is not None:
                continue
            if member.filename in seen:
                message = "Official SEC ZIP contains duplicate candidate member names."
                raise ValueError(message)
            seen.add(member.filename)
            content = snapshot.read(member)
            decoded = json.loads(content)
            if not isinstance(decoded, dict) or ("cik" in decoded and int(decoded["cik"]) != cik):
                message = "SEC bulk member is not a JSON object with consistent CIK identity."
                raise ValueError(message)
            if match[2] is None:
                present.add(cik)
            name = f"{cik:010}.json" if kind == "companyfacts" else member.filename
            destination = folder / (name + ".gz")
            compressed = _gzip_member(archive, member, content)
            atomic_bytes(destination, compressed)
            receipt = {
                "url": URLS[kind],
                "status": "extracted_official_bulk",
                "file": str(destination),
                "sha256": hashlib.sha256(content).hexdigest(),
                "stored_sha256": hashlib.sha256(compressed).hexdigest(),
                "uncompressed_bytes": len(content),
                "bytes": len(compressed),
                "archive_sha256": record["sha256"],
                "archive_member": member.filename,
                "archive_member_crc": member.CRC,
                "retrieved_at": record["retrieved_at"],
            }
            _json(destination.with_suffix(".gz.metadata.json"), receipt)
            files.append(receipt)
    manifest = {
        "status": "complete",
        "kind": kind,
        "archive": record,
        "candidate_ciks": sorted(ciks),
        "present_ciks": sorted(present),
        "absent_ciks": sorted(ciks - present),
        "files": files,
        "absence_meaning": "not present in this complete official nightly bulk snapshot",
    }
    _json(root / "bulk" / f"{kind}-manifest.json", manifest)
    return manifest


def install_candidates(output: Path, kind: str) -> dict[str, Any]:
    """Atomically install staged JSON without replacing any existing raw cache response."""
    _kind(kind)
    root = source_root(output)
    manifest = json.loads((root / "bulk" / f"{kind}-manifest.json").read_text())
    installed, preserved = 0, 0
    for receipt in manifest["files"]:
        source = Path(receipt["file"])
        if file_hash(source) != receipt["stored_sha256"]:
            message = "Staged SEC bulk JSON differs from its recorded content hash."
            raise ValueError(message)
        destination = root / kind / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.with_suffix("").exists() or destination.exists():
            preserved += 1
            continue
        try:
            os.link(source.resolve(strict=True), destination)
        except FileExistsError:
            preserved += 1
            continue
        _json(destination.with_suffix(".gz.metadata.json"), {**receipt, "file": str(destination)})
        installed += 1
    result = {
        "status": "installed",
        "kind": kind,
        "installed": installed,
        "preserved": preserved,
        "url": manifest["archive"]["url"],
        "archive_sha256": manifest["archive"]["sha256"],
        "retrieved_at": manifest["archive"]["retrieved_at"],
        "absent_ciks": manifest["absent_ciks"],
    }
    _json(root / "bulk" / f"{kind}-installed.json", result)
    return result


def acquire_bulk(
    output: Path, candidate_ciks: Iterable[int], identity: str | None, *, offline: bool = False
) -> dict[str, Any]:
    """Reuse or acquire official snapshots before per-CIK metadata; never invent missing JSON."""
    root = source_root(output)
    ciks = sorted({int(cik) for cik in candidate_ciks})
    archives: dict[str, dict[str, Any]] = {}
    for kind, url in URLS.items():
        archive = root / "bulk/raw" / f"{kind}.zip"
        if offline and not archive.exists():
            archives[kind] = {"status": "not_acquired_offline", "url": url}
            continue
        try:
            archive = download_archive(root, kind, identity, offline=offline)
            raw = json.loads(archive.with_suffix(".zip.metadata.json").read_text())
            manifest_path = root / "bulk" / f"{kind}-manifest.json"
            manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
            if not (
                manifest.get("status") == "complete"
                and manifest.get("candidate_ciks") == ciks
                and manifest.get("archive", {}).get("sha256") == raw["sha256"]
                and all(Path(row["file"]).exists() for row in manifest.get("files", []))
            ):
                manifest = extract_candidates(root, kind, ciks, archive=archive)
            installed = install_candidates(root, kind)
            archives[kind] = {
                **installed,
                "archive": raw,
                "present_ciks": len(manifest["present_ciks"]),
                "absent_ciks": len(manifest["absent_ciks"]),
                "extracted_files": len(manifest["files"]),
            }
        except (httpx.HTTPError, OSError, ValueError, zipfile.BadZipFile) as error:
            archives[kind] = {
                "status": "bulk_unavailable",
                "url": url,
                "error": type(error).__name__,
            }
    result = {
        "status": "installed"
        if all(row["status"] == "installed" for row in archives.values())
        else "partial",
        "candidate_ciks": ciks,
        "archives": archives,
    }
    _json(root / "bulk/acquisition.json", result)
    return result
