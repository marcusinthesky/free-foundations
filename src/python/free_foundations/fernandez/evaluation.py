"""Separate the paper's cross-sectional exercise from ex ante covariance forecasts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import shapiro
from sklearn.covariance import LedoitWolf

from free_foundations.fernandez.diagnostics import first_stage_f, pseudo_r2, residual_moran
from free_foundations.fernandez.models import error_ml, lag_iv, ols, residual_covariance
from free_foundations.pilot.experiment import FACTORS
from free_foundations.pilot.spatial import daily_scores

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

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


def legacy_betas(estimates: pd.DataFrame) -> pd.DataFrame:
    """The original single-factor ``mm-betas.csv`` layout used by earlier artifacts."""
    original = estimates.loc[estimates["replicate"].eq(0)]
    wide = original.pivot_table(index="ticker", columns="term", values="estimate")
    status = original.groupby("ticker")[["converged", "observations", "package_version"]].first()
    return pd.concat(
        [wide.rename(columns={"market": "beta"})[["beta", "intercept"]], status], axis=1
    )


def cross_section(
    quarters: pd.DataFrame, betas: pd.DataFrame, networks: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """Replicate the two-stage specification on US data; no OOS claims for this table."""
    medians = quarters.groupby("ticker")["excess"].median()
    records = []
    for name, network in networks.items():
        tickers = network.index
        x = betas.loc[tickers, ["beta"]].to_numpy(dtype=float)
        y = medians.loc[tickers].to_numpy(dtype=float)
        weights = network.to_numpy(dtype=float)
        baseline = ols(y, x)
        statistic = residual_moran(baseline.innovations, x, weights)
        records.extend(
            {
                "network": name,
                "estimator": fit.estimator,
                "firms": len(y),
                "premium_quarterly": fit.premium,
                "spatial_coefficient": fit.intensity,
                "stable_unit_interval": abs(fit.intensity) < 1,
                "ml_search_boundary": fit.estimator == "spatial_error_ml"
                and abs(fit.intensity) > 0.985,
                "r_squared_structural": pseudo_r2(y, fit.fitted),
                "shapiro_p": float(shapiro(fit.innovations).pvalue),
                "ols_premium_quarterly": baseline.premium,
                "ols_moran": statistic.statistic,
                "ols_moran_p": statistic.p_value,
                "lag_first_stage_f": first_stage_f(y, x, weights),
            }
            for fit in (lag_iv(y, x, weights), error_ml(y, x, weights))
        )
    return pd.DataFrame(records)


def forecasts(
    prices: pd.DataFrame,
    factors: pd.DataFrame,
    networks: dict[str, FloatArray],
    year: int,
) -> pd.DataFrame:
    """Score full excess-return covariance, with an identical mean across every model."""
    returns = prices.pct_change(fill_method=None).reindex(factors.index).sub(factors["RF"], axis=0)
    train = returns.loc[f"{year - 3}" : str(year - 1)]
    test = returns.loc[str(year)]
    # Same forecast mean for all covariance estimates: prior three-year sample mean.
    centered_test = test.to_numpy(dtype=float) - train.mean().to_numpy(dtype=float)
    covariances = {
        "sample_covariance": np.cov(train.to_numpy(dtype=float), rowvar=False, ddof=1),
        "ledoit_wolf_reference": LedoitWolf().fit(train).covariance_,
    }
    intensities: dict[str, float] = {}
    for label, columns in (("capm", ["Mkt-RF"]), ("ff5_mom", FACTORS)):
        f_train = factors.loc[train.index, columns].to_numpy(dtype=float)
        design = np.column_stack([np.ones(len(train)), f_train])
        coefficients = np.linalg.lstsq(design, train.to_numpy(dtype=float), rcond=None)[0]
        residuals = train.to_numpy(dtype=float) - design @ coefficients
        omega = np.atleast_2d(np.cov(f_train, rowvar=False, ddof=1))
        systematic = coefficients[1:].T @ omega @ coefficients[1:]
        covariances[f"{label}__diagonal"] = systematic + np.diag(np.mean(residuals**2, axis=0))
        covariances[f"{label}__spherical"] = systematic + np.eye(len(prices.columns)) * np.mean(
            residuals**2
        )
        for name, weights in networks.items():
            covariance, intensity = residual_covariance(residuals, weights)
            key = f"{label}__{name}"
            covariances[key], intensities[key] = systematic + covariance, intensity
    rows = []
    for name, covariance in covariances.items():
        loss, _ = daily_scores(centered_test, covariance)
        precision_one = np.linalg.solve(covariance, np.ones(len(covariance)))
        portfolio = precision_one / precision_one.sum()
        portfolio_returns = test.to_numpy(dtype=float) @ portfolio
        rows.append(
            {
                "year": year,
                "model": name,
                "firms": len(prices.columns),
                "gaussian_loss": float(loss.mean()),
                "gmv_volatility": float(portfolio_returns.std(ddof=1) * np.sqrt(252)),
                "lambda": intensities.get(name, np.nan),
            }
        )
    return pd.DataFrame(rows)
