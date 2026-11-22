"""Rank encoders by gains over their matching direct-input spatial lag controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.matched_panel import Period, prepare_graph
from free_foundations.methods.networks import knn_weights, representation_distance
from free_foundations.study.experiments.matched_panel import (
    FACTOR_SETS,
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
BROAD_FACTOR_SETS = ("market", "ff5", "ff5_mom")


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


def _periods(
    cell: Path, sample: Sample, factor_sets: tuple[str, ...]
) -> tuple[dict[str, list[Period]], str]:
    periods: dict[str, list[Period]] = {name: [] for name in factor_sets}
    for period in sample.quarters:
        state = load_cell(cell, period.formation, period.issuers)
        if state is None:
            reason = f"representation unavailable for {period.formation.date()}"
            return {}, reason
        try:
            weights = knn_weights(representation_distance(state), NEIGHBOURS)
            graph = prepare_graph(weights)
            for specification in factor_sets:
                periods[specification].append(
                    Period.of(period.outcome, period.design[specification], graph)
                )
        except ValueError as error:
            return {}, str(error)
    return periods, ""


def run(sample: Path, cells: Path, output: Path, params: Path) -> None:
    """Keep market-only selection and test the broad TabPFN pair under richer controls."""
    common = load_sample(sample, params)
    orders, block = orders_for(common)
    ranking = tuple((rung, model) for rung in RUNG_ORDER for model in common.spec.models)
    estimates: dict[tuple[str, str, str, Process], Fit | None] = {}
    fits: list[dict[str, object]] = []
    comparisons: list[dict[str, object]] = []
    contributions: list[dict[str, object]] = []
    cell_hashes: dict[str, str] = {}
    for rung in RUNG_ORDER:
        for model in ("direct", *common.spec.models):
            identity = f"{rung}:{model}"
            cell = cells / rung / model
            cell_hashes[identity] = cell_manifest_hash(cell, common)
            factor_sets = (
                BROAD_FACTOR_SETS
                if rung == "standard_xbrl" and model in ("direct", "tabpfn_full")
                else ("market",)
            )
            periods, reason = _periods(cell, common, factor_sets)
            for specification in factor_sets:
                prefix = "" if specification == "market" else f"{specification}|"
                name = f"{prefix}{identity}"
                metadata = {"factor_set": specification, "rung": rung, "model": model}
                for process in PROCESSES:
                    estimate, row = (
                        (None, fit_row(name, process, None, reason))
                        if reason
                        else fit_cell(name, process, periods[specification], common)
                    )
                    estimates[specification, rung, model, process] = estimate
                    fits.append({**row, **metadata})
                    if estimate is not None:
                        contributions.extend(
                            {**contribution, **metadata}
                            for contribution in contribution_rows(name, estimate, common)
                        )
                    if model != "direct":
                        direct = estimates[specification, rung, "direct", process]
                        comparison = comparison_row(
                            name, f"{prefix}{rung}:direct", process, (estimate, direct), orders
                        )
                        comparisons.append(
                            {**comparison, **metadata, "contrast": "versus_direct_control"}
                        )
    market_lag_estimates = {
        (rung, model): estimate
        for (specification, rung, model, process), estimate in estimates.items()
        if specification == "market" and process == "lag"
    }
    winner = select_winner(ranking, market_lag_estimates)
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
            "broad_factor_comparison": {
                "rung": "standard_xbrl",
                "candidate": "tabpfn_full",
                "reference": "direct",
                "factor_sets": {name: FACTOR_SETS[name] for name in BROAD_FACTOR_SETS},
                "sample": "same ordered issuer-quarters, outcomes and graphs for every control",
                "selection": "fixed TabPFN comparison; market-only encoder selection is unchanged",
            },
            "weighting": "symmetrized 10-nearest-neighbour",
            "spatial_processes": PROCESSES,
            "bootstrap": "stationary quarterly draws of paired point-fit likelihood contributions",
            "expected_block_quarters": block,
            "draws": len(orders),
            "seed": common.spec.seed,
        },
        extra_artifacts={"selection.json": file_hash(output / "selection.json")},
    )
