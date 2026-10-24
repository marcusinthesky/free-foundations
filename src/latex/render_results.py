"""Render publication assets from saved estimates; never run empirical models."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from itertools import pairwise
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
GEOMETRY = "research/panel/geometry"
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

GEOMETRY_MODELS = (
    MODELS
    | SUPPLEMENTARY
    | {
        "kumo_random43__late": "Random Kumo (43)",
        "kumo_random44__late": "Random Kumo (44)",
    }
)
CHARACTERISTICS = {
    "fernandez_market_cap_assets": "Market cap/assets",
    "fernandez_market_to_book": "Market-to-book",
    "fernandez_dividend_yield": "Dividend yield",
    "fernandez_joint": "Joint characteristics",
}
GEOMETRY_APPROACHES = (
    CHARACTERISTICS
    | {
        f"histories{suffix}__{model}": label + (" (decoded)" if suffix else " (native)")
        for model, label in GEOMETRY_MODELS.items()
        for suffix in ("", "@decoded")
    }
    | {"histories@decoded__intercept_only": "Intercept only (decoded)"}
)


def record(relative):
    """Require an artifact and record its content hash without interpreting it."""
    path = ROOT / relative
    if not path.is_file():
        raise ValueError(
            f"Missing recorded artifact: {relative}; restore it with DVC, not estimation"
        )
    SOURCES[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def read(relative):
    """Read an existing artifact and record its exact content hash."""
    path = record(relative)
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


def replication_cohort_counts(cohorts, estimates):
    """Bind displayed sample sizes to the saved firms and every fitted specification."""
    counts = {}
    for arm, characteristics in (("four", 4), ("three", 3)):
        key = f"common_{arm}"
        cohort = cohorts[key]
        tickers = cohort["tickers"]
        count = cohort["firms"]
        if (
            not isinstance(count, int)
            or count < 4
            or len(tickers) != count
            or len(set(tickers)) != count
            or len(cohort["characteristics"]) != characteristics
        ):
            raise ValueError(f"Invalid replication cohort: {key}")
        selected = [row for row in estimates if row["table"] == key]
        if not selected:
            raise ValueError(f"Missing replication estimates: {key}")
        for row in selected:
            close(float(row["firms"]), count, f"replication cohort {key}")
        counts[key] = count
    return counts


def render_replication_premiums(estimates, bootstrap, cohorts):
    """Separate conditional premium errors from generated-beta percentile intervals."""
    counts = replication_cohort_counts(cohorts, estimates)
    claims, rows = [], []
    procedures = (
        ("OLS", "ols", "nonspatial", "none", "ols_premium"),
        ("Joint lag IV", "spatial_lag_iv", "fernandez_joint", "exp", "iv_premium"),
        ("Joint error ML", "spatial_error_ml", "fernandez_joint", "exp", "sem_premium"),
    )
    for arm in ("four", "three"):
        table = f"common_{arm}"
        for label, estimator, network, kernel, parameter in procedures:
            point = select(
                estimates,
                table=table,
                factors="capm",
                network=network,
                kernel=kernel,
                estimator=estimator,
                self_links="False",
            )
            interval = select(
                bootstrap,
                table=table,
                factors="capm",
                network="fernandez_joint",
                parameter=parameter,
            )
            premium = float(point["premium_market"])
            error = float(point["se_market"])
            lower, upper = float(interval["lower"]), float(interval["upper"])
            draws = float(interval["replicates"])
            if (
                not all(
                    math.isfinite(value)
                    for value in (premium, error, lower, upper, draws)
                )
                or error < 0
                or lower > upper
                or draws != 199
            ):
                raise ValueError(
                    f"Invalid generated-beta premium summary: {table}/{estimator}"
                )
            claim = {
                "cohort": table,
                "firms": counts[table],
                "estimator": estimator,
                "premium_percent": 100 * premium,
                "conditional_se_percentage_points": 100 * error,
                "generated_beta_lower_percent": 100 * lower,
                "generated_beta_upper_percent": 100 * upper,
                "valid_draws": int(draws),
            }
            claims.append(claim)
            rows.append(
                [
                    arm.capitalize(),
                    str(counts[table]),
                    label,
                    f"{claim['premium_percent']:.2f}",
                    f"{claim['conditional_se_percentage_points']:.2f}",
                    (
                        f"[{claim['generated_beta_lower_percent']:.2f}, "
                        f"{claim['generated_beta_upper_percent']:.2f}]"
                    ),
                    str(claim["valid_draws"]),
                ]
            )
    CLAIMS["replication_premium_uncertainty"] = claims
    tabular(
        "replication-premiums.tex",
        "lrlrrcr",
        [
            "Cohort",
            "$N$",
            "Estimator",
            "Premium",
            "Cond. SE",
            r"Bootstrap 95\% interval",
            "Draws",
        ],
        rows,
    )


def validate_source_recovery(summary):
    """Reconcile observed characteristic coverage and the declared recovery policy."""
    years = summary["source_years"]
    if (
        not years
        or years[0] != 2009
        or years != list(range(years[0], years[-1] + 1))
        or summary["contract"]["years"] != years
        or summary["contract"]["maximum_age_days"] != 550
        or not summary["preserve_complete_annual_first_three"]
        or set(summary["annual_forms"]) != {"10-K", "10-K/A"}
        or set(summary["fallback_forms"]) != {"10-K", "10-K/A", "10-Q", "10-Q/A"}
        or summary["quarterly_facts"] != "instant only; no quarterly duration facts"
    ):
        raise ValueError("Unexpected observed-data recovery policy")
    characteristics = (
        "market_cap_assets",
        "market_to_book",
        "dividend_yield",
        "debt_maturity",
    )
    snapshots = recovered = annual = aligned_debt = 0
    for year in years:
        row = summary["by_year"][str(year)]
        size = row["snapshots"]
        available = row["available_by_characteristic"]
        missing = row["missing_by_characteristic"]
        if set(available) != set(characteristics) or set(missing) != set(
            characteristics
        ):
            raise ValueError("Incomplete characteristic coverage inventory")
        counts = [
            size,
            row["complete_first_three"],
            row["annual_complete_first_three"],
            row["quarterly_recovered_snapshots"],
            row["aligned_quarterly_debt_recovered_snapshots"],
            *available.values(),
            *missing.values(),
        ]
        if (
            any(not isinstance(value, int) or value < 0 for value in counts)
            or size == 0
        ):
            raise ValueError("Invalid characteristic coverage counts")
        for name in characteristics:
            if available[name] + missing[name] != size:
                raise ValueError("Observed and missing characteristic counts disagree")
        complete = row["complete_first_three"]
        if complete != row["annual_complete_first_three"] + row[
            "quarterly_recovered_snapshots"
        ] or complete > min(available[name] for name in characteristics[:3]):
            raise ValueError("Annual and recovered snapshot counts disagree")
        debt_fills = row["aligned_quarterly_debt_recovered_snapshots"]
        if debt_fills > min(
            row["annual_complete_first_three"], available["debt_maturity"]
        ):
            raise ValueError("Aligned debt recoveries exceed eligible annual snapshots")
        snapshots += size
        recovered += row["quarterly_recovered_snapshots"]
        annual += row["annual_complete_first_three"]
        aligned_debt += debt_fills
    policies = summary["source_policy_counts"]
    if (
        summary["snapshot_rows"] != snapshots
        or sum(policies.values()) != snapshots
        or policies.get("quarterly_recovery", 0) != recovered
        or policies.get("annual", 0) != annual
        or summary["aligned_quarterly_debt_recovered_snapshots"] != aligned_debt
    ):
        raise ValueError("Recovery policy totals disagree with annual coverage")
    return {
        "first_year": years[0],
        "last_year": years[-1],
        "years": len(years),
        "snapshot_rows": snapshots,
        "quarterly_recovered_snapshots": recovered,
        "aligned_quarterly_debt_recovered_snapshots": aligned_debt,
    }


def render_source_recovery(summary, samples):
    """Display observed source coverage separately from annual estimation eligibility."""
    claims = validate_source_recovery(summary)
    claims["fixed_annual_cohort"] = len(
        set.intersection(*(set(row["tickers"]) for row in samples))
    )
    CLAIMS["source_recovery"] = claims
    tabular(
        "source-coverage.tex",
        "rrrrrr",
        [
            "Year",
            "Cap/assets",
            "Market/book",
            "Dividend yield",
            "Debt maturity",
            "Quarterly recoveries",
        ],
        [
            [str(year)]
            + [
                str(summary["by_year"][str(year)]["available_by_characteristic"][name])
                for name in (
                    "market_cap_assets",
                    "market_to_book",
                    "dividend_yield",
                    "debt_maturity",
                )
            ]
            + [str(summary["by_year"][str(year)]["quarterly_recovered_snapshots"])]
            for year in summary["source_years"]
        ],
    )


def close(actual, expected, label, tolerance=1e-6):
    """Reject an inconsistent recorded numerical claim."""
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, abs_tol=tolerance, rel_tol=0
    ):
        raise ValueError(f"{label}: {actual} != {expected}")


def write(name, lines):
    """Atomically replace generated files, including restored DVC hard links."""
    target = OUT / name
    temporary = target.with_name(f".{target.name}.tmp")
    temporary.write_text("\n".join(lines) + "\n")
    temporary.replace(target)


def save_figure(figure, name):
    """Render PGF without writing through a restored cache hard link."""
    target = OUT / name
    temporary = target.with_name(f".{target.stem}.tmp.pgf")
    figure.savefig(temporary)
    temporary.replace(target)


def tabular(name, columns, header, rows):
    """Let pandas own LaTeX table markup, including booktabs rules."""
    latex = pd.DataFrame(rows, columns=header).to_latex(
        index=False,
        escape=False,
        column_format=columns,
        multicolumn_format="c",
    )
    write(name, [latex.rstrip()])


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


def boolean(value):
    """Parse a recorded boolean without treating the string False as true."""
    if str(value).lower() not in ("true", "false"):
        raise ValueError(f"Invalid recorded boolean: {value}")
    return str(value).lower() == "true"


def optional_float(value):
    """CSV represents an undefined numerical diagnostic by an empty field."""
    return float(value) if value not in ("", None) else math.nan


def numerical_mean(rows, field):
    """Average only defined annual diagnostics."""
    values = [optional_float(row[field]) for row in rows]
    defined = [value for value in values if math.isfinite(value)]
    return mean(defined) if defined else math.nan


def diagnostic_mean(rows, field):
    """Display missing annual diagnostic means explicitly."""
    value = numerical_mean(rows, field)
    return f"{value:.3f}" if math.isfinite(value) else "---"


def validate_pcoa_energy(row):
    """Reconcile centered projection shares to saved annual energy totals."""
    rank, firms = int(row["rank"]), int(row["firms"])
    close(
        float(row["random_relative_expectation"]),
        rank / (firms - 1),
        "random subspace expectation",
    )
    for prefix, original in (
        ("raw", "raw_reconstruction_share"),
        ("residual", "residual_reconstruction_share"),
    ):
        total, relative, projected = (
            float(row[f"{prefix}_{name}_energy"])
            for name in ("total", "relative", "projected")
        )
        if not all(math.isfinite(v) and v >= 0 for v in (total, relative, projected)):
            raise ValueError("Invalid PCoA return-energy total")
        tolerance = 1e-10 * max(1, total)
        if projected > relative + tolerance or relative > total + tolerance:
            raise ValueError("PCoA projection exceeds available return energy")
        energy_defined = boolean(row[f"{prefix}_energy_defined"])
        relative_defined = boolean(row[f"{prefix}_relative_defined"])
        if energy_defined != (total > 0) or relative_defined != (
            relative > 1e-24 * total and energy_defined
        ):
            raise ValueError("Inconsistent PCoA energy denominator flags")
        for field, defined, expected in (
            (
                original,
                energy_defined,
                projected / total if energy_defined else math.nan,
            ),
            (
                f"{prefix}_relative_energy_share",
                energy_defined,
                relative / total if energy_defined else math.nan,
            ),
            (
                f"{prefix}_relative_reconstruction_share",
                relative_defined,
                projected / relative if relative_defined else math.nan,
            ),
        ):
            value = optional_float(row[field])
            if defined:
                if not -1e-8 <= value <= 1 + 1e-8:
                    raise ValueError(f"Invalid descriptive PCoA {field}")
                close(value, expected, f"PCoA energy identity {field}")
            elif not math.isnan(value):
                raise ValueError("Undefined PCoA energy ratio must remain missing")
        if relative_defined:
            close(
                float(row[original]),
                float(row[f"{prefix}_relative_reconstruction_share"])
                * float(row[f"{prefix}_relative_energy_share"]),
                "PCoA raw-relative energy identity",
            )
        reference = [
            optional_float(row[f"{prefix}_random_relative_{name}"])
            for name in ("mean", "lower", "upper")
        ]
        if relative_defined:
            if (
                any(not math.isfinite(v) or not 0 <= v <= 1 for v in reference)
                or reference[1] > reference[2]
            ):
                raise ValueError("Invalid random-subspace diagnostic distribution")
        elif any(not math.isnan(v) for v in reference):
            raise ValueError("Undefined random-subspace ratios must remain missing")


def validate_pcoa_cutoff(row, eigenvalues):
    """Separate numerical cutoff ties from the declared near-cutoff diagnostic."""
    rank, positive = int(row["rank"]), int(row["positive_rank"])
    applicable = 0 < rank < positive
    if boolean(row["cutoff_applicable"]) != applicable:
        raise ValueError("Inconsistent PCoA cutoff applicability")
    if applicable:
        retained, omitted = (
            float(eigenvalues[k]["eigenvalue"]) for k in (rank - 1, rank)
        )
        gap, relative_gap = retained - omitted, (retained - omitted) / retained
        close(float(row["cutoff_gap"]), gap, "PCoA cutoff gap")
        close(
            float(row["cutoff_relative_gap"]), relative_gap, "PCoA relative cutoff gap"
        )
        tied, near = gap <= float(row["tolerance"]), relative_gap <= 1e-3
    else:
        if any(
            not math.isnan(optional_float(row[field]))
            for field in ("cutoff_gap", "cutoff_relative_gap")
        ):
            raise ValueError("Untruncated PCoA spectrum has no cutoff gap")
        tied, near = False, False
    if boolean(row["cutoff_tied"]) != tied or boolean(row["cutoff_near_tied"]) != near:
        raise ValueError("Inconsistent PCoA cutoff tie diagnostic")
    if boolean(row["subspace_unique"]) != (not tied):
        raise ValueError("Numerically tied PCoA cutoff must be marked nonunique")


def validate_geometry_inventory(comparison, annual, summary, spectrum):
    """Require the full matched geometry grid and reconcile all saved summaries."""
    expected = {
        (approach, model, variance)
        for approach in GEOMETRY_APPROACHES
        for model in ("gram", "spatial")
        for variance in ("full", "correlation")
    }
    keys = [(r["approach"], r["model"], r["variance"]) for r in comparison]
    if len(set(keys)) != len(keys):
        raise ValueError("Duplicate geometry comparison procedure")
    if set(keys) != expected:
        raise ValueError("Incomplete geometry comparison inventory")
    annual_keys = [(r["column"], int(r["year"])) for r in annual]
    expected_annual = {
        ("|".join(key), year) for key in expected for year in range(2020, 2026)
    }
    if len(set(annual_keys)) != len(annual_keys) or set(annual_keys) != expected_annual:
        raise ValueError("Incomplete or duplicate geometry evaluation years")
    for row in comparison:
        key = "|".join(row[k] for k in ("approach", "model", "variance"))
        if row["column"] != key:
            raise ValueError("Inconsistent geometry column identifier")
        total = sum(
            float(select(annual, column=key, year=y)["score"])
            for y in range(2020, 2026)
        )
        close(float(row["heldout_log_likelihood"]), total, "geometry annual score")
        firm_days = float(row["firm_days"])
        if not math.isfinite(firm_days) or firm_days <= 0:
            raise ValueError("Invalid geometry firm-days")
        close(
            float(row["score_per_firm_day"]),
            total / firm_days,
            "geometry normalized score",
        )
        parameter = float(row["theta"] if row["model"] == "gram" else row["lambda"])
        if not math.isfinite(parameter):
            raise ValueError("Nonfinite geometry parameter")
        if row["model"] == "gram" and not 0 <= parameter <= 1 - 1e-6:
            raise ValueError("Invalid direct covariance parameter")
    summary_keys = [(r["approach"], int(r["year"])) for r in summary]
    expected_summary = {(a, y) for a in GEOMETRY_APPROACHES for y in range(2016, 2026)}
    if (
        len(set(summary_keys)) != len(summary_keys)
        or set(summary_keys) != expected_summary
    ):
        raise ValueError("Incomplete or duplicate PCoA summaries")
    spectrum_keys = [
        (r["approach"], int(r["year"]), int(r["component"])) for r in spectrum
    ]
    if len(set(spectrum_keys)) != len(spectrum_keys):
        raise ValueError("Duplicate PCoA eigenvalue")
    spectral_rows = dict(zip(spectrum_keys, spectrum, strict=True))
    expected_spectrum = set()
    for row in summary:
        approach, year = row["approach"], int(row["year"])
        firms, rank = int(row["firms"]), int(row["rank"])
        if int(row["requested_rank"]) != 5 or rank < 0 or rank > 5 or rank > firms - 1:
            raise ValueError("Invalid retained PCoA rank")
        if row["rank_shortfall"] not in (str(rank < 5), str(rank < 5).lower()):
            raise ValueError("Inconsistent PCoA rank shortfall")
        try:
            eigenvalues = [
                spectral_rows[(approach, year, k)] for k in range(1, firms + 1)
            ]
        except KeyError as error:
            raise ValueError("Incomplete PCoA spectrum inventory") from error
        expected_spectrum.update((approach, year, k) for k in range(1, firms + 1))
        if any(not math.isfinite(float(r["eigenvalue"])) for r in eigenvalues):
            raise ValueError("Nonfinite PCoA spectrum")
        tolerance = float(row["tolerance"])
        if any(float(r["eigenvalue"]) < -tolerance for r in eigenvalues):
            raise ValueError("Materially negative PCoA eigenvalue")
        positive_rank = sum(float(r["eigenvalue"]) > tolerance for r in eigenvalues)
        if int(row["positive_rank"]) != positive_rank or rank != min(5, positive_rank):
            raise ValueError("Inconsistent positive PCoA rank")
        share = sum(float(r["variance_share"]) for r in eigenvalues[:rank])
        close(float(row["variance_share"]), share, "PCoA retained variance")
        for field in ("variance_share",):
            value = float(row[field])
            if not math.isfinite(value) or not -1e-8 <= value <= 1 + 1e-8:
                raise ValueError(f"Invalid descriptive PCoA {field}")
        validate_pcoa_energy(row)
        validate_pcoa_cutoff(row, eigenvalues)
        gross = float(row["max_gross_weight"])
        if not math.isfinite(gross) or gross < 0:
            raise ValueError("Invalid PCoA gross portfolio weight")
    if set(spectrum_keys) != expected_spectrum:
        raise ValueError("Incomplete PCoA spectrum inventory")


def pcoa_decay(spectrum, approaches):
    """Average annual component shares, preserving equal weight for each year's fit."""
    indexed = {}
    for row in spectrum:
        if row["approach"] not in approaches:
            continue
        key = row["approach"], int(row["year"]), int(row["component"])
        if key in indexed:
            raise ValueError("Duplicate PCoA decay component")
        indexed[key] = row
    result = {}
    for approach in approaches:
        annual = []
        for year in range(2016, 2026):
            try:
                rows = [
                    indexed[approach, year, component] for component in range(1, 21)
                ]
            except KeyError as error:
                raise ValueError("Incomplete annual PCoA decay spectrum") from error
            shares = [float(row["variance_share"]) for row in rows]
            if any(not math.isfinite(value) or not 0 <= value <= 1 for value in shares):
                raise ValueError("Invalid PCoA decay share")
            if any(right > left + 1e-10 for left, right in pairwise(shares)):
                raise ValueError("Unordered PCoA decay spectrum")
            if sum(shares) > 1 + 1e-8:
                raise ValueError("Invalid cumulative PCoA decay share")
            for component, row in enumerate(rows, 1):
                close(
                    sum(shares[:component]),
                    float(row["cumulative_variance_share"]),
                    "PCoA cumulative decay share",
                )
            annual.append(shares)
        result[approach] = {
            "shares": [mean(values[k] for values in annual) for k in range(5)],
            "cumulative": {
                str(k): mean(sum(values[:k]) for values in annual)
                for k in (2, 3, 5, 10, 20)
            },
            "years": 10,
        }
    return result


