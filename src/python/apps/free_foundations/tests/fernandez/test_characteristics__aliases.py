"""Conservative recovery of explicitly disclosed, balance-date-aligned components."""

import numpy as np
import pandas as pd
import pytest
from numpy.testing import assert_allclose

from free_foundations.fernandez.characteristics import (
    debt_components,
    debt_maturity_with_audit,
    parent_equity,
    snapshot,
    snapshot_with_audit,
)

PERIOD = pd.Timestamp("2020-12-31")
CONSOLIDATED_EQUITY = "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"
LONG_WITH_CURRENT = "LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities"
CURRENT_LONG = "LongTermDebtAndCapitalLeaseObligationsCurrent"


def facts(values: dict[str, float], period: pd.Timestamp = PERIOD) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "tag": list(values),
            "val": list(values.values()),
            "end": period,
            "filed": pd.Timestamp("2021-02-01"),
            "accn": "original",
            "form": "10-K",
        }
    )


def market() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Close": [5.0],
            "historical_close": [5.0],
            "trailing_dividends": [0.5],
            "Stock Splits": [0.0],
        },
        index=[PERIOD],
    )


@pytest.mark.parametrize("reported_parent", [-10.0, 0.0, 50.0])
def test_parent_equity_prefers_even_nonpositive_explicit_parent(reported_parent: float) -> None:
    observations = facts(
        {"StockholdersEquity": reported_parent, CONSOLIDATED_EQUITY: 100, "MinorityInterest": 20}
    )
    assert parent_equity(observations, PERIOD) == reported_parent


def test_parent_equity_recovery_requires_explicit_same_period_nci() -> None:
    observations = facts({CONSOLIDATED_EQUITY: 100})
    assert np.isnan(parent_equity(observations, PERIOD))
    wrong_period = facts({"MinorityInterest": 20}, PERIOD - pd.Timedelta(days=90))
    assert np.isnan(parent_equity(pd.concat([observations, wrong_period]), PERIOD))
    assert parent_equity(pd.concat([observations, facts({"MinorityInterest": 20})]), PERIOD) == 80
    # Explicit zero NCI is evidence; absence is not.
    assert parent_equity(pd.concat([observations, facts({"MinorityInterest": 0})]), PERIOD) == 100


def test_combined_debt_recovery_uses_current_part_and_explicit_short_term_debt() -> None:
    observations = facts({LONG_WITH_CURRENT: 100, CURRENT_LONG: 20, "ShortTermBorrowings": 5})
    assert_allclose(debt_components(observations, PERIOD), [80, 105])
    zero_short = observations.assign(
        val=observations["val"].where(observations["tag"].ne("ShortTermBorrowings"), 0)
    )
    assert_allclose(debt_components(zero_short, PERIOD), [80, 100])


def test_combined_debt_recovery_does_not_treat_commercial_paper_as_all_borrowing() -> None:
    observations = facts({LONG_WITH_CURRENT: 100, CURRENT_LONG: 20, "CommercialPaper": 5})
    long_debt, total_debt = debt_components(observations, PERIOD)
    assert long_debt == 80
    assert np.isnan(total_debt)
    misaligned_short = facts({"ShortTermBorrowings": 5}, PERIOD - pd.Timedelta(days=90))
    assert np.isnan(debt_components(pd.concat([observations, misaligned_short]), PERIOD)[1])


def test_current_total_can_recover_noncurrent_debt_without_lease_basis_changes() -> None:
    observations = facts({LONG_WITH_CURRENT: 100, "DebtCurrent": 25, "ShortTermBorrowings": 5})
    assert_allclose(debt_components(observations, PERIOD), [80, 105])
    exclusive = facts({"LongTermDebtNoncurrent": 80, CURRENT_LONG: 20, "ShortTermBorrowings": 5})
    assert np.isnan(debt_components(exclusive, PERIOD)[0])
    assert np.isnan(debt_components(exclusive, PERIOD)[1])


def test_existing_finite_debt_components_keep_their_priority() -> None:
    observations = facts(
        {
            "LongTermDebtNoncurrent": 70,
            "FinanceLeaseLiabilityNoncurrent": 10,
            "DebtCurrent": 20,
            LONG_WITH_CURRENT: 999,
            CURRENT_LONG: 888,
            "ShortTermBorrowings": 777,
        }
    )
    assert_allclose(debt_components(observations, PERIOD), [80, 100])


