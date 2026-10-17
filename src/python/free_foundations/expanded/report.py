"""Audit labeled annual matrices and summarize the predetermined comparison grid."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from free_foundations.pilot.data import write_json


def audit_distances(output: Path) -> pd.DataFrame:
    """Check every artifact and compare geometry under metric and context changes."""
    inventory = pd.read_csv(output / "distance-inventory.csv")
    rows = []
    labels: dict[int, tuple[str, ...]] = {}
    for record in inventory.to_dict("records"):
        matrix = pd.read_parquet(output / record["path"])
        values = matrix.to_numpy()
        year = int(record["year"])
        identities = tuple(matrix.index)
        valid = (
            identities == tuple(matrix.columns)
            and len(set(identities)) == record["firms"]
            and values.shape == (record["firms"], record["firms"])
            and np.isfinite(values).all()
            and (values >= 0).all()
            and np.allclose(values, values.T, atol=1e-12)
            and np.allclose(np.diag(values), 0, atol=1e-12)
            and labels.setdefault(year, identities) == identities
        )
        if not valid:
            message = f"Invalid labeled distance matrix: {record['path']}"
            raise ValueError(message)
        if record["metric"] == "chord":
            upper = np.triu_indices(len(matrix), 1)
            alternatives = {
                "metric": str(record["path"]).replace("__chord", "__euclidean"),
            }
            if "__income__" in str(record["path"]):
                alternatives["context"] = str(record["path"]).replace(
                    "__income__", "__operating_cash__"
                )
            for change, path in alternatives.items():
                other = pd.read_parquet(output / path).to_numpy()
                correlation = float(spearmanr(values[upper], other[upper]).statistic)
                rows.append(
                    {
                        "year": year,
                        "representation": record["representation"],
                        "comparison": change,
                        "pairwise_rank_correlation": correlation,
                    }
                )
    write_json(
        output / "distance-audit.json",
        {
            "matrices": len(inventory),
            "years": sorted(labels),
            "firms_by_year": {str(year): len(tickers) for year, tickers in labels.items()},
            "checks": [
                "finite",
                "nonnegative",
                "symmetric",
                "zero diagonal",
                "ordered ticker labels",
            ],
            "status": "passed",
        },
    )
    result = pd.DataFrame(rows)
    result.to_csv(output / "geometry-sensitivity.csv", index=False)
    return result


def comparison_tables(output: Path) -> pd.DataFrame:
    """Report paired annual gains without choosing a winner on the evaluation sample."""
    annual = pd.read_csv(output / "annual.csv")
    losses = annual.pivot_table(index="year", columns="model", values="gaussian_loss")
    gains = losses.rsub(losses["diagonal"], axis=0)
    summary = annual.groupby("model")[["gaussian_loss", "gmv_volatility", "moran_i"]].mean()
    summary["loss_gain_vs_diagonal"] = gains.mean()
    summary["years_better_than_diagonal"] = (gains > 0).sum()
    summary.to_csv(output / "summary.csv")
    comparisons = []
    for name in losses.columns:
        if name.endswith("__late__chord"):
            for control in ("shuffled", "industry_shuffled", "size_shuffled"):
                difference = losses[f"{name}__{control}"] - losses[name]
                comparisons.append(
                    {
                        "model": name,
                        "control": control,
                        "mean_loss_gain": float(difference.mean()),
                        "years_better": int((difference > 0).sum()),
                    }
                )
    pd.DataFrame(comparisons).to_csv(output / "permutation-comparisons.csv", index=False)
    return summary


def write_report(output: Path, summary: pd.DataFrame, geometry: pd.DataFrame) -> None:
    """Show fixed late-readout income/chord configurations and reference estimators."""
    chosen = ["diagonal", "ledoit_wolf", "size", "accounting", "pca_5"]
    for view in ("core19", "broad", "metrics"):
        chosen.append(f"{view}__standardized__euclidean")
        chosen.extend(
            f"{view}__{baseline}__chord"
            for baseline in ("pca16", "autoencoder", "random_autoencoder")
        )
        chosen.extend(
            f"{view}__income__{model}__late__chord"
            for model in ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")
        )
    lines = [
        "# Expanded experiment results",
        "",
        "Development results from the fixed grid described in [README](README.md).",
        "Foundation rows use income-label context, late readouts and chord distance;",
        "matched input/compression controls use the same support preprocessing.",
        "Positive gain means lower mean annual Gaussian covariance loss than the diagonal model.",
        "Risk is annualized RMS of residual GMV returns, not tradable total-return volatility.",
        "Both quantities are averaged across years; no best-variant selection is applied.",
        "",
        "| Configuration | Loss gain | Residual risk | Years beating diagonal |",
        "| --- | --- | --- | --- |",
    ]
    for name in chosen:
        row = summary.loc[name].to_dict()
        lines.append(
            f"| `{name}` | {row['loss_gain_vs_diagonal']:.5f} | "
            f"{row['gmv_volatility']:.2%} | {int(row['years_better_than_diagonal'])} |"
        )
    losses = summary["gaussian_loss"].to_dict()
    foundations = [
        name
        for name in losses
        if any(
            f"__{model}__" in str(name)
            for model in ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")
        )
        and not str(name).endswith(("__shuffled", "__industry_shuffled", "__size_shuffled"))
    ]
    better = sum(losses[name] < losses["ledoit_wolf"] for name in foundations)
    lines.extend(
        [
            "",
            f"{better} of {len(foundations)} foundation-model configurations have lower mean",
            "covariance loss than Ledoit-Wolf. This is a descriptive comparison across the",
            "entire development grid, not a significance test or evidence of a causal effect.",
            "",
            "![All foundation-model configurations](comparison.png)",
            "",
            "## Geometry sensitivity",
            "",
            "Spearman correlations compare the upper triangles of the same labeled cohort.",
            "Ranges describe configurations and years; firm pairs are not independent samples.",
            "",
            "| Change | Minimum | Median | Maximum |",
            "| --- | --- | --- | --- |",
        ]
    )
    for comparison, group in geometry.groupby("comparison"):
        values = group["pairwise_rank_correlation"]
        lines.append(
            f"| {comparison} | {values.min():.3f} | {values.median():.3f} | {values.max():.3f} |"
        )
    lines.extend(
        [
            "",
            "See `summary.csv` for every configuration and `permutation-comparisons.csv` for",
            "unrestricted, industry-group and size-group shuffles of late-readout chord networks.",
            "The SIC control uses current classifications. No multiple-comparison-adjusted",
            "significance or causal interpretation is claimed. A new holdout is needed before",
            "using this grid to choose an economic measurement model.",
            "",
        ]
    )
    (output / "RESULTS.md").write_text("\n".join(lines))


def plot_grid(output: Path, summary: pd.DataFrame) -> None:
    """Show all foundation configurations without selecting the best variant."""
    import matplotlib.pyplot as plt  # noqa: PLC0415 -- plotting is only needed for reports.

    columns = (
        ("tabpfn_fast", "late", "PFN Fast"),
        ("tabpfn_full", "late", "PFN full"),
        ("tabfm", "early_concat", "TabFM early\nconcat"),
        ("tabfm", "early_mean", "TabFM early\nmean"),
        ("tabfm", "late", "TabFM late"),
        ("exaone", "late", "EXAONE"),
    )
    configurations = [
        (view, target, metric)
        for view in ("core19", "broad", "metrics")
        for target in ("income", "operating_cash")
        for metric in ("chord", "euclidean")
    ]
    years = pd.read_csv(output / "annual.csv")["year"]
    gains = summary["loss_gain_vs_diagonal"].to_dict()
    values = np.array(
        [
            [
                gains[f"{view}__{target}__{model}__{readout}__{metric}"]
                for model, readout, _label in columns
            ]
            for view, target, metric in configurations
        ]
    )
    limit = max(float(np.abs(values).max()), 1e-8)
    figure, axes = plt.subplots(figsize=(12, 8), layout="constrained")
    heatmap = axes.imshow(values, cmap="RdBu", vmin=-limit, vmax=limit, aspect="auto")
    axes.set_xticks(range(len(columns)), [label for _model, _readout, label in columns])
    axes.set_yticks(range(len(configurations)), [" / ".join(row) for row in configurations])
    for row, column in np.ndindex(values.shape):
        axes.text(
            column,
            row,
            f"{values[row, column]:.3f}",
            ha="center",
            va="center",
            color="white" if abs(values[row, column]) > limit * 0.65 else "black",
        )
    axes.set_title(
        f"Mean covariance-loss improvement over diagonal ({years.min()}-{years.max()})\n"
        f"Development comparison; Ledoit-Wolf reference gain: {gains['ledoit_wolf']:.3f}"
    )
    figure.colorbar(heatmap, ax=axes, label="Positive = lower held-out Gaussian loss")
    figure.savefig(output / "comparison.png", dpi=150)
    svg = output / "comparison.svg"
    figure.savefig(svg)
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
    plt.close(figure)


def main() -> None:
    """Audit a finished run and regenerate its compact reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("research/expanded"))
    output = parser.parse_args().output
    status = json.loads((output / "execution-status.json").read_text())
    if status["status"] != "complete":
        message = "Wait for the experiment to complete before generating final reports."
        raise ValueError(message)
    geometry = audit_distances(output)
    summary = comparison_tables(output)
    write_report(output, summary, geometry)
    plot_grid(output, summary)


if __name__ == "__main__":
    main()
