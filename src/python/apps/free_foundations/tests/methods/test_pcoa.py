"""Principal-coordinate geometry and the strict interpretation threshold."""

import numpy as np
import pytest

from free_foundations.methods.pcoa import Coordinates, coordinate_distances, principal_coordinates


@pytest.mark.unit
def test_principal_coordinates_reconstruct_euclidean_distances() -> None:
    # Arrange
    distance = np.array([[0.0, 1.0, 3.0], [1.0, 0.0, 2.0], [3.0, 2.0, 0.0]])

    # Act
    result = principal_coordinates(distance)

    # Assert
    np.testing.assert_allclose(coordinate_distances(result.coordinates), distance, atol=1e-12)
    np.testing.assert_allclose(result.shares, [1.0])
    assert result.trigger


@pytest.mark.unit
@pytest.mark.parametrize(("first_share", "expected"), [(0.25, False), (0.25001, True)])
def test_interpretation_trigger_is_strict(first_share: float, *, expected: bool) -> None:
    # Arrange
    fit = Coordinates(np.empty(0), np.empty((0, 0)), np.array([first_share]), 0.0)

    # Act
    triggered = fit.trigger

    # Assert
    assert triggered is expected
