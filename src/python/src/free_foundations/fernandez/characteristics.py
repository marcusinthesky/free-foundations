"""Auditable US analogues of the four Fernández characteristic histories."""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)
CHARACTERISTICS = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")


def at_period(facts: pd.DataFrame, tags: tuple[str, ...], period: pd.Timestamp) -> float:
    """Require the exact common balance-sheet date; never infer missing debt as zero."""
    for tag in tags:
        rows = facts.loc[(facts["tag"] == tag) & (facts["end"] == period)]
        if not rows.empty:
            return float(rows.sort_values(["filed", "accn"]).iloc[-1]["val"])
    return np.nan


def debt_components(facts: pd.DataFrame, period: pd.Timestamp) -> tuple[float, float]:
    """Return noncurrent and total debt on a consistently lease-inclusive basis."""
    # Keep both numerator and denominator on a lease-inclusive debt basis.
    long_debt = at_period(facts, ("LongTermDebtAndCapitalLeaseObligations",), period)
    if not np.isfinite(long_debt):
        debt_only = at_period(facts, ("LongTermDebtNoncurrent",), period)
        if not np.isfinite(debt_only):
            debt_only = at_period(facts, ("LongTermDebt",), period) - at_period(
                facts, ("LongTermDebtCurrent",), period
            )
        long_debt = debt_only + at_period(
            facts, ("FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent"), period
        )
    current_debt = at_period(facts, ("DebtCurrent",), period)
    if not np.isfinite(current_debt):
        current_debt = (
            at_period(facts, ("LongTermDebtCurrent",), period)
            + at_period(facts, ("ShortTermBorrowings",), period)
            + at_period(
                facts, ("FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"), period
            )
        )
    total_debt = at_period(facts, ("DebtAndCapitalLeaseObligations",), period)
    if not np.isfinite(total_debt):
        total_debt = long_debt + current_debt
    if not np.isfinite(long_debt):
        long_debt = total_debt - current_debt
    return long_debt, total_debt


def snapshot(facts: pd.DataFrame, market: pd.DataFrame) -> dict[str, float | str]:
    """Construct ratios at the latest disclosed asset period, from aligned observations."""
    assets = facts.loc[facts["tag"].eq("Assets")].sort_values(["end", "filed", "accn"])
    if assets.empty:
        return {}
    row = assets.iloc[-1]
    period = pd.Timestamp(row["end"])
    available = market.loc[:period]
    if available.empty or (period - available.index[-1]).days > 7:
        return {}
    price = available.iloc[-1]
    share_rows = facts.loc[facts["tag"].eq("EntityCommonStockSharesOutstanding")].sort_values(
        ["end", "filed"]
    )
    if share_rows.empty:
        share_rows = facts.loc[facts["tag"].eq("CommonStockSharesOutstanding")].sort_values(
            ["end", "filed"]
        )
    share_period = pd.Timestamp(share_rows.iloc[-1]["end"]) if not share_rows.empty else period
    shares = float(share_rows.iloc[-1]["val"]) if not share_rows.empty else np.nan
    share_rows = share_rows.tail(1)
    share_market = market.loc[:share_period]
    if share_market.empty:
        return {}
    price = share_market.iloc[-1]
    # A filing after a split can restate the earlier share count. Do not guess its basis.
    if not share_rows.empty:
        filed = share_rows["filed"].max()
        if (
            market.loc[(market.index > share_period) & (market.index <= filed), "Stock Splits"]
            .ne(0)
            .any()
        ):
            shares = np.nan
    assets_value = float(row["val"])
    equity = at_period(facts, ("StockholdersEquity",), period)
    long_debt, total_debt = debt_components(facts, period)
    cap = shares * float(price["historical_close"])
    return {
        "market_cap_assets": cap / assets_value if assets_value > 0 else np.nan,
        "market_to_book": cap / equity if equity > 0 else np.nan,
        "dividend_yield": float(price["trailing_dividends"] / price["Close"]),
        "debt_maturity": long_debt / total_debt
        if total_debt > 0 and 0 <= long_debt <= total_debt
        else np.nan,
        "period_end": str(period.date()),
        "share_date": str(share_period.date()),
        "latest_filed": str(facts.loc[facts["end"].eq(period), "filed"].max().date()),
    }


def history_view(panel: pd.DataFrame, length: int) -> pd.DataFrame:
    """Flatten exactly the same trailing histories for learned and direct distances."""
    views = []
    for lag in range(length):
        shifted = panel.copy()
        shifted.index = pd.MultiIndex.from_tuples(
            [(year + lag, ticker) for year, ticker in panel.index], names=panel.index.names
        )
        views.append(shifted.add_suffix(f"__lag{lag}"))
    return pd.concat(views, axis=1).reindex(panel.index).sort_index()
