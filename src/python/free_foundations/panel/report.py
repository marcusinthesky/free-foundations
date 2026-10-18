"""Report each panel design without selecting a test-period winner."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.panel.characteristics import ROOT, audit_disclosures
from free_foundations.panel.decoding import FACTORS
from free_foundations.panel.design import DESIGNS, FOCUSED
from free_foundations.pilot.data import write_json

# v1 names of unchanged approaches in the original `research/panel` run.
V1_MODELS = {
    "tabpfn_fast": "tabpfn_fast__late",
    "tabpfn_full": "tabpfn_full__late",
    "tabfm": "tabfm__late",
    "exaone": "exaone__late",
}


def audit_checkpoints() -> dict[str, dict[str, object]]:
    """Verify pinned local weights and record the fast checkpoint's observed hash."""
    records: dict[str, dict[str, object]] = {}
    for path in sorted(Path("research/expanded/cache/models").glob("*/provenance.json")):
        metadata = json.loads(path.read_text())
        for name, expected in metadata["sha256"].items():
            with (path.parent / name).open("rb") as stream:
                observed = hashlib.file_digest(stream, "sha256").hexdigest()
            if observed != expected:
                message = f"Checkpoint hash differs from pinned provenance: {path.parent / name}"
                raise ValueError(message)
        records[path.parent.name] = metadata
    metadata = json.loads(Path("research/pilot/cache/checkpoint.json").read_text())
    with Path(metadata["path"]).open("rb") as stream:
        metadata["observed_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    records["tabpfn_fast"] = metadata
    return records


def v1_name(name: str) -> str | None:
    """Map a v1 approach to its explicitly named successor in the `four` design."""
    if name == "fernandez_joint_four":
        return "fernandez_joint"
    if name.startswith("fernandez_"):
        return name
    if name == "ff5_mom_spherical":
        return "zero_network"
    if name == "uniform_network":
        return name
    rung, _, method = name.partition("__")
    if rung in {"four", "broad", "metrics"}:
        return f"{'histories' if rung == 'four' else rung}__{V1_MODELS.get(method, method)}"
    return None


def regression_check(comparison: pd.DataFrame) -> pd.DataFrame:
    """The refactored exp-kernel spherical arm must reproduce the original panel scores."""
    original = pd.read_csv(ROOT / "comparison.csv")
    current = comparison.loc[
        comparison["innovation"].eq("spherical") & comparison["kernel"].isin(["exp", "none"])
    ].set_index("approach")
    rows = []
    heldout = current["heldout_log_likelihood"].to_dict()
    intensities = current["lambda"].to_dict()
    for approach, before, intensity in zip(
        original["approach"].astype(str),
        original["heldout_log_likelihood"].to_numpy(dtype=float),
        original["lambda"].to_numpy(dtype=float),
        strict=True,
    ):
        name = v1_name(approach)
        if name is None or name not in heldout:
            continue
        new = float(heldout[name])
        rows.append(
            {
                "v1_approach": approach,
                "approach": name,
                "v1_heldout": before,
                "heldout": new,
                "difference": new - before,
                "v1_lambda": intensity,
                "lambda": float(intensities[name]),
            }
        )
    return pd.DataFrame(rows)


def ladder_table(comparison: pd.DataFrame) -> list[str]:
    """Gains over the joint benchmark for every network, by kernel and innovation arm."""
    arms = [
        ("exp", "spherical"),
        ("exp", "diagonal"),
        ("median", "diagonal"),
        ("matched", "diagonal"),
        ("exp", "correlation"),
    ]
    networks = comparison.loc[~comparison["innovation"].eq("control")]
    names = list(dict.fromkeys(networks["approach"]))
    header = "| Approach | Arm | " + " | ".join(f"{k}/{i}" for k, i in arms) + " |"
    lines = [header, "| --- | --- |" + " ---: |" * len(arms)]
    indexed = networks.set_index(["approach", "kernel", "innovation"])
    for name in names:
        cells = []
        for kernel, innovation in arms:
            key = (
                name,
                "none" if name in {"uniform_network", "zero_network"} else kernel,
                innovation,
            )
            cells.append(
                f"{indexed.loc[key, 'gain_vs_joint_exp']:+,.2f}" if key in indexed.index else "—"
            )
        arm = networks.loc[networks["approach"].eq(name), "arm"].iloc[0]
        lines.append(f"| `{name}` | {arm} | " + " | ".join(cells) + " |")
    return lines


def control_table(comparison: pd.DataFrame) -> list[str]:
    """Nonspatial covariance controls, each joined one-to-one to its correlation-only row."""
    keys = ["approach", "kernel"]
    controls = comparison.loc[comparison["innovation"].eq("control")]
    correlation = comparison.loc[
        comparison["innovation"].eq("correlation"), [*keys, "heldout_log_likelihood"]
    ]
    joined = controls.merge(
        correlation, on=keys, suffixes=("", "_correlation"), validate="one_to_one"
    )
    lines = ["| Control | Held-out log-likelihood | Correlation-only |", "| --- | ---: | ---: |"]
    lines += [
        f"| `{row['approach']}` | {row['heldout_log_likelihood']:,.2f} | "
        f"{row['heldout_log_likelihood_correlation']:,.2f} |"
        for row in joined.to_dict("records")
    ]
    return lines


def contrast_table(contrasts: pd.DataFrame) -> list[str]:
    """Declared matched-input contrasts with paired intervals and yearly totals."""
    years = [column for column in contrasts.columns if column.startswith("year_")]
    lines = [
        "",
        "## Declared paired contrasts",
        "",
        "Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals",
        "(21-day expected blocks). The intervals resample realized daily differences and hold",
        "the fitted coefficients, networks and searched specifications fixed.",
        "",
        "| Contrast | Left | Right | Arm | Difference | 21-day interval | "
        + " | ".join(y.removeprefix("year_") for y in years)
        + " |",
        "| --- | --- | --- | --- | ---: | ---: |" + " ---: |" * len(years),
    ]
    for row in contrasts.to_dict("records"):
        left, kernel, innovation = str(row["left"]).split("|")
        lines.append(
            f"| {row['contrast']} | `{left}` | `{str(row['right']).split('|')[0]}` | "
            f"{kernel}/{innovation} | {row['difference']:+,.1f} | "
            f"[{row['lower_21']:+,.1f}, {row['upper_21']:+,.1f}] | "
            + " | ".join(f"{row[y]:+,.0f}" for y in years)
            + " |"
        )
    return lines


# Rows shown in the attribution table, when scored in a design.
ATTRIBUTED = (
    "fernandez_joint",
    "covariance_exposures",
    "reference_exposures",
    "histories__direct",
    "histories__supervised_mlp16",
    "histories__tabfm__early_concat",
    "histories__tabfm__early_concat_labelnull",
    "histories__tabpfn_full__late",
    "histories__exaone__late",
    "histories@decoded__direct",
    "histories@decoded__tabfm__early_concat",
)
PARTS = (
    "spectrum",
    "variance",
    "baseline",
    "alignment",
    "concentration_own",
    "concentration_cross",
)
MEASURED_ROWS = {
    "native": "histories__{}",
    "redraw 1": "histories@redraw1__{}",
    "redraw 2": "histories@redraw2__{}",
    "shared cap/assets": "histories@shared_market_cap_assets__{}",
    "shared income/assets": "histories@shared_income_assets__{}",
    "both shared": "histories@shared_both__{}",
    "decoded": "histories@decoded__{}",
}


def attribution_table(attribution: pd.DataFrame, geometry: pd.DataFrame) -> list[str]:
    """Held-out residual log-likelihood parts relative to the uniform network."""
    held = attribution.loc[attribution["year"] >= 2020]
    lines = [
        "",
        "## Where the residual likelihood comes from",
        "",
        "Exact split of the held-out spatial-error log-likelihood of factor residuals,",
        "conditional on realized factors, at the frozen coefficient and prior-window",
        "variances (Lean `Likelihood.spatial_loss`), summed over 2020-2025, minus the uniform",
        "network's parts. `alignment` is the term linear in lambda (weighted cross products",
        "of a firm's and its neighbours' residuals); the two `concentration` terms are",
        "quadratic, split into the neighbours' own second moments weighted by squared",
        "weights and their cross products. Those second moments hold common and",
        "idiosyncratic variance together, so `concentration_own` is not a pure noise cost,",
        "and a larger `alignment` is not by itself evidence of recovered exposures. This",
        "split does not decompose the headline unconditional scores, which add factor",
        "uncertainty around the prior mean. `H` is the mean row Herfindahl index.",
        "",
    ]
    for kernel, innovation in (("exp", "diagonal"), ("matched", "diagonal")):
        arm = held.loc[held["innovation"].eq(innovation)]
        totals = arm.groupby(["approach", "kernel"])[list(PARTS)].sum()
        if ("uniform_network", "none") not in set(totals.index):
            continue
        values = {
            key: dict(zip(PARTS, row, strict=True))
            for key, row in zip(totals.index, totals.to_numpy(dtype=float), strict=True)
        }
        base = values[("uniform_network", "none")]
        herfindahl = (
            geometry.loc[geometry["year"] >= 2020]
            .groupby(["approach", "kernel"])["mean_herfindahl"]
            .mean()
        )
        lines += [
            f"### {kernel} kernel, {innovation} innovations",
            "",
            "| Approach | lambda | " + " | ".join(PARTS) + " | Total | H |",
            "| --- | ---: |" + " ---: |" * (len(PARTS) + 2),
        ]
        rows = [("uniform_network", "none"), *((n, kernel) for n in ATTRIBUTED)]
        for approach, row_kernel in rows:
            if (approach, row_kernel) not in values:
                continue
            parts = values[approach, row_kernel]
            shown = {
                part: parts[part] - (0.0 if approach == "uniform_network" else base[part])
                for part in PARTS
            }
            selected = arm["approach"].eq(approach) & arm["kernel"].eq(row_kernel)
            intensity = float(arm.loc[selected, "lambda"].iloc[0])
            lines.append(
                f"| `{approach}` | {intensity:.3f} | "
                + " | ".join(f"{shown[part]:+,.0f}" for part in PARTS)
                + f" | {sum(shown.values()):+,.0f} | "
                + f"{float(herfindahl.get((approach, row_kernel), np.nan)):.4f} |"
            )
        lines.append("")
    lines.append("The uniform row shows its own parts; every other row is its difference from it.")
    return lines


def ceiling(audit: pd.DataFrame, rank: int = FACTORS) -> tuple[float, float]:
    """Mean reliability of the reference target: the R^2 and distance-Spearman ceilings."""
    rows = audit.loc[audit["target"].eq("reference") & audit["rank"].eq(rank)]
    return float(rows["spearman_brown"].mean()), float(rows["distance_reliability"].mean())


def target_table(audit: pd.DataFrame, quality: pd.DataFrame) -> list[str]:
    """Reliability of both calibration targets, and decoder quality across ranks."""
    summary = audit.groupby(["target", "rank"], sort=False)[
        [
            "half_correlation",
            "spearman_brown",
            "distance_reliability",
            "commonality_mean",
            "effective_firm_fraction",
        ]
    ].mean()
    firms = audit["reference_firms"]
    lines = [
        "",
        "## Calibration targets",
        "",
        "`reference` is each cohort firm's OLS loadings on the leading principal components",
        "of standardized prior factor residuals of firms outside the cohort",
        f"({firms.min()}-{firms.max()} a year); a held-out firm's returns never reach another",
        "firm's target. `covariance` is the earlier in-panel construction, the rank-k",
        "coordinates of the cohort's own residual covariance, kept as a control. Means over",
        "years. Halves split the prior window; the reference halves share the full-window",
        "factor series, so the Spearman-Brown value estimates the reliability of the",
        "full-window target and bounds any decoder's R^2 against it. In-panel coordinates",
        "rotate between halves, so only their distances are compared. Commonality is the",
        "share of each firm's residual variance the target explains; the effective firm",
        "fraction is (1 / sum p_i^2) / N for p_i a firm's share of the target's squared",
        "mass, low when a few firms hold it, as for a diagonal covariance.",
        "",
        (
            "| Target | Rank | Half-window correlation | Spearman-Brown | Distance reliability "
            "| Commonality | Effective firm fraction |"
        ),
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in summary.reset_index().to_dict("records"):
        cells = [
            f"{row[column]:.3f}" if np.isfinite(row[column]) else "—" for column in summary.columns
        ]
        lines.append(f"| {row['target']} | {row['rank']} | " + " | ".join(cells) + " |")
    primary = quality.loc[quality["rung"].eq("histories")]
    by_rank = primary.pivot_table(
        index="representation", columns="rank", values="decoder_r2", aggfunc="mean", sort=False
    )
    lines += [
        "",
        "Mean out-of-fold decoder R^2 against the reference target at each rank (history",
        "rung); networks use rank 5 only.",
        "",
        "| Representation | " + " | ".join(f"Rank {rank}" for rank in by_rank.columns) + " |",
        "| --- |" + " ---: |" * len(by_rank.columns),
        *[
            f"| `{rep}` | " + " | ".join(f"{value:.3f}" for value in row) + " |"
            for rep, row in by_rank.iterrows()
        ],
    ]
    return lines


def support_table(
    comparison: pd.DataFrame, quality: pd.DataFrame, audit: pd.DataFrame, sizes: tuple[int, ...]
) -> list[str]:
    """Native and decoded gains, and decoder quality, at each nested support size."""
    gains = comparison.set_index(["approach", "kernel", "innovation"])["gain_vs_joint_exp"]
    rungs = {rows: f"histories@support{rows}" for rows in sizes} | {256: "histories"}
    names = [name for name in FOCUSED if name != "direct"]
    r2_ceiling, rho_ceiling = ceiling(audit)
    primary = quality.loc[quality["rank"].eq(FACTORS)]
    lines = [
        "",
        "## Support size",
        "",
        "Every row re-encodes the same query firms on a nested prefix of the 256-row support.",
        "Query-only rows (`direct`) do not depend on the support and appear once. Gains are",
        "over the joint network (exp kernel), matched kernel with diagonal innovations, the",
        "arm declared before this design ran.",
        "",
    ]
    for title, pattern in (("Native", "{}__{}"), ("Decoded", "{}@decoded__{}")):
        lines += [
            f"### {title} distance",
            "",
            "| Representation | " + " | ".join(f"{rows} rows" for rows in sorted(rungs)) + " |",
            "| --- |" + " ---: |" * len(rungs),
        ]
        for name in ("direct", *names):
            cells = []
            for rows in sorted(rungs):
                rung = "histories" if name == "direct" else rungs[rows]
                key = (pattern.format(rung, name), "matched", "diagonal")
                cells.append(f"{gains[key]:+,.1f}" if key in gains.index else "—")
            lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
        lines.append("")
    lines += [
        "### Decoder quality",
        "",
        f"Mean out-of-fold R^2 (median in brackets) against the rank-{FACTORS} reference",
        f"target. The target's own reliability bounds R^2 near {r2_ceiling:.2f} and distance",
        f"Spearman near {rho_ceiling:.2f}.",
        "",
        "| Representation | " + " | ".join(f"{rows} rows" for rows in sorted(rungs)) + " |",
        "| --- |" + " ---: |" * len(rungs),
    ]
    for name in ("direct", *names):
        cells = []
        for rows in sorted(rungs):
            rung = "histories" if name == "direct" else rungs[rows]
            fit = primary.loc[primary["rung"].eq(rung) & primary["representation"].eq(name)]
            values = fit["decoder_r2"]
            cells.append(f"{values.mean():.3f} [{values.median():.3f}]" if len(values) else "—")
        lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
    return lines


def measurement_table(
    comparison: pd.DataFrame, quality: pd.DataFrame, audit: pd.DataFrame
) -> list[str]:
    """One readout per family under each measurement variant, and decoder quality."""
    from free_foundations.panel.inference import MEASURED  # noqa: PLC0415

    gains = comparison.set_index(["approach", "kernel", "innovation"])["gain_vs_joint_exp"]
    lines = [
        "",
        "## Measurement variants",
        "",
        "Held-out gains over the joint network (exp kernel) for the history rung: the native",
        "readout, two re-encodings on differently salted 256-row supports, the two support",
        "targets on shared rows and their combination (RMS of the two distances), and",
        "networks built from reference-factor exposures decoded out of the same states",
        "(see `decoding.py`).",
        "",
    ]
    for kernel, innovation in (("exp", "diagonal"), ("matched", "diagonal")):
        lines += [
            f"### {kernel} kernel, {innovation} innovations",
            "",
            "| Representation | " + " | ".join(MEASURED_ROWS) + " |",
            "| --- |" + " ---: |" * len(MEASURED_ROWS),
        ]
        for name in ("direct", *MEASURED):
            cells = []
            for pattern in MEASURED_ROWS.values():
                key = (pattern.format(name), kernel, innovation)
                cells.append(f"{gains[key]:+,.1f}" if key in gains.index else "—")
            lines.append(f"| `{name}` | " + " | ".join(cells) + " |")
        lines.append("")
    primary = quality.loc[quality["rung"].eq("histories") & quality["rank"].eq(FACTORS)]
    if not primary.empty:
        summary = primary.groupby("representation", sort=False).agg(
            decoder_r2=("decoder_r2", "mean"),
            median_r2=("decoder_r2", "median"),
            exposure_distance_spearman=("exposure_distance_spearman", "mean"),
        )
        r2_ceiling, rho_ceiling = ceiling(audit)
        lines += [
            f"Decoders: out-of-fold R^2 of the rank-{FACTORS} reference exposures (mean over",
            "years, median in brackets), and the Spearman correlation between decoded and",
            f"target distances. The target's reliability bounds R^2 near {r2_ceiling:.2f}",
            f"and distance Spearman near {rho_ceiling:.2f}; see Calibration targets.",
            "",
            "| Representation | Out-of-fold R^2 | Distance Spearman |",
            "| --- | ---: | ---: |",
            *[
                f"| `{row['representation']}` | {row['decoder_r2']:.3f} "
                f"[{row['median_r2']:.3f}] | {row['exposure_distance_spearman']:.3f} |"
                for row in summary.reset_index().to_dict("records")
            ],
        ]
    return lines


def results(name: str) -> None:
    """Write one design's RESULTS.md from its saved machine-readable tables."""
    design = DESIGNS[name]
    output = design.output
    comparison = pd.read_csv(output / "comparison.csv")
    bootstrap = pd.read_csv(output / "bootstrap.csv")
    mcs = pd.read_csv(output / "mcs.csv")
    placebo = pd.read_csv(output / "placebo.csv")
    geometry = pd.read_csv(output / "geometry.csv")
    samples = [
        json.loads(path.read_text()) | {"year": int(path.name[:4])}
        for path in sorted((output / "observations").glob("*-sample.json"))
    ]
    firm_days = int(comparison["firm_days"].iloc[0])
    lines = [
        f"# Panel design `{name}`",
        "",
        (
            f"Characteristics: {', '.join(design.characteristics)}. Network history: "
            f"{design.history} annual snapshots; cohort requires complete, nonconstant "
            f"{'- and '.join(map(str, design.cohort_histories))}-year histories. "
            f"All rows score the same {firm_days:,} held-out firm-days (2020-2025)."
        ),
        "One spatial coefficient per network, kernel and innovation arm is fitted on",
        "2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint",
        "Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;",
        "higher is better. Columns are kernel/innovation; `correlation` imposes prior raw",
        "sample variances on every row so only implied correlations differ.",
        "",
        "## Cohorts",
        "",
        "| Return year | Firms | Prior complete days | Scored days | Reference firms |",
        "| --- | ---: | ---: | ---: | ---: |",
        *[
            f"| {s['year']} | {s['firms']} | {s['past_complete_days']} | {s['evaluation_days']} "
            f"| {s.get('reference_firms', '—')} |"
            for s in samples
        ],
        "",
        "## Held-out gains over the joint Fernández network",
        "",
        *ladder_table(comparison),
        "",
        "## Covariance controls",
        "",
        *control_table(comparison),
    ]
    joint = bootstrap.loc[
        bootstrap["versus"].eq("joint") & bootstrap["column"].str.endswith("|exp|diagonal")
    ]
    lines += [
        "",
        "## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)",
        "",
        "Summed daily differences against the joint network; 95% percentile intervals",
        "with 21- and 63-day expected blocks. Intervals are descriptive: the approaches",
        "were not preregistered and these years were inspected during development.",
        "",
        "| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in joint.to_dict("records"):
        lines.append(
            f"| `{row['column'].split('|')[0]}` | {row['difference']:+,.2f} | "
            f"[{row['lower_21']:+,.1f}, {row['upper_21']:+,.1f}] | "
            f"[{row['lower_63']:+,.1f}, {row['upper_63']:+,.1f}] | "
            f"{row['politis_white_block']:.1f} |"
        )
    lines += contrast_table(pd.read_csv(output / "contrasts.csv"))
    if (output / "attribution.csv").exists():
        lines += attribution_table(pd.read_csv(output / "attribution.csv"), geometry)
    if design.decoded:
        quality = pd.read_csv(output / "decoding.csv")
        audit = pd.read_csv(output / "target-audit.csv")
        lines += measurement_table(comparison, quality, audit)
        lines += target_table(audit, quality)
        if design.support_sizes:
            lines += support_table(comparison, quality, audit, design.support_sizes)
    lines += [
        "",
        "## Model confidence sets (size 0.10)",
        "",
        "Families are networks within one kernel and innovation arm; covariance controls and",
        "the uniform and zero networks enter every family of their arm. A set ranks within",
        "its family only; choosing a family after seeing the results is not accounted for.",
        "",
    ]
    lines += ["| Family | Members | Included |", "| --- | ---: | --- |"]
    for family, group in mcs.groupby("family", sort=False):
        included = ", ".join(f"`{c.split('|')[0]}`" for c in group.loc[group["included"], "column"])
        lines.append(f"| {family} | {len(group)} | {included} |")
    lines += [
        "",
        "## Label-permutation placebos (exp kernel, diagonal innovations)",
        "",
        "Each prespecified network is compared with 19 permutations P W P' restricted",
        "within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.",
        "",
        "| Approach | Observed | Placebo mean | Placebo max | Rank p-value |",
        "| --- | ---: | ---: | ---: | ---: |",
        *[
            f"| `{r['approach']}` | {r['observed']:,.2f} | {r['placebo_mean']:,.2f} | "
            f"{r['placebo_max']:,.2f} | {r['rank_p_value']:.2f} |"
            for r in placebo.to_dict("records")
        ],
        "",
        "## Network concentration",
        "",
        "Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform. The matched",
        "kernel targets the joint network's mean effective neighbours under exp each year;",
        "`Matched miss` is the largest achieved miss, in neighbours, over all years. Matching",
        "the mean of 1/H_i does not match the mean row Herfindahl H, which the last two",
        "columns compare (held-out years), nor spectral structure.",
        "",
        "| Approach | exp | median | matched | Matched miss | Matched H | Joint exp H |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    fractions = geometry.pivot_table(
        index="approach", columns="kernel", values="effective_fraction", aggfunc="mean"
    )
    target = geometry.loc[
        geometry["approach"].eq("fernandez_joint") & geometry["kernel"].eq("exp")
    ].set_index("year")["effective_neighbours"]
    matched = geometry.loc[geometry["kernel"].eq("matched")]
    miss = (
        (matched["effective_neighbours"] - matched["year"].map(target))
        .abs()
        .groupby(matched["approach"])
        .max()
    )
    held = geometry.loc[geometry["year"] >= 2020]
    herfindahl = held.loc[held["kernel"].eq("matched")].groupby("approach")["mean_herfindahl"]
    joint = held.loc[held["approach"].eq("fernandez_joint") & held["kernel"].eq("exp")]
    joint_h = float(joint["mean_herfindahl"].mean())
    for approach, row in fractions.iterrows():
        values = [row.get(kernel, np.nan) for kernel in ("exp", "median", "matched")]
        lines.append(
            f"| `{approach}` | "
            + " | ".join(f"{v:.3f}" for v in values)
            + f" | {miss.get(approach, np.nan):.2g} | "
            + f"{herfindahl.mean().get(approach, np.nan):.4f} | {joint_h:.4f} |"
        )
    if name == "four" and (ROOT / "comparison.csv").exists():
        check = regression_check(comparison)
        check.to_csv(output / "regression-check.csv", index=False)
        lines += [
            "",
            "## Regression check against the original panel",
            "",
            f"{len(check)} unchanged approaches were rescored under the exp kernel and spherical",
            (
                "innovations; the largest absolute held-out difference is "
                f"{check['difference'].abs().max():.2e}."
            ),
        ]
    lines += [
        "",
        "## Interpretation limits",
        "",
        "Retrospective current-survivor sample; checkpoints postdate some evaluated dates.",
        "Daily Gaussian densities are working models; differences are paired and dependent,",
        "and many networks were compared. No row is a selected winner. Designs differ in",
        "firms and cannot be ranked against each other.",
    ]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n")
    artifacts = sorted(
        path
        for pattern in ("*.csv", "*.json", "*.parquet")
        for path in output.rglob(pattern)
        if path.name != "manifest.json"
    )
    sources = [
        *sorted(Path(__file__).parent.parent.rglob("*.py")),
        *sorted(Path(__file__).parent.parent.rglob("*.R")),
        Path("src/python/pyproject.toml"),
        Path("src/python/uv.lock"),
        Path("research/universe/cache/prices.parquet"),
        Path("research/universe/cache/factors.parquet"),
    ]
    write_json(
        output / "manifest.json",
        {
            "sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in artifacts},
            "source_sha256": {
                str(p.resolve().relative_to(Path.cwd())): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sources
            },
        },
    )


def main() -> None:
    """Report requested designs and shared provenance records."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--designs", nargs="+", default=list(DESIGNS), choices=list(DESIGNS))
    args = parser.parse_args()
    checkpoints, disclosures = audit_checkpoints(), audit_disclosures()
    for name in args.designs:
        output = DESIGNS[name].output
        if (output / "comparison.csv").exists():
            write_json(output / "checkpoints.json", checkpoints)
            write_json(output / "disclosure-audit.json", disclosures)
            results(name)


if __name__ == "__main__":
    main()
