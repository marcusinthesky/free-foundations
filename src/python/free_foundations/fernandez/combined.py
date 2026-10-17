"""One shared cross-section and one spatial parameter per combined representation."""

from __future__ import annotations

import gc
import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import multivariate_normal

from free_foundations.expanded.baselines import compression_states
from free_foundations.expanded.disclosures import input_views
from free_foundations.expanded.distance import pairwise_distance, save_distance
from free_foundations.expanded.encoding import foundation_states, load_tabfm, prepare
from free_foundations.fernandez.characteristics import CHARACTERISTICS, history_view
from free_foundations.fernandez.models import error_ml, paper_weights, rank_distance
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")
SUPERSEDED = (
    "> Superseded by the matched cross-sectional ladder in "
    "[`research/ladder`](../../ladder/README.md),"
)


def likelihood(y: FloatArray, x: FloatArray, weights: FloatArray) -> dict[str, float | bool]:
    """Evaluate the full Gaussian likelihood, including its spatial Jacobian."""
    if np.any(weights):
        fit = error_ml(y, x, weights)
        intensity, premium = fit.intensity, fit.premium
    else:
        intensity = 0.0
        premium = float(np.linalg.lstsq(x, y, rcond=None)[0][0])
    operator = np.eye(len(y)) - intensity * weights
    innovations = operator @ (y - x[:, 0] * premium)
    variance = float(np.mean(innovations**2))
    value = float(
        np.linalg.slogdet(operator)[1] - len(y) / 2 * (np.log(2 * np.pi) + 1 + np.log(variance))
    )
    # Independently check the Jacobian formula against the implied normal density.
    inverse = np.linalg.solve(operator, np.eye(len(y)))
    direct = multivariate_normal.logpdf(
        y, mean=x[:, 0] * premium, cov=variance * inverse @ inverse.T
    )
    if not np.isclose(value, direct, atol=1e-8, rtol=0):
        message = "Spatial Jacobian and covariance-density likelihoods disagree."
        raise ArithmeticError(message)
    return {
        "lambda": intensity,
        "premium": premium,
        "innovation_variance": variance,
        "log_likelihood": value,
        "search_boundary": abs(intensity) > 0.985,
    }


def combined_distances(root: Path, tickers: tuple[str, ...]) -> dict[str, FloatArray]:
    """Encode all four histories jointly; add the same disclosures for the richer rung."""
    source, expanded = Path("research/pilot/cache"), Path("research/expanded/cache")
    panel = pd.read_parquet(root / "cache/characteristics.parquet")
    history = history_view(panel, 10)
    query = history.xs(2024, level="year").loc[list(tickers)]
    distances = {
        f"fernandez__{name}": rank_distance(query.filter(like=f"{name}__").to_numpy(dtype=float))
        for name in CHARACTERISTICS
    }
    distances["joint_four__rms"] = np.sqrt(np.mean([d**2 for d in distances.values()], axis=0))
    core = pd.read_parquet(source / "accounting.parquet")
    broad = pd.read_parquet(expanded / "broad.parquet")
    views = {
        "four_histories": history,
        "four_plus_broad": pd.concat(
            [history, input_views(core, broad, 2025)["broad"].reindex(history.index)], axis=1
        ),
    }
    labels = panel[["market_cap_assets"]].rename(columns={"market_cap_assets": "income"})
    labels["operating_cash"] = labels["income"]
    for name, view in views.items():
        data = prepare(view, labels, tickers, 2025, "income")
        write_json(
            root / "combined" / f"context-{name}.json",
            {
                "features": data.features,
                "support_ids": data.support_ids,
                "tickers": data.tickers,
                "digest": data.digest,
                "target": "next snapshot market_cap_assets",
                "support_rows": len(data.support),
                "prepared_columns": len(data.features),
            },
        )
        distances[f"{name}__direct"] = pairwise_distance(
            np.column_stack([data.query, np.ones(len(tickers))])
        )
        for method, vectors in compression_states(data).items():
            distances[f"{name}__{method}"] = pairwise_distance(vectors)
        for model in MODELS:
            LOGGER.info(
                "Combined %s / %s: %s firms, %s columns",
                name,
                model,
                len(tickers),
                len(data.features),
            )
            states = foundation_states(data, model, expanded, source)
            distances[f"{name}__{model}"] = pairwise_distance(states["late"])
            load_tabfm.cache_clear()
            gc.collect()
    return distances


