"""Replication cohorts, estimator scope, bootstrap indices and documented substitutions."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.testing import assert_allclose

from free_foundations.fernandez import manifest
from free_foundations.fernandez.bootstrap import REPLICATES, SPARE, network_draws, quarter_indices
from free_foundations.fernandez.estimates import nonspatial, spatial
from free_foundations.fernandez.evaluation import quarterly_data
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.fernandez.replication import (
    audit,
    distances,
    sensitivity_cohorts,
    sensitivity_contrasts,
)
from free_foundations.fernandez.replication_data import WINDOWS, Inputs, cohort


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
    assert set(rows) == {"spatial_lag_iv", "spatial_error_ml"}
    assert np.isnan(float(rows["spatial_lag_iv"]["aic"]))
    assert np.isfinite(float(rows["spatial_error_ml"]["aic"]))
    assert nonspatial(y, x, ("market",))["parameters"] == 2


def test_manifest_sections_are_complete(tmp_path: Path) -> None:
    manifest.write(tmp_path)
    record = json.loads((tmp_path / "replication-manifest.json").read_text())
    assert all(record[key] for key in ("reported", "conventions", "substitutions"))
    assert "Information matrix" in (tmp_path / "replication-manifest.md").read_text()
    assert "iiisdp234.pdf" in (tmp_path / "replication-manifest.md").read_text()


def test_common_cohorts_and_joint_distance_keep_the_declared_information() -> None:
    names = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")
    index = pd.MultiIndex.from_product(
        [range(2015, 2025), ["A", "B", "C"]], names=["year", "ticker"]
    )
    frame = pd.DataFrame(index=index)
    for number, name in enumerate(names):
        frame[name] = np.arange(len(index), dtype=float) ** (number + 1)
    frame.loc[(2020, "C"), "debt_maturity"] = np.nan
    inputs = Inputs(frame, pd.DataFrame(), ("A", "B", "C"))
    assert cohort(inputs, names) == ("A", "B")
    assert cohort(inputs, names[:3]) == ("A", "B", "C")
    built = distances(inputs, names[:3], ("A", "B", "C"))
    assert set(built) == {"fernandez_joint", *(f"fernandez_{name}" for name in names[:3])}
    assert_allclose(
        built["fernandez_joint"] ** 2,
        np.mean([built[f"fernandez_{name}"] ** 2 for name in names[:3]], axis=0),
    )
    matched = sensitivity_cohorts(
        {
            "shifted": inputs,
            "contemporaneous": Inputs(frame, pd.DataFrame(), ("A", "C"), "contemporaneous"),
        }
    )
    assert matched["shifted"]["common_four|natural"] == ("A", "B")
    assert matched["contemporaneous"]["common_four|natural"] == ("A",)
    assert matched["shifted"]["common_four|intersection"] == ("A",)
    assert matched["shifted"]["common_three|intersection"] == ("A", "C")
    assert matched["contemporaneous"]["common_three|intersection"] == ("A", "C")


def test_timing_and_software_contrasts_are_right_minus_left_on_matched_samples() -> None:
    rows = [
        {
            "table": "common_four",
            "sample": "intersection",
            "sample_id": "common_four:intersection",
            "network": "fernandez_joint",
            "estimator": "spatial_error_ml",
            "firms": 32,
            "timing": timing,
            "backend": backend,
            "premium_market": value,
            "intensity": value,
            "pseudo_r2_structural": value,
            "pseudo_r2_reduced": value,
        }
        for timing, offset in (("shifted", 0), ("contemporaneous", 10))
        for backend, value in (("robustbase", offset + 1), ("robust", offset + 3))
    ]
    contrasts = sensitivity_contrasts(pd.DataFrame(rows))
    assert len(contrasts) == 4
    assert contrasts.loc[contrasts["contrast"].eq("timing"), "delta_premium_market"].eq(10).all()
    assert contrasts.loc[contrasts["contrast"].eq("software"), "delta_premium_market"].eq(2).all()
    assert contrasts["sample_id"].eq("common_four:intersection").all()


def test_quarterly_windows_include_forty_distinct_calendar_quarters() -> None:
    dates = pd.bdate_range("2014-12-31", "2025-12-31")
    prices = pd.DataFrame({"A": np.exp(np.arange(len(dates)) * 0.0001)}, index=dates)
    factors = pd.DataFrame({"RF": 0.0001, "Mkt-RF": 0.0003}, index=dates)
    for start, end in WINDOWS.values():
        data = quarterly_data(prices, factors, start=start, end=end)
        assert len(data) == 40
        assert data["date"].is_unique
        assert data["date"].min().year == int(start[:4])
        assert data["date"].max().year == int(end[:4])


def test_var_audit_preserves_the_unreconciled_published_result(tmp_path: Path) -> None:
    audit(tmp_path)
    record = json.loads((tmp_path / "audit.json").read_text())["var_audit"]
    assert record["reconciled"] is False
    assert record["maximum_under_stated_calibration"] < 16.86 < record["published_value"]
