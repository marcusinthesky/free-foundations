"""Small spatial-error estimators and strictly held-out dependence scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.spatial.distance import cdist
from scipy.stats import rankdata

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


@dataclass(frozen=True)
class SpatialFit:
    """Gaussian spatial-error fit on standardized training residuals."""

    intensity: float
    covariance: FloatArray


def normalize_weights(affinity: FloatArray) -> FloatArray:
    """Zero self-links and normalize each row; reject isolated or invalid rows."""
    weights = np.array(affinity, dtype=np.float64, copy=True)
    np.fill_diagonal(weights, 0)
    if not np.isfinite(weights).all() or (weights < 0).any() or (weights.sum(axis=1) <= 0).any():
        message = "Weights must be finite, nonnegative, and have a neighbor in every row."
        raise ValueError(message)
    return weights / weights.sum(axis=1, keepdims=True)


def kernel_weights(vectors: FloatArray) -> FloatArray:
    """Use exp(-squared distance / median positive distance), without tuning on returns."""
    distance = cdist(vectors, vectors, metric="sqeuclidean")
    positive = distance[distance > 0]
    bandwidth = float(np.median(positive)) if positive.size else 1.0
    # A row-wise offset cancels on normalization and prevents isolated rows
    # caused only by exponential underflow for distant observations.
    np.fill_diagonal(distance, np.inf)
    distance -= distance.min(axis=1, keepdims=True)
    return normalize_weights(np.exp(-distance / bandwidth))


def history_weights(histories: FloatArray) -> FloatArray:
    """Fernández-inspired exp(-sqrt(2(1-Spearman))) on four annual asset states."""
    ranks = rankdata(histories, axis=1)
    ranks -= ranks.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(ranks, axis=1, keepdims=True)
    ranks = np.divide(ranks, norms, out=np.zeros_like(ranks), where=norms > 0)
    correlation = np.clip(ranks @ ranks.T, -1, 1)
    return normalize_weights(np.exp(-np.sqrt(2 * (1 - correlation))))


def fit_spatial(weights: FloatArray, residuals: FloatArray) -> SpatialFit:
    """Profile Gaussian likelihood over lambda in [-0.8, 0.8], with diagonal innovations."""
    identity = np.eye(weights.shape[0])
    weighted = residuals @ weights.T
    second = np.mean(residuals**2, axis=0)
    cross = np.mean(residuals * weighted, axis=0)
    spatial_second = np.mean(weighted**2, axis=0)

    def objective(intensity: float) -> float:
        operator = identity - intensity * weights
        variances = np.maximum(
            second - 2 * intensity * cross + intensity**2 * spatial_second, 1e-10
        )
        _, logdet = np.linalg.slogdet(operator)
        return float(np.log(variances).sum() - 2 * logdet)

    result = minimize_scalar(objective, bounds=(-0.8, 0.8), method="bounded")
    if not result.success:
        message = "Spatial profile likelihood optimization failed."
        raise RuntimeError(message)
    intensity = float(result.x)
    operator = identity - intensity * weights
    variances = np.maximum(np.mean((residuals @ operator.T) ** 2, axis=0), 1e-10)
    inverse = np.linalg.solve(operator, identity)
    return SpatialFit(intensity, (inverse * variances) @ inverse.T)


def daily_scores(residuals: FloatArray, covariance: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Per-firm Gaussian loss and daily unconstrained GMV realized squared return."""
    sign, logdet = np.linalg.slogdet(covariance)
    if sign <= 0:
        message = "Forecast covariance must be positive definite."
        raise ValueError(message)
    precision = np.linalg.solve(covariance, np.eye(len(covariance)))
    loss = (logdet + np.einsum("ti,ij,tj->t", residuals, precision, residuals)) / len(covariance)
    portfolio = precision.sum(axis=1) / precision.sum()
    return loss, (residuals @ portfolio) ** 2


def moran(residuals: FloatArray, weights: FloatArray) -> FloatArray:
    """Daily Moran I, centering each cross-section; W has row sums one."""
    centered = residuals - residuals.mean(axis=1, keepdims=True)
    return np.einsum("ti,ij,tj->t", centered, weights, centered) / np.sum(centered**2, axis=1)
