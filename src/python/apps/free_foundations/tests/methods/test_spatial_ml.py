"""Fast fixed-graph refits recover known coefficients and reproduce statadic fits."""

from __future__ import annotations

import numpy as np
import pytest

from free_foundations.methods import spatial, spatial_ml
from free_foundations.methods.networks import knn_weights, representation_distance


def _graph(count: int, seed: int) -> np.ndarray:
    points = np.random.default_rng(seed).normal(size=(count, 3))
    return knn_weights(representation_distance(points), 6)


def _lag_sample(count: int, rho: float, seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    weights = _graph(count, seed)
    beta = rng.normal(1.0, 0.3, count)
    outcome = np.linalg.solve(
        np.eye(count) - rho * weights, 0.01 + 0.02 * beta + rng.normal(0, 0.01, count)
    )
    return outcome, beta, weights


@pytest.mark.integration
@pytest.mark.parametrize(("estimator", "process"), [("lag_ml", "lag"), ("error_ml", "error")])
def test_profile_likelihood_matches_statadic_on_the_same_sample(
    estimator: spatial.Estimator, process: spatial_ml.Process
) -> None:
    # Arrange
    outcome, beta, weights = _lag_sample(120, 0.4, seed=3)
    design = np.column_stack([np.ones_like(beta), beta])

    # Act
    reference = spatial.cross_section(outcome, {"beta": beta}, weights, estimator, intercept=True)
    coefficients, value, _ = spatial_ml.profile(
        outcome, design, spatial_ml.Graph.of(weights), process
    )

    # Assert: the bootstrap path and statadic agree within the replication tolerance.
    assert reference["status"] == "available"
    assert value == pytest.approx(reference["spatial"], abs=1e-4)
    assert coefficients[-1] == pytest.approx(reference["beta"], abs=1e-4)


@pytest.mark.integration
def test_two_stage_lag_matches_statadic_instruments() -> None:
    # Arrange
    outcome, beta, weights = _lag_sample(120, 0.4, seed=5)

    # Act
    reference = spatial.cross_section(outcome, {"beta": beta}, weights, "lag_iv", intercept=False)
    coefficients, rho = spatial_ml.lag_iv(
        outcome, beta[:, None], spatial_ml.Graph.of(weights), (0,)
    )

    # Assert
    assert reference["status"] == "available"
    assert rho == pytest.approx(reference["spatial"], abs=1e-8)
    assert coefficients[0] == pytest.approx(reference["beta"], abs=1e-8)


@pytest.mark.unit
def test_period_effects_panel_recovers_the_spatial_coefficient() -> None:
    # Arrange: sixty quarters with common shocks, a CAPM regressor and rho = 0.3.
    rng = np.random.default_rng(7)
    periods = []
    for quarter in range(60):
        weights = _graph(80, 100 + quarter)
        regressor = rng.normal(1, 0.3, 80) * rng.normal(0.02, 0.08)
        shock = rng.normal(0, 0.05)
        outcome = np.linalg.solve(
            np.eye(80) - 0.3 * weights, shock + regressor + rng.normal(0, 0.05, 80)
        )
        periods.append(spatial_ml.Period.of(outcome, regressor, weights))

    # Act
    fit = spatial_ml.panel_profile(periods, "lag")

    # Assert: the true value lies inside the profile-likelihood interval.
    assert abs(fit.spatial - 0.3) < 1.96 * fit.spatial_se + 0.02
    assert fit.slope == pytest.approx(1.0, abs=0.1)
    assert fit.contributions.sum() == pytest.approx(fit.loglik)


@pytest.mark.unit
def test_graph_interval_keeps_the_spatial_filter_invertible() -> None:
    # Arrange
    graph = spatial_ml.Graph.of(_graph(30, 9))

    # Act
    low, high = graph.interval

    # Assert
    for value in (low, high):
        assert np.all(np.abs(1 - value * graph.spectrum) > 0)
    assert -1 <= low < 0 < high <= 1


@pytest.mark.unit
def test_two_stage_lag_rejects_unidentified_coefficients() -> None:
    # Arrange
    weights = (np.ones((4, 4)) - np.eye(4)) / 3
    graph = spatial_ml.Graph.of(weights)

    # Act
    coefficients, rho = spatial_ml.lag_iv(np.arange(4.0), np.ones((4, 1)), graph, (0,))

    # Assert
    assert np.isnan(coefficients).all()
    assert np.isnan(rho)
