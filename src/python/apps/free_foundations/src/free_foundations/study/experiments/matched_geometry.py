"""Dated PCoA, conditional attribution and matched spatial lag comparisons."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from free_foundations.artifacts.atomic import atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.methods.matched_networks import kernel_weights
from free_foundations.methods.matched_panel import Period, fit
from free_foundations.methods.networks import CHARACTERISTICS, representation_distance
from free_foundations.methods.pcoa import coordinate_distances, principal_coordinates
from free_foundations.study.experiments.inputs import load
from free_foundations.study.experiments.matched_factors import (
    compare,
    contribution_rows,
    fit_row,
    load_sample,
    orders_for,
)
from free_foundations.study.representations.matched import encode_cell, load_cell
from free_foundations.study.spec import file_hash

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.methods.matched_panel import Fit
    from free_foundations.methods.pcoa import Coordinates
    from free_foundations.study.experiments.inputs import StudyInputs
    from free_foundations.study.experiments.matched_factors import Sample

LEADING_AXES = 3
KERNEL = "knn10"


def _latest(history: np.ndarray) -> np.ndarray:
    valid = np.isfinite(history)
    present = valid.any(axis=1)
    latest = np.full(len(history), np.nan)
    reverse = valid[present, ::-1].argmax(axis=1)
    latest[present] = history[present, -1 - reverse]
    return latest


def _association(name: str, descriptor: np.ndarray, axes: np.ndarray) -> dict[str, object]:
    selected = np.isfinite(descriptor)
    y = rankdata(descriptor[selected])
    z = axes[selected]
    n = len(y)
    correlations: list[float | None] = [None] * LEADING_AXES
    r2 = None
    if n > z.shape[1] + 1 and np.ptp(y) > 0 and z.shape[1]:
        design = np.column_stack((np.ones(n), z))
        prediction = design @ np.linalg.lstsq(design, y, rcond=None)[0]
        r2 = float(1 - np.sum((y - prediction) ** 2) / np.sum((y - y.mean()) ** 2))
        for index, axis in enumerate(z.T):
            if np.ptp(axis) > 0:
                correlations[index] = float(spearmanr(axis, y).statistic)
    return {
        "descriptor": name,
        "n": n,
        **{f"spearman_pc{i + 1}": value for i, value in enumerate(correlations)},
        "leading_rank_r2": r2,
        "leading_axes": z.shape[1],
    }


def _descriptors(
    inputs: StudyInputs, rows: pd.DataFrame, quarter: pd.Timestamp, issuers: tuple[str, ...]
) -> dict[str, np.ndarray]:
    descriptors = {name: _latest(history) for name, history in inputs.histories(rows).items()}
    descriptors["formation_market_equity_usd"] = inputs.formation_equity(quarter.year - 1, issuers)
    for sic in sorted(rows["sic"].dropna().astype(str).str[:2].unique()):
        codes = rows["sic"].astype("string").str[:2]
        descriptors[f"sic2:{sic}"] = (
            codes.eq(sic).astype("Float64").to_numpy(float, na_value=np.nan)
        )
    return descriptors


def _tables(
    fit: Coordinates, issuers: tuple[str, ...], descriptors: dict[str, np.ndarray]
) -> dict[str, pd.DataFrame]:
    shares = np.full(len(fit.eigenvalues), np.nan)
    shares[: len(fit.shares)] = fit.shares
    leading = fit.coordinates[:, :LEADING_AXES]
    axes = {f"pc{i + 1}": axis for i, axis in enumerate(leading.T)}
    return {
        "spectrum": pd.DataFrame(
            {
                "coordinate": np.arange(1, len(shares) + 1),
                "eigenvalue": fit.eigenvalues,
                "positive_share": shares,
                "cumulative_positive_share": np.cumsum(shares),
            }
        ),
        "coordinates": pd.DataFrame({"issuer_id": issuers, **axes}),
        "associations": pd.DataFrame(
            [_association(name, values, leading) for name, values in descriptors.items()]
        ),
    }


def _write_geometry(
    inputs: StudyInputs,
    quarter: pd.Timestamp,
    output: Path,
    values: np.ndarray | None,
    *,
    historical: bool = False,
) -> dict[str, object]:
    rows = inputs.roster(quarter)
    issuers = tuple(rows["issuer_id"].astype(str))
    identity: dict[str, object] = {
        "quarter": quarter.strftime("%Y-%m-%d"),
        "n": len(issuers),
        "roster": "ordered analytical formation roster before outcome masking",
        "ordered_issuer_sha256": hashlib.sha256("\n".join(issuers).encode()).hexdigest(),
    }
    if values is None:
        return identity | {"status": "unavailable", "reason": "Dated encoder state unavailable"}
    distance = representation_distance(values)
    coordinates = principal_coordinates(distance)
    descriptors = (
        _descriptors(inputs, rows, quarter, issuers) if historical or coordinates.trigger else {}
    )
    tables = _tables(coordinates, issuers, descriptors)
    artifacts = {}
    prefix = "historical_ratio" if historical else "selected"
    for table, frame in tables.items():
        filename = f"{prefix}_{table}.parquet"
        atomic_parquet(output / filename, frame)
        artifacts[filename] = file_hash(output / filename)
    eigenvalues = coordinates.eigenvalues
    negative = eigenvalues[eigenvalues < -coordinates.tolerance]
    return identity | {
        "status": "complete",
        "scope": "historical ratio geometry" if historical else "selected financial geometry",
        "positive_inertia_shares": coordinates.shares[:LEADING_AXES].tolist(),
        "cumulative_positive_inertia_shares": np.cumsum(coordinates.shares[:LEADING_AXES]).tolist(),
        "eigenvalues_first_5": eigenvalues[:5].tolist(),
        "positive_count": len(coordinates.shares),
        "negative_count": len(negative),
        "negative_absolute_inertia": float(-negative.sum()),
        "tolerance": coordinates.tolerance,
        "distance_sha256": hashlib.sha256(distance.tobytes()).hexdigest(),
        "embedding_sha256": hashlib.sha256(values.tobytes()).hexdigest(),
        "trigger": coordinates.trigger if not historical else None,
        "artifacts": artifacts,
    }


def run(panel: Path, selection: Path, cells: Path, output: Path, params: Path) -> None:
    """Produce the selected financial formation geometry and interpretation gate."""
    inputs = load(panel, None, params)
    selected = json.loads(selection.read_text())
    quarter = pd.Timestamp(year=inputs.spec.primary_formation + 1, month=3, day=31)
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").unlink(missing_ok=True)
    geometry = {"status": "unavailable", "reason": "No qualified financial winner"}
    if selected["status"] == "selected":
        path = cells / selected["rung"] / selected["model"]
        if selected["analysis_formation"] != quarter.strftime("%Y-%m-%d") or selected[
            "cell_sha256"
        ] != file_hash(path / "manifest.json"):
            msg = "Selection does not match the declared interpretation date and encoder cell."
            raise ValueError(msg)
        issuers = tuple(inputs.roster(quarter)["issuer_id"].astype(str))
        values = load_cell(path, quarter, issuers)
        geometry = _write_geometry(inputs, quarter, output, values) | {
            "rung": selected["rung"],
            "model": selected["model"],
            "cell_manifest_sha256": selected["cell_sha256"],
            "sample_sha256": selected["sample_sha256"],
            "mask_sha256": selected["mask_sha256"],
        }
    write_json(
        output / "manifest.json",
        {
            "status": geometry["status"],
            "selection_sha256": file_hash(selection),
            "panel_manifest_sha256": file_hash(panel / "manifest.json"),
            "positive_inertia_gate": {"statistic": "PC1 share", "operator": ">", "threshold": 0.25},
            "selected": geometry,
            "interpretation": "Dated descriptive associations, with no causal or pricing claims",
        },
    )


def historical(panel: Path, representations: Path, output: Path, params: Path) -> None:
    """Verify the archived January 2016 TabPFN geometry used in the workshop exhibit."""
    inputs = load(panel, representations, params)
    if inputs.store is None:
        msg = "Historical geometry requires a verified archived representation store."
        raise ValueError(msg)
    quarter = pd.Timestamp("2016-03-31")
    issuers = tuple(inputs.roster(quarter)["issuer_id"].astype(str))
    values = inputs.store.states(quarter, issuers, rung="fernandez").get("fernandez:tabpfn_full")
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").unlink(missing_ok=True)
    exhibit = _write_geometry(inputs, quarter, output, values, historical=True)
    metadata = {
        "panel_manifest_sha256": file_hash(panel / "manifest.json"),
        "representation_manifest_sha256": file_hash(representations / "manifest.json"),
        "rung": "fernandez",
        "model": "tabpfn_full",
        "interpretation": "Historical descriptive associations on the analytical formation roster",
    }
    if values is not None:
        state, digest = inputs.store.state_file(quarter, "fernandez")
        metadata |= {"state_path": state, "state_sha256": digest}
    write_json(output / "manifest.json", exhibit | metadata)


@dataclass
class ComparisonFit:
    """One fixed-cohort lag fit and its neighbour overlap with the baseline."""

    fitted: Fit | None
    reason: str
    overlap: list[dict[str, object]]


def _conditional_fits(
    study: Sample, baseline: Path, cell: Path, views: dict[str, int]
) -> dict[str, ComparisonFit]:
    periods: dict[str, list[Period]] = {label: [] for label in views}
    overlap: dict[str, list[dict[str, object]]] = {label: [] for label in views}
    failures: dict[str, str] = {}
    for rows in study.quarters:
        original = load_cell(baseline, rows.formation, rows.issuers)
        candidate = original if cell == baseline else load_cell(cell, rows.formation, rows.issuers)
        if original is None or candidate is None:
            reason = f"State unavailable for {rows.formation.date()}"
            return {label: ComparisonFit(None, reason, overlap[label]) for label in views}
        original_distance = representation_distance(original)
        distance = original_distance if cell == baseline else representation_distance(candidate)
        axes = principal_coordinates(distance).coordinates if any(views.values()) else None
        original_graph = kernel_weights(original_distance, KERNEL)[0]
        for label, count in views.items():
            if label in failures:
                continue
            selected_axes = axes[:, :count] if count and axes is not None else None
            if selected_axes is not None and not selected_axes.shape[1]:
                failures[label] = f"No positive axes for {rows.formation.date()}"
                continue
            projected = distance if selected_axes is None else coordinate_distances(selected_axes)
            graph = (
                original_graph
                if cell == baseline and not count
                else kernel_weights(projected, KERNEL)[0]
            )
            union = np.count_nonzero((original_graph > 0) | (graph > 0), axis=1)
            intersection = np.count_nonzero((original_graph > 0) & (graph > 0), axis=1)
            overlap[label].append(
                {
                    "cell": label,
                    "quarter": rows.quarter,
                    "formation": rows.formation,
                    "mean_peer_jaccard": float(np.mean(intersection / union)),
                    "n": len(rows.issuers),
                    "positive_axes_used": None if selected_axes is None else selected_axes.shape[1],
                }
            )
            periods[label].append(Period.of(rows.outcome, rows.design["market"], graph))
    results = {}
    for label, period in periods.items():
        reason = failures.get(label, "")
        fitted = None
        if not reason:
            try:
                fitted = fit(period, "lag")
            except (ValueError, FloatingPointError, np.linalg.LinAlgError) as error:
                reason = str(error)
        results[label] = ComparisonFit(fitted, reason, overlap[label])
    return results


@dataclass(frozen=True)
class AblationInputs:
    """Locations required for re-encoding a selected cell."""

    contexts: Path
    weights: Path
    cache: Path
    output: Path
    params: Path
    device: str


def _ablation_results(
    study: Sample, baseline: Path, selected: dict[str, Any], paths: AblationInputs
) -> tuple[dict[str, ComparisonFit], list[dict[str, str]]]:
    results = _conditional_fits(
        study, baseline, baseline, {"full": 0, "pc1": 1, "top_three": LEADING_AXES}
    )
    omissions: list[dict[str, str]] = []
    for group in CHARACTERISTICS:
        label = f"omit:{group}"
        cell = paths.output / "encoded" / group
        encode_cell(
            paths.contexts,
            paths.weights,
            paths.cache,
            cell,
            paths.params,
            rung=selected["rung"],
            model=selected["model"],
            omit=group,
            device=paths.device,
        )
        results.update(_conditional_fits(study, baseline, cell, {label: 0}))
        omissions.append(
            {
                "group": group,
                "status": "available" if results[label].fitted else "unavailable",
                "cell_manifest_sha256": file_hash(cell / "manifest.json"),
            }
        )
    return results, omissions


def ablate(  # noqa: PLR0913, PLR0917 -- explicit DVC inputs, outputs and execution device.
    panel: Path,
    sample: Path,
    selection: Path,
    geometry: Path,
    contexts: Path,
    cells: Path,
    weights: Path,
    cache: Path,
    output: Path,
    params: Path,
    *,
    device: str = "cuda",
) -> None:
    """Only re-encode after a verified above-threshold PCoA decision."""
    manifest_path = geometry / "manifest.json"
    decision = json.loads(manifest_path.read_text())
    selection_sha = file_hash(selection)
    if decision["selection_sha256"] != selection_sha or decision[
        "panel_manifest_sha256"
    ] != file_hash(panel / "manifest.json"):
        msg = "PCoA decision and selected cell do not share the study identity."
        raise ValueError(msg)
    output.mkdir(parents=True, exist_ok=True)
    (output / "manifest.json").unlink(missing_ok=True)
    identity: dict[str, object] = {
        "selection_sha256": selection_sha,
        "geometry_sha256": file_hash(manifest_path),
    }
    if decision["status"] != "complete" or not decision["selected"]["trigger"]:
        status = "not_triggered" if decision["status"] == "complete" else "unavailable"
        write_json(output / "manifest.json", identity | {"status": status})
        return
    selected = json.loads(selection.read_text())
    if selected["sample_sha256"] != file_hash(sample / "manifest.json"):
        msg = "Selected fit and ablation do not share a common sample."
        raise ValueError(msg)
    baseline = cells / selected["rung"] / selected["model"]
    if file_hash(baseline / "manifest.json") != decision["selected"]["cell_manifest_sha256"]:
        msg = "Selected encoder cell changed after the PCoA decision."
        raise ValueError(msg)
    study = load_sample(sample, params, panel)
    if selected["mask_sha256"] != study.manifest["mask_sha256"]:
        msg = "Selected fit and ablation do not share the same outcome mask."
        raise ValueError(msg)
    paths = AblationInputs(contexts, weights, cache, output, params, device)
    results, omissions = _ablation_results(study, baseline, selected, paths)
    omission_scope = (
        "Mapped underlying fiscal operand histories"
        if selected["rung"] == "operands"
        else "Engineered ratio histories; any broad XBRL facts remain available"
    )
    _write_ablation(
        output,
        results,
        study,
        identity | {"omissions": omissions, "omission_scope": omission_scope},
    )


def _write_ablation(
    output: Path,
    results: dict[str, ComparisonFit],
    study: Sample,
    identity: dict[str, object],
) -> None:
    orders, block = orders_for(study)
    reference = results["full"].fitted
    fits = []
    comparisons = []
    contributions = []
    overlaps = []
    for label, result in results.items():
        fits.append(fit_row(label, "lag", result.fitted, result.reason))
        overlaps.extend(result.overlap)
        if result.fitted is not None:
            contributions.extend(contribution_rows(label, result.fitted, study))
        if label != "full":
            paired = reference is not None and result.fitted is not None
            comparison = {
                "candidate": label,
                "cell": label,
                "reference": "full",
                "process": "lag",
                "status": "available" if paired else "unavailable",
            }
            if reference is not None and result.fitted is not None:
                comparison |= compare(result.fitted, reference, orders)
            comparisons.append(comparison)
    tables = {
        "fits.parquet": fits,
        "comparisons.parquet": comparisons,
        "contributions.parquet": contributions,
        "peer_overlap.parquet": overlaps,
    }
    for filename, records in tables.items():
        atomic_parquet(output / filename, pd.DataFrame(records))
    write_json(
        output / "manifest.json",
        identity
        | {
            "status": "complete"
            if all(result.fitted is not None for result in results.values())
            else "partial",
            "sample": study.manifest,
            "leading_coordinates": LEADING_AXES,
            "top_three_rank_rule": "use all positive axes when fewer than three exist",
            "stationary_block_length": block,
            "process": "lag",
            "factor": "market",
            "kernel": KERNEL,
            "interval": "Paired stationary-quarter bootstrap given point fits and loadings",
            "artifacts": {filename: file_hash(output / filename) for filename in tables},
        },
    )
