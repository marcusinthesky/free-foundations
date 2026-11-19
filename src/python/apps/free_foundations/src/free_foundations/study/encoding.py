"""Matched information ladders with native missingness and full-column block coverage."""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import replace
from datetime import UTC, timedelta
from importlib import metadata as package_metadata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from free_foundations.data import write_json
from free_foundations.representations import cache as state_cache
from free_foundations.representations.checkpoints import expected as checkpoint_expected
from free_foundations.representations.encoding import Prepared, foundation_states
from free_foundations.study.features import feature_value_types, read_feature_rows
from free_foundations.study.history import annual_history_slots
from free_foundations.study.source_io import atomic_output
from free_foundations.study.spec import (
    StudySpec,
    digest_json,
    file_hash,
    frame_digest,
    panel_contract,
)

KEYS = ["issuer_id", "quarter"]
SCHEMA = "column_first_available"
VALUE_TYPES = "column_value_types"


def _implementation_provenance(spec: StudySpec) -> dict[str, Any]:
    """Identify reviewed code and approved weights without importing model runtimes."""
    package = Path(__file__).resolve().parents[1]
    sources = {
        *state_cache.SOURCES,
        "representations/checkpoints.py",
        "representations/setup.py",
        "study/encoding.py",
        "study/features.py",
        "study/history.py",
        "study/source_io.py",
        "study/spec.py",
    }
    checkpoints = {}
    for model in spec.models:
        base = model.partition("_random")[0].removesuffix("_labelnull")
        checkpoints[model] = (
            checkpoint_expected(base)
            if base in state_cache.RUNTIMES
            else {"status": "external_adapter"}
        )
    return {
        "schema": 1,
        "source_sha256": {name: file_hash(package / name) for name in sorted(sources)},
        "lock_sha256": file_hash(package.parents[3] / "uv.lock"),
        "checkpoints": checkpoints,
    }


def _runtime_provenance(spec: StudySpec) -> dict[str, Any]:
    """Record extraction dependencies; financial loading does not require these packages."""
    names = {"numpy", "pandas", "pyarrow", "scipy", "scikit-learn", "torch", "huggingface-hub"}
    for model in spec.models:
        base = model.partition("_random")[0].removesuffix("_labelnull")
        if base in state_cache.RUNTIMES:
            names.add(state_cache.RUNTIMES[base])
    runtimes = {}
    for name in sorted(names):
        try:
            package = package_metadata.distribution(name)
        except package_metadata.PackageNotFoundError:
            runtimes[name] = {"status": "not_installed"}
        else:
            runtimes[name] = {
                "status": "installed",
                "version": package.version,
                "direct_url": json.loads(package.read_text("direct_url.json") or "null"),
            }
    return {"python": sys.version, "packages": runtimes}


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


def feature_blocks(data: Prepared, width: int) -> list[Prepared]:
    """Partition every ordered column exactly once, without random feature subsampling."""
    if width < 1:
        message = "Block width must be positive."
        raise ValueError(message)
    blocks = []
    for start in range(0, len(data.features), width):
        stop = min(start + width, len(data.features))
        blocks.append(
            replace(
                data,
                support=data.support[:, start:stop],
                query=data.query[:, start:stop],
                features=data.features[start:stop],
                digest=digest_json({"parent": data.digest, "columns": [start, stop]}),
            )
        )
    if tuple(name for block in blocks for name in block.features) != data.features:
        message = "Column partition lost or duplicated source features."
        raise ValueError(message)
    return blocks


def conventional_states(data: Prepared) -> dict[str, np.ndarray]:
    """The direct control: the same features, support-median imputed with indicators.

    Imputation and standardization use the labeled support rows only and fit no
    parameter to returns; the result is a deterministic coordinate system for the
    same information the foundation models receive.
    """
    imputer = SimpleImputer(strategy="median", keep_empty_features=True, add_indicator=True)
    train = imputer.fit_transform(data.support)
    query = imputer.transform(data.query)
    scaler = StandardScaler().fit(train)
    return {"direct": np.asarray(scaler.transform(query), dtype=float)}


def _validate_embeddings(values: np.ndarray, rows: int) -> None:
    if values.ndim != 2 or values.shape[0] != rows or not values.shape[1]:
        message = "Adapter embeddings must be nonempty and preserve every ordered query row."
        raise ValueError(message)
    if not np.isfinite(values).all():
        message = "Adapter embeddings must be finite; native missing features cannot pass through."
        raise ValueError(message)


