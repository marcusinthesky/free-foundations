"""Ten annual characteristic snapshots and forty quarters on the 1,000-issuer universe."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from free_foundations.fernandez.characteristics import CHARACTERISTICS, history_view
from free_foundations.fernandez.evaluation import quarterly_data

ROOT = Path("research/replication")
SOURCE = Path("research/universe/cache")
CUTOFF_YEAR = 2025  # Snapshots 2015-2024, each available by 31 December of its year.
HISTORY = 10
QUARTERS = 40
TERMS = ("market",)
ARMS = {"four": CHARACTERISTICS, "three": CHARACTERISTICS[:3]}
WINDOWS = {
    "shifted": ("2016-01-01", "2025-12-31"),
    "contemporaneous": ("2015-01-01", "2024-12-31"),
}


@dataclass(frozen=True)
class Inputs:
    """Characteristics, disclosures and complete quarterly excess returns with factors."""

    four: pd.DataFrame
    quarters: pd.DataFrame
    complete: tuple[str, ...]
    timing: str = "shifted"


def load(*, timing: str = "shifted") -> Inputs:
    """Reuse the panel's point-in-time characteristics and the universe return cache."""
    if timing not in WINDOWS:
        message = f"Unknown return window: {timing}."
        raise ValueError(message)
    four = pd.read_parquet("research/panel/cache/four.parquet")
    prices = pd.read_parquet(SOURCE / "prices.parquet")
    factors = pd.read_parquet(SOURCE / "factors.parquet")
    start, end = WINDOWS[timing]
    quarters = quarterly_data(prices, factors, start=start, end=end)
    expected = pd.date_range(start, end, freq="QE")
    complete = tuple(
        sorted(
            str(ticker)
            for ticker, frame in quarters.groupby("ticker")
            if len(frame) == QUARTERS and pd.DatetimeIndex(frame["date"]).equals(expected)
        )
    )
    return Inputs(four, quarters.loc[quarters["ticker"].isin(complete)], complete, timing)


def cohort(inputs: Inputs, characteristics: tuple[str, ...]) -> tuple[str, ...]:
    """Complete, nonconstant ten-year histories of every characteristic and 40 quarters."""
    histories = pd.DataFrame(
        history_view(inputs.four[list(characteristics)], HISTORY).xs(CUTOFF_YEAR - 1, level="year")
    )
    valid = histories.notna().all(axis=1)
    for name in characteristics:
        columns = histories.filter(like=f"{name}__")
        valid &= columns.max(axis=1) > columns.min(axis=1)
    return tuple(sorted(set(histories.index[valid]) & set(inputs.complete)))


def medians(quarters: pd.DataFrame, tickers: tuple[str, ...]) -> pd.Series:
    """The paper's outcome: each firm's median quarterly excess return."""
    return quarters.groupby("ticker")["excess"].median().loc[list(tickers)]
