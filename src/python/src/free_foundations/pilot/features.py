"""Point-in-time annual accounting states, with auditable fact selection."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.pilot.data import fact_rows

if TYPE_CHECKING:
    from pathlib import Path

# Alternatives are ordered only to break ties at the same period and filing date.
TAGS = {
    "assets": ("Assets",),
    "liabilities": ("Liabilities",),
    "equity": (
        "StockholdersEquity",
        "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
    ),
    "cash": ("CashAndCashEquivalentsAtCarryingValue",),
    "receivables": ("AccountsReceivableNetCurrent",),
    "inventory": ("InventoryNet",),
    "current_assets": ("AssetsCurrent",),
    "current_liabilities": ("LiabilitiesCurrent",),
    "ppe": ("PropertyPlantAndEquipmentNet",),
    "goodwill": ("Goodwill",),
    "intangibles": ("FiniteLivedIntangibleAssetsNet", "IntangibleAssetsNetExcludingGoodwill"),
    "retained": ("RetainedEarningsAccumulatedDeficit",),
    "revenue": (
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet",
    ),
    "income": ("NetIncomeLoss", "ProfitLoss"),
    "operating_income": ("OperatingIncomeLoss",),
    "operating_cash": ("NetCashProvidedByUsedInOperatingActivities",),
    "capex": ("PaymentsToAcquirePropertyPlantAndEquipment",),
    "research": ("ResearchAndDevelopmentExpense",),
    "interest": ("InterestExpense",),
}
FLOWS = frozenset(
    {"revenue", "income", "operating_income", "operating_cash", "capex", "research", "interest"}
)
FEATURES = ("log_assets", *(key for key in TAGS if key != "assets"))


def select_facts(facts: pd.DataFrame, cutoff: pd.Timestamp) -> pd.DataFrame:
    """Select latest known facts, excluding future restatements and short flow periods."""
    available = facts.loc[(facts["filed"] <= cutoff) & (facts["end"] <= cutoff)].copy()
    available = available.loc[available["end"] >= cutoff - pd.Timedelta(days=550)]
    selected = []
    for name, tags in TAGS.items():
        candidates = available.loc[available["tag"].isin(tags)].copy()
        days = (candidates["end"] - candidates["start"]).dt.days
        candidates = candidates.loc[
            days.between(300, 380) if name in FLOWS else candidates["start"].isna()
        ]
        if candidates.empty:
            continue
        candidates["priority"] = candidates["tag"].map({tag: i for i, tag in enumerate(tags)})
        latest = candidates.sort_values(
            ["end", "filed", "priority"], ascending=[False, False, True]
        ).iloc[0]
        selected.append({"feature": name, **latest.to_dict()})
    return pd.DataFrame(selected)


def accounting_panel(cache: Path, universe: pd.DataFrame) -> pd.DataFrame:
    """Build year-end 2012-2024 states and retain the selected filing audit trail."""
    rows: list[dict[str, str | int | float]] = []
    audit: list[pd.DataFrame] = []
    for issuer in universe.to_dict("records"):
        facts = fact_rows(json.loads((cache / "facts" / f"{issuer['cik']:010}.json").read_text()))
        for year in range(2012, 2025):
            selected = select_facts(facts, pd.Timestamp(year=year, month=12, day=31))
            if selected.empty or "assets" not in selected["feature"].to_numpy():
                continue
            values = selected.set_index("feature")["val"]
            assets = float(values["assets"])
            if assets <= 0:
                continue
            row = {"ticker": issuer["ticker"], "year": year, "log_assets": np.log(assets)}
            row.update({name: float(values.get(name, np.nan)) / assets for name in FEATURES[1:]})
            rows.append(row)
            selected["ticker"], selected["cutoff_year"] = issuer["ticker"], year
            audit.append(selected)
    panel = pd.DataFrame(rows).set_index(["year", "ticker"]).sort_index()
    panel.to_parquet(cache / "accounting.parquet")
    pd.concat(audit, ignore_index=True).to_parquet(cache / "filing-audit.parquet")
    return panel
