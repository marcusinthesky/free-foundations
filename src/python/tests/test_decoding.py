"""Calibrated readouts decode prior covariance exposures out of fold."""

import numpy as np

from free_foundations.expanded.distance import pairwise_distance
from free_foundations.panel.decoding import covariance_exposures, decode, folds


def test_exposures_recover_the_common_distances_of_a_factor_structure() -> None:
    rng = np.random.default_rng(0)
    loadings = rng.normal(size=(30, 2))
    returns = rng.normal(size=(20000, 2)) @ loadings.T + 0.05 * rng.normal(size=(20000, 30))
    exposures = covariance_exposures(returns, factors=2)
    np.testing.assert_allclose(
        pairwise_distance(exposures, metric="euclidean"),
        pairwise_distance(loadings, metric="euclidean"),
        atol=0.05,
    )


def test_folds_are_deterministic_and_balanced() -> None:
    tickers = tuple(f"T{i}" for i in range(23))
    labels = folds(tickers)
    assert np.array_equal(labels, folds(tickers))
    assert sorted(np.bincount(labels.astype(int)).tolist()) == [4, 4, 5, 5, 5]


def test_decoding_is_out_of_fold_and_accurate_for_linear_states() -> None:
    rng = np.random.default_rng(1)
    tickers = tuple(f"T{i}" for i in range(60))
    exposures = rng.normal(size=(60, 3))
    states = exposures @ rng.normal(size=(3, 8)) + 0.01 * rng.normal(size=(60, 8))
    predictions, quality = decode(states, exposures, tickers)
    assert quality["decoder_r2"] > 0.95
    assert quality["exposure_distance_spearman"] > 0.95
    # A firm's own exposure never enters its own prediction.
    changed = exposures.copy()
    changed[0] += 100
    again, _ = decode(states, changed, tickers)
    np.testing.assert_allclose(again[0], predictions[0])