def test_negative_alternative_debt_components_cannot_cancel_into_valid_maturity() -> None:
    observations = facts(
        {
            "Assets": 200,
            "StockholdersEquity": 100,
            "CommonStockSharesOutstanding": 10,
            LONG_WITH_CURRENT: 100,
            CURRENT_LONG: -20,
            "ShortTermBorrowings": 50,
        }
    )
    # Without constituent validation, these values yield 120 / 150 despite a
    # negative amount for the current portion of long-term debt and leases.
    assert np.isnan(snapshot(observations, market())["debt_maturity"])


def test_selected_fact_audit_reconstructs_exact_ratio_components() -> None:
    observations = facts(
        {
            "Assets": 200,
            "CommonStockSharesOutstanding": 10,
            CONSOLIDATED_EQUITY: 100,
            "MinorityInterest": 20,
            LONG_WITH_CURRENT: 100,
            CURRENT_LONG: 20,
            "ShortTermBorrowings": 5,
        }
    )
    # A newer disclosure for the exact period must be the audited one.
    restated = facts({"MinorityInterest": 10}).assign(
        filed=pd.Timestamp("2021-02-15"), accn="restated", form="10-K/A"
    )
    observations = pd.concat([observations, restated], ignore_index=True)
    result, audit = snapshot_with_audit(observations, market())
    expected = {"assets": 200, "shares": 10, "equity": 90, "debt_noncurrent": 80, "debt_total": 105}
    for name, value in expected.items():
        component = audit.loc[audit["component"].eq(name)]
        assert_allclose((component["val"] * component["coefficient"]).sum(), value)
        assert_allclose(component["component_value"], value)
        assert component["end"].eq(PERIOD).all()
    nci = audit.loc[audit["component"].eq("equity") & audit["tag"].eq("MinorityInterest")]
    assert nci["accn"].tolist() == ["restated"]
    assert nci["coefficient"].tolist() == [-1.0]
    assert_allclose(float(result["market_to_book"]), 50 / 90)
    assert_allclose(float(result["debt_maturity"]), 80 / 105)
    assert result["market_date"] == "2020-12-31"
    assert result["market_historical_close"] == 5
    assert result["market_close"] == 5
    assert result["trailing_dividends"] == 0.5
    assert snapshot(observations, market()) == result


def test_same_period_debt_helper_retains_signed_evidence_without_other_snapshot_inputs() -> None:
    observations = facts(
        {LONG_WITH_CURRENT: 100, CURRENT_LONG: 20, "ShortTermBorrowings": 5}
    ).assign(form="10-Q")
    different_period = facts(
        {"DebtAndCapitalLeaseObligations": 999}, PERIOD - pd.Timedelta(days=90)
    )
    maturity, evidence = debt_maturity_with_audit(
        pd.concat([observations, different_period], ignore_index=True), PERIOD
    )
    assert maturity == pytest.approx(80 / 105)
    assert set(evidence["component"]) == {"debt_noncurrent", "debt_total"}
    assert evidence["end"].eq(PERIOD).all()
    assert evidence["form"].eq("10-Q").all()
    for component, scalar in (("debt_noncurrent", 80), ("debt_total", 105)):
        parts = evidence.loc[evidence["component"].eq(component)]
        assert_allclose((parts["coefficient"] * parts["val"]).sum(), scalar)
        assert_allclose(parts["component_value"], scalar)
    current = evidence.loc[
        evidence["component"].eq("debt_noncurrent") & evidence["tag"].eq(CURRENT_LONG)
    ]
    assert current["coefficient"].tolist() == [-1.0]


def test_same_period_debt_helper_keeps_missing_components_undefined() -> None:
    maturity, evidence = debt_maturity_with_audit(
        facts({LONG_WITH_CURRENT: 100, CURRENT_LONG: 20}), PERIOD
    )
    assert np.isnan(maturity)
    assert not evidence["tag"].eq("ShortTermBorrowings").any()
    total = evidence.loc[evidence["component"].eq("debt_total"), "component_value"]
    assert total.isna().all()
