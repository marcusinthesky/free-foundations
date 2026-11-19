"""Quarter-start SEC information sets and faithfully identified characteristic components."""

from __future__ import annotations

import gzip
import json
import logging
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse

import numpy as np
import pandas as pd
from pandas.api.types import is_object_dtype, is_string_dtype

from free_foundations.fernandez.characteristics import characteristics
from free_foundations.study.sec import (
    CROSSWALK_COLUMNS,
    FACT_COLUMNS,
    load_source_facts,
    scalar_fact_types,
    source_root,
)
from free_foundations.study.source_io import atomic_parquet

if TYPE_CHECKING:
    from pathlib import Path

    from pandas._libs.tslibs.nattype import NaTType

    from free_foundations.study.spec import StudySpec

LOGGER = logging.getLogger(__name__)
STANDARD_TAXONOMIES = {"us-gaap", "ifrs-full", "dei", "srt"}
CHAR_COLUMNS = [
    "issuer_id",
    "permco",
    "quarter",
    "characteristic",
    "value",
    "status",
    "reason",
    "cutoff",
    "fact_available_at",
    "components",
]
BROAD_COLUMNS = [
    "issuer_id",
    "permco",
    "quarter",
    "feature_id",
    "value",
    "value_type",
    "taxonomy",
    "is_standard",
    "entity_wide",
    "dimensions",
    "concept",
    "unit",
    "period_kind",
    "fact_available_at",
    "accession",
    "start",
    "end",
    "source_url",
    "status",
    "cutoff",
]
AVAILABILITY_COLUMNS = [
    "issuer_id",
    "permco",
    "quarter",
    "cutoff",
    "cik",
    "xbrl_available",
    "status",
    "reason",
    "native_scalar_count",
    "original_characteristics_available",
    "sic",
]


def feature_value_types(frame: pd.DataFrame) -> dict[str, str]:
    """Validate explicit native scalar types without inferring from numeric-looking values."""
    if frame.empty or "value_type" not in frame:
        return {}
    declared = frame[["feature_id", "value_type"]].drop_duplicates()
    if (~declared["value_type"].isin(["numeric", "categorical"])).any() or declared[
        "feature_id"
    ].duplicated().any():
        message = (
            "One XBRL feature must have exactly one declared numeric or categorical value_type."
        )
        raise ValueError(message)
    return dict(
        zip(declared["feature_id"].astype(str), declared["value_type"].astype(str), strict=True)
    )


def _timestamp(value: object) -> pd.Timestamp | NaTType:
    if value is None or str(value).strip() in {"", "NaT", "nan", "<NA>"}:
        return pd.NaT
    try:
        stamp = pd.Timestamp(str(value))
    except (ValueError, TypeError):
        return pd.NaT
    return (
        stamp.tz_localize("America/New_York").tz_convert("UTC")
        if stamp.tzinfo is None
        else stamp.tz_convert("UTC")
    )


def _available(row: pd.Series) -> pd.Timestamp | NaTType:
    accepted = _timestamp(row.get("accepted"))
    if not pd.isna(accepted):
        return accepted
    filed = row.get("filed", "")
    if pd.isna(filed) or not str(filed).strip():
        return pd.NaT
    # Filing dates have no intraday timestamp. Never use a last-day filing for
    # a return whose opening close may precede its dissemination.
    stamp = pd.to_datetime(filed, errors="coerce")
    return _timestamp(stamp + pd.Timedelta(days=1)) if not pd.isna(stamp) else pd.NaT


def _period_kind(row: pd.Series) -> str:
    if pd.isna(row["start"]):
        return "instant"
    days = _elapsed_days(pd.Series([row["end"]]), pd.Series([row["start"]])).iloc[0]
    if 300 <= days <= 380:
        return "annual"
    if 60 <= days <= 120:
        return "quarter"
    if 150 <= days <= 210:
        return "ytd_2q"
    if 240 <= days <= 300:
        return "ytd_3q"
    return f"duration_{days}d"


