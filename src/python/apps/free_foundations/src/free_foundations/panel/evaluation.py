"""Matched financial forecasts for an explicit principal and diagnostic inventory."""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.fernandez.kernels import effective_neighbours, geometry, kernel_weights
from free_foundations.fernandez.models import paper_weights, symmetric_spectrum
from free_foundations.panel.likelihood import (
    block,
    correlation_only,
    fit,
    forecast_covariance,
    gaussian_daily,
)
from free_foundations.representations.representations import ARMS

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.panel.likelihood import Block
    from free_foundations.panel.observations import Annual

LOGGER = logging.getLogger(__name__)
CALIBRATION, EVALUATION = range(2016, 2020), range(2020, 2026)
JOINT = "fernandez_joint"
type Key = tuple[str, str]


def describe(name: str) -> dict[str, str]:
    """Stable labels for the retained histories, readouts and reference controls."""
    if "__" not in name:
        arm = "fernandez" if name.startswith("fernandez_") else "control"
        return {"history": "primary", "rung": "", "representation": name, "arm": arm}
    rung, representation = name.split("__", 1)
    return {
        "history": "primary",
        "rung": rung,
        "representation": representation,
        "arm": "calibrated" if rung.endswith("@decoded") else ARMS.get(representation, "control"),
    }


def sample_size(name: str) -> bool:
    """Sample-size curves use the principal fitted-innovation specification only."""
    return "@support" in name or "@calibration" in name


def digest(values: FloatArray) -> str:
    """Identify duplicate networks within one year's shared financial calculation."""
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


@dataclass
class Panel:
    """Calibration blocks and common-date scores for one declared study."""

    calibration: dict[Key, list[Block]] = field(default_factory=dict)
    intensities: dict[tuple[str, str, str], tuple[float, float]] = field(default_factory=dict)
    daily: dict[str, list[FloatArray]] = field(default_factory=dict)
    dates: list[str] = field(default_factory=list)
    geometry: list[dict[str, object]] = field(default_factory=list)
    annual: list[dict[str, object]] = field(default_factory=list)


def networks(distances: dict[str, FloatArray]) -> dict[Key, tuple[FloatArray, float]]:
    """Match learned distances to the original joint network's concentration."""
    target = effective_neighbours(paper_weights(distances[JOINT]))
    result: dict[Key, tuple[FloatArray, float]] = {}
    cached: dict[tuple[str, str], tuple[FloatArray, float]] = {}
    for name, distance in distances.items():
        kernel = "exp" if name.startswith("fernandez_") else "matched"
        identity = digest(distance), kernel
        if identity not in cached:
            cached[identity] = kernel_weights(distance, kernel, target=target)
        result[name, kernel] = cached[identity]
    firms = len(distances[JOINT])
    result["uniform_network", "none"] = (
        (np.ones((firms, firms)) - np.eye(firms)) / (firms - 1),
        0.0,
    )
    result["zero_network", "none"] = (np.zeros((firms, firms)), 0.0)
    return result


def update(panel: Panel, year: int, annual: Annual, distances: dict[str, FloatArray]) -> None:
    """Use each unique annual network once; names retain separate auditable results."""
    built = networks(distances)
    target = effective_neighbours(paper_weights(distances[JOINT]))
    for (name, kernel), (weights, bandwidth) in built.items():
        achieved = effective_neighbours(weights)
        matched = kernel == "matched"
        panel.geometry.append(
            {
                "year": year,
                "approach": name,
                "kernel": kernel,
                "bandwidth": bandwidth,
                "requested_neighbors": target if matched else None,
                "achieved_neighbors": achieved,
                "match_status": ("matched" if abs(achieved - target) < 1e-6 else "unattainable")
                if matched
                else "not_requested",
                **geometry(distances.get(name), weights),
            }
        )
    if year in CALIBRATION:
        cached: dict[str, Block] = {}
        for key, (weights, _) in built.items():
            identity = digest(weights)
            if identity not in cached:
                cached[identity] = block(annual.realized, weights)
            panel.calibration.setdefault(key, []).append(cached[identity])
        if year == CALIBRATION[-1]:
            calibrate(panel)
        return
    evaluate(panel, year, annual, built)


def calibrate(panel: Panel) -> None:
    """Freeze one spatial coefficient per network using 2016-2019 only."""
    fitted: dict[tuple[int, ...], tuple[float, float]] = {}
    for (name, kernel), blocks in panel.calibration.items():
        identity = tuple(id(item) for item in blocks)
        if name == "zero_network":
            result = (0.0, sum(item.score(0.0, "diagonal") for item in blocks))
        else:
            if identity not in fitted:
                fitted[identity] = fit(blocks, "diagonal")
            result = fitted[identity]
        panel.intensities[name, kernel, "diagonal"] = result
    LOGGER.info(
        "Calibrated %s networks (%s distinct fitted procedures)",
        len(panel.intensities),
        len(fitted),
    )


def evaluate(
    panel: Panel, year: int, annual: Annual, built: dict[Key, tuple[FloatArray, float]]
) -> None:
    """Score full returns; common marginals qualify the principal comparison."""
    values = annual.raw_realized - annual.raw_prior.mean(axis=0)
    panel.dates.extend(annual.dates)
    cached: dict[tuple[str, float], tuple[FloatArray, FloatArray | None]] = {}
    for (name, kernel), (weights, _) in built.items():
        intensity = panel.intensities[name, kernel, "diagonal"][0]
        identity = digest(weights), intensity
        needs_common = not sample_size(name)
        if identity not in cached or (needs_common and cached[identity][1] is None):
            previous = block(annual.prior, weights, symmetric_spectrum(weights))
            covariance = forecast_covariance(
                previous, weights, intensity, annual.factor_covariance, "diagonal"
            )
            diagonal = gaussian_daily(values, covariance)
            common = (
                gaussian_daily(values, correlation_only(covariance, annual.raw_prior))
                if needs_common
                else None
            )
            cached[identity] = diagonal, common
        diagonal, common = cached[identity]
        record(panel, f"{name}|{kernel}|diagonal", year, diagonal)
        if needs_common:
            if common is None:
                message = f"Missing common-marginal forecast: {name}"
                raise ValueError(message)
            record(panel, f"{name}|{kernel}|correlation", year, common)
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
    """Daily and annual records always refer to the same outcome dates."""
    panel.daily.setdefault(column, []).append(scores)
    panel.annual.append({"column": column, "year": year, "score": float(scores.sum())})


def daily_frame(panel: Panel) -> pd.DataFrame:
    """Days by scored columns, with strict common-length construction."""
    return pd.DataFrame(
        {column: np.concatenate(parts) for column, parts in panel.daily.items()},
        index=pd.Index(panel.dates, name="date"),
    )


def comparison(panel: Panel, daily: pd.DataFrame, firm_days: int) -> pd.DataFrame:
    """Scores, frozen coefficients, and a stable joint-reference gain."""
    rows = []
    for column in map(str, daily.columns):
        name, kernel, innovation = column.split("|")
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
    for arm, group in result.groupby("innovation"):
        reference = f"{JOINT}|exp|{'diagonal' if arm == 'control' else arm}"
        if reference in daily:
            result.loc[group.index, "gain_vs_joint_exp"] = group["heldout_log_likelihood"] - float(
                daily[reference].sum()
            )
    result["score_per_firm_day"] = result["heldout_log_likelihood"] / firm_days
    return result
