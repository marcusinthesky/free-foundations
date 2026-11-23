"""Freeze the contexts shared by the T08 financial comparisons."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.artifacts.metadata import write_json
from free_foundations.study.panel.matched_operands import operand_history, operand_snapshots
from free_foundations.study.panel.store import inputs
from free_foundations.study.representations.arrays import _save_states
from free_foundations.study.representations.contexts import (
    _context_panel,
    load_contexts,
    original_view,
    prepare_quarter,
)
from free_foundations.study.spec import CHARACTERISTICS, digest_json, file_hash

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.encoders.context import Prepared

RUNGS = ("fernandez", "operands", "standard_xbrl", *CHARACTERISTICS)


def select_columns(data: Prepared, group: str, *, omit: bool) -> Prepared:
    """Change only the features, preserving the fixed context labels and rows."""
    indices = [
        index
        for index, name in enumerate(data.features)
        if name.startswith((f"original:{group}:", f"operands:{group}:")) != omit
    ]
    if not indices or len(indices) == len(data.features):
        message = f"Characteristic {group!r} did not select a proper feature subset."
        raise ValueError(message)
    return replace(
        data,
        support=data.support[:, indices],
        query=data.query[:, indices],
        features=tuple(data.features[index] for index in indices),
        digest=digest_json({"parent": data.digest, "columns": indices}),
    )


def _matched(reference: Prepared, candidate: Prepared, quarter: str, rung: str) -> None:
    if (
        reference.support_ids != candidate.support_ids
        or reference.tickers != candidate.tickers
        or reference.available_at != candidate.available_at
        or reference.query_period != candidate.query_period
        or not np.array_equal(reference.targets, candidate.targets)
    ):
        message = f"Unmatched observations, labels or cutoff for {quarter}/{rung}."
        raise ValueError(message)


def _save(root: Path, quarter: str, rung: str, data: Prepared) -> dict[str, Any]:
    destination = root / quarter / rung / "context.npz"
    destination.parent.mkdir(parents=True, exist_ok=True)
    _save_states(
        destination, {"support": data.support, "query": data.query, "targets": data.targets}
    )
    return {
        "quarter": quarter,
        "rung": rung,
        "sha256": file_hash(destination),
        "features": data.features,
        "support_ids": data.support_ids,
        "tickers": data.tickers,
        "year": data.year,
        "digest": data.digest,
        "available_at": data.available_at.isoformat() if data.available_at else None,
        "preprocessing": data.preprocessing,
        "query_period": data.query_period,
    }


def _legacy_quarter(
    data: Prepared | None, quarter: str, rung: str, previous: dict[str, Prepared]
) -> Prepared:
    if (
        data is None
        or rung in previous
        or data.query_period != quarter
        or data.support.shape != (len(data.support_ids), len(data.features))
        or data.query.shape != (len(data.tickers), len(data.features))
        or data.targets.shape != (len(data.support_ids),)
        or len(set(data.features)) != len(data.features)
        or len(set(data.support_ids)) != len(data.support_ids)
        or len(set(data.tickers)) != len(data.tickers)
        or not np.isfinite(data.targets).all()
        or np.isinf(data.support).any()
        or np.isinf(data.query).any()
    ):
        message = f"Invalid legacy context for {quarter}/{rung}."
        raise ValueError(message)
    return data


def prepare_contexts(
    panel: Path, sources: Path, legacy_contexts: Path, output: Path, params: Path
) -> None:
    """Freeze three comparable inputs and the four ratio subsets."""
    spec, tables = inputs(panel, params)
    prepared = json.loads((panel / "manifest.json").read_text())
    frozen = json.loads((sources / "manifest.json").read_text())
    if prepared["source_crsp_sha256"] != frozen["crsp_sha256"]:
        message = "Prepared panel and frozen CRSP sources disagree."
        raise ValueError(message)
    master = tables["panel"]
    char = tables["characteristics"]
    snapshots = operand_snapshots(char)
    source_digest = file_hash(panel / "manifest.json")
    legacy_by_date: dict[str, dict[str, Prepared]] = {}
    for quarter, rung, data in load_contexts(legacy_contexts, spec.rungs, source_digest):
        previous = legacy_by_date.setdefault(quarter, {})
        previous[rung] = _legacy_quarter(data, quarter, rung, previous)
    expected = {
        str(pd.Timestamp(quarter).date()) for quarter in spec.panel_calendar if quarter.quarter == 1
    }
    if expected != legacy_by_date.keys():
        message = "Legacy contexts have missing or unexpected formation quarters."
        raise ValueError(message)
    records = []
    for quarter, legacy in sorted(legacy_by_date.items()):
        if set(legacy) != set(spec.rungs):
            message = f"Legacy contexts lack one of the required views at {quarter}."
            raise ValueError(message)
        ratio, broad = legacy["fernandez"], legacy["standard_xbrl"]
        _matched(ratio, broad, quarter, "standard_xbrl")
        date = pd.Timestamp(quarter)
        selection = _context_panel(master, char, date, spec)
        rebuilt = prepare_quarter(original_view(selection, char, spec), char, master, date, spec)
        if (
            rebuilt is None
            or rebuilt.digest != ratio.digest
            or not np.array_equal(rebuilt.support, ratio.support, equal_nan=True)
            or not np.array_equal(rebuilt.query, ratio.query, equal_nan=True)
        ):
            message = f"Legacy ratio context disagrees with the prepared panel at {quarter}."
            raise ValueError(message)
        _matched(ratio, rebuilt, quarter, "fernandez")
        view = operand_history(selection, snapshots, years=spec.characteristic_history_years)
        # Keep advertised but entirely missing annual slots, as in the ratio histories.
        view.attrs["column_first_available"] = dict.fromkeys(
            view.columns, selection["quarter"].min()
        )
        view.attrs["column_value_types"] = dict.fromkeys(view.columns, "numeric")
        operands = prepare_quarter(view, char, master, date, spec)
        if operands is None:
            message = f"Matched operands could not preserve the reference context at {quarter}."
            raise ValueError(message)
        _matched(ratio, operands, quarter, "operands")
        variants = legacy | {"operands": operands}
        variants.update({name: select_columns(ratio, name, omit=False) for name in CHARACTERISTICS})
        records.extend(_save(output, quarter, name, variants[name]) for name in RUNGS)
    write_json(
        output / "manifest.json",
        {
            "input_digest": source_digest,
            "master": prepared["master"],
            "frozen_sources_sha256": file_hash(sources / "manifest.json"),
            "legacy_contexts_sha256": file_hash(legacy_contexts / "manifest.json"),
            "availability": {
                "population_issuer_quarters": prepared["population_issuer_quarters"],
                "analytical_issuer_quarters": prepared["analytical_issuer_quarters"],
                "reasons": prepared["availability_reasons"],
            },
            "broad": {
                "source": "legacy standard_xbrl, including all ratio-history slots",
                "field": (
                    "latest as-of undimensioned entity-wide standard concept by unit "
                    "and period kind"
                ),
                "minimum_coverage": spec.standard_min_coverage,
                "denominator": ("unique support and query keys with eligible standard fact rows"),
            },
            "operands": {
                "units": "USD as reported without rescaling",
                "timing": "same accounting vintages, cutoffs and annual slots as the ratio rung",
                "missingness": "operands stay visible for missing or implausible ratios",
                "shared": (
                    "balance-sheet market equity serves both ME/assets and ME/book; "
                    "a single-group omission keeps operands still used by another group"
                ),
            },
            "contexts": records,
        },
    )
