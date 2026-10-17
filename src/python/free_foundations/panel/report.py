"""Report pooled calibration and one held-out score per financial topology."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.fernandez.models import paper_weights
from free_foundations.panel.characteristics import ROOT, audit_disclosures
from free_foundations.pilot.data import write_json


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


def audit_geometry() -> None:
    """Check labeled distances and weights and expose nearly uniform networks."""
    records: list[dict[str, str | int | float | bool]] = []
    for path in sorted((ROOT / "distances").glob("*/*.parquet")):
        matrix = pd.read_parquet(path)
        sample = json.loads((ROOT / "observations" / f"{path.parent.name}-sample.json").read_text())
        values = matrix.to_numpy(dtype=float)
        valid = (
            list(matrix.index) == sample["tickers"] == list(matrix.columns)
            and np.isfinite(values).all()
            and values.min() >= 0
            and values.max() <= 2 + 1e-8
            and np.allclose(values, values.T)
            and np.allclose(np.diag(values), 0)
        )
        if not valid:
            message = f"Invalid annual distance matrix: {path}"
            raise ValueError(message)
        weights = pd.read_parquet(ROOT / "weights" / path.parent.name / path.name)
        expected = paper_weights(values)
        if list(weights.index) != list(matrix.index) or list(weights.columns) != list(
            matrix.columns
        ):
            message = f"Weight labels disagree with distance labels: {path}"
            raise ValueError(message)
        np.testing.assert_allclose(weights.to_numpy(), expected, atol=1e-12, rtol=1e-12)
        off_diagonal = values[~np.eye(len(values), dtype=bool)]
        records.append(
            {
                "year": int(path.parent.name),
                "approach": path.stem,
                "firms": len(values),
                "mean_distance": float(off_diagonal.mean()),
                "sd_distance": float(off_diagonal.std()),
                "collapsed": bool(off_diagonal.max() < 1e-10),
                "mean_effective_neighbors": float(np.mean(1 / np.sum(expected**2, axis=1))),
            }
        )
    pd.DataFrame(records).to_csv(ROOT / "geometry-audit.csv", index=False)


def run() -> None:
    """Keep comparison units, common sample, timing, and replication limits explicit."""
    audit_geometry()
    write_json(ROOT / "checkpoints.json", audit_checkpoints())
    write_json(ROOT / "disclosure-audit.json", audit_disclosures())
    results = pd.read_csv(ROOT / "comparison.csv").set_index("approach")
    samples = [
        json.loads(path.read_text()) | {"year": int(path.name[:4])}
        for path in sorted((ROOT / "observations").glob("*-sample.json"))
    ]
    coverage = pd.DataFrame(
        [
            {key: sample[key] for key in ("year", "firms", "past_complete_days", "evaluation_days")}
            for sample in samples
        ]
    )
    coverage.to_csv(ROOT / "panel-coverage.csv", index=False)
    overlaps = []
    for sample in samples:
        contexts = [
            set(
                json.loads((ROOT / "contexts" / f"{sample['year']}-{rung}.json").read_text())[
                    "support_ids"
                ]
            )
            for rung in ("four", "broad", "metrics")
        ]
        overlaps.append(
            {
                "year": sample["year"],
                "common_support_rows": len(set.intersection(*contexts)),
                "support_rows_per_rung": len(contexts[0]),
            }
        )
    pd.DataFrame(overlaps).to_csv(ROOT / "context-overlap.csv", index=False)
    baseline = float(results["heldout_log_likelihood"].loc["fernandez_joint_four"])
    lines = [
        "# Chronological matched-panel comparison",
        "",
        "One constant spatial coefficient per approach is estimated by Gaussian residual ML",
        "on 2016-2019 and frozen for 2020-2025. The principal score is summed held-out",
        "Gaussian log-likelihood of daily excess returns; higher is better. It includes all",
        "normalizing constants. Returns are decimals, not percentages.",
        "",
        "All approaches use the identical annual firms and dates. Every annual spatial",
        "network combines its input into one W. There is no coefficient per feature or year.",
        "Annual nuisance variances and factor loadings are estimated using preceding returns.",
        "No test-year factors or returns enter an annual covariance or expected-return forecast.",
        "",
        "| Approach | Frozen lambda | Held-out log-likelihood | Gain vs joint four | Boundary |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for name, row in results.iterrows():
        intensity = "—" if np.isnan(row["lambda"]) else f"{row['lambda']:.4f}"
        score = float(row["heldout_log_likelihood"])
        lines.append(
            f"| {name} | {intensity} | {score:,.2f} | "
            f"{score - baseline:+,.2f} | {row['boundary']} |"
        )
    lines += [
        "",
        "## Annual matched cohorts",
        "",
        "| Return year | Firms | Prior complete days | Scored days |",
        "| --- | ---: | ---: | ---: |",
    ]
    for sample in samples:
        lines.append(
            f"| {sample['year']} | {sample['firms']} | "
            f"{sample['past_complete_days']} | {sample['evaluation_days']} |"
        )
    lines += [
        "",
        "## Construction and chronology",
        "",
        "- The four characteristics are capitalization/assets, market/book, dividend yield,",
        "  and the strict lease-inclusive noncurrent-debt/total-debt ratio. Missing debt is",
        "  never interpreted as zero. Known unresolved multiple share classes are excluded.",
        "- Each annual snapshot uses only 10-K/10-K-A facts filed by December 31, with period",
        "  ends no more than 550 days old. Original dates and accessions are retained in cache.",
        "  Capitalization uses shares and split-reversed prices at the share observation date;",
        "  assets and equity share a balance-sheet date. These dates can differ and are audited.",
        "  Dividend yield uses trailing cash dividends on the same split basis as price.",
        "- The strict cohort requires three complete, nonconstant annual histories for all",
        "  four characteristics and at least 500 prior returns. The three-year history is",
        "  a coverage compromise and yields relatively coarse Spearman distances.",
        "  This is a US chronological adaptation, not an exact replication of Fernández's",
        "  original sample, robust cross-sectional S-APT estimation, or history length.",
        "- Fernández rows use Spearman chord distances, exp(-distance), zero diagonal,",
        "  and row normalization. The joint-four RMS row is our extension; the original",
        "  single-characteristic networks remain explicit references.",
        "  A uniform network provides a geometry-free reference for the added value of topology.",
        "- `four` encodes all four three-year histories jointly. `broad` adds up to 200",
        "  unit- and period-specific SEC concepts in signed-log levels. `metrics` adds",
        "  up to 100 concepts, asset-normalized dollar measures, their annual changes, and",
        "  log assets. Schema selection uses past support-period coverage only.",
        "- Model inputs use support-only median imputation, missingness indicators,",
        "  standardization and clipping. PCA, autoencoder and random-encoder controls share",
        "  a deterministic, outcome-independent 256-row historical support cap with the",
        "  pretrained models. Preprocessing is fit before this cap on eligible past support.",
        "  Support membership is matched across encoders within a rung. Cross-rung eligibility",
        "  can differ slightly; common support counts are recorded in context-overlap.csv.",
        "- Frozen foundation-model readouts use native late row states, not return predictions.",
        "  The supervised context target is next-snapshot capitalization/assets, available",
        "  by the network cutoff. Context years, rows, schemas and checkpoint hashes are saved.",
        "  All learned vectors use unit-sphere chord distance and the same exponential kernel.",
        "  The direct baseline adds a constant coordinate to avoid zero-vector distances.",
        "- Factor means, loadings and covariances use the preceding three calendar years.",
        "  The spatial coefficient is fitted once on calibration-year factor residuals,",
        "  profiling an innovation variance per calibration year. Each evaluation year's",
        "  variance is estimated from prior residuals at that fixed coefficient.",
        "  Covariance forecasts are B Cov(F) B' plus the spatial residual covariance.",
        "  Mean forecasts are prior mean excess returns. Raw covariance uses the same window.",
        "- The full sample-residual FF covariance reconstructs raw sample covariance under",
        "  OLS orthogonality; their equal scores are a useful independent consistency check.",
        "- The first daily return of each year is excluded: its interval can start before",
        "  a December 31 after-close filing. Filing dates have no intraday timestamp.",
        "- Missing future observations remove dates identically for every approach, never",
        "  firms when forming the network; removed dates are recorded in sample JSON files.",
        "  Thus scores condition on common observed dates and omit missing outcomes.",
        "",
        "## Interpretation and limitations",
        "",
        "This is a retrospective public-data experiment on current survivors. Checkpoints",
        "were released after some evaluated dates; their pretraining provenance is not a",
        "verified historical information set. The research pipeline prevents panel look-ahead,",
        "but does not establish absence of checkpoint pretraining contamination.",
        "",
        "The raw SEC snapshot schema is broad, not a complete universe of economically",
        "harmonized accounting ratios. Company-specific extension tags and segment facts",
        "are outside companyfacts. Dividend nonpayers and firms missing strict debt histories",
        "are excluded from this matched comparison; the larger acquired universe is not",
        "the estimation sample. Yahoo share-class alignment remains a limitation.",
        "",
        "Daily Gaussian densities are working models; serial dependence, changing volatility,",
        "and selecting among many encoders prevent treating likelihood differences as",
        "conventional significance tests. No chi-square p-values are attached to nonnested",
        "network comparisons. A boundary flag means |lambda| >= 0.985 within (-0.99, 0.99).",
        "",
        "See `comparison.csv` for the separate calibration ML likelihood and normalized score,",
        "`annual-scores.csv` for diagnostics, `panel-coverage.csv` for sample sizes, and",
        "`distances/<year>/` and `weights/<year>/` for labeled matrices. The geometry audit",
        "checks those matrices and reports effective neighbor counts. Reproduce with",
        "`just python-panel`; model readouts and characteristics are cached.",
    ]
    (ROOT / "RESULTS.md").write_text("\n".join(lines) + "\n")
    artifacts = [*ROOT.rglob("*.parquet"), *ROOT.rglob("*.csv"), *ROOT.rglob("*.json")]
    write_json(
        ROOT / "manifest.json",
        {
            "sha256": {
                str(path): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(artifacts)
                if path.name != "manifest.json"
            },
            "source_sha256": {
                str(path.resolve().relative_to(Path.cwd())): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in [
                    *sorted(Path(__file__).parent.parent.rglob("*.py")),
                    Path("src/python/pyproject.toml"),
                    Path("src/python/uv.lock"),
                    Path("research/universe/manifest.json"),
                    Path("research/universe/cache/prices.parquet"),
                    Path("research/universe/cache/factors.parquet"),
                ]
            },
        },
    )


if __name__ == "__main__":
    run()
