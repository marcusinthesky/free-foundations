"""Paired annual summaries: uncertainty is across years, not independent firm pairs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from pathlib import Path


def summarize(output: Path) -> pd.DataFrame:
    """Save ten-year averages and a paired year-bootstrap versus the diagonal model."""
    annual = pd.read_csv(output / "annual.csv")
    loss = annual.pivot_table(index="year", columns="model", values="gaussian_loss")
    differences = loss.subtract(loss["diagonal"], axis=0)
    rng = np.random.default_rng(42)
    indices = rng.integers(0, len(loss), size=(5000, len(loss)))
    means = differences.to_numpy()[indices].mean(axis=1)
    intervals = np.quantile(means, [0.025, 0.975], axis=0)
    summary = annual.groupby("model")[
        ["gaussian_loss", "gmv_volatility", "moran_i", "lambda"]
    ].mean()
    summary["loss_vs_diagonal"] = differences.mean()
    summary["ci_low"] = pd.Series(intervals[0], index=differences.columns)
    summary["ci_high"] = pd.Series(intervals[1], index=differences.columns)
    summary = summary.sort_values("gaussian_loss")
    summary.to_csv(output / "summary.csv")
    write_json(
        output / "run-summary.json",
        {
            "years": sorted(annual["year"].unique().tolist()),
            "min_firms": int(annual["firms"].min()),
            "max_firms": int(annual["firms"].max()),
            "models": summary.index.tolist(),
            "bootstrap_unit": "year, paired across models",
            "bootstrap_replicates": 5000,
            "seed": 42,
            "interpretation": "Exploratory dependence/risk experiment; no causal or alpha claim.",
        },
    )
    return summary


def paired_comparisons(output: Path) -> pd.DataFrame:
    """Compare the pretrained network directly with each available benchmark."""
    annual = pd.read_csv(output / "annual.csv")
    loss = annual.pivot_table(index="year", columns="model", values="gaussian_loss")
    differences = loss.subtract(loss["tabpfn_fast"], axis=0)
    indices = np.random.default_rng(42).integers(0, len(loss), size=(5000, len(loss)))
    bounds = np.quantile(differences.to_numpy()[indices].mean(axis=1), [0.025, 0.975], axis=0)
    result = pd.DataFrame(
        {
            "benchmark": differences.columns,
            "tabpfn_loss_improvement": differences.mean().to_numpy(),
            "ci_low": bounds[0],
            "ci_high": bounds[1],
            "years_tabpfn_better": (differences > 0).sum().to_numpy(),
        }
    )
    result.to_csv(output / "paired-comparisons.csv", index=False)
    return result


def plot_summary(output: Path) -> None:
    """Write a standalone comparison figure; positive gain means lower held-out loss."""
    import matplotlib.pyplot as plt  # noqa: PLC0415 -- plotting is only needed for reports.

    summary = pd.read_csv(output / "summary.csv", index_col="model").iloc[::-1]
    names = {
        "diagonal": "Diagonal",
        "ledoit_wolf": "Ledoit-Wolf",
        "size": "Size",
        "leverage": "Leverage",
        "accounting": "Accounting ratios",
        "pca_5": "PCA (5)",
        "random_projection_8": "Random projection (8)",
        "fernandez_assets_history": "Asset-history correlation",
        "tabpfn_fast": "TabPFN 3.5 Fast",
        "tabpfn_shuffled": "TabPFN, shuffled firms",
    }
    positions = np.arange(len(summary))
    gain = -summary["loss_vs_diagonal"].to_numpy()
    low, high = -summary["ci_high"].to_numpy(), -summary["ci_low"].to_numpy()
    colors = ["#176b87" if name == "tabpfn_fast" else "#8195a5" for name in summary.index]
    figure, axes = plt.subplots(1, 2, figsize=(11, 5), sharey=True, layout="constrained")
    axes[0].barh(positions, gain, color=colors)
    axes[0].errorbar(
        gain,
        positions,
        xerr=np.maximum([gain - low, high - gain], 0),
        fmt="none",
        color="#303030",
        capsize=3,
    )
    axes[0].axvline(0, color="#303030", linewidth=0.7)
    axes[0].set_yticks(positions, [names[name] for name in summary.index])
    axes[0].set_xlabel("Loss improvement versus diagonal (higher is better)")
    axes[1].barh(positions, 100 * summary["gmv_volatility"], color=colors)
    axes[1].set_xlabel("Mean annualized residual GMV RMS risk (%)")
    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle(
        "2016-2025: held-out residual covariance and risk\n"
        "Exploratory paired-year bootstrap intervals; current large-cap sample"
    )
    svg = output / "comparison.svg"
    figure.savefig(svg)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    figure.savefig(output / "comparison.png", dpi=180)
    plt.close(figure)
