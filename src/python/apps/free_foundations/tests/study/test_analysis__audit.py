"""Scientific comparisons use identical geometry, outcomes and calendar resamples."""

# These oracle checks intentionally exercise internal geometry/covariance boundaries.
# ruff: noqa: SLF001

from __future__ import annotations

import json
from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.fernandez.kernels import effective_neighbours, kernel_weights
from free_foundations.fernandez.models import error_ml, lag_iv
from free_foundations.study import analysis
from free_foundations.study.analysis import Geometry, match_gram_geometry, run_analyses
from free_foundations.study.inference import paired_intervals, scientific_contrasts
from free_foundations.study.moments import exponential_weights, identity_shrink
from free_foundations.study.spec import CHARACTERISTICS, StudySpec, file_hash

if TYPE_CHECKING:
    from pathlib import Path


def test_matched_spatial_uses_exact_repaired_gram_and_preserves_original_network() -> None:
    raw = np.array([[1, 0.9, 0.9], [0.9, 1, -0.9], [0.9, -0.9, 1]])
    gram, delta = identity_shrink(raw)
    distance = np.sqrt(2 * (1 - raw))
    weights = exponential_weights(distance)
    original = Geometry(distance, weights, gram, delta, 0)
    target = effective_neighbours(weights)
    matched = match_gram_geometry(original, target)
    chord = np.sqrt(np.maximum(2 * (1 - gram), 0))
    expected, bandwidth = kernel_weights(chord, "matched", target=target)
    np.testing.assert_array_equal(matched.weights, weights)
    np.testing.assert_array_equal(matched.distance, distance)
    np.testing.assert_array_equal(matched.gram, gram)
    assert matched.matched_weights is not None
    np.testing.assert_allclose(matched.matched_weights, expected)
    assert matched.matched_bandwidth == pytest.approx(bandwidth)
    assert matched.matched_target == target
    assert delta > 0


def test_native_euclidean_arm_stays_distinct_from_unit_gram_chord_arm() -> None:
    distance = np.array([[0, 1, 2], [1, 0, 1.5], [2, 1.5, 0]])
    weights = exponential_weights(distance)
    reference = Geometry(distance, weights, np.eye(3), 0, 0)
    values = np.array([[1, 0], [10, 0], [0, 1]], dtype=float)
    native = analysis._native_geometry(values, reference, StudySpec())
    matched = match_gram_geometry(native, effective_neighbours(weights))
    assert native.spatial_metric == "native_euclidean"
    assert native.distance[0, 1] == 9
    assert np.sqrt(2 * (1 - matched.gram[0, 1])) < 0.01
    assert matched.matched_weights is not None
    assert not np.allclose(matched.weights, matched.matched_weights)


def test_zero_readout_pair_audit_counts_each_unordered_pair_once() -> None:
    distance = np.ones((3, 3)) - np.eye(3)
    reference = Geometry(distance, exponential_weights(distance), np.eye(3), 0, 0)
    native = analysis._native_geometry(
        np.array([[0, 0], [0, 0], [1, 2]], dtype=float), reference, StudySpec()
    )
    assert native.undefined_pairs == 3


def test_spatial_matched_and_gram_forecasts_share_scales_and_exact_gram_geometry() -> None:
    rng = np.random.default_rng(198)
    prior = rng.normal(0, 0.1, size=(20, 3))
    factors = rng.normal(0, 0.03, size=(20, 6))
    spec = StudySpec()
    fit = analysis.estimate_exposures(prior, factors, spec)
    distance = np.array([[0, 1, 2], [1, 0, 1.5], [2, 1.5, 0]])
    weights = exponential_weights(distance)
    gram = np.array([[1, 0.6, -0.1], [0.6, 1, 0.2], [-0.1, 0.2, 1]])
    item = match_gram_geometry(
        Geometry(distance, weights, gram, 0, 0), effective_neighbours(weights)
    )
    covariances, audits, _ = analysis._forecast_covariances(prior, fit, {"test": item}, spec)
    audit = {row["method"]: row for row in audits}
    common = fit.beta @ fit.factor_covariance @ fit.beta.T
    variance, _ = analysis._positive_variances(fit.residuals, spec.min_eigenvalue)
    matched_parameter = audit["test|spatial_matched"]["parameter"]
    gram_parameter = audit["test|gram"]["parameter"]
    assert isinstance(matched_parameter, float)
    assert isinstance(gram_parameter, float)
    assert item.matched_weights is not None
    inverse = np.linalg.inv(np.eye(3) - matched_parameter * item.matched_weights)
    expected_spatial = common + (inverse * variance) @ inverse.T
    expected_gram = common + (
        ((1 - gram_parameter) * np.eye(3) + gram_parameter * gram)
        * np.sqrt(np.outer(variance, variance))
    )
    np.testing.assert_allclose(covariances["test|spatial_matched"], expected_spatial)
    np.testing.assert_allclose(covariances["test|gram"], expected_gram)
    assert audit["test|spatial"]["geometry"] == "raw_characteristic_distance"
    assert audit["test|spatial_matched"]["geometry"] == "repaired_unit_gram"
    assert audit["test|gram"]["geometry"] == "repaired_unit_gram"


