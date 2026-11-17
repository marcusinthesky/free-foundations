"""Intersection-specific moments, undefined entries and visible PSD shrinkage."""

import numpy as np
import pytest
from scipy.stats import spearmanr

from free_foundations.study.moments import (
    exponential_weights,
    identity_shrink,
    pairwise_covariance,
    pairwise_spearman,
)


def test_spearman_reranks_the_pairwise_intersection() -> None:
    values = np.array([[1, 2, 3, 100], [2, np.nan, 1, 3]], dtype=float)
    result = pairwise_spearman(values)
    assert result.counts.tolist() == [[4, 3], [3, 3]]
    assert result.raw[0, 1] == pytest.approx(0.5)
    assert result.defined.all()


def test_complete_histories_preserve_original_spearman_and_exponential_kernel() -> None:
    values = np.array([[1, 3, 2, 4], [3, 1, 2, 4], [4, 2, 1, 3]], dtype=float)
    result = pairwise_spearman(values)
    expected = spearmanr(values, axis=1).statistic
    np.testing.assert_allclose(result.raw, expected)
    distances = np.sqrt(np.maximum(2 * (1 - expected), 0))
    np.fill_diagonal(distances, 0)
    affinity = np.exp(-distances)
    np.fill_diagonal(affinity, 0)
    np.testing.assert_allclose(result.weights, affinity / affinity.sum(axis=1, keepdims=True))
    np.testing.assert_array_equal(np.diag(result.weights), 0)


def test_missing_constant_and_short_histories_do_not_remove_entities() -> None:
    values = np.array([[np.nan, np.nan, np.nan], [1, np.nan, np.nan], [7, 7, 7], [1, 2, 3]])
    result = pairwise_spearman(values)
    assert result.raw.shape == (4, 4)
    np.testing.assert_array_equal(result.raw, np.eye(4))
    assert result.counts.diagonal().tolist() == [0, 1, 3, 3]
    assert result.defined.diagonal().tolist() == [False, False, False, True]
    assert result.counts[1, 3] == 1
    assert not result.defined[2, 3]
    np.testing.assert_allclose(result.weights.sum(axis=1), 1)


def test_indefinite_pairwise_raw_and_original_weights_survive_separate_shrinkage() -> None:
    values = np.array(
        [
            [1, 2, 1, 2, np.nan, np.nan],
            [1, 2, np.nan, np.nan, 1, 2],
            [np.nan, np.nan, 1, 2, 2, 1],
        ]
    )
    result = pairwise_spearman(values)
    expected = np.array([[1, 1, 1], [1, 1, -1], [1, -1, 1]], dtype=float)
    np.testing.assert_allclose(result.raw, expected)
    assert np.linalg.eigvalsh(result.raw)[0] < 0
    assert result.delta == pytest.approx((1 + 1e-6) / 2)
    assert np.linalg.eigvalsh(result.correlation)[0] >= 1e-6
    np.testing.assert_allclose(np.diag(result.correlation), 1)
    np.testing.assert_allclose(
        result.correlation, (1 - result.delta) * result.raw + result.delta * np.eye(3)
    )
    np.testing.assert_allclose(result.weights, exponential_weights(result.distance))
    assert result.distance[0, 1] == pytest.approx(0, abs=1e-7)
    assert result.gram_distance[0, 1] > 0


def test_covariance_and_pearson_use_their_own_pair_means_and_variances() -> None:
    values = np.array([[1, 2, 7], [2, np.nan, 7], [3, 6, np.nan], [np.nan, 8, 7]], dtype=float)
    result = pairwise_covariance(values)
    assert result.covariance is not None
    assert result.covariance_defined is not None
    assert result.counts.tolist() == [[3, 2, 2], [2, 3, 2], [2, 2, 3]]
    assert result.covariance[0, 1] == pytest.approx(4)
    assert result.covariance[0, 0] == pytest.approx(1)
    assert result.raw[0, 1] == pytest.approx(1)
    assert result.raw[0, 2] == 0
    assert not result.defined[0, 2]
    assert result.covariance_defined.all()
    assert result.covariance[0, 2] == 0
    np.testing.assert_allclose(np.diag(result.raw), 1)


def test_undefined_covariance_is_zero_with_separate_availability() -> None:
    result = pairwise_covariance(np.array([[1, np.nan], [np.nan, 2]], dtype=float))
    assert result.covariance_defined is not None
    np.testing.assert_array_equal(result.covariance, np.zeros((2, 2)))
    assert not result.covariance_defined.any()
    assert not result.defined.any()
    np.testing.assert_array_equal(result.raw, np.eye(2))
    assert result.counts.tolist() == [[1, 0], [0, 1]]


def test_pairwise_constant_subset_is_undefined_even_when_full_column_varies() -> None:
    result = pairwise_covariance(np.array([[0.1, 2], [0.1, 3], [0.1, 5], [1e5, np.nan]]))
    assert result.covariance is not None
    assert result.covariance[0, 1] == 0
    assert result.raw[0, 1] == 0
    assert not result.defined[0, 1]


def test_empty_and_single_entity_inputs_remain_well_defined() -> None:
    empty = pairwise_covariance(np.empty((3, 0)))
    assert empty.raw.shape == (0, 0)
    assert empty.delta == 0
    singleton = pairwise_spearman(np.empty((1, 0)))
    np.testing.assert_array_equal(singleton.raw, [[1]])
    np.testing.assert_array_equal(singleton.weights, [[0]])
    assert not singleton.defined[0, 0]


def test_identity_shrink_validates_and_never_mutates_raw() -> None:
    original = np.array([[1, 0.2], [0.2, 1]])
    snapshot = original.copy()
    repaired, delta = identity_shrink(original)
    assert delta == 0
    np.testing.assert_array_equal(original, snapshot)
    repaired[0, 1] = 0
    np.testing.assert_array_equal(original, snapshot)
    with pytest.raises(ValueError, match="unit-diagonal"):
        identity_shrink(np.array([[2, 0], [0, 1]], dtype=float))
    with pytest.raises(ValueError, match="without infinity"):
        pairwise_spearman(np.array([[np.inf, 1]]))
