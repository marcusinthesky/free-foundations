"""Selection and broad-input factor contrasts share one fixed quarterly sample."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.methods.matched_panel import Period, fit
from free_foundations.methods.networks import knn_weights, representation_distance
from free_foundations.study.experiments import matched_encoders
from free_foundations.study.experiments.matched_encoders import select_winner
from free_foundations.study.experiments.matched_panel import (
    FACTOR_SETS,
    NEIGHBOURS,
    RUNG_ORDER,
    Sample,
    SampleQuarter,
    compare,
)
from free_foundations.study.spec import StudySpec

if TYPE_CHECKING:
    from pathlib import Path

    from numpy.typing import NDArray

    from free_foundations.encoders.contracts import FloatArray
    from free_foundations.methods.matched_panel import Fit
    from free_foundations.methods.spatial_ml import Graph


@pytest.mark.unit
def test_likelihood_gain_ranks_against_each_rungs_direct_control() -> None:
    # Arrange
    result = fit([Period.of(np.array([0.0, 1.0, 3.0]), np.zeros((3, 0)))], "none")
    first = ("fernandez", "tabpfn_full")
    second = ("operands", "tabfm")
    order = (first, second)
    estimates = {
        first: replace(result, loglik=100.0),
        second: replace(result, loglik=50.0),
        ("fernandez", "direct"): replace(result, loglik=97.0),
        ("operands", "direct"): replace(result, loglik=44.0),
    }

    # Act
    winner = select_winner(order, estimates)

    # Assert
    assert winner == (second, pytest.approx(2.0))


@pytest.mark.unit
@pytest.mark.parametrize("invalid_fit", ["unavailable", "boundary", "flat"])
@pytest.mark.parametrize("invalid_model", ["direct", "tabfm"])
def test_any_invalid_fit_blocks_selection(invalid_fit: str, invalid_model: str) -> None:
    # Arrange
    result = fit([Period.of(np.array([0.0, 1.0, 3.0]), np.zeros((3, 0)))], "none")
    first = ("fernandez", "tabpfn_full")
    second = ("operands", "tabfm")
    order = (first, second)
    estimates = {
        first: result,
        second: result,
        ("fernandez", "direct"): result,
        ("operands", "direct"): result,
    }
    invalid = ("operands", invalid_model)
    if invalid_fit == "unavailable":
        del estimates[invalid]
    else:
        estimates[invalid] = replace(
            result, boundary=invalid_fit == "boundary", flat_profile=invalid_fit == "flat"
        )

    # Act and assert
    assert select_winner(order, estimates) is None


@pytest.mark.unit
def test_tie_tolerance_is_in_nats_per_observation() -> None:
    # Arrange
    result = fit([Period.of(np.array([0.0, 1.0, 3.0]), np.zeros((3, 0)))], "none")
    first = ("fernandez", "tabpfn_full")
    second = ("fernandez", "tabfm")
    order = (first, second)
    estimates = {
        first: replace(result, loglik=11.0),
        second: replace(result, loglik=11.0 + 2e-8),
        ("fernandez", "direct"): replace(result, loglik=8.0),
    }

    # Act and assert
    assert select_winner(order, estimates) == (first, pytest.approx(1.0))


@pytest.mark.unit
def test_paired_interval_weights_each_resampled_issuer_quarter() -> None:
    # Arrange
    periods = [Period.of(np.arange(n, dtype=float), np.zeros((n, 0))) for n in (3, 5)]
    baseline = fit(periods, "none")
    candidate = replace(baseline, contributions=baseline.contributions + np.array([3.0, 15.0]))
    orders = np.array([[0, 0], [1, 1], [1, 0]])

    # Act
    result = compare(candidate, baseline, orders)

    # Assert
    assert result["gain_per_observation"] == pytest.approx(18 / 8)
    expected = np.percentile([1, 3, 18 / 8], [2.5, 97.5])
    assert result["low_per_observation"] == pytest.approx(expected[0])
    assert result["high_per_observation"] == pytest.approx(expected[1])


@dataclass
class EncoderCase:
    sample: Sample
    sample_path: Path
    params: Path
    cells: Path
    output: Path
    states: dict[tuple[str, str], FloatArray]
    orders: NDArray[np.int64]
    graph_calls: list[FloatArray]


@pytest.fixture
def encoder_case(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> EncoderCase:
    params = tmp_path / "params.yaml"
    params.write_text(
        'study:\n  version: crsp-sec-quarterly-v2\n  archive_end: "2011-09-30"\n'
        "  models: [tabpfn_full]\n  likelihood_draws: 6\n"
    )
    spec = StudySpec.read(params)
    rng = np.random.default_rng(41)
    quarters = []
    for date, count in zip(spec.panel_calendar, (15, 18, 21), strict=True):
        columns = rng.normal(size=(count, 6))
        design = {
            name: columns[:, : len(FACTOR_SETS[name])]
            for name in matched_encoders.BROAD_FACTOR_SETS
        }
        quarters.append(
            SampleQuarter(
                date,
                spec.panel_calendar[0],
                tuple(f"issuer{i:02d}" for i in range(count)),
                columns @ np.arange(1.0, 7.0) / 10 + rng.normal(size=count),
                design,
            )
        )
    sample_path = tmp_path / "sample"
    sample_path.mkdir()
    (sample_path / "manifest.json").write_text("{}")
    sample = Sample(
        tuple(quarters),
        np.array([0.1, -0.2, 0.05]),
        spec,
        {"mask_sha256": "common-mask", "panel_sha256": "common-panel"},
    )
    states = {
        (rung, model): rng.normal(size=(21, 5))
        for rung in RUNG_ORDER
        for model in ("direct", "tabpfn_full")
    }
    orders = np.array([[0, 0, 0], [1, 1, 1], [2, 2, 2], [0, 1, 2], [2, 0, 1], [2, 2, 0]])
    graph_calls: list[FloatArray] = []
    case = EncoderCase(
        sample,
        sample_path,
        params,
        tmp_path / "cells",
        tmp_path / "results",
        states,
        orders,
        graph_calls,
    )

    def load_sample(_path: Path, _params: Path) -> Sample:
        return sample

    def load_cell(cell: Path, formation: pd.Timestamp, issuers: tuple[str, ...]) -> FloatArray:
        assert formation == sample.quarters[0].formation
        assert issuers == tuple(f"issuer{i:02d}" for i in range(len(issuers)))
        return states[cell.parent.name, cell.name][: len(issuers)]

    def manifest(_cell: Path, _sample: Sample) -> str:
        return "verified-cell"

    def orders_for(_sample: Sample) -> tuple[NDArray[np.int64], float]:
        return orders, 2.0

    prepare_graph = matched_encoders.prepare_graph

    def graph(weights: FloatArray) -> Graph:
        graph_calls.append(weights.copy())
        return prepare_graph(weights)

    monkeypatch.setattr(matched_encoders, "load_sample", load_sample)
    monkeypatch.setattr(matched_encoders, "load_cell", load_cell)
    monkeypatch.setattr(matched_encoders, "cell_manifest_hash", manifest)
    monkeypatch.setattr(matched_encoders, "orders_for", orders_for)
    monkeypatch.setattr(matched_encoders, "prepare_graph", graph)
    return case


def _independent_fit(case: EncoderCase, rung: str, model: str, control: str) -> Fit:
    return fit(
        [
            Period.of(
                quarter.outcome,
                quarter.design[control],
                knn_weights(
                    representation_distance(case.states[rung, model][: len(quarter.issuers)]),
                    NEIGHBOURS,
                ),
            )
            for quarter in case.sample.quarters
        ],
        "lag",
    )


@pytest.mark.integration
def test_broad_factor_contrasts_hold_graphs_and_observations_fixed(
    encoder_case: EncoderCase,
) -> None:
    # Arrange
    case = encoder_case
    observations = sum(len(quarter.issuers) for quarter in case.sample.quarters)

    # Act
    matched_encoders.run(case.sample_path, case.cells, case.output, case.params)

    # Assert
    comparisons = pd.read_parquet(case.output / "comparisons.parquet")
    fits = pd.read_parquet(case.output / "fits.parquet")
    contributions = pd.read_parquet(case.output / "contributions.parquet")
    assert not comparisons.duplicated(["cell", "reference", "process"]).any()
    assert len(case.graph_calls) == len(RUNG_ORDER) * 2 * len(case.sample.quarters)
    assert fits.loc[fits.status.eq("available"), "observations"].eq(observations).all()
    assert len(fits) == 20  # Original twelve process fits plus eight richer-control fits.
    for control in matched_encoders.BROAD_FACTOR_SETS:
        prefix = "" if control == "market" else f"{control}|"
        candidate = f"{prefix}standard_xbrl:tabpfn_full"
        reference = f"{prefix}standard_xbrl:direct"
        row = comparisons.loc[comparisons.cell.eq(candidate) & comparisons.process.eq("lag")].iloc[
            0
        ]
        expected = compare(
            _independent_fit(case, "standard_xbrl", "tabpfn_full", control),
            _independent_fit(case, "standard_xbrl", "direct", control),
            case.orders,
        )
        assert row.reference == reference
        assert row.factor_set == control
        assert row.status == "available"
        for key in ("gain_per_observation", "low_per_observation", "high_per_observation"):
            assert row[key] == pytest.approx(expected[key])
        periods = contributions.loc[
            contributions.cell.eq(candidate) & contributions.process.eq("lag")
        ]
        assert periods.quarter.tolist() == [quarter.quarter for quarter in case.sample.quarters]
        assert periods.observations.tolist() == [15, 18, 21]
    manifest = json.loads((case.output / "manifest.json").read_text())
    assert manifest["mask_sha256"] == "common-mask"
    assert manifest["broad_factor_comparison"]["factor_sets"] == {
        name: list(FACTOR_SETS[name]) for name in matched_encoders.BROAD_FACTOR_SETS
    }
    market_estimates = {
        (rung, model): _independent_fit(case, rung, model, "market")
        for rung in RUNG_ORDER
        for model in ("direct", "tabpfn_full")
    }
    winner = select_winner(tuple((rung, "tabpfn_full") for rung in RUNG_ORDER), market_estimates)
    selection = json.loads((case.output / "selection.json").read_text())
    if winner is None:
        assert selection["status"] == "unavailable"
    else:
        (rung, model), gain = winner
        assert selection["status"] == "selected"
        assert (selection["rung"], selection["model"]) == (rung, model)
        assert selection["gain_per_observation"] == pytest.approx(gain)


@pytest.mark.integration
@pytest.mark.parametrize("missing_model", ["direct", "tabpfn_full"])
def test_missing_broad_quarter_makes_every_factor_contrast_unavailable(
    encoder_case: EncoderCase, monkeypatch: pytest.MonkeyPatch, missing_model: str
) -> None:
    # Arrange
    case = encoder_case
    original_load = matched_encoders.load_cell

    def load_cell(
        cell: Path, formation: pd.Timestamp, issuers: tuple[str, ...]
    ) -> FloatArray | None:
        if (
            cell.parent.name == "standard_xbrl"
            and cell.name == missing_model
            and len(issuers) == 18
        ):
            return None
        return original_load(cell, formation, issuers)

    monkeypatch.setattr(matched_encoders, "load_cell", load_cell)

    # Act
    matched_encoders.run(case.sample_path, case.cells, case.output, case.params)

    # Assert
    comparisons = pd.read_parquet(case.output / "comparisons.parquet")
    broad = comparisons.loc[comparisons.rung.eq("standard_xbrl")]
    assert len(broad) == 6
    assert broad.status.eq("unavailable").all()
    assert set(broad.factor_set) == set(matched_encoders.BROAD_FACTOR_SETS)
    fits = pd.read_parquet(case.output / "fits.parquet")
    missing = fits.loc[fits.rung.eq("standard_xbrl") & fits.model.eq(missing_model)]
    assert missing.status.eq("unavailable").all()
    assert missing.reason.str.contains("representation unavailable").all()
    contributions = pd.read_parquet(case.output / "contributions.parquet")
    assert not (
        contributions.rung.eq("standard_xbrl") & contributions.model.eq(missing_model)
    ).any()
