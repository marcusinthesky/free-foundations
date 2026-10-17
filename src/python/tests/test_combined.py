"""Independent likelihood and matched-network invariance checks."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.stats import multivariate_normal, norm

from free_foundations.fernandez.combined import likelihood
from free_foundations.fernandez.models import paper_weights, rank_distance


@given(st.integers(min_value=0, max_value=10000))
@settings(max_examples=12)
def test_combined_likelihood_matches_density_and_is_permutation_invariant(seed: int) -> None:
    rng = np.random.default_rng(seed)
    count = 12
    x = rng.uniform(0.5, 1.5, (count, 1))
    y = 0.03 * x[:, 0] + rng.normal(0, 0.01, count)
    weights = paper_weights(rank_distance(rng.normal(size=(count, 10))))
    fit = likelihood(y, x, weights)
    operator = np.eye(count) - fit["lambda"] * weights
    inverse = np.linalg.inv(operator)
    expected = multivariate_normal.logpdf(
        y, mean=x[:, 0] * fit["premium"], cov=fit["innovation_variance"] * inverse @ inverse.T
    )
    assert fit["log_likelihood"] == pytest.approx(expected, abs=1e-9)
    order = rng.permutation(count)
    reordered = likelihood(y[order], x[order], weights[np.ix_(order, order)])
    assert reordered["log_likelihood"] == pytest.approx(fit["log_likelihood"], abs=1e-8)
    baseline = likelihood(y, x, np.zeros_like(weights))
    assert fit["log_likelihood"] >= baseline["log_likelihood"] - 1e-8


def test_no_spatial_limit_is_the_profiled_independent_gaussian_likelihood() -> None:
    x = np.array([[0.7], [0.9], [1.1], [1.4]])
    y = np.array([0.01, 0.03, 0.02, 0.05])
    coefficient = np.linalg.lstsq(x, y, rcond=None)[0]
    variance = np.mean((y - x @ coefficient) ** 2)
    expected = norm.logpdf(y, loc=x @ coefficient, scale=np.sqrt(variance)).sum()
    fit = likelihood(y, x, np.zeros((4, 4)))
    assert fit["lambda"] == 0
    assert fit["log_likelihood"] == pytest.approx(expected, abs=1e-10)