def test_required_contrasts_keep_variance_treatments_and_rungs_matched() -> None:
    geometries = [
        "fernandez_joint",
        "fernandez/model",
        "standard_xbrl/model",
        "full_xbrl/model",
        "full_xbrl/model@decoded",
    ]
    names = {
        f"{geometry}|{arm}|{variance}"
        for geometry in geometries
        for arm in analysis.COVARIANCE_ARMS
        for variance in ("correlation", "covariance")
    } | {f"ff5_mom_diagonal|{variance}" for variance in ("correlation", "covariance")}
    contrasts = scientific_contrasts(names)
    assert (
        "full_xbrl/model|gram|correlation",
        "full_xbrl/model|spatial_matched|correlation",
        "gram_minus_matched_spatial",
    ) in contrasts
    assert (
        "full_xbrl/model@decoded|gram|correlation",
        "full_xbrl/model|gram|correlation",
        "decoded_minus_native",
    ) in contrasts
    assert (
        "full_xbrl/model|gram|correlation",
        "standard_xbrl/model|gram|correlation",
        "adjacent_information_rungs",
    ) in contrasts
    assert (
        "standard_xbrl/model|spatial_matched|covariance",
        "fernandez_joint|spatial_matched|covariance",
        "learned_minus_fernandez",
    ) in contrasts
    assert all(left.rsplit("|", 1)[-1] == right.rsplit("|", 1)[-1] for left, right, _ in contrasts)
    assert contrasts[0][0].endswith("|correlation")


def test_default_direct_intervals_retain_missing_calendar_cells_and_unavailable_pairs() -> None:
    dates = pd.date_range("2010-03-31", periods=4, freq="QE")
    scores = pd.DataFrame(
        [
            {
                "quarter": date,
                "method": f"full_xbrl/model|{arm}|correlation",
                "score_per_issuer": value,
                "mask_sha256": str(index),
            }
            for index, date in enumerate(dates)
            for arm, value in (
                ("gram", float(index) if index != 1 else np.nan),
                ("spatial_matched", 0.0),
                ("spatial", np.nan),
            )
        ]
    )
    intervals = paired_intervals(scores, calendar=dates, draws=99)
    paired = intervals.loc[intervals["contrast_family"].eq("gram_minus_matched_spatial")]
    assert paired["difference"].eq(5 / 3).all()
    assert paired["defined_quarters"].eq(3).all()
    assert paired["calendar_quarters"].eq(4).all()
    undefined = intervals.loc[intervals["contrast_family"].eq("spatial_geometry_sensitivity")]
    assert undefined["defined_quarters"].eq(0).all()
    assert undefined["defined_draws"].eq(0).all()
    assert undefined["status"].eq("unavailable").all()


