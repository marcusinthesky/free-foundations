"""Kernel scaling, concentration matching and unattainable targets."""

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from numpy.testing import assert_allclose

from free_foundations.fernandez.kernels import (
    effective_neighbours,
    geometry,
    kernel_weights,
    matched_scale,
    scaled_weights,
)
from free_foundations.fernandez.models import paper_weights, rank_distance


def distances(seed: int, firms: int = 25) -> np.ndarray:
    return rank_distance(np.random.default_rng(seed).normal(size=(firms, 6)))


def test_scaled_kernel_is_row_stochastic_without_underflow() -> None:
    distance = distances(1) * 50
    weights = scaled_weights(distance, 1e-4)
    assert np.isfinite(weights).all()
    assert_allclose(weights.sum(axis=1), 1)
    assert_allclose(weights.diagonal(), 0)
    assert_allclose(scaled_weights(distances(1), 1.0), paper_weights(distances(1)), atol=1e-12)


def test_median_kernel_is_invariant_to_rescaling_distances() -> None:
    distance = distances(2)
    first, _ = kernel_weights(distance, "median")
    second, _ = kernel_weights(distance * 7.5, "median")
    assert_allclose(first, second, atol=1e-12)


@given(st.integers(0, 1000), st.floats(0.2, 0.95))
@settings(max_examples=25, deadline=None)
def test_matched_bandwidth_hits_attainable_targets(seed: int, fraction: float) -> None:
    distance = distances(seed)
    target = 1 + fraction * (len(distance) - 2)
    weights, scale = kernel_weights(distance, "matched", target=target)
    assert_allclose(effective_neighbours(weights), target, rtol=1e-6)
    larger = scaled_weights(distance, scale * 1.5)
    assert effective_neighbours(larger) >= effective_neighbours(weights)


def test_matching_the_reference_to_itself_recovers_unit_bandwidth() -> None:
    distance = distances(4)
    target = effective_neighbours(paper_weights(distance))
    assert_allclose(matched_scale(distance, target), 1.0, rtol=1e-6)


def test_uniform_network_has_zero_gap_and_maximal_effective_count() -> None:
    firms = 12
    uniform = (np.ones((firms, firms)) - np.eye(firms)) / (firms - 1)
    record = geometry(None, uniform)
    assert_allclose(record["frobenius_gap"], 0, atol=1e-12)
    assert_allclose(record["effective_fraction"], 1)


def test_matched_kernel_rejects_self_links_and_reports_unattainable_geometry() -> None:
    with pytest.raises(ValueError, match="zero self-links only"):
        kernel_weights(distances(9), "matched", self_links=True, target=3)
    identical = np.zeros((6, 6))
    weights, bandwidth = kernel_weights(identical, "matched", target=3)
    assert bandwidth > 0
    assert_allclose(effective_neighbours(weights), 5)
    assert_allclose(geometry(identical, weights)["effective_neighbours"], 5)
    # A target above the maximal concentration limit chooses the upper endpoint.
    weights, _ = kernel_weights(distances(9, 6), "matched", target=8)
    assert_allclose(effective_neighbours(weights), 5, atol=1e-6)


def test_empty_rows_have_no_effective_neighbours_and_herfindahl_is_reported() -> None:
    from free_foundations.fernandez.kernels import geometry  # noqa: PLC0415

    assert np.isnan(effective_neighbours(np.zeros((4, 4))))
    uniform = (np.ones((5, 5)) - np.eye(5)) / 4
    record = geometry(None, uniform)
    assert_allclose(record["mean_herfindahl"], 1 / 4)
    assert_allclose(record["effective_neighbours"], 4)
