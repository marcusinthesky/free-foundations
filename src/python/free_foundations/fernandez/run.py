"""Run a paper-aligned cross-section and a matched-information forecasting ladder."""

from __future__ import annotations

import argparse
import gc
import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.baselines import compression_states
from free_foundations.expanded.disclosures import input_views
from free_foundations.expanded.distance import pairwise_distance, save_distance
from free_foundations.expanded.encoding import foundation_states, load_tabfm, prepare
from free_foundations.fernandez.characteristics import CHARACTERISTICS, build_panel, history_view
from free_foundations.fernandez.evaluation import (
    cross_section,
    forecasts,
    quarterly_data,
    robust_betas,
)
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.pilot.data import write_json
from free_foundations.pilot.experiment import make_fold

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")


def paper_cross_section(
    panel: pd.DataFrame, prices: pd.DataFrame, factors: pd.DataFrame, output: Path
) -> None:
    """Use ten annual characteristic states and forty quarterly returns, separately per W."""
    tickers = panel.index.get_level_values("ticker").unique()
    quarters = quarterly_data(prices[tickers], factors)
    counts = quarters.groupby("ticker").size()
    complete = counts.index[counts == 40]
    quarters = quarters.loc[quarters["ticker"].isin(complete)]
    betas = robust_betas(quarters, output)
    networks = {}
    for characteristic in CHARACTERISTICS:
        history = (
            panel.reset_index()
            .pivot_table(index="ticker", columns="year", values=characteristic)
            .reindex(columns=range(2015, 2025))
        )
        history = history.dropna()
        history = history.loc[history.max(axis=1) > history.min(axis=1)]
        history = history.loc[history.index.intersection(complete)]
        if len(history) < 5:
            continue
        distance = rank_distance(history.to_numpy(dtype=float))
        for self_links in (False, True):
            label = f"{characteristic}__self_links_{self_links}"
            network = pd.DataFrame(
                paper_weights(distance, self_links=self_links),
                index=history.index,
                columns=history.index,
            )
            networks[label] = network
            destination = output / "cross-sectional-weights" / f"{label}.parquet"
            destination.parent.mkdir(exist_ok=True)
            network.to_parquet(destination)
        # Individual-characteristic learned comparisons retain each original W's cohort.
        view = history_view(panel[[characteristic]], 10)
        labels = panel[[characteristic]].rename(columns={characteristic: "income"})
        labels["operating_cash"] = labels["income"]
        prepared = prepare(view, labels, tuple(history.index), 2025, "income")
        for model in MODELS:
            LOGGER.info("Cross-section %s %s: %s firms", characteristic, model, len(history))
            states = foundation_states(
                prepared, model, Path("research/expanded/cache"), Path("research/pilot/cache")
            )
            distance = pairwise_distance(states["late"])
            label = f"{characteristic}__{model}"
            save_distance(
                output / "cross-sectional-distances" / f"{label}.parquet",
                distance,
                tuple(history.index),
            )
            networks[label] = pd.DataFrame(
                paper_weights(distance), index=history.index, columns=history.index
            )
            load_tabfm.cache_clear()
            gc.collect()
    cross_section(quarters, betas, networks).to_csv(output / "cross-section.csv", index=False)