def _elapsed_days(later: pd.Series, earlier: pd.Series) -> pd.Series:
    """Compute whole elapsed days without overflowing nanosecond timedelta bounds.

    Each source endpoint may be a valid timestamp even when their separation
    exceeds the roughly 292-year timedelta range. Subtract bounded day ordinals
    first, then borrow a day when the within-day remainder requires it. This also
    preserves the usual floor convention for intraday and reversed intervals.
    """
    if not later.index.equals(earlier.index):
        message = "Elapsed-day endpoints must refer to the same ordered source rows."
        raise ValueError(message)
    day_ns = 86_400_000_000_000
    end = later.to_numpy(dtype="datetime64[ns]")
    start = earlier.to_numpy(dtype="datetime64[ns]")
    end_day, end_remainder = np.divmod(end.view("int64"), day_ns)
    start_day, start_remainder = np.divmod(start.view("int64"), day_ns)
    days = end_day - start_day - (end_remainder < start_remainder)
    return pd.Series(days, index=later.index).mask(np.isnat(end) | np.isnat(start))


def _timestamp_values(values: pd.Series, *, filing_date: bool = False) -> pd.Series:
    """Parse repeated SEC filing clocks once per distinct source value, never per fact."""
    codes, unique = pd.factorize(values, sort=False)
    stamps = []
    for value in unique:
        if filing_date:
            parsed = pd.to_datetime(value, errors="coerce")
            stamp = _timestamp(parsed + pd.Timedelta(days=1)) if not pd.isna(parsed) else pd.NaT
        else:
            stamp = _timestamp(value)
        stamps.append(stamp)
    result = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns, UTC]")
    observed = codes >= 0
    if observed.any():
        parsed_stamps = pd.to_datetime(pd.Series(stamps, dtype="object"), utc=True)
        result.iloc[np.flatnonzero(observed)] = parsed_stamps.array.take(codes[observed])
    return result


def _period_kinds(frame: pd.DataFrame) -> np.ndarray:
    """Classify duration vectors with the same inclusive boundaries and priority."""
    days = _elapsed_days(frame["end"], frame["start"])
    duration = "duration_" + days.astype("Int64").astype("string").fillna("nan") + "d"
    return np.select(
        [
            frame["start"].isna(),
            days.between(300, 380),
            days.between(60, 120),
            days.between(150, 210),
            days.between(240, 300),
        ],
        ["instant", "annual", "quarter", "ytd_2q", "ytd_3q"],
        default=duration.to_numpy(dtype=object),
    )


def _normalized_facts(frame: pd.DataFrame) -> pd.DataFrame:
    optional_types = [name for name in ("xbrl_type", "type") if name in frame]
    frame = frame.reindex(columns=[*FACT_COLUMNS, *optional_types]).copy()
    if frame.empty:
        frame["fact_available_at"] = pd.Series(dtype="datetime64[ns, UTC]")
        frame["period_kind"] = pd.Series(dtype="str")
        return frame
    frame["value_type"] = scalar_fact_types(frame)
    declared_start = frame["start"].notna() & frame["start"].astype(str).str.strip().ne("")
    for name in ("start", "end"):
        frame[f"raw_{name}"] = frame[name]
        frame[name] = pd.to_datetime(frame[name], errors="coerce")
    invalid_period = (
        (declared_start & frame["start"].isna())
        | frame["end"].isna()
        | frame["start"].gt(frame["end"])
    )
    frame.loc[invalid_period, "status"] = "invalid_period"
    accepted = _timestamp_values(frame["accepted"])
    missing = accepted.isna()
    accepted.loc[missing] = _timestamp_values(frame.loc[missing, "filed"], filing_date=True)
    frame["fact_available_at"] = accepted
    frame["period_kind"] = _period_kinds(frame)
    frame["dimensions"] = frame["dimensions"].fillna("{}")
    frame["entity_wide"] = frame["dimensions"].eq("{}")
    frame["is_standard"] = frame["namespace"].isin(STANDARD_TAXONOMIES) & frame["entity_wide"]
    return frame


