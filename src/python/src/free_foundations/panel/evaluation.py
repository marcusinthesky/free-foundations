"""Calibrate one coefficient per network, kernel and innovation arm; score later years."""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.representations import ARMS
from free_foundations.fernandez.kernels import (
    KERNELS,
    Kernel,
    effective_neighbours,
    geometry,
    kernel_weights,
    placebo,
    size_groups,
)
from free_foundations.fernandez.models import paper_weights, symmetric_spectrum
from free_foundations.panel.likelihood import (
    INNOVATIONS,
    block,
    correlation_only,
    fit,
    forecast_covariance,
    gaussian_daily,
)
from free_foundations.panel.networks import ASSETS

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.panel.likelihood import Block, Innovations
    from free_foundations.panel.observations import Annual

LOGGER = logging.getLogger(__name__)
CALIBRATION, EVALUATION = range(2016, 2020), range(2020, 2026)
JOINT = "fernandez_joint"
PLACEBO_DRAWS = 19
# Prespecified placebo rows: the joint benchmark, direct input, PCA, one model per arm.
PLACEBO_ROWS = (
    JOINT,
    "histories__direct",
    "histories__pca16",
    "histories__tabpfn_full__late",
    "histories__tabfm__early_concat",
)
type Key = tuple[str, str]


def describe(name: str) -> dict[str, str]:
    """History prefix, rung/target label, representation and interpretive arm."""
    match = re.match(r"(h\d+)__(.*)", name)
    history, rest = (match.group(1), match.group(2)) if match else ("primary", name)
    rest = rest.split("__placebo")[0]
    if rest.startswith("fernandez") or rest in {"uniform_network", "zero_network"}:
        arm = "reference" if rest in {"uniform_network", "zero_network"} else "fernandez"
        return {"history": history, "rung": "", "representation": rest, "arm": arm}
    if "__" not in rest:
        return {"history": history, "rung": "", "representation": rest, "arm": "control"}
    rung, representation = rest.split("__", 1)
    return {
        "history": history,
        "rung": rung,
        "representation": representation,
        "arm": "calibrated" if rung.endswith("@decoded") else ARMS[representation],
    }


@dataclass
class Panel:
    """Accumulated calibration statistics and held-out daily densities for one design."""

    kernels: tuple[Kernel, ...] = KERNELS
    include_placebos: bool = True
    diagonal_only: bool = False
    calibration: dict[Key, list[Block]] = field(default_factory=dict)
    intensities: dict[tuple[str, str, str], tuple[float, float]] = field(default_factory=dict)
    daily: dict[str, list[FloatArray]] = field(default_factory=dict)
    dates: list[str] = field(default_factory=list)
    geometry: list[dict[str, float | str | int]] = field(default_factory=list)
    annual: list[dict[str, float | str | int]] = field(default_factory=list)
    own: dict[Key, list[FloatArray]] = field(default_factory=dict)
    attribution: list[dict[str, float | str | int]] = field(default_factory=list)


def attribute(
    item: Block, own: FloatArray, intensity: float, variances: FloatArray
) -> dict[str, float]:
    """Exact split of the residual spatial-error log-likelihood (Lean `Likelihood`).

    With filtered second moments m = second - 2 lambda cross + lambda^2 spatial and the
    spatial term split into the Herfindahl-weighted own second moments sum_j W_ij^2 s_j
    and the cross products, the five parts sum to ``Block.score``. This is the residual
    likelihood given realized factors, not the unconditional score. ``s_j`` is the total
    residual second moment, common and idiosyncratic together, so ``concentration_own`` is
    not the idiosyncratic-noise term eta of the common-plus-noise model, and
    ``alignment`` measures weighted residual cross products, not recovered exposures.
    """
    days = item.days
    return {
        "spectrum": days * float(np.log(np.abs(1 - intensity * item.eigenvalues)).sum()),
        "variance": -0.5 * days * float(np.log(2 * np.pi * variances).sum()),
        "baseline": -0.5 * days * float(np.sum(item.second / variances)),
        "alignment": days * intensity * float(np.sum(item.cross / variances)),
        "concentration_own": -0.5 * days * intensity**2 * float(np.sum(own / variances)),
        "concentration_cross": -0.5
        * days
        * intensity**2
        * float(np.sum((item.spatial - own) / variances)),
    }


