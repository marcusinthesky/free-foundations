"""The bounded diagnostic grid changes its declared measurement dimension only."""

import numpy as np
import pandas as pd
import pytest
from arch.bootstrap import StationaryBootstrap

from free_foundations.contracts import FloatArray
from free_foundations.panel import inference
from free_foundations.panel.validation import (
    PRINCIPAL,
    RANDOM,
    SALTS,
    diagnostic_distances,
    diagnostic_pairs,
)
from free_foundations.representations.distance import pairwise_distance


def test_normalization_grid_preserves_euclidean_scale_and_exposes_fold_null() -> None:
    rng = np.random.default_rng(71)
    tickers = tuple(f"T{i}" for i in range(30))
    targets = rng.normal(size=(30, 5))
    states = {name: rng.normal(size=(30, 4)) for name in (*PRINCIPAL, *RANDOM)}
    states |= {f"kumo_random{seed}__late": np.ones((30, 4)) for seed in ("", "43", "44")}
    distances, quality, checks = diagnostic_distances(states, targets, tickers, 2020)
    assert len(quality) == len(SALTS) * (len(PRINCIPAL) + len(RANDOM) + 1)
    assert len(checks) == 3
    assert all(
        isinstance(row["prediction_max_error"], float) and row["prediction_max_error"] < 1e-12
        for row in checks
    )
    np.testing.assert_allclose(
        distances["normalization_native_euclidean__direct"],
        pairwise_distance(states["direct"], metric="euclidean"),
    )
    assert not np.allclose(
        distances["normalization_native_chord__direct"], distances["published_native__direct"]
    )
    for name in PRINCIPAL:
        np.testing.assert_array_equal(
            distances[f"normalization_decoded_euclidean__{name}"],
            distances[f"fold0@decoded__{name}"],
        )


def test_diagnostic_pairs_reject_incomplete_scores() -> None:
    with pytest.raises(ValueError, match="Incomplete diagnostic scores"):
        diagnostic_pairs({"published_native__direct|matched|diagonal"})


def test_bootstrap_cache_is_readonly_and_preserves_stationary_draws() -> None:
    counts = inference.resample_counts(12, 3, replicates=17, seed=7)
    expected = np.zeros((17, 12))
    bootstrap = StationaryBootstrap(3, np.arange(12), seed=7)
    for row, (arguments, _) in enumerate(bootstrap.bootstrap(17)):
        expected[row] = np.bincount(arguments[0], minlength=12)
    np.testing.assert_array_equal(counts, expected)
    assert inference.resample_counts(12, 3, replicates=17, seed=7) is counts
    assert not counts.flags.writeable


def test_vectorized_contrasts_match_scalar_resampling(monkeypatch: pytest.MonkeyPatch) -> None:
    rng = np.random.default_rng(52)
    daily = pd.DataFrame(
        rng.normal(size=(24, 3)),
        columns=["A", "B", "C"],
        index=pd.date_range("2020-12-20", periods=24),
    )
    counts = rng.multinomial(24, np.full(24, 1 / 24), size=101).astype(float)

    def fixed_counts(_days: int, _block: int) -> FloatArray:
        return counts

    monkeypatch.setattr(inference, "resample_counts", fixed_counts)
    pairs = [("first", "A", "B"), ("second", "A", "C")]
    result = inference.contrasts(daily, pairs)
    records = result.to_dict("records")
    for row, (_, left, right) in zip(records, pairs, strict=True):
        difference = (daily[left] - daily[right]).to_numpy()
        expected = np.percentile(counts @ difference, [2.5, 97.5])
        for block in inference.BLOCKS:
            np.testing.assert_allclose(
                [float(row[f"lower_{block}"]), float(row[f"upper_{block}"])],
                expected,
            )
        assert float(row["difference"]) == pytest.approx(difference.sum())
        assert float(row["year_2020"]) + float(row["year_2021"]) == pytest.approx(difference.sum())
