"""FinFM exhibits from paired spatial-lag comparisons."""

import json
from math import isfinite
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes
from free_foundations.study.publication.matched import verify_evidence


def _comparisons(results: Path, stage: str) -> pd.DataFrame:
    rows = pd.read_parquet(results / stage / "comparisons.parquet")
    return rows.loc[rows.process.eq("lag")].set_index(["cell", "reference"], verify_integrity=True)


def _contrast(rows: pd.DataFrame, key: tuple[str, str]) -> pd.Series:
    """Read the unique comparison for this candidate and reference."""
    return rows.loc[[key]].iloc[0]


def _interval(row: pd.Series, digits: int = 4) -> str:
    if row.status != "available":
        return "---"
    low = row.low_per_observation
    high = row.high_per_observation
    return f"{row.gain_per_observation:.{digits}f} [{low:.{digits}f}, {high:.{digits}f}]"


def broad_factor_table(comparisons: pd.DataFrame) -> pd.DataFrame:
    """Compare the same broad-input graphs under three factor-control designs.

    Missing rows identify an older encoder-stage output, which must be rerun.
    Recorded unavailable fits remain visible instead of becoming numeric claims.
    """
    required = {"factor_set", "rung", "model", "contrast"}
    if not required.issubset(comparisons.columns):
        message = (
            "Missing encoder metadata; rerun research_matched_encoders and collect its evidence."
        )
        raise ValueError(message)
    candidates = comparisons.loc[
        comparisons.rung.eq("standard_xbrl")
        & comparisons.model.eq("tabpfn_full")
        & comparisons.contrast.eq("versus_direct_control")
    ].set_index("factor_set", verify_integrity=True)
    rows = []
    for factor, label in (("market", "Market"), ("ff5", "FF5"), ("ff5_mom", "FF5 + Momentum")):
        if factor not in candidates.index:
            message = (
                f"Missing broad-input {factor} comparison; rerun research_matched_encoders "
                "and collect its matched evidence before rendering."
            )
            raise ValueError(message)
        row = candidates.loc[[factor]].iloc[0]
        if row.status != "available":
            rows.append([label, "---", "---"])
            continue
        gain, low, high = (
            float(row[name])
            for name in ("gain_per_observation", "low_per_observation", "high_per_observation")
        )
        if not all(isfinite(value) for value in (gain, low, high)) or low > high:
            message = f"Invalid broad-input {factor} likelihood contrast or interval."
            raise ValueError(message)
        rows.append([label, f"{gain:.4f}", f"[{low:.4f}, {high:.4f}]"])
    return pd.DataFrame(rows, columns=["Control", "Gain", "95% interval"])


def _neutral_table(graphs: pd.DataFrame, tables: Path) -> None:
    rows = []
    for key, name in [
        ("market_cap_assets", "Market equity/assets"),
        ("market_to_book", "Market-to-book"),
        ("dividend_yield", "Dividend yield"),
        ("debt_maturity", "Debt maturity"),
    ]:
        periods = graphs.loc[graphs.cell.eq(f"{key}:direct|knn10")].sort_values("quarter")
        pairs = periods.issuers * (periods.issuers - 1) / 2
        percent = 100 * periods.neutral_pairs / pairs
        pooled = 100 * periods.neutral_pairs.sum() / pairs.sum()
        rows.append([name, percent.iloc[0], percent.iloc[-1], pooled])
    quarters = pd.PeriodIndex(graphs["quarter"], freq="Q")
    endpoints = [period.strftime("%Y Q%q") for period in (quarters.min(), quarters.max())]
    frame = pd.DataFrame(rows, columns=["Characteristic", *endpoints, "Pooled"])
    atomic_bytes(
        tables / "matched-neutral.tex", frame.to_latex(index=False, float_format="%.2f").encode()
    )


