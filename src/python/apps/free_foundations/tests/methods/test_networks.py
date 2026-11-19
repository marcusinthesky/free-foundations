"""Networks are row-stochastic, label-equivariant and fitted to no outcome."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays

from free_foundations.methods.networks import (
    Network,
    exponential_weights,
    industry_weights,
    knn_weights,
    permuted,
    representation_distance,
)

POINTS = arrays(
    np.float64,
    st.tuples(st.integers(6, 15), st.integers(2, 5)),
    elements=st.floats(-5, 5, allow_nan=False, width=32),
)


def _distinct(points: np.ndarray) -> np.ndarray:
    """Add a fixed tiny jitter so nearest-neighbour ties are generic."""
    rng = np.random.default_rng(0)
    return points + rng.normal(scale=1e-3, size=points.shape) + 1.0


@pytest.mark.unit
@settings(max_examples=40, deadline=None)
@given(points=POINTS, neighbours=st.integers(1, 4))
def test_knn_graph_is_row_stochastic_symmetric_in_support_and_label_equivariant(
    points: np.ndarray, neighbours: int
) -> None:
    # Arrange
    distance = representation_distance(_distinct(points))
    order = np.random.default_rng(1).permutation(len(points))

    # Act
    weights = knn_weights(distance, neighbours)
    relabelled = knn_weights(distance[np.ix_(order, order)], neighbours)

    # Assert: rows sum to one, links are mutual, and relabelling only permutes W.
    np.testing.assert_allclose(weights.sum(axis=1), 1.0)
    assert np.array_equal(weights > 0, (weights > 0).T)
    assert np.all(np.diag(weights) == 0)
    assert np.all((weights > 0).sum(axis=1) >= neighbours)
    np.testing.assert_allclose(relabelled, weights[np.ix_(order, order)])


@pytest.mark.unit
def test_fernandez_kernel_is_her_rownormalized_exponential() -> None:
    # Arrange
    distance = np.array([[0.0, 0.5, 2.0], [0.5, 0.0, 1.0], [2.0, 1.0, 0.0]])

    # Act
    weights = exponential_weights(distance)

    # Assert: equation (10) with a zero diagonal.
    expected = np.exp(-distance)
    np.fill_diagonal(expected, 0)
    np.testing.assert_allclose(weights, expected / expected.sum(axis=1, keepdims=True))


@pytest.mark.unit
def test_industry_links_same_sic2_and_isolates_unknown_or_singleton_codes() -> None:
    # Arrange
    codes = pd.Series(["3571", "3572", "6021", None])

    # Act
    weights = industry_weights(codes)

    # Assert
    np.testing.assert_allclose(weights[0], [0, 1, 0, 0])
    np.testing.assert_allclose(weights[1], [1, 0, 0, 0])
    assert weights[2:].sum() == 0
    network = Network("industry|sic2", "comparator", "same SIC-2", ("A", "B", "C", "D"), weights)
    assert network.isolates == 2


@pytest.mark.unit
def test_permutation_null_keeps_degrees_and_breaks_identities() -> None:
    # Arrange
    distance = representation_distance(_distinct(np.arange(20.0).reshape(10, 2) ** 1.5))
    weights = knn_weights(distance, 2)

    # Act
    null = permuted(weights, seed=42)

    # Assert
    assert sorted((null > 0).sum(axis=1)) == sorted((weights > 0).sum(axis=1))
    assert not np.allclose(null, weights)


@pytest.mark.unit
def test_network_rejects_unnormalized_or_self_linked_weights() -> None:
    # Arrange
    bad = np.array([[0.5, 0.5], [1.0, 0.0]])

    # Act / Assert
    with pytest.raises(ValueError, match="row-normalized"):
        Network("bad", "control", "test", ("A", "B"), bad)
