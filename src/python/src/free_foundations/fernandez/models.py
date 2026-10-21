"""Paper equations (2), (4), (9) and (10), with explicit numerical conventions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import rankdata

if TYPE_CHECKING:
    from collections.abc import Callable

    from free_foundations.contracts import FloatArray

BOUNDS = (-0.99, 0.99)


@dataclass(frozen=True)
class CrossSection:
    """One fitted cross-section: premiums, spatial coefficient and their covariance.

    ``covariance`` orders the premiums first and the spatial coefficient last; that row
    and column are zero for OLS. ``fitted`` is structural, so it uses realized ``Wy`` for
    the lag model; ``reduced`` is the corresponding reduced-form mean. Likelihood and
    parameter counts are absent for two-stage least squares, which maximizes no likelihood.
    """

    estimator: str
    premiums: FloatArray
    intensity: float
    covariance: FloatArray
    variance: float
    log_likelihood: float | None
    parameters: int | None
    fitted: FloatArray
    reduced: FloatArray
    innovations: FloatArray

    @property
    def premium(self) -> float:
        """Market premium: the first regressor is always the market exposure."""
        return float(self.premiums[0])

    @property
    def standard_errors(self) -> FloatArray:
        """Square roots of the covariance diagonal, premiums then spatial coefficient."""
        return np.sqrt(np.maximum(np.diag(self.covariance), 0))


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


def symmetric_spectrum(weights: FloatArray) -> FloatArray:
    """Eigenvalues of W = D^-1 A for a symmetric nonnegative affinity A.

    W is similar to D^-1/2 A D^-1/2, whose entries equal sqrt(W_ij W_ji). Every network
    here is a row-normalized symmetric kernel (with or without self-links), a uniform
    network or zero, so its spectrum is real; label permutations PWP' share it.
    """
    return np.asarray(np.linalg.eigvalsh(np.sqrt(weights * weights.T)), dtype=np.float64)


def maximize_profile(
    objective: Callable[[float], float],
    bounds: tuple[float, float] = BOUNDS,
    points: int = 201,
    xatol: float | None = None,
) -> tuple[float, float]:
    """Grid search, then bounded refinement between the best grid neighbours."""
    grid = np.linspace(bounds[0], bounds[1], points)
    values = np.array([objective(float(point)) for point in grid])
    best = int(np.argmax(values))

    def negative(value: float) -> float:
        return -objective(float(value))

    interval = (float(grid[max(0, best - 1)]), float(grid[min(len(grid) - 1, best + 1)]))
    result = (
        minimize_scalar(negative, bounds=interval, method="bounded")
        if xatol is None
        else minimize_scalar(negative, bounds=interval, method="bounded", options={"xatol": xatol})
    )
    if not result.success:
        message = "Spatial profile likelihood optimization failed."
        raise RuntimeError(message)
    return float(result.x), -float(result.fun)


def _jacobian(intensity: float, eigenvalues: FloatArray) -> float:
    return float(np.log(np.abs(1 - intensity * eigenvalues)).sum())


def _gaussian(innovations: FloatArray) -> tuple[float, float]:
    variance = float(innovations @ innovations / len(innovations))
    return variance, -len(innovations) / 2 * (np.log(2 * np.pi * variance) + 1)


def ols(y: FloatArray, x: FloatArray) -> CrossSection:
    """No-intercept least squares; s^2 uses N-k for SEs and e'e/N for the likelihood."""
    coefficients = np.linalg.lstsq(x, y, rcond=None)[0]
    fitted = x @ coefficients
    residuals = y - fitted
    variance, log_likelihood = _gaussian(residuals)
    scale = residuals @ residuals / (len(y) - x.shape[1])
    covariance = np.zeros((x.shape[1] + 1, x.shape[1] + 1))
    covariance[:-1, :-1] = scale * np.linalg.inv(x.T @ x)
    return CrossSection(
        estimator="ols",
        premiums=coefficients,
        intensity=0.0,
        covariance=covariance,
        variance=variance,
        log_likelihood=log_likelihood,
        parameters=x.shape[1] + 1,
        fitted=fitted,
        reduced=fitted,
        innovations=residuals,
    )


