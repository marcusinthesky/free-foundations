"""Economic invariants and filing-time leakage checks for the research pilot."""

import numpy as np
import pandas as pd
from hypothesis import given
from hypothesis import strategies as st
from numpy.testing import assert_allclose

from free_foundations.contracts import FloatArray
from free_foundations.pilot.data import fact_rows
from free_foundations.pilot.features import select_facts
from free_foundations.pilot.spatial import fit_spatial, history_weights, kernel_weights
from tests.strategies import token_arrays


@given(token_arrays())
def test_kernel_invariant_to_common_scale_and_reflection(values: FloatArray) -> None:
    vectors = values.reshape(values.shape[0], -1)
    if len(vectors) < 2:
        return
    weights = kernel_weights(vectors)
    assert_allclose(weights.sum(axis=1), 1)
    assert_allclose(weights.diagonal(), 0)
    assert_allclose(weights, kernel_weights(vectors * 2), atol=1e-12)
    assert_allclose(weights, kernel_weights(-vectors), atol=1e-12)


def test_future_restatement_and_quarter_flow_are_excluded() -> None:
    rows = [
        ("Assets", None, "2019-12-31", "2020-02-01", 100),
        ("Assets", None, "2019-12-31", "2021-02-01", 900),
        ("NetIncomeLoss", "2019-01-01", "2019-12-31", "2020-02-01", 10),
        ("NetIncomeLoss", "2020-07-01", "2020-09-30", "2020-11-01", 80),
    ]
    facts = pd.DataFrame(rows, columns=["tag", "start", "end", "filed", "val"])
    for column in ("start", "end", "filed"):
        facts[column] = pd.to_datetime(facts[column])
    result = select_facts(facts, pd.Timestamp("2020-12-31")).set_index("feature")
    assert result.loc["assets", "val"] == 100
    assert result.loc["income", "val"] == 10


@given(st.integers(0, 100))
def test_spatial_covariance_and_fit_are_permutation_equivariant(seed: int) -> None:
    rng = np.random.default_rng(seed)
    weights = kernel_weights(rng.normal(size=(6, 3)))
    operator = np.eye(6) - 0.5 * weights
    residuals = rng.normal(size=(1000, 6)) @ np.linalg.inv(operator).T
    fitted = fit_spatial(weights, residuals)
    permutation = rng.permutation(6)
    permuted = fit_spatial(weights[np.ix_(permutation, permutation)], residuals[:, permutation])
    assert np.linalg.eigvalsh(fitted.covariance).min() > 0
    assert abs(fitted.intensity - 0.5) < 0.15
    assert_allclose(
        permuted.covariance, fitted.covariance[np.ix_(permutation, permutation)], atol=1e-7
    )


def test_history_network_uses_rank_correlation() -> None:
    history = np.array([[1.0, 2.0, 3.0, 4.0], [3.0, 4.0, 5.0, 6.0], [4.0, 3.0, 2.0, 1.0]])
    weights = history_weights(history)
    assert weights[0, 1] > weights[0, 2]
    assert_allclose(weights, history_weights(np.exp(history)))


def test_empty_or_foreign_only_facts_have_a_valid_empty_schema() -> None:
    facts = fact_rows(
        {
            "facts": {
                "us-gaap": {
                    "Assets": {
                        "units": {
                            "USD": [
                                {
                                    "form": "20-F",
                                    "val": 100,
                                    "end": "2024-12-31",
                                    "filed": "2025-03-01",
                                }
                            ]
                        }
                    }
                }
            }
        }
    )
    assert facts.empty
    assert select_facts(facts, pd.Timestamp("2025-12-31")).empty
