"""Layer B: quarterly spatial panels of excess returns with period effects.

Each quarter's analytical roster with an observed return and a full-panel MM beta
enters the panel. Period effects absorb common shocks; the regressor is the CAPM
component ``beta_i * MktRF_t``; the only network parameter is the spatial lag (or
error) coefficient on that quarter's as-of graph. Missing returns remove their
issuer from that quarter's graph before construction (about half a percent of
cells). Intervals come from profile-likelihood curvature and a stationary quarter
bootstrap; network comparisons use per-quarter likelihood contributions.
"""

from __future__ import annotations

import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from free_foundations.artifacts.atomic import atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.methods import spatial_ml
from free_foundations.methods.fernandez.evaluation import robust_betas
from free_foundations.methods.inference import (
    block_length,
    holm,
    percentile_interval,
    stationary_orders,
)
from free_foundations.study.experiments.inputs import StudyInputs, load

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
PROCESSES = ("lag", "error")
Z = 1.959963984540054


SETTINGS = (
    "panel_start",
    "characteristic_history_years",
    "min_beta_quarters",
    "generated_beta_draws",
    "likelihood_draws",
    "neighbours",
    "neighbour_sensitivities",
    "seed",
)


def panel_betas(inputs: StudyInputs, output: Path) -> pd.Series:
    """MM CAPM betas of every analytical issuer over the whole panel calendar."""
    spec = inputs.spec
    panel = inputs.tables["panel"].copy()
    panel["quarter"] = pd.to_datetime(panel["quarter"]).dt.to_period("Q").dt.to_timestamp("Q")
    calendar = spec.panel_calendar
    panel = panel.loc[panel["quarter"].isin(calendar) & panel["observed"].astype(bool)]
    factors = inputs.factors.reindex(calendar)
    sample = pd.DataFrame(
        {
            "ticker": panel["issuer_id"].astype(str),
            "date": panel["quarter"],
            "excess": panel["total_return"] - panel["quarter"].map(factors["RF"]),
            "market": panel["quarter"].map(factors["Mkt-RF"]),
        }
    )
    counts = sample.groupby("ticker").size()
    sample = sample.loc[sample["ticker"].map(counts).ge(spec.min_beta_quarters)]
    with TemporaryDirectory(dir=output, prefix=".mm-") as directory:
        try:
            estimates = robust_betas(
                sample, Path(directory), terms=("market",), cores=6, tag="panel"
            )
        except RuntimeError as error:
            if "did not converge" not in str(error):
                raise
            estimates = pd.read_csv(Path(directory) / "cache/mm-panel-output.csv")
    selected = estimates.loc[estimates["term"].eq("market")].set_index("ticker")
    return selected["estimate"].where(selected["converged"].astype(bool))


def _periods(
    inputs: StudyInputs, betas: pd.Series
) -> tuple[dict[str, list[spatial_ml.Period]], list[dict[str, Any]], list[pd.Timestamp]]:
    """Sufficient period vectors for every network, quarter by quarter."""
    spec = inputs.spec
    factors = inputs.factors
    neighbours = (spec.neighbours, *spec.neighbour_sensitivities)
    periods: dict[str, list[spatial_ml.Period]] = {}
    ledger: list[dict[str, Any]] = []
    calendar: list[pd.Timestamp] = []
    for quarter in spec.panel_calendar:
        # Networks form each January, like the December roster, and hold for the year.
        formation = pd.Timestamp(year=quarter.year, month=3, day=31)
        formed = set(inputs.roster(formation)["issuer_id"].astype(str))
        rows = inputs.roster(quarter)
        beta = rows["issuer_id"].map(betas)
        keep = rows["observed"].astype(bool) & beta.notna() & rows["issuer_id"].isin(formed)
        rows = rows.loc[keep].reset_index(drop=True)
        if len(rows) <= max(neighbours):
            ledger.append({"quarter": quarter, "issuers": len(rows), "status": "too_few_issuers"})
            continue
        calendar.append(quarter)
        rate, market = factors.reindex([quarter])[["RF", "Mkt-RF"]].to_numpy(float)[0]
        y = rows["total_return"].to_numpy(float) - rate
        z = beta.loc[keep].to_numpy(float) * market
        networks = inputs.networks(formation, rows.assign(quarter=formation), neighbours)
        ledger.append(
            {
                "quarter": quarter,
                "formation": formation,
                "roster": len(keep),
                "issuers": len(rows),
                "missing_return": int((~inputs.roster(quarter)["observed"].astype(bool)).sum()),
                "missing_beta": int(beta.isna().sum()),
                "not_formed_in_january": int(
                    (~inputs.roster(quarter)["issuer_id"].isin(formed)).sum()
                ),
                "networks": len(networks),
            }
        )
        for name, network in networks.items():
            if not (name.startswith("fernandez:") and name.endswith("|exp")):
                periods.setdefault(name, []).append(spatial_ml.Period.of(y, z, network.weights))
        LOGGER.info("Quarter %s: %s issuers, %s networks", quarter.date(), len(rows), len(networks))
    complete = {name: items for name, items in periods.items() if len(items) == len(calendar)}
    ledger.extend(
        {"network": name, "status": "unavailable_some_quarters"}
        for name in sorted(set(periods) - set(complete))
    )
    return complete, ledger, calendar