def _cutoff(quarter: pd.Timestamp, monthly: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    period = pd.Timestamp(quarter).to_period("Q")
    day = period.start_time - pd.Timedelta(days=1)
    dates = pd.to_datetime(monthly["date"] if "date" in monthly else monthly["month"])
    previous = dates.loc[dates.dt.to_period("M").astype(str).eq(str(day.to_period("M")))]
    # CRSP's actual final trading date, where present, prevents weekend end dates
    # from admitting an after-close filing before the opening return boundary.
    trading_day = previous.max() if not previous.empty else pd.offsets.BDay().rollback(day)
    close = pd.Timestamp(trading_day).normalize().tz_localize("America/New_York") + pd.Timedelta(
        hours=16
    )
    return day.normalize(), close.tz_convert("UTC")


def _linked_cik(crosswalk: pd.DataFrame, permco: int, day: pd.Timestamp) -> tuple[int | None, str]:
    if crosswalk.empty:
        return None, "linkage_unresolved"
    linked = crosswalk.loc[
        pd.to_numeric(crosswalk["permco"], errors="coerce").eq(permco)
        & crosswalk["status"].isin({"verified_interval", "verified_observation"})
        & pd.to_datetime(crosswalk["effective_from"], errors="coerce").le(day)
        & pd.to_datetime(crosswalk["effective_to"], errors="coerce").ge(day)
        & crosswalk["evidence_url"].map(_official_url)
        & crosswalk["accession"].notna()
    ]
    ciks = pd.to_numeric(linked["cik"], errors="coerce").dropna().astype(int).unique()
    if len(ciks) != 1:
        return None, "linkage_conflict" if len(ciks) > 1 else "linkage_unresolved"
    return int(ciks[0]), "verified"


def _population_links(
    population: pd.DataFrame,
    crosswalk: pd.DataFrame,
    cutoffs: dict[pd.Timestamp, tuple[pd.Timestamp, pd.Timestamp]],
) -> dict[tuple[str, pd.Timestamp], tuple[int | None, str]]:
    """Resolve all interval joins once, retaining unresolved and conflicting task rows."""
    rows = population[["issuer_id", "permco", "quarter"]].copy().reset_index(drop=True)
    rows["_position"] = np.arange(len(rows))
    rows["_day"] = rows["quarter"].map({quarter: day for quarter, (day, _) in cutoffs.items()})
    candidates = crosswalk.loc[
        crosswalk["status"].isin({"verified_interval", "verified_observation"})
        & crosswalk["evidence_url"].map(_official_url)
        & crosswalk["accession"].notna()
    ].copy()
    for name in ("permco", "cik"):
        candidates[name] = pd.to_numeric(candidates[name], errors="coerce")
    candidates = candidates.dropna(subset=["permco", "cik"])
    candidates["cik"] = candidates["cik"].astype(int)
    for name in ("effective_from", "effective_to"):
        candidates[name] = pd.to_datetime(candidates[name], errors="coerce")
    matched = rows.merge(
        candidates[["permco", "cik", "effective_from", "effective_to"]],
        on="permco",
        how="inner",
    )
    matched = matched.loc[
        matched["effective_from"].le(matched["_day"]) & matched["effective_to"].ge(matched["_day"])
    ].drop_duplicates(["_position", "cik"])
    counts = matched.groupby("_position")["cik"].size()
    ciks = matched.groupby("_position")["cik"].first()
    resolved = {}
    for position, row in enumerate(rows.itertuples(index=False, name=None)):
        count = counts.get(position, 0)
        cik = int(ciks[position]) if count == 1 else None
        status = (
            "verified" if count == 1 else "linkage_conflict" if count > 1 else "linkage_unresolved"
        )
        resolved[str(row[0]), pd.Timestamp(row[2])] = cik, status
    return resolved


def _current(
    facts: pd.DataFrame,
    cik: int,
    cutoff: pd.Timestamp,
    day: pd.Timestamp,
    archive_start: pd.Timestamp,
) -> pd.DataFrame:
    if facts.empty:
        return facts.copy()
    selected = facts.loc[
        facts["cik"].eq(cik)
        & facts["fact_available_at"].le(cutoff)
        & facts["end"].le(day)
        & facts["end"].ge(archive_start)
        & ~facts["status"].eq("invalid_period")
        & facts["value_type"].isin(["numeric", "categorical"])
    ].copy()
    selected["_source_order"] = selected["source_kind"].eq("original_filing").astype(int)
    selected["fact_age_days"] = _elapsed_days(pd.Series(day, index=selected.index), selected["end"])
    return selected.sort_values(["end", "fact_available_at", "accession", "_source_order"])


def _provenance(frame: pd.DataFrame) -> str:
    columns = [
        name
        for name in (
            "concept",
            "value",
            "unit",
            "start",
            "end",
            "accession",
            "filed",
            "accepted",
            "dimensions",
            "source_url",
            "source_sha256",
            "semantic_evidence_url",
            "semantic_scope",
        )
        if name in frame
    ]
    return frame[columns].to_json(orient="records", date_format="iso")


def _official_url(value: object) -> bool:
    return urlparse(str(value)).hostname in {"www.sec.gov", "data.sec.gov"}


def _acquisition_issue(root: Path, cik: int) -> str:
    filename = root / "acquisition.json"
    if not filename.exists():
        return "no_available_native_facts"
    issues = {
        row["status"]
        for row in json.loads(filename.read_text()).get("requests", [])
        if str(cik) in row.get("url", "") or f"{cik:010}" in row.get("url", "")
    }
    for status in (
        "access_denied",
        "blocked_host",
        "network_error",
        "parse_error",
        "identity_required",
        "not_acquired_offline",
        "http_error",
        "http_not_found",
    ):
        if status in issues:
            return f"sec_{status}"
    return "no_available_native_facts"


def current_sic(root: Path, cik: int | None) -> str | None:
    """The filer's current four-digit SIC from its frozen submissions record.

    SEC submissions expose only the current code, so industry networks built from it
    carry today's classification back in time; ``0000`` and blanks are missing.
    """
    if cik is None:
        return None
    filename = root / "submissions" / f"CIK{cik:010}.json"
    compressed = filename.with_suffix(".json.gz")
    if filename.is_file():
        record = json.loads(filename.read_text())
    elif compressed.is_file():
        record = json.loads(gzip.decompress(compressed.read_bytes()))
    else:
        return None
    if not isinstance(record, dict):
        return None
    code = str(record.get("sic") or "").strip()
    return code if code.isdigit() and int(code) > 0 else None


def market_equity(monthly: pd.DataFrame) -> dict[int, pd.Series]:
    """CRSP issuer market equity in USD by PERMCO and month end, summed over classes."""
    if monthly.empty or "market_cap_usd" not in monthly:
        return {}
    month = (
        monthly["month"]
        if "month" in monthly
        else pd.to_datetime(monthly["date"]).dt.to_period("M").dt.to_timestamp("M")
    )
    totals = monthly.assign(month=month).groupby(["permco", "month"])["market_cap_usd"].sum()
    return {
        int(str(permco)): series.droplevel("permco")
        for permco, series in totals.groupby(level="permco")
    }


def _characteristics(
    facts: pd.DataFrame, equity: pd.Series, base: dict[str, Any]
) -> list[dict[str, Any]]:
    rows = []
    for item in characteristics(facts, equity):
        evidence = item.evidence
        rows.append(
            {
                **base,
                "characteristic": item.name,
                "value": item.value,
                "status": "available" if not item.reason else "unavailable",
                "reason": item.reason,
                "fact_available_at": evidence["fact_available_at"].max()
                if not evidence.empty and "fact_available_at" in evidence
                else pd.NaT,
                "components": _provenance(evidence) if not evidence.empty else "[]",
            }
        )
    return rows


def _broad_frame(selected: pd.DataFrame, base: dict[str, Any], day: pd.Timestamp) -> pd.DataFrame:
    """Materialize one full native fact panel with vectorized period identifiers."""
    ends = selected["end"].dt.to_period("Q")
    lag = day.to_period("Q").ordinal - ends.astype("int64")
    end_offset = _elapsed_days(ends.dt.end_time.dt.normalize(), selected["end"])
    duration = _elapsed_days(selected["end"], selected["start"]).astype("Int64").astype("string")
    duration = duration.fillna("instant")
    prefix = selected["concept"].astype(str)
    for name in ("unit", "dimensions", "period_kind"):
        prefix = prefix + "|" + selected[name].astype(str)
    identifier = (
        prefix
        + "|lag"
        + lag.astype(str)
        + "|end_offset"
        + end_offset.astype(str)
        + "|span"
        + duration
    )
    columns = [name for name in BROAD_COLUMNS if name in selected]
    broad = selected[columns].copy()
    broad["feature_id"] = identifier.astype(object)
    broad["taxonomy"] = selected["namespace"]
    for name, value in base.items():
        broad[name] = value
    return broad.reindex(columns=BROAD_COLUMNS)


def _build_feature_chunk(  # noqa: PLR0913 -- bounded CIK task and cached shared metadata.
    quarterly: pd.DataFrame,
    monthly: pd.DataFrame,
    source_dir: Path,
    spec: StudySpec,
    *,
    normalized: pd.DataFrame | None = None,
    links: pd.DataFrame | None = None,
    equity: dict[int, pd.Series] | None = None,
    cutoffs: dict[pd.Timestamp, tuple[pd.Timestamp, pd.Timestamp]] | None = None,
    resolved_links: dict[tuple[str, pd.Timestamp], tuple[int | None, str]] | None = None,
) -> dict[str, pd.DataFrame]:
    """Materialize one pre-quarter information set for every population task-quarter.

    Missing original geometry never removes a row from the availability ledger.
    A verified identity and at least one available native scalar determine the
    XBRL-available analytical population; richer features retain native missingness.
    """
    root = source_root(source_dir)
    filename = root / "crosswalk.csv"
    crosswalk = (
        links
        if links is not None
        else (
            pd.read_csv(filename) if filename.exists() else pd.DataFrame(columns=CROSSWALK_COLUMNS)
        )
    )
    linked_ciks = set(
        pd.to_numeric(
            crosswalk.loc[
                crosswalk["status"].isin({"verified_interval", "verified_observation"}), "cik"
            ],
            errors="coerce",
        )
        .dropna()
        .astype(int)
    )
    facts = (
        normalized
        if normalized is not None
        else _normalized_facts(load_source_facts(root, linked_ciks))
    )
    equities = equity if equity is not None else market_equity(monthly)
    sic_codes: dict[int | None, str | None] = {}
    chars: list[dict[str, Any]] = []
    broad: list[pd.DataFrame] = []
    availability: list[dict[str, Any]] = []
    first = pd.Timestamp(getattr(spec, "feature_start", "2009-01-01"))
    archive_start = pd.Timestamp(spec.archive_start)
    population = quarterly[["issuer_id", "permco", "quarter"]].drop_duplicates()
    for record in population.to_dict("records"):
        quarter = pd.Timestamp(record["quarter"]).to_period("Q").end_time.normalize()
        day, cutoff = cutoffs[quarter] if cutoffs is not None else _cutoff(quarter, monthly)
        permco = int(record["permco"])
        base = {
            "issuer_id": record["issuer_id"],
            "permco": permco,
            "quarter": quarter,
            "cutoff": cutoff,
        }
        cik, link_status = (
            resolved_links[str(record["issuer_id"]), quarter]
            if resolved_links is not None
            else _linked_cik(crosswalk, permco, day)
        )
        current = (
            _current(facts, cik, cutoff, day, archive_start)
            if cik is not None and day >= first
            else facts.iloc[:0]
        )
        numeric_or_categorical = (
            current["value_type"].isin({"numeric", "categorical"})
            if not current.empty
            else pd.Series(dtype=bool)
        )
        xbrl_available = bool(not current.empty and numeric_or_categorical.any())
        if day < first:
            reason = "before_xbrl_feature_window"
        elif cik is None:
            reason = link_status
        elif current.empty:
            reason = _acquisition_issue(root, cik)
        else:
            reason = ""
        if cik not in sic_codes:
            sic_codes[cik] = current_sic(root, cik)
        characteristic_rows = _characteristics(
            current, equities.get(permco, pd.Series(dtype=float)), base
        )
        chars.extend(characteristic_rows)
        availability.append(
            {
                **base,
                "cik": cik,
                "xbrl_available": xbrl_available,
                "status": "available" if xbrl_available else "unavailable",
                "reason": reason,
                "native_scalar_count": len(current),
                "original_characteristics_available": sum(
                    row["status"] == "available" for row in characteristic_rows
                ),
                "sic": sic_codes[cik],
            }
        )
        if current.empty:
            continue
        keys = ["concept", "unit", "dimensions", "start", "end"]
        selected = current.drop_duplicates(keys, keep="last")
        broad.append(_broad_frame(selected, base, day))
    return {
        "crosswalk": crosswalk,
        "facts": facts,
        "characteristics": pd.DataFrame(chars, columns=CHAR_COLUMNS),
        "broad": pd.concat(broad, ignore_index=True)
        if broad
        else pd.DataFrame(columns=BROAD_COLUMNS),
        "availability": pd.DataFrame(availability, columns=AVAILABILITY_COLUMNS),
    }


def _write_partition(frame: pd.DataFrame, directory: Path, number: int) -> None:
    """Give scalar source columns a consistent physical schema across issuer chunks."""
    directory.mkdir(parents=True, exist_ok=True)
    saved = frame.copy()
    for name in saved:
        if name in {"quarter", "start", "end"}:
            saved[name] = pd.to_datetime(saved[name])
        elif name in {"fact_available_at", "cutoff"}:
            saved[name] = pd.to_datetime(saved[name], utc=True)
        elif name in {"is_standard", "entity_wide"}:
            saved[name] = saved[name].astype(bool)
        elif (
            name == "value"
            or is_object_dtype(saved[name].dtype)
            or is_string_dtype(saved[name].dtype)
        ):
            saved[name] = saved[name].astype("string")
    atomic_parquet(directory / f"part-{number:06d}.parquet", saved)


def build_features(  # noqa: PLR0912, PLR0915, C901 -- one bounded source materialization.
    quarterly: pd.DataFrame,
    monthly: pd.DataFrame,
    source_dir: Path,
    spec: StudySpec,
    *,
    destination: Path | None = None,
) -> dict[str, pd.DataFrame]:
    """Build unchanged information sets one CIK at a time.

    The default returns in-memory frames for small fixtures and bounded reviews.
    Destination mode writes facts/broad parquet partitions and a global first-known
    feature schema, retaining only characteristics and availability in memory. No
    concept, period or missing value is removed for computational convenience.
    """
    root = source_root(source_dir)
    filename = root / "crosswalk.csv"
    crosswalk = (
        pd.read_csv(filename) if filename.exists() else pd.DataFrame(columns=CROSSWALK_COLUMNS)
    )
    population = (
        quarterly[["issuer_id", "permco", "quarter"]].drop_duplicates().reset_index(drop=True)
    )
    date_column = "date" if "date" in monthly else "month"
    clock = monthly[[date_column]].drop_duplicates().reset_index(drop=True)
    cutoffs = {
        pd.Timestamp(quarter): _cutoff(pd.Timestamp(quarter), clock)
        for quarter in population["quarter"].unique()
    }
    resolved_links = _population_links(population, crosswalk, cutoffs)
    tasks: dict[int | None, list[int]] = {}
    for position, row in enumerate(population.to_dict("records")):
        cik, _ = resolved_links[str(row["issuer_id"]), pd.Timestamp(row["quarter"])]
        tasks.setdefault(cik, []).append(position)
    small: dict[str, list[pd.DataFrame]] = {"characteristics": [], "availability": []}
    large: dict[str, list[pd.DataFrame]] = {"facts": [], "broad": []}
    schema: dict[str, tuple[pd.Timestamp, bool, bool, str, str]] = {}
    empty_facts = _normalized_facts(pd.DataFrame(columns=FACT_COLUMNS))
    empty_broad = pd.DataFrame(columns=BROAD_COLUMNS)
    equities = market_equity(monthly)
    if destination is not None:
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("facts", "broad"):
            directory = destination / name
            directory.mkdir(parents=True, exist_ok=True)
            # Only generated partition names owned by this function are replaced.
            for previous in directory.glob("part-*.parquet"):
                previous.unlink()
    for number, (cik, positions) in enumerate(tasks.items()):
        selected = population.iloc[positions]
        facts = (
            _normalized_facts(load_source_facts(root, {cik})) if cik is not None else empty_facts
        )
        links = crosswalk.loc[crosswalk["permco"].isin(selected["permco"])]
        chunk = _build_feature_chunk(
            selected,
            clock,
            root,
            spec,
            normalized=facts,
            links=links,
            equity=equities,
            cutoffs=cutoffs,
            resolved_links=resolved_links,
        )
        for name, pieces in small.items():
            pieces.append(chunk[name])
        broad = chunk["broad"]
        if not broad.empty:
            declared_types = feature_value_types(broad)
            metadata_columns = ["is_standard", "entity_wide", "dimensions"]
            if (
                broad.groupby("feature_id")[metadata_columns]
                .nunique(dropna=False)
                .gt(1)
                .any()
                .any()
            ):
                message = "One XBRL feature identifier has conflicting source metadata."
                raise ValueError(message)
            known = broad.groupby("feature_id", sort=False).agg(
                quarter=("quarter", "min"),
                is_standard=("is_standard", "first"),
                entity_wide=("entity_wide", "first"),
                dimensions=("dimensions", "first"),
            )
            for feature, row in known.iterrows():
                key = str(feature)
                first = pd.Timestamp(row["quarter"])
                metadata = (
                    bool(row["is_standard"]),
                    bool(row["entity_wide"]),
                    str(row["dimensions"]),
                    declared_types[key],
                )
                if key in schema:
                    first = min(first, schema[key][0])
                    if metadata != schema[key][1:]:
                        message = "One XBRL feature identifier has conflicting source metadata."
                        raise ValueError(message)
                schema[key] = (first, *metadata)
        for name, pieces in large.items():
            if destination is None:
                pieces.append(chunk[name])
            elif not chunk[name].empty:
                _write_partition(chunk[name], destination / name, number)
        LOGGER.info(
            "Prepared SEC CIK %s (%d/%d): %d source facts, %d task quarters, "
            "%d XBRL-available rows, %d broad facts",
            cik if cik is not None else "unresolved",
            number + 1,
            len(tasks),
            len(facts),
            len(selected),
            int(chunk["availability"]["xbrl_available"].sum()),
            len(broad),
        )
    result = {
        "crosswalk": crosswalk,
        "characteristics": pd.concat(small["characteristics"], ignore_index=True)
        if small["characteristics"]
        else pd.DataFrame(columns=CHAR_COLUMNS),
        "availability": pd.concat(small["availability"], ignore_index=True)
        if small["availability"]
        else pd.DataFrame(columns=AVAILABILITY_COLUMNS),
    }
    for name, empty in (("facts", empty_facts), ("broad", empty_broad)):
        result[name] = (
            pd.concat(large[name], ignore_index=True)
            if destination is None and large[name]
            else empty
        )
        if destination is not None and not any((destination / name).glob("part-*.parquet")):
            _write_partition(empty, destination / name, 0)
    if destination is not None:
        fields = pd.DataFrame(
            [(feature, *values) for feature, values in sorted(schema.items())],
            columns=[
                "feature_id",
                "quarter",
                "is_standard",
                "entity_wide",
                "dimensions",
                "value_type",
            ],
        ).astype(
            {
                "feature_id": "string",
                "quarter": "datetime64[ns]",
                "is_standard": "bool",
                "entity_wide": "bool",
                "dimensions": "string",
                "value_type": "string",
            }
        )
        atomic_parquet(destination / "schema.parquet", fields)
    return result


def read_feature_rows(
    source: Path,
    keys: pd.MultiIndex,
    *,
    standard_only: bool = False,
) -> pd.DataFrame:
    """Read exactly requested issuer-quarter rows, without a global dense pivot."""
    if keys.names != ["issuer_id", "quarter"]:
        message = "Feature row keys must be named issuer_id, quarter in that order."
        raise ValueError(message)
    if not len(keys):
        return pd.DataFrame(columns=BROAD_COLUMNS)
    requested = keys.to_frame(index=False)
    filters = []
    for quarter, group in requested.groupby("quarter", sort=False):
        predicate: list[tuple[str, str, object]] = [
            ("quarter", "==", pd.Timestamp(str(quarter))),
            ("issuer_id", "in", group["issuer_id"].astype(str).tolist()),
        ]
        if standard_only:
            predicate.extend([("is_standard", "==", True), ("entity_wide", "==", True)])
        filters.append(predicate)
    frame = pd.read_parquet(source, filters=filters)
    return frame.merge(
        requested.drop_duplicates(),
        on=["issuer_id", "quarter"],
        how="inner",
        validate="many_to_one",
    )
