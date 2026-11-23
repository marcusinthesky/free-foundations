"""Quarterly empirical tables, figures and scalar claims."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

import matplotlib as mpl
import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes
from free_foundations.study.publication.formatting import (
    CHARACTERISTIC_LABELS,
    ESTIMATOR_LABELS,
    _escape,
    _interval,
    _number,
    network_label,
)

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.study.spec import StudySpec


def compact_peer_label(key: str) -> str:
    """Shorten peer labels for the quarterly likelihood table."""
    return (
        network_label(key)
        .removesuffix(", 10-NN")
        .replace("Fernández histories", "ratios")
        .replace("CompanyFacts XBRL", "XBRL")
        .replace("Fernández: Joint (RMS)", "Fernández joint")
    )


def _tabular(  # noqa: PLR0913 -- one table's caption, label, cells and alignment.
    caption: str,
    label: str,
    header: list[str],
    rows: list[list[str]],
    note: str,
    *,
    text_columns: int = 1,
) -> str:
    columns = "l" * text_columns + "r" * (len(header) - text_columns)
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    return (
        f"% ff-table:{label.removeprefix('tab:')}\n"
        f"% caption: {caption}\n"
        f"% note: {note}\n"
        f"\\begin{{tabular}}{{{columns}}}\n\\toprule\n"
        + " & ".join(header)
        + " \\\\\n\\midrule\n"
        + body
        + "\n\\bottomrule\n\\end{tabular}\n"
        + "\n"
    )


class Report:
    """Collects tables, macros and audited claims for one rendering."""

    def __init__(self) -> None:
        """Start with no tables or claims."""
        self.parts: list[str] = []
        self.metrics: dict[str, float | int | str] = {}

    def claim(self, key: str, value: float | str) -> None:
        """Record a scalar and define its manuscript macro."""
        self.metrics[key.replace(" ", "_")] = value
        # Raw values stay in metrics; the TeX catalog formats them at publication.


def _sample(report: Report, replication: Path, comovement: Path, spec: StudySpec) -> None:
    rosters = pd.read_parquet(replication / "roster.parquet")
    ledger = pd.read_parquet(comovement / "ledger.parquet")
    rows = []
    for formation, group in rosters.groupby("formation"):
        window = spec.window(int(str(formation)))
        available = group["status"].eq("available")
        rows.append(
            [
                f"{formation}",
                f"{window[0].year}--{window[-1].year}",
                f"{len(group):,}",
                f"{int(available.sum()):,}",
                _number(group.loc[available, "observed_quarters"].mean(), 1),
                _number(group.loc[available, "mm_beta"].median(), 2),
            ]
        )
    primary = rosters.loc[rosters["formation"].eq(spec.primary_formation)]
    report.claim("primary roster", len(primary))
    report.claim("primary issuers", int(primary["status"].eq("available").sum()))
    quarters = ledger.loc[ledger["quarter"].notna()] if "quarter" in ledger else ledger
    report.claim("panel quarters", len(quarters))
    report.claim("panel issuer quarters", int(quarters["issuers"].sum()))
    report.parts.append(
        _tabular(
            "Formation cohorts and stage-one estimation",
            "tab:cohorts",
            ["Formation", "Window", "Roster", "Estimated", "Mean quarters", "Median MM $\\beta$"],
            rows,
            "Roster: December top-1,000 issuers with verified SEC information at the window "
            "start, followed through exits with CRSP delisting returns. Estimated: issuers "
            f"with at least {spec.min_beta_quarters} observed quarters and a converged MM fit.",
        )
    )


def _replication(report: Report, replication: Path, spec: StudySpec) -> None:
    estimates = pd.read_parquet(replication / "estimates.parquet")
    primary = estimates.loc[estimates["formation"].eq(spec.primary_formation)]
    intervals = (
        pd.read_parquet(replication / "intervals.parquet").set_index("quantity")
        if (replication / "intervals.parquet").exists()
        else pd.DataFrame(columns=["low", "high"])
    )

    def boot(network: str, estimator: str, name: str, *, intercept: bool) -> str:
        label = "with" if intercept else "without"
        key = f"{network}|{estimator}:{name}:{label}"
        if key not in intervals.index:
            return "--"
        return _interval(intervals.loc[key, "low"], intervals.loc[key, "high"])

    for intercept in (False, True):
        rows = []
        subset = primary.loc[primary["with_intercept"].eq(intercept)]
        ols = subset.loc[subset["estimator"].eq("ols")].iloc[0]
        rows.append(
            [
                "OLS",
                "",
                _number(ols.get("beta")),
                _interval(ols.get("beta_low"), ols.get("beta_high")),
                "--",
                "--",
                _number(ols.get("aic"), 1),
            ]
        )
        for name, characteristic in CHARACTERISTIC_LABELS.items():
            network = f"fernandez:{name}|exp"
            for estimator in ("lag_iv", "lag_ml", "error_ml"):
                row = subset.loc[subset["network"].eq(network) & subset["estimator"].eq(estimator)]
                if row.empty or row.iloc[0]["status"] != "available":
                    rows.append(
                        [
                            characteristic,
                            ESTIMATOR_LABELS[estimator],
                            "--",
                            "--",
                            "--",
                            "--",
                            "--",
                        ]
                    )
                    continue
                item = row.iloc[0]
                rows.append(
                    [
                        characteristic,
                        ESTIMATOR_LABELS[estimator],
                        _number(item.get("beta")),
                        boot(network, estimator, "premium", intercept=intercept),
                        _number(item.get("spatial")),
                        boot(network, estimator, "spatial", intercept=intercept),
                        _number(item.get("aic"), 1),
                    ]
                )
        suffix = "with" if intercept else "without"
        report.parts.append(
            _tabular(
                f"Fern\\'andez spatial CAPM, {spec.primary_formation} formation, "
                f"{suffix} an intercept",
                f"tab:fernandez-{suffix}",
                [
                    "Network",
                    "Estimator",
                    "Premium",
                    "95\\% CI",
                    "$\\rho$/$\\lambda$",
                    "95\\% CI",
                    "AIC",
                ],
                rows,
                "Outcome: median quarterly excess return; regressor: MM CAPM beta. Networks: "
                "$W=\\mathrm{rownorm}(\\exp(-d))$ on Spearman chord distances of formation-date "
                "characteristic histories. Intervals: stationary quarter bootstrap refitting "
                "betas, medians and the spatial model "
                f"({spec.generated_beta_draws} draws). Without an intercept the spatial term "
                "also absorbs the cross-sectional mean (her specification).",
                text_columns=2,
            )
        )
    joint = primary.loc[
        primary["network"].eq("fernandez:joint|exp")
        & primary["estimator"].eq("lag_ml")
        & ~primary["with_intercept"].astype(bool)
    ]
    if not joint.empty:
        report.claim("fernandez joint rho", float(joint.iloc[0]["spatial"]))
        report.claim("fernandez joint premium", float(joint.iloc[0]["beta"]))
        spatial_interval = "fernandez:joint|exp|lag_ml:spatial:without"
        if spatial_interval in intervals.index:
            interval = intervals.loc[[spatial_interval]].iloc[0]
            report.claim("fernandez joint rho bootstrap low", float(interval["low"]))
            report.claim("fernandez joint rho bootstrap high", float(interval["high"]))
            report.claim("fernandez joint rho bootstrap draws", int(interval["draws"]))

        networks = pd.read_parquet(replication / "networks.parquet")
        joint_network = networks.loc[
            networks["formation"].eq(spec.primary_formation)
            & networks["network"].eq("fernandez:joint|exp")
        ]
        if not joint_network.empty:
            report.claim(
                "fernandez joint effective neighbours",
                float(joint_network.iloc[0]["effective_neighbours"]),
            )


def _matched(report: Report, replication: Path, spec: StudySpec) -> None:
    estimates = pd.read_parquet(replication / "estimates.parquet")
    diagnostics = pd.read_parquet(replication / "diagnostics.parquet")
    networks = pd.read_parquet(replication / "networks.parquet")
    intervals = (
        pd.read_parquet(replication / "intervals.parquet").set_index("quantity")
        if (replication / "intervals.parquet").exists()
        else pd.DataFrame(columns=["low", "high"])
    )
    primary = estimates.loc[
        estimates["formation"].eq(spec.primary_formation) & estimates["with_intercept"].astype(bool)
    ]
    suffix = f"|knn{spec.neighbours}"
    names = [name for name in primary["network"].unique() if name.endswith(suffix)] + [
        "industry|sic2"
    ]
    rows = []
    for name in names:
        lag = primary.loc[primary["network"].eq(name) & primary["estimator"].eq("lag_ml")]
        error = primary.loc[primary["network"].eq(name) & primary["estimator"].eq("error_ml")]
        test = diagnostics.loc[
            diagnostics["network"].eq(name) & diagnostics["formation"].eq(spec.primary_formation)
        ]
        shape = networks.loc[
            networks["network"].eq(name) & networks["formation"].eq(spec.primary_formation)
        ]
        key = f"{name}|lag_ml:spatial:with"
        rows.append(
            [
                _escape(network_label(name)),
                _number(lag.iloc[0].get("spatial")) if not lag.empty else "--",
                _interval(intervals.loc[key, "low"], intervals.loc[key, "high"])
                if key in intervals.index
                else "--",
                _number(error.iloc[0].get("spatial")) if not error.empty else "--",
                _number(test.iloc[0].get("moran_residual")) if not test.empty else "--",
                _number(test.iloc[0].get("moran_residual_p")) if not test.empty else "--",
                _number(shape.iloc[0].get("effective_neighbours"), 1) if not shape.empty else "--",
            ]
        )
    report.parts.append(
        _tabular(
            f"Matched networks on the {spec.primary_formation} formation (with intercept)",
            "tab:matched",
            [
                "Network",
                "$\\rho$ (lag ML)",
                "95\\% CI",
                "$\\lambda$ (error ML)",
                "Moran's $I$",
                "$p$",
                "Eff. neighbours",
            ],
            rows,
            f"Every network is a symmetrized, row-normalized {spec.neighbours}-nearest-neighbour "
            "graph on formation-date distances, except industry (same SIC-2). Only the spatial "
            "coefficient is fitted to returns. Moran's $I$: OLS residuals with an intercept.",
        )
    )


def _comovement(report: Report, comovement: Path, spec: StudySpec) -> None:
    estimates = pd.read_parquet(comovement / "estimates.parquet")
    comparisons = pd.read_parquet(comovement / "comparisons.parquet")
    suffix = f"|knn{spec.neighbours}"
    rows = []
    lag = estimates.loc[estimates["process"].eq("lag") & estimates["status"].eq("available")]
    for item in lag.to_dict("records"):
        name = str(item["network"])
        if not (name.endswith(suffix) or name.startswith("industry")):
            continue
        rows.append(
            [
                _escape(network_label(name)),
                _number(item["spatial"]),
                _interval(item["spatial_low"], item["spatial_high"]),
                _interval(item.get("bootstrap_low"), item.get("bootstrap_high")),
                _number(item["capm_slope"]),
                _number(item["log_likelihood"], 1),
            ]
        )
    report.parts.append(
        _tabular(
            "Quarterly spatial co-movement panels (spatial lag, period effects)",
            "tab:comovement",
            [
                "Network",
                "$\\rho$",
                "Profile 95\\% CI",
                "Bootstrap 95\\% CI",
                "CAPM slope",
                "Log-lik.",
            ],
            rows,
            f"Quarterly excess returns, {spec.panel_start[:4]}--{spec.archive_end[:4]}. Period "
            "effects absorb common shocks; the regressor is the MM beta times Mkt-RF. Each "
            "quarter's graph uses only information available before that quarter.",
        )
    )
    rows = []
    for item in comparisons.loc[comparisons["process"].eq("lag")].to_dict("records"):
        rows.append(
            [
                _escape(compact_peer_label(str(item["network"]))),
                _escape(compact_peer_label(str(item["reference"]))),
                _number(item["mean_difference"], 2),
                _interval(item["low"], item["high"], 2),
                _number(item["p_holm"]),
            ]
        )
    report.parts.append(
        _tabular(
            "Paired in-sample likelihood differences per quarter",
            "tab:likelihood",
            ["Network", "Reference", "$\\Delta\\ell$/quarter", "95\\% CI", "Holm $p$"],
            rows,
            "Positive differences favour the network over its reference. Intervals: "
            f"stationary quarter bootstrap ({spec.likelihood_draws} draws) of the mean "
            "per-quarter log-likelihood difference at each network's in-sample fit.",
            text_columns=2,
        )
    )


def _alignment(report: Report, alignment: Path) -> None:
    mantel = pd.read_parquet(alignment / "mantel.parquet")
    gaps = pd.read_parquet(alignment / "gaps.parquet")
    rows = [
        [
            _escape(network_label(str(item["network"]))),
            _number(item["mantel"]),
            _interval(item["low"], item["high"]),
            _number(item["p_holm"]),
        ]
        for item in mantel.to_dict("records")
    ]
    report.parts.append(
        _tabular(
            "Mantel alignment with realized excess-return co-movement",
            "tab:mantel",
            ["Distance", "Spearman Mantel", "Node-bootstrap 95\\% CI", "Holm $p$"],
            rows,
            "Target: chord distance of pairwise excess-return correlations over the primary "
            "window. No parameter is fitted.",
        )
    )
    rows = [
        [
            _escape(network_label(str(item["network"]))),
            _escape(network_label(str(item["reference"]))),
            _number(item["gap"]),
            _interval(item["low"], item["high"]),
        ]
        for item in gaps.to_dict("records")
    ]
    report.parts.append(
        _tabular(
            "Paired Mantel gaps",
            "tab:mantel-gaps",
            ["Distance", "Reference", "Gap", "95\\% CI"],
            rows,
            "Gap: Mantel correlation of the distance minus that of its reference, on shared "
            "node-bootstrap draws.",
            text_columns=2,
        )
    )


def _figure(replication: Path, output: Path, spec: StudySpec) -> str:
    mpl.use("Agg")
    # TrueType fonts embed cleanly in the xdvipdfmx-built manuscript; Type 3 fonts do not.
    mpl.rcParams["pdf.fonttype"] = 42
    import matplotlib.pyplot as plt  # noqa: PLC0415 -- after selecting the backend.

    estimates = pd.read_parquet(replication / "estimates.parquet")
    selected = estimates.loc[
        estimates["estimator"].eq("lag_ml")
        & estimates["with_intercept"].astype(bool)
        & estimates["status"].eq("available")
    ]
    figure, axis = plt.subplots(figsize=(6.4, 3.4))
    for name in ("fernandez:joint|exp", f"fernandez:joint|knn{spec.neighbours}"):
        series = selected.loc[selected["network"].eq(name)].sort_values("formation")
        if series.empty:
            continue
        axis.errorbar(
            series["formation"],
            series["spatial"],
            yerr=[
                series["spatial"] - series["spatial_low"],
                series["spatial_high"] - series["spatial"],
            ],
            capsize=3,
            marker="o",
            label=network_label(name),
        )
    axis.axhline(0, color="0.5", linewidth=0.8)
    axis.set_xlabel("December formation")
    axis.set_ylabel(r"$\hat\rho$ (lag ML, 95% Wald CI)")
    axis.legend(frameon=False, fontsize=8)
    figure.tight_layout()
    path = output / "rolling-rho.pdf"
    buffer = BytesIO()
    figure.savefig(buffer, format="pdf", metadata={"CreationDate": None})
    plt.close(figure)
    atomic_bytes(path, buffer.getvalue())
    return f"\\includegraphics[width=0.8\\linewidth]{{generated/figures/{path.name}}}\n"