def _foundation_blocks(
    blocks: list[Prepared], model: str, models: tuple[Path, Path], contracts: list[dict[str, Any]]
) -> np.ndarray:
    pieces = []
    base = model.partition("_random")[0].removesuffix("_labelnull")
    for block in blocks:
        # Use the same identity calculation as foundation_states; approved metadata
        # suffices here because its existing resolver verifies the actual weight bytes.
        identity = (
            state_cache.identity(block, model, checkpoint_expected(base))
            if base in state_cache.RUNTIMES
            else None
        )
        readouts = foundation_states(block, model, *models)
        values = np.asarray(readouts.get("late"), dtype=float)
        _validate_embeddings(values, len(block.tickers))
        pieces.append(values)
        contracts.append(
            {
                "context_digest": block.digest,
                "cache_contract_sha256": digest_json(identity) if identity is not None else None,
                "execution": identity["execution"] if identity is not None else None,
            }
        )
    return np.concatenate(pieces, axis=1)


def _save_states(destination: Path, states: dict[str, np.ndarray]) -> None:
    # The typed payload makes it explicit that no array can bind NumPy's allow_pickle argument.
    payload: dict[str, Any] = dict(states)
    with atomic_output(destination) as temporary, temporary.open("wb") as stream:
        np.savez_compressed(stream, allow_pickle=False, **payload)


def _unavailable_context(common: dict[str, Any]) -> dict[str, Any]:
    return common | {
        "status": "training_context_unavailable",
        "reason": "fewer_than_two_observed_past_context_labels",
    }


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


def encode_panel(  # noqa: PLR0913, PLR0915 -- matched source/context/model availability ledger.
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    broad: pd.DataFrame | Path,
    spec: StudySpec,
    output: Path,
    *,
    weights: Path,
    states_cache: Path,
    input_digest: str | None = None,
) -> None:
    """Extract all declared states; unsupported cells are statuses, never smaller cohorts.

    Quarters before the panel start are context only: they supply labeled support
    rows but no query states, because no analysis reads them.
    """
    output.mkdir(parents=True, exist_ok=True)
    contract = panel_contract(panel, spec)
    provenance = {
        "implementation": _implementation_provenance(spec),
        "runtimes": _runtime_provenance(spec),
    }
    provenance_digest = digest_json(provenance)
    records: list[dict[str, Any]] = []
    contexts: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {}
    first = pd.Timestamp(spec.panel_start)
    for quarter in sorted(panel["quarter"].unique()):
        date = pd.Timestamp(quarter)
        # Networks form annually from January information, like the December roster.
        if date < first or date.quarter != 1:
            continue
        selected = _context_panel(panel, characteristics, date, spec)
        shared = {
            "quarter": str(date.date()),
            "master": contract,
            "input_digest": input_digest,
            "provenance_sha256": provenance_digest,
        }
        if int(selected["quarter"].lt(date).sum()) < 2:
            records.extend(_unavailable_context(shared | {"rung": rung}) for rung in spec.rungs)
            continue
        facts, schema = _quarter_facts(broad, selected, date)
        for rung in spec.rungs:
            view = rung_view(selected, characteristics, facts, spec, rung, schema=schema)
            data = _required_context(view, characteristics, panel, date, spec)
            common = shared | {"rung": rung}
            signature = data.support_ids, data.tickers
            context_key = str(date.date())
            if contexts.setdefault(context_key, signature) != signature:
                message = (
                    "Information rungs disagree on their ordered support or query observations."
                )
                raise ValueError(message)
            blocks = feature_blocks(data, spec.block_columns)
            path = output / str(date.date()) / rung
            path.mkdir(parents=True, exist_ok=True)
            context = common | {
                "context_digest": data.digest,
                "support_ids": data.support_ids,
                "issuer_ids": data.tickers,
                "features": data.features,
                "blocks": [list(block.features) for block in blocks],
                "preprocessing": "native NA for foundation models; support-only controls",
                "available_at": data.available_at.isoformat() if data.available_at else None,
                "provenance": provenance,
            }
            write_json(path / "context.json", context)
            states: dict[str, np.ndarray] = {}
            try:
                states = conventional_states(data)
                for values in states.values():
                    _validate_embeddings(values, len(data.tickers))
            except (ImportError, ValueError, RuntimeError, OSError) as error:
                states = {}
                records.append(
                    common
                    | {
                        "model": "controls",
                        "status": "model_rung_unavailable",
                        "reason": str(error),
                        "context_digest": data.digest,
                    }
                )
            native_contracts: dict[str, list[dict[str, Any]]] = {}
            for model in spec.models:
                try:
                    model_contracts: list[dict[str, Any]] = []
                    states[model] = _foundation_blocks(
                        blocks, model, (weights, states_cache), model_contracts
                    )
                    native_contracts[model] = model_contracts
                except (ImportError, ValueError, RuntimeError, OSError) as error:
                    records.append(
                        common
                        | {
                            "model": model,
                            "status": "model_rung_unavailable",
                            "reason": str(error),
                            "context_digest": data.digest,
                        }
                    )
            destination = path / "states.npz"
            _save_states(destination, states)
            record = context | {
                "status": "complete" if {*spec.models, "direct"}.issubset(states) else "incomplete",
                "models": sorted(states),
                "sha256": file_hash(destination),
                "path": str(destination),
                "native_cache_contracts": native_contracts,
            }
            write_json(path / "manifest.json", record)
            records.append(record)
    available = any("path" in record and record["models"] for record in records)
    complete = bool(records) and all(record["status"] == "complete" for record in records)
    status = "complete" if complete else "incomplete" if available else "unavailable"
    write_json(
        output / "manifest.json",
        {
            "master": contract,
            "status": status,
            "states": records,
            "input_digest": input_digest,
            "provenance": provenance,
            "provenance_sha256": provenance_digest,
        },
    )


