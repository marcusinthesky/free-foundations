"""Shared sample and financial comparison contracts for the matched experiments."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.artifacts.atomic import atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.inference import block_length, percentile_interval, stationary_orders
from free_foundations.methods.matched_panel import Fit, Period, Process, fit
from free_foundations.study.spec import StudySpec, digest_json, file_hash

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

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


def _design_column(specification: str, term: str) -> str:
    return f"{specification}:{term}"


def _market_cell(quarter: pd.Timestamp) -> pd.Timestamp:
    return pd.Timestamp(year=quarter.year, month=3, day=31)


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
        not np.array_equal(candidate.period_sizes, reference.period_sizes)
    ):
        msg = "Likelihood contributions require identical outcome calendars and sample sizes."
        raise ValueError(msg)
    gap = candidate.contributions - reference.contributions
    values = gap[orders].sum(axis=1) / candidate.period_sizes[orders].sum(axis=1)
    low, high, count = percentile_interval(values)
    return {
        "total_difference": float(gap.sum()),
        "gain_per_observation": float(gap.sum() / candidate.observations),
        "low_per_observation": low,
        "high_per_observation": high,
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
            "observations": len(period.issuers),
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


def write_results(  # noqa: PLR0913 -- explicit stage artifacts.
    output: Path,
    fits: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    contributions: list[dict[str, object]],
    manifest: dict[str, object],
    *,
    extra_artifacts: dict[str, str] | None = None,
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
    write_json(
        output / "manifest.json", {**manifest, "artifacts": (extra_artifacts or {}) | artifacts}
    )