def render_pcoa_decay(spectrum):
    """Component-by-component appendix tables and audited interpretation bindings."""
    native = {"fernandez_joint": "Joint characteristics"} | {
        f"histories__{name}": label for name, label in MODELS.items()
    }
    pretrained = ("tabpfn_full__late", "tabfm__late", "kumo__late", "limix__late")
    decoded = {f"histories@decoded__{name}": MODELS[name] for name in pretrained}
    values = pcoa_decay(spectrum, native | decoded)

    def percentage(value):
        return r"$>99.9$" if 0.999 < value < 1 - 1e-10 else f"{100 * value:.1f}"

    tabular(
        "pcoa-decay.tex",
        "lrrrrrrr",
        ["Native geometry", "PC1", "PC2", "PC3", "PC4", "PC5", "First 5", "First 10"],
        [
            [
                label,
                *[percentage(value) for value in values[approach]["shares"]],
                *[percentage(values[approach]["cumulative"][str(k)]) for k in (5, 10)],
            ]
            for approach, label in native.items()
        ],
    )
    tabular(
        "pcoa-decay-decoded.tex",
        "lrrrrr",
        ["Decoded geometry", "PC1", "PC2", "PC3", "PC4", "PC5"],
        [
            [label, *[percentage(value) for value in values[approach]["shares"]]]
            for approach, label in decoded.items()
        ],
    )
    native_values = [values[f"histories__{name}"] for name in pretrained]
    ranges = {
        f"Native{label}{extreme}": 100
        * function(item["cumulative"][str(k)] for item in native_values)
        for label, k in (("Two", 2), ("Five", 5))
        for extreme, function in (("Min", min), ("Max", max))
    }
    ranges.update(
        {
            f"Decoded{label}{extreme}": 100
            * function(values[name]["shares"][k] for name in decoded)
            for k, label in enumerate(("One", "Two", "Three", "Four", "Five"))
            for extreme, function in (("Min", min), ("Max", max))
        }
    )
    ranges.update(
        {
            "TabfmTwenty": 100 * values["histories__tabfm__late"]["cumulative"]["20"],
            "KumoTwenty": 100 * values["histories__kumo__late"]["cumulative"]["20"],
        }
    )
    CLAIMS["pcoa_decay"] = {
        "annual_fits": [2016, 2025],
        "averaging": "unweighted mean annual shares; no pooled eigendecomposition",
        "variance": "centered characteristic geometry",
        "approaches": values,
        "ranges_percent": ranges,
    }


