"""Pairwise correlations on each pair's own observed dates, and their chord distances."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import rankdata

if TYPE_CHECKING:
    from collections.abc import Callable

    import pandas as pd

    from free_foundations.encoders.contracts import BoolArray, FloatArray


@dataclass(frozen=True)
class PairwiseCorrelation:
    """Correlations with a unit diagonal; undefined pairs are zero and flagged.

    ``defined`` marks pairs with at least two common observations and positive
    variance in both histories. ``distance`` is the chord ``sqrt(2(1 - r))``, so an
    undefined pair sits at the neutral distance ``sqrt(2)``.
    """

    correlation: FloatArray
    counts: np.ndarray
    defined: BoolArray

    @property
    def distance(self) -> FloatArray:
        """Chord distance on the unit sphere of standardized (ranked) histories."""
        distance = np.sqrt(np.maximum(2 * (1 - np.clip(self.correlation, -1, 1)), 0))
        np.fill_diagonal(distance, 0.0)
        return distance

    @property
    def neutral_pairs(self) -> int:
        """Off-diagonal pairs without a defined correlation."""
        off = ~np.eye(len(self.defined), dtype=bool)
        return int(np.count_nonzero(off & ~self.defined) // 2)


def _values(values: pd.DataFrame | FloatArray) -> FloatArray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 2 or np.isinf(result).any():
        message = "Pairwise moments require a two-dimensional array without infinity."
        raise ValueError(message)
    return result


def _pairwise(
    entities: FloatArray, transform: Callable[[FloatArray], FloatArray]
) -> PairwiseCorrelation:
    """Correlate every pair on its own intersection (rows are entities).

    Rows sharing a missingness pattern are processed together, so the work grows
    with the number of distinct patterns rather than with every pair.
    """
    finite = np.isfinite(entities)
    counts = finite.astype(np.int64) @ finite.astype(np.int64).T
    correlation = np.zeros((len(entities), len(entities)), dtype=float)
    defined = np.zeros_like(correlation, dtype=bool)
    patterns, labels = np.unique(finite, axis=0, return_inverse=True)
    groups = [np.flatnonzero(labels == label) for label in range(len(patterns))]
    for left, left_rows in enumerate(groups):
        for right in range(left, len(groups)):
            right_rows = groups[right]
            overlap = patterns[left] & patterns[right]
            if np.count_nonzero(overlap) < 2:
                continue
            a = transform(entities[np.ix_(left_rows, overlap)])
            b = transform(entities[np.ix_(right_rows, overlap)])
            a -= a.mean(axis=1, keepdims=True)
            b -= b.mean(axis=1, keepdims=True)
            scale = np.outer(np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1))
            valid = scale > 0
            product = np.divide(a @ b.T, scale, out=np.zeros_like(scale), where=valid)
            correlation[np.ix_(left_rows, right_rows)] = product
            correlation[np.ix_(right_rows, left_rows)] = product.T
            defined[np.ix_(left_rows, right_rows)] = valid
            defined[np.ix_(right_rows, left_rows)] = valid.T
    correlation = np.clip((correlation + correlation.T) / 2, -1, 1)
    np.fill_diagonal(correlation, 1.0)
    return PairwiseCorrelation(correlation, counts, defined)


def pairwise_spearman(histories: pd.DataFrame | FloatArray) -> PairwiseCorrelation:
    """Spearman correlations reranked on each pair's common dates (rows are entities)."""
    return _pairwise(_values(histories), lambda block: rankdata(block, axis=1, method="average"))


def pairwise_pearson(returns: pd.DataFrame | FloatArray) -> PairwiseCorrelation:
    """Pearson correlations of returns on each pair's common dates (rows are periods)."""
    return _pairwise(_values(returns).T, lambda block: np.array(block, dtype=float))
