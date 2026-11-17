"""Matched-population, timing and missing-return checks for the quarterly study."""

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
from scipy.stats import multivariate_normal

from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.study import analysis
from free_foundations.study.analysis import (
    estimate_exposures,
    fernandez_geometries,
    fit_gram,
    fit_spatial,
    gaussian_observed,
    positive_covariance,
    run_analyses,
    spatial_training_score,
    validate_panel,
)
from free_foundations.study.inference import (
    generated_beta_indices,
    paired_intervals,
    stationary_orders,
    summarize_generated,
)
from free_foundations.study.spec import CHARACTERISTICS, StudySpec, panel_contract

if TYPE_CHECKING:
    from pathlib import Path


def test_original_complete_fernandez_network_survives_gram_shrinkage() -> None:
    issuers = ("PERMCO:1", "PERMCO:2", "PERMCO:3")
    quarters = pd.to_datetime(["2009-03-31", "2010-03-31", "2011-03-31", "2012-03-31"])
    histories = np.array([[1, 2, 3, 4], [4, 2, 3, 1], [3, 4, 1, 2]], dtype=float)
    frame = pd.DataFrame(
        [
            {
                "issuer_id": issuer,
                "quarter": quarter,
                **dict.fromkeys(CHARACTERISTICS, histories[index, position]),
            }
            for index, issuer in enumerate(issuers)
            for position, quarter in enumerate(quarters)
        ]
    )
    result = fernandez_geometries(frame, issuers, quarters[-1], StudySpec())
    expected = rank_distance(histories)
    np.testing.assert_allclose(result["fernandez_joint"].distance, expected)
    np.testing.assert_allclose(result["fernandez_joint"].weights, paper_weights(expected))
    assert np.linalg.eigvalsh(result["fernandez_joint"].gram).min() >= 1e-6 - 1e-12


def test_missing_characteristic_pairs_have_neutral_not_absent_links() -> None:
    frame = pd.DataFrame(
        {
            "issuer_id": ["A", "A", "B", "B"],
            "quarter": pd.to_datetime(["2009-03-31", "2009-06-30"] * 2),
            "market_cap_assets": [1, 2, np.nan, np.nan],
        }
    )
    result = fernandez_geometries(frame, ("A", "B"), "2009Q2", StudySpec())
    item = result["fernandez_market_cap_assets"]
    assert item.undefined_pairs == 1
    assert item.distance[0, 1] == pytest.approx(np.sqrt(2))
    np.testing.assert_array_equal(item.weights, [[0, 1], [1, 0]])
    assert item.gram[0, 1] == 0


def test_gaussian_missing_returns_are_marginalized_not_conditioned_or_filled() -> None:
    covariance = np.array([[2, 0.8, 0.2], [0.8, 3, 0.6], [0.2, 0.6, 1]])
    values = np.array([0.7, np.nan, -0.2])
    score, count = gaussian_observed(values, covariance)
    expected = multivariate_normal.logpdf(values[[0, 2]], cov=covariance[np.ix_([0, 2], [0, 2])])
    assert count == 2
    assert score == pytest.approx(expected)
    assert score != pytest.approx(multivariate_normal.logpdf(np.nan_to_num(values), cov=covariance))
    assert gaussian_observed(np.full(3, np.nan), covariance)[1] == 0
    with pytest.raises(ValueError, match="mask disagree"):
        gaussian_observed(values, covariance, np.ones(3, dtype=bool))


def test_unbalanced_covariance_is_positive_definite_with_no_history_issuer() -> None:
    values = np.array([[1, 2, np.nan], [2, np.nan, np.nan], [3, 6, np.nan]], dtype=float)
    covariance, delta = positive_covariance(values)
    np.linalg.cholesky(covariance)
    assert 0 <= delta <= 1
    assert covariance.shape == (3, 3)
    assert covariance[2, 2] > 0


def test_fast_spatial_objective_integrates_the_unobserved_coordinates() -> None:
    residuals = np.array([[0.2, np.nan, -0.1], [np.nan, 0.4, 0.1], [0.3, -0.1, 0.2]])
    weights = paper_weights(np.array([[0, 1, 2], [1, 0, 1.5], [2, 1.5, 0]], dtype=float))
    variances = np.array([0.1, 0.2, 0.3])
    coefficient, score = fit_spatial(residuals, weights, variances)
    assert score == pytest.approx(
        spatial_training_score(residuals, weights, variances, coefficient), abs=1e-9
    )
    assert score >= spatial_training_score(residuals, weights, variances, 0) - 1e-9


