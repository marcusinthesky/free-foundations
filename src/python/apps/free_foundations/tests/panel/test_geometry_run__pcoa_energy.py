"""Denominators and return-independent references for centered characteristic projections."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from free_foundations.panel import geometry, geometry_run

from .test_geometry_run import annual, histories, records


def test_uniform_returns_change_total_share_but_not_relative_projection() -> None:
    rng = np.random.default_rng(812)
    vectors = rng.normal(size=(12, 3))
    vectors -= vectors.mean(axis=0)
    basis, _ = np.linalg.qr(vectors)
    values = rng.normal(size=(80, 12))
    values -= values.mean(axis=1, keepdims=True)
    projected = values @ basis @ basis.T
    first = geometry_run.energy_diagnostics(values, projected)
    shifted = values + rng.normal(0, 8, (len(values), 1))
    second_projection = shifted @ basis @ basis.T
    second = geometry_run.energy_diagnostics(shifted, second_projection)
    assert_allclose(projected, second_projection, atol=1e-13)
    assert second["reconstruction_share"] < first["reconstruction_share"]
    assert second["relative_reconstruction_share"] == pytest.approx(
        first["relative_reconstruction_share"]
    )
    assert first["relative_energy_share"] == pytest.approx(1)
    assert second["relative_energy_share"] < 0.1
    assert second["reconstruction_share"] == pytest.approx(
        second["relative_reconstruction_share"] * second["relative_energy_share"], abs=1e-14
    )


def test_zero_energy_and_uniform_only_denominators_are_undefined() -> None:
    zero = np.zeros((10, 7))
    result = geometry_run.energy_diagnostics(zero, zero)
    assert not result["energy_defined"]
    assert not result["relative_defined"]
    for key in ("reconstruction_share", "relative_reconstruction_share", "relative_energy_share"):
        assert np.isnan(result[key])
    uniform = np.full((10, 7), 0.25)
    result = geometry_run.energy_diagnostics(uniform, zero)
    assert result["energy_defined"]
    assert not result["relative_defined"]
    assert result["reconstruction_share"] == result["relative_energy_share"] == 0
    assert np.isnan(result["relative_reconstruction_share"])


def test_random_reference_is_rank_matched_and_permutation_and_scale_invariant() -> None:
    tickers = tuple(f"firm{index:02}" for index in range(12))
    outcomes = annual(tickers)
    first = geometry_run.random_reference(outcomes, 5)
    order = np.arange(len(tickers))[::-1]
    permuted = replace(
        outcomes,
        tickers=tuple(tickers[index] for index in order),
        raw_realized=outcomes.raw_realized[:, order] * 3,
        realized=outcomes.realized[:, order] * 4,
    )
    second = geometry_run.random_reference(permuted, 5)
    assert_allclose(list(first.values()), list(second.values()), atol=1e-14)
    assert first["random_relative_expectation"] == pytest.approx(5 / 11)
    for prefix in ("raw", "residual"):
        assert first[f"{prefix}_random_relative_lower"] <= first[f"{prefix}_random_relative_mean"]
        assert first[f"{prefix}_random_relative_mean"] <= first[f"{prefix}_random_relative_upper"]
        assert first[f"{prefix}_random_relative_mean"] == pytest.approx(5 / 11, abs=0.04)


def test_random_reference_retains_zero_rank_and_undefined_energy() -> None:
    outcomes = annual(tuple("ABCDEFG"))
    result = geometry_run.random_reference(outcomes, 0)
    assert all(value == 0 for value in result.values())
    uniform = replace(outcomes, raw_realized=np.full_like(outcomes.raw_realized, 0.25))
    result = geometry_run.random_reference(uniform, 4)
    assert np.isnan(result["raw_random_relative_mean"])
    assert result["residual_random_relative_mean"] > 0
    with pytest.raises(ValueError, match="rank"):
        geometry_run.random_reference(outcomes, 7)


def test_description_records_energy_identity_and_nonunique_cutoff() -> None:
    tickers = tuple(f"firm{index:02}" for index in range(12))
    outcomes = annual(tickers)
    saved = records()
    geometry_run.describe(np.eye(12), outcomes, histories(tickers), 2020, "tied", saved)
    summary = saved["pcoa-summary"][0]
    assert summary["rank"] == 5
    assert summary["cutoff_tied"]
    assert not summary["subspace_unique"]
    assert summary["random_relative_expectation"] == pytest.approx(5 / 11)
    for prefix in ("raw", "residual"):
        assert summary[f"{prefix}_reconstruction_share"] == pytest.approx(
            summary[f"{prefix}_relative_reconstruction_share"]
            * summary[f"{prefix}_relative_energy_share"],
            abs=1e-14,
        )
        assert summary[f"{prefix}_projected_energy"] <= summary[f"{prefix}_relative_energy"]


def test_reference_draws_are_shared_for_matching_cohort_and_rank() -> None:
    tickers = tuple(f"firm{index:02}" for index in range(12))
    outcomes = annual(tickers)
    saved = records()
    rng = np.random.default_rng(17)
    references: dict[int, dict[str, float]] = {}
    for label in ("first", "second"):
        gram = geometry.unit_gram(rng.normal(size=(len(tickers), 8)))
        geometry_run.describe(
            gram, outcomes, histories(tickers), 2020, label, saved, references=references
        )
    frame = pd.DataFrame(saved["pcoa-summary"])
    assert set(references) == {5}
    assert frame["raw_random_relative_mean"].eq(frame["raw_random_relative_mean"].iloc[0]).all()
    assert frame["raw_random_relative_lower"].eq(frame["raw_random_relative_lower"].iloc[0]).all()
