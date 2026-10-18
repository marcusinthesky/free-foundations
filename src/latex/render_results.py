"""Render publication assets from saved estimates; never run empirical models."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean

import matplotlib
import pandas as pd
from jinja2 import Environment, FileSystemLoader, StrictUndefined

matplotlib.use("pgf")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "src/latex/build"
PANEL = "research/panel/three-foundations"
MODELS = {
    "direct": "Direct",
    "pca16": "PCA",
    "supervised_mlp16": "Supervised network",
    "tabpfn_full__late": "TabPFN 3.5",
    "tabfm__late": "TabFM 1.1",
    "kumo__late": "Kumo Large",
    "limix__late": "LimiX-2",
}
SUPPLEMENTARY = {
    "tabpfn_full_random__late": "Random TabPFN (42)",
    "tabpfn_full_random43__late": "Random TabPFN (43)",
    "tabpfn_full_random44__late": "Random TabPFN (44)",
    "kumo_random__late": "Random Kumo (42)",
    "kumo_random43__late": "Random Kumo (43)",
    "kumo_random44__late": "Random Kumo (44)",
    "tabfm__early_concat": "TabFM early",
    "kumo__early_concat": "Kumo early",
}
VARIANCE_LABELS = {
    "spherical": "Common innovation variance",
    "diagonal": "Firm-specific innovation variances",
    "correlation": "Common marginal variances",
}
SOURCES = {}
CLAIMS = {}


def read(relative):
    """Read an existing artifact and record its exact content hash."""
    path = ROOT / relative
    if not path.is_file():
        raise ValueError(
            f"Missing recorded artifact: {relative}; restore it with DVC, not estimation"
        )
    SOURCES[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.suffix == ".json":
        return json.loads(path.read_text())
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def select(rows, **filters):
    """Require one unambiguous source row."""
    found = [r for r in rows if all(r[k] == str(v) for k, v in filters.items())]
    if len(found) != 1:
        raise ValueError(f"Expected one row for {filters}; found {len(found)}")
    return found[0]


def close(actual, expected, label, tolerance=1e-6):
    """Reject an inconsistent recorded numerical claim."""
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, abs_tol=tolerance, rel_tol=0
    ):
        raise ValueError(f"{label}: {actual} != {expected}")


def write(name, lines):
    (OUT / name).write_text("\n".join(lines) + "\n")


def tabular(name, columns, header, rows):
    """Let pandas own LaTeX table markup, including booktabs rules."""
    pd.DataFrame(rows, columns=header).to_latex(
        OUT / name, index=False, escape=False, column_format=columns
    )


def main():
    """Validate saved summaries and render tables, figure, and provenance."""
    OUT.mkdir(parents=True, exist_ok=True)
    comparison = read(f"{PANEL}/comparison.csv")
    decoding = read(f"{PANEL}/decoding.csv")
    contrasts = read(f"{PANEL}/contrasts.csv")
    annual = read(f"{PANEL}/annual-scores.csv")
    targets = read(f"{PANEL}/target-audit.csv")
    config = read(f"{PANEL}/configuration.json")
    read(f"{PANEL}/checkpoints.json")
    read(f"{PANEL}/manifest.json")
    protocol = f"{PANEL}/README.md"
    SOURCES[protocol] = hashlib.sha256((ROOT / protocol).read_bytes()).hexdigest()
    estimates = read("research/ladder/four/estimates.csv")
    r0 = read("research/ladder/r0/estimates.csv")
    bootstrap = read("research/ladder/r0/bootstrap.csv")
    mcs = read(f"{PANEL}/mcs.csv")
    if config["evaluation"] != [2020, 2025] or config["calibration"] != [2016, 2019]:
        raise ValueError("Unexpected panel windows")
    samples = [
        read(f"{PANEL}/observations/{year}-sample.json") for year in range(2016, 2026)
    ]
    for year, sample in zip(range(2016, 2026), samples, strict=True):
        previous = read(f"research/panel/three-support/observations/{year}-sample.json")
        if sample != previous:
            raise ValueError(
                f"Cohort or timing changed relative to legacy experiment: {year}"
            )
        current_context = read(f"{PANEL}/contexts/{year}-histories.json")
        previous_context = read(
            f"research/panel/three-support/contexts/{year}-histories.json"
        )
        if current_context != previous_context:
            raise ValueError(
                f"Model information changed relative to legacy experiment: {year}"
            )
    firms = [s["firms"] for s in samples[4:]]
    close(min(firms), 406, "minimum evaluation firms")
    close(max(firms), 459, "maximum evaluation firms")
    firm_days = sum(s["firms"] * s["evaluation_days"] for s in samples[4:])
    close(firm_days, 642024, "common firm-days")
    # Independently reconcile every aggregate in the grid to saved annual scores.
    keys = set()
    for row in comparison:
        key = tuple(row[k] for k in ("approach", "kernel", "innovation"))
        if key in keys:
            raise ValueError(f"Duplicate grid row: {key}")
        keys.add(key)
        close(float(row["firm_days"]), firm_days, str(key))
        total = sum(
            float(select(annual, column="|".join(key), year=y)["score"])
            for y in range(2020, 2026)
        )
        close(total, float(row["heldout_log_likelihood"]), str(key))
        ref = select(
            comparison,
            approach="fernandez_joint",
            kernel="exp",
            innovation="diagonal"
            if row["innovation"] == "control"
            else row["innovation"],
        )
        if row["gain_vs_joint_exp"]:
            close(
                total - float(ref["heldout_log_likelihood"]),
                float(row["gain_vs_joint_exp"]),
                str(key),
            )

    def gain(model, size=256, decoded=False):
        rung = (
            "histories"
            if size == 256 or model == "direct"
            else f"histories@support{size}"
        )
        approach = f"{rung}{'@decoded' if decoded else ''}__{model}"
        return float(
            select(
                comparison, approach=approach, kernel="matched", innovation="diagonal"
            )["gain_vs_joint_exp"]
        )

    def quality(model, size=256, start=2016):
        rung = (
            "histories"
            if size == 256 or model == "direct"
            else f"histories@support{size}"
        )
        return mean(
            float(
                select(decoding, rung=rung, representation=model, rank=5, year=y)[
                    "decoder_r2"
                ]
            )
            for y in range(start, 2026)
        )

    # Every shared legacy procedure must reproduce its recorded score.
    legacy = read("research/panel/three-support/comparison.csv")
    current = {(r["approach"], r["kernel"], r["innovation"]): r for r in comparison}
    overlap = 0
    for row in legacy:
        key = tuple(row[k] for k in ("approach", "kernel", "innovation"))
        if key in current:
            for field in ("heldout_log_likelihood", "lambda"):
                if not row[field] and not current[key][field]:
                    continue
                close(
                    float(current[key][field]),
                    float(row[field]),
                    f"legacy {key} {field}",
                    1e-5,
                )
            overlap += 1
    if overlap < 200:
        raise ValueError(f"Insufficient legacy overlap: {overlap}")
    CLAIMS["legacy_reproduced_rows"] = overlap
    legacy_quality = read("research/panel/three-support/decoding.csv")
    quality_keys = ("year", "rung", "representation", "rank")
    measured = {tuple(row[k] for k in quality_keys): row for row in decoding}
    checked_quality = 0
    for row in legacy_quality:
        key = tuple(row[k] for k in quality_keys)
        if key in measured:
            close(
                float(measured[key]["decoder_r2"]),
                float(row["decoder_r2"]),
                f"legacy decoder {key}",
            )
            checked_quality += 1
    CLAIMS["legacy_reproduced_decoder_rows"] = checked_quality
    main_rows, decoder_rows, supplementary_rows = [], [], []
    for model, label in (MODELS | SUPPLEMENTARY).items():
        native, calibrated, r2 = gain(model), gain(model, decoded=True), quality(model)
        (main_rows if model in MODELS else supplementary_rows).append(
            [label, f"{native:+,.1f}", f"{calibrated:+,.1f}", f"{r2:.3f}"]
        )
        decoder_rows.append([label, f"{r2:.3f}", f"{quality(model, start=2020):.3f}"])
        CLAIMS[model] = {
            "native_gain": native,
            "calibrated_gain": calibrated,
            "decoder_mean_2016_2025": r2,
            "decoder_mean_2020_2025": quality(model, start=2020),
        }
    tabular(
        "measurement.tex",
        "lrrr",
        ["Representation", "Native gain", "Calibrated gain", r"Decoder $R^2$"],
        main_rows,
    )
    tabular(
        "decoder-periods.tex",
        "lrr",
        ["Representation", "2016--2025", "2020--2025"],
        decoder_rows,
    )

    tabular(
        "supplementary-measurement.tex",
        "lrrr",
        ["Representation", "Native gain", "Calibrated gain", r"Decoder $R^2$"],
        supplementary_rows,
    )

    # Preserve EXAONE evidence on its original four-characteristic cohort.
    four = read("research/panel/four/comparison.csv")
    four_annual = read("research/panel/four/annual-scores.csv")
    four_quality = read("research/panel/four/decoding.csv")
    four_rows = []
    for model, label in {
        "direct": "Direct",
        "tabpfn_full__late": "TabPFN 3.5",
        "tabfm__late": "TabFM 1.1",
        "exaone__late": "EXAONE",
    }.items():
        values = []
        for suffix in ("", "@decoded"):
            approach = f"histories{suffix}__{model}"
            row = select(
                four, approach=approach, kernel="matched", innovation="diagonal"
            )
            total = sum(
                float(
                    select(four_annual, column=f"{approach}|matched|diagonal", year=y)[
                        "score"
                    ]
                )
                for y in range(2020, 2026)
            )
            close(total, float(row["heldout_log_likelihood"]), f"four {approach}")
            reference = float(
                select(
                    four,
                    approach="fernandez_joint",
                    kernel="exp",
                    innovation="diagonal",
                )["heldout_log_likelihood"]
            )
            close(
                total - reference,
                float(row["gain_vs_joint_exp"]),
                f"four gain {approach}",
            )
            close(float(row["firm_days"]), 87351, "four-characteristic firm-days")
            values.append(f"{float(row['gain_vs_joint_exp']):+,.1f}")
        r2 = mean(
            float(
                select(
                    four_quality, rung="histories", representation=model, rank=5, year=y
                )["decoder_r2"]
            )
            for y in range(2016, 2026)
        )
        four_rows.append([label, *values, f"{r2:.3f}"])
    tabular(
        "earlier-four.tex",
        "lrrr",
        ["Representation", "Native gain", "Calibrated gain", r"Decoder $R^2$"],
        four_rows,
    )

    networks = {
        "nonspatial": "Nonspatial",
        "fernandez_market_cap_assets": "Market cap/assets",
        "fernandez_market_to_book": "Market-to-book",
        "fernandez_dividend_yield": "Dividend yield",
        "fernandez_debt_maturity": "Debt maturity",
        "fernandez_joint": "Joint (extension)",
    }
    base = select(
        estimates,
        factors="capm",
        network="nonspatial",
        kernel="none",
        estimator="ols",
        self_links="False",
    )
    rows = []
    for network, label in networks.items():
        r = (
            base
            if network == "nonspatial"
            else select(
                estimates,
                factors="capm",
                network=network,
                kernel="exp",
                estimator="spatial_error_ml",
                self_links="False",
            )
        )
        close(float(r["firms"]), 33, "replication cohort")
        close(
            float(r["aic"]),
            2 * float(r["parameters"]) - 2 * float(r["log_likelihood"]),
            "AIC",
        )
        for field in ("premium_market", "se_market", "intensity", "intensity_se"):
            if not math.isfinite(float(r[field])):
                raise ValueError(f"Nonfinite replication {field}: {network}")
        CLAIMS[f"replication_{network}"] = {
            "slope_percent": 100 * float(r["premium_market"]),
            "se_percentage_points": 100 * float(r["se_market"]),
            "intensity": float(r["intensity"]),
            "intensity_se": float(r["intensity_se"]),
        }
        rows.append(
            [
                label,
                f"{float(r['intensity']):.3f}",
                f"{100 * float(r['premium_market']):.2f}",
                f"{float(r['log_likelihood']) - float(base['log_likelihood']):+.3f}",
                f"{float(r['aic']):.2f}",
            ]
        )
        rows.append(
            [
                "",
                "" if network == "nonspatial" else f"({float(r['intensity_se']):.3f})",
                f"({100 * float(r['se_market']):.2f})",
                "",
                "",
            ]
        )
    tabular(
        "replication.tex",
        "lrrrr",
        ["Network", r"$\lambda$", r"Beta slope (\%)", r"$\Delta\log L$", "AIC"],
        rows,
    )
    rows = []
    for network, label in list(networks.items())[1:-1]:
        r = select(
            r0,
            table="common_four",
            factors="capm",
            kernel="exp",
            network=network,
            estimator="spatial_lag_iv",
            self_links="False",
        )
        b = select(
            bootstrap,
            table="common_four",
            network=network,
            parameter="iv_intensity",
            factors="capm",
        )
        rows.append(
            [
                label,
                f"{float(r['intensity']):.3f}",
                f"{float(r['intensity_p']):.3f}",
                f"[{float(b['lower']):.3f}, {float(b['upper']):.3f}]",
                b["replicates"],
            ]
        )
    tabular(
        "replication-iv.tex",
        "lrrrr",
        ["Network", r"$\rho$", "Conditional $p$", "Bootstrap interval", "Draws"],
        rows,
    )

    contrast_rows = []
    for model, label in (("tabpfn_full", "TabPFN"), ("kumo", "Kumo")):
        for seed in (42, 43, 44):
            random = f"{model}_random{'' if seed == 42 else seed}"
            for arm in ("diagonal", "correlation"):
                left = f"histories@decoded__{model}__late|matched|{arm}"
                right = f"histories@decoded__{random}__late|matched|{arm}"
                r = select(contrasts, left=left, right=right)
                diffs = []
                for y in range(2020, 2026):
                    d = float(select(annual, column=left, year=y)["score"]) - float(
                        select(annual, column=right, year=y)["score"]
                    )
                    close(d, float(r[f"year_{y}"]), f"annual contrast {y}")
                    diffs.append(d)
                close(sum(diffs), float(r["difference"]), "contrast sum")
                CLAIMS[f"contrast_{model}_{seed}_{arm}"] = r
                if model == "tabpfn_full" and seed == 42:
                    CLAIMS[f"contrast_{arm}"] = r
                contrast_rows.append(
                    [
                        label,
                        str(seed),
                        "Innovation" if arm == "diagonal" else "Marginal",
                        f"{sum(diffs):+,.1f}",
                        f"[{float(r['lower_21']):+,.1f}, {float(r['upper_21']):+,.1f}]",
                        f"[{float(r['lower_63']):+,.1f}, {float(r['upper_63']):+,.1f}]",
                    ]
                )
    tabular(
        "weight-contrasts.tex",
        "lllrll",
        [
            "Model",
            "Seed",
            "Variances",
            "Difference",
            "21-day interval",
            "63-day interval",
        ],
        contrast_rows,
    )
    for model in ("tabpfn_full", "kumo"):
        differences = [
            float(CLAIMS[f"contrast_{model}_{seed}_diagonal"]["difference"])
            for seed in (42, 43, 44)
        ]
        CLAIMS[f"weights_{model}"] = {
            "minimum": min(differences),
            "maximum": max(differences),
        }
    included = [
        r["column"]
        for r in mcs
        if r["family"] == "diagonal|matched" and r["included"] == "True"
    ]
    CLAIMS["matched_diagonal_confidence_set"] = included
    names = {
        "reference_exposures": "Reference exposures",
        "covariance_exposures": "In-panel exposures",
    }

    def forecast_label(column):
        if column.startswith("h3__"):
            return "Three-year " + forecast_label(column.removeprefix("h3__"))
        approach = column.split("|")[0]
        if approach in names:
            return names[approach]
        if approach.startswith("histories"):
            rung, model = approach.split("__", 1)
            label = (MODELS | SUPPLEMENTARY)[model]
            kind = "Calibrated" if "@decoded" in rung else "Native"
            suffix = ""
            if "@support" in rung:
                suffix = " (support " + rung.split("@support")[1].split("@")[0] + ")"
            if "@calibration" in rung:
                suffix = (
                    " (training firms "
                    + rung.split("@calibration")[1].split("@")[0]
                    + ")"
                )
            return f"{kind} {label}{suffix}"
        if approach in networks:
            return networks[approach]
        controls = {
            "uniform_network": "Uniform network",
            "zero_network": "Zero network",
            "raw_sample_covariance": "Sample covariance",
            "ff5_mom_diagonal": "Diagonal factor model",
            "ff5_mom_sample_residual_covariance": "Factor model with sample residual covariance",
        }
        return controls[approach]

    tabular(
        "confidence-set.tex",
        "l",
        ["Retained forecast"],
        [[forecast_label(c)] for c in included],
    )

    sizes = [32, 64, 128, 256]
    plt.rcParams.update(
        {
            "font.family": "serif",
            "pgf.texsystem": "pdflatex",
            "pgf.rcfonts": False,
            "pgf.preamble": r"\usepackage{lmodern}",
            "font.size": 9,
        }
    )
    fig, axes = plt.subplots(
        2, 2, figsize=(6.5, 4.8), sharey="row", layout="constrained"
    )
    plotted = {k: v for k, v in MODELS.items() if k != "supervised_mlp16"}
    colors = ["#555555", "#0072B2", "#009E73", "#D55E00", "#CC79A7", "#AA7700"]
    for (model, label), color, marker in zip(
        plotted.items(), colors, ["o", "s", "^", "D", "v", "P"], strict=True
    ):
        encoder = [
            [gain(model, size, True) for size in sizes],
            [quality(model, size) for size in sizes],
        ]
        calibration = [[], []]
        for size in sizes:
            rung = f"histories@calibration{size}"
            calibration[0].append(
                float(
                    select(
                        comparison,
                        approach=f"{rung}@decoded__{model}",
                        kernel="matched",
                        innovation="diagonal",
                    )["gain_vs_joint_exp"]
                )
            )
            calibration[1].append(
                mean(
                    float(
                        select(
                            decoding, rung=rung, representation=model, rank=5, year=y
                        )["decoder_r2"]
                    )
                    for y in range(2016, 2026)
                )
            )
        CLAIMS[f"support_{model}"] = {"calibrated": encoder[0], "decoder": encoder[1]}
        CLAIMS[f"calibration_{model}"] = {
            "calibrated": calibration[0],
            "decoder": calibration[1],
        }
        for column, series in enumerate((encoder, calibration)):
            for row, values in enumerate(series):
                axes[row, column].plot(
                    sizes,
                    values,
                    label=label,
                    color=color,
                    marker=marker,
                    linewidth=1.3,
                    markersize=3.5,
                )
    for column, title in enumerate(("Encoder context", "Financial calibration")):
        axes[0, column].set_title(title)
        for row in range(2):
            ax = axes[row, column]
            ax.set_xscale("log", base=2)
            ax.set_xticks(sizes, labels=[str(s) for s in sizes])
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", alpha=0.2)
            ax.axhline(0, color="0.65", linewidth=0.6, linestyle="--", zorder=0)
        axes[1, column].set_xlabel(
            "Support examples" if column == 0 else "Training firms per fold"
        )
    axes[0, 0].set_ylabel("Calibrated log-score gain")
    axes[1, 0].set_ylabel("Mean decoder $R^2$")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3, frameon=False)
    fig.savefig(OUT / "support.pgf")
    plt.close(fig)

    controls = []
    for r in comparison:
        if r["kernel"] != "none":
            continue
        arm = "diagonal" if r["innovation"] == "control" else r["innovation"]
        ref = select(
            comparison, approach="fernandez_joint", kernel="exp", innovation=arm
        )
        value = float(r["heldout_log_likelihood"])
        controls.append(
            [
                {
                    "uniform_network": "Uniform network",
                    "zero_network": "Zero network",
                    "raw_sample_covariance": "Sample covariance",
                    "ff5_mom_diagonal": "Factor model, diagonal residuals",
                    "ff5_mom_sample_residual_covariance": "Factor model, sample residual covariance",
                }[r["approach"]],
                VARIANCE_LABELS[arm],
                f"{value:,.1f}",
                f"{value - float(ref['heldout_log_likelihood']):+,.1f}",
            ]
        )
    tabular(
        "covariance-controls.tex",
        r">{\raggedright\arraybackslash}p{0.35\linewidth}"
        r">{\raggedright\arraybackslash}p{0.25\linewidth}rr",
        ["Approach", "Reference specification", "Log score", "Gain"],
        controls,
    )
    # Entire recorded network grid, including supplementary supports and histories.
    header = ["Approach"] + [
        f"{k}/{a}" for k in ("Unit", "Median", "Matched") for a in ("S", "D", "C")
    ]
    grid_rows = []
    short_names = {
        **MODELS,
        **SUPPLEMENTARY,
        "supervised_mlp16": "Supervised network",
        "tabfm__early_concat_labelnull": "TabFM constant",
        "tabpfn_full__late": "TabPFN",
        "tabpfn_full_random__late": "Random TabPFN",
    }
    lookup = {(r["approach"], r["kernel"], r["innovation"]): r for r in comparison}
    for approach in dict.fromkeys(
        r["approach"] for r in comparison if r["kernel"] != "none"
    ):
        history = "3y" if approach.startswith("h3__") else "5y"
        base_name = approach.removeprefix("h3__")
        if base_name.startswith("histories"):
            rung, model = base_name.split("__", 1)
            support = (
                rung.split("@support")[1].split("@")[0] if "@support" in rung else "256"
            )
            if "@calibration" in rung:
                support += "/fit" + rung.split("@calibration")[1].split("@")[0]
            distance = "calibrated" if "@decoded" in rung else "native"
            label = f"{history} / {support} / {distance} / {short_names[model]}"
        else:
            label = {
                **networks,
                "reference_exposures": "Reference exposures",
                "covariance_exposures": "In-panel exposures",
            }[base_name]
            label = f"{history} / {label}"
        values = [label]
        for kernel in ("exp", "median", "matched"):
            for arm in ("spherical", "diagonal", "correlation"):
                r = lookup.get((approach, kernel, arm))
                values.append(
                    f"{float(r['gain_vs_joint_exp']):+,.1f}"
                    if r and r["gain_vs_joint_exp"]
                    else "---"
                )
        grid_rows.append(values)
    pd.DataFrame(grid_rows, columns=header).to_latex(
        OUT / "full-grid.tex",
        index=False,
        escape=False,
        longtable=True,
        column_format=r">{\raggedright\arraybackslash}p{0.28\linewidth}rrrrrrrrr",
        caption="Complete three-characteristic comparison: gains over the joint exponential-kernel reference within each innovation specification. "
        "All kernels are exponential; Unit, Median, and Matched denote unit, median-distance, and matched-neighbor bandwidths. "
        "S: spherical; D: diagonal; C: fixed marginal variances. "
        "Model rows identify history length in years, support examples, distance, and representation. "
        "Fit indicates training firms per financial calibration fold at 256 encoder examples. A dash denotes an unreported cell.",
        label="tab:full-grid",
    )
    rows = []
    for rank in (3, 5, 8):
        selected = [
            select(targets, target="reference", rank=rank, year=y)
            for y in range(2016, 2026)
        ]
        rows.append(
            [str(rank)]
            + [
                f"{mean(float(r[k]) for r in selected):.3f}"
                for k in (
                    "half_correlation",
                    "spearman_brown",
                    "distance_reliability",
                    "commonality_mean",
                )
            ]
        )
    tabular(
        "target-reliability.tex",
        "rrrrr",
        [
            "Rank",
            "Half correlation",
            "Spearman--Brown",
            "Distance reliability",
            "Commonality",
        ],
        rows,
    )
    tabular(
        "cohorts.tex",
        "rrrrr",
        ["Year", "Firms", "Prior days", "Scored days", "Reference firms"],
        [
            [str(y)]
            + [
                str(s[k])
                for k in (
                    "firms",
                    "past_complete_days",
                    "evaluation_days",
                    "reference_firms",
                )
            ]
            for y, s in zip(range(2016, 2026), samples, strict=True)
        ],
    )
    CLAIMS["firm_days"] = firm_days
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        undefined=StrictUndefined,
        autoescape=False,
        variable_start_string="((*",
        variable_end_string="*))",
    )
    values = {
        "claims": CLAIMS,
        "firms_min": min(firms),
        "firms_max": max(firms),
        "figure_sizes": sizes,
    }
    (OUT / "numbers.tex").write_text(
        env.get_template("numbers.tex.j2").render(**values)
    )
    audit = {
        "design": "three-foundations",
        "legacy_reviewed_commit": "162a7fd6f32fa1a02f8caa6262968687a285b417",
        "source_sha256": SOURCES,
        "rendering_source_sha256": {
            str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in (
                Path(__file__),
                Path(__file__).with_name("numbers.tex.j2"),
                Path(__file__).with_name("main.tex"),
            )
        },
        "selectors": {
            "main_table": "histories, support=256, rank=5, matched/diagonal; reference=joint/exp/diagonal",
            "decoder": "unweighted annual mean, 2016-2025; supplement also 2020-2025",
            "replication": "four, 33 firms, CAPM, zero diagonal, exp, SEM-ML; nonspatial OLS",
            "scores": "sum saved annual scores, 2020-2025; no estimation rerun",
        },
        "claims": CLAIMS,
        "validated_grid_rows": len(comparison),
    }
    write("claims-audit.json", [json.dumps(audit, indent=2)])
    print(
        f"Rendered publication assets; validated {len(comparison)} score rows and {firm_days:,} firm-days."
    )


if __name__ == "__main__":
    main()
