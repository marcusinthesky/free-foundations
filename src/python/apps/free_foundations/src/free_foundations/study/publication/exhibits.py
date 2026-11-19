"""FinFM exhibits from paired spatial-lag comparisons."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes


def _comparisons(results: Path, stage: str) -> pd.DataFrame:
    rows = pd.read_parquet(results / stage / "comparisons.parquet")
    return rows.loc[rows.process.eq("lag")].set_index(["cell", "reference"], verify_integrity=True)


def _interval(row: pd.Series) -> str:
    if row.status != "available":
        return "---"
    return f"{row.gain_per_observation:.4f} [{row.low_per_observation:.4f}, {row.high_per_observation:.4f}]"


def render(results: Path, generated: Path) -> None:
    """Write the three matched exhibits and their selected-geometry statistic."""
    factors = _comparisons(results, "factors")
    fits = pd.read_parquet(results / "factors/fits.parquet")
    baselines = fits.loc[fits.process.eq("none")].set_index("factor_set")
    headings = ["Control", "Baseline LL", "Fernández gain", "TabPFN gain", "TabPFN minus Fernández"]
    rows = []
    for key, name in [
        ("market", "Market"),
        ("mom", "Momentum"),
        ("market_mom", "Market + momentum"),
        ("ff5", "FF5"),
        ("ff5_mom", "FF5 + momentum"),
    ]:
        direct, model, base = (
            f"{key}|{arm}" for arm in ("direct_characteristics", "tabpfn_full", "none")
        )
        rows.append(
            [
                name,
                f"{baselines.loc[key].log_likelihood:,.1f}",
                *[
                    _interval(factors.loc[pair])
                    for pair in [(direct, base), (model, base), (model, direct)]
                ],
            ]
        )
    tables = generated / "tables"
    full = fits[
        ["factor_set", "graph", "process", "status", "parameters", "log_likelihood", "aic", "bic"]
    ]
    for process in ("none", "lag", "error"):
        subset = full.loc[full.process.eq(process)].drop(columns="process")
        subset["factor_set"] = (
            subset.factor_set.str.upper()
            .str.replace("MARKET", "Market")
            .str.replace("MOM", "Momentum")
            .str.replace("_", " + ")
        )
        subset["graph"] = subset.graph.replace(
            {"direct_characteristics": "Fernández", "tabpfn_full": "TabPFN 3.5"}
        )
        if subset.status.eq("available").all():
            subset = subset.drop(columns="status")
        if process == "none":
            subset = subset.drop(columns="graph")
        subset = subset.rename(
            columns={
                "factor_set": "Factors",
                "graph": "Peer graph",
                "parameters": "Parameters",
                "log_likelihood": "Log likelihood",
                "aic": "AIC",
                "bic": "BIC",
                "status": "Fit status",
            }
        )
        atomic_bytes(
            tables / f"matched-detail-{process}.tex",
            subset.to_latex(index=False, escape=True, float_format="%.2f").encode(),
        )
    atomic_bytes(
        tables / "matched-factors.tex",
        pd.DataFrame(rows, columns=headings).to_latex(index=False).encode(),
    )
    encoders = _comparisons(results, "encoders")
    rows = []
    for key, name in [
        ("tabpfn_full", "TabPFN 3.5"),
        ("tabfm", "TabFM"),
        ("kumo", "Kumo"),
        ("limix", "LimiX"),
    ]:
        rows.append(
            [
                name,
                *[
                    _interval(encoders.loc[(f"{r}:{key}", f"{r}:direct")])
                    for r in ("fernandez", "operands", "standard_xbrl")
                ],
            ]
        )
    atomic_bytes(
        tables / "matched-encoders.tex",
        pd.DataFrame(
            rows,
            columns=["Encoder", "Ratio histories", "Underlying financials", "Broad financials"],
        )
        .to_latex(index=False)
        .encode(),
    )
    kernels = _comparisons(results, "kernels")
    graphs = (
        pd.read_parquet(results / "kernels/graphs.parquet")
        .groupby("cell")
        .effective_neighbours.mean()
    )
    fig, ax = plt.subplots(figsize=(5.8, 2.3), layout="constrained")
    labels = []
    for y, (key, name) in enumerate(
        [("knn10", "10-NN"), ("gaussian", "Gaussian"), ("exp", "Exponential")]
    ):
        candidate, reference = (f"joint:{family}|{key}" for family in ("tabpfn", "direct"))
        row = kernels.loc[(candidate, reference)]
        ax.hlines(y, row.low_per_observation, row.high_per_observation)
        ax.plot(row.gain_per_observation, y, "ko")
        labels.append(f"{name} ({graphs[reference]:.0f}, {graphs[candidate]:.0f})")
    ax.set_yticks(range(3), labels)
    ax.axvline(0, color="grey", linewidth=0.7)
    ax.set_xlabel("TabPFN minus Fernández (nats per issuer-quarter)")
    output = generated / "figures/matched-kernels.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
    selected = json.loads((results / "geometry/manifest.json").read_text())["selected"]
    atomic_bytes(
        tables / "matched-inertia.tex",
        f"{100 * selected['positive_inertia_shares'][0]:.2f}".encode(),
    )
