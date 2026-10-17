"""Readable R0 and R1-R4 tables from the saved machine-readable estimates."""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from free_foundations.ladder.data import ARMS, ROOT


def stars(value: float) -> str:
    """A compact p-value cell."""
    return "—" if not np.isfinite(value) else f"{value:.3f}"


def r0() -> None:
    """Fernández Table 2/3 layout per cohort, with sensitivities below."""
    output = ROOT / "r0"
    estimates = pd.read_csv(output / "estimates.csv")
    cohorts = json.loads((output / "cohorts.json").read_text())
    bootstrap = (
        pd.read_csv(output / "bootstrap.csv") if (output / "bootstrap.csv").exists() else None
    )
    lines = [
        "# R0: practical replication of Fernández (2011) on US data",
        "",
        "Stage one: robust MM CAPM betas (robustbase `lmrob`, MM) from 40 quarterly excess",
        "returns, 2016-2025. Stage two: median quarterly excess return on beta, no intercept.",
        "Networks: Spearman chord distances between 2015-2024 annual characteristic histories,",
        "exp(-d), row-normalized, zero diagonal (primary). See",
        "[the replication manifest](replication-manifest.md) for every substitution.",
        "",
        "`common_four` is the faithful design (one sample, every network on it).",
        "`coverage_*` tables use each characteristic's maximal cohort; their columns",
        "are not comparable with each other. These are in-sample descriptive fits.",
        "",
        "| Table | Firms |",
        "| --- | ---: |",
        *[f"| {label} | {entry['firms']} |" for label, entry in cohorts.items()],
    ]
    primary = estimates.loc[
        estimates["kernel"].isin(["exp", "none"]) & ~estimates["self_links"].astype(bool)
    ]
    for label, group in primary.groupby("table", sort=False):
        ols_row = group.loc[group["estimator"].eq("ols")].iloc[0]
        lines += [
            "",
            f"## {label}",
            "",
            (
                f"Least squares: premium {ols_row['premium_market']:.4f} "
                f"(p {ols_row['p_market']:.3f}), Shapiro-Wilk p {ols_row['shapiro_p']:.3f}, "
                f"pseudo-R² {ols_row['pseudo_r2_structural']:.3f}, AIC {ols_row['aic']:.2f}."
            ),
            "",
            (
                "| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | "
                "Pseudo-R² | AIC | Boundary |"
            ),
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |",
        ]
        for row in group.loc[group["estimator"].ne("ols")].to_dict("records"):
            lines.append(
                f"| {row['network'].removeprefix('fernandez_')} | "
                f"{row['ols_moran']:.3f} ({row['ols_moran_p']:.3f}) | {row['estimator']} | "
                f"{row['premium_market']:.4f} ({stars(row['p_market'])}) | "
                f"{row['intensity']:.3f} ({stars(row['intensity_p'])}) | {row['shapiro_p']:.3f} | "
                f"{row['pseudo_r2_structural']:.3f} | "
                f"{'—' if not np.isfinite(row['aic']) else format(row['aic'], '.2f')} | "
                f"{row['boundary']} |"
            )
    sensitivity = estimates.loc[
        estimates["estimator"].eq("spatial_error_ml")
        & (estimates["kernel"].ne("exp") | estimates["self_links"].astype(bool))
    ]
    lines += [
        "",
        "## Sensitivity: literal self-links and median-scaled kernel (SEM-ML)",
        "",
        "| Table | Network | Kernel | Self-links | Premium | λ | Boundary |",
        "| --- | --- | --- | --- | ---: | ---: | --- |",
        *[
            f"| {r['table']} | {r['network'].removeprefix('fernandez_')} | {r['kernel']} | "
            f"{r['self_links']} | {r['premium_market']:.4f} | {r['intensity']:.3f} | "
            f"{r['boundary']} |"
            for r in sensitivity.to_dict("records")
        ],
    ]
    if bootstrap is not None:
        lines += [
            "",
            "## Generated-beta bootstrap (W fixed)",
            "",
            "Quarters resampled jointly for returns and factors (stationary bootstrap,",
            "expected block four quarters), MM betas and medians recomputed, 199 valid replicates.",
            "",
            "| Table | Network | Parameter | Bootstrap SE | 95% interval |",
            "| --- | --- | --- | ---: | --- |",
            *[
                f"| {r['table']} | {r['network'].removeprefix('fernandez_')} | {r['parameter']} | "
                f"{r['bootstrap_se']:.4f} | [{r['lower']:.4f}, {r['upper']:.4f}] |"
                for r in bootstrap.to_dict("records")
            ],
        ]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n")


