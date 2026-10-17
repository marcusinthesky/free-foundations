"""Prior-only cohort selection, factor estimation, and shared outcome dates."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.fernandez.characteristics import CHARACTERISTICS, history_view
from free_foundations.panel.characteristics import ROOT, SOURCE
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


def annual_data(
    four: pd.DataFrame, year: int
) -> tuple[tuple[str, ...], FloatArray, FloatArray, FloatArray, FloatArray, FloatArray]:
    """Select on preyear information; drop missing outcome dates identically for all models."""
    prices = pd.read_parquet(SOURCE / "prices.parquet")
    factors = pd.read_parquet(SOURCE / "factors.parquet")
    returns = prices.pct_change(fill_method=None).sub(factors["RF"], axis=0)
    history = pd.DataFrame(history_view(four, 3).xs(year - 1, level="year"))
    valid = history.notna().all(axis=1)
    for name in CHARACTERISTICS:
        values = history.filter(like=f"{name}__")
        valid &= values.max(axis=1) > values.min(axis=1)
    past = (
        returns.loc[f"{year - 3}-01-01" : f"{year - 1}-12-31"]
        .reindex(factors.index)
        .dropna(how="all")
    )
    eligible = sorted(set(history.index[valid]) & set(past.columns[past.notna().sum() >= 500]))
    tickers = tuple(eligible)
    if len(tickers) < 5:
        message = f"Only {len(tickers)} strict eligible firms in {year}."
        raise ValueError(message)
    training = past[list(tickers)].dropna()
    future = returns.loc[f"{year}-01-01" : f"{year}-12-31", list(tickers)]
    # Filing dates have no intraday timestamp. Exclude the first close-to-close
    # return, whose opening boundary can precede a year-end after-close filing.
    observed = future.iloc[1:].dropna()
    factor_names = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]
    x_train = np.column_stack([np.ones(len(training)), factors.loc[training.index, factor_names]])
    x_test = np.column_stack([np.ones(len(observed)), factors.loc[observed.index, factor_names]])
    beta = np.linalg.lstsq(x_train, training.to_numpy(dtype=float), rcond=None)[0]
    residual_train = training.to_numpy(dtype=float) - x_train @ beta
    residual_test = observed.to_numpy(dtype=float) - x_test @ beta
    output = ROOT / "observations"
    output.mkdir(exist_ok=True)
    observed.to_parquet(output / f"{year}-returns.parquet")
    pd.DataFrame(residual_train, index=training.index, columns=tickers).to_parquet(
        output / f"{year}-prior-residuals.parquet"
    )
    pd.DataFrame(residual_test, index=observed.index, columns=tickers).to_parquet(
        output / f"{year}-residuals.parquet"
    )
    write_json(
        output / f"{year}-sample.json",
        {
            "tickers": tickers,
            "firms": len(tickers),
            "past_complete_days": len(training),
            "evaluation_days": len(observed),
            "excluded_outcome_dates": [
                str(date.date()) for date in future.index.difference(observed.index)
            ],
            "first_return_excluded_for_filing_time": str(future.index[0].date()),
            "factor_beta": beta.tolist(),
            "factor_names": ["intercept", *factor_names],
        },
    )
    return (
        tickers,
        residual_train,
        residual_test,
        training.to_numpy(dtype=float),
        observed.to_numpy(dtype=float),
        beta[1:].T @ np.cov(x_train[:, 1:], rowvar=False) @ beta[1:],
    )
