"""Quarter resampling schedules, percentile intervals and Holm adjustment."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from free_foundations.study.inference import (
    generated_beta_indices,
    holm,
    percentile_interval,
    stationary_orders,
)


@pytest.mark.unit
def test_holm_matches_hand_computed_step_down_values() -> None:
    # Arrange
    pvalues = pd.Series([0.01, 0.04, 0.03, np.nan], index=list("abcd"))

    # Act
    adjusted = holm(pvalues)

    # Assert: 3 x 0.01, max(0.03, 2 x 0.03), max(0.06, 1 x 0.04); NaN stays NaN.
    np.testing.assert_allclose(adjusted[["a", "c", "b"]], [0.03, 0.06, 0.06])
    assert np.isnan(adjusted["d"])


@pytest.mark.unit
def test_stationary_orders_stay_on_the_calendar_and_are_reproducible() -> None:
    # Act
    first = stationary_orders(40, 50, 3.5, 42)
    second = stationary_orders(40, 50, 3.5, 42)

    # Assert
    assert first.shape == (50, 40)
    assert first.min() >= 0
    assert first.max() < 40
    np.testing.assert_array_equal(first, second)


@pytest.mark.unit
def test_generated_indices_keep_the_original_calendar_as_replicate_zero() -> None:
    # Arrange
    quarters = pd.date_range("2016-03-31", periods=8, freq="QE")

    # Act
    indices = generated_beta_indices(quarters, 5, 2.0, 1)

    # Assert
    original = indices.loc[indices["replicate"].eq(0), "quarter"].tolist()
    assert original == list(quarters.strftime("%Y-%m-%d"))
    assert indices["replicate"].nunique() == 6


@pytest.mark.unit
def test_percentile_interval_ignores_failed_draws() -> None:
    # Arrange
    values = np.r_[np.arange(101.0), np.nan]

    # Act
    low, high, count = percentile_interval(values)

    # Assert
    assert (low, high, count) == (2.5, 97.5, 101)
