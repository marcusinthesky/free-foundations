"""Gaussian affinity on a matched roster."""

import numpy as np
import pytest

from free_foundations.methods.matched_networks import gaussian_weights


@pytest.mark.unit
def test_gaussian_uses_positive_median_and_keeps_coincident_pairs() -> None:
    # Arrange
    distance = np.array([[0.0, 0.0, 2.0], [0.0, 0.0, 2.0], [2.0, 2.0, 0.0]])

    # Act
    weights, bandwidth = gaussian_weights(distance)

    # Assert
    affinity = np.exp(-0.5)
    assert bandwidth == 2.0
    np.testing.assert_allclose(weights[0], [0.0, 1 / (1 + affinity), affinity / (1 + affinity)])
    np.testing.assert_allclose(weights[2], [0.5, 0.5, 0.0])


@pytest.mark.unit
def test_all_coincident_issuers_have_uniform_off_diagonal_weights() -> None:
    # Arrange
    distance = np.zeros((3, 3))

    # Act
    weights, bandwidth = gaussian_weights(distance)

    # Assert
    assert bandwidth is None
    np.testing.assert_allclose(weights, (1 - np.eye(3)) / 2)
