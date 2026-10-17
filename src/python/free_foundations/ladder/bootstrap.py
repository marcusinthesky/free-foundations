"""Generated-beta uncertainty: resample quarters, re-estimate MM exposures, keep W fixed."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from arch.bootstrap import StationaryBootstrap

from free_foundations.fernandez.evaluation import robust_betas
from free_foundations.fernandez.models import error_ml, lag_iv, ols, symmetric_spectrum

if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
REPLICATES, SPARE, BLOCK = 199, 60, 4


def quarter_indices(quarters: tuple[str, ...], seed: int = 42) -> pd.DataFrame:
    """Stationary-bootstrap quarter orders (expected block four quarters), shared by all."""
    bootstrap = StationaryBootstrap(BLOCK, np.arange(len(quarters)), seed=seed)
    rows = [
        (replicate, position, quarters[index])
        for replicate, (arguments, _) in enumerate(bootstrap.bootstrap(REPLICATES + SPARE), 1)
        for position, index in enumerate(np.asarray(arguments[0], dtype=int).tolist())
    ]
    return pd.DataFrame(rows, columns=["replicate", "position", "quarter"])


def resample(  # noqa: PLR0913 -- sample, terms, indices and an output location.
    quarters: pd.DataFrame,
    *,
    tickers: tuple[str, ...],
    terms: tuple[str, ...],
    indices: pd.DataFrame,
    output: Path,
    tag: str,
) -> tuple[dict[int, pd.DataFrame], dict[int, pd.Series], int]:
    """Exposures and medians for the first valid replicates; returns the rejection count."""
    sample = quarters.loc[quarters["ticker"].isin(tickers)]
    estimates = robust_betas(sample, output, terms=terms, indices=indices, cores=6, tag=tag)
    estimates.to_parquet(output / f"bootstrap-{tag}.parquet")
    (output / "cache" / f"mm-{tag}-output.csv").unlink(missing_ok=True)
    outcomes = sample.pivot_table(index="date", columns="ticker", values="excess")
    outcomes.index = pd.DatetimeIndex(outcomes.index).strftime("%Y-%m-%d")
    exposures: dict[int, pd.DataFrame] = {}
    medians: dict[int, pd.Series] = {}
    rejected = 0
    for replicate in np.unique(estimates["replicate"].to_numpy(dtype=int)):
        group = estimates.loc[estimates["replicate"].eq(replicate)]
        slopes = group.loc[group["term"].ne("intercept")]
        if not (slopes["converged"].all() and np.isfinite(slopes["estimate"]).all()):
            rejected += 1
            continue
        if len(exposures) == REPLICATES:
            break
        order = indices.loc[indices["replicate"].eq(replicate)].sort_values("position")
        exposures[int(replicate)] = slopes.pivot_table(
            index="ticker", columns="term", values="estimate"
        )[list(terms)]
        medians[int(replicate)] = outcomes.loc[order["quarter"]].median()
    if len(exposures) < REPLICATES:
        message = f"Only {len(exposures)} valid bootstrap replicates for {tag}."
        raise RuntimeError(message)
    return exposures, medians, rejected


def refit(
    y: FloatArray, x: FloatArray, weights: FloatArray, spectrum: FloatArray
) -> dict[str, float]:
    """Point estimates only: OLS premium, S2SLS and SEM premium and coefficient."""
    iv = lag_iv(y, x, weights)
    sem = error_ml(y, x, weights, eigenvalues=spectrum, standard_errors=False, xatol=None)
    return {
        "ols_premium": ols(y, x).premium,
        "iv_premium": iv.premium,
        "iv_intensity": iv.intensity,
        "sem_premium": sem.premium,
        "sem_intensity": sem.intensity,
    }


def network_draws(
    networks: dict[str, FloatArray],
    tickers: tuple[str, ...],
    exposures: dict[int, pd.DataFrame],
    medians: dict[int, pd.Series],
) -> pd.DataFrame:
    """Refit every fixed network on every valid replicate."""
    rows = []
    for name, weights in networks.items():
        spectrum = symmetric_spectrum(weights)
        for replicate, frame in exposures.items():
            x = frame.loc[list(tickers)].to_numpy(dtype=float)
            y = medians[replicate].loc[list(tickers)].to_numpy(dtype=float)
            rows.append({"network": name, "replicate": replicate} | refit(y, x, weights, spectrum))
    return pd.DataFrame(rows)


def percentile(level: float) -> Callable[[pd.Series], float]:
    """A named aggregation returning one percentile of the bootstrap draws."""

    def compute(values: pd.Series) -> float:
        return float(np.percentile(values.to_numpy(dtype=float), level))

    return compute


def summarize(draws: pd.DataFrame) -> pd.DataFrame:
    """Bootstrap standard errors and 95% percentile intervals per network and parameter."""
    long = draws.melt(id_vars=["network", "replicate"], var_name="parameter")
    return (
        long.groupby(["network", "parameter"])["value"]
        .agg(
            bootstrap_se="std",
            lower=percentile(2.5),
            upper=percentile(97.5),
            replicates="size",
        )
        .reset_index()
    )
