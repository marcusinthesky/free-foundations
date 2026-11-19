"""Matched spatial lag comparisons of three kernels on ten frozen geometries."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import TYPE_CHECKING, NamedTuple

import numpy as np
import pandas as pd

from free_foundations.artifacts.atomic import atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.matched_networks import kernel_weights
from free_foundations.methods.matched_panel import Period
from free_foundations.methods.moments import pairwise_spearman
from free_foundations.methods.networks import (
    CHARACTERISTICS,
    Network,
    characteristic_distances,
    representation_distance,
)
from free_foundations.study.experiments.inputs import load
from free_foundations.study.experiments.matched_panel import (
    cell_manifest_hash,
    compare,
    contribution_rows,
    fit_cell,
    fit_row,
    load_sample,
    orders_for,
)
from free_foundations.study.representations.matched import load_cell
from free_foundations.study.spec import file_hash

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.methods.matched_panel import Fit
    from free_foundations.study.experiments.inputs import StudyInputs
    from free_foundations.study.experiments.matched_panel import Sample, SampleQuarter

KERNELS = ("exp", "gaussian", "knn10")
GEOMETRIES = (*CHARACTERISTICS, "joint")
FAMILIES = ("direct", "tabpfn")


class GraphCell(NamedTuple):
    """One named geometry and weighting rule."""

    geometry: str
    family: str
    kernel: str

    @property
    def label(self) -> str:
        """Stable fit and evidence key."""
        return f"{self.geometry}:{self.family}|{self.kernel}"


@dataclass
class GridResults:
    """Fits, explicit failure reasons and per-quarter graph diagnostics."""

    fits: dict[GraphCell, Fit]
    failed: dict[GraphCell, str]
    diagnostics: list[dict[str, object]]


def _direct_distance(
    inputs: StudyInputs, rows: SampleQuarter, geometry: str
) -> tuple[np.ndarray, int]:
    roster = inputs.roster(rows.formation).set_index("issuer_id", drop=False)
    selected = roster.loc[list(rows.issuers)].reset_index(drop=True)
    histories = inputs.histories(selected)
    if geometry == "joint":
        return characteristic_distances(histories)[geometry]
    correlation = pairwise_spearman(histories[geometry])
    return correlation.distance, correlation.neutral_pairs


def _fit_geometry(
    sample: Sample, inputs: StudyInputs, cells: Path, geometry: str, family: str
) -> GridResults:
    cell_path = cells / ("fernandez" if geometry == "joint" else geometry) / "tabpfn_full"
    if family == "tabpfn":
        cell_manifest_hash(cell_path, sample)
    period_sets: dict[GraphCell, list[Period]] = {}
    unavailable: dict[GraphCell, str] = {}
    diagnostics: list[dict[str, object]] = []
    for rows in sample.quarters:
        if family == "direct":
            distance, neutral = _direct_distance(inputs, rows, geometry)
        else:
            values = load_cell(cell_path, rows.formation, rows.issuers)
            if values is None:
                for kernel in KERNELS:
                    unavailable[GraphCell(geometry, family, kernel)] = (
                        f"Encoder state unavailable for {rows.formation.date()}"
                    )
                break
            distance, neutral = representation_distance(values), 0
        pairs = distance[np.triu_indices(len(distance), 1)]
        for kernel in KERNELS:
            cell = GraphCell(geometry, family, kernel)
            graph, bandwidth = kernel_weights(distance, kernel)
            network = Network(
                cell.label, family, kernel, rows.issuers, graph, neutral_pairs=neutral
            )
            period = Period.of(rows.outcome, rows.design["market"], graph)
            period_sets.setdefault(cell, []).append(period)
            diagnostics.append(
                network.summary()
                | {
                    "cell": cell.label,
                    "quarter": rows.quarter,
                    "formation": rows.formation,
                    "bandwidth": bandwidth,
                    "zero_distances": int(np.sum(pairs == 0)),
                }
            )
    fits = {}
    for cell, periods in period_sets.items():
        if cell in unavailable:
            continue
        fitted, row = fit_cell(cell.label, "lag", periods, sample)
        if fitted is None:
            unavailable[cell] = str(row["reason"])
        else:
            fits[cell] = fitted
    return GridResults(fits, unavailable, diagnostics)


def _pairs() -> list[tuple[GraphCell, GraphCell]]:
    pairs = []
    for geometry in GEOMETRIES:
        pairs.extend(
            (GraphCell(geometry, "tabpfn", kernel), GraphCell(geometry, "direct", kernel))
            for kernel in KERNELS
        )
        pairs.extend(
            (GraphCell(geometry, family, candidate), GraphCell(geometry, family, reference))
            for family in FAMILIES
            for reference, candidate in combinations(KERNELS, 2)
        )
    return pairs


def run(panel: Path, sample: Path, cells: Path, output: Path, params: Path) -> None:
    """Compare every geometry and rule on identical quarterly market designs."""
    study = load_sample(sample, params, panel)
    inputs = load(panel, None, params)
    results = GridResults({}, {}, [])
    for geometry in GEOMETRIES:
        for family in FAMILIES:
            cell = _fit_geometry(study, inputs, cells, geometry, family)
            results.fits.update(cell.fits)
            results.failed.update(cell.failed)
            results.diagnostics.extend(cell.diagnostics)
    orders, block = orders_for(study)
    comparison_rows = []
    for candidate, reference in _pairs():
        left, right = results.fits.get(candidate), results.fits.get(reference)
        paired = (
            compare(left, right, orders)
            if left is not None and right is not None
            else {
                "total_difference": None,
                "gain_per_observation": None,
                "low_per_observation": None,
                "high_per_observation": None,
                "draws": 0,
                "attempted_draws": len(orders),
            }
        )
        comparison_rows.append(
            {
                "candidate": candidate.label,
                "cell": candidate.label,
                "reference": reference.label,
                "process": "lag",
                "status": "available" if left is not None and right is not None else "unavailable",
            }
            | paired
        )
    fit_rows = []
    contribution_records = []
    for geometry in GEOMETRIES:
        for family in FAMILIES:
            for kernel in KERNELS:
                cell = GraphCell(geometry, family, kernel)
                fitted = results.fits.get(cell)
                fit_rows.append(
                    fit_row(cell.label, "lag", fitted, results.failed.get(cell, ""))
                    | {"geometry": geometry, "family": family, "kernel": kernel}
                )
                if fitted is not None:
                    contribution_records.extend(contribution_rows(cell.label, fitted, study))
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").unlink(missing_ok=True)
    tables = {
        "fits.parquet": fit_rows,
        "comparisons.parquet": comparison_rows,
        "contributions.parquet": contribution_records,
        "graphs.parquet": results.diagnostics,
    }
    for filename, records in tables.items():
        atomic_parquet(output / filename, pd.DataFrame(records))
    write_json(
        output / "manifest.json",
        {
            "status": "partial" if results.failed else "complete",
            "sample": study.manifest,
            "process": "lag",
            "factor": "market",
            "stationary_block_length": block,
            "interval": "Paired stationary-quarter bootstrap given point fits and loadings",
            "cells": len(fit_rows),
            "failed": len(results.failed),
            "direct_distance": "Spearman chord by ratio history, root mean square for joint",
            "tabpfn_distance": "Chord distance on matched single-ratio or joint frozen states",
            "kernels": {
                "exp": "exp(-d)",
                "gaussian": "exp(-d²/(2h²)), h median positive off-diagonal distance",
                "knn10": "symmetric union, stable ordered-issuer tie break, binary affinities",
            },
            "normalization": "zero diagonal, row normalization after affinity/symmetrization",
            "coincidence": "zero-d pairs have unit dense affinity; all-coincident Gaussian uniform",
            "artifacts": {filename: file_hash(output / filename) for filename in tables},
        },
    )
