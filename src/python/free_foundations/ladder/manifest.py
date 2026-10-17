"""What R0 reproduces from Fernández (2011), which conventions it adds, what it substitutes."""

from __future__ import annotations

from typing import TYPE_CHECKING

from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from pathlib import Path

REPORTED = (
    ("distance", "Eq. (9): sqrt(2(1 - Spearman)) between one characteristic's histories", "§2.4"),
    ("kernel", "Eq. (10): exp(-d), each row divided by its sum", "§2.4"),
    ("networks", "Four networks: cap/size, market-to-book, dividend yield, debt maturity", "§3.2"),
    ("sample_design", "One firm sample, every network estimated on the same firms", "§3.2"),
    ("stage_one", "Robust MM CAPM betas from quarterly returns (Yohai)", "§3.2"),
    ("stage_two", "Median quarterly excess returns on betas, no intercept (eqs. 6-7)", "§3.2"),
    ("lag_estimator", "Spatial lag by S2SLS, instruments [WX X], sigma^2 = e'e/N (eq. 2)", "§2.1"),
    ("error_estimator", "SAR error by concentrated Gaussian ML over lambda (eq. 4)", "§2.1"),
    ("moran", "Moran's I on least-squares residuals for each network (eq. 5)", "§2.1"),
    ("normality", "Shapiro-Wilk on model residuals", "Table 2"),
    ("fit", "Pseudo-R^2 = corr(fitted, actual)^2", "Table 2"),
    ("returns", "Forty quarterly returns and ten annual characteristic snapshots", "§3.1-3.2"),
)
CONVENTIONS = (
    ("diagonal", "Zero self-links primary; literal positive diagonal reported", "Eq. (10) silent"),
    ("ties", "Average ranks for tied history values", "Spearman"),
    (
        "bounds",
        "lambda and rho searched on (-0.99, 0.99): 201-point grid, bounded refinement",
        "Grid search",
    ),
    (
        "moran_moments",
        "Exact Cliff-Ord residual moments; printed E(M) sign corrected",
        "Eq. (5) prints +1/(N-1)",
    ),
    (
        "standard_errors",
        "ML information-matrix SEs (spreg-equivalent); S2SLS eq. (2)",
        "OPG not reproducible",
    ),
    (
        "factor_compounding",
        (
            "Compounded daily-factor proxies: quarterly long-short factors as prod(1+f)-1, "
            "not French quarterly portfolio legs (prod(1+L)-prod(1+S) differs)"
        ),
        "R4 extension",
    ),
    (
        "timing",
        "Snapshots 2015-2024 available by each year end; returns 2016Q1-2025Q4",
        "Paper uses 1997-2006 for both",
    ),
    ("mm_seed", "robustbase lmrob MM, seed 42 before each firm fit", "S-Plus tuning unknown"),
    (
        "mm_retry",
        "Non-converged fits refitted once with larger iteration limits (recorded)",
        "Default k.max=200 fails for a few firms",
    ),
)
SUBSTITUTIONS = (
    ("sample", "126 Brazilian, Chilean and Mexican firms", "Current US 1,000-issuer universe"),
    ("source", "Economatica", "SEC companyfacts and Yahoo prices"),
    ("firm_size", "Unspecified firm size", "Total assets"),
    ("debt_maturity", "Long-term / total debt", "Lease-inclusive noncurrent / total debt"),
    ("dividend_yield", "Dividend / price", "Trailing 365-day cash dividends / close"),
    ("market", "MSCI EM Latin America (USD)", "French Mkt-RF"),
    ("risk_free", "10-year US Treasury", "French one-month RF"),
    ("currency", "Local returns converted to USD", "USD"),
    ("inflation", "Inflation-adjusted ratios", "No inflation adjustment"),
    ("estimator_software", "S-Plus 7.0", "R robustbase and Python (NumPy/SciPy)"),
    (
        "standard_errors",
        "Outer product of first derivatives",
        "Information matrix: log|I - lambda W| has no per-observation split",
    ),
)


def write(output: Path) -> None:
    """JSON entries plus a Markdown table for the replication README."""
    write_json(
        output / "replication-manifest.json",
        {
            "reported": [dict(zip(("id", "text", "source"), row, strict=True)) for row in REPORTED],
            "conventions": [
                dict(zip(("id", "text", "reason"), row, strict=True)) for row in CONVENTIONS
            ],
            "substitutions": [
                dict(zip(("id", "paper", "ours"), row, strict=True)) for row in SUBSTITUTIONS
            ],
        },
    )
    lines = ["# R0 replication manifest", "", "## Reported choices reproduced", ""]
    lines += ["| Item | Paper | Source |", "| --- | --- | --- |"]
    lines += [f"| {item} | {text} | {source} |" for item, text, source in REPORTED]
    lines += ["", "## Implementation conventions", "", "| Item | Choice | Reason |"]
    lines += ["| --- | --- | --- |"]
    lines += [f"| {item} | {text} | {reason} |" for item, text, reason in CONVENTIONS]
    lines += ["", "## Substitutions", "", "| Item | Paper | Ours |", "| --- | --- | --- |"]
    lines += [f"| {item} | {paper} | {ours} |" for item, paper, ours in SUBSTITUTIONS]
    (output / "replication-manifest.md").write_text("\n".join(lines) + "\n")