def own_variance(weights: FloatArray, item: Block) -> FloatArray:
    """sum_j W_ij^2 s_j: the spatial term's part from neighbours' own total second moments."""
    return (weights**2) @ item.second


def networks(
    distances: dict[str, FloatArray],
    groups: FloatArray,
    year: int,
    *,
    kernels: tuple[Kernel, ...] = KERNELS,
    include_placebos: bool = True,
) -> dict[Key, tuple[FloatArray, float]]:
    """Every distance under each kernel; matched kernels copy the joint benchmark's spread."""
    target = effective_neighbours(paper_weights(distances[JOINT]))
    result: dict[Key, tuple[FloatArray, float]] = {}
    for name, distance in distances.items():
        for kernel in kernels:
            result[name, kernel] = kernel_weights(distance, kernel, target=target)
    result[JOINT, "exp"] = (paper_weights(distances[JOINT]), 1.0)
    firms = len(groups)
    result["uniform_network", "none"] = (
        (np.ones((firms, firms)) - np.eye(firms)) / (firms - 1),
        0.0,
    )
    result["zero_network", "none"] = (np.zeros((firms, firms)), 0.0)
    for name in PLACEBO_ROWS if include_placebos else ():
        if name in distances:
            weights = result[name, "exp"][0]
            for draw in range(PLACEBO_DRAWS):
                result[f"{name}__placebo{draw}", "exp"] = (
                    placebo(weights, groups, seed=year * 100 + draw),
                    1.0,
                )
    return result


def innovations_for(name: str) -> tuple[Innovations, ...]:
    """Placebos use the matched heterogeneous-variance arm only."""
    return ("diagonal",) if "__placebo" in name else INNOVATIONS


def update(
    panel: Panel,
    year: int,
    annual: Annual,
    distances: dict[str, FloatArray],
    broad: pd.DataFrame,
) -> None:
    """Add one year's calibration blocks or held-out daily log densities."""
    assets = broad[ASSETS].reindex(pd.MultiIndex.from_product([[year - 1], annual.tickers]))
    groups = size_groups(np.log(assets.where(assets > 0).to_numpy(dtype=float)))
    built = networks(
        distances, groups, year, kernels=panel.kernels, include_placebos=panel.include_placebos
    )
    for (name, kernel), (weights, bandwidth) in built.items():
        if "__placebo" not in name:
            panel.geometry.append(
                {"year": year, "approach": name, "kernel": kernel, "bandwidth": bandwidth}
                | geometry(distances.get(name), weights)
            )
    if year in CALIBRATION:
        for key, (weights, _) in built.items():
            item = block(annual.realized, weights)
            panel.calibration.setdefault(key, []).append(item)
            panel.own.setdefault(key, []).append(own_variance(weights, item))
        if year == CALIBRATION[-1]:
            calibrate(panel)
        return
    evaluate(panel, year, annual, built)


def evaluate(
    panel: Panel, year: int, annual: Annual, built: dict[Key, tuple[FloatArray, float]]
) -> None:
    """Score one held-out year for every network and the nonspatial controls."""
    values = annual.raw_realized - annual.raw_prior.mean(axis=0)
    panel.dates.extend(annual.dates)
    for (name, kernel), (weights, _) in built.items():
        previous = block(annual.prior, weights, symmetric_spectrum(weights))
        realized = block(annual.realized, weights, previous.eigenvalues)
        for innovation in ("diagonal",) if panel.diagonal_only else innovations_for(name):
            intensity = panel.intensities[name, kernel, innovation][0]
            if "__placebo" not in name:
                panel.attribution.append(
                    {
                        "approach": name,
                        "kernel": kernel,
                        "innovation": innovation,
                        "year": year,
                        "lambda": intensity,
                    }
                    | attribute(
                        realized,
                        own_variance(weights, realized),
                        intensity,
                        previous.variances(intensity, innovation),
                    )
                )
            covariance = forecast_covariance(
                previous, weights, intensity, annual.factor_covariance, innovation
            )
            record(panel, f"{name}|{kernel}|{innovation}", year, gaussian_daily(values, covariance))
            if innovation == "diagonal" and "__placebo" not in name:
                record(
                    panel,
                    f"{name}|{kernel}|correlation",
                    year,
                    gaussian_daily(values, correlation_only(covariance, annual.raw_prior)),
                )
    factor = annual.factor_covariance
    controls = {
        "raw_sample_covariance": np.cov(annual.raw_prior, rowvar=False),
        "ff5_mom_diagonal": factor + np.diag(np.mean(annual.prior**2, axis=0)),
        "ff5_mom_sample_residual_covariance": factor + np.cov(annual.prior, rowvar=False),
    }
    for name, covariance in controls.items():
        record(panel, f"{name}|none|control", year, gaussian_daily(values, covariance))
        record(
            panel,
            f"{name}|none|correlation",
            year,
            gaussian_daily(values, correlation_only(covariance, annual.raw_prior)),
        )


