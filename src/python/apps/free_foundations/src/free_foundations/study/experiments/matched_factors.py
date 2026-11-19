"""Matched quarterly sample and Fama-French comparisons with fixed loadings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.artifacts.atomic import atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.fernandez.evaluation import robust_betas
from free_foundations.methods.inference import block_length, percentile_interval, stationary_orders
from free_foundations.methods.matched_panel import Fit, Period, Process, fit, prepare_graph
from free_foundations.methods.networks import (
    characteristic_distances,
    knn_weights,
    representation_distance,
)
from free_foundations.study.experiments.inputs import StudyInputs, load
from free_foundations.study.representations.matched import load_cell
from free_foundations.study.spec import StudySpec, digest_json, file_hash

if TYPE_CHECKING:
    from collections.abc import Sequence

    from numpy.typing import NDArray

    from free_foundations.encoders.contracts import FloatArray

OTHER_FACTORS = {"smb": "SMB", "hml": "HML", "rmw": "RMW", "cma": "CMA", "mom": "Mom"}
FACTORS = {"market": "Mkt-RF", **OTHER_FACTORS}
FACTOR_SETS = {
    "market": ("market",),
    **{name: (name,) for name in OTHER_FACTORS},
    **{f"market_{name}": ("market", name) for name in OTHER_FACTORS},
    "ff5": ("market", "smb", "hml", "rmw", "cma"),
    "ff5_mom": tuple(FACTORS),
}
RUNG_ORDER = ("fernandez", "operands", "standard_xbrl")
NEIGHBOURS = 10
SAMPLE_SETTINGS = ("panel_start", "archive_end", "min_beta_quarters")
SPATIAL_PROCESSES: tuple[Process, ...] = ("lag", "error")


@dataclass(frozen=True)
class SampleQuarter:
    """Ordered outcomes and issuer-specific factor components for a quarter."""

    quarter: pd.Timestamp
    formation: pd.Timestamp
    issuers: tuple[str, ...]
    outcome: FloatArray
    design: dict[str, FloatArray]


@dataclass(frozen=True)
class Sample:
    """The verified common sample and policy for all t08 comparisons."""

    quarters: tuple[SampleQuarter, ...]
    market: FloatArray
    spec: StudySpec
    manifest: dict[str, object]


def _exposure_fit(
    frame: pd.DataFrame, work: Path, name: str, terms: tuple[str, ...], minimum: int
) -> pd.DataFrame:
    counts = frame.groupby("ticker").size()
    sample = frame.loc[frame["ticker"].map(counts).ge(max(minimum, len(terms) + 2))]
    path = work / f"cache/mm-{name}-output.csv"
    if sample.empty:
        return pd.DataFrame(columns=["ticker", "term", "estimate", "converged"]).assign(
            specification=name
        )
    try:
        result = robust_betas(sample, work, terms=terms, tag=name)
    except RuntimeError as error:
        if "did not converge" not in str(error):
            raise
        result = pd.read_csv(path)
    return result.assign(specification=name)


def _sample_frame(inputs: StudyInputs) -> pd.DataFrame:
    panel = inputs.tables["panel"]
    observed = panel.loc[panel["observed"].astype(bool)].copy()
    observed["date"] = pd.to_datetime(observed["quarter"])
    observed["ticker"] = observed["issuer_id"].astype(str)
    observed = observed.loc[observed["date"].isin(inputs.spec.panel_calendar)].copy()
    if observed.duplicated(["ticker", "date"]).any():
        msg = "Observed quarterly outcomes must have unique issuer identities."
        raise ValueError(msg)
    factors = inputs.factors.reindex(inputs.spec.panel_calendar)
    required = factors[["RF", *FACTORS.values()]].to_numpy(float)
    if not np.isfinite(required).all():
        msg = "The quarterly factor series is incomplete on the declared panel calendar."
        raise ValueError(msg)
    observed["excess"] = observed["total_return"] - observed["date"].map(factors["RF"])
    if not np.isfinite(observed["excess"].to_numpy(float)).all():
        msg = "An observed quarterly outcome is not finite."
        raise ValueError(msg)
    for term, source in FACTORS.items():
        observed[term] = observed["date"].map(factors[source])
    return observed.sort_values(["ticker", "date"]).reset_index(drop=True)


def _design_column(specification: str, term: str) -> str:
    return f"{specification}:{term}"


def _market_cell(quarter: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=quarter.year, month=3, day=31)


def prepare_sample(panel: Path, output: Path, params: Path) -> None:
    """Freeze period identities, common eligibility and all MM interaction designs."""
    inputs = load(panel, None, params)
    observed = _sample_frame(inputs)
    factors = inputs.factors
    output.mkdir(parents=True, exist_ok=True)
    exposures = []
    exposure_counts = {}
    with TemporaryDirectory(dir=output, prefix=".mm-") as directory:
        for specification, terms in FACTOR_SETS.items():
            estimates = _exposure_fit(
                observed, Path(directory), specification, terms, inputs.spec.min_beta_quarters
            )
            exposures.append(estimates)
            converged = estimates.loc[
                estimates["converged"].fillna(value=False).astype(bool)
                & np.isfinite(estimates["estimate"].to_numpy(float))
            ]
            exposure_counts[specification] = {
                "coefficients": len(converged),
                "issuers": int(converged["ticker"].nunique()),
            }
            for term in terms:
                estimates_by_issuer = converged.loc[converged["term"].eq(term)].set_index("ticker")
                observed[_design_column(specification, term)] = (
                    observed["ticker"].map(estimates_by_issuer["estimate"]) * observed[term]
                )
    columns = [
        _design_column(specification, term)
        for specification, terms in FACTOR_SETS.items()
        for term in terms
    ]
    quarters = []
    ledger = []
    for quarter in inputs.spec.panel_calendar:
        formation = _market_cell(quarter)
        rows = observed.loc[observed["date"].eq(quarter)].copy()
        formation_issuers = inputs.roster(formation)["issuer_id"].astype(str)
        formed = rows["ticker"].isin(formation_issuers)
        finite = np.isfinite(rows[columns].to_numpy(float)).all(axis=1)
        kept = rows.loc[formed & finite].rename(columns={"date": "quarter_date"})
        eligible = len(kept) > NEIGHBOURS
        ledger.append(
            {
                "quarter": quarter,
                "formation": formation,
                "roster": len(inputs.roster(quarter)),
                "formation_roster": len(formation_issuers),
                "observed": len(rows),
                "outside_formation": int((~formed).sum()),
                "missing_loadings": int((formed & ~finite).sum()),
                "retained": len(kept),
                "status": "available" if eligible else "too_few_issuers",
            }
        )
        if eligible:
            quarters.append(
                kept[["quarter_date", "ticker", "excess", *columns]].assign(
                    formation=formation,
                    market=float(factors.loc[[quarter], "Mkt-RF"].to_numpy(float)[0]),
                )
            )
    if not quarters:
        msg = "No quarters satisfy the common observed-return and factor loading mask."
        raise ValueError(msg)
    rows = pd.concat(quarters, ignore_index=True).sort_values(["quarter_date", "ticker"])
    atomic_parquet(output / "sample.parquet", rows)
    atomic_parquet(output / "exposures.parquet", pd.concat(exposures, ignore_index=True))
    atomic_parquet(output / "ledger.parquet", pd.DataFrame(ledger))
    write_json(
        output / "manifest.json",
        {
            "study_sha256": inputs.spec.experiment_digest(SAMPLE_SETTINGS),
            "panel_sha256": file_hash(panel / "manifest.json"),
            "artifacts": {
                name: file_hash(output / name)
                for name in ("sample.parquet", "exposures.parquet", "ledger.parquet")
            },
            "mask_sha256": digest_json(
                [
                    (str(date.date()), str(issuer))
                    for date, issuer in zip(rows["quarter_date"], rows["ticker"], strict=True)
                ]
            ),
            "factor_sets": FACTOR_SETS,
            "first_stage_counts": exposure_counts,
            "loading_estimator": (
                "issuer MM with intercept, separately for each declared factor set"
            ),
            "loading_window": "full observed quarterly panel; fixed in the conditional comparison",
            "minimum_issuer_quarters": inputs.spec.min_beta_quarters,
            "quarter_rows": "observed excess return, January formation member, all terms available",
        },
    )


def load_sample(sample: Path, params: Path, panel: Path | None = None) -> Sample:
    """Hash-check the fixed ordered sample before constructing any graph or design."""
    manifest = json.loads((sample / "manifest.json").read_text())
    spec = StudySpec.read(params)
    if manifest["study_sha256"] != spec.experiment_digest(SAMPLE_SETTINGS) or (
        panel is not None and manifest["panel_sha256"] != file_hash(panel / "manifest.json")
    ):
        msg = "Matched sample belongs to different study settings or prepared panel."
        raise ValueError(msg)
    for name in ("sample.parquet", "exposures.parquet", "ledger.parquet"):
        if file_hash(sample / name) != manifest["artifacts"][name]:
            msg = f"Matched sample checksum mismatch: {name}."
            raise ValueError(msg)
    table = pd.read_parquet(sample / "sample.parquet")
    quarters = []
    market = []
    masks = []
    for date, rows in table.groupby("quarter_date", sort=False):
        quarter = pd.Timestamp(str(date))
        formation = _market_cell(quarter)
        issuers = tuple(rows["ticker"].astype(str))
        masks.extend((str(quarter.date()), issuer) for issuer in issuers)
        if (
            len(issuers) <= NEIGHBOURS
            or len(set(issuers)) != len(issuers)
            or tuple(sorted(issuers)) != issuers
            or not rows["formation"].eq(formation).all()
            or not rows["market"].eq(rows["market"].iloc[0]).all()
            or quarter not in spec.panel_calendar
        ):
            msg = "Matched sample contains invalid quarterly identities."
            raise ValueError(msg)
        outcome = rows["excess"].to_numpy(float)
        design = {
            name: rows[[_design_column(name, term) for term in terms]].to_numpy(float)
            for name, terms in FACTOR_SETS.items()
        }
        if not np.isfinite(outcome).all() or not all(
            np.isfinite(matrix).all() for matrix in design.values()
        ):
            msg = "Matched sample contains a nonfinite outcome or factor interaction."
            raise ValueError(msg)
        quarters.append(SampleQuarter(quarter, formation, issuers, outcome, design))
        market.append(float(rows["market"].iloc[0]))
    dates = [item.quarter for item in quarters]
    if not dates or dates != sorted(dates) or digest_json(masks) != manifest["mask_sha256"]:
        msg = "Matched sample calendar is empty, inconsistent or not in declared order."
        raise ValueError(msg)
    return Sample(tuple(quarters), np.array(market), spec, manifest)


def compare(candidate: Fit, reference: Fit, orders: NDArray[np.int64]) -> dict[str, object]:
    """Paired stationary-quarter comparison conditional on point fits and loadings."""
    if candidate.contributions.shape != reference.contributions.shape or (
        candidate.observations != reference.observations
    ):
        msg = "Likelihood contributions require identical outcome calendars and sample sizes."
        raise ValueError(msg)
    gap = candidate.contributions - reference.contributions
    values = gap[orders].mean(axis=1)
    low, high, count = percentile_interval(values)
    return {
        "total_difference": float(gap.sum()),
        "mean_difference": float(gap.mean()),
        "low": low,
        "high": high,
        "draws": count,
        "attempted_draws": len(orders),
    }


def cell_manifest_hash(cell: Path, sample: Sample) -> str:
    """Bind each representation cell to the same prepared panel as the outcome sample."""
    manifest = cell / "manifest.json"
    if json.loads(manifest.read_text())["input_digest"] != sample.manifest["panel_sha256"]:
        msg = f"Representation cell {cell} belongs to a different prepared panel."
        raise ValueError(msg)
    return file_hash(manifest)


def fit_row(
    cell: str, process: Process, estimate: Fit | None, reason: str = ""
) -> dict[str, object]:
    """Serialize a fit or its recorded failure without dropping the cell."""
    if estimate is None:
        return {"cell": cell, "process": process, "status": "unavailable", "reason": reason}
    return {
        "cell": cell,
        "process": process,
        "status": "available",
        "reason": "",
        "coefficients": estimate.coefficients.tolist(),
        "spatial": estimate.spatial,
        "variance": estimate.variance,
        "log_likelihood": estimate.loglik,
        "observations": estimate.observations,
        "parameters": estimate.parameters,
        "aic": estimate.aic,
        "bic": estimate.bic,
        "lower_bound": estimate.lower,
        "upper_bound": estimate.upper,
        "boundary": estimate.boundary,
        "flat_profile": estimate.flat_profile,
        "profile_range": estimate.profile_range,
    }


def contribution_rows(cell: str, estimate: Fit, sample: Sample) -> list[dict[str, object]]:
    """Persist one full-data likelihood contribution for each matched quarter."""
    return [
        {
            "cell": cell,
            "process": estimate.process,
            "quarter": period.quarter,
            "log_likelihood": value,
        }
        for period, value in zip(sample.quarters, estimate.contributions, strict=True)
    ]


def orders_for(sample: Sample) -> tuple[NDArray[np.int64], float]:
    """Use one calendar resampling schedule in every matched analysis."""
    block = block_length(sample.market)
    return stationary_orders(
        len(sample.quarters), sample.spec.likelihood_draws, block, sample.spec.seed
    ), block


def fit_cell(
    cell: str, process: Process, periods: Sequence[Period], sample: Sample
) -> tuple[Fit | None, dict[str, object]]:
    """Treat missing quarters and numerical failures as unavailable cells."""
    if len(periods) != len(sample.quarters):
        return None, fit_row(cell, process, None, "missing matched quarters")
    try:
        estimate = fit(periods, process)
    except (ValueError, np.linalg.LinAlgError) as error:
        return None, fit_row(cell, process, None, str(error))
    return estimate, fit_row(cell, process, estimate)


def _periods(
    inputs: StudyInputs, sample: Sample, tabpfn: Path
) -> dict[tuple[str, str], list[Period]]:
    periods: dict[tuple[str, str], list[Period]] = {}
    for period in sample.quarters:
        formation = inputs.roster(period.formation).set_index("issuer_id", drop=False)
        roster = formation.loc[list(period.issuers)].reset_index(drop=True)
        direct, _ = characteristic_distances(inputs.histories(roster))["joint"]
        weights = {"direct_characteristics": knn_weights(direct, NEIGHBOURS)}
        state = load_cell(tabpfn, period.formation, period.issuers)
        if state is not None:
            weights["tabpfn_full"] = knn_weights(representation_distance(state), NEIGHBOURS)
        graphs = {name: prepare_graph(matrix) for name, matrix in weights.items()}
        for specification, design in period.design.items():
            periods.setdefault((specification, "none"), []).append(
                Period.of(period.outcome, design)
            )
            for name, graph in graphs.items():
                periods.setdefault((specification, name), []).append(
                    Period.of(period.outcome, design, graph)
                )
    return periods


def comparison_row(
    name: str,
    reference: str,
    process: Process,
    estimates: tuple[Fit | None, Fit | None],
    orders: NDArray[np.int64],
) -> dict[str, object]:
    """Serialize an available contrast or the reason it is unavailable."""
    candidate, baseline = estimates
    row = {"cell": name, "reference": reference, "process": process}
    if candidate is None or baseline is None:
        return {**row, "status": "unavailable", "reason": "missing point fit"}
    return {**row, "status": "available", **compare(candidate, baseline, orders)}


def write_results(
    output: Path,
    fits: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    contributions: list[dict[str, object]],
    manifest: dict[str, object],
) -> None:
    """Save analysis tables before writing the receipt that identifies their bytes."""
    output.mkdir(parents=True, exist_ok=True)
    artifacts = {}
    for name, rows in (
        ("fits.parquet", fits),
        ("comparisons.parquet", comparisons),
        ("contributions.parquet", contributions),
    ):
        atomic_parquet(output / name, pd.DataFrame(rows))
        artifacts[name] = file_hash(output / name)
    write_json(output / "manifest.json", {**manifest, "artifacts": artifacts})


def run(panel: Path, sample: Path, cells: Path, output: Path, params: Path) -> None:
    """Cross thirteen factor sets with no graph and two matched joint spatial graphs."""
    common = load_sample(sample, params, panel)
    orders, block = orders_for(common)
    tabpfn = cells / "fernandez" / "tabpfn_full"
    cell_hash = cell_manifest_hash(tabpfn, common)
    all_periods = _periods(load(panel, None, params), common, tabpfn)
    rows = []
    comparisons = []
    contributions = []
    estimates: dict[tuple[str, str, Process], Fit | None] = {}
    graph_processes: tuple[tuple[str, tuple[Process, ...]], ...] = (
        ("none", ("none",)),
        ("direct_characteristics", SPATIAL_PROCESSES),
        ("tabpfn_full", SPATIAL_PROCESSES),
    )
    for specification in FACTOR_SETS:
        baseline_name = f"{specification}|none"
        for graph, processes in graph_processes:
            name = f"{specification}|{graph}"
            periods = all_periods.get((specification, graph), [])
            for process in processes:
                estimate, row = fit_cell(name, process, periods, common)
                rows.append({**row, "factor_set": specification, "graph": graph})
                estimates[specification, graph, process] = estimate
                if estimate is not None:
                    contributions.extend(contribution_rows(name, estimate, common))
                if process != "none":
                    comparisons.append(
                        comparison_row(
                            name,
                            baseline_name,
                            process,
                            (estimate, estimates[specification, "none", "none"]),
                            orders,
                        )
                    )
                if graph == "tabpfn_full":
                    comparisons.append(
                        comparison_row(
                            name,
                            f"{specification}|direct_characteristics",
                            process,
                            (estimate, estimates[specification, "direct_characteristics", process]),
                            orders,
                        )
                    )
                if specification != "market":
                    comparisons.append(
                        comparison_row(
                            name,
                            f"market|{graph}",
                            process,
                            (estimate, estimates["market", graph, process]),
                            orders,
                        )
                    )
    write_results(
        output,
        rows,
        comparisons,
        contributions,
        {
            "sample_sha256": file_hash(sample / "manifest.json"),
            "mask_sha256": common.manifest["mask_sha256"],
            "tabpfn_cell_sha256": cell_hash,
            "factor_sets": FACTOR_SETS,
            "first_stage_counts": common.manifest["first_stage_counts"],
            "weights": "symmetrized 10-nearest-neighbour",
            "intercepts": "one per quarter",
            "parameters": (
                "design columns, quarter intercepts, variance, and spatial coefficient if fitted"
            ),
            "information_criteria": "conditional on first-stage issuer loadings and fixed graphs",
            "bootstrap": "stationary quarterly draws of paired point-fit likelihood contributions",
            "expected_block_quarters": block,
            "draws": len(orders),
            "seed": common.spec.seed,
        },
    )
