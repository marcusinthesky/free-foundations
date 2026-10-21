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
    "supervised_mlp16": "Valuation-task network",
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
}
VARIANCE_LABELS = {
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
        OUT / name,
        index=False,
        escape=False,
        column_format=columns,
        multicolumn_format="c",
    )


def validate_inventory(comparison, decoding, annual):
    """Reject partial study outputs before producing publication assets."""
    expected = set()
    for arm in ("diagonal", "correlation"):
        expected.add(("fernandez_joint", "exp", arm))
        for model in MODELS | SUPPLEMENTARY:
            for suffix in ("", "@decoded"):
                expected.add((f"histories{suffix}__{model}", "matched", arm))
    for model in MODELS:
        if model == "supervised_mlp16":
            continue
        for size in (32, 64, 128, 256):
            expected.add(
                (f"histories@calibration{size}@decoded__{model}", "matched", "diagonal")
            )
            if model != "direct" and size != 256:
                expected.add(
                    (f"histories@support{size}@decoded__{model}", "matched", "diagonal")
                )
    for approach in ("reference_exposures", "covariance_exposures"):
        expected.add((approach, "matched", "diagonal"))
    for approach in (
        "raw_sample_covariance",
        "ff5_mom_diagonal",
        "ff5_mom_sample_residual_covariance",
    ):
        for arm in ("control", "correlation"):
            expected.add((approach, "none", arm))
    for approach in ("uniform_network", "zero_network"):
        for arm in ("diagonal", "correlation"):
            expected.add((approach, "none", arm))
    keys = [(r["approach"], r["kernel"], r["innovation"]) for r in comparison]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate comparison procedure")
    if missing := expected - set(keys):
        raise ValueError(f"Incomplete publication procedures: {sorted(missing)}")
    annual_keys = [(r["column"], int(r["year"])) for r in annual]
    if len(set(annual_keys)) != len(annual_keys):
        raise ValueError("Duplicate annual score")
    required_annual = {
        ("|".join(key), y) for key in expected for y in range(2020, 2026)
    }
    if missing := required_annual - set(annual_keys):
        raise ValueError(f"Incomplete evaluation years: {sorted(missing)}")
    for model in MODELS | SUPPLEMENTARY:
        for year in range(2016, 2026):
            row = select(
                decoding, rung="histories", representation=model, rank=5, year=year
            )
            if not math.isfinite(float(row["decoder_r2"])):
                raise ValueError(f"Nonfinite decoder quality: {model}, {year}")


