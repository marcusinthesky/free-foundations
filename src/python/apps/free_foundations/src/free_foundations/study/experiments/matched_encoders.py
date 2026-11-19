"""Rank encoders by gains over their matching direct-input spatial lag controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.matched_panel import Period
from free_foundations.methods.networks import knn_weights, representation_distance
from free_foundations.study.experiments.matched_panel import (
    NEIGHBOURS,
    RUNG_ORDER,
    cell_manifest_hash,
    comparison_row,
    contribution_rows,
    fit_cell,
    fit_row,
    load_sample,
    orders_for,
    write_results,
)
from free_foundations.study.representations.matched import load_cell
from free_foundations.study.spec import file_hash

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

    from free_foundations.methods.matched_panel import Fit, Process
    from free_foundations.study.experiments.matched_panel import Sample

TIE_TOLERANCE = 1e-8
PROCESSES: tuple[Process, ...] = ("lag", "error")


def _valid(estimate: Fit | None) -> bool:
    return (
        estimate is not None
        and not estimate.flat_profile
        and not estimate.boundary
        and np.isfinite(estimate.loglik)
        and estimate.observations > 0
    )


def select_winner(
    ranking: tuple[tuple[str, str], ...], estimates: Mapping[tuple[str, str], Fit | None]
) -> tuple[tuple[str, str], float] | None:
    """Require a complete valid grid, then rank gains in nats per observation."""
    gains: dict[tuple[str, str], float] = {}
    for identity in ranking:
        candidate = estimates.get(identity)
        direct = estimates.get((identity[0], "direct"))
        if (
            candidate is None
            or direct is None
            or not _valid(candidate)
            or not _valid(direct)
            or candidate.observations != direct.observations
        ):
            return None
        gains[identity] = (candidate.loglik - direct.loglik) / candidate.observations
    if not gains:
        return None
    best = max(gains.values())
    return next(
        (identity, gain) for identity, gain in gains.items() if best - gain <= TIE_TOLERANCE
    )


def _periods(cell: Path, sample: Sample) -> tuple[list[Period], str]:
    periods = []
    for period in sample.quarters:
        state = load_cell(cell, period.formation, period.issuers)
        if state is None:
            reason = f"representation unavailable for {period.formation.date()}"
            return [], reason
        try:
            weights = knn_weights(representation_distance(state), NEIGHBOURS)
            periods.append(Period.of(period.outcome, period.design["market"], weights))
        except (ValueError, np.linalg.LinAlgError) as error:
            return [], str(error)
    return periods, ""


def run(sample: Path, cells: Path, output: Path, params: Path) -> None:
    """Score each frozen encoder and every matching direct input control."""
    common = load_sample(sample, params)
    orders, block = orders_for(common)
    ranking = tuple((rung, model) for rung in RUNG_ORDER for model in common.spec.models)
    estimates: dict[Process, dict[tuple[str, str], Fit | None]] = {
        process: {} for process in PROCESSES
    }
    fits: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []
    contributions: list[dict[str, object]] = []
    cell_hashes: dict[str, str] = {}
    for rung in RUNG_ORDER:
        for model in ("direct", *common.spec.models):
            name = f"{rung}:{model}"
            cell = cells / rung / model
            cell_hashes[name] = cell_manifest_hash(cell, common)
            periods, reason = _periods(cell, common)
            for process in PROCESSES:
                estimate, row = (
                    (None, fit_row(name, process, None, reason))
                    if reason
                    else fit_cell(name, process, periods, common)
                )
                estimates[process][rung, model] = estimate
                fits.append({**row, "rung": rung, "model": model})
                if estimate is not None:
                    contributions.extend(contribution_rows(name, estimate, common))
                if model != "direct":
                    direct = estimates[process][rung, "direct"]
                    comparison = comparison_row(
                        name, f"{rung}:direct", process, (estimate, direct), orders
                    )
                    comparisons.append({**comparison, "contrast": "versus_direct_control"})
    winner = select_winner(ranking, estimates["lag"])
    selection: dict[str, object] = {
        "status": "unavailable",
        "reason": "selection requires available, interior and nonflat lag fits for the full grid",
        "sample_sha256": file_hash(sample / "manifest.json"),
        "mask_sha256": common.manifest["mask_sha256"],
        "analysis_formation": f"{common.spec.primary_formation + 1}-03-31",
        "endpoint": (
            "gain in in-sample market-adjusted quarterly lag log likelihood "
            "over the same-rung direct control, in nats per observation"
        ),
        "weighting": "symmetrized 10-nearest-neighbour",
        "tie_tolerance": TIE_TOLERANCE,
        "tie_order": ranking,
        "selection_sample": "same observations used for model fitting",
    }
    if winner is not None:
        (rung, model), gain = winner
        selection.update(
            {
                "status": "selected",
                "reason": "",
                "rung": rung,
                "model": model,
                "gain_per_observation": gain,
                "cell_sha256": cell_hashes[f"{rung}:{model}"],
            }
        )
    write_json(output / "selection.json", selection)
    write_results(
        output,
        fits,
        comparisons,
        contributions,
        {
            "sample_sha256": selection["sample_sha256"],
            "mask_sha256": selection["mask_sha256"],
            "cell_manifests": cell_hashes,
            "selection_endpoint": selection["endpoint"],
            "spatial_processes": PROCESSES,
            "bootstrap": "stationary quarterly draws of paired point-fit likelihood contributions",
            "expected_block_quarters": block,
            "draws": len(orders),
            "seed": common.spec.seed,
        },
        extra_artifacts={"selection.json": file_hash(output / "selection.json")},
    )
