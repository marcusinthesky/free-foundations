"""APT tables and claims for the shared saved-result publisher.

Every value and table is derived from saved parquet or manifest files.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.study.publication import (
    CHARACTERISTIC_LABELS,
    MODEL_LABELS,
    _escape,
    _interval,
    _number,
)

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.study.spec import StudySpec

MODELS = ("tabpfn_full", "tabfm", "kumo", "limix")
RUNGS = ("fernandez", "standard_xbrl")
RUNG_SHORT = {"fernandez": "Histories", "standard_xbrl": "XBRL"}
HOLM_LEVEL = 0.05


class Workshop:
    """Macros and table bodies for one rendering."""

    def __init__(self) -> None:
        """Start empty."""
        self.macros: dict[str, str] = {}
        self.values: dict[str, float | int | str] = {}
        self.tables: dict[str, str] = {}

    def claim(self, key: str, value: float | str, digits: int = 3) -> None:
        r"""Define ``\ffw<Key>`` from a saved value."""
        self.values[key] = value
        if isinstance(value, str):
            text = value
        elif isinstance(value, (int, np.integer)):
            text = f"{int(value):,}"
        else:
            text = _number(value, digits)
        self.macros[key] = _escape(text)


def _scalar(value: object) -> float:
    """A saved pandas or NumPy scalar as a Python float."""
    return float(np.asarray(value, dtype=float).item())


def _tabular(columns: str, header: list[str], rows: list[list[str]]) -> str:
    body = "\n".join(" & ".join(row) + r" \\" for row in rows)
    return (
        f"\\begin{{tabular}}{{{columns}}}\n\\toprule\n"
        + " & ".join(header)
        + " \\\\\n\\midrule\n"
        + body
        + "\n\\bottomrule\n\\end{tabular}\n"
    )


def _star(p_holm: float, low: float, high: float) -> str:
    """Daggers mark unadjusted CIs excluding zero; stars mark Holm p < 0.05."""
    if np.isfinite(p_holm) and p_holm < 0.05:
        return "$^{*}$"
    if np.isfinite(low) and np.isfinite(high) and (low > 0 or high < 0):
        return "$^{\\dagger}$"
    return ""


def replication(work: Workshop, replication: Path, spec: StudySpec) -> None:
    """Her specification without an intercept, OLS with one, and kernel uniformity."""
    estimates = pd.read_parquet(replication / "estimates.parquet")
    primary = estimates.loc[estimates["formation"].eq(spec.primary_formation)]
    intervals = pd.read_parquet(replication / "intervals.parquet").set_index("quantity")
    networks = pd.read_parquet(replication / "networks.parquet")
    networks = networks.loc[networks["formation"].eq(spec.primary_formation)]
    roster = pd.read_parquet(replication / "roster.parquet")
    roster = roster.loc[roster["formation"].eq(spec.primary_formation)]
    work.claim("roster", len(roster))
    work.claim("issuers", int(roster["status"].eq("available").sum()))

    def interval(key: str) -> str:
        if key not in intervals.index:
            return "--"
        return _interval(intervals.loc[key, "low"], intervals.loc[key, "high"])

    rows = []
    for intercept in (False, True):
        ols = primary.loc[
            primary["estimator"].eq("ols") & primary["with_intercept"].eq(intercept)
        ].iloc[0]
        label = "with" if intercept else "without"
        work.claim(f"ols premium {label}", _scalar(ols["beta"]))
        work.claim(f"ols premium {label} ci", _interval(ols.get("beta_low"), ols.get("beta_high")))
        rows.append(
            [
                f"OLS, {label} intercept",
                _number(ols["beta"]),
                _interval(ols.get("beta_low"), ols.get("beta_high")),
                "--",
                "--",
            ]
        )
    for name, characteristic in CHARACTERISTIC_LABELS.items():
        network = f"fernandez:{name}|exp"
        row = primary.loc[
            primary["network"].eq(network)
            & primary["estimator"].eq("lag_ml")
            & ~primary["with_intercept"].astype(bool)
        ].iloc[0]
        rows.append(
            [
                f"Lag ML: {characteristic}",
                _number(row["beta"]),
                interval(f"{network}|lag_ml:premium:without"),
                _number(row["spatial"]),
                interval(f"{network}|lag_ml:spatial:without"),
            ]
        )
        if name == "joint":
            work.claim("joint rho", _scalar(row["spatial"]))
            work.claim("joint rho ci", interval(f"{network}|lag_ml:spatial:without"))
            work.claim("joint premium", _scalar(row["beta"]))
    work.tables["replication"] = _tabular(
        "lrrrr", ["Model", "Premium", "95\\% CI", "$\\rho$", "95\\% CI"], rows
    )
    exp = networks.loc[networks["network"].str.endswith("|exp")]
    work.claim("exp eff min", _scalar(exp["effective_neighbours"].min()), 0)
    work.claim("exp eff max", _scalar(exp["effective_neighbours"].max()), 0)
    work.claim("exp uniform min", _scalar(exp["distance_from_uniform"].min()), 2)
    work.claim("exp uniform max", _scalar(exp["distance_from_uniform"].max()), 2)
    with_intercept = primary.loc[
        primary["with_intercept"].astype(bool) & primary["network"].str.endswith("|exp")
    ]
    work.claim("intercept fits", len(with_intercept))
    work.claim("intercept boundary", int(with_intercept["status"].ne("available").sum()))
    work.claim("generated draws", spec.generated_beta_draws)


def apt(work: Workshop, apt_dir: Path) -> None:
    """Exposure recovery and the out-of-sample CAPM/APT/spatial ladder."""
    manifest = json.loads((apt_dir / "manifest.json").read_text())
    models = pd.read_parquet(apt_dir / "models.parquet").set_index("model")
    comparisons = pd.read_parquet(apt_dir / "comparisons.parquet")
    recovery = pd.read_parquet(apt_dir / "recovery.parquet").set_index("representation")
    alignment = pd.read_parquet(apt_dir / "alignment.parquet").set_index("geometry")
    for key in ("issuers", "train_months", "test_months", "test_issuer_months"):
        work.claim(f"apt {key}", int(manifest[key]))
    work.claim("apt roster", int(manifest["roster_issuers"]))
    work.claim("apt exiting", int(manifest["test_issuers_exiting"]))
    work.claim("apt draws", int(manifest["apt"]["score_draws"]))
    work.claim("apt mantel draws", int(manifest["apt"]["mantel_draws"]))

    # Recovery: out-of-fold exposure R^2, Mantel with exposure distance, certificate.
    rows = []
    for model in ("direct", *MODELS):
        cells = [MODEL_LABELS[model]]
        for rung in RUNGS:
            key = f"{rung}:{model}"
            fit = recovery.loc[key]
            cells += [
                _number(fit["r_squared"], 2),
                _number(alignment.loc[f"{key}:raw", "mantel_exposure"], 2),
                _number(alignment.loc[f"{key}:calibrated", "mantel_exposure"], 2),
            ]
        rows.append(cells)
    joint = alignment.loc["characteristics:fernandez_joint", "mantel_exposure"]
    work.claim("joint mantel exposure", _scalar(joint), 2)
    work.tables["recovery"] = _tabular(
        "lrrrrrr",
        [
            (
                " & \\multicolumn{3}{c}{Histories} & \\multicolumn{3}{c}{XBRL} \\\\\n"
                "\\cmidrule(lr){2-4}\\cmidrule(lr){5-7}\n"
                " & $R^2$ & Raw & Cal. & $R^2$ & Raw & Cal."
            )
        ],
        rows,
    )
    fm = recovery.loc[[f"{rung}:{model}" for rung in RUNGS for model in MODELS]]
    direct = recovery.loc[[f"{rung}:direct" for rung in RUNGS]]
    work.claim("fm rsq min", _scalar(fm["r_squared"].min()), 2)
    work.claim("fm rsq max", _scalar(fm["r_squared"].max()), 2)
    work.claim("direct rsq hist", _scalar(direct.loc["fernandez:direct", "r_squared"]), 2)
    work.claim("direct rsq xbrl", _scalar(direct.loc["standard_xbrl:direct", "r_squared"]), 2)
    work.claim("certified max", _scalar(recovery["certified_share"].max()), 3)
    work.claim("rms error min", _scalar(recovery["rms_error"].min()), 3)
    work.claim("margin median max", _scalar(recovery["median_margin"].max()) * 1e4, 1)
    ratio = _scalar(recovery["rms_error"].min()) / _scalar(recovery["median_margin"].max())
    work.claim("error margin ratio", int(round(ratio, -1)))
    raw = alignment.loc[[f"{rung}:{model}:raw" for rung in RUNGS for model in MODELS]]
    calibrated = alignment.loc[[f"{rung}:{model}:calibrated" for rung in RUNGS for model in MODELS]]
    work.claim("fm mantel raw mean", _scalar(raw["mantel_exposure"].mean()), 2)
    work.claim("fm mantel cal mean", _scalar(calibrated["mantel_exposure"].mean()), 2)
    work.claim("jaccard max", _scalar(alignment["knn_jaccard_exposure"].max()), 3)

    _ladder(work, models, comparisons)


def _ladder(work: Workshop, models: pd.DataFrame, comparisons: pd.DataFrame) -> None:
    """Out-of-sample ladder: improvement in mean log score per issuer-month vs APT."""
    versus = comparisons.loc[comparisons["reference"].eq("apt")].set_index("model")

    def improvement(model: str, scale: float = 1000.0) -> str:
        if model not in versus.index:
            return "--"
        row = versus.loc[model]
        return _number(_scalar(row["mean_improvement"]) * scale, 2) + _star(
            _scalar(row["p_holm"]), _scalar(row["low"]), _scalar(row["high"])
        )

    rows = []
    for model in ("direct", *MODELS):
        cells = [MODEL_LABELS[model]]
        cells += [
            improvement(f"spatial_apt|{rung}:{model}:{kind}")
            for rung in RUNGS
            for kind in ("raw", "calibrated")
        ]
        rows.append(cells)
    work.tables["apt"] = _tabular(
        "lrrrr",
        ["", "Hist.\\ raw", "Hist.\\ cal.", "XBRL raw", "XBRL cal."],
        rows,
    )
    baselines = [
        ("CAPM", "capm"),
        ("Fern\\'andez characteristics", "spatial_apt|characteristics:fernandez_joint"),
        ("Estimated exposures", "spatial_apt|exposures:estimated"),
        ("Industry (SIC-2)", "spatial_apt|industry:sic2"),
        ("Relabelled null", "spatial_apt|null:relabelled"),
    ]
    work.tables["apt-baselines"] = _tabular(
        "lrrr",
        ["Network", "$\\lambda$", "$\\Delta$ score", "GMV vol."],
        [
            [
                "APT (no spatial term)",
                "--",
                "0",
                _number(models.loc["apt", "gmv_volatility_annual"], 3),
            ],
            *[
                [
                    label,
                    _number(models.loc[name, "spatial"], 2),
                    improvement(name),
                    _number(models.loc[name, "gmv_volatility_annual"], 3),
                ]
                for label, name in baselines
            ],
        ],
    )
    fm_names = [
        f"spatial_apt|{rung}:{model}:{kind}"
        for rung in RUNGS
        for model in MODELS
        for kind in ("raw", "calibrated")
    ]
    fm_rows = versus.loc[fm_names]
    significant = fm_rows["p_holm"] < HOLM_LEVEL
    work.claim("fm spatial count", len(fm_rows))
    work.claim("fm better holm", int(((fm_rows["mean_improvement"] > 0) & significant).sum()))
    work.claim("fm worse holm", int(((fm_rows["mean_improvement"] < 0) & significant).sum()))
    work.claim("fm better point", int((fm_rows["mean_improvement"] > 0).sum()))
    for key, name in (
        ("industry", "spatial_apt|industry:sic2"),
        ("capm", "capm"),
        ("exposure", "spatial_apt|exposures:estimated"),
        ("characteristics", "spatial_apt|characteristics:fernandez_joint"),
    ):
        row = versus.loc[name]
        work.claim(f"{key} gain", _scalar(row["mean_improvement"]) * 1000, 1)
        work.claim(f"{key} ci", _interval(row["low"] * 1000, row["high"] * 1000, 1))
        if name in models.index and np.isfinite(_scalar(models.loc[name, "spatial"])):
            work.claim(f"{key} lambda", _scalar(models.loc[name, "spatial"]), 2)
    work.claim("apt gmv", _scalar(models.loc["apt", "gmv_volatility_annual"]), 3)
    industry_gmv = models.loc["spatial_apt|industry:sic2", "gmv_volatility_annual"]
    work.claim("industry gmv", _scalar(industry_gmv), 3)
    calibrated_names = comparisons["model"].str.removesuffix(":calibrated")
    paired = comparisons.loc[
        comparisons["model"].str.endswith(":calibrated")
        & comparisons["reference"].str.endswith(":raw")
        & calibrated_names.eq(comparisons["reference"].str.removesuffix(":raw"))
    ]
    better = (paired["mean_improvement"] > 0) & (paired["p_holm"] < HOLM_LEVEL)
    work.claim("cal over raw better holm", int(better.sum()))
    work.claim("cal over raw count", len(paired))
    work.claim("cal over raw positive", int((paired["mean_improvement"] > 0).sum()))
    work.claim("comparisons", len(comparisons))

    # Appendix: every model's absolute test score and GMV volatility.
    full = []
    for name, row in models.iterrows():
        label = str(name).replace("spatial_apt|", "")
        full.append(
            [
                "\\texttt{" + _escape(label) + "}",
                _number(row["spatial"], 3),
                _number(row["test_score"], 4),
                improvement(str(name)) if name != "apt" else "--",
                _number(row["gmv_volatility_annual"], 4),
            ]
        )
    work.tables["apt-full"] = _tabular(
        "lrrrr", ["Model", "$\\lambda$", "Score", "$\\Delta$ vs APT", "GMV vol."], full
    )


def insample(work: Workshop, comovement: Path, alignment: Path) -> None:
    """Appendix: in-sample co-movement panels and Mantel against realized correlations."""
    estimates = pd.read_parquet(comovement / "estimates.parquet")
    lag = estimates.loc[estimates["process"].eq("lag")].set_index("network")
    mantel = pd.read_parquet(alignment / "mantel.parquet").set_index("network")
    rows = []
    for rung in RUNGS:
        for model in ("direct", *MODELS):
            key = f"{rung}:{model}"
            name = f"{key}|knn10"
            rows.append(
                [
                    f"{MODEL_LABELS[model]} ({RUNG_SHORT[rung]})",
                    _number(lag.loc[name, "spatial"]) if name in lag.index else "--",
                    _number(mantel.loc[key, "mantel"]) if key in mantel.index else "--",
                ]
            )
    for label, name, key in (
        ("Fern\\'andez joint", "fernandez:joint|knn10", "fernandez:joint"),
        ("Size", "size|knn10", "size"),
        ("Industry (SIC-2)", "industry|sic2", None),
        ("Relabelled null", "null|knn10", None),
    ):
        rows.append(
            [
                label,
                _number(lag.loc[name, "spatial"]) if name in lag.index else "--",
                _number(mantel.loc[key, "mantel"]) if key is not None else "--",
            ]
        )
    work.tables["insample"] = _tabular("lrr", ["Network", "Panel $\\rho$", "Mantel"], rows)
