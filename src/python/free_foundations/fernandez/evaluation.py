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

from free_foundations.fernandez.models import error_ml, lag_iv, residual_covariance
from free_foundations.pilot.experiment import FACTORS
from free_foundations.pilot.spatial import daily_scores, moran

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


def quarterly_data(prices: pd.DataFrame, factors: pd.DataFrame) -> pd.DataFrame:
    """Compound daily total returns and RF separately before computing quarterly excess."""
    returns = prices.pct_change(fill_method=None).reindex(factors.index)
    quarterly = (1 + returns).resample("QE").prod(min_count=1) - 1
    counts = returns.resample("QE").count()
    quarterly = quarterly.where(counts.eq(returns.resample("QE").size(), axis=0))
    risk_free = (1 + factors["RF"]).resample("QE").prod() - 1
    market = (1 + factors["Mkt-RF"] + factors["RF"]).resample("QE").prod() - 1 - risk_free
    quarterly = quarterly.sub(risk_free, axis=0)
    frame = (
        quarterly.rename_axis(index="date")
        .reset_index()
        .melt(id_vars="date", var_name="ticker", value_name="excess")
        .dropna()
    )
    frame["market"] = frame["date"].map(market)
    return frame.loc[frame["date"].between("2016-01-01", "2025-12-31")]


def robust_betas(quarters: pd.DataFrame, output: Path) -> pd.DataFrame:
    """Call the established MM implementation rather than relabel OLS or Huber estimates."""
    source, destination = output / "quarterly-returns.csv", output / "mm-betas.csv"
    quarters.to_csv(source, index=False)
    executable = shutil.which("Rscript")
    if executable is None:
        message = "Run inside devenv shell: robustbase's Rscript runtime is required."
        raise RuntimeError(message)
    subprocess.run(  # noqa: S603 -- fixed local R script and generated data paths.
        [executable, str(Path(__file__).with_name("betas.R")), str(source), str(destination)],
        check=True,
    )
    result = pd.read_csv(destination).set_index("ticker")
    if not result["converged"].all():
        message = "At least one robust MM beta did not converge."
        raise RuntimeError(message)
    return result


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
        ols = x @ np.linalg.lstsq(x, y, rcond=None)[0]
        instruments = np.column_stack([x, weights @ x])
        endogenous = weights @ y
        restricted = endogenous - x @ np.linalg.lstsq(x, endogenous, rcond=None)[0]
        unrestricted = (
            endogenous - instruments @ np.linalg.lstsq(instruments, endogenous, rcond=None)[0]
        )
        restricted_ss, unrestricted_ss = (
            float(restricted @ restricted),
            float(unrestricted @ unrestricted),
        )
        first_stage_f = (restricted_ss - unrestricted_ss) / (unrestricted_ss / (len(y) - 2))

        for estimator, fit in (
            ("spatial_lag_iv", lag_iv(y, x, weights)),
            ("spatial_error_ml", error_ml(y, x, weights)),
        ):
            records.append(
                {
                    "network": name,
                    "estimator": estimator,
                    "firms": len(y),
                    "premium_quarterly": fit.premium,
                    "spatial_coefficient": fit.intensity,
                    "stable_unit_interval": abs(fit.intensity) < 1,
                    "ml_search_boundary": estimator == "spatial_error_ml"
                    and abs(fit.intensity) > 0.985,
                    "r_squared_structural": float(np.corrcoef(y, fit.fitted)[0, 1] ** 2),
                    "shapiro_p": float(shapiro(fit.innovations).pvalue),
                    "ols_premium_quarterly": float(np.linalg.lstsq(x, y, rcond=None)[0][0]),
                    "ols_moran": float(moran((y - ols)[None, :], weights)[0]),
                    "lag_first_stage_f": first_stage_f,
                }
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
