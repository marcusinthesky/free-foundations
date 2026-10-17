"""Report each panel design without selecting a test-period winner."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.panel.characteristics import ROOT, audit_disclosures
from free_foundations.panel.design import DESIGNS
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
            f"{design.history} annual snapshots; cohort requires complete, nonconstant {'- and '.join(map(str, design.cohort_histories))}-year histories. "
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
        "| Return year | Firms | Prior complete days | Scored days |",
        "| --- | ---: | ---: | ---: |",
        *[
            f"| {s['year']} | {s['firms']} | {s['past_complete_days']} | {s['evaluation_days']} |"
            for s in samples
        ],
        "",
        "## Held-out gains over the joint Fernández network",
        "",
        *ladder_table(comparison),
        "",
        "## Covariance controls",
        "",
        "| Control | Held-out log-likelihood | Correlation-only |",
        "| --- | ---: | ---: |",
    ]
    controls = comparison.loc[comparison["arm"].eq("control")]
    for row in controls.to_dict("records"):
        correlation = comparison.loc[
            comparison["approach"].eq(row["approach"]) & comparison["innovation"].eq("correlation")
        ]["heldout_log_likelihood"]
        lines.append(
            f"| `{row['approach']}` | {row['heldout_log_likelihood']:,.2f} | "
            f"{float(correlation.iloc[0]):,.2f} |"
        )
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
    lines += ["", "## Model confidence sets (size 0.10)", ""]
    lines += ["| Family | Networks | Included |", "| --- | ---: | --- |"]
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
        "Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform.",
        "",
        "| Approach | exp | median | matched |",
        "| --- | ---: | ---: | ---: |",
    ]
    fractions = geometry.pivot_table(
        index="approach", columns="kernel", values="effective_fraction", aggfunc="mean"
    )
    for approach, row in fractions.iterrows():
        values = [row.get(kernel, np.nan) for kernel in ("exp", "median", "matched")]
        lines.append(f"| `{approach}` | " + " | ".join(f"{v:.3f}" for v in values) + " |")
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
