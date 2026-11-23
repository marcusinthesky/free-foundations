"""As-of operands selected by the frozen characteristic definitions."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Iterable

GROUP_ROLES = {
    "market_cap_assets": ("market_equity_balance_sheet", "assets"),
    "market_to_book": ("market_equity_balance_sheet", "parent_equity"),
    "dividend_yield": ("dividends", "market_equity_dividend_year"),
    "debt_maturity": ("noncurrent_debt", "total_debt"),
}
SOURCE_TAGS = {
    "market_equity_balance_sheet": ("IssuerMarketEquity",),
    "assets": ("Assets",),
    "parent_equity": ("StockholdersEquity",),
    "dividends": ("PaymentsOfDividendsCommonStock", "PaymentsOfDividends"),
    "market_equity_dividend_year": ("IssuerMarketEquity",),
}
KEYS = ["issuer_id", "quarter"]


def _value(facts: dict[str, float], tags: Iterable[str]) -> float:
    return next((facts[tag] for tag in tags if tag in facts), float("nan"))


def _debt(facts: dict[str, float]) -> tuple[float, float]:
    long = _value(facts, ("LongTermDebtNoncurrent",))
    if not np.isfinite(long):
        current_long = _value(
            facts,
            (
                "LongTermDebtCurrent",
                "LongTermDebtMaturitiesRepaymentsOfPrincipalInNextTwelveMonths",
            ),
        )
        long = _value(facts, ("LongTermDebt",)) - current_long
    if not np.isfinite(long):
        long = _value(facts, ("LongTermDebtAndCapitalLeaseObligations",))
    current = _value(facts, ("DebtCurrent",))
    if "DebtCurrent" not in facts:
        parts = [
            facts[tag] for tag in ("LongTermDebtCurrent", "ShortTermBorrowings") if tag in facts
        ]
        current = (
            float(np.nansum(parts))
            if parts
            else facts.get("LongTermDebtAndCapitalLeaseObligationsCurrent", 0.0)
        )
    return long, long + current


def _decode(components: str) -> dict[str, float]:
    rows: list[dict[str, Any]] = json.loads(components)
    return {
        str(row["concept"]).rsplit(":", 1)[-1]: float(row["value"])
        for row in rows
        if row["value"] is not None
    }


def operand_snapshots(characteristics: pd.DataFrame) -> pd.DataFrame:
    """Recover USD operands from the same dated evidence that produced each ratio.

    Available facts remain visible when the ratio required another missing operand
    or failed its plausibility screen. An unreported current-debt contribution is
    zero only when a noncurrent-debt observation identifies the debt measure.
    """
    rows = []
    for issuer, quarter, name, ratio, components in characteristics[
        [*KEYS, "characteristic", "value", "components"]
    ].itertuples(index=False, name=None):
        roles = GROUP_ROLES[name]
        facts = _decode(components)
        values = (
            _debt(facts)
            if name == "debt_maturity"
            else tuple(_value(facts, SOURCE_TAGS[role]) for role in roles)
        )
        numerator, denominator = values
        if pd.notna(ratio) and (
            not denominator or not np.isclose(numerator / denominator, ratio, rtol=1e-8, atol=1e-9)
        ):
            message = (
                f"Archived operand evidence cannot reconstruct {name} for {issuer} at {quarter}."
            )
            raise ValueError(message)
        rows.append((issuer, quarter, name, *values))
    columns = [*KEYS, "characteristic", "numerator", "denominator"]
    wide = pd.DataFrame(rows, columns=columns).pivot(  # noqa: PD010 -- duplicate facts are invalid.
        index=KEYS, columns="characteristic", values=["numerator", "denominator"]
    )
    ordered = [(position, group) for group in GROUP_ROLES for position in columns[-2:]]
    wide = wide.reindex(columns=pd.MultiIndex.from_tuples(ordered))
    wide.columns = [f"{group}:{role}" for group, roles in GROUP_ROLES.items() for role in roles]
    market_assets = wide.pop("market_cap_assets:market_equity_balance_sheet")
    market_book = wide.pop("market_to_book:market_equity_balance_sheet")
    overlap = market_assets.notna() & market_book.notna()
    if not market_assets[overlap].equals(market_book[overlap]):
        message = "The two balance-sheet ratios disagree on their shared CRSP market equity."
        raise ValueError(message)
    return wide.assign(
        **{"shared:market_equity_balance_sheet": market_assets.combine_first(market_book)}
    )


def operand_history(panel: pd.DataFrame, snapshots: pd.DataFrame, *, years: int) -> pd.DataFrame:
    """Align operands to the same annual-spaced slots and ordered keys as the ratios."""
    index = pd.MultiIndex.from_frame(panel[KEYS])
    parts = []
    for lag in range(years):
        earlier = pd.MultiIndex.from_arrays(
            [panel["issuer_id"], panel["quarter"] - pd.DateOffset(years=lag)], names=KEYS
        )
        values = snapshots.reindex(earlier).set_axis(index)
        parts.append(values.add_prefix("operands:").add_suffix(f":annual_lag{lag}"))
    return pd.concat(parts, axis=1)