def lag_iv(y: FloatArray, x: FloatArray, weights: FloatArray) -> CrossSection:
    """Equation (2): instruments [WX, X], no unmentioned W-squared instruments, s2=e'e/N."""
    design = np.column_stack([weights @ y, x])
    instruments = np.column_stack([weights @ x, x])
    projected = instruments @ np.linalg.lstsq(instruments, design, rcond=None)[0]
    if np.linalg.matrix_rank(projected) != design.shape[1]:
        message = "Spatial lag instruments do not identify the coefficients."
        raise ValueError(message)
    coefficients = np.linalg.lstsq(projected, y, rcond=None)[0]
    fitted = design @ coefficients
    innovations = y - fitted
    variance = float(innovations @ innovations / len(y))
    inverse = variance * np.linalg.inv(projected.T @ design)
    order = [*range(1, design.shape[1]), 0]
    reduced = np.linalg.solve(np.eye(len(y)) - coefficients[0] * weights, x @ coefficients[1:])
    return CrossSection(
        estimator="spatial_lag_iv",
        premiums=coefficients[1:],
        intensity=float(coefficients[0]),
        covariance=inverse[np.ix_(order, order)],
        variance=variance,
        log_likelihood=None,
        parameters=None,
        fitted=fitted,
        reduced=reduced,
        innovations=innovations,
    )


def _information_traces(
    weights: FloatArray, intensity: float, eigenvalues: FloatArray
) -> tuple[float, float, float]:
    """tr(WA^-1), tr((WA^-1)^2) and tr((WA^-1)'WA^-1) for A = I - intensity W."""
    ratio = eigenvalues / (1 - intensity * eigenvalues)
    product = weights @ np.linalg.inv(np.eye(len(weights)) - intensity * weights)
    return float(ratio.sum()), float((ratio**2).sum()), float(np.sum(product**2))


def error_ml(  # noqa: PLR0913 -- keyword-only numerical options.
    y: FloatArray,
    x: FloatArray,
    weights: FloatArray,
    *,
    eigenvalues: FloatArray | None = None,
    xatol: float | None = 1e-9,
    standard_errors: bool = True,
) -> CrossSection:
    """Equation (4): profile premiums and spherical variance; information-matrix SEs.

    ``standard_errors=False`` skips the O(N^3) information matrix for resampling refits.
    """
    spectrum = symmetric_spectrum(weights) if eigenvalues is None else eigenvalues
    lagged_y, lagged_x = weights @ y, weights @ x

    def fit(intensity: float) -> tuple[FloatArray, FloatArray]:
        filtered_x = x - intensity * lagged_x
        filtered_y = y - intensity * lagged_y
        coefficients = np.linalg.lstsq(filtered_x, filtered_y, rcond=None)[0]
        return coefficients, filtered_y - filtered_x @ coefficients

    def profile(intensity: float) -> float:
        return _jacobian(intensity, spectrum) + _gaussian(fit(intensity)[1])[1]

    intensity, log_likelihood = maximize_profile(profile, xatol=xatol)
    coefficients, innovations = fit(intensity)
    variance = _gaussian(innovations)[0]
    filtered_x = x - intensity * lagged_x
    covariance = np.full((x.shape[1] + 1, x.shape[1] + 1), np.nan)
    if standard_errors:
        trace, square, cross = _information_traces(weights, intensity, spectrum)
        information = np.array(
            [[square + cross, trace / variance], [trace / variance, len(y) / (2 * variance**2)]]
        )
        covariance = np.zeros((x.shape[1] + 1, x.shape[1] + 1))
        covariance[:-1, :-1] = variance * np.linalg.inv(filtered_x.T @ filtered_x)
        covariance[-1, -1] = np.linalg.inv(information)[0, 0]
    mean = x @ coefficients
    return CrossSection(
        estimator="spatial_error_ml",
        premiums=coefficients,
        intensity=intensity,
        covariance=covariance,
        variance=variance,
        log_likelihood=log_likelihood,
        parameters=x.shape[1] + 2,
        fitted=mean + intensity * weights @ (y - mean),
        reduced=mean,
        innovations=innovations,
    )
