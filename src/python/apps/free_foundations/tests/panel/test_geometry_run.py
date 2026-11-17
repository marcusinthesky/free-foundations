"""Saved-geometry inventory, descriptive outputs, and spatial reconciliation."""

from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from free_foundations.panel import geometry, geometry_run
from free_foundations.panel.decoding import FACTORS, Targets
from free_foundations.panel.design import FOUNDATION_READOUTS, PRINCIPAL, STUDY
from free_foundations.panel.observations import Annual
from free_foundations.representations.distance import pairwise_distance

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


def histories(tickers: tuple[str, ...]) -> pd.DataFrame:
    """Complete nonconstant annual characteristic histories on the selected firms."""
    rng = np.random.default_rng(93)
    index = pd.MultiIndex.from_product([range(2015, 2020), tickers], names=["year", "ticker"])
    return pd.DataFrame(
        rng.normal(size=(len(index), len(STUDY.characteristics))),
        index=index,
        columns=list(STUDY.characteristics),
    )


def annual(tickers: tuple[str, ...]) -> Annual:
    """Small complete residual and raw-return blocks, with distinct prior means."""
    rng = np.random.default_rng(81)
    firms = len(tickers)
    return Annual(
        tickers=tickers,
        prior=rng.normal(size=(30, firms)) * 0.01,
        realized=rng.normal(size=(8, firms)) * 0.01,
        raw_prior=rng.normal(size=(30, firms)) * 0.02 + 0.003,
        raw_realized=rng.normal(size=(8, firms)) * 0.02 + 0.005,
        factor_covariance=np.eye(firms) * 1e-5,
        dates=tuple(pd.bdate_range("2020-01-02", periods=8).strftime("%Y-%m-%d")),
        reference=rng.normal(size=(30, 5)) * 0.01,
    )


def records() -> dict[str, list[geometry_run.Row]]:
    """Separate result collections used by the descriptive writer."""
    return {
        name: []
        for name in (
            "spectrum",
            "pcoa-summary",
            "coordinates",
            "weights",
            "component-returns",
            "component-covariance",
            "characteristic-associations",
            "extremes",
        )
    }


def test_parameter_boundary_marks_both_gram_endpoints() -> None:
    assert geometry_run.boundary(0.0, "gram")
    assert geometry_run.boundary(geometry.THETA_MAX, "gram")
    assert not geometry_run.boundary(0.1, "gram")
    assert geometry_run.boundary(-0.99, "spatial")
    assert geometry_run.boundary(0.99, "spatial")
    assert not geometry_run.boundary(0.0, "spatial")


def test_construct_inventory_preserves_unit_geometry_and_direct_constant_coordinate() -> None:
    rng = np.random.default_rng(47)
    tickers = tuple(f"firm{index:02}" for index in range(16))
    states = {name: rng.normal(size=(len(tickers), 6)) for name in FOUNDATION_READOUTS}
    for name in states:
        if name.startswith("kumo_random"):
            states[name] = np.ones((len(tickers), 6))
    target = rng.normal(size=(len(tickers), FACTORS)) + 2
    calibration = Targets(reference={FACTORS: target}, covariance=target)
    grams, distances = geometry_run.construct(
        histories(tickers), 2020, tickers, states, calibration
    )

    assert len(grams) == 31
    assert set(grams) == set(distances) == set(geometry_run.APPROACHES)
    assert all(f"histories__{name}" in grams for name in PRINCIPAL)
    appended = np.column_stack([states["direct"], np.ones(len(tickers))])
    assert_allclose(grams["histories__direct"], geometry.unit_gram(appended))
    assert_allclose(distances["histories__direct"], pairwise_distance(appended))
    assert not np.allclose(grams["histories__direct"], geometry.unit_gram(states["direct"]))
    for name, gram in grams.items():
        assert_allclose(gram, 1 - distances[name] ** 2 / 2, atol=1e-10)
        assert_allclose(np.diag(gram), 1)
    for suffix in ("", "43", "44"):
        assert_allclose(
            grams[f"histories@decoded__kumo_random{suffix}__late"],
            grams["histories@decoded__intercept_only"],
            atol=1e-10,
        )
        assert_allclose(grams[f"histories__kumo_random{suffix}__late"], 1)
    assert_allclose(
        grams["fernandez_joint"],
        np.mean([grams[f"fernandez_{name}"] for name in STUDY.characteristics], axis=0),
        atol=1e-12,
    )


def test_declared_comparisons_use_existing_columns_and_reset_parent() -> None:
    columns = {
        f"{approach}|{model}|{variance}"
        for approach in geometry_run.APPROACHES
        for model in ("gram", "spatial")
        for variance in ("full", "correlation")
    }
    pairs = geometry_run.declared_pairs()
    assert len(pairs) == len(set(pairs))
    assert all(left in columns and right in columns for _, left, right in pairs)
    assert sum(label == "gram vs spatial" for label, _, _ in pairs) == 62
    assert (
        "pretrained vs reset",
        "histories__tabpfn_full__late|gram|correlation",
        "histories__tabpfn_full_random43__late|gram|correlation",
    ) in pairs
    assert geometry_run.configuration()["primary_variance"] == "correlation"
    assert geometry_run.configuration()["pcoa_rank"] == 5


