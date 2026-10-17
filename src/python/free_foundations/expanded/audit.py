"""How much a frozen-model geometry depends on query cohort, support and labels."""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING

import numpy as np
import numpy.typing as npt
from scipy.stats import spearmanr

from free_foundations.expanded.distance import pairwise_distance
from free_foundations.expanded.encoding import foundation_states, load_tabfm, variant
from free_foundations.expanded.representations import READOUTS
from free_foundations.pilot.spatial import normalize_weights

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared

type Record = dict[str, str | int | float]
type IntArray = npt.NDArray[np.int64]


def context_audit(data: Prepared) -> Record:
    """Support years, cutoff and how often a query firm's own history is in the support."""
    years = [int(row.rsplit(":", 1)[1]) for row in data.support_ids]
    firms = {row.rsplit(":", 1)[0] for row in data.support_ids}
    return {
        "year": data.year,
        "cutoff": f"{data.year - 1}-12-31",
        "support_rows": len(data.support_ids),
        "first_support_year": min(years),
        "last_support_year": max(years),
        "label_year_max": max(years) + 1,
        "query_firms": len(data.tickers),
        "query_firms_in_support": sum(ticker in firms for ticker in data.tickers),
        "features": len(data.features),
    }


def _upper(matrix: FloatArray) -> FloatArray:
    return matrix[np.triu_indices(len(matrix), 1)]


def compare(reference: FloatArray, other: FloatArray) -> Record:
    """Embedding drift and distance/network agreement for the same ordered firms."""
    scale = float(np.linalg.norm(reference, axis=1).mean()) or 1.0
    record: Record = {
        "firms": len(reference),
        "max_relative_state_change": float(np.abs(other - reference).max() / scale),
    }
    if len(reference) >= 3:
        first, second = pairwise_distance(reference), pairwise_distance(other)
        record |= {
            "distance_spearman": float(spearmanr(_upper(first), _upper(second)).statistic),
            "max_distance_change": float(np.abs(first - second).max()),
            "max_weight_change": float(
                np.abs(normalize_weights(np.exp(-first)) - normalize_weights(np.exp(-second))).max()
            ),
        }
    return record


def _states(
    data: Prepared, model: str, cache: Path, source: Path, *, store: bool = False
) -> dict[str, FloatArray]:
    states = foundation_states(data, model, cache, source, store=store)
    load_tabfm.cache_clear()
    gc.collect()
    return states


def query_cohort_audit(data: Prepared, model: str, cache: Path, source: Path) -> list[Record]:
    """Re-encode seeded halves, reversed order and singletons with the same support."""
    full = _states(data, model, cache, source, store=True)
    rng = np.random.default_rng(42)
    order = rng.permutation(len(data.tickers))
    halves: dict[str, IntArray] = {
        "half_a": np.sort(order[: len(order) // 2]),
        "half_b": np.sort(order[len(order) // 2 :]),
    }
    variants: dict[str, IntArray] = {**halves, "reversed": np.arange(len(order))[::-1]}
    variants |= {f"singleton_{i}": order[[i]] for i in range(min(5, len(order)))}
    records: list[Record] = []
    for label, positions in variants.items():
        subset = variant(
            data,
            f"query:{label}",
            query=data.query[positions],
            tickers=tuple(data.tickers[i] for i in positions),
        )
        states = _states(subset, model, cache, source)
        for readout, name, arm in READOUTS[model]:
            records.append(
                {
                    "check": "query_cohort",
                    "variant": label,
                    "representation": name,
                    "arm": arm,
                    **compare(full[readout][positions], states[readout]),
                }
            )
    return records


def support_label_audit(data: Prepared, model: str, cache: Path, source: Path) -> list[Record]:
    """Shuffle or null the support labels, and redraw the support, holding queries fixed."""
    full = _states(data, model, cache, source, store=True)
    variants = {
        f"shuffled_{seed}": variant(
            data,
            f"labels:shuffled:{seed}",
            targets=np.random.default_rng(seed).permutation(data.targets),
        )
        for seed in (1, 2, 3)
    }
    # TabPFN returns before building its encoder when the target is constant, so it has
    # no null-label state to compare.
    if not model.startswith("tabpfn"):
        variants["null"] = variant(data, "labels:null", targets=np.zeros_like(data.targets))
    records: list[Record] = []
    for label, changed in variants.items():
        states = _states(changed, model, cache, source)
        records.extend(
            {
                "check": "support_labels",
                "variant": label,
                "representation": name,
                "arm": arm,
                **compare(full[readout], states[readout]),
            }
            for readout, name, arm in READOUTS[model]
        )
    return records


def target_audit(
    data: Prepared, alternate: Prepared, model: str, cache: Path, source: Path
) -> list[Record]:
    """Agreement between geometries conditioned on two declared support targets."""
    first = _states(data, model, cache, source, store=True)
    second = _states(alternate, model, cache, source, store=True)
    return [
        {
            "check": "support_target",
            "variant": "income_assets",
            "representation": name,
            "arm": arm,
            **compare(first[readout], second[readout]),
        }
        for readout, name, arm in READOUTS[model]
    ]
