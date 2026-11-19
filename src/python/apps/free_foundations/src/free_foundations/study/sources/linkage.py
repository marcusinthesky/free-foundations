"""Historical SEC issuer identities from ownership filings, independent of predictors.

Forms 3/4/5 are XML metadata sources, not additional financial predictor inputs.
An interval requires two distinct dated SEC attestations of the same issuer,
inside one continuous CRSP security/ticker segment and without a conflicting CIK.
Nothing is extrapolated outside those corroborating dates.
"""

from __future__ import annotations

import hashlib
import json
import logging
import zipfile
from itertools import pairwise
from pathlib import Path
from typing import Any

import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes, atomic_csv, atomic_parquet
from free_foundations.study.sources.sec import SECClient, source_root

API_VERSION = "sec-ownership-linkage-v1"
LOGGER = logging.getLogger(__name__)
BASE_URL = "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets"
OBS_COLUMNS = [
    "accession",
    "filed_date",
    "period_of_report",
    "original_submission_date",
    "form",
    "cik",
    "issuer_name",
    "ticker",
    "symbol_key",
    "source_url",
    "source_sha256",
    "archive_period",
    "observation_date",
    "scope",
]
LINK_COLUMNS = [
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
    "attestation_set_sha256",
]
FIELDS = {
    "ACCESSION_NUMBER": "accession",
    "FILING_DATE": "filed_date",
    "PERIOD_OF_REPORT": "period_of_report",
    "DATE_OF_ORIG_SUB": "original_submission_date",
    "DOCUMENT_TYPE": "form",
    "ISSUERCIK": "cik",
    "ISSUERNAME": "issuer_name",
    "ISSUERTRADINGSYMBOL": "ticker",
}


def _write_json(filename: Path, value: object) -> None:
    payload = (json.dumps(value, indent=2, allow_nan=False, default=str) + "\n").encode()
    atomic_bytes(filename, payload)


def symbol_key(symbol: object) -> str:
    """Normalize exchange punctuation without collapsing distinct share-class suffixes."""
    return str(symbol).strip().upper().replace(".", "-")


def acquire_identifier_sources(
    monthly: pd.DataFrame,
    source_dir: Path,
    identity: str | None,
    *,
    offline: bool = False,
    start_year: int = 2006,
) -> dict[str, Any]:
    """Archive public ownership ZIPs without changing the running financial acquisition."""
    root = source_root(source_dir)
    archive = root / "metadata/ownership"
    archive.mkdir(parents=True, exist_ok=True)
    dates = pd.to_datetime(monthly["date"] if "date" in monthly else monthly["month"])
    last = dates.max().to_period("Q")
    if start_year < 2006:
        message = "The official SEC ownership bulk archive begins in 2006."
        raise ValueError(message)
    with SECClient(identity, offline=offline) as client:
        for year in range(start_year, last.year + 1):
            for quarter in range(1, 5):
                if year == last.year and quarter > last.quarter:
                    break
                name = f"{year}q{quarter}_form345.zip"
                client.fetch(f"{BASE_URL}/{name}", archive / name)
                LOGGER.info("SEC identifier archive %s: %s", name, client.records[-1]["status"])
                _write_json(
                    root / "metadata/identifier-acquisition.json",
                    {
                        "api_version": API_VERSION,
                        "scope": "issuer_identity_only",
                        "offline": offline,
                        "requests": client.records,
                        "status": "pending_acquisition"
                        if any(
                            row["status"] not in {"cached", "acquired"} for row in client.records
                        )
                        else "acquired",
                    },
                )
    return {
        "api_version": API_VERSION,
        "source_dir": str(root),
        "requests": client.records,
        "status": "pending_acquisition"
        if any(row["status"] not in {"cached", "acquired"} for row in client.records)
        else "acquired",
    }


def read_identifier_archive(filename: Path, symbols: set[str]) -> pd.DataFrame:
    """Stream the authoritative issuer fields, never the reporting-owner CIK.

    All ZIP bytes remain archived. The materialized observation table contains
    every matching historical issuer attestation, including amendments/conflicts.
    """
    digest = hashlib.sha256(filename.read_bytes()).hexdigest()
    parts: list[pd.DataFrame] = []
    with zipfile.ZipFile(filename) as archive:
        names = [
            name
            for name in archive.namelist()
            if Path(name).name.lower() in {"submission.tsv", "submission.txt"}
        ]
        if len(names) != 1:
            message = "Ownership archive needs exactly one SUBMISSION table."
            raise ValueError(message)
        with archive.open(names[0]) as stream:
            for raw_chunk in pd.read_csv(
                stream, sep="\t", dtype="string", encoding="utf-8-sig", chunksize=50000
            ):
                required = set(FIELDS) - {"DATE_OF_ORIG_SUB"}
                if not required.issubset(raw_chunk.columns):
                    message = (
                        f"Ownership SUBMISSION lacks {sorted(required - set(raw_chunk.columns))}."
                    )
                    raise ValueError(message)
                chunk = raw_chunk.reindex(columns=list(FIELDS)).rename(columns=FIELDS)
                chunk["symbol_key"] = chunk["ticker"].map(symbol_key)
                chunk = chunk.loc[chunk["symbol_key"].isin(symbols)].copy()
                if chunk.empty:
                    continue
                for column in ("filed_date", "period_of_report", "original_submission_date"):
                    chunk[column] = pd.to_datetime(chunk[column], format="mixed", errors="coerce")
                chunk["cik"] = pd.to_numeric(chunk["cik"], errors="coerce").astype("Int64")
                chunk["observation_date"] = chunk["filed_date"]
                chunk["source_url"] = f"{BASE_URL}/{filename.name}"
                chunk["source_sha256"] = digest
                chunk["archive_period"] = filename.name.split("_", 1)[0]
                chunk["scope"] = "issuer_identity_only"
                parts.append(chunk)
    return (
        pd.concat(parts, ignore_index=True).reindex(columns=OBS_COLUMNS)
        if parts
        else pd.DataFrame(columns=OBS_COLUMNS)
    )


