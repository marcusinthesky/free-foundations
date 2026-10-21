"""Fit the paper's second stage for one outcome, exposures and network; tabulate it."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import shapiro

from free_foundations.fernandez.diagnostics import (
    first_stage_f,
    information_criteria,
    pseudo_r2,
    residual_moran,
    z_statistics,
)
from free_foundations.fernandez.models import (
    error_ml,
    lag_iv,
    ols,
    symmetric_spectrum,
)

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.fernandez.models import CrossSection

type Row = dict[str, str | int | float | bool]


def summarize(fit: CrossSection, y: FloatArray, terms: tuple[str, ...]) -> Row:
    """Premiums, spatial coefficient, inference, conditional ICs and residual checks."""
    errors = fit.standard_errors
    z, p = z_statistics(np.append(fit.premiums, fit.intensity), errors)
    row: Row = {
        "estimator": fit.estimator,
        "firms": len(y),
        "intensity": fit.intensity,
        "intensity_se": float(errors[-1]),
        "intensity_p": float(p[-1]) if fit.estimator != "ols" else np.nan,
        "boundary": abs(fit.intensity) >= 0.985,
        "stable_unit_interval": abs(fit.intensity) < 1,
        "innovation_variance": fit.variance,
        "log_likelihood": np.nan if fit.log_likelihood is None else fit.log_likelihood,
        "parameters": np.nan if fit.parameters is None else fit.parameters,
        "pseudo_r2_structural": pseudo_r2(y, fit.fitted),
        "pseudo_r2_reduced": pseudo_r2(y, fit.reduced),
        "shapiro_p": float(shapiro(fit.innovations).pvalue),
    }
    for index, term in enumerate(terms):
        row |= {
            f"premium_{term}": float(fit.premiums[index]),
            f"se_{term}": float(errors[index]),
            f"z_{term}": float(z[index]),
            f"p_{term}": float(p[index]),
        }
    criteria = (
        information_criteria(fit.log_likelihood, fit.parameters, len(y))
        if fit.log_likelihood is not None and fit.parameters is not None
        else {"aic": np.nan, "bic": np.nan, "hqic": np.nan}
    )
    return row | criteria


def nonspatial(y: FloatArray, x: FloatArray, terms: tuple[str, ...]) -> Row:
    """The paper's least-squares benchmark with no network."""
    return {"network": "nonspatial", "kernel": "none", "self_links": False} | summarize(
        ols(y, x), y, terms
    )


def spatial(
    y: FloatArray,
    x: FloatArray,
    weights: FloatArray,
    terms: tuple[str, ...],
    *,
    estimators: tuple[str, ...] = ("spatial_lag_iv", "spatial_error_ml"),
) -> list[Row]:
    """S2SLS and SEM-ML on one network, with residual Moran from OLS."""
    spectrum = symmetric_spectrum(weights)
    moran = residual_moran(ols(y, x).innovations, x, weights)
    shared: Row = {
        "ols_moran": moran.statistic,
        "ols_moran_expectation": moran.expectation,
        "ols_moran_z": moran.z,
        "ols_moran_p": moran.p_value,
        "lag_first_stage_f": first_stage_f(y, x, weights),
    }
    fits = {
        "spatial_lag_iv": lambda: lag_iv(y, x, weights),
        "spatial_error_ml": lambda: error_ml(y, x, weights, eigenvalues=spectrum),
    }
    return [summarize(fits[name](), y, terms) | shared for name in estimators]