def render(results: Path, generated: Path) -> None:
    """Write the matched exhibits and numeric bindings from indexed results."""
    verify_evidence(results, results / "evidence/manifest.json")
    encoders = _comparisons(results, "encoders")
    broad_table = broad_factor_table(encoders).to_latex(
        index=False, escape=True, column_format="lrr"
    )
    factors = _comparisons(results, "factors")
    fits = pd.read_parquet(results / "factors/fits.parquet")
    baselines = fits.loc[fits.process.eq("none")].set_index("factor_set")
    headings = ["Control", "Baseline LL", "Fernández gain", "TabPFN gain", "TabPFN minus Fernández"]
    rows = []
    for key, name in [
        ("market", "Market"),
        ("mom", "Momentum"),
        ("market_mom", "Market + Mom."),
        ("ff5", "FF5"),
        ("ff5_mom", "FF5 + Mom."),
    ]:
        direct, model, base = (
            f"{key}|{arm}" for arm in ("direct_characteristics", "tabpfn_full", "none")
        )
        rows.append(
            [
                name,
                f"{baselines.loc[key].log_likelihood:,.1f}",
                *[
                    _interval(_contrast(factors, pair))
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
                    _interval(_contrast(encoders, (f"{r}:{key}", f"{r}:direct")))
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
    atomic_bytes(
        tables / "matched-broad-factors.tex",
        broad_table.encode(),
    )
    kernels = _comparisons(results, "kernels")
    diagnostics = pd.read_parquet(results / "kernels/graphs.parquet")
    _neutral_table(diagnostics, tables)
    graphs = diagnostics.groupby("cell").effective_neighbours.mean()
    fig, ax = plt.subplots(figsize=(3.4, 1.8), layout="constrained")
    labels = []
    for y, (key, name) in enumerate(
        [("knn10", "10-NN"), ("gaussian", "Gaussian"), ("exp", "Exponential")]
    ):
        candidate, reference = (f"joint:{family}|{key}" for family in ("tabpfn", "direct"))
        row = _contrast(kernels, (candidate, reference))
        ax.hlines(y, row.low_per_observation, row.high_per_observation)
        ax.plot(row.gain_per_observation, y, "ko")
        labels.append(f"{name} ({graphs[reference]:.0f}, {graphs[candidate]:.0f})")
    ax.set_yticks(range(3), labels)
    ax.axvline(0, color="grey", linewidth=0.7)
    ax.tick_params(labelsize=8)
    ax.set_xlabel("Gain (nats per issuer-quarter)", fontsize=9)
    output = generated / "figures/matched-kernels.pdf"
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output)
    plt.close(fig)
    factor = _contrast(factors, ("ff5_mom|tabpfn_full", "ff5_mom|direct_characteristics"))
    broad = _contrast(encoders, ("standard_xbrl:tabpfn_full", "standard_xbrl:direct"))
    values = {
        "observations": f"{baselines.loc['ff5_mom'].observations:,.0f}",
        "broad-gain": f"{broad.gain_per_observation:.4f}",
        "factor-gain": f"{factor.gain_per_observation:.4f}",
        "factor-interval": f"[{factor.low_per_observation:.4f}, {factor.high_per_observation:.4f}]",
    }
    _render_geometry(results, generated, values)


def _render_geometry(results: Path, generated: Path, values: dict[str, str]) -> None:
    selected = json.loads((results / "geometry/manifest.json").read_text())["selected"]
    associations = pd.read_parquet(results / "geometry/selected_associations.parquet")
    valuation = associations.set_index("descriptor").spearman_pc1.abs().loc["market_cap_assets"]
    ablations = _comparisons(results, "ablation")
    overlap = pd.read_parquet(results / "ablation/peer_overlap.parquet")
    means = overlap.groupby("cell").mean_peer_jaccard.mean()
    rows = []
    for cell, label in [
        ("pc1", "First coordinate"),
        ("top_three", "First three coordinates"),
        ("omit:market_cap_assets", "Omit market equity / assets"),
        ("omit:market_to_book", "Omit market-to-book"),
        ("omit:dividend_yield", "Omit dividend yield"),
        ("omit:debt_maturity", "Omit debt maturity"),
    ]:
        row = _contrast(ablations, (cell, "full"))
        rows.append([label, f"{means[cell]:.3f}", _interval(row, 5)])
    table = pd.DataFrame(
        rows, columns=["Peer graph", "Mean overlap", r"Fit difference [95\% interval]"]
    )
    atomic_bytes(
        generated / "tables/matched-ablation.tex",
        table.to_latex(index=False, escape=False).encode(),
    )
    history = results / "historical-geometry"
    beta = json.loads((history / "manifest.json").read_text())["beta_overlay"]
    descriptors = pd.read_parquet(history / "historical_ratio_associations.parquet")
    ratio = descriptors.set_index("descriptor").loc["market_cap_assets"]
    values.update(
        {
            "historical-beta-r2": f"{100 * beta['leading_rank_r2']:.2f}",
            "historical-beta-n": str(beta["n"]),
            "historical-value-r2": f"{100 * ratio.leading_rank_r2:.0f}",
            "historical-value-n": f"{ratio.n:.0f}",
            "inertia": f"{100 * selected['positive_inertia_shares'][0]:.2f}",
            "valuation": f"{valuation:.2f}",
            "overlap": f"{means['pc1']:.3f}",
            "projected-gain": f"{_contrast(ablations, ('pc1', 'full')).gain_per_observation:.4f}",
        }
    )
    bindings = "".join(f"\\ffDeclareValue{{matched-{k}}}{{{v}}}\n" for k, v in values.items())
    atomic_bytes(generated / "matched-values.tex", bindings.encode())
