"""Dated support, query selection and information rungs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.artifacts.metadata import write_json
from free_foundations.encoders.context import Prepared
from free_foundations.study.panel.features import feature_value_types, read_feature_rows
from free_foundations.study.panel.history import annual_history_slots
from free_foundations.study.spec import (
    StudySpec,
    digest_json,
    file_hash,
    frame_digest,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


from free_foundations.study.representations.arrays import _save_states

KEYS = ["issuer_id", "quarter"]
SCHEMA = "column_first_available"
VALUE_TYPES = "column_value_types"


def _validate_filing_times(frame: pd.DataFrame) -> None:
    """Reject source-value evidence that was unavailable at its own feature cutoff."""
    if frame.empty or not {"cutoff", "fact_available_at"}.issubset(frame.columns):
        return
    cutoff = pd.to_datetime(frame["cutoff"], utc=True)
    available = pd.to_datetime(frame["fact_available_at"], utc=True)
    reported = frame["value"].notna()
    invalid = (reported & available.isna()) | (available.notna() & available.gt(cutoff))
    if (invalid | (reported & cutoff.isna())).any():
        message = "Feature evidence lacks a filing time or was published after the cutoff."
        raise ValueError(message)


def original_view(
    panel: pd.DataFrame, characteristics: pd.DataFrame, spec: StudySpec
) -> pd.DataFrame:
    """Retain ten annual-spaced as-of slots; missing/constant histories never select rows."""
    _validate_filing_times(characteristics)
    # Duplicate cells are an upstream contract error, not values to aggregate.
    current = characteristics.pivot(  # noqa: PD010 -- reject ambiguous source cells.
        index=KEYS, columns="characteristic", values="value"
    )
    result = annual_history_slots(panel, current, years=spec.characteristic_history_years)
    if not panel.empty:
        result.attrs[SCHEMA] = {
            column: pd.Timestamp(panel["quarter"].min()) for column in result.columns
        }
    result.attrs[VALUE_TYPES] = dict.fromkeys(result.columns, "numeric")
    return result


def _native_feature_values(wide: pd.DataFrame, declared_types: dict[str, str]) -> pd.DataFrame:
    """Canonicalize declared scalars equally before and after parquet serialization."""
    for name, value_type in declared_types.items():
        if name not in wide:
            continue
        values = wide[name]
        if value_type == "numeric":
            numeric = pd.to_numeric(values, errors="coerce")
            if (values.notna() & numeric.isna()).any():
                message = (
                    f"Declared numeric XBRL feature {name!r} contains nonnumeric source values."
                )
                raise ValueError(message)
            wide[name] = numeric.astype(float)
        else:
            wide[name] = values.astype("string")
    return wide


def _standard_rows(broad: pd.DataFrame) -> pd.DataFrame:
    """Entity-wide standard-taxonomy facts, each published by its own feature cutoff."""
    selected = broad.loc[
        broad["is_standard"].fillna(value=False).astype(bool)
        & broad["entity_wide"].fillna(value=False).astype(bool)
    ]
    if "dimensions" in selected:
        selected = selected.loc[selected["dimensions"].fillna("{}").isin(["", "{}", "[]"])]
    _validate_filing_times(selected)
    return selected


def _latest_facts(selected: pd.DataFrame) -> pd.DataFrame:
    """Collapse every lag and offset variant to the most recent disclosed period.

    Ties keep the later source row, so collapsing consecutive source parts and then
    their concatenation keeps the same row as a single pass over all parts.
    """
    if selected.empty:
        return selected
    order = [name for name in ("end", "fact_available_at") if name in selected]
    frame = selected.sort_values(order or KEYS, kind="stable")
    if {"concept", "unit", "period_kind"}.issubset(frame.columns):
        frame = frame.assign(
            feature_id=frame["concept"].astype(str)
            + "|"
            + frame["unit"].astype(str)
            + "|"
            + frame["period_kind"].astype(str)
        )
    return frame.drop_duplicates([*KEYS, "feature_id"], keep="last")


def _standard_snapshot(selected: pd.DataFrame, coverage: float) -> pd.DataFrame:
    """Latest as-of value of each standard concept, unit and period kind.

    Concepts reported by fewer than ``coverage`` of the view's issuer-quarters are
    dropped; the threshold reads disclosure coverage only, never outcomes.
    """
    frame = _latest_facts(selected)
    if frame.empty:
        return frame
    reported = frame.loc[frame["value"].notna(), [*KEYS, "feature_id"]].drop_duplicates()
    rows = len(frame[KEYS].drop_duplicates())
    shares = reported.groupby("feature_id").size() / rows
    return frame.loc[frame["feature_id"].isin(shares.index[shares >= coverage])]


def rung_view(  # noqa: PLR0913 -- matched rows, information inputs and as-of facts.
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    broad: pd.DataFrame,
    spec: StudySpec,
    rung: str,
    *,
    schema: pd.DataFrame | None = None,  # noqa: ARG001 -- streamed callers pass their schema.
) -> pd.DataFrame:
    """Expand information only; the master roster, dates and outcomes remain fixed.

    ``fernandez`` is the annual characteristic history. ``standard_xbrl`` adds the
    latest as-of value of each entity-wide standard-taxonomy concept reported by at
    least ``spec.standard_min_coverage`` of the view's issuer-quarters.
    """
    if rung not in spec.rungs:
        message = f"Undeclared information rung: {rung}"
        raise ValueError(message)
    result = original_view(panel, characteristics, spec)
    if rung == "fernandez" or broad.empty:
        return result
    selected = _standard_rows(broad)
    keys = pd.MultiIndex.from_frame(panel[KEYS])
    selected = selected.loc[pd.MultiIndex.from_frame(selected[KEYS]).isin(keys)]
    selected = _standard_snapshot(selected, spec.standard_min_coverage)
    declared_types = feature_value_types(selected)
    wide = selected.pivot(  # noqa: PD010 -- keys are unique after the snapshot.
        index=KEYS, columns="feature_id", values="value"
    )
    wide = _native_feature_values(wide, declared_types)
    wide.columns = [f"xbrl:{column}" for column in wide.columns]
    joined = result.join(wide, how="left")
    first = selected.groupby("feature_id", sort=True)["quarter"].min()
    joined.attrs[SCHEMA] = result.attrs.get(SCHEMA, {}) | {
        f"xbrl:{name}": pd.Timestamp(date) for name, date in first.items()
    }
    joined.attrs[VALUE_TYPES] = result.attrs[VALUE_TYPES] | {
        f"xbrl:{name}": value_type for name, value_type in declared_types.items()
    }
    return joined


def _context_panel(
    panel: pd.DataFrame, characteristics: pd.DataFrame, quarter: pd.Timestamp, spec: StudySpec
) -> pd.DataFrame:
    """Select the common support keys before reading or pivoting the wide fact table."""
    labels = characteristics.loc[characteristics["characteristic"].eq("market_cap_assets")]
    label_map = labels.set_index(KEYS)["value"]
    candidates = panel.loc[panel["quarter"].lt(quarter)].copy()
    target_dates = pd.DatetimeIndex(candidates["quarter"]) + pd.offsets.QuarterEnd(1)
    target_keys = pd.MultiIndex.from_arrays([candidates["issuer_id"], target_dates], names=KEYS)
    known = (target_dates < quarter) & np.isfinite(label_map.reindex(target_keys).to_numpy(float))
    candidates = candidates.loc[known]
    identifiers = [
        f"{issuer}:{pd.Timestamp(date).date()}"
        for issuer, date in candidates[KEYS].itertuples(index=False, name=None)
    ]
    order = sorted(
        range(len(identifiers)),
        key=lambda position: hashlib.sha256(identifiers[position].encode()).hexdigest(),
    )[: spec.support_rows]
    return pd.concat([candidates.iloc[order], panel.loc[panel["quarter"].eq(quarter)]])


def _source_parts(source: Path) -> list[Path]:
    """Parquet parts in the order a dataset read concatenates them."""
    if source.is_file():
        return [source]
    return sorted(
        path
        for path in source.rglob("*")
        if path.is_file()
        and not any(name.startswith(("_", ".")) for name in path.relative_to(source).parts)
    )


def _quarter_facts(
    broad: pd.DataFrame | Path, context: pd.DataFrame, quarter: pd.Timestamp
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read selected rows and the as-of column catalogue without a full-panel dense pivot.

    A streamed source keeps only each part's latest standard facts. The selected
    rows carry every lag and offset of every concept, millions of rows for a late
    quarter, which the rung's snapshot would drop anyway.
    """
    if isinstance(broad, Path):
        schema = pd.read_parquet(broad.parent / "schema.parquet")
        schema = schema.loc[schema["quarter"].le(quarter)]
        keys = pd.MultiIndex.from_frame(context[KEYS])
        parts = [
            _latest_facts(_standard_rows(read_feature_rows(part, keys)))
            for part in _source_parts(broad)
        ]
        kept = [part for part in parts if not part.empty]
        facts = pd.concat(kept or parts[:1] or [pd.DataFrame(columns=KEYS)], ignore_index=True)
    else:
        known = broad.loc[broad["quarter"].le(quarter)]
        declared_types = feature_value_types(known)
        schema = pd.DataFrame(
            known.groupby(["feature_id", "is_standard", "entity_wide"], as_index=False)[
                "quarter"
            ].min()
        )
        if declared_types:
            schema["value_type"] = schema["feature_id"].map(declared_types)
        facts = broad
    selected = pd.MultiIndex.from_frame(context[KEYS])
    facts = facts.loc[pd.MultiIndex.from_frame(facts[KEYS]).isin(selected)].copy()
    return facts, schema


