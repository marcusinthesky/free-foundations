"""Summarize acquired coverage without presenting it as a fitted research sample."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path


def write_report(output: Path) -> None:
    """Write the realized universe and time coverage, including binding exclusions."""
    status = json.loads((output / "status.json").read_text())
    configuration = json.loads((output / "configuration.json").read_text())
    coverage = pd.read_csv(output / "coverage.csv")
    factors = pd.read_parquet(output / "cache/factors.parquet")
    lines = [
        "# Expanded public-data universe",
        "",
        f"{status['issuers']:,} SEC issuers; {status['with_prices']:,} have Yahoo prices.",
        f"Observed prices span {status['first_price']} to {status['last_price']}.",
        f"FF5, momentum and RF span {factors.index.min().date()} to {factors.index.max().date()}.",
        f"There are {status['accounting_snapshots']:,} annual filing-availability snapshots.",
        "",
        "These are acquisition and availability results, not estimates from the spatial models.",
        "The candidates are current US exchange listings ranked by current market capitalization.",
        "One share class is kept per SEC CIK, with USD US-GAAP annual 10-K assets required.",
        "Current-listing selection retains survivorship bias.",
        "",
        "## Annual availability",
        "",
        "The eligibility column requires positive assets known at the preceding year end and",
        "at least 500 observed daily returns in the prior three-calendar-year window.",
        "Future prices do not select the cohort; missing outcomes need separate handling.",
        "Debt uses the existing strict, period-aligned, lease-inclusive mapping.",
        "Market-cap/assets, dividend yield, full histories, and broader model inputs",
        "still require their own construction and audits before a new spatial comparison.",
        "",
        "| Year | Assets | Equity > 0 | Strict debt | Assets + prior returns | With strict debt |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.extend(
        f"| {row['evaluation_year']} | {row['known_assets']} | "
        f"{row['positive_book_equity']} | {row['strict_debt_maturity']} | "
        f"{row['assets_and_500_prior_returns']} | {row['eligible_with_strict_debt']} |"
        for row in coverage.to_dict("records")
    )
    lines += [
        "",
        "## Reproduction and artifacts",
        "",
        "Run `devenv shell just python-universe` with `EDGAR_IDENTITY` set.",
        f"The requested screen contains up to {configuration['candidates']:,} candidates.",
        "The configuration is frozen per output directory; change `--output` for another design.",
        "Downloads resume from individual compressed SEC files and cached Yahoo batches.",
        "`universe.csv` lists issuers; `universe-exclusions.json` records exclusions.",
        "`price-coverage.json`, `price-failures.json`, and `coverage.csv` record availability.",
        "The cache preserves SEC facts, Yahoo OHLC/actions, adjusted closes, and French factors.",
        "`availability.parquet` and per-issuer snapshots retain asset filing dates and accessions.",
        "`manifest.json` hashes the acquired files. Large inputs are ignored by Git.",
        "",
        "The main study should use annual changing cohorts with identical observations across",
        "approaches within each comparison. Exact Fernandez replication remains a separate",
        "strict cohort. Imputations or alternative debt definitions are extensions.",
        "The working paper design and conditional stability proof are in `src/latex/main.tex`.",
    ]
    (output / "README.md").write_text("\n".join(lines) + "\n")
