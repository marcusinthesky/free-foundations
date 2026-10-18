"""Calibrated readouts decode held-out reference-factor exposures out of fold."""

import numpy as np

from free_foundations.expanded.distance import pairwise_distance
from free_foundations.panel.decoding import (
    covariance_exposures,
    decode,
    folds,
    reference_exposures,
    reference_factors,
    reliability,
    targets,
)
from free_foundations.panel.observations import residualize


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


def test_reference_factors_recover_cohort_loadings_up_to_rotation() -> None:
    rng = np.random.default_rng(4)
    days = 20000
    common = rng.normal(size=(days, 2))
    reference = common @ rng.normal(size=(2, 200)) + 0.5 * rng.normal(size=(days, 200))
    loadings = rng.normal(size=(30, 2))
    cohort = common @ loadings.T + 0.05 * rng.normal(size=(days, 30))
    exposures = reference_exposures(cohort, reference_factors(reference, 2))
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


def test_a_held_out_firms_returns_never_reach_its_fold_model() -> None:
    """Perturb one firm's raw returns: its fold's decoder and predictions are unchanged."""
    rng = np.random.default_rng(2)
    days, firms, outside = 600, 40, 80
    factors = rng.normal(size=(days, 6)) * 0.01
    x = np.column_stack([np.ones(days), factors])
    common = rng.normal(size=(days, 3)) * 0.01
    loadings = rng.normal(size=(firms, 3))
    raw = x @ rng.normal(size=(7, firms)) + common @ loadings.T
    raw += 0.01 * rng.normal(size=(days, firms))
    others = x @ rng.normal(size=(7, outside)) + common @ rng.normal(size=(3, outside))
    others += 0.01 * rng.normal(size=(days, outside))
    tickers = tuple(f"T{i}" for i in range(firms))
    states = loadings @ rng.normal(size=(3, 12)) + 0.1 * rng.normal(size=(firms, 12))

    def pipeline(cohort: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        _, prior = residualize(cohort, x)
        _, reference = residualize(others, x)
        bundle = targets(prior, reference)
        predictions, _ = decode(states, bundle.reference[5], tickers)
        return bundle.reference[5], predictions, bundle.covariance

    target, predictions, in_panel = pipeline(raw)
    held = 7
    changed = raw.copy()
    changed[:, held] += 0.05 * rng.normal(size=days)
    again, predicted, in_panel_again = pipeline(changed)
    others_rows = np.arange(firms) != held
    np.testing.assert_allclose(again[others_rows], target[others_rows])
    assert not np.allclose(again[held], target[held])
    fold = folds(tickers) == folds(tickers)[held]
    np.testing.assert_allclose(predicted[fold], predictions[fold])
    # The in-panel eigendecomposition pools the cohort: the same change moves other rows.
    moved = pairwise_distance(in_panel_again[others_rows], metric="euclidean")
    assert not np.allclose(moved, pairwise_distance(in_panel[others_rows], metric="euclidean"))


def test_a_diagonal_covariance_has_no_reference_exposure() -> None:
    """The review's counterexample: no common dependence, but unequal idiosyncratic risk."""
    rng = np.random.default_rng(3)
    days, firms = 5000, 30
    scale = np.where(np.arange(firms) < 3, 0.05, 0.01)
    prior = rng.normal(size=(days, firms)) * scale
    reference = rng.normal(size=(days, 60)) @ np.diag(rng.uniform(0.01, 0.05, 60))
    bundle = targets(prior, reference)
    in_panel = np.linalg.norm(covariance_exposures(prior, 3), axis=1)
    # In-panel coordinates single out the three high-variance firms.
    assert set(np.argsort(in_panel)[-3:]) == {0, 1, 2}
    assert in_panel[:3].min() > 10 * in_panel[3:].max()
    # Loadings on outside factors are noise: a tiny share of each firm's variance.
    rows = {row["target"]: row for row in reliability(prior, reference, 3)}
    assert float(rows["reference"]["commonality_mean"]) < 0.01
    assert float(rows["covariance"]["effective_firm_fraction"]) < 0.15
    assert np.abs(bundle.reference[3]).max() < 0.2 * scale.max()


def test_readout_never_extrapolates_beyond_its_training_fold() -> None:
    """One firm far outside a near-degenerate state cloud cannot decide the fit."""
    rng = np.random.default_rng(5)
    tickers = tuple(f"T{i}" for i in range(80))
    exposures = rng.normal(size=(80, 2))
    states = 1e-4 * rng.normal(size=(80, 50))
    states[0] += 0.02  # 200 training standard deviations out.
    predictions, quality = decode(states, exposures, tickers)
    assert quality["decoder_r2"] > -1
    assert np.all(predictions <= exposures.max(axis=0))
    assert np.all(predictions >= exposures.min(axis=0))
