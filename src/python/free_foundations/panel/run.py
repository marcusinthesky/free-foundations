"""Run the matched annual ladder, calibrating intensity before the held-out period."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.distance import save_distance
from free_foundations.panel.characteristics import ROOT, build
from free_foundations.panel.likelihood import block, fit, gaussian_score
from free_foundations.panel.networks import networks
from free_foundations.panel.observations import annual_data
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.panel.likelihood import Block

LOGGER = logging.getLogger(__name__)
YEARS = tuple(range(2016, 2026))


def run() -> None:
    """Fit one intensity on 2016-2019, then sum untouched 2020-2025 log scores."""
    four, broad = build()
    (ROOT / "contexts").mkdir(exist_ok=True)
    calibration: dict[str, list[Block]] = {}
    evaluation: dict[str, list[tuple[int, Block, Block, FloatArray, FloatArray, FloatArray]]] = {}
    controls: list[dict[str, str | int | float]] = []
    for year in YEARS:
        tickers, prior, realized, raw_prior, raw_realized, factor_covariance = annual_data(
            four, year
        )
        LOGGER.info("Panel %s: %s firms, %s observed days", year, len(tickers), len(realized))
        weights = networks(four, broad, year, tickers)
        weights["ff5_mom_spherical"] = np.zeros((len(tickers), len(tickers)))
        weights["uniform_network"] = (
            np.ones((len(tickers), len(tickers))) - np.eye(len(tickers))
        ) / (len(tickers) - 1)
        for name, matrix in weights.items():
            save_distance(ROOT / "weights" / str(year) / f"{name}.parquet", matrix, tickers)
            current = block(realized, matrix)
            if year < 2020:
                calibration.setdefault(name, []).append(current)
            else:
                evaluation.setdefault(name, []).append(
                    (
                        year,
                        current,
                        block(prior, matrix),
                        matrix,
                        raw_realized - raw_prior.mean(axis=0),
                        factor_covariance,
                    )
                )
        if year >= 2020:
            for name, values, covariance in (
                (
                    "raw_sample_covariance",
                    raw_realized - raw_prior.mean(axis=0),
                    np.cov(raw_prior, rowvar=False),
                ),
                (
                    "ff5_mom_diagonal",
                    raw_realized - raw_prior.mean(axis=0),
                    factor_covariance + np.diag(np.mean(prior**2, axis=0)),
                ),
                (
                    "ff5_mom_sample_residual_covariance",
                    raw_realized - raw_prior.mean(axis=0),
                    factor_covariance + np.cov(prior, rowvar=False),
                ),
            ):
                controls.append(
                    {
                        "approach": str(name),
                        "year": year,
                        "score": gaussian_score(values, covariance),
                        "firm_days": int(realized.size),
                    }
                )
    records: list[dict[str, str | float | int | bool]] = []
    yearly: list[dict[str, str | float | int]] = []
    for name, blocks in calibration.items():
        intensity, train_score = (
            (0.0, sum(item.score(0.0) for item in blocks))
            if name == "ff5_mom_spherical"
            else fit(blocks)
        )
        score = 0.0
        observations = 0
        for year, current, previous, matrix, values, factor_covariance in evaluation[name]:
            inverse = np.linalg.solve(
                np.eye(current.firms) - intensity * matrix, np.eye(current.firms)
            )
            covariance = factor_covariance + previous.variance(intensity) * inverse @ inverse.T
            value = gaussian_score(values, covariance)
            score += value
            observations += current.days * current.firms
            yearly.append(
                {
                    "approach": str(name),
                    "year": year,
                    "score": value,
                    "firm_days": current.days * current.firms,
                }
            )
        records.append(
            {
                "approach": str(name),
                "lambda": intensity,
                "calibration_ml_log_likelihood": train_score,
                "heldout_log_likelihood": score,
                "firm_days": observations,
                "boundary": abs(intensity) >= 0.985,
            }
        )
    for name, group in pd.DataFrame(controls).groupby("approach"):
        records.append(
            {
                "approach": str(name),
                "lambda": np.nan,
                "calibration_ml_log_likelihood": np.nan,
                "heldout_log_likelihood": group["score"].sum(),
                "firm_days": group["firm_days"].sum(),
                "boundary": False,
            }
        )
    result = pd.DataFrame(records).set_index("approach")
    result["gain_vs_joint_four"] = result["heldout_log_likelihood"] - float(
        result["heldout_log_likelihood"].loc["fernandez_joint_four"]
    )
    result["score_per_firm_day"] = result["heldout_log_likelihood"] / result["firm_days"]
    result.to_csv(ROOT / "comparison.csv")
    pd.DataFrame([*yearly, *controls]).to_csv(ROOT / "annual-scores.csv", index=False)
    write_json(
        ROOT / "configuration.json",
        {
            "calibration": [2016, 2019],
            "evaluation": [2020, 2025],
            "history_years": 3,
            "prior_return_years": 3,
            "minimum_prior_returns": 500,
            "exclude_first_return_each_year": True,
            "support_cap": 256,
            "kernel": "exp(-distance), zero diagonal, row normalized",
            "distance": "Spearman chord for Fernandez; unit-sphere chord for embeddings",
            "lambda": "one constant per approach fitted only on calibration years",
            "score": "unconditional Gaussian; prior factor plus spatial residual covariance",
            "innovation_variance": "spherical; prior three-year residuals at fixed lambda",
        },
    )
    LOGGER.info("Completed %s approaches", len(result))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()