def _validate_representation_manifest(
    manifest: dict[str, Any],
    panel: pd.DataFrame,
    spec: StudySpec,
    expected_input_digest: str | None,
) -> None:
    if manifest["master"] != panel_contract(panel, spec):
        message = "Representation manifest belongs to a different master experiment."
        raise ValueError(message)
    if manifest.get("input_digest") != expected_input_digest:
        message = "Representation prepared-input digest disagrees with the feature vintage."
        raise ValueError(message)
    provenance = manifest.get("provenance")
    if not isinstance(provenance, dict) or digest_json(provenance) != manifest.get(
        "provenance_sha256"
    ):
        message = "Representation extraction provenance is missing or corrupted."
        raise ValueError(message)
    if provenance.get("implementation") != _implementation_provenance(spec):
        message = "Representation implementation, lock or approved checkpoints changed."
        raise ValueError(message)


def _validate_context_provenance(record: dict[str, Any], manifest: dict[str, Any]) -> None:
    if (
        record.get("input_digest") != manifest["input_digest"]
        or record.get("provenance_sha256") != manifest["provenance_sha256"]
    ):
        message = "Representation context belongs to another input or extraction vintage."
        raise ValueError(message)
    if (
        "provenance" in record
        and digest_json(record["provenance"]) != manifest["provenance_sha256"]
    ):
        message = "Representation context extraction provenance is corrupted."
        raise ValueError(message)


class RepresentationStore:
    """Verified, quarter-at-a-time access to saved representation states.

    The manifest and its provenance are validated once; each quarter's arrays are
    hash-checked when read, so memory holds one quarter's states at a time.
    """

    def __init__(
        self,
        output: Path,
        panel: pd.DataFrame,
        spec: StudySpec,
        *,
        expected_input_digest: str | None,
    ) -> None:
        """Validate the representation manifest against the prepared master panel."""
        manifest = json.loads((output / "manifest.json").read_text())
        _validate_representation_manifest(manifest, panel, spec, expected_input_digest)
        self.records: dict[str, list[dict[str, Any]]] = {}
        for record in manifest["states"]:
            _validate_context_provenance(record, manifest)
            if "path" in record:
                self.records.setdefault(record["quarter"], []).append(record)
        self.statuses = [
            {key: record.get(key) for key in ("quarter", "rung", "model", "status", "reason")}
            for record in manifest["states"]
        ]

    def states(self, quarter: pd.Timestamp, issuers: tuple[str, ...]) -> dict[str, np.ndarray]:
        """``rung:model`` arrays for one quarter, rows reordered to ``issuers``."""
        result: dict[str, np.ndarray] = {}
        for record in self.records.get(str(pd.Timestamp(quarter).date()), []):
            path = Path(record["path"])
            if file_hash(path) != record["sha256"]:
                message = "Representation bytes disagree with their manifest."
                raise ValueError(message)
            position = {issuer: index for index, issuer in enumerate(record["issuer_ids"])}
            if any(issuer not in position for issuer in issuers):
                message = "A roster issuer has no representation row for its quarter."
                raise ValueError(message)
            rows = [position[issuer] for issuer in issuers]
            with np.load(path, allow_pickle=False) as arrays:
                if sorted(arrays.files) != record["models"]:
                    message = "Representation inventory disagrees with its manifest."
                    raise ValueError(message)
                for name in arrays.files:
                    values = arrays[name]
                    _validate_embeddings(values, len(record["issuer_ids"]))
                    result[f"{record['rung']}:{name}"] = values[rows]
        return result
