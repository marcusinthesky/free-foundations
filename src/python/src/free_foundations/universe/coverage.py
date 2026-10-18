"""Point-in-time accounting availability, without requiring balanced issuer histories."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.fernandez.characteristics import debt_components
from free_foundations.pilot.data import fact_rows
from free_foundations.universe.sources import company_facts

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
DEBT_TAGS = {
    "LongTermDebtAndCapitalLeaseObligations",
    "LongTermDebtNoncurrent",
    "LongTermDebt",
    "LongTermDebtCurrent",
    "FinanceLeaseLiabilityNoncurrent",
    "CapitalLeaseObligationsNoncurrent",
    "DebtCurrent",
    "ShortTermBorrowings",
    "FinanceLeaseLiabilityCurrent",
    "CapitalLeaseObligationsCurrent",
    "DebtAndCapitalLeaseObligations",
}


def snapshots(cache: Path, universe: pd.DataFrame, first: int, last: int) -> pd.DataFrame:
    """Keep original filing cutoffs; audit the strict lease-consistent debt definition."""
    parts = []
    directory = cache / "snapshots"
    directory.mkdir(exist_ok=True)
    for number, issuer in enumerate(universe.to_dict("records"), 1):
        destination = directory / f"{issuer['cik']:010}-{first}-{last}.parquet"
        if destination.exists():
            parts.append(pd.read_parquet(destination))
            continue
        facts = fact_rows(company_facts(cache, issuer["cik"]))
        facts = facts.loc[
            facts["tag"].isin(DEBT_TAGS | {"Assets", "StockholdersEquity"}) & facts["start"].isna()
        ]
        records = []
        for year in range(first, last + 1):
            cutoff = pd.Timestamp(year=year, month=12, day=31)
            known = facts.loc[
                (facts["filed"] <= cutoff)
                & facts["end"].between(cutoff - pd.Timedelta(days=550), cutoff)
            ]
            assets = known.loc[known["tag"].eq("Assets")].sort_values(["end", "filed", "accn"])
            if assets.empty:
                continue
            observation = assets.iloc[-1]
            period = pd.Timestamp(observation["end"])
            equity = known.loc[
                known["tag"].eq("StockholdersEquity") & known["end"].eq(period)
            ].sort_values(["filed", "accn"])
            noncurrent, total = debt_components(known, period)
            records.append(
                {
                    "year": year,
                    "ticker": issuer["ticker"],
                    "cik": issuer["cik"],
                    "assets": float(observation["val"]),
                    "equity": float(equity.iloc[-1]["val"]) if not equity.empty else np.nan,
                    "debt_maturity": noncurrent / total
                    if total > 0 and 0 <= noncurrent <= total
                    else np.nan,
                    "asset_period": period,
                    "asset_filed": observation["filed"],
                    "asset_accession": observation["accn"],
                }
            )
        frame = pd.DataFrame(
            records,
            columns=[
                "year",
                "ticker",
                "cik",
                "assets",
                "equity",
                "debt_maturity",
                "asset_period",
                "asset_filed",
                "asset_accession",
            ],
        )
        frame.to_parquet(destination, index=False)
        parts.append(frame)
        if number % 50 == 0:
            LOGGER.info("PIT availability: %s / %s issuers", number, len(universe))
    result = pd.concat(parts, ignore_index=True)
    result.to_parquet(cache / "availability.parquet", index=False)
    return result


def coverage(panel: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    """Report annual disclosure and return coverage; do not select cohorts on future prices."""
    records = []
    for key, group in panel.groupby("year"):
        year = int(str(key))
        cutoff = pd.Timestamp(year=year, month=12, day=31)
        training = prices.loc[f"{year - 2}-01-01" : str(cutoff.date())].pct_change(fill_method=None)
        observation_counts = training.notna().sum()
        eligible = group.loc[
            (group["assets"] > 0) & group["ticker"].map(observation_counts.ge(500))
        ]
        following = prices.loc[f"{year + 1}-01-01" : f"{year + 1}-12-31"]
        records.append(
            {
                "snapshot_year": year,
                "evaluation_year": year + 1,
                "known_assets": int(group["assets"].gt(0).sum()),
                "positive_book_equity": int(group["equity"].gt(0).sum()),
                "strict_debt_maturity": int(group["debt_maturity"].notna().sum()),
                "assets_and_500_prior_returns": len(eligible),
                "eligible_with_strict_debt": int(eligible["debt_maturity"].notna().sum()),
                "following_year_any_price": int(
                    following.reindex(columns=eligible["ticker"]).notna().any().sum()
                ),
            }
        )
    return pd.DataFrame(records)
