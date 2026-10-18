"""Prior-only cohort selection, factor estimation, and shared outcome dates."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.fernandez.characteristics import CHARACTERISTICS, history_view
from free_foundations.panel.characteristics import ROOT, SOURCE
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray

FACTOR_NAMES = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]
# A close-to-close price ratio beyond tenfold flags a suspect series. Every flagged day must
# be reviewed below; distress and repricing are kept unless shown to be a series error.
PRICE_BREAK = 10.0
LARGE_MOVE = 0.5
# Reviewed extreme days. ``masked`` days are series errors; the rest are genuine and kept.
EVENTS: dict[tuple[str, str], tuple[bool, str]] = {
    ("CHRD", "2020-11-20"): (
        True,
        (
            "Chapter 11 emergence: the series splices pre-bankruptcy Oasis shares ($0.073) "
            "to the new equity ($18.84), a +25,733% non-return"
        ),
    ),
    ("QXO", "2024-07-30"): (
        False,
        (
            "genuine repricing: a 2024-07-29 registration made about $4.1bn of "
            "private-placement shares tradable, raising the float from about 0.67m to "
            "about 400m shares"
        ),
    ),
}


@dataclass(frozen=True)
class Annual:
    """One return year's frozen cohort, prior residuals and realized outcomes."""

    tickers: tuple[str, ...]
    prior: FloatArray
    realized: FloatArray
    raw_prior: FloatArray
    raw_realized: FloatArray
    factor_covariance: FloatArray
    dates: tuple[str, ...]


def eligible(
    four: pd.DataFrame, year: int, characteristics: tuple[str, ...], history: int
) -> pd.Index:
    """Firms with complete, nonconstant histories of every characteristic by year - 1."""
    values = pd.DataFrame(
        history_view(four[list(characteristics)], history).xs(year - 1, level="year")
    )
    valid = values.notna().all(axis=1)
    for name in characteristics:
        columns = values.filter(like=f"{name}__")
        valid &= columns.max(axis=1) > columns.min(axis=1)
    return values.index[valid]


def _cells(frame: pd.DataFrame, selected: pd.DataFrame, name: str) -> pd.DataFrame:
    """Selected cells of a date-by-ticker frame as (ticker, date, value) rows."""
    rows, columns = np.nonzero(selected.to_numpy(dtype=bool))
    return pd.DataFrame(
        {
            "ticker": frame.columns[columns].astype(str),
            "date": pd.DatetimeIndex(frame.index[rows]).strftime("%Y-%m-%d"),
            name: frame.to_numpy(dtype=float)[rows, columns],
        }
    )


def price_breaks(prices: pd.DataFrame) -> pd.DataFrame:
    """Firm-days the tenfold rule flags, as (ticker, date, ratio) rows."""
    ratio = prices / prices.shift(1)
    return _cells(ratio, (ratio > PRICE_BREAK) | (ratio < 1 / PRICE_BREAK), "ratio")


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns, missing where the price ratio is outside [1/10, 10]."""
    ratio = prices / prices.shift(1)
    broken = (ratio > PRICE_BREAK) | (ratio < 1 / PRICE_BREAK)
    return prices.pct_change(fill_method=None).mask(broken)


def price_audit(prices: pd.DataFrame) -> pd.DataFrame:
    """Every flagged or large daily move, with its review; unreviewed masks are an error."""
    returns = prices.pct_change(fill_method=None)
    rows = _cells(returns, returns.abs() > LARGE_MOVE, "return")
    flagged = set(map(tuple, price_breaks(prices)[["ticker", "date"]].to_numpy()))
    rows["masked"] = [(t, d) in flagged for t, d in zip(rows["ticker"], rows["date"], strict=True)]
    rows["reviewed"] = [(t, d) in EVENTS for t, d in zip(rows["ticker"], rows["date"], strict=True)]
    rows["note"] = [
        EVENTS.get((t, d), (False, ""))[1]
        for t, d in zip(rows["ticker"], rows["date"], strict=True)
    ]
    unreviewed = sorted(flagged - {key for key, (masked, _) in EVENTS.items() if masked})
    if unreviewed:
        message = f"Unreviewed price breaks would be masked: {unreviewed}"
        raise ValueError(message)
    return rows


def annual_data(  # noqa: PLR0913 -- keyword-only design options.
    four: pd.DataFrame,
    year: int,
    *,
    characteristics: tuple[str, ...] = CHARACTERISTICS,
    histories: tuple[int, ...] = (3,),
    output: Path = ROOT,
    exclude: tuple[str, ...] = (),
) -> Annual:
    """Select on preyear information; drop missing outcome dates identically for all models."""
    prices = pd.read_parquet(SOURCE / "prices.parquet")
    factors = pd.read_parquet(SOURCE / "factors.parquet")
    returns = daily_returns(prices).sub(factors["RF"], axis=0)
    past = (
        returns.loc[f"{year - 3}-01-01" : f"{year - 1}-12-31"]
        .reindex(factors.index)
        .dropna(how="all")
    )
    # A firm must support every network built on it: a complete five-year history can
    # still be constant over its last three years.
    candidates = set.intersection(
        *(set(eligible(four, year, characteristics, length)) for length in histories)
    )
    candidates -= set(exclude)
    tickers = tuple(sorted(candidates & set(past.columns[past.notna().sum() >= 500])))
    if len(tickers) < 5:
        message = f"Only {len(tickers)} strict eligible firms in {year}."
        raise ValueError(message)
    training = past[list(tickers)].dropna()
    future = returns.loc[f"{year}-01-01" : f"{year}-12-31", list(tickers)]
    # Filing dates have no intraday timestamp. Exclude the first close-to-close
    # return, whose opening boundary can precede a year-end after-close filing.
    observed = future.iloc[1:].dropna()
    x_train = np.column_stack([np.ones(len(training)), factors.loc[training.index, FACTOR_NAMES]])
    x_test = np.column_stack([np.ones(len(observed)), factors.loc[observed.index, FACTOR_NAMES]])
    beta = np.linalg.lstsq(x_train, training.to_numpy(dtype=float), rcond=None)[0]
    residual_train = training.to_numpy(dtype=float) - x_train @ beta
    residual_test = observed.to_numpy(dtype=float) - x_test @ beta
    destination = output / "observations"
    destination.mkdir(parents=True, exist_ok=True)
    observed.to_parquet(destination / f"{year}-returns.parquet")
    write_json(
        destination / f"{year}-sample.json",
        {
            "tickers": tickers,
            "firms": len(tickers),
            "characteristics": characteristics,
            "history_years": histories,
            "excluded_tickers": exclude,
            "past_complete_days": len(training),
            "evaluation_days": len(observed),
            "excluded_outcome_dates": [
                str(date.date()) for date in future.index.difference(observed.index)
            ],
            "first_return_excluded_for_filing_time": str(future.index[0].date()),
            "factor_names": ["intercept", *FACTOR_NAMES],
        },
    )
    return Annual(
        tickers=tickers,
        prior=residual_train,
        realized=residual_test,
        raw_prior=training.to_numpy(dtype=float),
        raw_realized=observed.to_numpy(dtype=float),
        factor_covariance=beta[1:].T @ np.cov(x_train[:, 1:], rowvar=False) @ beta[1:],
        dates=tuple(str(date.date()) for date in observed.index),
    )
