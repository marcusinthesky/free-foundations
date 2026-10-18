"""Audit and summarize the matched comparison without selecting a test-period winner."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.pilot.data import write_json


def comparison_table(losses: pd.DataFrame) -> pd.DataFrame:
    """Distinguish factor upgrades, learned geometry and added disclosure information."""
    comparisons = []
    names = [str(name) for name in losses]
    learned = [
        name for name in names if any(model in name for model in ("tabpfn", "tabfm", "exaone"))
    ]
    for model in learned:
        factor = model.split("__", 1)[0]
        benchmarks = [
            "sample_covariance",
            "capm__diagonal",
            "ff5_mom__diagonal",
            f"{factor}__spherical",
        ]
        benchmarks += [name for name in names if name.startswith(f"{factor}__paper__")]
        if factor == "ff5_mom":
            benchmarks += [name for name in names if name.startswith("capm__paper__")]
        view = model.split("__")[1]
        benchmarks += [
            f"{factor}__{view}__{control}"
            for control in ("direct", "pca16", "autoencoder", "random_autoencoder")
        ]
        if view == "four_plus_broad":
            benchmarks.append(model.replace("four_plus_broad", "same_four_histories"))
        for benchmark in dict.fromkeys(benchmarks):
            gains = losses[benchmark] - losses[model]
            comparisons.append(
                {
                    "model": model,
                    "benchmark": benchmark,
                    "mean_loss_gain": gains.mean(),
                    "years_better": int((gains > 0).sum()),
                    "years": len(gains),
                }
            )
    return pd.DataFrame(comparisons)


def report(output: Path) -> None:
    """Require all requested folds and the cross-section before writing the final report."""
    status = json.loads((output / "execution-status.json").read_text())
    if status["completed_years"] != status["requested_years"]:
        message = "Do not summarize an incomplete matched forecasting ladder."
        raise ValueError(message)
    annual = pd.read_csv(output / "annual.csv")
    cross = pd.read_csv(output / "cross-section.csv")
    inventory = pd.read_csv(output / "distance-inventory.csv")
    for row in inventory.to_dict("records"):
        matrix = pd.read_parquet(output / row["path"])
        values = matrix.to_numpy(dtype=float)
        valid = (
            matrix.index.equals(pd.Index(matrix.columns))
            and values.shape == (row["firms"], row["firms"])
            and np.isfinite(values).all()
            and (values >= 0).all()
            and np.allclose(values, values.T)
            and np.allclose(np.diag(values), 0)
        )
        if not valid:
            message = f"Invalid distance artifact: {row['path']}"
            raise ValueError(message)
    write_json(output / "distance-audit.json", {"passed": True, "matrices": len(inventory)})
    losses = annual.pivot_table(index="year", columns="model", values="gaussian_loss")
    comparison_table(losses).to_csv(output / "paired-comparisons.csv", index=False)
    summary = annual.groupby("model")[["gaussian_loss", "gmv_volatility"]].mean()
    rows = [
        "# Fernández comparison results",
        "",
        "This is a US methodological replication and a retrospective forecasting extension.",
        "The original Economatica sample is not reproduced. See [methods](README.md).",
        "",
        "## Matched annual forecasting ladder",
        "",
        (
            f"Completed {len(losses)} years; common annual samples range from "
            f"{annual.firms.min()} to {annual.firms.max()} firms."
        ),
        f"All {len(inventory)} labeled distance matrices passed the artifact audit.",
        "",
        "Lower Gaussian loss is better. Risk is annualized realized GMV volatility of",
        "full excess returns; all covariances use the same training-only mean forecast.",
        "",
        "| Model | Mean loss | GMV volatility |",
        "| --- | ---: | ---: |",
    ]
    means = {
        str(name): float(value)
        for name, value in zip(
            summary.index, summary["gaussian_loss"].to_numpy(dtype=float), strict=True
        )
    }
    learned_names = [
        str(name)
        for name in summary.index
        if any(model in str(name) for model in ("tabpfn", "tabfm", "exaone"))
    ]
    conclusions = [
        "## Main comparisons",
        "",
        "Counts below use mean held-out Gaussian loss; they are not significance tests.",
        "",
        "| Benchmark | Learned configurations with lower mean loss |",
        "| --- | ---: |",
    ]
    for benchmark in ("sample_covariance", "ff5_mom__diagonal"):
        wins = sum(means[name] < means[benchmark] for name in learned_names)
        conclusions.append(f"| {benchmark} | {wins}/{len(learned_names)} |")
    for characteristic in (
        "market_cap_assets",
        "market_to_book",
        "dividend_yield",
        "debt_maturity",
        "joint_rms",
    ):
        wins = sum(
            means[name] < means[f"{name.split('__')[0]}__paper__{characteristic}"]
            for name in learned_names
        )
        conclusions.append(
            f"| Same-factor Fernández: {characteristic} | {wins}/{len(learned_names)} |"
        )
    conclusions += [
        "",
        "These results do not establish an advantage for learned geometry. The small",
        "complete-case cohort limits their interpretation; the older asset-history proxy",
        "is not an adequate substitute for this comparison.",
        "",
    ]
    rows[5:5] = conclusions
    for model, values in summary.iterrows():
        rows.append(f"| {model} | {values['gaussian_loss']:.5f} | {values['gmv_volatility']:.2%} |")
    rows += [
        "",
        "## Paper-style cross-sectional exercise",
        "",
        "Robust MM betas use 40 quarterly observations. Both spatial IV and spatial-error",
        "ML are estimated on median excess returns. These are descriptive in-sample fits.",
        "",
        "| Characteristic | Firms |",
        "| --- | ---: |",
    ]
    original = cross.loc[
        cross.network.str.endswith("__self_links_False") & cross.estimator.eq("spatial_error_ml")
    ]
    for row in original.itertuples(index=False):
        rows.append(f"| {str(row.network).removesuffix('__self_links_False')} | {row.firms} |")
    rows += [
        "",
        "Full coefficients and stability flags are in `cross-section.csv`.",
        "Conditional parameter significance and generated-beta uncertainty are not estimated.",
        "",
        "## Interpretation limits",
        "",
        "The all-four sample is small and selected for disclosure completeness and nonconstant",
        "histories. The ten test years have already been examined; these are development",
        "comparisons, not confirmatory evidence. Do not select a winning characteristic",
        "or model using these test losses. The richer-input rung includes the same four",
        "histories, so its incremental information is the added SEC concepts.",
        "",
        "The paired-comparisons table reports each learned model against raw covariance,",
        "factor-only covariance and every individual Fernández network, plus the joint",
        "classical control. Ledoit-Wolf is only a reference, not a success requirement.",
        "",
    ]
    (output / "RESULTS.md").write_text("\n".join(rows))
    paths = [
        *Path("src/python/src/free_foundations").rglob("*.py"),
        Path("src/python/src/free_foundations/fernandez/betas.R"),
        Path("src/python/uv.lock"),
        Path("devenv.lock"),
        Path("devenv.nix"),
        Path("research/pilot/manifest.json"),
        Path("research/expanded/checkpoints.json"),
        *output.glob("*.csv"),
        *output.glob("context-*.json"),
        *output.glob("cache/markets/*.parquet"),
        output / "cache/characteristics.parquet",
    ]
    hashes = {}
    for path in paths:
        with path.open("rb") as stream:
            hashes[str(path)] = hashlib.file_digest(stream, "sha256").hexdigest()
    write_json(
        output / "manifest.json",
        {
            "sha256": hashes,
            "paper_sha256": "7391cb6ed0b986ff3dffd3f0870b7a3a5f94a2291f773d0ebed0a91149bfbabe",
            "classification": "US methodological replication; retrospective development forecasts",
        },
    )
