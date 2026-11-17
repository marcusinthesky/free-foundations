"""Paper-equation checks and data conventions that prevent misleading replications."""

import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st
from numpy.testing import assert_allclose

from free_foundations.fernandez.characteristics import history_view, snapshot
from free_foundations.fernandez.models import (
    lag_iv,
    paper_weights,
    rank_distance,
)


@given(st.permutations([0.0, 1.0, 2.0, 3.0]))
def test_history_distance_is_rank_invariant_and_constants_are_rejected(order: list[float]) -> None:
    histories = np.array([order, [3, 2, 1, 0], [1, 3, 0, 2]], dtype=float)
    distance = rank_distance(histories)
    assert_allclose(distance, rank_distance(np.exp(histories)))
    assert_allclose(distance, distance.T)
    assert_allclose(distance.diagonal(), 0)
    weights = paper_weights(distance)
    assert_allclose(weights.sum(axis=1), 1)
    assert_allclose(weights.diagonal(), 0)
    assert (paper_weights(distance, self_links=True).diagonal() > 0).all()
    with pytest.raises(ValueError, match="Constant"):
        rank_distance(np.ones((3, 4)))


def test_spatial_iv_recovers_the_structural_coefficient_without_ols_endogeneity() -> None:
    rng = np.random.default_rng(42)
    weights = paper_weights(rank_distance(rng.normal(size=(30, 10))))
    beta = rng.uniform(0.5, 1.5, (30, 1))
    returns = np.linalg.solve(np.eye(30) - 0.7 * weights, 0.02 * beta[:, 0])
    fit = lag_iv(returns, beta, weights)
    assert_allclose([fit.premium, fit.intensity], [0.02, 0.7], atol=1e-10)
    assert_allclose(fit.innovations, 0, atol=1e-10)


def test_missing_debt_is_not_zero_and_histories_never_pull_forward() -> None:
    period = pd.Timestamp("2020-12-31")
    facts = pd.DataFrame(
        {
            "tag": [
                "Assets",
                "StockholdersEquity",
                "CommonStockSharesOutstanding",
                "LongTermDebtNoncurrent",
            ],
            "val": [100, 50, 10, 20],
            "end": period,
            "filed": pd.Timestamp("2021-02-01"),
            "accn": "a",
        }
    )
    market = pd.DataFrame(
        {
            "Close": [5.0],
            "historical_close": [5.0],
            "trailing_dividends": [0.0],
            "Stock Splits": [0.0],
        },
        index=[period],
    )
    result = snapshot(facts, market)
    assert result["market_to_book"] == 1
    assert np.isnan(result["debt_maturity"])
    index = pd.MultiIndex.from_product([[2020, 2021, 2022], ["A"]], names=["year", "ticker"])
    history = history_view(pd.DataFrame({"x": [1, 2, 999]}, index=index), 2)
    assert_allclose(history.loc[[(2021, "A")]].to_numpy()[0], [2, 1])


def test_var_zero_spatial_limit_and_market_risk_transmission() -> None:
    from free_foundations.fernandez.simulation import portfolio_var  # noqa: PLC0415

    # Symmetric row-stochastic W makes the equal-weight portfolio an eigenvector.
    weights = (np.ones((20, 20)) - np.eye(20)) / 19
    beta = np.full(20, 0.75)
    lag_zero, error_zero = portfolio_var(beta, weights, 0)
    assert_allclose(lag_zero, error_zero)
    assert_allclose(lag_zero, 1000 * 1.6448536269514722 * 0.01 * np.sqrt(0.75**2 + 1 / 20))
    lag, error = portfolio_var(beta, weights, 0.5)
    assert_allclose(lag, lag_zero / 0.5)
    assert lag > error > error_zero


def test_debt_maturity_never_mixes_lease_inclusive_and_exclusive_components() -> None:
    period = pd.Timestamp("2020-12-31")
    tags = [
        "Assets",
        "StockholdersEquity",
        "CommonStockSharesOutstanding",
        "LongTermDebtNoncurrent",
        "DebtCurrent",
    ]
    facts = pd.DataFrame(
        {
            "tag": tags,
            "val": [200, 100, 10, 80, 20],
            "end": period,
            "filed": pd.Timestamp("2021-02-01"),
            "accn": "a",
        }
    )
    market = pd.DataFrame(
        {
            "Close": [5.0],
            "historical_close": [5.0],
            "trailing_dividends": [0.0],
            "Stock Splits": [0.0],
        },
        index=[period],
    )
    # DebtCurrent includes leases; LongTermDebtNoncurrent excludes them.
    assert np.isnan(snapshot(facts, market)["debt_maturity"])
    lease = facts.iloc[[0]].assign(tag="FinanceLeaseLiabilityNoncurrent", val=10)
    consistent = snapshot(pd.concat([facts, lease], ignore_index=True), market)
    assert_allclose(float(consistent["debt_maturity"]), 90 / 110)
