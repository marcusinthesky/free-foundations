"""Ten annual characteristic snapshots and forty quarters on the 1,000-issuer universe."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from free_foundations.fernandez.characteristics import CHARACTERISTICS
from free_foundations.fernandez.evaluation import FACTOR_NAMES, quarterly_data
from free_foundations.panel.characteristics import SOURCE, build
from free_foundations.panel.observations import eligible

ROOT = Path("research/ladder")
CUTOFF_YEAR = 2025  # Snapshots 2015-2024, each available by 31 December of its year.
HISTORY = 10
QUARTERS = 40
FACTORS = tuple(FACTOR_NAMES)
TERMS = {"capm": ("market",), "ff6": tuple(FACTOR_NAMES.values())}
ARMS = {"four": CHARACTERISTICS, "three": CHARACTERISTICS[:3]}


@dataclass(frozen=True)
class Inputs:
    """Characteristics, disclosures and complete quarterly excess returns with factors."""

    four: pd.DataFrame
    broad: pd.DataFrame
    quarters: pd.DataFrame
    complete: tuple[str, ...]


def load() -> Inputs:
    """Reuse the panel's point-in-time characteristics and the universe return cache."""
    four, broad = build()
    prices = pd.read_parquet(SOURCE / "prices.parquet")
    factors = pd.read_parquet(SOURCE / "factors.parquet")
    quarters = quarterly_data(prices, factors, factor_columns=FACTORS)
    counts = quarters.groupby("ticker").size()
    complete = tuple(sorted(counts.index[counts == QUARTERS]))
    return Inputs(four, broad, quarters.loc[quarters["ticker"].isin(complete)], complete)


def cohort(inputs: Inputs, characteristics: tuple[str, ...]) -> tuple[str, ...]:
    """Complete, nonconstant ten-year histories of every characteristic and 40 quarters."""
    histories = eligible(inputs.four, CUTOFF_YEAR, characteristics, HISTORY)
    return tuple(sorted(set(histories) & set(inputs.complete)))


def medians(quarters: pd.DataFrame, tickers: tuple[str, ...]) -> pd.Series:
    """The paper's outcome: each firm's median quarterly excess return."""
    return quarters.groupby("ticker")["excess"].median().loc[list(tickers)]
