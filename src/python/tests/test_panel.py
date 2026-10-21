"""Independent density and chronological information-set checks."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from scipy.stats import multivariate_normal

from free_foundations.fernandez.models import paper_weights
from free_foundations.panel import inference, observations
from free_foundations.panel.likelihood import (
    block,
    correlation_only,
    fit,
    forecast_covariance,
    gaussian_daily,
    gaussian_score,
)
from free_foundations.representations.encoding import prepare


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


def test_price_breaks_are_missing_returns_not_outliers() -> None:
    dates = pd.bdate_range("2020-11-18", periods=4)
    prices = pd.DataFrame(
        {"CHRD": [0.07, 0.073, 18.84, 19.0], "rally": [10.0, 22.0, 4.0, 4.4]}, index=dates
    )
    returns = observations.daily_returns(prices)
    assert np.isnan(returns["CHRD"].iloc[2])
    assert returns["CHRD"].iloc[3] == pytest.approx(19.0 / 18.84 - 1)
    # A +120% day and a -82% day are large but genuine moves.
    assert returns["rally"].iloc[1:3].tolist() == pytest.approx([1.2, 4 / 22 - 1])


def test_the_review_decision_not_the_threshold_sets_the_mask(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    dates = pd.bdate_range("2021-01-04", periods=3)
    prices = pd.DataFrame({"GEN": [1.0, 12.0, 12.6], "ERR": [5.0, 5.5, 5.6]}, index=dates)
    with pytest.raises(ValueError, match="Unreviewed price breaks"):
        observations.daily_returns(prices)
    monkeypatch.setitem(observations.EVENTS, ("GEN", "2021-01-05"), (False, "genuine"))
    # A recorded error is masked even inside the tenfold band.
    monkeypatch.setitem(observations.EVENTS, ("ERR", "2021-01-06"), (True, "series error"))
    returns = observations.daily_returns(prices)
    assert returns["GEN"].iloc[1] == pytest.approx(11.0)
    assert np.isnan(returns["ERR"].iloc[2])
    assert returns["ERR"].iloc[1] == pytest.approx(0.1)
    audit = observations.price_audit(prices)
    genuine = audit.loc[audit["ticker"].eq("GEN")]
    assert genuine["reviewed"].tolist() == [True]
    assert not genuine["masked"].any()


def test_every_masked_price_break_must_be_reviewed() -> None:
    dates = pd.bdate_range("2020-11-18", periods=4)
    reviewed = pd.DataFrame({"CHRD": [0.07, 0.073, 18.84, 19.0]}, index=dates)
    audit = observations.price_audit(reviewed)
    assert audit.loc[audit["masked"], "ticker"].tolist() == ["CHRD"]
    assert audit["reviewed"].all()
    with pytest.raises(ValueError, match="Unreviewed price breaks"):
        observations.price_audit(reviewed.rename(columns={"CHRD": "NEW"}))
    # Genuine large moves are listed, never masked.
    genuine = pd.DataFrame(
        {"QXO": [70.0, 60.5, 12.05]}, index=pd.bdate_range("2024-07-26", periods=3)
    )
    audit = observations.price_audit(genuine)
    assert not audit["masked"].any()
    assert audit["reviewed"].tolist() == [True]


def test_study_keeps_the_declared_cohort_and_principal_labels() -> None:
    from free_foundations.panel.design import STUDY  # noqa: PLC0415
    from free_foundations.panel.evaluation import describe  # noqa: PLC0415

    assert STUDY.cohort_histories == (3, 5)
    assert "debt_maturity" not in STUDY.characteristics
    assert describe("raw_sample_covariance")["arm"] == "control"
    assert describe("histories__tabfm__late")["arm"] == "task"
    assert describe("histories@decoded__limix__late")["arm"] == "calibrated"
    assert (
        describe("histories@support32@decoded__tabpfn_full__late")["rung"]
        == "histories@support32@decoded"
    )


def test_contrasts_and_confidence_sets_use_principal_matched_procedures() -> None:
    columns = [
        "histories@decoded__tabfm__late|matched|diagonal",
        "histories__tabfm__late|matched|diagonal",
        "histories__direct|matched|diagonal",
        "histories@decoded__tabpfn_full__late|matched|diagonal",
        "histories@decoded__tabpfn_full_random__late|matched|diagonal",
        "uniform_network|none|diagonal",
        "ff5_mom_diagonal|none|control",
        "fernandez_joint|exp|diagonal",
        "histories@support32@decoded__tabfm__late|matched|diagonal",
    ]
    rng = np.random.default_rng(0)
    daily = pd.DataFrame(
        rng.normal(size=(30, len(columns))),
        columns=columns,
        index=pd.date_range("2020-01-02", periods=30),
    )
    table = inference.contrasts(daily)
    assert set(table["contrast"]) == {
        "decoded vs native",
        "decoded vs native inputs",
        "pretrained vs reset",
    }
    first = table.loc[table["contrast"].eq("decoded vs native")].iloc[0]
    expected = (daily[columns[0]] - daily[columns[1]]).sum()
    assert first["difference"] == pytest.approx(expected)
    assert first["year_2020"] == pytest.approx(expected)
    groups = inference.families(daily)
    assert set(groups) == {"diagonal|matched"}
    assert "ff5_mom_diagonal|none|control" in groups["diagonal|matched"]
    assert "fernandez_joint|exp|diagonal" in groups["diagonal|matched"]
    assert not any(
        "random" in column or "@support" in column for column in groups["diagonal|matched"]
    )


def test_duplicate_networks_reuse_construction_and_sample_curves_score_diagonal_only(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from free_foundations.contracts import FloatArray  # noqa: PLC0415
    from free_foundations.fernandez.kernels import Kernel  # noqa: PLC0415
    from free_foundations.fernandez.models import rank_distance  # noqa: PLC0415
    from free_foundations.panel import evaluation  # noqa: PLC0415

    rng = np.random.default_rng(27)
    firms = 8
    joint = rank_distance(rng.normal(size=(firms, 5)))
    learned = np.abs(
        np.subtract.outer(np.arange(firms, dtype=float), np.arange(firms, dtype=float))
    )
    distances = {
        "fernandez_joint": joint,
        "histories__direct": learned,
        "histories@support32@decoded__pca16": learned.copy(),
    }
    calls: list[str] = []
    original = evaluation.kernel_weights

    def counted(
        distance: FloatArray,
        kernel: Kernel,
        *,
        self_links: bool = False,
        target: float | None = None,
    ) -> tuple[FloatArray, float]:
        calls.append(kernel)
        return original(distance, kernel, self_links=self_links, target=target)

    monkeypatch.setattr(evaluation, "kernel_weights", counted)
    built = evaluation.networks(distances)
    assert calls == ["exp", "matched"]
    assert (
        built["histories__direct", "matched"]
        is built["histories@support32@decoded__pca16", "matched"]
    )
    annual = observations.Annual(
        tuple(f"T{i}" for i in range(firms)),
        rng.normal(size=(100, firms)),
        rng.normal(size=(20, firms)),
        rng.normal(size=(100, firms)),
        rng.normal(size=(20, firms)),
        np.eye(firms),
        tuple(str(day) for day in pd.bdate_range("2020-01-02", periods=20)),
        rng.normal(size=(100, 6)),
    )
    panel = evaluation.Panel()
    for name, kernel in built:
        panel.intensities[name, kernel, "diagonal"] = (0.0 if name == "zero_network" else 0.2, 0.0)
    evaluation.update(panel, 2020, annual, distances)
    native = "histories__direct|matched|diagonal"
    sampled = "histories@support32@decoded__pca16|matched|diagonal"
    np.testing.assert_array_equal(panel.daily[native][0], panel.daily[sampled][0])
    assert "histories__direct|matched|correlation" in panel.daily
    assert "histories@support32@decoded__pca16|matched|correlation" not in panel.daily


def test_same_current_network_preserves_different_frozen_spatial_coefficients() -> None:
    from free_foundations.fernandez.models import rank_distance  # noqa: PLC0415
    from free_foundations.panel import evaluation  # noqa: PLC0415

    rng = np.random.default_rng(91)
    firms = 7
    distance = rank_distance(rng.normal(size=(firms, 5)))
    distances = {
        "fernandez_joint": distance,
        "histories__direct": distance,
        "histories__pca16": distance.copy(),
    }
    annual = observations.Annual(
        tuple(f"T{i}" for i in range(firms)),
        rng.normal(size=(100, firms)),
        rng.normal(size=(20, firms)),
        rng.normal(size=(100, firms)),
        rng.normal(size=(20, firms)),
        np.eye(firms),
        tuple(str(day) for day in pd.bdate_range("2020-01-02", periods=20)),
        rng.normal(size=(100, 6)),
    )
    panel = evaluation.Panel()
    built = evaluation.networks(distances)
    for name, kernel in built:
        intensity = 0.6 if name == "histories__pca16" else 0.1
        panel.intensities[name, kernel, "diagonal"] = (intensity, 0.0)
    evaluation.update(panel, 2020, annual, distances)
    for name in ("histories__direct", "histories__pca16"):
        weights = built[name, "matched"][0]
        intensity = panel.intensities[name, "matched", "diagonal"][0]
        expected_covariance = forecast_covariance(
            block(annual.prior, weights), weights, intensity, annual.factor_covariance, "diagonal"
        )
        expected = gaussian_daily(
            annual.raw_realized - annual.raw_prior.mean(axis=0), expected_covariance
        )
        np.testing.assert_allclose(panel.daily[f"{name}|matched|diagonal"][0], expected)
    assert not np.allclose(
        panel.daily["histories__direct|matched|diagonal"][0],
        panel.daily["histories__pca16|matched|diagonal"][0],
    )
