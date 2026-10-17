"""Cross-sectional ladder data rules, bootstrap indices and the replication manifest."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.testing import assert_allclose

from free_foundations.fernandez.evaluation import quarterly_data
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.ladder import manifest
from free_foundations.ladder.bootstrap import REPLICATES, SPARE, network_draws, quarter_indices
from free_foundations.ladder.estimates import nonspatial, spatial


def test_market_column_is_unchanged_by_extra_factors() -> None:
    rng = np.random.default_rng(1)
    dates = pd.bdate_range("2016-01-01", "2016-12-30")
    prices = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0, 0.01, (len(dates), 2)), axis=0)),
        index=dates,
        columns=["A", "B"],
    )
    factors = pd.DataFrame(
        rng.normal(0, 0.001, (len(dates), 7)),
        index=dates,
        columns=["Mkt-RF", "SMB", "HML", "RMW", "CMA", "RF", "Mom"],
    )
    single = quarterly_data(prices, factors)
    extended = quarterly_data(prices, factors, factor_columns=("Mkt-RF", "SMB", "Mom"))
    assert_allclose(single["market"], extended["market"])
    assert {"smb", "mom"} <= set(extended.columns)


def test_bootstrap_indices_are_deterministic_and_shared() -> None:
    quarters = tuple(f"q{i}" for i in range(40))
    first, second = quarter_indices(quarters), quarter_indices(quarters)
    pd.testing.assert_frame_equal(first, second)
    assert first["replicate"].nunique() == REPLICATES + SPARE
    assert first.groupby("replicate").size().eq(40).all()


def test_network_stays_fixed_across_replicates() -> None:
    rng = np.random.default_rng(2)
    tickers = tuple("ABCDEFGHIJ")
    weights = paper_weights(rank_distance(rng.normal(size=(10, 6))))
    original = weights.copy()
    exposures = {
        r: pd.DataFrame({"market": rng.uniform(0.5, 1.5, 10)}, index=list(tickers)) for r in (1, 2)
    }
    medians = {r: pd.Series(rng.normal(0.02, 0.01, 10), index=list(tickers)) for r in (1, 2)}
    draws = network_draws({"w": weights}, tickers, exposures, medians)
    assert len(draws) == 2
    np.testing.assert_array_equal(weights, original)


def test_two_stage_rows_have_no_information_criteria() -> None:
    rng = np.random.default_rng(3)
    weights = paper_weights(rank_distance(rng.normal(size=(25, 6))) * 3)
    x = rng.uniform(0.5, 1.5, (25, 1))
    y = 0.02 * x[:, 0] + rng.normal(0, 0.01, 25)
    rows = {row["estimator"]: row for row in spatial(y, x, weights, ("market",))}
    assert np.isnan(float(rows["spatial_lag_iv"]["aic"]))
    assert np.isfinite(float(rows["spatial_error_ml"]["aic"]))
    assert nonspatial(y, x, ("market",))["parameters"] == 2


def test_manifest_sections_are_complete(tmp_path: Path) -> None:
    manifest.write(tmp_path)
    record = json.loads((tmp_path / "replication-manifest.json").read_text())
    assert all(record[key] for key in ("reported", "conventions", "substitutions"))
    assert "Information matrix" in (tmp_path / "replication-manifest.md").read_text()
