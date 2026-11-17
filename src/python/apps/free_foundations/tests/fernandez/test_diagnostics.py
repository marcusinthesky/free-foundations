"""Residual Moran moments and conditional information criteria."""

import warnings

import numpy as np
import pytest
from libpysal.weights import full2W
from numpy.testing import assert_allclose
from spreg.diagnostics_sp import MoranRes
from spreg.ols import BaseOLS

from free_foundations.fernandez.diagnostics import information_criteria, residual_moran
from free_foundations.fernandez.models import error_ml, lag_iv, ols, paper_weights, rank_distance


def network(seed: int, *, self_links: bool = False) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return paper_weights(rank_distance(rng.normal(size=(30, 8))) * 3, self_links=self_links)


def test_exact_moments_match_spreg_for_zero_diagonal() -> None:
    warnings.filterwarnings("ignore")
    rng = np.random.default_rng(1)
    weights = network(1)
    x = rng.uniform(0.5, 1.5, (30, 1))
    y = 0.02 * x[:, 0] + rng.normal(0, 0.01, 30)
    ours = residual_moran(ols(y, x).innovations, x, weights)
    reference = MoranRes(BaseOLS(y[:, None], x), full2W(weights), z=True)
    assert_allclose(ours.statistic, reference.I, rtol=1e-10)
    assert_allclose(ours.expectation, reference.eI, rtol=1e-10)
    assert_allclose(ours.variance, reference.vI, rtol=1e-8)
    assert_allclose(ours.z, reference.zI, rtol=1e-8)


def test_exact_mean_holds_with_self_links_under_the_null() -> None:
    rng = np.random.default_rng(2)
    weights = network(2, self_links=True)
    x = rng.uniform(0.5, 1.5, (30, 1))
    expected = residual_moran(rng.normal(size=30), x, weights).expectation
    draws = []
    for _ in range(4000):
        y = rng.normal(size=30)
        draws.append(residual_moran(ols(y, x).innovations, x, weights).statistic)
    assert expected > 0
    assert abs(np.mean(draws) - expected) < 4 * np.std(draws) / np.sqrt(len(draws))


def test_information_criteria_formulas_and_parameter_counts() -> None:
    rng = np.random.default_rng(3)
    weights = network(3)
    x = rng.uniform(0.5, 1.5, (30, 2))
    y = x @ [0.01, 0.02] + rng.normal(0, 0.01, 30)
    assert ols(y, x).parameters == 3
    assert error_ml(y, x, weights).parameters == 4
    assert lag_iv(y, x, weights).parameters is None
    criteria = information_criteria(10.0, 3, 30)
    assert criteria["aic"] == pytest.approx(-20 + 6)
    assert criteria["bic"] == pytest.approx(-20 + 3 * np.log(30))
    assert criteria["hqic"] == pytest.approx(-20 + 6 * np.log(np.log(30)))
