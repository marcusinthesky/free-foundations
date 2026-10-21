"""Separate the paper's cross-sectional exercise from ex ante covariance forecasts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pandas as pd

SCRIPT = Path(__file__).with_name("betas.R")


FACTOR_NAMES = {
    "Mkt-RF": "market",
    "SMB": "smb",
    "HML": "hml",
    "RMW": "rmw",
    "CMA": "cma",
    "Mom": "mom",
}


def quarterly_data(
    prices: pd.DataFrame,
    factors: pd.DataFrame,
    *,
    factor_columns: tuple[str, ...] = ("Mkt-RF",),
    start: str = "2016-01-01",
    end: str = "2025-12-31",
) -> pd.DataFrame:
    """Compound daily total returns and RF separately before computing quarterly excess.

    The market excess return compounds the total market return and subtracts compounded
    RF. Long-short factors are compounded as prod(1 + f) - 1: a compounded daily-factor
    proxy, not a quarterly payoff built from the factor's long and short legs.
    """
    returns = prices.pct_change(fill_method=None).reindex(factors.index)
    quarterly = (1 + returns).resample("QE").prod(min_count=1) - 1
    counts = returns.resample("QE").count()
    quarterly = quarterly.where(counts.eq(returns.resample("QE").size(), axis=0))
    risk_free = (1 + factors["RF"]).resample("QE").prod() - 1
    quarterly = quarterly.sub(risk_free, axis=0)
    frame = (
        quarterly.rename_axis(index="date")
        .reset_index()
        .melt(id_vars="date", var_name="ticker", value_name="excess")
        .dropna()
    )
    for column in factor_columns:
        if column == "Mkt-RF":
            values = (1 + factors["Mkt-RF"] + factors["RF"]).resample("QE").prod() - 1 - risk_free
        else:
            values = (1 + factors[column]).resample("QE").prod() - 1
        frame[FACTOR_NAMES[column]] = frame["date"].map(values)
    return frame.loc[frame["date"].between(start, end)]


def robust_betas(  # noqa: PLR0913 -- keyword-only R runtime options.
    quarters: pd.DataFrame,
    output: Path,
    *,
    terms: tuple[str, ...] = ("market",),
    indices: pd.DataFrame | None = None,
    cores: int = 1,
    tag: str = "capm",
) -> pd.DataFrame:
    """Call the established MM implementation rather than relabel OLS or Huber estimates.

    Returns long estimates with one row per replicate, firm and term. Replicate 0 is the
    original sample; ``indices`` lists resampled quarters for bootstrap replicates.
    """
    executable = shutil.which("Rscript")
    if executable is None:
        message = "Run inside devenv shell: robustbase's Rscript runtime is required."
        raise RuntimeError(message)
    cache = output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    source, destination = cache / f"mm-{tag}-input.csv", cache / f"mm-{tag}-output.csv"
    frame = quarters[["date", "ticker", "excess", *terms]].rename(columns={"date": "quarter"})
    frame.assign(quarter=frame["quarter"].astype(str).str[:10]).to_csv(source, index=False)
    arguments = [executable, str(SCRIPT), str(source), str(destination), ",".join(terms)]
    if indices is not None:
        path = cache / f"mm-{tag}-indices.csv"
        indices.assign(quarter=indices["quarter"].astype(str).str[:10]).to_csv(path, index=False)
        arguments += [str(path), str(cores)]
    subprocess.run(arguments, check=True)  # noqa: S603 -- fixed local R script and generated paths.
    result = pd.read_csv(destination)
    original = result.loc[result["replicate"].eq(0)]
    if not original.empty and not original["converged"].all():
        message = "At least one robust MM fit on the original sample did not converge."
        raise RuntimeError(message)
    return result


def runtime_record(output: Path, tag: str = "capm") -> dict[str, str]:
    """R, robustbase and lmrob.control settings recorded by the last MM call."""
    path = output / "cache" / f"mm-{tag}-output-runtime.csv"
    frame = pd.read_csv(path, dtype=str)
    return dict(zip(frame["name"], frame["value"], strict=True))


def exposure_table(estimates: pd.DataFrame, replicate: int = 0) -> pd.DataFrame:
    """Wide factor exposures for one replicate, indexed by ticker, excluding intercepts."""
    selected = estimates.loc[
        estimates["replicate"].eq(replicate) & estimates["term"].ne("intercept")
    ]
    terms = list(dict.fromkeys(selected["term"]))
    return selected.pivot_table(index="ticker", columns="term", values="estimate")[terms]
