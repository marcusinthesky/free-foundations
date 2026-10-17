"""Reproducible expanded model/input/metric comparison with yearly distance artifacts."""

from __future__ import annotations

import argparse
import gc
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.baselines import (
    compression_states,
    group_permutation,
    industry_vectors,
)
from free_foundations.expanded.disclosures import build_disclosures, input_views
from free_foundations.expanded.distance import (
    Metric,
    distance_weights,
    pairwise_distance,
    save_distance,
)
from free_foundations.expanded.encoding import foundation_states, load_tabfm, prepare
from free_foundations.expanded.setup import ensure_checkpoints, ensure_industry, write_manifest
from free_foundations.pilot.data import write_json
from free_foundations.pilot.experiment import candidate_networks, evaluate_networks, make_fold

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")
TARGETS = ("income", "operating_cash")
METRICS: tuple[Metric, ...] = ("chord", "euclidean")


@dataclass
class Networks:
    """Collect weights and labeled distance artifacts for one annual cohort."""

    output: Path
    year: int
    tickers: tuple[str, ...]
    permutations: dict[str, np.ndarray]
    weights: dict[str, FloatArray]
    inventory: list[dict[str, str | int | float]] = field(default_factory=list)

    def add(self, name: str, vectors: FloatArray, metric: Metric = "euclidean") -> None:
        """Persist labeled distances and derive weights without selecting on returns."""
        distances = pairwise_distance(vectors, metric)
        weights, bandwidth = distance_weights(distances)
        key = f"{name}__{metric}"
        self.weights[key] = weights
        destination = self.output / "distances" / str(self.year) / f"{key}.parquet"
        save_distance(destination, distances, self.tickers)
        off_diagonal = distances[np.triu_indices(len(self.tickers), 1)]
        self.inventory.append(
            {
                "year": self.year,
                "representation": name,
                "metric": metric,
                "firms": len(self.tickers),
                "dimensions": vectors.shape[1],
                "bandwidth_squared": bandwidth,
                "mean_distance": float(off_diagonal.mean()),
                "distance_cv": float(off_diagonal.std() / off_diagonal.mean())
                if off_diagonal.mean()
                else 0.0,
                "path": str(destination.relative_to(self.output)),
                "as_of": f"{self.year - 1}-12-31",
            }
        )
        if metric == "chord" and name.endswith("late"):
            for label, permutation in self.permutations.items():
                self.weights[f"{key}__{label}"] = weights[np.ix_(permutation, permutation)]


def run(output: Path, source: Path, years: list[int]) -> None:
    """Evaluate predetermined configurations; preserve the original pilot's cohorts."""
    write_json(output / "execution-status.json", {"status": "running", "years": years})
    cache = output / "cache"
    broad, ages = build_disclosures(source, cache)
    core = pd.read_parquet(source / "accounting.parquet")
    prices, factors = (
        pd.read_parquet(source / "prices.parquet"),
        pd.read_parquet(source / "factors.parquet"),
    )
    industry = pd.read_csv(output / "industry.csv", dtype={"sic": str})
    universe = pd.read_csv(source.parent / "universe.csv")
    summaries: list[dict[str, str | float | int]] = []
    inventory: list[dict[str, str | int | float]] = []
    for year in years:
        fold = make_fold(prices[universe["ticker"]], factors, core, year)
        tickers = tuple(fold.query.index)
        networks = candidate_networks(fold)
        views = input_views(core, broad, year)
        groups = industry_vectors(industry, tickers)
        industry_groups = np.argmax(groups, axis=1).astype(float)
        size_groups = pd.qcut(fold.query["log_assets"], 4, labels=False).to_numpy(dtype=float)
        permutations = {
            "shuffled": np.random.default_rng(42).permutation(len(tickers)),
            "industry_shuffled": group_permutation(industry_groups),
            "size_shuffled": group_permutation(size_groups),
        }

        artifacts = Networks(output, year, tickers, permutations, networks)

        artifacts.add("industry_current_sic", groups)
        for view_name, view in views.items():
            query = pd.DataFrame(view.xs(year - 1, level="year")).reindex(tickers)
            artifacts.add(f"{view_name}__missingness", query.isna().to_numpy(dtype=float))
            if view_name == "broad":
                age = pd.DataFrame(ages.xs(year - 1, level="year")).reindex(
                    index=tickers, columns=view.columns
                )
                artifacts.add("broad__disclosure_age", age.fillna(550).to_numpy(dtype=float) / 550)
            baseline = prepare(view, core, tickers, year, "income")
            artifacts.add(f"{view_name}__standardized", baseline.query)
            for compression, vectors in compression_states(baseline).items():
                for metric in METRICS:
                    artifacts.add(f"{view_name}__{compression}", vectors, metric)
            for target in TARGETS:
                data = prepare(view, core, tickers, year, target)
                schema = output / "schemas" / f"{year}-{view_name}-{target}.json"
                schema.parent.mkdir(exist_ok=True)
                write_json(
                    schema,
                    {
                        "columns": data.features,
                        "support_ids": data.support_ids,
                        "query_tickers": tickers,
                        "context_digest": data.digest,
                        "target": f"next snapshot {target}/assets",
                        "query_as_of": f"{year - 1}-12-31",
                    },
                )
                for model in MODELS:
                    LOGGER.info(
                        "%s %s %s %s: %s features, %s support rows",
                        year,
                        view_name,
                        target,
                        model,
                        len(data.features),
                        len(data.support),
                    )
                    states = foundation_states(data, model, cache, source)
                    for readout, vectors in states.items():
                        for metric in METRICS:
                            artifacts.add(
                                f"{view_name}__{target}__{model}__{readout}", vectors, metric
                            )
                    load_tabfm.cache_clear()
                    gc.collect()
        inventory.extend(artifacts.inventory)
        annual, daily = evaluate_networks(fold, networks, year)
        summaries.extend(annual)
        pd.DataFrame(annual).to_csv(output / f"annual-{year}.csv", index=False)
        pd.concat(daily).to_parquet(cache / f"scores-{year}.parquet", index=False)
        pd.DataFrame(inventory).to_csv(output / "distance-inventory.csv", index=False)
        pd.DataFrame(summaries).to_csv(output / "annual.csv", index=False)
        LOGGER.info("Completed expanded %s: %s networks", year, len(networks))
    results = pd.DataFrame(summaries)
    results.groupby("model")[["gaussian_loss", "gmv_volatility", "moran_i"]].mean().sort_values(
        "gaussian_loss"
    ).to_csv(output / "summary.csv")
    write_json(
        output / "execution-status.json",
        {
            "status": "complete",
            "years": years,
            "models": MODELS,
            "targets": TARGETS,
            "metrics": METRICS,
            "distance_matrices": len(inventory),
            "classification": "development evidence; historical evaluation already examined",
        },
    )


def main() -> None:
    """Run a bounded development comparison without refreshing original inputs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("research/expanded"))
    parser.add_argument("--source", type=Path, default=Path("research/pilot/cache"))
    parser.add_argument("--years", nargs="+", type=int, default=list(range(2016, 2026)))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ.setdefault("TABPFN_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    ensure_checkpoints(args.output)
    ensure_industry(args.source, args.output)
    write_manifest(args.source, args.output)
    run(args.output, args.source, args.years)


if __name__ == "__main__":
    main()
