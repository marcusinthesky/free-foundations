"""Reference tests for matched quarterly Gaussian likelihoods."""

import numpy as np
import pytest

from free_foundations.methods.matched_panel import Period, Process, fit


@pytest.mark.unit
@pytest.mark.parametrize("process", ["none", "lag", "error"])
def test_likelihood_matches_explicit_quarter_intercepts(process: Process) -> None:
    # Arrange
    rng = np.random.default_rng(42)
    outcomes = [rng.normal(size=n) for n in (7, 9, 12)]
    designs = [rng.normal(size=(len(y), 2)) for y in outcomes]
    weights = []
    for y in outcomes:
        raw = rng.uniform(size=(len(y), len(y)))
        adjacency = raw + raw.T
        np.fill_diagonal(adjacency, 0)
        weights.append(adjacency / adjacency.sum(axis=1, keepdims=True))

    # Act
    result = fit(
        [Period.of(y, x, w) for y, x, w in zip(outcomes, designs, weights, strict=True)],
        process,
    )

    # Assert
    transformed_outcomes = []
    transformed_designs = []
    determinants = []
    for idx, (y, x, w) in enumerate(zip(outcomes, designs, weights, strict=True)):
        transform = np.eye(len(y)) - result.spatial * w
        indicators = np.zeros((len(y), len(outcomes)))
        indicators[:, idx] = 1
        transformed_outcomes.append(transform @ y)
        transformed_designs.append(
            np.column_stack((transform @ x if process == "error" else x, indicators))
        )
        determinants.append(np.linalg.slogdet(transform)[1])
    design = np.vstack(transformed_designs)
    outcome = np.concatenate(transformed_outcomes)
    coefficients = np.linalg.lstsq(design, outcome, rcond=None)[0]
    errors = outcome - design @ coefficients
    variance = np.mean(errors**2)
    expected = sum(determinants) - len(outcome) / 2 * (np.log(2 * np.pi * variance) + 1)
    np.testing.assert_allclose(result.coefficients, coefficients[:2])
    assert result.loglik == pytest.approx(expected)
    assert result.contributions.sum() == pytest.approx(expected)
    assert result.parameters == 2 + len(outcomes) + 1 + (process != "none")
    assert result.aic == pytest.approx(2 * result.parameters - 2 * expected)


@pytest.mark.unit
def test_quarter_constant_regressor_fails_rank_check() -> None:
    # Arrange
    one = Period.of(np.arange(6, dtype=float), np.ones((6, 1)))
    two = Period.of(np.arange(7, dtype=float), np.full((7, 1), 2.0))

    # Act and assert
    with pytest.raises(ValueError, match="rank deficient"):
        fit([one, two], "none")


@pytest.mark.unit
def test_graph_reversibility_rejects_directional_cycle() -> None:
    # Arrange
    weights = np.array([[0, 0.6, 0.4], [0.4, 0, 0.6], [0.6, 0.4, 0]])

    # Act and assert
    with pytest.raises(ValueError, match="reversible"):
        Period.of(np.arange(3, dtype=float), np.ones((3, 1)), weights)
