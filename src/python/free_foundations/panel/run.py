"""Run each declared panel design: calibrate on 2016-2019, score 2020-2025."""

from __future__ import annotations

import argparse
import logging
from typing import TYPE_CHECKING

import pandas as pd

from free_foundations.panel.characteristics import build
from free_foundations.panel.design import DESIGNS
from free_foundations.panel.evaluation import (
    CALIBRATION,
    EVALUATION,
    PLACEBO_DRAWS,
    PLACEBO_ROWS,
    Panel,
    comparison,
    daily_frame,
    placebo_table,
    update,
)
from free_foundations.panel.inference import BLOCKS, REPLICATES, confidence_set, paired
from free_foundations.panel.networks import distances
from free_foundations.panel.observations import annual_data
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.panel.design import Design

LOGGER = logging.getLogger(__name__)
YEARS = (*CALIBRATION, *EVALUATION)
ALTERNATE = "next snapshot NetIncomeLoss/Assets"


def run_design(
    design: Design,
    four: pd.DataFrame,
    broad: pd.DataFrame,
    models: tuple[str, ...] | None = None,
) -> None:
    """Hold firms, dates, kernels and estimators fixed across every approach in a design."""
    output = design.output
    output.mkdir(parents=True, exist_ok=True)
    panel = Panel()
    firm_days = 0
    for year in YEARS:
        annual = annual_data(
            four,
            year,
            characteristics=design.characteristics,
            histories=design.cohort_histories,
            output=output,
        )
        LOGGER.info(
            "%s %s: %s firms, %s days", design.name, year, len(annual.tickers), len(annual.dates)
        )
        built = distances(four, broad, year, annual.tickers, design, models=models)
        update(panel, year, annual, built, broad)
        if year in EVALUATION:
            firm_days += annual.realized.size
    daily = daily_frame(panel)
    daily.to_parquet(output / "daily-scores.parquet")
    comparison(panel, daily, firm_days).to_csv(output / "comparison.csv", index=False)
    pd.DataFrame(panel.annual).to_csv(output / "annual-scores.csv", index=False)
    pd.DataFrame(panel.geometry).to_csv(output / "geometry.csv", index=False)
    placebo_table(daily).to_csv(output / "placebo.csv", index=False)
    paired(daily).to_csv(output / "bootstrap.csv", index=False)
    confidence_set(daily).to_csv(output / "mcs.csv", index=False)
    write_json(
        output / "configuration.json",
        {
            "design": design.name,
            "characteristics": design.characteristics,
            "history_years": design.history,
            "extra_history_years": design.extra_histories,
            "cohort_history_years": design.cohort_histories,
            "rungs": design.rungs,
            "alternate_target": ALTERNATE if design.alternate_target else None,
            "calibration": [CALIBRATION[0], CALIBRATION[-1]],
            "evaluation": [EVALUATION[0], EVALUATION[-1]],
            "prior_return_years": 3,
            "minimum_prior_returns": 500,
            "exclude_first_return_each_year": True,
            "support_cap": 256,
            "kernels": {
                "exp": "exp(-d), zero diagonal, row normalized (equation 10)",
                "median": "exp(-d/m), m = median positive off-diagonal distance",
                "matched": "exp(-d/h), h matches that year's joint Fernandez effective neighbours",
            },
            "innovations": {
                "spherical": "sigma^2 I per year (paper-aligned reference)",
                "diagonal": "one variance per firm and year, same rule for every network",
                "correlation": "diagonal-arm correlation with prior raw sample variances",
            },
            "lambda": "one per network, kernel and innovation arm, fitted on calibration years",
            "placebo": {
                "rows": PLACEBO_ROWS,
                "draws": PLACEBO_DRAWS,
                "restriction": "within prior-year log-assets terciles",
            },
            "bootstrap": {
                "method": "arch StationaryBootstrap",
                "expected_blocks": BLOCKS,
                "replicates": REPLICATES,
                "seed": 42,
            },
            "mcs": {"size": 0.10, "method": "max", "block": 21, "replicates": 1000},
        },
    )
    LOGGER.info("Completed design %s with %s scored columns", design.name, daily.shape[1])


def main() -> None:
    """Run the requested designs; foundation-model readouts are cached by context."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--designs", nargs="+", default=list(DESIGNS), choices=list(DESIGNS))
    parser.add_argument("--models", nargs="*", default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    four, broad = build()
    models = None if args.models is None else tuple(args.models)
    for name in args.designs:
        run_design(DESIGNS[name], four, broad, models)


if __name__ == "__main__":
    main()
