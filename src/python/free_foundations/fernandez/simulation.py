"""Reproduce Section 4's stated calibration, without tuning to match Table 6."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import norm

from free_foundations.fernandez.models import paper_weights

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


def portfolio_var(beta: FloatArray, weights: FloatArray, intensity: float) -> tuple[float, float]:
    """Equations (8a)-(8b): V0=1000, alpha=.95, sigma_market=sigma_innovation=.01."""
    allocation = np.full(len(beta), 1 / len(beta))
    exposure = np.linalg.solve((np.eye(len(beta)) - intensity * weights).T, allocation)
    idiosyncratic = float(exposure @ exposure)
    multiplier = 1000 * float(norm.ppf(0.95)) * 0.01
    lag = multiplier * np.sqrt((exposure @ beta) ** 2 + idiosyncratic)
    error = multiplier * np.sqrt((allocation @ beta) ** 2 + idiosyncratic)
    return float(lag), float(error)


def simulate(output: Path, repetitions: int = 200) -> None:
    """Use symmetric uniform pairwise draws; these need not form a PSD correlation matrix."""
    rng = np.random.default_rng(42)
    rows = []
    for firms in (20, 40, 80, 150, 300):
        for repetition in range(repetitions):
            upper = np.triu(rng.uniform(-1, 1, (firms, firms)), 1)
            correlation = upper + upper.T + np.eye(firms)
            weights = paper_weights(np.sqrt(2 * (1 - correlation)))
            uniforms = rng.uniform(size=firms)
            for case, lower in ((1, 0.5), (2, -0.5)):
                beta = lower + (1 - lower) * uniforms
                for intensity in (0.0, 0.1, 0.5, 0.8):
                    lag, error = portfolio_var(beta, weights, intensity)
                    rows.append(
                        {
                            "case": case,
                            "firms": firms,
                            "repetition": repetition,
                            "intensity": intensity,
                            "spatial_lag_var": lag,
                            "spatial_error_var": error,
                        }
                    )
    frame = pd.DataFrame(rows)
    summary = frame.groupby(["case", "firms", "intensity"])[
        ["spatial_lag_var", "spatial_error_var"]
    ].agg(["mean", "std", "sem"])
    summary.columns = ["_".join(column) for column in summary.columns]
    summary.to_csv(output / "simulation.csv")


if __name__ == "__main__":
    simulate(Path("research/fernandez"))
