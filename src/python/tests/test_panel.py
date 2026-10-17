"""Independent density and chronological information-set checks."""

import json
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
from free_foundations.panel.likelihood import (
    block,
    correlation_only,
    fit,
    forecast_covariance,
    gaussian_daily,
    gaussian_score,
)


@given(st.integers(min_value=3, max_value=12), st.floats(min_value=-0.8, max_value=0.8))
@settings(max_examples=20, deadline=None)
def test_panel_score_matches_full_covariance(firms: int, intensity: float) -> None:
    rng = np.random.default_rng(42)
    positions = rng.normal(size=(firms, 3))
    distance = np.linalg.norm(positions[:, None] - positions[None, :], axis=-1)
    weights = paper_weights(distance)
    residuals = rng.normal(size=(23, firms)) * 0.02
    stats = block(residuals, weights)
    variance = np.full(firms, 0.0007)
    inverse = np.linalg.inv(np.eye(firms) - intensity * weights)
    expected = multivariate_normal.logpdf(residuals, cov=0.0007 * inverse @ inverse.T).sum()
    np.testing.assert_allclose(stats.score(intensity, variances=variance), expected, rtol=1e-10)
    profiled = float(stats.variances(intensity)[0])
    np.testing.assert_allclose(
        stats.score(intensity),
        multivariate_normal.logpdf(residuals, cov=profiled * inverse @ inverse.T).sum(),
        rtol=1e-10,
    )
    # Heterogeneous innovations: A^-1 D A^-T with one profiled variance per firm.
    diagonal = stats.variances(intensity, "diagonal")
    np.testing.assert_allclose(
        stats.score(intensity, "diagonal"),
        multivariate_normal.logpdf(residuals, cov=(inverse * diagonal) @ inverse.T).sum(),
        rtol=1e-10,
    )
    # The vector refactor keeps the original scalar spherical formula.
    weighted = residuals @ weights.T
    scalar = (
        np.mean(residuals**2)
        - 2 * intensity * np.mean(residuals * weighted)
        + intensity**2 * np.mean(weighted**2)
    )
    np.testing.assert_allclose(profiled, scalar, rtol=1e-12)


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
    prices.to_parquet(source / "prices.parquet")
    factors.to_parquet(source / "factors.parquet")
    index = pd.MultiIndex.from_product([range(2013, 2016), tickers], names=["year", "ticker"])
    four = pd.DataFrame(
        np.repeat(np.arange(1, 4), 6)[:, None] * np.ones((18, 4)),
        index=index,
        columns=observations.CHARACTERISTICS,
    )
    expected = observations.annual_data(four, 2016, output=output)
    scored = pd.read_parquet(output / "observations/2016-returns.parquet")
    future_dates = prices.loc["2016"].index
    assert scored.index[0] == future_dates[1]
    prices.loc[future_dates[10], "A"] = np.nan
    prices.to_parquet(source / "prices.parquet")
    actual = observations.annual_data(four, 2016, output=output)
    assert actual.tickers == expected.tickers == tuple(tickers)
    for component in ("prior", "raw_prior", "factor_covariance"):
        np.testing.assert_array_equal(getattr(actual, component), getattr(expected, component))


def test_diagonal_arm_at_zero_is_the_diagonal_factor_benchmark() -> None:
    rng = np.random.default_rng(5)
    firms = 7
    residuals = rng.normal(size=(300, firms)) * rng.uniform(0.01, 0.04, firms)
    factor = np.cov(rng.normal(size=(300, firms)), rowvar=False) * 1e-4
    weights = paper_weights(rng.uniform(0, 2, (firms, firms)) + rng.uniform(0, 2, (firms, firms)).T)
    previous = block(residuals, weights)
    covariance = forecast_covariance(previous, weights, 0.0, factor, "diagonal")
    np.testing.assert_array_equal(covariance, factor + np.diag(np.mean(residuals**2, axis=0)))


def test_heterogeneous_variance_coefficient_is_recovered() -> None:
    rng = np.random.default_rng(11)
    blocks = []
    for firms in (12, 15):
        positions = rng.normal(size=(firms, 2))
        weights = paper_weights(3 * np.linalg.norm(positions[:, None] - positions[None], axis=-1))
        scales = rng.uniform(0.5, 3.0, firms)
        shocks = rng.normal(size=(6000, firms)) * scales
        residuals = np.linalg.solve(np.eye(firms) - 0.4 * weights, shocks.T).T
        blocks.append(block(residuals, weights))
    estimate, score = fit(blocks, "diagonal")
    assert abs(estimate - 0.4) < 0.05
    assert score >= sum(item.score(0.0, "diagonal") for item in blocks)