def run() -> None:
    """Save a reproducible matched-sample likelihood table, with no return-based selection."""
    root = Path("research/fernandez")
    output = root / "combined"
    output.mkdir(exist_ok=True)
    cohorts = [
        set(
            pd.read_parquet(
                root / "cross-sectional-weights" / f"{name}__self_links_False.parquet"
            ).index
        )
        for name in CHARACTERISTICS
    ]
    tickers = tuple(sorted(set.intersection(*cohorts)))
    quarters = pd.read_csv(root / "quarterly-returns.csv")
    betas = pd.read_csv(root / "mm-betas.csv").set_index("ticker")
    medians = quarters.groupby("ticker")["excess"].median()
    x = betas.loc[list(tickers), ["beta"]].to_numpy(dtype=float)
    y = medians.loc[list(tickers)].to_numpy(dtype=float)
    pd.DataFrame({"ticker": tickers, "median_excess": y, "mm_beta": x[:, 0]}).to_csv(
        output / "sample.csv", index=False
    )
    LOGGER.info("Shared cross-section: %s firms: %s", len(tickers), tickers)
    distances = combined_distances(root, tickers)
    records = [
        {
            "model": "nonspatial_capm",
            "firms": len(y),
            **likelihood(y, x, np.zeros((len(y), len(y)))),
        }
    ]
    for name, distance in distances.items():
        save_distance(output / "distances" / f"{name}.parquet", distance, tickers)
        weights = paper_weights(distance)
        save_distance(output / "weights" / f"{name}.parquet", weights, tickers)
        records.append({"model": name, "firms": len(y), **likelihood(y, x, weights)})
    results = pd.DataFrame(records).set_index("model")
    results["delta_vs_nonspatial"] = results["log_likelihood"] - float(
        results["log_likelihood"].loc["nonspatial_capm"]
    )
    results["delta_vs_joint_four"] = results["log_likelihood"] - float(
        results["log_likelihood"].loc["joint_four__rms"]
    )
    results.to_csv(output / "likelihood.csv")
    lines = [
        "# Combined-network spatial-error ML comparison",
        "",
        SUPERSEDED,
        "> which uses 33 (four-characteristic) and 395 (three-characteristic) firms.",
        "",
        f"All rows use the same {len(tickers)} firms: {', '.join(tickers)}.",
        "",
        "The likelihood has one observation per firm: median quarterly excess return over",
        "2016-2025, regressed on the saved 40-quarter robust MM beta without an intercept.",
        "Each spatial row estimates one lambda, one premium, and one innovation variance.",
        "The no-spatial row fixes lambda at zero. All Gaussian constants are included.",
        "",
        "Fernández benchmarks use individual 2015-2024 characteristic histories.",
        "Joint RMS combines their four distances; it is our extension of the paper.",
        "Every learned representation combines all four histories in one vector per firm;",
        "the broader input additionally contains up to 200 SEC concepts from the 2024 snapshot.",
        "Support context and preprocessing follow the existing annual ladder and are saved.",
        "All networks use exp(-distance), zero diagonal, and row normalization.",
        "",
        "This is an in-sample, six-firm demonstration, not a forecast or a significance test.",
        "A boundary flag means the estimate reaches the (-0.99, 0.99) search limit.",
        "",
        "| Model / input | Lambda | Log-likelihood | Gain over nonspatial | Boundary |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for name, row in results.iterrows():
        lines.append(
            f"| {name} | {row['lambda']:.4f} | {row['log_likelihood']:.6f} | "
            f"{row['delta_vs_nonspatial']:.6f} | {row['search_boundary']} |"
        )
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n")
    paths = [
        root / "quarterly-returns.csv",
        root / "mm-betas.csv",
        root / "cache/characteristics.parquet",
        Path("research/pilot/cache/accounting.parquet"),
        Path("research/expanded/cache/broad.parquet"),
        Path(__file__),
        Path(__file__).with_name("models.py"),
        *sorted(output.rglob("*.parquet")),
        *sorted(output.glob("*.csv")),
        *sorted(output.glob("context-*.json")),
    ]
    write_json(
        output / "manifest.json",
        {
            "tickers": tickers,
            "observations": len(y),
            "models": len(results),
            "sha256": {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
        },
    )
    LOGGER.info("Completed %s fits on the same %s observations", len(results), len(y))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()