def test_stage_records_every_planned_unavailable_model_without_changing_outcome_mask(
    tmp_path: Path,
) -> None:
    rng = np.random.default_rng(8)
    dates = pd.date_range("2009-03-31", periods=21, freq="QE")
    factors = pd.DataFrame(rng.normal(0, 0.02, size=(21, 6)), columns=analysis.FACTOR_NAMES)
    factors["quarter"], factors["RF"] = dates, 0.001
    values = rng.normal(0, 0.05, size=(21, 3))
    history = pd.DataFrame(
        [
            {
                "quarter": date,
                "issuer_id": f"PERMCO:{column}",
                "asof_year": 2014,
                "total_return": values[index, column],
                "observed": True,
            }
            for index, date in enumerate(dates)
            for column in range(3)
        ]
    )
    panel = history.loc[history["quarter"].eq(dates[-1])].drop(columns="asof_year").copy()
    panel.loc[panel.index[0], ["observed", "total_return"]] = [False, np.nan]
    characteristics = history[["issuer_id", "quarter"]].copy()
    for name in CHARACTERISTICS:
        characteristics[name] = rng.normal(size=len(characteristics))
    characteristics["cutoff"] = [
        (pd.Timestamp(value).to_period("Q") - 1).end_time.tz_localize("UTC")
        for value in characteristics["quarter"]
    ]
    spec = replace(
        StudySpec(),
        feature_start="2014-01-01",
        archive_end="2014-03-31",
        models=("test_missing_model",),
        generated_beta_draws=0,
        bootstrap_draws=19,
    )
    result = run_analyses(
        panel, characteristics, factors, {}, spec, tmp_path, history=history, tasks="measurement"
    )
    scores = result["scores"]
    expected = "full_xbrl/test_missing_model@decoded|spatial_matched|correlation"
    row = scores.loc[scores["method"].eq(expected)].iloc[0]
    assert row["status"] == "unavailable_representation"
    assert np.isnan(row["score"])
    assert scores["firms"].eq(3).all()
    assert scores["observed_firms"].eq(2).all()
    assert len(set(scores["mask_sha256"])) == 1
    assert not scores.duplicated(["quarter", "method"]).any()
    assert "adjacent_information_rungs" in set(result["conditional_intervals"]["contrast_family"])
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    audit = manifest["pairwise_arrays"][0]
    archive = tmp_path / audit["file"]
    assert audit["sha256"] == file_hash(archive)
    with np.load(archive, allow_pickle=False) as arrays:
        np.testing.assert_array_equal(arrays["issuer_ids"], sorted(panel["issuer_id"]))
        np.testing.assert_array_equal(arrays["prior_returns__counts"], np.full((3, 3), 20))
        assert arrays["prior_returns__raw_covariance"].dtype == np.float64
        assert arrays["fernandez_market_cap_assets__counts"].dtype == np.int32
        assert arrays["fernandez_market_cap_assets__defined"].all()
        np.testing.assert_allclose(
            arrays["fernandez_market_cap_assets__raw_distance"] ** 2,
            2 * (1 - arrays["fernandez_market_cap_assets__raw_correlation"]),
        )
        assert len(arrays["prior_quarters"]) == 20


def test_spatial_lag_is_two_stage_least_squares_with_published_instruments() -> None:
    x = np.array([[0.5], [1.4], [0.7], [2], [1.1]])
    y = np.array([0.2, 0.6, 0.1, 0.8, 0.4])
    distance = np.abs(np.arange(5)[:, None] - np.arange(5))
    weights = exponential_weights(distance)
    design = np.column_stack([weights @ y, x])
    instruments = np.column_stack([weights @ x, x])
    projection = instruments @ np.linalg.inv(instruments.T @ instruments) @ instruments.T
    expected = np.linalg.solve(design.T @ projection @ design, design.T @ projection @ y)
    fitted = lag_iv(y, x, weights)
    np.testing.assert_allclose([fitted.intensity, fitted.premium], expected)
    assert fitted.log_likelihood is None
    assert fitted.parameters is None


