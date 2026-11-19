"""Selection uses same-rung gains and requires the full set of valid fits."""

from dataclasses import replace

import numpy as np
import pytest

from free_foundations.methods.matched_panel import Period, fit
from free_foundations.study.experiments.matched_encoders import select_winner


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