def test_unbalanced_gram_profile_matches_direct_marginal_gaussians() -> None:
    residuals = np.array([[0.2, np.nan, -0.1], [np.nan, 0.4, 0.1], [0.3, -0.1, 0.2]])
    gram = np.array([[1, 0.3, -0.2], [0.3, 1, 0.4], [-0.2, 0.4, 1]])
    variances = np.array([0.1, 0.2, 0.3])
    theta, score = fit_gram(residuals, gram, variances, 1e-6)
    covariance = ((1 - theta) * np.eye(3) + theta * gram) * np.sqrt(np.outer(variances, variances))
    assert score == pytest.approx(
        sum(gaussian_observed(row, covariance)[0] for row in residuals), abs=1e-10
    )


def test_exposure_proxy_keeps_short_and_unobserved_histories_explicit() -> None:
    rng = np.random.default_rng(10)
    factors = rng.normal(size=(20, 6)) * 0.02
    values = factors @ rng.normal(size=(6, 3))
    values[:, 1] = np.nan
    values[1:, 2] = np.nan
    result = estimate_exposures(values, factors, StudySpec())
    assert result.counts.tolist() == [20, 0, 1]
    assert np.isnan(result.beta[1]).all()
    assert np.isfinite(result.beta[2]).all()
    assert result.statuses[1].startswith("unavailable")
    assert result.statuses[2] == "regularized_rank_deficient_proxy"


def test_stationary_orders_retain_calendar_and_generated_draw_failures() -> None:
    orders = stationary_orders(8, 50, 4, 42)
    np.testing.assert_array_equal(orders, stationary_orders(8, 50, 4, 42))
    assert orders.shape == (50, 8)
    indices = generated_beta_indices(pd.date_range("2009-03-31", periods=8, freq="QE"), 3)
    assert indices.groupby("replicate").size().to_dict() == {0: 8, 1: 8, 2: 8, 3: 8}
    draws = pd.DataFrame(
        {
            "quarter": ["2010-03-31"] * 3,
            "method": ["W"] * 3,
            "estimator": ["ols"] * 3,
            "status": ["available", "unavailable", "available"],
            "premium_market": [1, np.nan, 3],
            "intensity": [0, np.nan, 0],
        }
    )
    result = summarize_generated(draws, 3)
    assert result["defined_draws"].eq(2).all()
    assert result["failed_draws"].eq(1).all()
    assert result["status"].eq("incomplete").all()


def test_conditional_intervals_keep_holes_and_reject_different_masks() -> None:
    quarters = pd.date_range("2009-03-31", periods=4, freq="QE")
    scores = pd.DataFrame(
        [
            {
                "quarter": quarter,
                "method": method,
                "score_per_issuer": value,
                "mask_sha256": str(index),
            }
            for index, quarter in enumerate(quarters)
            for method, value in (("A", float(index) if index != 1 else np.nan), ("B", 0.0))
        ]
    )
    result = paired_intervals(scores, pairs=[("A", "B")], draws=99)
    assert result["calendar_quarters"].eq(4).all()
    assert result["defined_quarters"].eq(3).all()
    assert result["difference"].eq(5 / 3).all()
    scores.loc[0, "mask_sha256"] = "different"
    with pytest.raises(ValueError, match="different observed"):
        paired_intervals(scores, draws=3)


def _small_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, StudySpec]:
    rng = np.random.default_rng(20)
    quarters = pd.date_range("2005-03-31", periods=22, freq="QE")
    factors = pd.DataFrame(rng.normal(0, 0.02, size=(22, 6)), columns=analysis.FACTOR_NAMES)
    factors["quarter"], factors["RF"] = quarters, 0.003
    issuers = tuple(f"PERMCO:{index}" for index in range(4))
    returns = rng.normal(0, 0.05, size=(22, 4))
    history = pd.DataFrame(
        [
            {
                "asof_year": 2010,
                "quarter": quarter,
                "issuer_id": issuer,
                "total_return": returns[position, column],
                "observed": True,
            }
            for position, quarter in enumerate(quarters)
            for column, issuer in enumerate(issuers)
        ]
    )
    panel = (
        history.loc[history["quarter"].ge("2010-01-01")]
        .drop(columns="asof_year")
        .reset_index(drop=True)
    )
    panel.loc[0, ["observed", "total_return"]] = [False, np.nan]
    characteristics = pd.DataFrame(
        [
            {
                "issuer_id": issuer,
                "quarter": quarter,
                **{name: float(position * (column + 1) + column % 2) for name in CHARACTERISTICS},
            }
            for position, quarter in enumerate(quarters)
            for column, issuer in enumerate(issuers)
        ]
    )
    spec = replace(
        StudySpec(),
        archive_end="2010-06-30",
        feature_start="2010-01-01",
        bootstrap_draws=19,
        generated_beta_draws=0,
    )
    return panel, characteristics, factors, history, spec