def record(panel: Panel, column: str, year: int, scores: FloatArray) -> None:
    """Store daily densities and the annual total for one scored column."""
    panel.daily.setdefault(column, []).append(scores)
    panel.annual.append({"column": column, "year": year, "score": float(scores.sum())})


def calibrate(panel: Panel) -> None:
    """One coefficient per network, kernel and innovation arm, from 2016-2019 only."""
    for (name, kernel), blocks in panel.calibration.items():
        for innovation in ("diagonal",) if panel.diagonal_only else innovations_for(name):
            if name == "zero_network":
                value = sum(item.score(0.0, innovation) for item in blocks)
                panel.intensities[name, kernel, innovation] = (0.0, value)
            else:
                panel.intensities[name, kernel, innovation] = fit(blocks, innovation)
            if "__placebo" in name:
                continue
            intensity = panel.intensities[name, kernel, innovation][0]
            for year, item, own in zip(CALIBRATION, blocks, panel.own[name, kernel], strict=True):
                panel.attribution.append(
                    {
                        "approach": name,
                        "kernel": kernel,
                        "innovation": innovation,
                        "year": year,
                        "lambda": intensity,
                    }
                    | attribute(item, own, intensity, item.variances(intensity, innovation))
                )
    LOGGER.info("Calibrated %s coefficients", len(panel.intensities))


def daily_frame(panel: Panel) -> pd.DataFrame:
    """Days by scored columns; every column covers exactly the same observed dates."""
    return pd.DataFrame(
        {column: np.concatenate(parts) for column, parts in panel.daily.items()},
        index=pd.Index(panel.dates, name="date"),
    )


def comparison(panel: Panel, daily: pd.DataFrame, firm_days: int) -> pd.DataFrame:
    """One row per network, kernel and innovation arm with calibration and held-out fit."""
    rows = []
    for column in map(str, daily.columns):
        name, kernel, innovation = column.split("|")
        if "__placebo" in name:
            continue
        lookup = "diagonal" if innovation == "correlation" else innovation
        intensity, calibration = panel.intensities.get((name, kernel, lookup), (np.nan, np.nan))
        rows.append(
            {
                "approach": name,
                "kernel": kernel,
                "innovation": innovation,
                **describe(name),
                "lambda": intensity,
                "calibration_ml_log_likelihood": calibration,
                "heldout_log_likelihood": float(daily[column].sum()),
                "firm_days": firm_days,
                "boundary": bool(abs(intensity) >= 0.985) if np.isfinite(intensity) else False,
            }
        )
    result = pd.DataFrame(rows)
    for _, group in result.groupby("innovation"):
        reference = group.loc[group["approach"].eq(JOINT) & group["kernel"].eq("exp")]
        if not reference.empty:
            result.loc[group.index, "gain_vs_joint_exp"] = group["heldout_log_likelihood"] - float(
                reference["heldout_log_likelihood"].iloc[0]
            )
    result["score_per_firm_day"] = result["heldout_log_likelihood"] / firm_days
    return result


def placebo_table(daily: pd.DataFrame) -> pd.DataFrame:
    """Held-out score of each prespecified network against its label-permuted placebos."""
    rows = []
    for name in PLACEBO_ROWS:
        column = f"{name}|exp|diagonal"
        if column not in daily:
            continue
        draws = np.array(
            [daily[f"{name}__placebo{draw}|exp|diagonal"].sum() for draw in range(PLACEBO_DRAWS)]
        )
        observed = float(daily[column].sum())
        rows.append(
            {
                "approach": name,
                "observed": observed,
                "placebo_mean": float(draws.mean()),
                "placebo_max": float(draws.max()),
                "rank_p_value": (1 + int((draws >= observed).sum())) / (PLACEBO_DRAWS + 1),
            }
        )
    return pd.DataFrame(rows)