def scalar_matrix(frame: pd.DataFrame) -> tuple[np.ndarray, tuple[str, ...]]:
    """Losslessly one-hot scalar categories, preserving missingness rather than filling it."""
    pieces: list[np.ndarray] = []
    names: list[str] = []
    declared_types = frame.attrs.get(VALUE_TYPES, {})
    for column in sorted(frame.columns):
        values = frame[column]
        numeric = pd.to_numeric(values, errors="coerce")
        missing = values.isna()
        value_type = declared_types.get(column)
        if value_type not in {None, "numeric", "categorical"}:
            message = f"Unsupported declared scalar value_type for {column!r}: {value_type!r}."
            raise ValueError(message)
        numeric_values = numeric.notna().equals(~missing)
        if value_type == "numeric" and not numeric_values:
            message = f"Declared numeric feature {column!r} contains nonnumeric source values."
            raise ValueError(message)
        if value_type == "numeric" or (value_type is None and numeric_values):
            pieces.append(numeric.to_numpy(dtype=float)[:, None])
            names.append(str(column))
            continue
        # Vocabulary uses only the as-of table passed to this call, never future rows.
        categories = sorted(values.loc[~missing].astype(str).unique())
        if not categories:
            pieces.append(np.full((len(frame), 1), np.nan))
            names.append(str(column))
        for category in categories:
            encoded = values.astype(str).eq(category).to_numpy(dtype=float)
            encoded[missing.to_numpy()] = np.nan
            pieces.append(encoded[:, None])
            names.append(f"{column}:category={category}")
    matrix = np.column_stack(pieces) if pieces else np.empty((len(frame), 0))
    if np.isinf(matrix).any():
        message = "Infinite model features must be resolved in the source-value audit."
        raise ValueError(message)
    if len(set(names)) != len(names):
        message = "Scalar feature names collide after categorical expansion."
        raise ValueError(message)
    return matrix, tuple(names)