def render_geometry(firm_days):
    """Render the complete direct-geometry comparison from recorded results."""
    comparison = read(f"{GEOMETRY}/comparison.csv")
    annual = read(f"{GEOMETRY}/annual-scores.csv")
    contrasts = read(f"{GEOMETRY}/contrasts.csv")
    summary = read(f"{GEOMETRY}/pcoa-summary.csv")
    spectrum = read(f"{GEOMETRY}/spectrum.csv")
    config = read(f"{GEOMETRY}/configuration.json")
    manifest = read(f"{GEOMETRY}/manifest.json")
    for name in (
        "daily-scores.parquet",
        "coordinates.parquet",
        "weights.parquet",
        "component-returns.parquet",
        "characteristic-associations.csv",
        "extremes.csv",
        "stability.csv",
        "component-covariance.csv",
    ):
        record(f"{GEOMETRY}/{name}")
    if (
        config["evaluation"] != [2020, 2025]
        or config["calibration"] != [2016, 2019]
        or config["encoder_support"] != 256
        or config["decoded_rank"] != 5
        or config["pcoa_rank"] != 5
        or config["pcoa_cutoff"]["near_tie_relative_tolerance"] != 1e-3
        or config["energy_diagnostics"]["relative_energy_tolerance"] != 1e-24
        or config["energy_diagnostics"]["random_subspace_draws"] != 199
        or config["energy_diagnostics"]["random_subspace_seed"] != 42
        or config["energy_diagnostics"]["random_subspace_quantiles"] != [0.025, 0.975]
    ):
        raise ValueError("Unexpected geometry windows")
    validate_geometry_inventory(comparison, annual, summary, spectrum)
    required = {
        path
        for path in SOURCES
        if path.startswith(GEOMETRY + "/") and not path.endswith("manifest.json")
    }
    if missing := required - manifest["sha256"].keys():
        raise ValueError(f"Incomplete geometry source manifest: {sorted(missing)}")
    for path in required:
        if SOURCES[path] != manifest["sha256"][path]:
            raise ValueError(
                f"Geometry artifact differs from recorded manifest: {path}"
            )
    protocol = f"{GEOMETRY}/README.md"
    record(protocol)
    if SOURCES[protocol] != manifest["protocol_sha256"]:
        raise ValueError("Geometry protocol differs from recorded manifest")
    for row in comparison:
        close(float(row["firm_days"]), firm_days, "geometry common firm-days")
    contrast_pairs = [(r["left"], r["right"]) for r in contrasts]
    if len(set(contrast_pairs)) != len(contrast_pairs):
        raise ValueError("Duplicate geometry contrast")
    for row in contrasts:
        total = 0
        for year in range(2020, 2026):
            difference = float(
                select(annual, column=row["left"], year=year)["score"]
            ) - float(select(annual, column=row["right"], year=year)["score"])
            close(float(row[f"year_{year}"]), difference, "geometry annual contrast")
            total += difference
        close(float(row["difference"]), total, "geometry paired contrast")
        for block in (21, 63):
            lower, upper = float(row[f"lower_{block}"]), float(row[f"upper_{block}"])
            if not (math.isfinite(lower) and math.isfinite(upper) and lower <= upper):
                raise ValueError("Invalid geometry contrast interval")
    rows, full_rows, interval_rows, pcoa_rows, energy_rows, cutoff_rows = (
        [],
        [],
        [],
        [],
        [],
        [],
    )
    principal = {"fernandez_joint": "Joint characteristics"} | {
        f"histories__{name}": label for name, label in MODELS.items()
    }
    for approach, label in GEOMETRY_APPROACHES.items():
        differences = {}
        for variance in ("full", "correlation"):
            gram = f"{approach}|gram|{variance}"
            spatial = f"{approach}|spatial|{variance}"
            contrast = select(contrasts, left=gram, right=spatial)
            differences[variance] = contrast
            interval_rows.append(
                [
                    label,
                    "Full" if variance == "full" else "Marginal",
                    f"{float(contrast['difference']):+,.1f}",
                    *[
                        f"[{float(contrast[f'lower_{b}']):+,.1f}, {float(contrast[f'upper_{b}']):+,.1f}]"
                        for b in (21, 63)
                    ],
                ]
            )
        scores = [
            float(
                select(comparison, approach=approach, model=m, variance=v)[
                    "heldout_log_likelihood"
                ]
            )
            for v in ("full", "correlation")
            for m in ("gram", "spatial")
        ]
        full_rows.append([label, *[f"{v:,.1f}" for v in scores]])
        selected = [
            select(summary, approach=approach, year=y) for y in range(2016, 2026)
        ]
        ranks = [int(r["rank"]) for r in selected]
        pcoa_rows.append(
            [
                label,
                f"{min(ranks)}--{max(ranks)}",
                *[
                    diagnostic_mean(selected, field)
                    for field in (
                        "variance_share",
                        "raw_reconstruction_share",
                        "residual_reconstruction_share",
                    )
                ],
                "/".join(
                    str(sum(boolean(r[f"{prefix}_energy_defined"]) for r in selected))
                    for prefix in ("raw", "residual")
                ),
                f"{max(float(r['max_gross_weight']) for r in selected):.2f}",
            ]
        )
        energy_rows.append(
            [
                label,
                diagnostic_mean(selected, "raw_relative_energy_share"),
                diagnostic_mean(selected, "raw_relative_reconstruction_share"),
                diagnostic_mean(selected, "raw_random_relative_mean"),
                f"[{diagnostic_mean(selected, 'raw_random_relative_lower')}, {diagnostic_mean(selected, 'raw_random_relative_upper')}]",
                str(sum(boolean(r["raw_relative_defined"]) for r in selected)),
            ]
        )
        truncated = [r for r in selected if boolean(r["cutoff_applicable"])]
        cutoff_rows.append(
            [
                label,
                len(truncated),
                f"{min(float(r['cutoff_gap']) for r in truncated):.3g}"
                if truncated
                else "---",
                f"{min(float(r['cutoff_relative_gap']) for r in truncated):.3g}"
                if truncated
                else "---",
                sum(boolean(r["cutoff_tied"]) for r in selected),
                sum(
                    boolean(r["cutoff_near_tied"]) and not boolean(r["cutoff_tied"])
                    for r in selected
                ),
            ]
        )
        if approach in principal:
            values = []
            for candidate in (
                approach,
                approach.replace("histories__", "histories@decoded__")
                if approach.startswith("histories__")
                else None,
            ):
                if candidate is None:
                    values.extend(["---", "---"])
                    continue
                contrast = select(
                    contrasts,
                    left=f"{candidate}|gram|correlation",
                    right=f"{candidate}|spatial|correlation",
                )
                values.extend(
                    [
                        f"{float(contrast['difference']):+,.1f}",
                        f"[{float(contrast['lower_21']):+,.1f}, {float(contrast['upper_21']):+,.1f}]",
                    ]
                )
            rows.append([principal[approach], *values])
    tabular(
        "geometry-main.tex",
        "lrlrl",
        ["Geometry", "Native", "21-date interval", "Decoded", "21-date interval"],
        rows,
    )
    tabular(
        "geometry-scores.tex",
        "lrrrr",
        [
            "Geometry",
            "Gram: full",
            "Spatial: full",
            "Gram: marginal",
            "Spatial: marginal",
        ],
        full_rows,
    )
    for variance, label in (("full", "Full"), ("correlation", "Marginal")):
        tabular(
            f"geometry-contrasts-{variance}.tex",
            "lrll",
            ["Geometry", "Difference", "21-date interval", "63-date interval"],
            [[r[0], *r[2:]] for r in interval_rows if r[1] == label],
        )
    tabular(
        "pcoa-summary.tex",
        "lrrrrrr",
        [
            "Geometry",
            "Rank range",
            "Geometry share",
            r"$q_{\rm raw}$",
            r"$q_{\rm residual}$",
            "Valid R/E",
            "Max. gross",
        ],
        pcoa_rows,
    )
    tabular(
        "pcoa-energy.tex",
        "lrrrrr",
        [
            "Geometry",
            r"$e_{\rm relative}$",
            r"$q_{\rm relative}$",
            "Random mean",
            "Random reference range",
            "Years",
        ],
        energy_rows,
    )
    tabular(
        "pcoa-cutoff.tex",
        "lrrrrr",
        [
            "Geometry",
            "Truncated years",
            "Min. gap",
            "Min. rel. gap",
            "Nonunique",
            "Near only",
        ],
        cutoff_rows,
    )
    fig, ax = plt.subplots(figsize=(6.5, 3.5), layout="constrained")
    for approach, label in principal.items():
        values = [
            select(spectrum, approach=approach, year=2025, component=k)
            for k in range(1, 11)
        ]
        ax.plot(
            range(1, 11),
            [float(r["variance_share"]) for r in values],
            marker="o",
            markersize=3,
            linewidth=1,
            label=label,
        )
    ax.set(
        xlabel="Principal coordinate",
        ylabel="Share of centered geometry",
        xticks=range(1, 11),
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(ncol=2, frameon=False, fontsize=8)
    save_figure(fig, "geometry-scree.pgf")
    plt.close(fig)
    render_pcoa_decay(spectrum)
    CLAIMS["geometry"] = {
        "procedures": len(comparison),
        "approaches": len(GEOMETRY_APPROACHES),
        "pcoa_summaries": len(summary),
        "scree_year": 2025,
        "pcoa_cutoff_ties": sum(boolean(row["cutoff_tied"]) for row in summary),
        "pcoa_cutoff_near": sum(boolean(row["cutoff_near_tied"]) for row in summary),
        "pcoa_native_above_random": sum(
            numerical_mean(
                [row for row in summary if row["approach"] == f"histories__{model}"],
                "raw_relative_reconstruction_share",
            )
            > numerical_mean(
                [row for row in summary if row["approach"] == f"histories__{model}"],
                "raw_random_relative_mean",
            )
            for model in MODELS
        ),
        "pcoa_native_principal_count": len(MODELS),
        "energy_reporting": "unweighted annual means over defined ratios; random bands are mean annual quantiles, not confidence intervals",
        "common_marginal_negative": sum(
            float(
                select(
                    contrasts,
                    left=f"{approach}|gram|correlation",
                    right=f"{approach}|spatial|correlation",
                )["difference"]
            )
            < 0
            for approach in GEOMETRY_APPROACHES
        ),
        "same_geometry_contrasts": [
            r
            for r in contrasts
            if r["left"].replace("|gram|", "|spatial|") == r["right"]
        ],
    }


def validate_replication_sensitivity(rows, cohorts):
    """Reject missing timing/software cells or comparisons that change firms."""
    expected = set()
    for timing in ("shifted", "contemporaneous"):
        for backend in ("robustbase", "robust"):
            for sample in ("natural", "intersection"):
                for table in ("common_four", "common_three"):
                    expected.add((timing, backend, sample, table, "nonspatial", "ols"))
                    networks = set(CHARACTERISTICS)
                    if table == "common_four":
                        networks.add("fernandez_debt_maturity")
                    for network in networks:
                        for estimator in ("spatial_lag_iv", "spatial_error_ml"):
                            expected.add(
                                (timing, backend, sample, table, network, estimator)
                            )
    fields = ("timing", "backend", "sample", "table", "network", "estimator")
    keys = [tuple(r[k] for k in fields) for r in rows]
    if len(set(keys)) != len(keys) or set(keys) != expected:
        raise ValueError("Incomplete or duplicate replication sensitivity inventory")
    for row in rows:
        timing, sample, table = row["timing"], row["sample"], row["table"]
        cohort = cohorts[timing][f"{table}|{sample}"]
        tickers = cohort["tickers"]
        if cohort["firms"] != len(tickers) or len(set(tickers)) != len(tickers):
            raise ValueError("Invalid replication sensitivity cohort")
        close(float(row["firms"]), len(tickers), "sensitivity cohort size")
        expected_id = (
            f"{table}:intersection"
            if sample == "intersection"
            else f"{table}:{timing}:natural"
        )
        if row["sample_id"] != expected_id or row["self_links"] != "False":
            raise ValueError("Inconsistent replication sensitivity identity")
        start, end = (2016, 2025) if timing == "shifted" else (2015, 2024)
        if (
            row["return_start"] != f"{start}-01-01"
            or row["return_end"] != f"{end}-12-31"
            or int(row["characteristic_start"]) != 2015
            or int(row["characteristic_end"]) != 2024
        ):
            raise ValueError("Unexpected replication sensitivity windows")
        for field in (
            "premium_market",
            "se_market",
            "intensity",
            "intensity_se",
            "pseudo_r2_structural",
            "pseudo_r2_reduced",
        ):
            if not math.isfinite(float(row[field])):
                raise ValueError(f"Nonfinite replication sensitivity {field}")
    for table in ("common_four", "common_three"):
        left = cohorts["shifted"][f"{table}|intersection"]["tickers"]
        right = cohorts["contemporaneous"][f"{table}|intersection"]["tickers"]
        if left != right:
            raise ValueError("Replication timing comparison changes firms")


def render_replication_sensitivity(primary):
    """Render timing and software contrasts while preserving primary estimates."""
    root = "research/replication"
    rows = read(f"{root}/sensitivity-estimates.csv")
    cohorts = read(f"{root}/sensitivity-cohorts.json")
    runtime = read(f"{root}/sensitivity-mm-runtime.json")
    contrasts = read(f"{root}/sensitivity-contrasts.csv")
    for name in ("sensitivity-quarterly-returns.csv", "sensitivity-mm-betas.csv"):
        record(f"{root}/{name}")
    validate_replication_sensitivity(rows, cohorts)
    if set(runtime) != {
        f"{t}|{b}"
        for t in ("shifted", "contemporaneous")
        for b in ("robustbase", "robust")
    }:
        raise ValueError("Incomplete MM software runtime records")
    for row in rows:
        if (
            row["timing"] == "shifted"
            and row["backend"] == "robustbase"
            and row["sample"] == "natural"
        ):
            baseline = select(
                primary,
                **{k: row[k] for k in ("table", "network", "estimator", "self_links")},
            )
            for field in (
                "premium_market",
                "se_market",
                "intensity",
                "intensity_se",
                "pseudo_r2_structural",
                "pseudo_r2_reduced",
            ):
                close(
                    float(row[field]),
                    float(baseline[field]),
                    f"preserved primary {field}",
                )
    for row in contrasts:
        identity = {
            k: row[k] for k in ("table", "sample", "sample_id", "network", "estimator")
        }
        left = select(
            rows, **identity, timing=row["left_timing"], backend=row["left_backend"]
        )
        right = select(
            rows, **identity, timing=row["right_timing"], backend=row["right_backend"]
        )
        for field in (
            "premium_market",
            "intensity",
            "pseudo_r2_structural",
            "pseudo_r2_reduced",
        ):
            close(
                float(row[f"delta_{field}"]),
                float(right[field]) - float(left[field]),
                "matched replication contrast",
            )
    table_rows, cohort_rows = [], []
    for table, label in (
        ("common_four", "Four characteristics"),
        ("common_three", "Three characteristics"),
    ):
        for timing in ("shifted", "contemporaneous"):
            cohort_rows.append(
                [
                    label,
                    timing.title(),
                    cohorts[timing][f"{table}|natural"]["firms"],
                    cohorts[timing][f"{table}|intersection"]["firms"],
                ]
            )
            for backend in ("robustbase", "robust"):
                identity = {
                    "table": table,
                    "sample": "intersection",
                    "timing": timing,
                    "backend": backend,
                }
                ols = select(rows, **identity, network="nonspatial", estimator="ols")
                sem = select(
                    rows,
                    **identity,
                    network="fernandez_joint",
                    estimator="spatial_error_ml",
                )
                table_rows.append(
                    [
                        "Four" if table == "common_four" else "Three",
                        timing.title(),
                        backend,
                        ols["firms"],
                        f"{100 * float(ols['premium_market']):.2f} ({100 * float(ols['se_market']):.2f})",
                        f"{100 * float(sem['premium_market']):.2f} ({100 * float(sem['se_market']):.2f})",
                        f"{float(sem['intensity']):.3f}",
                    ]
                )
    tabular(
        "replication-sensitivity.tex",
        "lllrrrr",
        [
            "Histories",
            "Returns",
            "MM package",
            "$N$",
            "OLS slope (SE)",
            "Joint SEM slope (SE)",
            r"$\lambda$",
        ],
        table_rows,
    )
    tabular(
        "replication-sensitivity-cohorts.tex",
        "llrr",
        ["Histories", "Returns", "Eligible", "Intersection"],
        cohort_rows,
    )
    diagnostic_rows = []
    for network, label in CHARACTERISTICS.items():
        row = select(
            primary,
            table="common_four",
            network=network,
            estimator="spatial_error_ml",
            self_links="False",
        )
        diagnostic_rows.append(
            [
                label,
                f"{float(row['ols_moran']):.4f}",
                f"{float(row['ols_moran_z']):.3f}",
                f"{float(row['pseudo_r2_structural']):.3f}",
                f"{float(row['pseudo_r2_reduced']):.3f}",
            ]
        )
    debt = select(
        primary,
        table="common_four",
        network="fernandez_debt_maturity",
        estimator="spatial_error_ml",
        self_links="False",
    )
    diagnostic_rows.insert(
        -1,
        [
            "Debt maturity",
            f"{float(debt['ols_moran']):.4f}",
            f"{float(debt['ols_moran_z']):.3f}",
            f"{float(debt['pseudo_r2_structural']):.3f}",
            f"{float(debt['pseudo_r2_reduced']):.3f}",
        ],
    )
    tabular(
        "replication-diagnostics.tex",
        "lrrrr",
        [
            "Network",
            r"Raw Moran $I$",
            r"Moran $z$",
            r"Conditional fit $R^2$",
            r"Mean fit $R^2$",
        ],
        diagnostic_rows,
    )
    CLAIMS["replication_sensitivity"] = {
        "cells": len(rows),
        "contrasts": len(contrasts),
        "cohorts": cohorts,
        "displayed_rows": table_rows,
    }


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
    replication_cohorts = read("research/replication/cohorts.json")
    CLAIMS["replication_cohorts"] = replication_cohort_counts(replication_cohorts, r0)
    estimates = [row for row in r0 if row["table"] == "common_four"]
    bootstrap = read("research/replication/bootstrap.csv")
    read("research/replication/audit.json")
    mcs = read(f"{PANEL}/mcs.csv")
    if config["evaluation"] != [2020, 2025] or config["calibration"] != [2016, 2019]:
        raise ValueError("Unexpected panel windows")
    samples = [
        read(f"{PANEL}/observations/{year}-sample.json") for year in range(2016, 2026)
    ]
    render_source_recovery(read("research/panel/source-recovery.json"), samples)
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
        close(
            float(r["firms"]),
            CLAIMS["replication_cohorts"]["common_four"],
            "replication cohort",
        )
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
    render_replication_premiums(r0, bootstrap, replication_cohorts)

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
    save_figure(fig, "support.pgf")
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
    render_geometry(firm_days)
    render_replication_sensitivity(r0)
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
    write("numbers.tex", [env.get_template("numbers.tex.j2").render(**values).rstrip()])
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
            "replication": (
                f"four, {CLAIMS['replication_cohorts']['common_four']} firms, "
                "CAPM, zero diagonal, exp, SEM-ML; nonspatial OLS"
            ),
            "replication_sensitivity": "both timing windows x both MM packages x both cohorts x natural/intersection; main table uses intersection",
            "geometry": "31 geometries x gram/spatial x full/correlation; all saved annual totals and paired intervals reconciled",
            "pcoa": "rank at most 5; annual 2016-2025 descriptive means; scree fixed to native geometries in 2025",
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
