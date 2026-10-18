"""The bounded diagnostic grid changes its declared measurement dimension only."""

import numpy as np

from free_foundations.expanded.distance import pairwise_distance
from free_foundations.panel.validation import PRINCIPAL, RANDOM, SALTS, diagnostic_distances


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
