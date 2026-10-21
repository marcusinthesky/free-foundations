"""Paper estimators against spreg reference implementations on no-intercept designs."""

import warnings

import numpy as np
import pytest
from libpysal.weights import full2W
from numpy.testing import assert_allclose
from scipy.stats import multivariate_normal
from spreg.ml_error import BaseML_Error
from spreg.ols import BaseOLS
from spreg.twosls import BaseTSLS

from free_foundations.contracts import FloatArray
from free_foundations.fernandez.models import (
    CrossSection,
    error_ml,
    lag_iv,
    ols,
    paper_weights,
    rank_distance,
    symmetric_spectrum,
)


def design(seed: int, intensity: float, *, lag: bool) -> tuple[FloatArray, FloatArray, FloatArray]:
    """A well-identified network and a single exposure, as in the second stage."""
    rng = np.random.default_rng(seed)
    firms = 80
    positions = rng.normal(size=(firms, 2))
    weights = paper_weights(4 * np.linalg.norm(positions[:, None] - positions[None], axis=-1))
    x = rng.uniform(0.5, 1.5, (firms, 1))
    operator = np.eye(firms) - intensity * weights
    shocks = rng.normal(0, 0.01, firms)
    mean = 0.02 * x[:, 0]
    y = (
        np.linalg.solve(operator, mean + shocks)
        if lag
        else mean + np.linalg.solve(operator, shocks)
    )
    return y, x, weights


def likelihood(fit: CrossSection) -> float:
    assert fit.log_likelihood is not None
    return fit.log_likelihood


@pytest.fixture(autouse=True)
def quiet() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)


def test_error_ml_matches_spreg_coefficients_likelihood_and_covariance() -> None:
    y, x, weights = design(7, 0.6, lag=False)
    ours = error_ml(y, x, weights)
    reference = BaseML_Error(y[:, None], x, full2W(weights))
    assert_allclose(ours.intensity, float(reference.lam), atol=1e-6)
    assert_allclose(ours.premiums, reference.betas[:-1, 0], rtol=1e-6)
    assert_allclose(likelihood(ours), float(reference.logll), rtol=1e-9)
    assert_allclose(ours.covariance, reference.vm, rtol=1e-5)


@pytest.mark.parametrize("self_links", [False, True])
def test_lag_iv_matches_spreg_two_stage_least_squares(*, self_links: bool) -> None:
    y, x, weights = design(3, 0.5, lag=True)
    if self_links:
        positions = np.random.default_rng(1).normal(size=(len(y), 2))
        weights = paper_weights(
            np.linalg.norm(positions[:, None] - positions[None], axis=-1), self_links=True
        )
    ours = lag_iv(y, x, weights)
    reference = BaseTSLS(y[:, None], x, yend=weights @ y[:, None], q=weights @ x)
    assert_allclose([*ours.premiums, ours.intensity], reference.betas[:, 0], rtol=1e-10)
    assert_allclose(ours.covariance, reference.vm, rtol=1e-8)


def test_ols_matches_spreg_and_spatial_models_nest_it_at_zero() -> None:
    y, x, weights = design(4, 0.3, lag=False)
    fit = ols(y, x)
    reference = BaseOLS(y[:, None], x)
    assert_allclose(fit.premiums, reference.betas[:, 0])
    assert_allclose(fit.covariance[:-1, :-1], reference.vm)
    # With no network the Jacobian vanishes and every lambda gives the OLS likelihood.
    nested = error_ml(y, x, np.zeros_like(weights), standard_errors=False)
    assert_allclose(likelihood(nested), likelihood(fit), rtol=1e-12)


def test_sem_likelihood_is_the_implied_gaussian_density() -> None:
    rng = np.random.default_rng(2)
    weights = paper_weights(rank_distance(rng.normal(size=(15, 10))))
    x = rng.uniform(0.5, 1.5, (15, 1))
    y = 0.03 * x[:, 0] + rng.normal(0, 0.01, 15)
    fit = error_ml(y, x, weights)
    inverse = np.linalg.inv(np.eye(15) - fit.intensity * weights)
    expected = multivariate_normal.logpdf(
        y, mean=x @ fit.premiums, cov=fit.variance * inverse @ inverse.T
    )
    assert_allclose(likelihood(fit), float(expected), rtol=1e-10)
    assert likelihood(fit) >= likelihood(ols(y, x)) - 1e-8


@pytest.mark.parametrize("self_links", [False, True])
def test_symmetric_spectrum_matches_general_eigenvalues(*, self_links: bool) -> None:
    rng = np.random.default_rng(8)
    weights = paper_weights(rank_distance(rng.normal(size=(20, 6))), self_links=self_links)
    general = np.sort(np.linalg.eigvals(weights).real)
    assert_allclose(np.sort(symmetric_spectrum(weights)), general, atol=1e-12)
    order = rng.permutation(20)
    assert_allclose(np.sort(symmetric_spectrum(weights[np.ix_(order, order)])), general, atol=1e-12)
