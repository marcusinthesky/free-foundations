"""Metric invariants for distances on frozen representation vectors."""

import numpy as np
import pytest
from hypothesis import given
from numpy.testing import assert_allclose

from free_foundations.encoders.contracts import FloatArray
from free_foundations.methods.distances import pairwise_distance
from tests._strategies import token_arrays


@given(token_arrays())
def test_chord_is_a_metric_and_ignores_individual_vector_length(values: FloatArray) -> None:
    rows = values.reshape(len(values), -1)
    if len(rows) < 2:
        return
    rows = np.column_stack([rows, np.ones(len(rows))])
    distance = pairwise_distance(rows)
    assert_allclose(distance, distance.T)
    assert_allclose(distance.diagonal(), 0)
    assert np.all((distance >= 0) & (distance <= 2 + 1e-12))
    assert_allclose(
        distance, pairwise_distance(rows * np.arange(1, len(rows) + 1)[:, None]), atol=1e-12
    )
    assert_allclose(distance[::-1, ::-1], pairwise_distance(rows[::-1]), atol=1e-12)
    assert_allclose(distance, pairwise_distance(-rows[:, ::-1]), atol=1e-12)
    for index in range(len(rows)):
        assert np.all(distance <= distance[:, index, None] + distance[index, None, :] + 1e-12)


def test_chord_distances_and_zero_vectors() -> None:
    values = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    distance = pairwise_distance(values)
    assert_allclose(distance[0], [0, np.sqrt(2), 2])
    with pytest.raises(ValueError, match="zero embedding"):
        pairwise_distance(np.zeros((2, 3)))
    assert_allclose(pairwise_distance(np.zeros((2, 3)), "euclidean"), 0)
