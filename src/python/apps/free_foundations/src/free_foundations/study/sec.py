"""Resumable public SEC evidence, with raw responses and explicit acquisition failures."""

from __future__ import annotations

import errno
import fcntl
import gzip
import hashlib
import io
import json
import logging
import math
import os
import re
import shutil
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self, override
from urllib.parse import quote, urlparse

import httpx
import pandas as pd

from free_foundations.study.source_io import atomic_bytes, atomic_copy, atomic_csv

if TYPE_CHECKING:
    from types import TracebackType

API_VERSION = "sec-evidence-v1"
PARSER_VERSION = "native-xbrl-v2-narrative-types"
NARRATIVE_MARKUP_PATTERN = (
    r"(?:<|&lt;)\s*/?\s*(?:div|p|table|thead|tbody|tfoot|tr|td|th|ul|ol|li|"
    r"h[1-6]|blockquote|pre|section|article|span|br|font|b|i|strong|em|a)"
    r"(?:\s|/?>|/?&gt;)"
)
_BLOCK_MARKUP = {"div", "p", "table", "ul", "ol", "li", "blockquote", "pre", "section", "article"}
LOGGER = logging.getLogger(__name__)
_DEFAULT_HTTP_GET = httpx.get
DISK_RESERVE_BYTES = 2_000_000_000
SEC_REQUESTS_PER_SECOND = 5
FORMS = {"10-K", "10-K/A", "10-Q", "10-Q/A", "10-KT", "10-KT/A", "10-QT", "10-QT/A"}
FACT_COLUMNS = [
    "cik",
    "concept",
    "namespace",
    "tag",
    "unit",
    "value",
    "value_type",
    "raw_value",
    "start",
    "end",
    "filed",
    "accepted",
    "accession",
    "form",
    "dimensions",
    "context_id",
    "entity_identifier",
    "decimals",
    "scale",
    "source_url",
    "source_kind",
    "source_sha256",
    "status",
]
CROSSWALK_COLUMNS = [
    "permno",
    "permco",
    "ticker",
    "cik",
    "effective_from",
    "effective_to",
    "status",
    "evidence_url",
    "accession",
    "evidence_type",
    "reason",
    "corroborating_accessions",
    "evidence_json",
    "segment_start",
    "segment_end",
    "attestations",
    "max_gap_days",
]


def _json(destination: Path, value: object) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, allow_nan=False, default=str) + "\n").encode()
    encoded = gzip.compress(payload, mtime=0) if destination.suffix == ".gz" else payload
    if destination.suffix == ".gz":
        _disk_reserve(destination.parent, len(encoded))
    atomic_bytes(destination, encoded)


def _response_bytes(filename: Path) -> bytes:
    payload = filename.read_bytes()
    return gzip.decompress(payload) if filename.suffix == ".gz" else payload


def _disk_reserve(folder: Path, size: int) -> None:
    if shutil.disk_usage(folder).free < size + DISK_RESERVE_BYTES:
        message = "SEC acquisition stopped to preserve the 2 GB free-space reserve."
        raise OSError(errno.ENOSPC, message, str(folder))


def _cache_path(destination: Path) -> Path:
    compressed = destination.with_suffix(destination.suffix + ".gz")
    if compressed.exists() and compressed.stat().st_size < 1024:
        try:
            marker = json.loads(_response_bytes(compressed))
        except (OSError, ValueError):
            marker = None
        if isinstance(marker, dict) and marker.get("source_status") == 404:
            return destination  # A copied historical absence marker remains retryable.
    return compressed if compressed.exists() else destination


def _response_path(destination: Path) -> Path:
    if destination.suffix != ".gz" and any(
        name in destination.parts for name in ("companyfacts", "submissions", "filings")
    ):
        return destination.with_suffix(destination.suffix + ".gz")
    return destination


def _json_files(folder: Path, pattern: str) -> list[Path]:
    """Choose one logical JSON response, preferring a compressed current response."""
    files = {str(path): path for path in folder.glob(pattern)}
    files.update({str(path.with_suffix("")): path for path in folder.glob(pattern + ".gz")})
    return [
        files[key]
        for key in sorted(files)
        if not files[key].name.endswith((".metadata.json", ".error.json"))
    ]


def _store_response(stored: Path, payload: bytes) -> dict[str, Any]:
    stored.parent.mkdir(parents=True, exist_ok=True)
    encoded = gzip.compress(payload, mtime=0) if stored.suffix == ".gz" else payload
    _disk_reserve(stored.parent, len(encoded))
    atomic_bytes(stored, encoded)
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "stored_sha256": hashlib.sha256(encoded).hexdigest(),
        "uncompressed_bytes": len(payload),
        "bytes": len(encoded),
        "compression": "gzip-mtime-0" if stored.suffix == ".gz" else "none",
    }


def source_root(output: Path) -> Path:
    """Accept either the study output directory or its SEC source directory."""
    return output if output.name == "sec" else output / "sec"


