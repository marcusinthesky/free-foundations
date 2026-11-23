"""Dated operands retain the accounting roles used by the ratios."""

import json

import pandas as pd
import pytest

from free_foundations.study.panel.matched_operands import operand_history, operand_snapshots


@pytest.mark.component
def test_annual_operands_keep_distinct_market_equity_dates_and_debt_fallback() -> None:
    # Arrange
    prior = pd.Timestamp("2015-03-31")
    query = pd.Timestamp("2016-03-31")
    evidence = {
        "market_cap_assets": (0.5, {"IssuerMarketEquity": 50, "Assets": 100}),
        "dividend_yield": (0.05, {"IssuerMarketEquity": 40, "PaymentsOfDividends": 2}),
        "debt_maturity": (0.8, {"LongTermDebt": 50, "LongTermDebtCurrent": 10}),
        "market_to_book": (float("nan"), {"IssuerMarketEquity": 50, "StockholdersEquity": -20}),
    }
    facts = pd.DataFrame(
        [
            {
                "issuer_id": "A",
                "quarter": prior,
                "characteristic": group,
                "value": ratio,
                "components": json.dumps(
                    [{"concept": f"tag:{tag}", "value": value} for tag, value in sources.items()]
                ),
            }
            for group, (ratio, sources) in evidence.items()
        ]
    )
    roster = pd.DataFrame({"issuer_id": ["A", "B"], "quarter": [query, query]})

    # Act
    result = operand_history(roster, operand_snapshots(facts), years=2)

    # Assert
    assert result.index.tolist() == [("A", query), ("B", query)]
    assert result.loc[("A", query), "operands:shared:market_equity_balance_sheet:annual_lag1"] == 50
    assert (
        result.loc[("A", query), "operands:dividend_yield:market_equity_dividend_year:annual_lag1"]
        == 40
    )
    assert result.loc[("A", query), "operands:debt_maturity:noncurrent_debt:annual_lag1"] == 40
    assert result.loc[("A", query), "operands:debt_maturity:total_debt:annual_lag1"] == 50
    assert result.loc[("A", query), "operands:market_to_book:parent_equity:annual_lag1"] == -20
    assert pd.isna(result.loc[("A", query), "operands:debt_maturity:total_debt:annual_lag0"])
    assert result.iloc[1].isna().all()