def prepare_quarter(
    view: pd.DataFrame,
    characteristics: pd.DataFrame,
    panel: pd.DataFrame,
    quarter: pd.Timestamp,
    spec: StudySpec,
) -> Prepared | None:
    """Choose one past-only labeled context shared across every rung and model."""
    _validate_filing_times(characteristics)
    quarter = pd.Timestamp(quarter)
    if quarter != quarter.to_period("Q").to_timestamp("Q"):
        message = "Representation queries must use calendar-quarter end timestamps."
        raise ValueError(message)
    query = panel.loc[panel["quarter"].eq(quarter)].sort_values("issuer_id")
    ids = tuple(query["issuer_id"].astype(str))
    if not ids:
        return None
    labels = characteristics.loc[characteristics["characteristic"].eq("market_cap_assets")]
    label_map = labels.set_index(KEYS)["value"]
    candidates = view.loc[view.index.get_level_values("quarter") < quarter].copy()
    candidate_quarters = pd.DatetimeIndex(candidates.index.get_level_values("quarter"))
    target_keys = pd.MultiIndex.from_arrays(
        [
            candidates.index.get_level_values("issuer_id"),
            candidate_quarters + pd.offsets.QuarterEnd(1),
        ],
        names=KEYS,
    )
    targets = label_map.reindex(target_keys).to_numpy(dtype=float)
    known = (target_keys.get_level_values("quarter") < quarter) & np.isfinite(targets)
    candidates = candidates.loc[known]
    targets = targets[known]
    support_ids = [f"{issuer}:{pd.Timestamp(date).date()}" for issuer, date in candidates.index]
    order = sorted(
        range(len(support_ids)),
        key=lambda position: hashlib.sha256(support_ids[position].encode()).hexdigest(),
    )[: spec.support_rows]
    if len(order) < 2:
        return None
    candidates = candidates.iloc[order]
    targets = targets[order]
    query_keys = pd.MultiIndex.from_arrays([ids, [quarter] * len(ids)], names=KEYS)
    raw = pd.concat([candidates, view.reindex(query_keys)])
    # Reported all-NA fields remain native NA. A concept that first appears after
    # this query cannot add dimensions or categories to the earlier model context.
    past = view.loc[view.index.get_level_values("quarter") <= quarter]
    first = view.attrs.get(SCHEMA)
    if first is None:
        raw = raw.loc[:, past.notna().any(axis=0)]
    else:
        raw = raw.loc[:, [name for name in raw if pd.Timestamp(first[name]) <= quarter]]
    raw.attrs[VALUE_TYPES] = view.attrs.get(VALUE_TYPES, {})
    matrix, names = scalar_matrix(raw)
    if not names:
        return None
    count = len(candidates)
    cutoff = quarter.to_period("Q").start_time.to_pydatetime() - timedelta(days=1)
    cutoff = cutoff.replace(tzinfo=UTC)
    values = characteristics.loc[characteristics["quarter"].eq(quarter)]
    if "cutoff" in values and values["cutoff"].notna().any():
        cutoff = pd.to_datetime(values["cutoff"], utc=True).min().to_pydatetime()
    payload = {
        "quarter": str(quarter.date()),
        "features": names,
        "support_ids": [support_ids[i] for i in order],
        "issuer_ids": ids,
        "raw_sha256": frame_digest(raw),
        "targets": targets.tolist(),
        "cutoff": cutoff.isoformat(),
        "mode": "native-na-full-coverage-v1",
    }
    return Prepared(
        matrix[:count],
        matrix[count:],
        targets,
        names,
        tuple(support_ids[i] for i in order),
        ids,
        quarter.year,
        digest_json(payload),
        available_at=cutoff,
        preprocessing="native-na-full-coverage-v1",
        query_period=str(quarter.date()),
    )