def security_segments(monthly: pd.DataFrame) -> list[dict[str, Any]]:
    """Split ticker changes, PERMCO changes and gaps in observed calendar months."""
    frame = monthly[["permno", "permco", "ticker"]].copy()
    frame["date"] = pd.to_datetime(monthly["date"] if "date" in monthly else monthly["month"])
    frame["symbol_key"] = frame["ticker"].map(symbol_key)
    frame = frame.sort_values(["permno", "date"])
    segments: list[dict[str, Any]] = []
    for permno, security in frame.groupby("permno", sort=True):
        month_number = security["date"].dt.year * 12 + security["date"].dt.month
        changed = (
            security["symbol_key"].ne(security["symbol_key"].shift())
            | security["permco"].ne(security["permco"].shift())
            | month_number.diff().ne(1)
        )
        for _, segment in security.groupby(changed.cumsum(), sort=True):
            first = segment.iloc[0]
            segments.append(
                {
                    "permno": int(str(permno)),
                    "permco": int(first["permco"]),
                    "ticker": str(first["ticker"]),
                    "symbol_key": str(first["symbol_key"]),
                    "segment_start": segment["date"].min(),
                    "segment_end": segment["date"].max(),
                }
            )
    return segments


def _attested_interval(
    segment: dict[str, Any], records: list[dict[str, Any]]
) -> dict[str, Any] | None:
    anchors = [row for row in records if str(row["form"]) in {"3", "4", "5"}]
    if (
        len({row["accession"] for row in anchors}) < 2
        or len({row["observation_date"] for row in anchors}) < 2
    ):
        return None
    anchors = sorted(anchors, key=lambda row: (row["observation_date"], row["accession"]))
    first, last = anchors[0], anchors[-1]
    dates = sorted({pd.Timestamp(row["observation_date"]) for row in anchors})
    evidence = [
        {
            key: row[key]
            for key in (
                "accession",
                "observation_date",
                "cik",
                "issuer_name",
                "ticker",
                "source_url",
                "source_sha256",
            )
        }
        for row in (first, last)
    ]
    return {
        **{
            key: segment[key]
            for key in ("permno", "permco", "ticker", "segment_start", "segment_end")
        },
        "cik": int(first["cik"]),
        "effective_from": first["observation_date"],
        "effective_to": last["observation_date"],
        "status": "verified_interval",
        "evidence_url": first["source_url"],
        "accession": first["accession"],
        "evidence_type": "bracketed_sec_ownership_in_continuous_crsp_segment",
        "reason": (
            "Same issuer attested on distinct filing dates; no conflicting issuer "
            "inside this interval; no extrapolation."
        ),
        "corroborating_accessions": json.dumps([str(first["accession"]), str(last["accession"])]),
        "evidence_json": json.dumps(evidence, default=str, sort_keys=True),
        "attestation_set_sha256": hashlib.sha256(
            json.dumps(
                [
                    (str(row["accession"]), str(row["observation_date"]), int(row["cik"]))
                    for row in anchors
                ],
                separators=(",", ":"),
            ).encode()
        ).hexdigest(),
        "attestations": len(anchors),
        "max_gap_days": max((later - earlier).days for earlier, later in pairwise(dates)),
    }