def arm(name: str) -> None:
    """One arm's matched ladder: SEM-ML gains over OLS and over the joint benchmark."""
    output = ROOT / name
    estimates = pd.read_csv(output / "estimates.csv")
    placebo = pd.read_csv(output / "placebo.csv").set_index(["network", "kernel"])
    geometry = pd.read_csv(output / "geometry.csv").set_index(["network", "kernel"])
    bootstrap = (
        pd.read_csv(output / "bootstrap.csv") if (output / "bootstrap.csv").exists() else None
    )
    firms = int(estimates["firms"].iloc[0])
    lines = [
        f"# Cross-sectional ladder: `{name}` arm ({', '.join(ARMS[name])})",
        "",
        f"All rows use the same {firms} firms, median quarterly excess returns 2016-2025 and",
        "MM exposures. Each spatial row estimates one coefficient for one combined network.",
        "Information criteria are conditional on generated exposures and W (n = firms).",
        "Rows with equal parameter counts have identical AIC/BIC/HQIC rankings",
        "(ΔIC = -2 ΔlogL), so the criteria add information only across nonspatial versus",
        "spatial rows and CAPM versus FF5+Mom exposures. Not ranked against the other arm.",
    ]
    for factors, group in estimates.groupby("factors", sort=False):
        sem = group.loc[group["estimator"].eq("spatial_error_ml")]
        base = group.loc[group["estimator"].eq("ols")].iloc[0]
        joint = sem.loc[sem["network"].eq("fernandez_joint") & sem["kernel"].eq("exp")]
        joint_ll = float(joint["log_likelihood"].iloc[0])
        lines += [
            "",
            f"## {str(factors).upper()} exposures, SEM-ML",
            "",
            (
                f"Nonspatial OLS: log-likelihood {base['log_likelihood']:.3f}, "
                f"AIC {base['aic']:.2f}, BIC {base['bic']:.2f}, HQIC {base['hqic']:.2f}."
            ),
            "",
            (
                "| Network | Rung | Kernel | λ (p) | Premium (p) | logL - OLS | logL - joint | "
                "BIC | Eff. nbrs | Placebo p | Boundary |"
            ),
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
        ]
        for row in sem.to_dict("records"):
            key = (row["network"], row["kernel"])
            fraction = geometry.loc[key, "effective_fraction"] if key in geometry.index else np.nan
            rank = (
                placebo.loc[key, "rank_p_value"]
                if key in placebo.index and factors == "capm"
                else np.nan
            )
            lines.append(
                f"| `{row['network']}` | {row['rung']} | {row['kernel']} | "
                f"{row['intensity']:.3f} ({stars(row['intensity_p'])}) | "
                f"{row['premium_market']:.4f} ({stars(row['p_market'])}) | "
                f"{row['log_likelihood'] - base['log_likelihood']:+.3f} | "
                f"{row['log_likelihood'] - joint_ll:+.3f} | {row['bic']:.2f} | "
                f"{float(fraction):.3f} | {stars(float(rank))} | {row['boundary']} |"
            )
    if bootstrap is not None:
        selected = bootstrap.loc[bootstrap["parameter"].isin(["sem_intensity", "sem_premium"])]
        lines += [
            "",
            "## Generated-beta bootstrap (exp kernel, W fixed)",
            "",
            "| Factors | Network | Parameter | Bootstrap SE | 95% interval |",
            "| --- | --- | --- | ---: | --- |",
            *[
                f"| {r['factors']} | `{r['network']}` | {r['parameter']} | "
                f"{r['bootstrap_se']:.4f} | [{r['lower']:.4f}, {r['upper']:.4f}] |"
                for r in selected.to_dict("records")
            ],
        ]
    (output / "RESULTS.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    """Write every available ladder report."""
    if (ROOT / "r0" / "estimates.csv").exists():
        r0()
    for name in ARMS:
        if (ROOT / name / "estimates.csv").exists():
            arm(name)


if __name__ == "__main__":
    main()