def _required_context(
    view: pd.DataFrame,
    characteristics: pd.DataFrame,
    panel: pd.DataFrame,
    quarter: pd.Timestamp,
    spec: StudySpec,
) -> Prepared:
    data = prepare_quarter(view, characteristics, panel, quarter, spec)
    if data is None:
        message = "An available common context lost its required support or query rows."
        raise ValueError(message)
    return data


def _contexts(
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    broad: pd.DataFrame | Path,
    spec: StudySpec,
    rungs: tuple[str, ...],
) -> Iterator[tuple[str, str, Prepared | None]]:
    contexts: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    first = pd.Timestamp(spec.panel_start)
    for quarter in sorted(panel["quarter"].unique()):
        date = pd.Timestamp(quarter)
        # Networks form annually from January information, like the December roster.
        if date < first or date.quarter != 1:
            continue
        selected = _context_panel(panel, characteristics, date, spec)
        if int(selected["quarter"].lt(date).sum()) < 2:
            for rung in rungs:
                yield str(date.date()), rung, None
            continue
        facts, schema = _quarter_facts(broad, selected, date)
        for rung in rungs:
            view = rung_view(selected, characteristics, facts, spec, rung, schema=schema)
            data = _required_context(view, characteristics, panel, date, spec)
            signature = data.support_ids, data.tickers
            context_key = str(date.date())
            if contexts.setdefault(context_key, signature) != signature:
                message = (
                    "Information rungs disagree on their ordered support or query observations."
                )
                raise ValueError(message)
            yield str(date.date()), rung, data


