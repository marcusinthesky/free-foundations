"""Fernández's four characteristics from CRSP market equity and SEC CompanyFacts books.

Market equity is CRSP issuer capitalization (USD) at the month of the accounting
period end, summed over the issuer's share classes in the extract. Book quantities are
entity-wide US-GAAP facts already restricted to the as-of information set. Debt
maturity uses reported debt and excludes lease liabilities, which were off balance
sheet in Fernández's sample. A missing component leaves its characteristic missing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Sequence

CHARACTERISTICS = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")
MARKET_EQUITY = "crsp:IssuerMarketEquity"
REASONS = {
    "market_cap_assets": "crsp_market_equity_or_positive_assets_unavailable",
    "market_to_book": "crsp_market_equity_or_positive_parent_equity_unavailable",
    "dividend_yield": "crsp_market_equity_or_annual_common_dividends_unavailable",
    "debt_maturity": "noncurrent_and_total_reported_debt_unavailable",
}
# Plausible ranges screen filer scale errors (for example assets tagged in millions).
# Values outside them are unavailable with their own reason, never rescaled.
PLAUSIBLE = {
    "market_cap_assets": (1e-3, 1e3),
    "market_to_book": (1e-3, 1e3),
    "dividend_yield": (0.0, 1.0),
    "debt_maturity": (0.0, 1.0),
}
IMPLAUSIBLE = "outside_plausible_range"
# Annual filers report within about three months of a fiscal year end; older
# balance sheets indicate a filer that stopped reporting and are not carried forward.
MAX_BALANCE_SHEET_AGE_DAYS = 456
STALE = "balance_sheet_older_than_15_months"
ANNUAL_FORMS = {"10-K", "10-K/A", "10-KT", "10-KT/A", "20-F", "20-F/A", "40-F", "40-F/A"}


@dataclass(frozen=True)
class Characteristic:
    """One characteristic value, its unavailability reason and its component evidence."""

    name: str
    value: float
    reason: str
    evidence: pd.DataFrame


def entity_facts(facts: pd.DataFrame) -> pd.DataFrame:
    """Entity-wide numeric US-GAAP USD facts, oldest information first."""
    if facts.empty:
        return facts
    return facts.loc[
        facts["namespace"].eq("us-gaap")
        & facts["unit"].eq("USD")
        & facts["dimensions"].eq("{}")
        & facts["value_type"].eq("numeric")
    ]


def _instant(facts: pd.DataFrame, tags: Sequence[str], period: pd.Timestamp) -> pd.DataFrame:
    """The latest reported value of the first listed tag at exactly ``period``."""
    for tag in tags:
        rows = facts.loc[
            facts["tag"].eq(tag) & facts["period_kind"].eq("instant") & facts["end"].eq(period)
        ]
        if not rows.empty:
            return rows.tail(1)
    return facts.iloc[:0]


def _rows(*frames: pd.DataFrame) -> pd.DataFrame:
    """Concatenate only nonempty evidence frames."""
    kept = [frame for frame in frames if not frame.empty]
    return pd.concat(kept, ignore_index=True) if kept else pd.DataFrame()


def _number(rows: pd.DataFrame) -> float:
    return float(pd.to_numeric(rows["value"], errors="coerce").iloc[-1]) if len(rows) else np.nan


def market_equity_evidence(equity: pd.Series, period: pd.Timestamp) -> pd.DataFrame:
    """One CRSP row for issuer market equity at the month containing ``period``."""
    month = pd.Timestamp(period).to_period("M").to_timestamp("M")
    value = float(equity.get(month, np.nan))
    if not np.isfinite(value) or value <= 0:
        return pd.DataFrame(columns=["concept", "value", "unit", "end"])
    return pd.DataFrame([{"concept": MARKET_EQUITY, "value": value, "unit": "USD", "end": month}])


def _first(facts: pd.DataFrame, period: pd.Timestamp, *options: tuple[str, ...]) -> pd.DataFrame:
    """Rows of the first option whose every tag is reported at ``period``."""
    for tags in options:
        rows = [_instant(facts, (tag,), period) for tag in tags]
        if all(not row.empty for row in rows):
            return _rows(*rows)
    return facts.iloc[:0]


def debt_maturity_with_audit(
    facts: pd.DataFrame, period: pd.Timestamp
) -> tuple[float, pd.DataFrame]:
    """Noncurrent over total reported debt, without operating-lease liabilities.

    Noncurrent debt is the first available of ``LongTermDebtNoncurrent``,
    ``LongTermDebt`` less its current part (``LongTermDebtCurrent`` or the next
    twelve months of scheduled maturities), and ``LongTermDebtAndCapitalLeaseObligations``.
    Current debt is ``DebtCurrent``, else the reported current long-term debt and
    ``ShortTermBorrowings``, else ``LongTermDebtAndCapitalLeaseObligationsCurrent``.
    Capital (finance) leases were balance-sheet debt in Fernández's sample; operating
    lease liabilities never enter. An untagged current component contributes nothing.
    """
    noncurrent = _instant(facts, ("LongTermDebtNoncurrent",), period)
    long_value = _number(noncurrent)
    used = [noncurrent]
    if not np.isfinite(long_value):
        total = _instant(facts, ("LongTermDebt",), period)
        current_part = _first(
            facts,
            period,
            ("LongTermDebtCurrent",),
            ("LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths",),
        )
        long_value = _number(total) - _number(current_part)
        used = [total, current_part]
    if not np.isfinite(long_value):
        capital = _instant(facts, ("LongTermDebtAndCapitalLeaseObligations",), period)
        long_value, used = _number(capital), [capital]
    current = _instant(facts, ("DebtCurrent",), period)
    if current.empty:
        parts = [
            _instant(facts, (tag,), period)
            for tag in ("LongTermDebtCurrent", "ShortTermBorrowings")
        ]
        current = _rows(*parts)
    if current.empty:
        current = _instant(facts, ("LongTermDebtAndCapitalLeaseObligationsCurrent",), period)
    current_value = (
        float(pd.to_numeric(current["value"], errors="coerce").sum()) if len(current) else 0.0
    )
    total_value = long_value + current_value
    evidence = _rows(*used, current).drop_duplicates()
    valid = (
        np.isfinite(total_value)
        and total_value > 0
        and 0 <= long_value <= total_value
        and current_value >= 0
    )
    return (long_value / total_value if valid else np.nan), evidence


def characteristics(facts: pd.DataFrame, equity: pd.Series) -> list[Characteristic]:
    """Fernández's four ratios at the latest as-of annual-report balance sheet.

    Her characteristics are annual; debt detail is reliably tagged only in annual
    reports. Without an annual report the latest balance sheet is used.

    ``facts`` is the as-of fact set. ``equity`` maps month ends to CRSP issuer
    market equity in USD.
    """
    entity = entity_facts(facts)
    assets_rows = entity.loc[entity["tag"].eq("Assets") & entity["period_kind"].eq("instant")]
    if "form" in assets_rows:
        annual = assets_rows.loc[assets_rows["form"].astype(str).isin(ANNUAL_FORMS)]
        assets_rows = annual if not annual.empty else assets_rows
    stale = (
        not assets_rows.empty
        and "fact_age_days" in assets_rows
        and float(assets_rows["fact_age_days"].iloc[-1]) > MAX_BALANCE_SHEET_AGE_DAYS
    )
    if assets_rows.empty or stale:
        reason = STALE if stale else None
        return [
            Characteristic(name, np.nan, reason or REASONS[name], pd.DataFrame())
            for name in CHARACTERISTICS
        ]
    assets = assets_rows.tail(1)
    period = pd.Timestamp(assets.iloc[-1]["end"])
    market = market_equity_evidence(equity, period)
    market_value = _number(market)
    assets_value = _number(assets)
    parent = _instant(entity, ("StockholdersEquity",), period)
    dividends = entity.loc[
        entity["tag"].isin({"PaymentsOfDividendsCommonStock", "PaymentsOfDividends"})
        & entity["period_kind"].eq("annual")
    ]
    if dividends["tag"].eq("PaymentsOfDividendsCommonStock").any():
        dividends = dividends.loc[dividends["tag"].eq("PaymentsOfDividendsCommonStock")]
    dividends = dividends.tail(1)
    dividend_market = (
        market_equity_evidence(equity, pd.Timestamp(dividends.iloc[-1]["end"]))
        if len(dividends)
        else market.iloc[:0]
    )
    dividend_value, dividend_equity = _number(dividends), _number(dividend_market)
    debt_value, debt_evidence = debt_maturity_with_audit(entity, period)
    values = {
        "market_cap_assets": (
            market_value / assets_value if assets_value > 0 else np.nan,
            _rows(market, assets),
        ),
        "market_to_book": (
            market_value / _number(parent) if _number(parent) > 0 else np.nan,
            _rows(market, parent),
        ),
        "dividend_yield": (
            dividend_value / dividend_equity if dividend_value >= 0 else np.nan,
            _rows(dividend_market, dividends),
        ),
        "debt_maturity": (debt_value, debt_evidence),
    }
    results = []
    for name, (value, evidence) in values.items():
        low, high = PLAUSIBLE[name]
        reason = "" if np.isfinite(value) else REASONS[name]
        if not reason and not low <= value <= high:
            reason = IMPLAUSIBLE
        results.append(Characteristic(name, np.nan if reason else float(value), reason, evidence))
    return results