def infer_intervals(
    monthly: pd.DataFrame, observations: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Bracket same-CIK runs; conflicting dates and issuer changes are hard barriers."""
    links: list[dict[str, Any]] = []
    coverage: list[dict[str, Any]] = []
    valid = observations.loc[
        observations["cik"].notna()
        & pd.to_numeric(observations["cik"], errors="coerce").gt(0)
        & observations["observation_date"].notna()
        & observations["accession"].notna()
    ].copy()
    valid = valid.drop_duplicates(["accession", "cik", "symbol_key", "observation_date"])
    by_symbol = {
        str(symbol): group.sort_values(["observation_date", "accession"])
        for symbol, group in valid.groupby("symbol_key", sort=False)
    }
    for segment in security_segments(monthly):
        symbol_rows = by_symbol.get(segment["symbol_key"], valid.iloc[:0])
        matching = symbol_rows.loc[
            symbol_rows["observation_date"].ge(segment["segment_start"])
            & symbol_rows["observation_date"].le(segment["segment_end"])
        ]
        start = len(links)
        conflict = matching.groupby("observation_date")["cik"].transform("nunique").gt(1)
        boundaries = (
            matching["cik"].ne(matching["cik"].shift())
            | conflict
            | conflict.shift(fill_value=False)
        )
        runs = boundaries.cumsum()
        conflict_dates = int(matching.loc[conflict, "observation_date"].nunique())
        for _, group in matching.loc[~conflict].groupby(runs, sort=False):
            records = [
                {str(key): value for key, value in row.items()} for row in group.to_dict("records")
            ]
            interval = _attested_interval(segment, records)
            if interval is not None:
                links.append(interval)
        intervals = len(links) - start
        unique_ciks = matching["cik"].nunique()
        reason = (
            ""
            if intervals
            else "no_historical_sec_attestation"
            if matching.empty
            else "conflicting_historical_sec_attestations"
            if conflict_dates or unique_ciks > 1
            else "insufficient_distinct_sec_attestations"
        )
        coverage.append(
            {
                **segment,
                "sec_attestations": len(matching),
                "candidate_ciks": int(unique_ciks),
                "conflicting_dates": conflict_dates,
                "verified_intervals": intervals,
                "status": "linked" if intervals else "unresolved",
                "reason": reason,
            }
        )
        if not intervals:
            links.append(
                {
                    **segment,
                    "cik": int(matching.iloc[0]["cik"]) if unique_ciks == 1 else None,
                    "effective_from": segment["segment_start"],
                    "effective_to": segment["segment_end"],
                    "status": "unresolved",
                    "reason": reason,
                    "attestations": len(matching),
                }
            )
    return pd.DataFrame(links, columns=LINK_COLUMNS), pd.DataFrame(coverage)


def materialize_linkage(monthly: pd.DataFrame, source_dir: Path) -> dict[str, pd.DataFrame]:
    """Save historical evidence separately; the orchestrator promotes reviewed intervals."""
    root = source_root(source_dir)
    destination = root / "metadata/historical-linkage"
    destination.mkdir(parents=True, exist_ok=True)
    archives = sorted((root / "metadata/ownership").glob("*_form345.zip"))
    input_keys = monthly[["permno", "permco", "ticker", "date"]].sort_values(["permno", "date"])
    identity = {
        "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "security_history_sha256": hashlib.sha256(
            pd.util.hash_pandas_object(input_keys, index=False).to_numpy().tobytes()
        ).hexdigest(),
        "archive_sha256": {
            filename.name: hashlib.sha256(filename.read_bytes()).hexdigest()
            for filename in archives
        },
    }
    manifest = destination / "manifest.json"
    names = ("observations", "crosswalk", "evidence", "coverage", "candidates")
    if manifest.exists():
        previous = json.loads(manifest.read_text())
        if previous.get("identity") == identity and all(
            (destination / f"{name}.parquet").is_file() for name in names
        ):
            LOGGER.info("Reusing unchanged historical SEC linkage evidence")
            return {name: pd.read_parquet(destination / f"{name}.parquet") for name in names}
    symbols = {symbol_key(value) for value in monthly["ticker"].dropna()}
    parts: list[pd.DataFrame] = []
    issues: list[dict[str, str]] = []
    for filename in archives:
        try:
            part = read_identifier_archive(filename, symbols)
            parts.append(part)
            LOGGER.info(
                "Parsed SEC identifier archive %s: %s observations", filename.name, len(part)
            )
        except (OSError, ValueError, zipfile.BadZipFile, pd.errors.ParserError) as error:
            issues.append(
                {
                    "archive": str(filename),
                    "status": "identifier_archive_parse_error",
                    "error": str(error),
                }
            )
    observations = (
        pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=OBS_COLUMNS)
    )
    crosswalk, coverage = infer_intervals(monthly, observations)
    evidence = crosswalk.loc[crosswalk["status"].eq("verified_interval")].copy()
    evidence["status"] = "verified"
    candidates = (
        observations[["cik", "ticker", "issuer_name"]]
        .dropna(subset=["cik"])
        .drop_duplicates()
        .reset_index(drop=True)
    )
    frames = {
        "observations": observations,
        "crosswalk": crosswalk,
        "evidence": evidence,
        "coverage": coverage,
        "candidates": candidates,
    }
    for name, frame in frames.items():
        atomic_parquet(destination / f"{name}.parquet", frame)
    atomic_csv(destination / "evidence.csv", evidence)
    atomic_csv(destination / "candidates.csv", candidates)
    _write_json(
        destination / "manifest.json",
        {
            "api_version": API_VERSION,
            "identity": identity,
            "scope": "issuer_identity_only",
            "archives": len(parts),
            "observations": len(observations),
            "verified_intervals": len(evidence),
            "candidate_ciks": int(candidates["cik"].nunique()),
            "issues": issues,
            "interval_policy": (
                "two distinct non-amendment accession numbers and filing dates; "
                "continuous CRSP ticker/PERMCO/security segment; split at any "
                "conflicting CIK; no extrapolation"
            ),
            "status": "partial" if issues else "materialized",
        },
    )
    return frames
