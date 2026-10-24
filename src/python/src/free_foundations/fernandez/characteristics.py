"""Auditable US analogues of the four Fernández characteristic histories."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Hashable

LOGGER = logging.getLogger(__name__)
CHARACTERISTICS = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")


@dataclass(frozen=True)
class _Component:
    value: float = np.nan
    evidence: tuple[tuple[dict[Hashable, Any], float], ...] = ()

    def __add__(self, other: _Component) -> _Component:
        return _Component(self.value + other.value, self.evidence + other.evidence)

    def __sub__(self, other: _Component) -> _Component:
        return _Component(
            self.value - other.value,
            self.evidence + tuple((row, -coefficient) for row, coefficient in other.evidence),
        )


def _nonnegative(component: _Component) -> _Component:
    """An alternative debt reconstruction requires nonnegative constituent amounts."""
    return component if np.isfinite(component.value) and component.value >= 0 else _Component()


def _at_period(facts: pd.DataFrame, tags: tuple[str, ...], period: pd.Timestamp) -> _Component:
    for tag in tags:
        rows = facts.loc[(facts["tag"] == tag) & (facts["end"] == period)]
        if not rows.empty:
            row = rows.sort_values(["filed", "accn"]).iloc[-1]
            return _Component(float(row["val"]), ((row.to_dict(), 1.0),))
    return _Component()


def at_period(facts: pd.DataFrame, tags: tuple[str, ...], period: pd.Timestamp) -> float:
    """Require the exact common balance-sheet date; never infer missing debt as zero."""
    return _at_period(facts, tags, period).value


def _parent_equity(facts: pd.DataFrame, period: pd.Timestamp) -> _Component:
    equity = _at_period(facts, ("StockholdersEquity",), period)
    # A reported zero or deficit is observed parent equity, not a missing value.
    if np.isfinite(equity.value):
        return equity
    return _at_period(
        facts, ("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",), period
    ) - _at_period(facts, ("MinorityInterest",), period)


def parent_equity(facts: pd.DataFrame, period: pd.Timestamp) -> float:
    """Use explicit parent equity, or consolidated equity less explicitly reported NCI."""
    return _parent_equity(facts, period).value


def _preferred_debt_components(
    facts: pd.DataFrame, period: pd.Timestamp
) -> tuple[_Component, _Component, _Component]:
    # Preserve the existing component preferences and their lease-inclusive basis.
    long_debt = _at_period(facts, ("LongTermDebtAndCapitalLeaseObligations",), period)
    if not np.isfinite(long_debt.value):
        debt_only = _at_period(facts, ("LongTermDebtNoncurrent",), period)
        if not np.isfinite(debt_only.value):
            debt_only = _at_period(facts, ("LongTermDebt",), period) - _at_period(
                facts, ("LongTermDebtCurrent",), period
            )
        long_debt = debt_only + _at_period(
            facts, ("FinanceLeaseLiabilityNoncurrent", "CapitalLeaseObligationsNoncurrent"), period
        )
    current_debt = _at_period(facts, ("DebtCurrent",), period)
    if not np.isfinite(current_debt.value):
        current_debt = (
            _at_period(facts, ("LongTermDebtCurrent",), period)
            + _at_period(facts, ("ShortTermBorrowings",), period)
            + _at_period(
                facts, ("FinanceLeaseLiabilityCurrent", "CapitalLeaseObligationsCurrent"), period
            )
        )
    total_debt = _at_period(facts, ("DebtAndCapitalLeaseObligations",), period)
    if not np.isfinite(total_debt.value):
        total_debt = long_debt + current_debt
    if not np.isfinite(long_debt.value):
        long_debt = total_debt - current_debt
    return long_debt, current_debt, total_debt


def _debt_components(facts: pd.DataFrame, period: pd.Timestamp) -> tuple[_Component, _Component]:
    long_debt, current_debt, total_debt = _preferred_debt_components(facts, period)

    # SEC taxonomy descriptions distinguish the current part of long-term debt
    # and leases from all current debt. Short-term borrowing must be explicit:
    # neither a missing value nor CommercialPaper (a subset) establishes zero.
    long_including_current = _nonnegative(
        _at_period(
            facts, ("LongTermDebtAndCapitalLeaseObligationsIncludingCurrentMaturities",), period
        )
    )
    long_current = _nonnegative(
        _at_period(facts, ("LongTermDebtAndCapitalLeaseObligationsCurrent",), period)
    )
    short_debt = _nonnegative(_at_period(facts, ("ShortTermBorrowings",), period))
    if not np.isfinite(long_debt.value):
        long_debt = _nonnegative(long_including_current - long_current)
    if not np.isfinite(current_debt.value):
        if not np.isfinite(long_current.value):
            long_current = _nonnegative(long_including_current - long_debt)
        current_debt = long_current + short_debt
    if not np.isfinite(total_debt.value):
        total_debt = long_debt + current_debt
    if not np.isfinite(total_debt.value):
        total_debt = long_including_current + short_debt
    if not np.isfinite(long_debt.value):
        long_debt = total_debt - current_debt
    return long_debt, total_debt


def debt_components(facts: pd.DataFrame, period: pd.Timestamp) -> tuple[float, float]:
    """Return noncurrent and total debt on a consistently lease-inclusive basis."""
    long_debt, total_debt = _debt_components(facts, period)
    return long_debt.value, total_debt.value


def _component_audit(components: tuple[tuple[str, _Component], ...]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                **fact,
                "component": name,
                "coefficient": coefficient,
                "component_value": component.value,
            }
            for name, component in components
            for fact, coefficient in component.evidence
        ]
    )


def _debt_maturity(long_debt: _Component, total_debt: _Component) -> float:
    return (
        long_debt.value / total_debt.value
        if total_debt.value > 0 and 0 <= long_debt.value <= total_debt.value
        else np.nan
    )


def debt_maturity_with_audit(
    facts: pd.DataFrame, period: pd.Timestamp
) -> tuple[float, pd.DataFrame]:
    """Construct debt maturity from exact-period facts with its selected component evidence.

    The caller retains responsibility for filing availability and observation age.
    No asset, equity, share, market-price or other characteristic inputs are changed.
    """
    long_debt, total_debt = _debt_components(facts, period)
    evidence = _component_audit((("debt_noncurrent", long_debt), ("debt_total", total_debt)))
    return _debt_maturity(long_debt, total_debt), evidence


def snapshot_with_audit(
    facts: pd.DataFrame, market: pd.DataFrame
) -> tuple[dict[str, float | str], pd.DataFrame]:
    """Construct a snapshot and retain its exact SEC component facts and arithmetic."""
    assets = facts.loc[facts["tag"].eq("Assets")].sort_values(["end", "filed", "accn"])
    if assets.empty:
        return {}, pd.DataFrame()
    row = assets.iloc[-1]
    period = pd.Timestamp(row["end"])
    available = market.loc[:period]
    if available.empty or (period - available.index[-1]).days > 7:
        return {}, pd.DataFrame()
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
        return {}, pd.DataFrame()
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
    assets_component = _Component(float(row["val"]), ((row.to_dict(), 1.0),))
    equity = _parent_equity(facts, period)
    long_debt, total_debt = _debt_components(facts, period)
    share_component = _Component(
        shares, tuple((row.to_dict(), 1.0) for _, row in share_rows.iterrows())
    )
    evidence = _component_audit(
        (
            ("assets", assets_component),
            ("shares", share_component),
            ("equity", equity),
            ("debt_noncurrent", long_debt),
            ("debt_total", total_debt),
        )
    )
    assets_value = assets_component.value
    cap = shares * float(price["historical_close"])
    result = {
        "market_cap_assets": cap / assets_value if assets_value > 0 else np.nan,
        "market_to_book": cap / equity.value if equity.value > 0 else np.nan,
        "dividend_yield": float(price["trailing_dividends"] / price["Close"]),
        "debt_maturity": _debt_maturity(long_debt, total_debt),
        "period_end": str(period.date()),
        "share_date": str(share_period.date()),
        "market_date": str(share_market.index[-1].date()),
        "market_close": float(price["Close"]),
        "market_historical_close": float(price["historical_close"]),
        "trailing_dividends": float(price["trailing_dividends"]),
        "latest_filed": str(facts.loc[facts["end"].eq(period), "filed"].max().date()),
    }
    return result, evidence


def snapshot(facts: pd.DataFrame, market: pd.DataFrame) -> dict[str, float | str]:
    """Construct ratios at the latest disclosed asset period, from aligned observations."""
    return snapshot_with_audit(facts, market)[0]


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