def _fake_mm(
    sample: pd.DataFrame, _calendar: pd.DatetimeIndex, _spec: StudySpec, _output: Path
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "replicate": 0,
                "ticker": issuer,
                "term": "market",
                "estimate": 1 + index,
                "converged": index != 3,
            }
            for index, issuer in enumerate(sorted(sample["ticker"].unique()))
        ]
    )


def test_matched_pipeline_retains_roster_masks_and_full_sample_mm_failures(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, characteristics, factors, history, spec = _small_inputs()
    monkeypatch.setattr(analysis, "_mm_estimates", _fake_mm)
    result = run_analyses(panel, characteristics, factors, {}, spec, tmp_path, history=history)
    assert len(result["core_roster"]) == len(panel)
    assert result["core"]["status"].eq("unavailable").all()
    assert result["core"]["firms"].eq(4).all()
    assert result["scores"].groupby("quarter")["observed_firms"].nunique().eq(1).all()
    assert result["scores"].groupby("quarter")["mask_sha256"].nunique().eq(1).all()
    assert result["exposures"]["observations"].eq(20).all()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["master"] == panel_contract(panel, spec)


def test_forecast_inputs_ignore_current_future_and_other_formation_histories(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, characteristics, factors, history, spec = _small_inputs()
    monkeypatch.setattr(analysis, "_mm_estimates", _fake_mm)
    before = run_analyses(
        panel, characteristics, factors, {}, spec, tmp_path / "before", history=history
    )
    changed = history.copy()
    changed.loc[changed["quarter"].ge("2010-03-31"), "total_return"] += 100
    changed = pd.concat(
        [changed, history.assign(asof_year=2020, total_return=999)], ignore_index=True
    )
    after = run_analyses(
        panel, characteristics, factors, {}, spec, tmp_path / "after", history=changed
    )
    first = pd.Timestamp("2010-03-31")
    pd.testing.assert_frame_equal(
        before["exposures"].loc[before["exposures"]["quarter"].eq(first)],
        after["exposures"].loc[after["exposures"]["quarter"].eq(first)],
    )
    pd.testing.assert_frame_equal(
        before["scores"].loc[before["scores"]["quarter"].eq(first)],
        after["scores"].loc[after["scores"]["quarter"].eq(first)],
    )


def test_master_mask_and_representation_identity_are_failure_gates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, characteristics, factors, history, spec = _small_inputs()
    wrong = panel.copy()
    wrong.loc[0, "observed"] = True
    with pytest.raises(ValueError, match="flags and finite"):
        validate_panel(wrong)
    monkeypatch.setattr(analysis, "_mm_estimates", _fake_mm)
    payload = {"issuer_ids": ["wrong"] * 4, "values": np.ones((4, 3))}
    with pytest.raises(ValueError, match="row IDs"):
        run_analyses(
            panel,
            characteristics,
            factors,
            {"2010Q1": {"full_xbrl/model": payload}},
            spec,
            tmp_path,
            history=history,
        )


def test_empty_analytical_population_has_a_reviewable_manifest_without_r(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, characteristics, factors, history, spec = _small_inputs()

    def forbidden(*_args: object, **_kwargs: object) -> None:
        msg = "MM backend must not run on an empty population"
        raise AssertionError(msg)

    monkeypatch.setattr(analysis, "robust_betas", forbidden)
    result = run_analyses(
        panel.iloc[:0],
        characteristics.iloc[:0],
        factors.iloc[:0],
        {},
        spec,
        tmp_path,
        history=history.iloc[:0],
    )
    assert result["calendar"]["firms"].eq(0).all()
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["status"] == "unavailable_no_analytical_population"


def test_task_owners_do_not_run_each_others_estimators(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, characteristics, factors, history, spec = _small_inputs()

    def no_mm(*_args: object, **_kwargs: object) -> None:
        message = "Measurement must not rerun descriptive MM"
        raise AssertionError(message)

    monkeypatch.setattr(analysis, "_mm_estimates", no_mm)
    result = run_analyses(
        panel,
        characteristics,
        factors,
        {},
        spec,
        tmp_path / "measure",
        history=history,
        tasks="measurement",
    )
    assert result["core"].empty
    assert not result["scores"].empty
    monkeypatch.setattr(analysis, "_mm_estimates", _fake_mm)

    def no_forecast(*_args: object, **_kwargs: object) -> None:
        message = "Replication must not rerun forecast estimation"
        raise AssertionError(message)

    monkeypatch.setattr(analysis, "estimate_exposures", no_forecast)
    result = run_analyses(
        panel,
        characteristics,
        factors,
        {},
        spec,
        tmp_path / "replicate",
        history=history,
        tasks="replication",
    )
    assert not result["core"].empty
    assert result["scores"].empty
    assert result["coordinates"].empty
