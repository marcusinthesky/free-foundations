"""Factor exposures, covariance estimators and portfolio scores."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

from free_foundations.methods import spatial_ml

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray


def factor_loadings(
    returns: FloatArray, factors: FloatArray
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Time-series OLS with an intercept: loadings (N x K), intercepts and residuals (T x N)."""
    design = np.column_stack([np.ones(len(factors)), factors])
    coefficients = np.linalg.lstsq(design, returns, rcond=None)[0]
    residuals = returns - design @ coefficients
    return coefficients[1:].T, coefficients[0], residuals


def symmetric_root(matrix: FloatArray) -> FloatArray:
    """Principal square root of a symmetric positive-semidefinite matrix."""
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
    return (vectors * np.sqrt(np.clip(values, 0, None))) @ vectors.T


@dataclass(frozen=True)
class Covariance:
    """A fitted training-window covariance and its estimation evidence."""

    name: str
    matrix: FloatArray
    spatial: float = float("nan")
    train_loglik: float = float("nan")


def factor_covariance(
    name: str, loadings: FloatArray, factor_cov: FloatArray, residuals: FloatArray
) -> Covariance:
    """``B Omega B' + diag(residual variances)``."""
    common = loadings @ factor_cov @ loadings.T
    return Covariance(name, common + np.diag(residuals.var(axis=0)))


def spatial_residual_fit(
    residuals: FloatArray, weights: FloatArray
) -> tuple[float, FloatArray, float]:
    """Gaussian ML of ``e_t = (I - lambda W)^-1 eps_t`` with ``eps_t ~ N(0, diag(d))``.

    Profiling out ``d_i = mean_t eps_it^2`` leaves
    ``T log|det(I - lambda W)| - T/2 sum_i log d_i(lambda)`` up to a constant.
    """
    graph = spatial_ml.Graph.of(weights)
    periods = len(residuals)
    lagged = residuals @ weights.T

    def loglik(value: float) -> float:
        innovations = residuals - value * lagged
        variance = np.mean(innovations**2, axis=0)
        logdet = float(np.log(np.abs(1 - value * graph.spectrum)).sum())
        return periods * logdet - periods / 2 * float(np.log(variance).sum())

    low, high = graph.interval
    grid = np.linspace(low, high, 81)
    values = np.array([loglik(float(point)) for point in grid])
    best = int(np.argmax(values))
    bracket = (float(grid[max(best - 1, 0)]), float(grid[min(best + 1, len(grid) - 1)]))
    result = minimize_scalar(
        lambda value: -loglik(float(value)),
        bounds=bracket,
        method="bounded",
        options={"xatol": 1e-9},
    )
    value = float(result.x)
    variance = np.mean((residuals - value * lagged) ** 2, axis=0)
    return value, variance, loglik(value)


def spatial_covariance(
    name: str,
    loadings: FloatArray,
    factor_cov: FloatArray,
    residuals: FloatArray,
    weights: FloatArray,
) -> Covariance:
    """``B Omega B' + P D P'`` with the training-window spatial fit."""
    value, variance, loglik = spatial_residual_fit(residuals, weights)
    inverse = np.linalg.inv(np.eye(len(weights)) - value * weights)
    residual = (inverse * variance) @ inverse.T
    common = loadings @ factor_cov @ loadings.T
    return Covariance(name, common + residual, value, loglik)


def monthly_scores(covariance: FloatArray, returns: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Per-month mean Gaussian negative log score and GMV realized return.

    Each month uses only its observed issuers: the score is the marginal Gaussian
    density on that subset, divided by its size, and the minimum-variance weights are
    computed from the same sub-covariance. Months without two observed issuers are NaN.
    """
    scores = np.full(len(returns), np.nan)
    portfolio = np.full(len(returns), np.nan)
    for month, row in enumerate(returns):
        observed = np.isfinite(row)
        if observed.sum() < 2:
            continue
        sub = covariance[np.ix_(observed, observed)]
        factor = np.linalg.cholesky(sub)
        values = row[observed]
        whitened = np.linalg.solve(factor, values)
        logdet = 2 * np.log(np.diag(factor)).sum()
        scores[month] = 0.5 * (logdet + whitened @ whitened + observed.sum() * np.log(2 * np.pi))
        scores[month] /= observed.sum()
        ones = np.linalg.solve(factor.T, np.linalg.solve(factor, np.ones(observed.sum())))
        portfolio[month] = float(ones @ values / ones.sum())
    return scores, portfolio