def annual_ladder(
    panel: pd.DataFrame, source: Path, expanded: Path, output: Path, years: list[int]
) -> None:
    """Hold firms, estimator, kernel, target and time window fixed across each rung."""
    core = pd.read_parquet(source / "accounting.parquet")
    broad = pd.read_parquet(expanded / "cache" / "broad.parquet")
    prices = pd.read_parquet(source / "prices.parquet")
    factors = pd.read_parquet(source / "factors.parquet")
    history = history_view(panel, 4)
    # The support target stays within the original characteristic family.
    labels = panel[["market_cap_assets"]].rename(columns={"market_cap_assets": "income"})
    labels["operating_cash"] = labels["income"]
    results: list[pd.DataFrame] = []
    cohorts: list[dict[str, object]] = []
    inventory: list[dict[str, str | int]] = []
    for year in years:
        fold = make_fold(prices, factors, core, year)
        query = pd.DataFrame(history.xs(year - 1, level="year")).reindex(fold.query.index)
        valid = query.notna().all(axis=1)
        for characteristic in CHARACTERISTICS:
            values = query.filter(like=f"{characteristic}__")
            valid &= values.max(axis=1) > values.min(axis=1)
        tickers = tuple(query.index[valid])
        cohorts.append(
            {
                "year": year,
                "eligible_original": len(query),
                "matched_complete": len(tickers),
                "tickers": tickers,
            }
        )
        write_json(output / "cohorts.json", cohorts)
        if len(tickers) < 5:
            LOGGER.warning(
                "Skipping %s: only %s complete nonconstant matched histories", year, len(tickers)
            )
            continue
        networks: dict[str, FloatArray] = {}
        distances: dict[str, FloatArray] = {}
        for characteristic in CHARACTERISTICS:
            values = (
                query.loc[list(tickers)].filter(like=f"{characteristic}__").to_numpy(dtype=float)
            )
            distances[f"paper__{characteristic}"] = rank_distance(values)
        distances["paper__joint_rms"] = np.sqrt(np.mean([d**2 for d in distances.values()], axis=0))
        views = {
            "same_four_histories": history,
            "four_plus_broad": pd.concat(
                [history, input_views(core, broad, year)["broad"].reindex(history.index)], axis=1
            ),
        }
        for view_name, view in views.items():
            prepared = prepare(view, labels, tickers, year, "income")
            write_json(
                output / f"context-{year}-{view_name}.json",
                {
                    "features": prepared.features,
                    "support_ids": prepared.support_ids,
                    "digest": prepared.digest,
                    "target": "next snapshot market_cap_assets",
                    "tickers": tickers,
                },
            )
            # A non-pretrained control sees exactly the same transformed table.
            vectors = prepared.query
            # Normalize with an intercept coordinate so all-zero standardized rows are defined.
            distances[f"{view_name}__direct"] = pairwise_distance(
                np.column_stack([vectors, np.ones(len(vectors))])
            )
            for compression, states in compression_states(prepared).items():
                distances[f"{view_name}__{compression}"] = pairwise_distance(states)
            for model in MODELS:
                LOGGER.info("%s %s %s: %s firms", year, view_name, model, len(tickers))
                states = foundation_states(prepared, model, expanded / "cache", source)
                distances[f"{view_name}__{model}"] = pairwise_distance(states["late"])
                load_tabfm.cache_clear()
                gc.collect()
        for name, distance in distances.items():
            destination = output / "distances" / str(year) / f"{name}.parquet"
            save_distance(destination, distance, tickers)
            networks[name] = paper_weights(distance)
            inventory.append(
                {
                    "year": year,
                    "as_of": f"{year - 1}-12-31",
                    "model": name,
                    "firms": len(tickers),
                    "path": str(destination.relative_to(output)),
                }
            )
        annual = forecasts(prices[list(tickers)], factors, networks, year)
        annual.to_csv(output / f"annual-{year}.csv", index=False)
        results.append(annual)
        pd.concat(results).to_csv(output / "annual.csv", index=False)
        pd.DataFrame(inventory).to_csv(output / "distance-inventory.csv", index=False)
    if results:
        pd.concat(results).groupby("model")[["gaussian_loss", "gmv_volatility"]].mean().sort_values(
            "gaussian_loss"
        ).to_csv(output / "summary.csv")
    write_json(
        output / "execution-status.json",
        {
            "status": "complete",
            "requested_years": years,
            "completed_years": [int(frame["year"].iloc[0]) for frame in results],
            "distance_matrices": len(inventory),
        },
    )


def main() -> None:
    """Reuse immutable market/factor/model caches; new data and results live separately."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("research/fernandez"))
    parser.add_argument("--years", type=int, nargs="+", default=list(range(2016, 2026)))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    source, expanded = Path("research/pilot/cache"), Path("research/expanded")
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output / "execution-status.json", {"status": "running"})
    panel = build_panel(source, expanded, args.output)
    prices, factors = (
        pd.read_parquet(source / "prices.parquet"),
        pd.read_parquet(source / "factors.parquet"),
    )
    paper_cross_section(panel, prices, factors, args.output)
    annual_ladder(panel, source, expanded, args.output, args.years)
    paths = [
        *Path(__file__).parent.glob("*.*"),
        source / "prices.parquet",
        source / "factors.parquet",
        args.output / "cache" / "characteristics.parquet",
    ]
    write_json(
        args.output / "manifest.json",
        {
            "sha256": {
                str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in paths
                if path.is_file()
            },
            "paper_sha256": "7391cb6ed0b986ff3dffd3f0870b7a3a5f94a2291f773d0ebed0a91149bfbabe",
            "classification": (
                "US methodological replication and retrospective forecasts; "
                "not original Economatica sample replication"
            ),
        },
    )


if __name__ == "__main__":
    main()
