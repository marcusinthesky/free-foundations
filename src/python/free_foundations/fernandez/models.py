"""Paper equations (2), (4), (8) and (9), with explicit numerical conventions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import rankdata

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


@dataclass(frozen=True)
class CrossSection:
    """Cross-sectional premium, spatial coefficient and fitted observations."""

    premium: float
    intensity: float
    fitted: FloatArray
    innovations: FloatArray


def rank_distance(histories: FloatArray) -> FloatArray:
    """Equation (9); constant or incomplete histories have undefined correlations."""
    if not np.isfinite(histories).all():
        message = "Fernández histories must be complete."
        raise ValueError(message)
    ranks = rankdata(histories, axis=1)
    centered = ranks - ranks.mean(axis=1, keepdims=True)
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    if (norms == 0).any():
        message = "Constant histories have undefined Spearman correlation."
        raise ValueError(message)
    normalized = centered / norms
    distances = np.sqrt(np.maximum(2 * (1 - np.clip(normalized @ normalized.T, -1, 1)), 0))
    np.fill_diagonal(distances, 0)
    return distances


def paper_weights(distance: FloatArray, *, self_links: bool = False) -> FloatArray:
    """Equation (10), zero diagonal by convention; expose its literal diagonal variant."""
    affinity = np.exp(-distance)
    if not self_links:
        np.fill_diagonal(affinity, 0)
    return affinity / affinity.sum(axis=1, keepdims=True)


def lag_iv(y: FloatArray, x: FloatArray, weights: FloatArray) -> CrossSection:
    """Equation (2), instruments [WX, X], no unmentioned W-squared instruments."""
    design = np.column_stack([weights @ y, x])
    instruments = np.column_stack([weights @ x, x])
    projected = instruments @ np.linalg.lstsq(instruments, design, rcond=None)[0]
    if np.linalg.matrix_rank(projected) != design.shape[1]:
        message = "Spatial lag instruments do not identify the coefficients."
        raise ValueError(message)
    coefficients = np.linalg.lstsq(projected, y, rcond=None)[0]
    fitted = design @ coefficients
    return CrossSection(float(coefficients[-1]), float(coefficients[0]), fitted, y - fitted)


def error_ml(y: FloatArray, x: FloatArray, weights: FloatArray) -> CrossSection:
    """Equation (4): profile beta and spherical innovation variance at each lambda."""
    identity = np.eye(len(y))

    def objective(intensity: float) -> float:
        operator = identity - intensity * weights
        transformed_y, transformed_x = operator @ y, operator @ x
        beta = np.linalg.lstsq(transformed_x, transformed_y, rcond=None)[0]
        innovations = transformed_y - transformed_x @ beta
        return float(len(y) * np.log(np.mean(innovations**2)) - 2 * np.linalg.slogdet(operator)[1])

    result = minimize_scalar(objective, bounds=(-0.99, 0.99), method="bounded")
    if not result.success:
        message = "Spatial-error maximum likelihood failed."
        raise RuntimeError(message)
    operator = identity - float(result.x) * weights
    beta = np.linalg.lstsq(operator @ x, operator @ y, rcond=None)[0]
    mean = x @ beta
    residual = y - mean
    fitted = mean + float(result.x) * weights @ residual
    return CrossSection(float(beta[-1]), float(result.x), fitted, operator @ residual)


def residual_covariance(residuals: FloatArray, weights: FloatArray) -> tuple[FloatArray, float]:
    """Pooled Gaussian SEM with spherical innovations, in original return units."""
    identity = np.eye(weights.shape[0])
    weighted = residuals @ weights.T
    second, cross, spatial = (
        np.mean(residuals**2),
        np.mean(residuals * weighted),
        np.mean(weighted**2),
    )

    def objective(intensity: float) -> float:
        variance = second - 2 * intensity * cross + intensity**2 * spatial
        return float(
            weights.shape[0] * np.log(variance)
            - 2 * np.linalg.slogdet(identity - intensity * weights)[1]
        )

    result = minimize_scalar(objective, bounds=(-0.99, 0.99), method="bounded")
    if not result.success:
        message = "Pooled spatial-error maximum likelihood failed."
        raise RuntimeError(message)
    intensity = float(result.x)
    variance = second - 2 * intensity * cross + intensity**2 * spatial
    inverse = np.linalg.solve(identity - intensity * weights, identity)
    return variance * inverse @ inverse.T, intensity