def _fit_rows(
    periods: dict[str, list[spatial_ml.Period]],
) -> tuple[pd.DataFrame, dict[tuple[str, str], spatial_ml.PanelFit]]:
    rows: list[dict[str, Any]] = []
    fits: dict[tuple[str, str], spatial_ml.PanelFit] = {}
    for name, items in periods.items():
        for process in PROCESSES:
            if process == "error" and name.startswith("industry"):
                rows.append(
                    {
                        "network": name,
                        "process": process,
                        "status": "unavailable",
                        "reason": "isolated issuers break W1 = 1 for period effects",
                    }
                )
                continue
            fit = spatial_ml.panel_profile(items, process)
            fits[name, process] = fit
            rows.append(
                {
                    "network": name,
                    "process": process,
                    "status": "available",
                    "reason": "",
                    "spatial": fit.spatial,
                    "spatial_se": fit.spatial_se,
                    "spatial_low": fit.spatial - Z * fit.spatial_se,
                    "spatial_high": fit.spatial + Z * fit.spatial_se,
                    "capm_slope": fit.slope,
                    "variance": fit.variance,
                    "log_likelihood": fit.loglik,
                    "observations": int(sum(len(period.outcome) for period in items)),
                }
            )
    return pd.DataFrame(rows), fits


def _bootstrap(
    periods: dict[str, list[spatial_ml.Period]],
    names: list[str],
    orders: np.ndarray,
) -> pd.DataFrame:
    """Stationary quarter bootstrap of the spatial coefficient, refitting each draw."""
    rows = []
    for name in names:
        items = periods[name]
        for process in PROCESSES:
            if process == "error" and name.startswith("industry"):
                continue
            values = np.array(
                [
                    spatial_ml.panel_profile([items[index] for index in order], process).spatial
                    for order in orders
                ]
            )
            low, high, count = percentile_interval(values)
            rows.append(
                {
                    "network": name,
                    "process": process,
                    "bootstrap_low": low,
                    "bootstrap_high": high,
                    "bootstrap_draws": count,
                }
            )
    return pd.DataFrame(rows)


def _comparisons(
    fits: dict[tuple[str, str], spatial_ml.PanelFit],
    spec_neighbours: int,
    draws: int,
    block: float,
    seed: int,
) -> pd.DataFrame:
    """Per-quarter log-likelihood differences against the matched references."""
    suffix = f"|knn{spec_neighbours}"
    rows = []
    for (name, process), fit in fits.items():
        if not name.endswith(suffix) or name.startswith("fernandez:joint"):
            continue
        rung = name.split(":", 1)[0]
        references = ["fernandez:joint" + suffix]
        if rung in {"fernandez", "standard_xbrl"} and not name.endswith(":direct" + suffix):
            references.append(f"{rung}:direct{suffix}")
        for reference in references:
            if (reference, process) not in fits:
                continue
            difference: FloatArray = fit.contributions - fits[reference, process].contributions
            orders = stationary_orders(len(difference), draws, block, seed)
            means = difference[orders].mean(axis=1)
            low, high, count = percentile_interval(means)
            standard = means.std(ddof=1)
            statistic = difference.mean() / standard if standard > 0 else np.nan
            rows.append(
                {
                    "network": name,
                    "reference": reference,
                    "process": process,
                    "mean_difference": float(difference.mean()),
                    "total_difference": float(difference.sum()),
                    "low": low,
                    "high": high,
                    "draws": count,
                    "p_value": float(2 * (1 - _normal_cdf(abs(statistic))))
                    if np.isfinite(statistic)
                    else np.nan,
                }
            )
    frame = pd.DataFrame(rows)
    if not frame.empty:
        frame["p_holm"] = holm(frame["p_value"])
    return frame


def _normal_cdf(value: float) -> float:
    return float(norm.cdf(value))


def run(panel: Path, representations: Path | None, output: Path, params: Path) -> None:
    """Fit every network's panel, bootstrap the primary graphs and compare networks."""
    inputs = load(panel, representations, params)
    spec = inputs.spec
    output.mkdir(parents=True, exist_ok=True)
    betas = panel_betas(inputs, output)
    periods, ledger, calendar = _periods(inputs, betas)
    estimates, fits = _fit_rows(periods)
    market = inputs.factors.reindex(calendar)["Mkt-RF"].to_numpy(float)
    block = block_length(market)
    orders = stationary_orders(len(calendar), spec.generated_beta_draws, block, spec.seed)
    primary = [
        name
        for name in periods
        if name.endswith(f"|knn{spec.neighbours}") or name.startswith("industry")
    ]
    intervals = _bootstrap(periods, primary, orders)
    estimates = estimates.merge(intervals, on=["network", "process"], how="left")
    comparisons = _comparisons(fits, spec.neighbours, spec.likelihood_draws, block, spec.seed)
    contributions = pd.DataFrame(
        [
            {"network": name, "process": process, "quarter": quarter, "log_likelihood": value}
            for (name, process), fit in fits.items()
            for quarter, value in zip(calendar, fit.contributions, strict=True)
        ]
    )
    atomic_parquet(output / "estimates.parquet", estimates)
    atomic_parquet(output / "comparisons.parquet", comparisons)
    atomic_parquet(output / "contributions.parquet", contributions)
    atomic_parquet(output / "ledger.parquet", pd.DataFrame(ledger))
    atomic_parquet(output / "betas.parquet", betas.rename("mm_beta").reset_index())
    write_json(
        output / "manifest.json",
        {
            "study_sha256": spec.experiment_digest(SETTINGS),
            "calendar": [str(quarter.date()) for quarter in calendar],
            "expected_block_quarters": block,
            "bootstrap_draws": spec.generated_beta_draws,
            "comparison_draws": spec.likelihood_draws,
            "regressor": "MM beta (full panel) times quarterly Mkt-RF",
            "effects": "period",
            "missing_returns": "issuer removed from that quarter's graph before construction",
        },
    )