@pytest.mark.parametrize("estimator", ["spatial_lag_iv", "spatial_error_ml"])
def test_generated_refits_match_original_estimates_without_unused_dense_diagnostics(
    estimator: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    x = np.array([[0.5], [1.4], [0.7], [2], [1.1]])
    y = np.array([0.2, 0.6, 0.1, 0.8, 0.4])
    weights = exponential_weights(np.abs(np.arange(5)[:, None] - np.arange(5)))
    full = lag_iv(y, x, weights) if estimator == "spatial_lag_iv" else error_ml(y, x, weights)

    def forbidden_inverse(_matrix: np.ndarray) -> np.ndarray:
        message = "A bootstrap refit must not compute unused asymptotic covariance inverses."
        raise AssertionError(message)

    def forbidden_solve(_matrix: np.ndarray, _right: np.ndarray) -> np.ndarray:
        message = "A bootstrap refit must not compute an unused reduced-form inverse solve."
        raise AssertionError(message)

    monkeypatch.setattr(np.linalg, "inv", forbidden_inverse)
    monkeypatch.setattr(np.linalg, "solve", forbidden_solve)
    fast = (
        lag_iv(y, x, weights, standard_errors=False, reduced_mean=False)
        if estimator == "spatial_lag_iv"
        else error_ml(y, x, weights, standard_errors=False)
    )
    np.testing.assert_array_equal(fast.premiums, full.premiums)
    np.testing.assert_array_equal(fast.innovations, full.innovations)
    assert fast.intensity == full.intensity
    assert fast.variance == full.variance
    assert fast.log_likelihood == full.log_likelihood
    assert np.isnan(fast.covariance).all()
    if estimator == "spatial_lag_iv":
        assert np.isnan(fast.reduced).all()


def test_generated_core_reuses_the_mm_calendar_draw_for_medians_and_retains_failed_firm(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dates = pd.date_range("2010-03-31", periods=3, freq="QE")
    issuers = tuple(f"PERMCO:{index}" for index in range(3))
    values = np.array([[0.03, 0.10, -0.04], [0.08, -0.02, 0.06], [-0.01, 0.09, 0.02]])
    panel = pd.DataFrame(
        [
            {"quarter": date, "issuer_id": issuer, "total_return": values[i, j], "observed": True}
            for i, date in enumerate(dates)
            for j, issuer in enumerate(issuers)
        ]
    )
    characteristics = panel[["issuer_id", "quarter"]].copy()
    for name in CHARACTERISTICS:
        characteristics[name] = np.tile([1.0, 3.0, 2.0], 3) + np.repeat([0, 1, -1], 3)
    factors = pd.DataFrame(
        {"quarter": dates, "RF": 0.001, **dict.fromkeys(analysis.FACTOR_NAMES, 0.01)}
    )
    spec = replace(
        StudySpec(),
        feature_start="2010-01-01",
        archive_end="2010-09-30",
        bootstrap_draws=0,
        generated_beta_draws=2,
    )

    def mm_fixture(
        _sample: pd.DataFrame, _calendar: pd.DatetimeIndex, _spec: StudySpec, _output: Path
    ) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "replicate": replicate,
                    "ticker": issuer,
                    "term": "market",
                    "estimate": (replicate + 1) * (index + 1),
                    "converged": replicate != 2 or index != 2,
                }
                for replicate in range(3)
                for index, issuer in enumerate(issuers)
            ]
        )

    recorded: list[tuple[np.ndarray, np.ndarray]] = []
    original = analysis._core_fit

    def record_fit(  # noqa: PLR0913 -- preserve the estimator's exact calling convention.
        y: np.ndarray,
        beta: np.ndarray,
        weights: np.ndarray,
        estimator: str,
        spectrum: np.ndarray | None = None,
        *,
        standard_errors: bool = True,
    ) -> dict[str, object]:
        if estimator == "ols" and not standard_errors:
            recorded.append((y.copy(), beta.copy()))
        return original(y, beta, weights, estimator, spectrum, standard_errors=standard_errors)

    monkeypatch.setattr(analysis, "_mm_estimates", mm_fixture)
    monkeypatch.setattr(analysis, "_core_fit", record_fit)
    result = run_analyses(panel, characteristics, factors, {}, spec, tmp_path, tasks="replication")
    indices = analysis.generated_beta_indices(dates, 2, 4, spec.seed)
    first_draw = pd.DatetimeIndex(indices.loc[indices["replicate"].eq(1), "quarter"])
    expected_median = (
        pd.DataFrame(values - 0.001, index=dates).reindex(first_draw).median(axis=0).to_numpy()
    )
    np.testing.assert_allclose(recorded[0][0], expected_median)
    np.testing.assert_array_equal(recorded[0][1], [2, 4, 6])
    failed = result["generated_draws"].loc[result["generated_draws"]["replicate"].eq(2)]
    assert failed["firms"].eq(3).all()
    assert failed["status"].eq("unavailable").all()
    ols_intervals = result["generated_intervals"].loc[
        result["generated_intervals"]["estimator"].eq("ols")
    ]
    assert ols_intervals["requested_draws"].eq(2).all()
    assert ols_intervals["defined_draws"].eq(1).all()
    assert ols_intervals["failed_draws"].eq(1).all()


def test_mm_cache_is_invalidated_when_estimator_source_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    calendar = pd.date_range("2010-03-31", periods=3, freq="QE")
    sample = pd.DataFrame(
        {"date": calendar, "ticker": "PERMCO:1", "excess": [0.1, -0.1, 0.2], "market": [1, 2, 3]}
    )
    source = tmp_path / "fixture-betas.R"
    source.write_text("first estimator definition\n")
    monkeypatch.setattr(analysis, "MM_SCRIPT", source)
    calls: list[str] = []

    def fixture_mm(_sample: pd.DataFrame, _output: Path, **options: object) -> pd.DataFrame:
        assert options["backend"] == "robustbase"
        calls.append(source.read_text())
        return pd.DataFrame(
            {
                "replicate": [0],
                "ticker": ["PERMCO:1"],
                "term": ["market"],
                "estimate": [1.0],
                "converged": [True],
            }
        )

    monkeypatch.setattr(analysis, "robust_betas", fixture_mm)
    spec = replace(StudySpec(), generated_beta_draws=0)
    first = analysis._mm_estimates(sample, calendar, spec, tmp_path)
    cached = analysis._mm_estimates(sample, calendar, spec, tmp_path)
    pd.testing.assert_frame_equal(first, cached)
    assert len(calls) == 1
    source.write_text("revised estimator definition\n")
    analysis._mm_estimates(sample, calendar, spec, tmp_path)
    assert len(calls) == 2
    identity = json.loads((tmp_path / "mm/identity.json").read_text())
    assert identity["r_script_sha256"] == file_hash(source)