def save_contexts(  # noqa: PLR0913, PLR0917 -- prepared panel and output provenance.
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    broad: pd.DataFrame | Path,
    spec: StudySpec,
    output: Path,
    input_digest: str,
) -> None:
    """Persist the common past-only support and ordered queries once per rung."""
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for quarter, rung, data in _contexts(panel, characteristics, broad, spec, spec.rungs):
        entry: dict[str, Any] = {"quarter": quarter, "rung": rung}
        if data is not None:
            path = output / quarter / rung / "context.npz"
            _save_states(
                path, {"support": data.support, "query": data.query, "targets": data.targets}
            )
            entry.update(
                {
                    "sha256": file_hash(path),
                    "features": data.features,
                    "support_ids": data.support_ids,
                    "tickers": data.tickers,
                    "year": data.year,
                    "digest": data.digest,
                    "available_at": data.available_at.isoformat() if data.available_at else None,
                    "preprocessing": data.preprocessing,
                    "query_period": data.query_period,
                }
            )
        rows.append(entry)
    write_json(output / "manifest.json", {"input_digest": input_digest, "contexts": rows})


def load_contexts(
    root: Path, rungs: tuple[str, ...], input_digest: str | None
) -> Iterator[tuple[str, str, Prepared | None]]:
    """Stream verified context arrays for the requested information rungs."""
    manifest = json.loads((root / "manifest.json").read_text())
    if manifest["input_digest"] != input_digest:
        msg = "Prepared contexts belong to a different panel."
        raise ValueError(msg)
    for row in manifest["contexts"]:
        quarter, rung = row["quarter"], row["rung"]
        if rung not in rungs:
            continue
        data = None
        if "sha256" in row:
            path = root / quarter / rung / "context.npz"
            if file_hash(path) != row["sha256"]:
                msg = f"Context checksum mismatch at {path}"
                raise ValueError(msg)
            with np.load(path, allow_pickle=False) as arrays:
                data = Prepared(
                    arrays["support"],
                    arrays["query"],
                    arrays["targets"],
                    tuple(row["features"]),
                    tuple(row["support_ids"]),
                    tuple(row["tickers"]),
                    row["year"],
                    row["digest"],
                    datetime.fromisoformat(row["available_at"]) if row["available_at"] else None,
                    row["preprocessing"],
                    row["query_period"],
                )
        yield quarter, rung, data
