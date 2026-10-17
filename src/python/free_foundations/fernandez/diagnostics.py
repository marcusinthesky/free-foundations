"""Residual Moran inference, conditional information criteria and fit summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import norm

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


@dataclass(frozen=True)
class Moran:
    """Moran's I for least-squares residuals, with exact normal-theory moments."""

    statistic: float
    expectation: float
    variance: float
    z: float
    p_value: float


def residual_moran(residuals: FloatArray, x: FloatArray, weights: FloatArray) -> Moran:
    """Equation (5) on uncentred residuals e = My, valid for any diagonal of W.

    Under normal errors, e'We / e'e is independent of e'e, giving
    E = (N/S0) tr(MW)/(N-k) and E[I^2] = (N/S0)^2 [tr(MWMW') + tr(MWMW) + tr(MW)^2]
    / ((N-k)(N-k+2)). The paper's printed mean has the wrong sign and assumes no
    regressors; Cliff-Ord residual moments replace it.
    """
    n, k = x.shape
    annihilator = np.eye(n) - x @ np.linalg.pinv(x)
    scale = n / weights.sum()
    product = annihilator @ weights
    trace = float(np.trace(product))
    expectation = scale * trace / (n - k)
    second = scale**2 * (
        float(np.sum(product * product.T))  # tr(MWMW)
        + float(np.sum(product * (annihilator @ weights.T).T))  # tr(MWMW')
        + trace**2
    )
    variance = second / ((n - k) * (n - k + 2)) - expectation**2
    statistic = scale * float(residuals @ weights @ residuals / (residuals @ residuals))
    z = (statistic - expectation) / np.sqrt(variance)
    return Moran(statistic, expectation, variance, float(z), float(2 * norm.sf(abs(z))))


def information_criteria(
    log_likelihood: float, parameters: int, observations: int
) -> dict[str, float]:
    """AIC, BIC and HQIC conditional on generated betas and W; n is the number of firms."""
    return {
        "aic": -2 * log_likelihood + 2 * parameters,
        "bic": -2 * log_likelihood + parameters * np.log(observations),
        "hqic": -2 * log_likelihood + 2 * parameters * np.log(np.log(observations)),
    }


def pseudo_r2(y: FloatArray, fitted: FloatArray) -> float:
    """The paper's goodness of fit: squared correlation of actual and fitted values."""
    return float(np.corrcoef(y, fitted)[0, 1] ** 2)


def z_statistics(
    estimates: FloatArray, standard_errors: FloatArray
) -> tuple[FloatArray, FloatArray]:
    """Asymptotic z-statistics and two-sided normal p-values."""
    values = np.asarray(estimates, dtype=float)
    errors = np.asarray(standard_errors, dtype=float)
    z = np.divide(values, errors, out=np.full_like(values, np.nan), where=errors > 0)
    return z, 2 * norm.sf(np.abs(z))


def first_stage_f(y: FloatArray, x: FloatArray, weights: FloatArray) -> float:
    """F statistic for the excluded instruments WX when explaining Wy given X."""
    endogenous = weights @ y
    instruments = np.column_stack([x, weights @ x])
    restricted = endogenous - x @ np.linalg.lstsq(x, endogenous, rcond=None)[0]
    unrestricted = (
        endogenous - instruments @ np.linalg.lstsq(instruments, endogenous, rcond=None)[0]
    )
    restricted_ss, unrestricted_ss = (
        float(restricted @ restricted),
        float(unrestricted @ unrestricted),
    )
    excluded, freedom = x.shape[1], len(y) - instruments.shape[1]
    return (restricted_ss - unrestricted_ss) / excluded / (unrestricted_ss / freedom)
