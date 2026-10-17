"""Numerical checks of the paper's conditional measurement-error bounds."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from free_foundations.fernandez.models import paper_weights


@given(st.integers(min_value=0, max_value=10000), st.floats(min_value=-0.8, max_value=0.8))
@settings(max_examples=20)
def test_kernel_and_covariance_perturbation_bounds(seed: int, intensity: float) -> None:
    rng = np.random.default_rng(seed)
    distance = rng.uniform(0, 2, (8, 8))
    alternative = distance + rng.uniform(0, 0.1, (8, 8))
    np.fill_diagonal(distance, 0)
    np.fill_diagonal(alternative, 0)
    first, second = paper_weights(distance), paper_weights(alternative)
    error = np.max(np.abs(distance - alternative))
    assert np.linalg.norm(first - second, ord=np.inf) <= np.expm1(2 * error) + 1e-12
    inverse = np.linalg.inv(np.eye(8) - intensity * first)
    other_inverse = np.linalg.inv(np.eye(8) - intensity * second)
    innovations = np.diag(rng.uniform(0.1, 2, 8))
    observed = np.linalg.norm(
        inverse @ innovations @ inverse.T - other_inverse @ innovations @ other_inverse.T, ord=2
    )
    resolvent_bound = max(np.linalg.norm(inverse, ord=2), np.linalg.norm(other_inverse, ord=2))
    bound = (
        2
        * np.linalg.norm(innovations, ord=2)
        * abs(intensity)
        * resolvent_bound**3
        * np.linalg.norm(first - second, ord=2)
    )
    assert observed <= bound + 1e-12
