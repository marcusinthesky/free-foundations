"""Pairwise observed-data moments and separately recorded correlation regularization."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import rankdata

if TYPE_CHECKING:
    import pandas as pd

    from free_foundations.contracts import BoolArray, FloatArray


@dataclass(frozen=True)
class PairwiseMoments:
    """Keep the original pairwise network distinct from its positive-definite Gram.

    ``raw`` has zero undefined off-diagonal correlations and a unit diagonal.
    ``defined`` records which entries were actually estimable, including the diagonal.
    ``distance`` and ``weights`` use this original completion. ``correlation`` and
    ``gram_distance`` use the separately recorded identity shrinkage ``delta``.
    Pairwise sample covariances use zero where fewer than two observations overlap;
    ``covariance_defined`` distinguishes that convention from an estimated zero.
    """

    raw: FloatArray
    correlation: FloatArray
    counts: np.ndarray
    defined: BoolArray
    delta: float
    distance: FloatArray
    gram_distance: FloatArray
    weights: FloatArray
    covariance: FloatArray | None = None
    covariance_defined: BoolArray | None = None


def _values(values: pd.DataFrame | FloatArray) -> FloatArray:
    result = np.asarray(values, dtype=np.float64)
    if result.ndim != 2 or np.isinf(result).any():
        message = "Pairwise moments require a two-dimensional array without infinity."
        raise ValueError(message)
    return result


def identity_shrink(
    correlation: FloatArray, min_eigenvalue: float = 1e-6
) -> tuple[FloatArray, float]:
    """Find identity shrinkage giving the prescribed positive eigenvalue floor.

    The raw matrix is never repaired in place. A small rounding guard makes the
    reported floor conservative under floating-point eigendecomposition.
    """
    value = np.asarray(correlation, dtype=np.float64)
    if not 0 < min_eigenvalue < 1:
        message = "The minimum eigenvalue must lie strictly between zero and one."
        raise ValueError(message)
    if (
        value.ndim != 2
        or value.shape[0] != value.shape[1]
        or not np.isfinite(value).all()
        or not np.allclose(value, value.T, atol=1e-12, rtol=0)
        or not np.allclose(np.diag(value), 1, atol=1e-12, rtol=0)
        or np.any(np.abs(value) > 1 + 1e-12)
    ):
        message = "Identity shrinkage requires a finite symmetric unit-diagonal correlation."
        raise ValueError(message)
    size = len(value)
    if size == 0:
        return value.copy(), 0.0
    minimum = float(np.linalg.eigvalsh(value)[0])
    if minimum >= min_eigenvalue:
        return value.copy(), 0.0
    guard = 32 * np.finfo(float).eps * size
    target = min(1.0, min_eigenvalue + guard)
    delta = float(np.clip((target - minimum) / (1 - minimum), 0, 1))
    result = (1 - delta) * value + delta * np.eye(size)
    np.fill_diagonal(result, 1.0)
    return result, delta


def exponential_weights(distance: FloatArray) -> FloatArray:
    """Original zero-self-link exp(-distance), normalized separately in each row.

    A singleton has no neighbours and therefore a zero row. Subtracting each row's
    minimum is algebraically neutral and prevents exponential underflow.
    """
    value = np.asarray(distance, dtype=np.float64)
    if (
        value.ndim != 2
        or value.shape[0] != value.shape[1]
        or not np.isfinite(value).all()
        or np.any(value < 0)
        or not np.allclose(np.diag(value), 0, atol=1e-12, rtol=0)
    ):
        message = "Network distances must be finite, square, nonnegative and zero-diagonal."
        raise ValueError(message)
    if len(value) < 2:
        return np.zeros_like(value)
    shifted = value.copy()
    np.fill_diagonal(shifted, np.inf)
    shifted -= shifted.min(axis=1, keepdims=True)
    weights = np.exp(-shifted)
    return weights / weights.sum(axis=1, keepdims=True)


def _distance(correlation: FloatArray) -> FloatArray:
    distance = np.sqrt(np.maximum(2 * (1 - np.clip(correlation, -1, 1)), 0))
    np.fill_diagonal(distance, 0.0)
    return distance


def _result(  # noqa: PLR0913 -- geometry and optional sample-covariance availability.
    raw: FloatArray,
    counts: np.ndarray,
    defined: BoolArray,
    min_eigenvalue: float,
    *,
    covariance: FloatArray | None = None,
    covariance_defined: BoolArray | None = None,
) -> PairwiseMoments:
    raw = np.clip((raw + raw.T) / 2, -1, 1)
    np.fill_diagonal(raw, 1.0)
    correlation, delta = identity_shrink(raw, min_eigenvalue)
    distance = _distance(raw)
    return PairwiseMoments(
        raw=raw,
        correlation=correlation,
        counts=counts,
        defined=defined,
        delta=delta,
        distance=distance,
        gram_distance=_distance(correlation),
        weights=exponential_weights(distance),
        covariance=covariance,
        covariance_defined=covariance_defined,
    )


def pairwise_spearman(
    histories: pd.DataFrame | FloatArray, min_eigenvalue: float = 1e-6
) -> PairwiseMoments:
    """Rerank each pair on its own observed history intersection (entities by dates).

    At least two common observations and positive rank variance in both histories
    are required. Missing and constant histories never remove an entity. Grouping
    equal missingness patterns avoids ranking every complete pair individually.
    """
    values = _values(histories)
    finite = np.isfinite(values)
    counts = finite.astype(np.int64) @ finite.astype(np.int64).T
    raw = np.zeros((len(values), len(values)), dtype=float)
    defined = np.zeros_like(raw, dtype=bool)
    patterns, labels = np.unique(finite, axis=0, return_inverse=True)
    groups = [np.flatnonzero(labels == label) for label in range(len(patterns))]
    for left, left_rows in enumerate(groups):
        for right in range(left, len(groups)):
            right_rows = groups[right]
            overlap = patterns[left] & patterns[right]
            if np.count_nonzero(overlap) < 2:
                continue
            a = rankdata(values[np.ix_(left_rows, overlap)], axis=1, method="average")
            b = rankdata(values[np.ix_(right_rows, overlap)], axis=1, method="average")
            a -= a.mean(axis=1, keepdims=True)
            b -= b.mean(axis=1, keepdims=True)
            scale = np.outer(np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1))
            valid = scale > 0
            product = np.divide(a @ b.T, scale, out=np.zeros_like(scale), where=valid)
            raw[np.ix_(left_rows, right_rows)] = product
            raw[np.ix_(right_rows, left_rows)] = product.T
            defined[np.ix_(left_rows, right_rows)] = valid
            defined[np.ix_(right_rows, left_rows)] = valid.T
    return _result(raw, counts, defined, min_eigenvalue)


def pairwise_covariance(
    returns: pd.DataFrame | FloatArray, min_eigenvalue: float = 1e-6
) -> PairwiseMoments:
    """Sample covariance and Pearson correlation on each pair's own intersection.

    Rows are periods and columns entities. Each covariance subtracts the two
    means on that intersection and divides by n-1. Correlations additionally
    require positive pair-specific variances. No common complete-case cut occurs.
    """
    values = _values(returns).T
    finite = np.isfinite(values)
    counts = finite.astype(np.int64) @ finite.astype(np.int64).T
    covariance_defined = counts >= 2
    raw = np.zeros((len(values), len(values)), dtype=float)
    covariance = np.zeros_like(raw)
    defined = np.zeros_like(raw, dtype=bool)
    patterns, labels = np.unique(finite, axis=0, return_inverse=True)
    groups = [np.flatnonzero(labels == label) for label in range(len(patterns))]
    for left, left_rows in enumerate(groups):
        for right in range(left, len(groups)):
            right_rows = groups[right]
            overlap = patterns[left] & patterns[right]
            count = int(np.count_nonzero(overlap))
            if count < 2:
                continue
            a = values[np.ix_(left_rows, overlap)]
            b = values[np.ix_(right_rows, overlap)]
            varying_a = np.ptp(a, axis=1) > 0
            varying_b = np.ptp(b, axis=1) > 0
            a = a - a.mean(axis=1, keepdims=True)
            b = b - b.mean(axis=1, keepdims=True)
            a[~varying_a] = 0
            b[~varying_b] = 0
            cross = a @ b.T
            scale = np.outer(np.linalg.norm(a, axis=1), np.linalg.norm(b, axis=1))
            valid = np.outer(varying_a, varying_b) & (scale > 0)
            product = np.divide(cross, scale, out=np.zeros_like(scale), where=valid)
            raw[np.ix_(left_rows, right_rows)] = product
            raw[np.ix_(right_rows, left_rows)] = product.T
            covariance[np.ix_(left_rows, right_rows)] = cross / (count - 1)
            covariance[np.ix_(right_rows, left_rows)] = cross.T / (count - 1)
            defined[np.ix_(left_rows, right_rows)] = valid
            defined[np.ix_(right_rows, left_rows)] = valid.T
    return _result(
        raw,
        counts,
        defined,
        min_eigenvalue,
        covariance=(covariance + covariance.T) / 2,
        covariance_defined=covariance_defined,
    )