def test_rank_zero_descriptive_output_retains_spectrum_and_firms_without_portfolios() -> None:
    tickers = tuple(f"firm{index}" for index in range(7))
    outcomes = annual(tickers)
    saved = records()
    identity = geometry_run.describe(
        np.ones((len(tickers), len(tickers))),
        outcomes,
        histories(tickers),
        2020,
        "constant",
        saved,
    )
    assert identity[0] == tickers
    assert identity[1].shape == (len(tickers), 0)
    summary = saved["pcoa-summary"][0]
    assert summary["rank"] == summary["positive_rank"] == 0
    assert summary["rank_shortfall"] is True
    assert summary["variance_share"] == summary["max_gross_weight"] == 0
    assert summary["raw_reconstruction_share"] == summary["residual_reconstruction_share"] == 0
    assert len(saved["spectrum"]) == len(saved["coordinates"]) == len(tickers)
    assert len(saved["weights"]) == len(tickers)
    assert saved["component-returns"] == saved["component-covariance"] == []
    assert saved["characteristic-associations"] == saved["extremes"] == []


def test_rank_five_descriptive_outputs_reproduce_portfolios_and_projection() -> None:
    rng = np.random.default_rng(106)
    tickers = tuple(f"firm{index:02}" for index in range(12))
    outcomes = annual(tickers)
    characteristics = histories(tickers)
    characteristics.loc[(2019, slice(None)), STUDY.characteristics[0]] = 1
    gram = geometry.unit_gram(rng.normal(size=(len(tickers), 8)))
    saved = records()
    _, coordinates = geometry_run.describe(gram, outcomes, characteristics, 2020, "unit", saved)
    weight_frame = pd.DataFrame(saved["weights"]).set_index("ticker").loc[list(tickers)]
    weights = weight_frame[[f"component_{index}" for index in range(1, 6)]].to_numpy(dtype=float)
    assert_allclose(weights.T @ coordinates, np.eye(5), atol=1e-12)
    assert_allclose(weights.sum(axis=0), 0, atol=1e-12)
    raw, residual = outcomes.raw_realized @ weights, outcomes.realized @ weights
    returned = pd.DataFrame(saved["component-returns"])
    assert_allclose(
        returned.pivot_table(index="date", columns="component", values="excess"), raw, atol=1e-14
    )
    assert_allclose(
        returned.pivot_table(index="date", columns="component", values="residual"),
        residual,
        atol=1e-14,
    )
    covariances = pd.DataFrame(saved["component-covariance"])
    assert_allclose(
        covariances.pivot_table(index="component", columns="other", values="excess_covariance"),
        np.cov(raw, rowvar=False),
        atol=1e-14,
    )
    summary = saved["pcoa-summary"][0]
    assert summary["rank"] == 5
    assert summary["positive_rank"] == 8
    assert summary["rank_shortfall"] is False
    assert 0 < summary["variance_share"] < 1
    assert summary["raw_reconstruction_share"] == pytest.approx(
        1
        - np.sum((outcomes.raw_realized - raw @ coordinates.T) ** 2)
        / np.sum(outcomes.raw_realized**2)
    )
    assert summary["max_gross_weight"] == pytest.approx(np.abs(weights).sum(axis=0).max())
    associations = pd.DataFrame(saved["characteristic-associations"])
    assert (
        associations.loc[associations["characteristic"] == STUDY.characteristics[0], "spearman"]
        .isna()
        .all()
    )
    assert len(saved["extremes"]) == 50
    assert len(saved["component-returns"]) == len(outcomes.dates) * 5


def test_subspace_stability_ignores_rotations_translation_and_firm_order() -> None:
    rng = np.random.default_rng(46)
    tickers = tuple(f"firm{index:02}" for index in range(15))
    coordinates = rng.normal(size=(len(tickers), 5))
    rotation, _ = np.linalg.qr(rng.normal(size=(5, 5)))
    order = rng.permutation(len(tickers))
    transformed = (coordinates @ rotation + np.arange(5))[order]
    result = geometry_run.stability(
        (tickers, coordinates),
        (tuple(tickers[index] for index in order), transformed),
        2020,
        "unit",
    )
    assert result["common_firms"] == len(tickers)
    assert result["previous_rank"] == result["current_rank"] == 5
    assert result["maximum_angle_radians"] < 1e-12
    assert result["mean_squared_cosine"] == pytest.approx(1)
    empty = geometry_run.stability(
        (tickers, np.zeros((len(tickers), 0))), (tickers, coordinates), 2020, "unit"
    )
    assert empty["previous_rank"] == 0
    assert np.isnan(empty["mean_squared_cosine"])


def test_reconciliation_checks_scores_and_dates(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    rng = np.random.default_rng(102)
    names = (*geometry_run.CLASSICAL, *(f"histories__{name}" for name in FOUNDATION_READOUTS))
    index = pd.Index(["2020-01-02", "2020-01-03", "2020-01-06"], name="date")
    original: dict[str, FloatArray] = {}
    current: dict[str, FloatArray] = {}
    for name in names:
        kernel = "exp" if name in geometry_run.CLASSICAL else "matched"
        for variance, innovation in (("full", "diagonal"), ("correlation", "correlation")):
            values = rng.normal(size=len(index))
            original[f"{name}|{kernel}|{innovation}"] = values
            current[f"{name}|spatial|{variance}"] = values.copy()
    pd.DataFrame(original, index=index).to_parquet(tmp_path / "daily-scores.parquet")
    monkeypatch.setattr(geometry_run, "STUDY", replace(STUDY, output=tmp_path))
    daily = pd.DataFrame(current, index=index)
    results = geometry_run.reconcile(daily)
    assert len(results) == len(names) * 2
    assert all(row["max_daily_error"] == 0 for row in results)
    changed = daily + 0.01
    with pytest.raises(AssertionError):
        geometry_run.reconcile(changed)
    with pytest.raises(ValueError, match="dates differ"):
        geometry_run.reconcile(daily.set_axis(index[::-1]))