def _pace() -> None:
    """Share a five-requests/second ceiling across this user's local SEC processes."""
    pace_directory = Path(tempfile.gettempdir()) / f"free-foundations-sec-{os.getuid()}"
    pace_directory.mkdir(mode=0o700, exist_ok=True)
    pace_file = pace_directory / "request-pace"
    descriptor = os.open(pace_file, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(descriptor, "r+") as handle:
        fcntl.flock(handle, fcntl.LOCK_EX)
        handle.seek(0)
        previous = handle.read().strip()
        delay = 1 / SEC_REQUESTS_PER_SECOND - (time.time() - float(previous or "0"))
        if delay > 0:
            time.sleep(delay)
        handle.seek(0)
        handle.truncate()
        handle.write(str(time.time()))
        handle.flush()


class SECClient:
    """Keep successful raw responses; failed responses remain retryable evidence."""

    def __init__(
        self, identity: str | None, *, offline: bool = False, client: httpx.Client | None = None
    ) -> None:
        """Defer identity requirements until an actual network operation."""
        self.identity = (identity or os.environ.get("EDGAR_IDENTITY", "")).strip()
        self.offline = offline
        self.records: list[dict[str, Any]] = []
        self.denials: dict[str, int] = {}
        self.blocked_hosts: set[str] = set()
        self._client = client
        self._owns_client = client is None
        self.bulk_absences: dict[str, dict[str, Any]] = {}

    def __enter__(self) -> Self:
        """Scope the persistent connection pool to one acquisition pass."""
        return self

    def __exit__(
        self,
        _kind: type[BaseException] | None,
        _error: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        """Release owned HTTP connections on success, errors or interruption."""
        self.close()

    def close(self) -> None:
        """Close only a connection pool owned by this client; injected pools stay external."""
        if self._client is not None and self._owns_client:
            self._client.close()

    def _request(self, url: str) -> httpx.Response:
        # Keep the existing module-level HTTP interception seam for offline fixtures
        # and instrumentation. Production requests share one persistent connection pool.
        if self._client is None and httpx.get is not _DEFAULT_HTTP_GET:
            return httpx.get(
                url,
                headers={"User-Agent": self.identity, "Accept-Encoding": "gzip, deflate"},
                timeout=45,
                follow_redirects=False,
            )
        if self._client is None:
            self._client = httpx.Client(timeout=45, follow_redirects=False)
        return self._client.get(
            url, headers={"User-Agent": self.identity, "Accept-Encoding": "gzip, deflate"}
        )

    def fetch(self, url: str, destination: Path) -> bytes | None:  # noqa: C901, PLR0912 -- retry and circuit states remain together.
        """Retrieve SEC content without turning transport failures into absent filings."""
        cached = _cache_path(destination)
        if cached.is_file():
            payload = _response_bytes(cached)
            self.records.append({"url": url, "status": "cached", "file": str(cached)})
            return payload
        host = urlparse(url).hostname or ""
        if host in self.blocked_hosts:
            self.records.append({"url": url, "status": "blocked_host", "file": str(destination)})
            return None
        if self.offline or not self.identity:
            status = "not_acquired_offline" if self.offline else "identity_required"
            self.records.append({"url": url, "status": status, "file": str(destination)})
            return None
        if urlparse(url).hostname not in {"www.sec.gov", "data.sec.gov", "www.archives.gov"}:
            message = "SEC acquisition accepts official SEC/archive hosts only."
            raise ValueError(message)
        stored = _response_path(destination)
        record: dict[str, Any] = {"url": url, "file": str(stored)}
        for attempt in range(4):
            _pace()
            try:
                response = self._request(url)
            except httpx.RequestError as error:
                record.update(status="network_error", error=type(error).__name__)
            else:
                record["http_status"] = response.status_code
                if response.status_code == 200:
                    self.denials[host] = 0
                    record.update(
                        _store_response(stored, response.content),
                        status="acquired",
                        retrieved_at=datetime.now(UTC).isoformat(),
                    )
                    _json(stored.with_suffix(stored.suffix + ".metadata.json"), record)
                    self.records.append(record)
                    return response.content
                if response.status_code == 404:
                    self.denials[host] = 0
                    record["status"] = "http_not_found"
                    break
                record["status"] = "access_denied" if response.status_code == 403 else "http_error"
                if response.status_code not in {403, 408, 429, 500, 502, 503, 504}:
                    break
            if attempt < 3:
                time.sleep(2**attempt)
        self.records.append(record)
        if record.get("http_status") == 403:
            self.denials[host] = self.denials.get(host, 0) + 1
            if self.denials[host] >= 3:
                self.blocked_hosts.add(host)
        else:
            self.denials[host] = 0
        _json(destination.with_suffix(destination.suffix + ".error.json"), record)
        return None

    def json(self, url: str, destination: Path) -> dict[str, Any] | None:
        """Parse a raw JSON response, preserving malformed content for diagnosis."""
        payload = self.fetch(url, destination)
        if payload is None:
            return None
        try:
            decoded = json.loads(payload)
        except (ValueError, UnicodeError):
            self.records.append({"url": url, "status": "parse_error", "file": str(destination)})
            return None
        if not isinstance(decoded, dict):
            self.records.append({"url": url, "status": "parse_error", "file": str(destination)})
            return None
        return decoded


def _local(name: str) -> str:
    return name.rsplit("}", 1)[-1].rsplit(":", 1)[-1].lower()


class _InlineHTML(HTMLParser):
    """Retain embedded inline-XBRL structures when issuer HTML is not valid XHTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = ET.Element("html")
        self.stack = [self.root]
        self.namespaces: dict[str, str] = {}

    @override
    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name: value or "" for name, value in attrs}
        for name, value in attributes.items():
            if name.startswith("xmlns:"):
                self.namespaces[name.split(":", 1)[1]] = value
        element = ET.SubElement(self.stack[-1], tag, attributes)
        if tag not in {"br", "hr", "img", "input", "link", "meta", "wbr", "source"}:
            self.stack.append(element)

    @override
    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack[-1].tag == tag:
            self.stack.pop()

    @override
    def handle_endtag(self, tag: str) -> None:
        for position in range(len(self.stack) - 1, 0, -1):
            if self.stack[position].tag == tag:
                del self.stack[position:]
                break

    @override
    def handle_data(self, data: str) -> None:
        element = self.stack[-1]
        if len(element):
            element[-1].tail = (element[-1].tail or "") + data
        else:
            element.text = (element.text or "") + data


def _attr(element: ET.Element, name: str, default: str = "") -> str:
    return next(
        (value for key, value in element.attrib.items() if _local(key) == name.lower()), default
    )


def _text(element: ET.Element) -> str:
    chunks = [element.text or ""]
    for child in element:
        if _local(child.tag) != "exclude":
            chunks.append(_text(child))
        chunks.append(child.tail or "")
    return "".join(chunks).strip()


def _number(value: str, element: ET.Element) -> float | None:
    if _attr(element, "nil").lower() == "true":
        return None
    cleaned = re.sub(r"[\s\u00a0$€£]", "", value)
    if cleaned in {"-", "\u2014", "\u2013"} and "dash" in _attr(element, "format").lower():
        return 0.0
    if "commadecimal" in _attr(element, "format").lower():
        cleaned = cleaned.replace(".", "").replace(",", ".")
    else:
        cleaned = cleaned.replace(",", "")
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]
    try:
        number = float(cleaned) * 10 ** int(_attr(element, "scale", "0"))
    except (ValueError, OverflowError):
        return None
    if _attr(element, "sign") == "-":
        number = -number
    return number if float("-inf") < number < float("inf") else None


def is_narrative_fact(
    concept: str, value: object, *, declared_type: str = "", has_block_markup: bool = False
) -> bool:
    """Identify explicit text blocks and HTML content, without a categorical-length cutoff."""
    return bool(
        "textblock" in declared_type.lower()
        or concept.rsplit(":", 1)[-1].lower().endswith("textblock")
        or has_block_markup
        or re.search(NARRATIVE_MARKUP_PATTERN, str(value), re.IGNORECASE)
    )


def _has_block_markup(element: ET.Element) -> bool:
    if _local(element.tag) == "exclude":
        return False
    return _local(element.tag) in _BLOCK_MARKUP or any(
        _has_block_markup(child) for child in element
    )


def scalar_fact_types(frame: pd.DataFrame) -> pd.Series:
    """Classify cached narrative and align missing scalar types to their concept/unit evidence."""
    kinds = frame["value_type"].copy()
    narrative = frame["concept"].fillna("").astype(str).str.lower().str.endswith("textblock")
    narrative |= kinds.eq("narrative")
    for name in ("xbrl_type", "type"):
        if name in frame:
            narrative |= frame[name].fillna("").astype(str).str.contains("textblock", case=False)
    candidates = kinds.eq("categorical") & ~narrative
    for name in ("value", "raw_value"):
        if name in frame:
            narrative.loc[candidates] |= (
                frame.loc[candidates, name]
                .astype(str)
                .str.contains(NARRATIVE_MARKUP_PATTERN, case=False, regex=True)
            )
    kinds.loc[narrative] = "narrative"
    keys = ["concept", "unit"]
    observed = frame["value"].notna() & kinds.isin(["numeric", "categorical"])
    known = frame.loc[observed, keys].copy()
    known["value_type"] = kinds.loc[observed]
    known = known.drop_duplicates()
    if known.duplicated(keys).any():
        message = "One SEC concept/unit has conflicting observed numeric and categorical types."
        raise ValueError(message)
    missing = frame["value"].isna() & kinds.isin(["numeric", "categorical"])
    if missing.any():
        lookup = known.set_index(keys)["value_type"]
        inferred = lookup.reindex(pd.MultiIndex.from_frame(frame.loc[missing, keys]))
        fallback = kinds.loc[missing].copy()
        # A reported XBRL unit, including pure, identifies an all-nil numeric item;
        # observed categorical values for the same concept/unit take precedence.
        fallback.loc[frame.loc[missing, "unit"].fillna("").ne("")] = "numeric"
        kinds.loc[missing] = inferred.fillna(
            pd.Series(fallback.to_numpy(), index=inferred.index)
        ).to_numpy()
    return kinds


def parse_xbrl(  # noqa: C901, PLR0912, PLR0913, PLR0915 -- one provenance-aware parser boundary.
    content: bytes,
    *,
    cik: int,
    accession: str = "",
    filed: str = "",
    accepted: str = "",
    source_url: str = "",
    form: str = "",
) -> list[dict[str, Any]]:
    """Archive native facts, contexts and units with explicit narrative classification.

    Custom namespaces and dimensional facts are retained, rather than flattened into
    entity-wide standard concepts. Reported nils and unparsable numbers remain missing.
    """
    if re.search(rb"<!\s*ENTITY", content.replace(b"\x00", b""), re.IGNORECASE):
        message = "Entity declarations are not accepted in SEC XBRL documents."
        raise ValueError(message)
    namespaces: dict[str, str] = {}
    try:
        for _, pair in ET.iterparse(io.BytesIO(content), events=("start-ns",)):  # noqa: S314 -- entity declarations rejected above.
            namespaces[pair[0]] = pair[1]
        root = ET.fromstring(content)  # noqa: S314 -- entity declarations rejected above.
    except ET.ParseError:
        parser = _InlineHTML()
        parser.feed(content.decode("utf-8", errors="replace"))
        root, namespaces = parser.root, parser.namespaces
    reverse = {uri: prefix for prefix, uri in namespaces.items()}

    def canonical(prefix: str) -> str:
        uri = namespaces.get(prefix, "")
        for taxonomy in ("us-gaap", "ifrs-full", "dei", "srt"):
            if f"/{taxonomy}/" in uri or uri.endswith("/" + taxonomy):
                return taxonomy
        return prefix

    def qname(name: str) -> str:
        if name.startswith("{"):
            uri, local = name[1:].split("}", 1)
            return f"{canonical(reverse.get(uri, uri))}:{local}"
        if ":" in name:
            prefix, local = name.split(":", 1)
            return f"{canonical(prefix)}:{local}"
        return name

    contexts: dict[str, dict[str, str]] = {}
    units: dict[str, str] = {}
    by_id = {_attr(item, "id"): item for item in root.iter() if _attr(item, "id")}
    for item in root.iter():
        if _local(item.tag) == "context":
            context = {"start": "", "end": "", "entity_identifier": ""}
            dimensions: dict[str, str] = {}
            for child in item.iter():
                local = _local(child.tag)
                if local in {"startdate", "enddate", "instant", "identifier"}:
                    key = {
                        "startdate": "start",
                        "enddate": "end",
                        "instant": "end",
                        "identifier": "entity_identifier",
                    }[local]
                    context[key] = _text(child)
                elif local in {"explicitmember", "typedmember"}:
                    dimensions[_attr(child, "dimension")] = (
                        _text(child)
                        if local == "explicitmember"
                        else ET.tostring(child, encoding="unicode")
                    )
            context["dimensions"] = json.dumps(dimensions, sort_keys=True)
            contexts[_attr(item, "id")] = context
        elif _local(item.tag) == "unit":
            measures = [
                _text(child).rsplit(":", 1)[-1]
                for child in item.iter()
                if _local(child.tag) == "measure"
            ]
            units[_attr(item, "id")] = "/".join(measures)
    rows = []
    digest = hashlib.sha256(content).hexdigest()
    for item in root.iter():
        context_id = _attr(item, "contextref")
        if not context_id or context_id not in contexts:
            continue
        local = _local(item.tag)
        inline = local in {"nonfraction", "nonnumeric", "fraction"}
        concept = qname(_attr(item, "name")) if inline else qname(item.tag)
        if not concept or ":" not in concept:
            continue
        raw = _text(item)
        block_markup = _has_block_markup(item)
        continuation, visited = _attr(item, "continuedat"), set()
        while continuation and continuation in by_id and continuation not in visited:
            visited.add(continuation)
            target = by_id[continuation]
            raw += " " + _text(target)
            block_markup |= _has_block_markup(target)
            continuation = _attr(target, "continuedat")
        unit_ref = _attr(item, "unitref")
        numeric = local in {"nonfraction", "fraction"} or bool(unit_ref)
        value: str | float | None = _number(raw, item) if numeric else raw
        if _attr(item, "nil").lower() == "true":
            value = None
        if local == "fraction":
            parts = {_local(child.tag): _number(_text(child), child) for child in item}
            numerator, denominator = parts.get("numerator"), parts.get("denominator")
            value = numerator / denominator if numerator is not None and denominator else None
        namespace, tag = concept.rsplit(":", 1)
        value_type = (
            "narrative"
            if is_narrative_fact(
                concept, raw, declared_type=_attr(item, "type"), has_block_markup=block_markup
            )
            else "numeric"
            if numeric
            else "categorical"
        )
        rows.append(
            {
                "cik": int(cik),
                "concept": concept,
                "namespace": namespace,
                "tag": tag,
                "unit": units.get(unit_ref, unit_ref),
                "value": value,
                "value_type": value_type,
                "raw_value": raw,
                **contexts[context_id],
                "filed": filed,
                "accepted": accepted,
                "accession": accession,
                "form": form,
                "context_id": context_id,
                "decimals": _attr(item, "decimals"),
                "scale": _attr(item, "scale", "0"),
                "source_url": source_url,
                "source_kind": "original_filing",
                "source_sha256": digest,
                "status": "observed" if value is not None else "native_missing",
            }
        )
    return rows


def companyfact_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Preserve all namespaces/units and original vintage dates from CompanyFacts."""
    rows = []
    cik = int(payload.get("cik", 0))
    for namespace, concepts in payload.get("facts", {}).items():
        for tag, concept in concepts.items():
            for unit, observations in concept.get("units", {}).items():
                observed_types = {
                    "numeric"
                    if isinstance(row["val"], (int, float)) and not isinstance(row["val"], bool)
                    else "categorical"
                    for row in observations
                    if row.get("val") is not None
                }
                if len(observed_types) > 1:
                    message = f"CompanyFacts {namespace}:{tag}/{unit} mixes observed scalar types."
                    raise ValueError(message)
                value_type = next(iter(observed_types), "numeric" if unit else "categorical")
                for observation in observations:
                    value = observation.get("val")
                    rows.append(
                        {
                            "cik": cik,
                            "concept": f"{namespace}:{tag}",
                            "namespace": namespace,
                            "tag": tag,
                            "unit": unit,
                            "value": value,
                            "value_type": "narrative"
                            if is_narrative_fact(f"{namespace}:{tag}", value)
                            else value_type,
                            "raw_value": str(value),
                            "start": observation.get("start", ""),
                            "end": observation.get("end", ""),
                            "filed": observation.get("filed", ""),
                            "accepted": "",
                            "accession": observation.get("accn", ""),
                            "form": observation.get("form", ""),
                            "dimensions": "{}",
                            "context_id": "",
                            "entity_identifier": str(cik),
                            "decimals": "",
                            "scale": "0",
                            "source_url": f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json",
                            "source_kind": "companyfacts",
                            "source_sha256": "",
                            "status": "observed" if value is not None else "native_missing",
                        }
                    )
    return rows


def submission_rows(payload: dict[str, Any], cik: int) -> list[dict[str, Any]]:
    """Handle the current submissions array and additional historical JSON arrays."""
    history = payload.get("filings", {}).get("recent", payload)
    accessions = history.get("accessionNumber", [])
    rows = []
    for index, accession in enumerate(accessions):
        row = {
            name: values[index]
            for name, values in history.items()
            if isinstance(values, list) and len(values) > index
        }
        rows.append({"cik": cik, **row, "accession": accession})
    return rows


def _read_json(filename: Path) -> dict[str, Any]:
    if filename.suffix == ".gz":
        with gzip.open(filename, "rt") as handle:
            return json.load(handle)
    return json.loads(filename.read_text())


def load_source_facts(source_dir: Path, ciks: set[int] | None = None) -> pd.DataFrame:
    """Read only the new source cache, with a stable schema even before acquisition."""
    root = source_root(source_dir)
    records = []
    for filename in _json_files(root / "companyfacts", "[0-9]*.json"):
        if ciks is not None and int(filename.name.split(".")[0]) not in ciks:
            continue
        try:
            payload = _read_json(filename)
            facts = companyfact_rows(payload)
            digest = hashlib.sha256(_response_bytes(filename)).hexdigest()
            records.extend({**row, "source_sha256": digest} for row in facts)
        except (ValueError, OSError, TypeError):
            continue
    for filename in _json_files(root / "filings", "*/*/facts.json"):
        if ciks is not None and int(filename.parents[1].name) not in ciks:
            continue
        records.extend(json.loads(_response_bytes(filename)))
    filing_metadata = root / "metadata/filings.json"
    if filing_metadata.exists():
        accepted = {
            (int(row["cik"]), row["accession"]): row.get("acceptanceDateTime", "")
            for row in json.loads(filing_metadata.read_text())
        }
        for row in records:
            if not row.get("accepted"):
                row["accepted"] = accepted.get((int(row["cik"]), str(row["accession"])), "")
    return pd.DataFrame(records, columns=FACT_COLUMNS)


def build_crosswalk(
    monthly: pd.DataFrame,
    candidates: dict[str, Any],
    facts: pd.DataFrame,
    evidence: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Export candidate links; verify only dated SEC observations or explicit intervals.

    A current ticker match is never promoted into a historical issuer identity.
    Automatically recovered DEI observations certify their reported instant only;
    broader effective intervals require separately documented SEC evidence.
    """
    records: list[dict[str, Any]] = []
    dates = pd.to_datetime(monthly["date"] if "date" in monthly else monthly["month"])
    for (permno, permco, observed_ticker), group in monthly.assign(_date=dates).groupby(
        ["permno", "permco", "ticker"], dropna=False
    ):
        ticker = "" if str(observed_ticker) in {"nan", "<NA>", "None"} else str(observed_ticker)
        matches = [
            int(row["cik_str"])
            for row in candidates.values()
            if isinstance(row, dict) and str(row.get("ticker", "")).upper() == str(ticker).upper()
        ]
        base = {
            "permno": permno,
            "permco": permco,
            "ticker": ticker,
            "effective_from": str(group["_date"].min().date()),
            "effective_to": str(group["_date"].max().date()),
            "evidence_url": "",
            "accession": "",
            "evidence_type": "current_ticker_candidate",
        }
        records.append(
            {
                **base,
                "cik": matches[0] if len(set(matches)) == 1 else None,
                "status": "candidate_only" if len(set(matches)) == 1 else "unresolved",
                "reason": "Current ticker mapping is not historical identity evidence.",
            }
        )
        if not facts.empty:
            matching = facts.loc[
                facts["concept"].eq("dei:TradingSymbol")
                & facts["value"].astype(str).str.upper().eq(str(ticker).upper())
            ]
            for fact in matching.to_dict("records"):
                instant = pd.to_datetime(fact["end"], errors="coerce")
                if pd.isna(instant) or not (
                    group["_date"].min().to_period("M").start_time
                    <= instant
                    <= group["_date"].max().to_period("M").end_time
                ):
                    continue
                records.append(
                    {
                        **base,
                        "cik": fact["cik"],
                        "effective_from": str(instant.date()),
                        "effective_to": str(instant.date()),
                        "status": "verified_observation",
                        "evidence_url": fact["source_url"],
                        "accession": fact["accession"],
                        "evidence_type": "dei:TradingSymbol",
                        "reason": "Reported SEC instant only; no extrapolation.",
                    }
                )
    if evidence is not None:
        for record in evidence.to_dict("records"):
            if (
                record.get("status") == "verified"
                and urlparse(str(record.get("evidence_url", ""))).hostname
                in {"www.sec.gov", "data.sec.gov"}
                and record.get("accession")
                and record.get("effective_from")
                and record.get("effective_to")
            ):
                records.append(  # noqa: PERF401 -- validation precedes promotion.
                    {
                        **{str(key): value for key, value in record.items()},
                        "status": "verified_interval",
                    }
                )
    return pd.DataFrame(records, columns=CROSSWALK_COLUMNS).drop_duplicates().reset_index(drop=True)


def _checkpoint(  # noqa: PLR0913 -- checkpoint identity, two ledgers and progress counters.
    root: Path,
    cik: int,
    filings: list[dict[str, Any]],
    requests: list[dict[str, Any]],
    *,
    completed: int,
    total: int,
    phase: str = "filings",
) -> None:
    checkpoint = {
        "cik": cik,
        "phase": phase,
        "filings": filings,
        "requests": requests,
        "checkpoint_at": datetime.now(UTC).isoformat(),
    }
    _json(root / "metadata/progress" / f"CIK{cik:010}.json", checkpoint)
    _json(root / "metadata/progress" / phase / f"CIK{cik:010}.json", checkpoint)
    _json(
        root / "metadata/progress.json",
        {
            "phase": phase,
            "completed_candidate_ciks": completed,
            "total_candidate_ciks": total,
            "last_cik": cik,
        },
    )
    LOGGER.info(
        "SEC checkpoint %s/%s: CIK%010d, %s filings, %s requests",
        completed,
        total,
        cik,
        len(filings),
        len(requests),
    )


def _reuse_existing(root: Path, existing_cache: Path | None) -> None:
    if existing_cache is None:
        return
    if (
        root.resolve() == existing_cache.resolve()
        or existing_cache.resolve() in root.resolve().parents
    ):
        message = "The new SEC archive must be separate from the frozen source cache."
        raise ValueError(message)
    for old in sorted((existing_cache / "facts").glob("*.json.gz")):
        target = root / "companyfacts" / old.name
        if not target.exists():
            atomic_copy(target, old)
    old_tickers = existing_cache / "sec-tickers.json"
    if old_tickers.exists() and not (root / "metadata/sec-tickers.json").exists():
        atomic_copy(root / "metadata/sec-tickers.json", old_tickers)
    old_universe = existing_cache.parent / "universe.csv"
    if old_universe.exists() and not (root / "metadata/sec-tickers.json").exists():
        old_issuers = pd.read_csv(old_universe)
        _json(
            root / "metadata/sec-tickers.json",
            {
                str(index): {"ticker": row["ticker"], "cik_str": int(row["cik"])}
                for index, row in enumerate(old_issuers.to_dict("records"))
            },
        )


def _candidate_ciks(
    monthly: pd.DataFrame, candidates: dict[str, Any], root: Path, evidence: pd.DataFrame | None
) -> set[int]:
    tickers = set(monthly["ticker"].dropna().str.upper())
    values = [
        row.get("cik_str")
        for row in candidates.values()
        if isinstance(row, dict) and str(row.get("ticker", "")).upper() in tickers
    ]
    if evidence is not None and "cik" in evidence:
        values.extend(evidence["cik"].dropna().tolist())
    historical = root / "metadata/historical-linkage/candidates.csv"
    if historical.exists():
        history = pd.read_csv(historical)
        if "cik" in history:
            values.extend(history["cik"].dropna().tolist())
    numeric = pd.to_numeric(pd.Series(values, dtype="object"), errors="coerce").dropna()
    return {
        int(value)
        for value in numeric
        if math.isfinite(value) and value > 0 and value == int(value)
    }


def _safe_name(name: str) -> bool:
    return bool(name) and name not in {".", ".."} and Path(name).name == name and "\\" not in name


def _metadata_json(
    client: SECClient, root: Path, kind: str, cik: int, url: str
) -> dict[str, Any] | None:
    name = f"{cik:010}.json" if kind == "companyfacts" else f"CIK{cik:010}.json"
    destination = root / kind / name
    if _cache_path(destination).exists():
        return client.json(url, destination)
    if kind not in client.bulk_absences:
        receipt = root / "bulk" / f"{kind}-installed.json"
        client.bulk_absences[kind] = json.loads(receipt.read_text()) if receipt.exists() else {}
    bulk = client.bulk_absences[kind]
    if bulk.get("status") == "installed" and cik in bulk.get("absent_ciks", []):
        client.records.append(
            {
                "url": url,
                "status": "not_in_bulk_snapshot",
                "cik": cik,
                "bulk_url": bulk["url"],
                "archive_sha256": bulk["archive_sha256"],
                "snapshot_retrieved_at": bulk["retrieved_at"],
            }
        )
        return None
    return client.json(url, destination)


def _metadata_cik(
    client: SECClient, root: Path, cik: int
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json"
    compressed = root / "companyfacts" / f"{cik:010}.json.gz"
    facts = None
    if compressed.exists():
        try:
            facts = _read_json(compressed)
        except (OSError, ValueError):
            facts = None
        if facts is not None and facts.get("source_status") != 404:
            client.records.append({"url": facts_url, "status": "cached", "file": str(compressed)})
        else:
            facts = None
    if facts is None:
        facts = _metadata_json(client, root, "companyfacts", cik, facts_url)
    facts_resolved = facts is not None or bool(
        client.records
        and client.records[-1].get("status") in {"http_not_found", "not_in_bulk_snapshot"}
    )
    submissions = _metadata_json(
        client,
        root,
        "submissions",
        cik,
        f"https://data.sec.gov/submissions/CIK{cik:010}.json",
    )
    submissions_resolved = submissions is not None or bool(
        client.records
        and client.records[-1].get("status") in {"http_not_found", "not_in_bulk_snapshot"}
    )
    filings = submission_rows(submissions, cik) if submissions is not None else []
    additions = submissions.get("filings", {}).get("files", []) if submissions is not None else []
    historical_count = 0
    for addition in additions:
        name = str(addition.get("name", ""))
        if not _safe_name(name):
            client.records.append({"status": "invalid_metadata_name", "cik": cik, "name": name})
            continue
        extra = client.json(
            f"https://data.sec.gov/submissions/{quote(name)}", root / "submissions" / name
        )
        if extra is not None:
            historical_count += 1
            filings.extend(submission_rows(extra, cik))
    unique = {str(filing["accession"]): filing for filing in reversed(filings)}
    receipt = {
        "cik": cik,
        "companyfacts_available": facts is not None,
        "companyfacts_resolved": facts_resolved,
        "submissions_available": submissions is not None,
        "submissions_resolved": submissions_resolved,
        "historical_files_expected": len(additions),
        "historical_files_available": historical_count,
        "filing_metadata_rows": len(unique),
        "complete": facts_resolved and submissions_resolved and historical_count == len(additions),
    }
    _json(root / "metadata/company-index" / f"CIK{cik:010}.json", receipt)
    return list(unique.values()), receipt


def _flag(value: object) -> bool | None:
    if str(value).lower() in {"1", "true", "1.0"}:
        return True
    if str(value).lower() in {"0", "false", "0.0"}:
        return False
    return None


def _filing_plan(
    filings: list[dict[str, Any]],
    first: pd.Timestamp,
    last: pd.Timestamp,
    feature_start: pd.Timestamp,
) -> list[dict[str, Any]]:
    result = []
    for filing in filings:
        if filing.get("form") not in FORMS:
            continue  # All other forms remain in the unmodified submissions JSON.
        filed = pd.to_datetime(str(filing.get("filingDate", "")), errors="coerce")
        if pd.isna(filed):
            status = "invalid_filing_date"
        elif filed < first or filed > last:
            status = "outside_return_archive"
        elif filed < feature_start:
            status = "before_xbrl_feature_era"
        elif _flag(filing.get("isXBRL")) is False and _flag(filing.get("isInlineXBRL")) is not True:
            status = "reported_non_xbrl"
        else:
            status = "original_pending"
        result.append({**filing, "status": status})
    return sorted(result, key=lambda row: (int(row["cik"]), str(row["accession"])))


def filing_documents(index: dict[str, Any], primary: str) -> list[str]:
    """Select primary HTML and possible instance XML, excluding taxonomy/report files."""
    names = {str(entry.get("name", "")) for entry in index.get("directory", {}).get("item", [])}
    selected = []
    for name in sorted(names):
        lower = name.lower()
        primary_html = name == primary and lower.endswith((".htm", ".html", ".xhtml"))
        instance_xml = lower.endswith(".xml") and not (
            lower in {"filingsummary.xml", "financial_report.xml", "metalinks.xml"}
            or lower.endswith(
                (
                    "_cal.xml",
                    "_def.xml",
                    "_lab.xml",
                    "_pre.xml",
                    "-cal.xml",
                    "-def.xml",
                    "-lab.xml",
                    "-pre.xml",
                    "_calculation.xml",
                    "_definition.xml",
                    "_labels.xml",
                    "_presentation.xml",
                )
            )
            or re.fullmatch(r"r\d+\.xml", lower)
        )
        if _safe_name(name) and (primary_html or instance_xml):
            selected.append(name)
    return sorted(selected, key=lambda name: (name != primary, name))


PARSER_IMPLEMENTATION_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _original_filing(client: SECClient, root: Path, filing: dict[str, Any]) -> dict[str, Any]:
    cik, accession = int(filing["cik"]), str(filing["accession"])
    archive = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}"
    folder = root / "filings" / f"{cik:010}" / accession
    parsed_file, parse_status = folder / "facts.json", folder / "parse-status.json"
    if _cache_path(parsed_file).exists() and parse_status.exists():
        previous = json.loads(parse_status.read_text())
        if (
            previous.get("complete")
            and previous.get("native_facts", 0) > 0
            and previous.get("parser_version") == PARSER_VERSION
        ):
            return {**filing, "status": "cached", "facts": previous.get("native_facts", 0)}
    index = client.json(archive + "/index.json", folder / "index.json")
    if index is None:
        return {**filing, "status": "index_not_acquired"}
    names = filing_documents(index, str(filing.get("primaryDocument", "")))
    if not names:
        _json(
            parse_status,
            {
                "complete": False,
                "native_facts": 0,
                "documents": [],
                "parser_version": PARSER_VERSION,
                "parser_implementation_sha256": PARSER_IMPLEMENTATION_SHA256,
            },
        )
        return {**filing, "status": "instance_documents_unavailable", "facts": 0}
    rows: list[dict[str, Any]] = []
    failures = 0
    for name in names:
        url = archive + "/" + quote(name)
        content = client.fetch(url, folder / name)
        if content is None:
            failures += 1
            continue
        try:
            rows.extend(
                parse_xbrl(
                    content,
                    cik=cik,
                    accession=accession,
                    filed=str(filing.get("filingDate", "")),
                    accepted=filing.get("acceptanceDateTime", ""),
                    source_url=url,
                    form=filing["form"],
                )
            )
        except ValueError as error:
            client.records.append({"url": url, "status": "parse_error", "error": str(error)})
            failures += 1
    if rows:
        _json(parsed_file.with_suffix(".json.gz"), rows)
    _json(
        parse_status,
        {
            "complete": failures == 0 and bool(rows),
            "native_facts": len(rows),
            "documents": names,
            "document_policy": "primary-html-and-instance-xml-v1",
            "parser_version": PARSER_VERSION,
            "parser_implementation_sha256": PARSER_IMPLEMENTATION_SHA256,
        },
    )
    status = "parsed_partial" if rows and failures else "parsed" if rows else "no_native_facts"
    return {**filing, "status": status, "facts": len(rows), "failed_documents": failures}


def _materialize_acquisition(  # noqa: PLR0913 -- source evidence and phase checkpoint identities.
    monthly: pd.DataFrame,
    root: Path,
    candidates: dict[str, Any],
    evidence: pd.DataFrame | None,
    *,
    client: SECClient,
    filings: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
    phase: str,
    metadata_only: bool,
) -> dict[str, Any]:
    native_count = 0
    symbol_facts: list[dict[str, Any]] = []
    for filename in _json_files(root / "companyfacts", "[0-9]*.json"):
        try:
            payload = _read_json(filename)
        except (OSError, ValueError):
            continue
        for concepts in payload.get("facts", {}).values():
            for concept in concepts.values():
                native_count += sum(len(values) for values in concept.get("units", {}).values())
    for filename in _json_files(root / "filings", "*/*/facts.json"):
        rows = json.loads(_response_bytes(filename))
        native_count += len(rows)
        symbol_facts.extend(row for row in rows if row["concept"] == "dei:TradingSymbol")
    crosswalk = build_crosswalk(
        monthly, candidates, pd.DataFrame(symbol_facts, columns=FACT_COLUMNS), evidence
    )
    atomic_csv(root / "crosswalk.csv", crosswalk)
    _json(root / "metadata/filings.json", filings)
    complete = bool(receipts) and all(receipt["complete"] for receipt in receipts)
    requests_resolved = all(
        row["status"] in {"cached", "acquired", "http_not_found", "not_in_bulk_snapshot"}
        for row in client.records
    )
    failed = {
        "index_not_acquired",
        "parsed_partial",
        "instance_documents_unavailable",
        "no_native_facts",
    }
    originals_failed = any(
        row["status"] in failed or row.get("failed_documents", 0) for row in filings
    )
    status = (
        "pending_parse"
        if any(row["status"] in {"no_native_facts", "parsed_partial"} for row in filings)
        else "pending_network"
    )
    if complete and requests_resolved and not originals_failed:
        status = "metadata_ready" if phase == "metadata" else "initialized"
    manifest = {
        "api_version": API_VERSION,
        "source_dir": str(root),
        "offline": client.offline,
        "identity_available": bool(client.identity),
        "candidate_ciks": len(receipts),
        "native_facts": native_count,
        "crosswalk_statuses": crosswalk["status"].value_counts().to_dict(),
        "requests": client.records,
        "filings": len(filings),
        "status": status,
        "phase": "originals" if phase == "filings" else phase,
        "metadata_only": metadata_only,
        "metadata_complete": complete,
        "company_index": receipts,
        "filing_statuses": pd.Series([row["status"] for row in filings], dtype="object")
        .value_counts()
        .to_dict(),
        "originals_pending": sum(row["status"] == "original_pending" for row in filings),
        "retrieved_at": datetime.now(UTC).isoformat(),
    }
    bulk_manifest = root / "bulk/acquisition.json"
    if bulk_manifest.exists():
        manifest["bulk"] = json.loads(bulk_manifest.read_text())
    _json(root / "acquisition.json", manifest)
    return manifest


def acquire_sources(  # noqa: PLR0913 -- raw roster, cache identity and acquisition-phase controls.
    monthly: pd.DataFrame,
    output: Path,
    identity: str | None,
    existing_cache: Path | None = None,
    *,
    offline: bool = False,
    metadata_only: bool = False,
    feature_start: str = "2009-01-01",
    prefer_bulk: bool = False,
) -> dict[str, Any]:
    """Cover all candidate metadata before downloading expensive original XBRL documents.

    Phase one materializes a global filings ledger, crosswalk and acquisition
    checkpoint. ``metadata_only`` stops there, enabling a quick coverage audit.
    Full runs resume phase two from cached responses; no raw response is deleted.
    """
    root = source_root(output)
    for directory in ("companyfacts", "submissions", "filings", "metadata"):
        (root / directory).mkdir(parents=True, exist_ok=True)
    _reuse_existing(root, existing_cache)
    dates = pd.to_datetime(monthly["date"] if "date" in monthly else monthly["month"])
    first, last = dates.min(), dates.max()
    with SECClient(identity, offline=offline) as client:
        candidates = (
            client.json(
                "https://www.sec.gov/files/company_tickers.json", root / "metadata/sec-tickers.json"
            )
            or {}
        )
        evidence_path = root / "metadata/linkage-evidence.csv"
        evidence = pd.read_csv(evidence_path) if evidence_path.exists() else None
        ciks = sorted(_candidate_ciks(monthly, candidates, root, evidence))
        _json(root / "metadata/candidate-ciks.json", ciks)
        if prefer_bulk:
            # Defer this optional path to avoid the bulk module's shared SEC helper cycle.
            from free_foundations.study.bulk import acquire_bulk  # noqa: PLC0415

            acquire_bulk(root, ciks, identity, offline=offline)
        filings: list[dict[str, Any]] = []
        receipts: list[dict[str, Any]] = []
        for number, cik in enumerate(ciks, 1):
            request_start = len(client.records)
            metadata, receipt = _metadata_cik(client, root, cik)
            planned = _filing_plan(metadata, first, last, pd.Timestamp(feature_start))
            filings.extend(planned)
            receipts.append(receipt)
            _checkpoint(
                root,
                cik,
                planned,
                client.records[request_start:],
                completed=number,
                total=len(ciks),
                phase="metadata",
            )
        _json(
            root / "metadata/metadata-phase.json",
            {
                "candidate_ciks": ciks,
                "company_index": receipts,
                "complete": bool(receipts) and all(receipt["complete"] for receipt in receipts),
            },
        )
        manifest = _materialize_acquisition(
            monthly,
            root,
            candidates,
            evidence,
            client=client,
            filings=filings,
            receipts=receipts,
            phase="metadata",
            metadata_only=metadata_only,
        )
        if metadata_only:
            return manifest
        for number, cik in enumerate(ciks, 1):
            request_start = len(client.records)
            positions = [index for index, filing in enumerate(filings) if int(filing["cik"]) == cik]
            for position in positions:
                if filings[position]["status"] == "original_pending":
                    filings[position] = _original_filing(client, root, filings[position])
            _checkpoint(
                root,
                cik,
                [filings[position] for position in positions],
                client.records[request_start:],
                completed=number,
                total=len(ciks),
                phase="filings",
            )
        return _materialize_acquisition(
            monthly,
            root,
            candidates,
            evidence,
            client=client,
            filings=filings,
            receipts=receipts,
            phase="filings",
            metadata_only=metadata_only,
        )