def main():
    """Validate saved summaries and render tables, figure, and provenance."""
    SOURCES.clear()
    CLAIMS.clear()
    OUT.mkdir(parents=True, exist_ok=True)
    comparison = read(f"{PANEL}/comparison.csv")
    decoding = read(f"{PANEL}/decoding.csv")
    contrasts = read(f"{PANEL}/contrasts.csv")
    annual = read(f"{PANEL}/annual-scores.csv")
    targets = read(f"{PANEL}/target-audit.csv")
    config = read(f"{PANEL}/configuration.json")
    read(f"{PANEL}/checkpoints.json")
    manifest = read(f"{PANEL}/manifest.json")
    protocol = f"{PANEL}/README.md"
    SOURCES[protocol] = hashlib.sha256((ROOT / protocol).read_bytes()).hexdigest()
    r0 = read("research/replication/estimates.csv")
    estimates = [row for row in r0 if row["table"] == "common_four"]
    bootstrap = read("research/replication/bootstrap.csv")
    read("research/replication/audit.json")
    mcs = read(f"{PANEL}/mcs.csv")
    if config["evaluation"] != [2020, 2025] or config["calibration"] != [2016, 2019]:
        raise ValueError("Unexpected panel windows")
    samples = [
        read(f"{PANEL}/observations/{year}-sample.json") for year in range(2016, 2026)
    ]
    for year in range(2016, 2026):
        read(f"{PANEL}/contexts/{year}-histories.json")
    validate_inventory(comparison, decoding, annual)
    firms = [s["firms"] for s in samples[4:]]
    firm_days = sum(s["firms"] * s["evaluation_days"] for s in samples[4:])
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

    main_rows, decoder_rows = [], []
    for model, label in (MODELS | SUPPLEMENTARY).items():
        native, calibrated, r2 = gain(model), gain(model, decoded=True), quality(model)
        if model in MODELS:
            main_rows.append(
                [label, f"{r2:.3f}", f"{native:+,.1f}", f"{calibrated:+,.1f}"]
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
        [
            "Representation",
            r"Exposure-prediction $R^2$",
            "Native gain",
            "Calibrated gain",
        ],
        main_rows,
    )
    benchmark_rows = []
    for approach, label in (
        ("reference_exposures", "Reference exposures"),
        ("covariance_exposures", "In-panel exposures"),
    ):
        selector = {
            "approach": approach,
            "kernel": "matched",
            "innovation": "diagonal",
        }
        row = select(comparison, **selector)
        value = float(row["gain_vs_joint_exp"])
        CLAIMS[f"benchmark_{approach}"] = {
            "selector": selector,
            "forecast_gain": value,
        }
        benchmark_rows.append([label, f"{value:+,.1f}"])
    tabular(
        "measurement-benchmarks.tex",
        "lr",
        ["Return-based benchmark", "Forecast gain"],
        benchmark_rows,
    )
    tabular(
        "decoder-periods.tex",
        "lrr",
        ["Representation", "2016--2025", "2020--2025"],
        decoder_rows,
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
        for seed in (42, 43, 44) if model == "tabpfn_full" else (42,):
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
            for seed in ((42, 43, 44) if model == "tabpfn_full" else (42,))
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
        if r["kernel"] != "none" or r["innovation"] == "spherical":
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
    validation_root = "research/panel/three-foundations-validation"
    validated = read(f"{validation_root}/validation.json")
    diagnostic_config = read(f"{validation_root}/configuration.json")
    diagnostic_protocol = f"{validation_root}/README.md"
    SOURCES[diagnostic_protocol] = hashlib.sha256(
        (ROOT / diagnostic_protocol).read_bytes()
    ).hexdigest()
    if (
        diagnostic_config["protocol_sha256"] != SOURCES[diagnostic_protocol]
        or diagnostic_config["evaluation"] != [2020, 2025]
        or diagnostic_config["calibration"] != [2016, 2019]
        or diagnostic_config["encoder_support"] != 256
        or diagnostic_config["rank"] != 5
        or diagnostic_config["partitions"]
        != ["", "fold-audit-1", "fold-audit-2", "fold-audit-3", "fold-audit-4"]
        or validated["partitions"] != diagnostic_config["partitions"]
        or not validated["overlap"]
        or any(
            not math.isfinite(row["max_daily_error"]) or row["max_daily_error"] > 1e-5
            for row in validated["overlap"]
        )
    ):
        raise ValueError("Diagnostic records differ from their declared protocol")
    diagnostic_contrasts = read(f"{validation_root}/contrasts.csv")
    direct_contrasts = read(f"{validation_root}/principal-contrasts.csv")
    diagnostic_scores = read(f"{validation_root}/scores.csv")
    diagnostic_decoders = read(f"{validation_root}/decoding.csv")
    null_checks = [
        r
        for r in read(f"{validation_root}/null-checks.csv")
        if r["representation"] == "kumo_random__late"
    ]
    expected_nulls = {
        (str(year), f"kumo_random{suffix}__late")
        for year in range(2016, 2026)
        for suffix in ("",)
    }
    if (
        len(null_checks) != len(expected_nulls)
        or {(r["year"], r["representation"]) for r in null_checks} != expected_nulls
        or any(
            not math.isfinite(float(r["prediction_max_error"]))
            or float(r["prediction_max_error"]) > 1e-12
            or float(r["feature_spread"]) != 0
            or int(r["prediction_vectors"]) > 5
            for r in null_checks
        )
    ):
        raise ValueError("Incomplete or inconsistent intercept-only diagnostic")
    dates = sum(int(sample["evaluation_days"]) for sample in samples[4:])
    close(dates, validated["dates"], "scored return-vector count")
    close(firm_days, validated["firm_days"], "diagnostic firm-days")
    CLAIMS["scored_dates"] = dates
    CLAIMS["target_commonality"] = 100 * mean(
        float(
            select(targets, target="reference", rank=5, year=year)["commonality_mean"]
        )
        for year in range(2016, 2026)
    )
    rows = []
    for name in list(MODELS)[3:]:
        for arm in ("diagonal", "correlation"):
            left = f"histories@decoded__{name}|matched|{arm}"
            for kind, source, right in (
                ("Calibration", contrasts, f"histories__{name}|matched|{arm}"),
                ("Direct", direct_contrasts, f"histories__direct|matched|{arm}"),
            ):
                r = select(source, left=left, right=right)
                actual = sum(
                    float(select(annual, column=left, year=y)["score"])
                    - float(select(annual, column=right, year=y)["score"])
                    for y in range(2020, 2026)
                )
                close(actual, float(r["difference"]), "headline paired contrast")
                if (
                    name == "tabpfn_full__late"
                    and arm == "diagonal"
                    and kind == "Direct"
                ):
                    CLAIMS["pfn_direct_normalized"] = actual / firm_days
                for block in (21, 63):
                    lower, upper = (
                        float(r[f"lower_{block}"]),
                        float(r[f"upper_{block}"]),
                    )
                    if not (
                        math.isfinite(lower) and math.isfinite(upper) and lower <= upper
                    ):
                        raise ValueError("Invalid headline contrast interval")
                rows.append(
                    [
                        MODELS[name],
                        kind,
                        "Innovation" if arm == "diagonal" else "Marginal",
                        f"{actual:+,.1f}",
                        f"[{float(r['lower_21']):+,.1f}, {float(r['upper_21']):+,.1f}]",
                        f"[{float(r['lower_63']):+,.1f}, {float(r['upper_63']):+,.1f}]",
                    ]
                )
    tabular(
        "measurement-contrasts.tex",
        "lllrll",
        [
            "Model",
            "Contrast",
            "Variances",
            "Difference",
            "21-day interval",
            "63-day interval",
        ],
        rows,
    )
    for arm, filename in (
        ("diagonal", "variance-contrasts.tex"),
        ("correlation", "variance-contrasts-marginal.tex"),
    ):
        variance_rows = []
        for name in list(MODELS)[3:]:
            r = select(
                contrasts,
                left=f"histories@decoded__{name}|matched|{arm}",
                right=f"histories__{name}|matched|{arm}",
            )
            variance_rows.append(
                [
                    MODELS[name],
                    f"{float(r['difference']):+,.1f}",
                    f"[{float(r['lower_21']):+,.1f}, {float(r['upper_21']):+,.1f}]",
                    f"[{float(r['lower_63']):+,.1f}, {float(r['upper_63']):+,.1f}]",
                ]
            )
        tabular(
            filename,
            "lrll",
            ["Model", "Difference", "21-day interval", "63-day interval"],
            variance_rows,
        )
    rows = []
    for name, label in MODELS.items():
        values = []
        for arm in ("diagonal", "correlation"):
            for metric in ("euclidean", "chord"):
                left = f"normalization_decoded_{metric}__{name}|matched|{arm}"
                right = f"normalization_native_{metric}__{name}|matched|{arm}"
                r = select(diagnostic_contrasts, left=left, right=right)
                close(
                    float(r["difference"]),
                    float(select(diagnostic_scores, column=left)["score"])
                    - float(select(diagnostic_scores, column=right)["score"]),
                    "normalization contrast",
                )
                values.append(f"{float(r['difference']):+,.1f}")
        rows.append([label, *values])
    tabular(
        "normalization.tex",
        "lrrrr",
        pd.MultiIndex.from_tuples(
            [
                ("", "Representation"),
                ("Fitted innovation variances", "Euclidean"),
                ("Fitted innovation variances", "Chord"),
                ("Common marginal variances", "Euclidean"),
                ("Common marginal variances", "Chord"),
            ]
        ),
        rows,
    )
    rows = []
    for arm in ("diagonal", "correlation"):
        r = select(
            diagnostic_contrasts,
            left=f"published_native__direct|matched|{arm}",
            right=f"normalization_native_chord__direct|matched|{arm}",
        )
        CLAIMS[f"direct_unit_{arm}"] = float(r["difference"])
        for partition in range(5):
            for suffix in ("", "43", "44"):
                r = select(
                    diagnostic_contrasts,
                    left=f"fold{partition}@decoded__tabpfn_full__late|matched|{arm}",
                    right=f"fold{partition}@decoded__tabpfn_full_random{suffix}__late|matched|{arm}",
                )
    fold_models = (
        MODELS
        | {k: v for k, v in SUPPLEMENTARY.items() if k.startswith("tabpfn_full_random")}
        | {"intercept_only": "Intercept only"}
    )
    for name, label in fold_models.items():
        values = []
        for arm in ("diagonal", "correlation"):
            baseline = float(
                select(
                    diagnostic_scores, column=f"published_native__direct|matched|{arm}"
                )["score"]
            )
            gains = [
                float(
                    select(
                        diagnostic_scores,
                        column=f"fold{partition}@decoded__{name}|matched|{arm}",
                    )["score"]
                )
                - baseline
                for partition in range(5)
            ]
            values.append(f"[{min(gains):+,.0f}, {max(gains):+,.0f}]")
        fit = [
            mean(
                float(
                    select(
                        diagnostic_decoders,
                        representation=name,
                        partition=partition,
                        year=year,
                    )["decoder_r2"]
                )
                for year in range(2016, 2026)
            )
            for partition in range(5)
        ]
        rows.append([label, *values, f"[{min(fit):.3f}, {max(fit):.3f}]"])
    tabular(
        "fold-sensitivity.tex",
        "llll",
        ["Representation", "Fitted variances", "Common marginals", "Decoder $R^2$"],
        rows,
    )
    best = max(MODELS, key=lambda name: CLAIMS[name]["decoder_mean_2016_2025"])
    CLAIMS["decoder_best"] = {
        "name": MODELS[best],
        "value": CLAIMS[best]["decoder_mean_2016_2025"],
    }
    CLAIMS["firm_days"] = firm_days
    for path, recorded in manifest["sha256"].items():
        if path in SOURCES and SOURCES[path] != recorded:
            raise ValueError(f"Artifact differs from recorded manifest: {path}")
    required_manifest = {
        f"{PANEL}/{name}"
        for name in (
            "comparison.csv",
            "decoding.csv",
            "annual-scores.csv",
            "configuration.json",
        )
    }
    if missing := required_manifest - manifest["sha256"].keys():
        raise ValueError(f"Incomplete source manifest: {sorted(missing)}")
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
            "main_benchmarks": "reference_exposures and covariance_exposures, matched/diagonal; reference=joint/exp/diagonal",
            "decoder": "unweighted annual mean, 2016-2025; supplement also 2020-2025",
            "replication": "four, 33 firms, CAPM, zero diagonal, exp, SEM-ML; nonspatial OLS",
            "scores": "sum saved annual scores, 2020-2025; no estimation rerun",
            "normalization": "rank=5, support=256, original folds; calibration minus native within metric",
            "fold_sensitivity": "five fixed assignments; range of scores versus published native direct; mean decoder fit 2016-2025",
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
