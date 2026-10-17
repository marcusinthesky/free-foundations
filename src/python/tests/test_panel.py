"""Independent density and chronological information-set checks."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.stats import multivariate_normal

from free_foundations.expanded.encoding import prepare
from free_foundations.fernandez.models import paper_weights
from free_foundations.panel import observations
from free_foundations.panel.likelihood import block, fit


@given(st.integers(min_value=3, max_value=12), st.floats(min_value=-0.8, max_value=0.8))
@settings(max_examples=20, deadline=None)
def test_panel_score_matches_full_covariance(firms: int, intensity: float) -> None:
    rng = np.random.default_rng(42)
    positions = rng.normal(size=(firms, 3))
    distance = np.linalg.norm(positions[:, None] - positions[None, :], axis=-1)
    weights = paper_weights(distance)
    residuals = rng.normal(size=(23, firms)) * 0.02
    stats = block(residuals, weights)
    variance = 0.0007
    inverse = np.linalg.inv(np.eye(firms) - intensity * weights)
    expected = multivariate_normal.logpdf(residuals, cov=variance * inverse @ inverse.T).sum()
    np.testing.assert_allclose(stats.score(intensity, variance), expected, rtol=1e-10)
    profiled = stats.variance(intensity)
    np.testing.assert_allclose(
        stats.score(intensity),
        multivariate_normal.logpdf(residuals, cov=profiled * inverse @ inverse.T).sum(),
        rtol=1e-10,
    )


def test_one_intensity_across_different_annual_networks() -> None:
    rng = np.random.default_rng(67)
    intensity = 0.45
    blocks = []
    for firms in (8, 13, 19):
        positions = rng.normal(size=(firms, 3))
        weights = paper_weights(np.linalg.norm(positions[:, None] - positions[None, :], axis=-1))
        residuals = np.linalg.solve(
            np.eye(firms) - intensity * weights,
            rng.normal(size=(firms, 4000)),
        ).T
        blocks.append(block(residuals, weights))
    estimate, score = fit(blocks)
    assert abs(estimate - intensity) < 0.04
    assert score >= sum(item.score(0) for item in blocks)


def test_future_snapshots_cannot_change_preprocessing_or_context() -> None:
    rng = np.random.default_rng(19)
    index = pd.MultiIndex.from_product(
        [range(2014, 2023), ["A", "B", "C"]], names=["year", "ticker"]
    )
    view = pd.DataFrame(rng.normal(size=(len(index), 4)), index=index, columns=list("abcd"))
    labels = pd.DataFrame(
        rng.normal(size=(len(index), 2)), index=index, columns=["income", "operating_cash"]
    )
    expected = prepare(view, labels, ("A", "B", "C"), 2020, "income")
    view.loc[2020:] = 1e9
    labels.loc[2020:] = -1e9
    actual = prepare(view, labels, ("A", "B", "C"), 2020, "income")
    assert actual.digest == expected.digest
    assert max(int(row.split(":")[-1]) for row in actual.support_ids) == 2018
    np.testing.assert_array_equal(actual.query, expected.query)
    np.testing.assert_array_equal(actual.targets, expected.targets)


def test_cohort_uses_past_data_and_first_return_is_not_scored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rng = np.random.default_rng(83)
    tickers = list("ABCDEF")
    dates = pd.bdate_range("2013-01-01", "2016-12-30")
    prices = pd.DataFrame(
        100 * np.exp(np.cumsum(rng.normal(0, 0.01, (len(dates), 6)), axis=0)),
        index=dates,
        columns=tickers,
    )
    factors = pd.DataFrame(
        rng.normal(0, 0.001, (len(dates), 7)),
        index=dates,
        columns=["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom", "RF"],
    )
    source, output = tmp_path / "source", tmp_path / "output"
    source.mkdir()
    output.mkdir()
    monkeypatch.setattr(observations, "SOURCE", source)
    monkeypatch.setattr(observations, "ROOT", output)
    prices.to_parquet(source / "prices.parquet")
    factors.to_parquet(source / "factors.parquet")
    index = pd.MultiIndex.from_product([range(2013, 2016), tickers], names=["year", "ticker"])
    four = pd.DataFrame(
        np.repeat(np.arange(1, 4), 6)[:, None] * np.ones((18, 4)),
        index=index,
        columns=observations.CHARACTERISTICS,
    )
    expected = observations.annual_data(four, 2016)
    scored = pd.read_parquet(output / "observations/2016-returns.parquet")
    future_dates = prices.loc["2016"].index
    assert scored.index[0] == future_dates[1]
    prices.loc[future_dates[10], "A"] = np.nan
    prices.to_parquet(source / "prices.parquet")
    actual = observations.annual_data(four, 2016)
    assert actual[0] == expected[0] == tuple(tickers)
    for component in (1, 3, 5):
        np.testing.assert_array_equal(actual[component], expected[component])
