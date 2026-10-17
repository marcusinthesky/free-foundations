"""Annual walk-forward FF5+momentum residual-network and covariance comparisons."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA

from free_foundations.pilot.features import FEATURES
from free_foundations.pilot.representations import pretrained_vectors, standardized
from free_foundations.pilot.spatial import (
    daily_scores,
    fit_spatial,
    history_weights,
    kernel_weights,
    moran,
)

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
FACTORS = ["Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom"]


@dataclass(frozen=True)
class Fold:
    """One common eligible firm cohort, with frozen factor coefficients."""

    query: pd.DataFrame
    history: FloatArray
    train: FloatArray
    test: FloatArray
    scales: FloatArray
    dates: pd.DatetimeIndex


def make_fold(prices: pd.DataFrame, factors: pd.DataFrame, panel: pd.DataFrame, year: int) -> Fold:
    """Use three prior return years; exclude incomplete histories explicitly."""
    returns = prices.pct_change(fill_method=None).reindex(factors.index)
    train_dates = (returns.index >= f"{year - 3}-01-01") & (returns.index < f"{year}-01-01")
    test_dates = (returns.index >= f"{year}-01-01") & (returns.index < f"{year + 1}-01-01")
    history = (
        panel.reset_index()
        .pivot_table(index="ticker", columns="year", values="log_assets")
        .reindex(columns=range(year - 4, year))
    )
    valid = returns.loc[train_dates | test_dates].notna().all()
    eligible = history.dropna().index.intersection(valid.index[valid])
    query = pd.DataFrame(panel.xs(year - 1, level="year")).reindex(eligible)[list(FEATURES)]
    if len(query) < 30:
        message = f"Only {len(query)} eligible firms for {year}."
        raise ValueError(message)
    excess = returns[eligible].sub(factors["RF"], axis=0).to_numpy(dtype=float)
    design = np.column_stack([np.ones(len(factors)), factors[FACTORS].to_numpy(dtype=float)])
    coefficients = np.linalg.lstsq(design[train_dates], excess[train_dates], rcond=None)[0]
    residuals = excess - design @ coefficients
    scales = residuals[train_dates].std(axis=0, ddof=1)
    return Fold(
        query=query,
        history=history.loc[eligible].to_numpy(dtype=float),
        train=residuals[train_dates] / scales,
        test=residuals[test_dates] / scales,
        scales=scales,
        dates=pd.DatetimeIndex(returns.index[test_dates]),
    )


def candidate_networks(fold: Fold) -> dict[str, FloatArray]:
    """Fixed, untuned accounting and random-projection benchmarks."""
    vectors = standardized(fold.query.to_numpy(dtype=float))
    rng = np.random.default_rng(42)
    projection = rng.normal(size=(vectors.shape[1], 8)) / np.sqrt(8)
    return {
        "fernandez_assets_history": history_weights(fold.history),
        "size": kernel_weights(vectors[:, :1]),
        "leverage": kernel_weights(vectors[:, 1:2]),
        "accounting": kernel_weights(vectors),
        "pca_5": kernel_weights(PCA(n_components=5).fit_transform(vectors)),
        "random_projection_8": kernel_weights(vectors @ projection),
    }


def evaluate_networks(
    fold: Fold, networks: dict[str, FloatArray], year: int
) -> tuple[list[dict[str, str | int | float]], list[pd.DataFrame]]:
    """Fit on training residuals and score once on the following calendar year."""
    summary: list[dict[str, str | int | float]] = []
    daily: list[pd.DataFrame] = []
    covariances = {
        "diagonal": np.diag(np.mean(fold.train**2, axis=0)),
        "ledoit_wolf": LedoitWolf(assume_centered=True).fit(fold.train).covariance_,
    }
    intensities = {}
    for name, weights in networks.items():
        fitted = fit_spatial(weights, fold.train)
        covariances[name], intensities[name] = fitted.covariance, fitted.intensity
    for name, covariance in covariances.items():
        # Restore original return units for both likelihood and portfolio weights.
        return_covariance = covariance * np.outer(fold.scales, fold.scales)
        loss, risk = daily_scores(fold.test * fold.scales, return_covariance)
        spatial = (
            moran(fold.test, networks[name]) if name in networks else np.full(len(loss), np.nan)
        )
        summary.append(
            {
                "year": year,
                "model": name,
                "firms": len(fold.query),
                "lambda": intensities.get(name, np.nan),
                "gaussian_loss": loss.mean(),
                "gmv_volatility": np.sqrt(252 * risk.mean()),
                "moran_i": np.nan if name not in networks else spatial.mean(),
            }
        )
        daily.append(
            pd.DataFrame(
                {
                    "date": fold.dates,
                    "year": year,
                    "model": name,
                    "gaussian_loss": loss,
                    "gmv_squared_return": risk,
                    "moran_i": spatial,
                }
            )
        )
    return summary, daily


def run_experiment(
    prices: pd.DataFrame,
    factors: pd.DataFrame,
    panel: pd.DataFrame,
    cache: Path,
    *,
    pretrained: bool,
) -> None:
    """Run ten held-out years, saving fold outputs incrementally for auditability."""
    summaries: list[dict[str, str | int | float]] = []
    daily: list[pd.DataFrame] = []
    cohorts: dict[str, list[str]] = {}
    for year in range(2016, 2026):
        fold = make_fold(prices, factors, panel, year)
        networks = candidate_networks(fold)
        if pretrained:
            vectors = pretrained_vectors(panel, fold.query, year, cache)
            networks["tabpfn_fast"] = kernel_weights(vectors)
            permutation = np.random.default_rng(42).permutation(len(vectors))
            networks["tabpfn_shuffled"] = networks["tabpfn_fast"][np.ix_(permutation, permutation)]
        result, observations = evaluate_networks(fold, networks, year)
        summaries.extend(result)
        daily.extend(observations)
        cohorts[str(year)] = fold.query.index.tolist()
        pd.DataFrame(summaries).to_csv(cache.parent / "annual.csv", index=False)
        pd.concat(daily).to_parquet(cache / "daily-scores.parquet", index=False)
        (cache.parent / "cohorts.json").write_text(json.dumps(cohorts, indent=2) + "\n")
        LOGGER.info("Completed %s: %s firms, %s networks", year, len(fold.query), len(networks))