def test_correlation_only_imposes_shared_marginals_and_daily_scores_sum() -> None:
    rng = np.random.default_rng(3)
    raw = rng.normal(size=(200, 4)) * [0.01, 0.02, 0.03, 0.04]
    covariance = np.cov(rng.normal(size=(200, 4)), rowvar=False)
    matched = correlation_only(covariance, raw)
    np.testing.assert_allclose(np.diag(matched), np.var(raw, axis=0, ddof=1))
    values = rng.normal(size=(30, 4)) * 0.02
    daily = gaussian_daily(values, matched)
    np.testing.assert_allclose(daily.sum(), gaussian_score(values, matched))
    np.testing.assert_allclose(daily, multivariate_normal.logpdf(values, cov=matched))


def test_three_characteristic_cohort_ignores_debt() -> None:
    index = pd.MultiIndex.from_product([range(2013, 2016), list("ABC")], names=["year", "ticker"])
    four = pd.DataFrame(
        np.repeat(np.arange(1, 4), 3)[:, None] * np.ones((9, 4)),
        index=index,
        columns=list(observations.CHARACTERISTICS),
    )
    four["debt_maturity"] = np.nan
    assert list(observations.eligible(four, 2016, observations.CHARACTERISTICS[:3], 3)) == list(
        "ABC"
    )
    assert list(observations.eligible(four, 2016, observations.CHARACTERISTICS, 3)) == []


def test_cohort_requires_nonconstant_histories_at_every_length() -> None:
    years = range(2011, 2016)
    index = pd.MultiIndex.from_product([years, list("AB")], names=["year", "ticker"])
    four = pd.DataFrame(1.0, index=index, columns=list(observations.CHARACTERISTICS))
    four.loc[(2011, "A"), :] = 0.0  # A varies over five years but is constant over three.
    four.loc[(2014, "B"), :] = 0.0
    assert list(observations.eligible(four, 2016, observations.CHARACTERISTICS, 5)) == list("AB")
    assert list(observations.eligible(four, 2016, observations.CHARACTERISTICS, 3)) == ["B"]


def test_saved_distances_are_recomputed_never_reused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from free_foundations.panel import design, networks  # noqa: PLC0415

    rng = np.random.default_rng(4)
    tickers = tuple("ABCDEF")
    index = pd.MultiIndex.from_product([range(2010, 2020), tickers], names=["year", "ticker"])
    four = pd.DataFrame(
        rng.uniform(0.1, 2, (len(index), 4)),
        index=index,
        columns=list(observations.CHARACTERISTICS),
    )
    broad = pd.DataFrame(
        {
            networks.ASSETS: rng.uniform(1, 9, len(index)),
            networks.INCOME: rng.normal(size=len(index)),
        },
        index=index,
    )
    calls: list[str] = []

    def encoded(data: object, **_: object) -> dict[str, np.ndarray]:
        calls.append(str(getattr(data, "digest", "")))
        return {"direct": np.zeros((len(tickers), len(tickers)))}

    monkeypatch.setattr(networks, "representation_distances", encoded)
    monkeypatch.setattr(networks, "ARMS", {"direct": "classical"})
    monkeypatch.setattr(design, "ROOT", tmp_path)
    plan = design.Design("unit", observations.CHARACTERISTICS, 3, ("histories",))
    stale = tmp_path / "unit" / "distances" / "2019" / "histories__direct.parquet"
    stale.parent.mkdir(parents=True)
    pd.DataFrame(np.ones((6, 6)), index=list(tickers), columns=list(tickers)).to_parquet(stale)
    result = networks.distances(four, broad, 2019, tickers, plan)
    assert calls
    np.testing.assert_array_equal(result["histories__direct"], 0)
    np.testing.assert_array_equal(pd.read_parquet(stale).to_numpy(), 0)
    sidecar = json.loads(stale.with_suffix(".json").read_text())
    assert sidecar["context_digest"] == calls[0]


def test_designs_declare_cohort_history_for_every_network() -> None:
    from free_foundations.panel.design import DESIGNS  # noqa: PLC0415

    assert DESIGNS["four"].cohort_histories == (3,)
    assert DESIGNS["four-h5"].cohort_histories == (3, 5)
    assert DESIGNS["three"].cohort_histories == (3, 5)
    assert "debt_maturity" not in DESIGNS["three"].characteristics


def test_every_scored_column_is_described() -> None:
    from free_foundations.panel.evaluation import describe  # noqa: PLC0415

    assert describe("raw_sample_covariance")["arm"] == "control"
    assert describe("uniform_network")["arm"] == "reference"
    assert describe("h3__fernandez_joint")["history"] == "h3"
    assert describe("histories__tabfm__early_concat")["arm"] == "state"
    assert describe("fernandez_joint__placebo3")["arm"] == "fernandez"
