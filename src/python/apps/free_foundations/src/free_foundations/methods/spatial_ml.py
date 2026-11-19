"""Fast fixed-graph refits for resampling, checked against statadic on every sample.

The study's point estimates, information covariances and diagnostics come from
statadic. Bootstrap draws refit thousands of cross-sections on the same graph, so
this module reuses one eigendecomposition of ``W`` per graph: the Gaussian
concentrated likelihood of the spatial lag and error models, and Fernández's 2SLS
lag with instruments ``[X, W X_cols]``. ``replication`` asserts agreement with the
statadic fit on the original sample before any draw is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from scipy.optimize import minimize_scalar

from free_foundations.encoders.contracts import FloatArray  # noqa: TC001 -- dataclass field types.

type Process = Literal["lag", "error"]
BOUND = 0.999


@dataclass(frozen=True)
class Graph:
    """Weights with their real spectrum and admissible coefficient interval."""

    weights: FloatArray
    spectrum: FloatArray

    @classmethod
    def of(cls, weights: FloatArray) -> Graph:
        """``W = D^-1 A`` with symmetric ``A`` is similar to ``sqrt(W * W')``."""
        weights = np.asarray(weights, dtype=float)
        spectrum = np.asarray(np.linalg.eigvalsh(np.sqrt(weights * weights.T)), dtype=float)
        return cls(weights, spectrum)

    @property
    def interval(self) -> tuple[float, float]:
        """Coefficients keeping ``I - rho W`` invertible, within ``(-BOUND, BOUND)``."""
        low = 1 / self.spectrum.min() if self.spectrum.min() < 0 else -np.inf
        high = 1 / self.spectrum.max() if self.spectrum.max() > 0 else np.inf
        return max(low, -1.0) * BOUND, min(high, 1.0) * BOUND


def _logdet(graph: Graph, value: float) -> float:
    return float(np.log(np.abs(1 - value * graph.spectrum)).sum())


def _ols(design: FloatArray, outcome: FloatArray) -> tuple[FloatArray, FloatArray]:
    coefficients = np.linalg.lstsq(design, outcome, rcond=None)[0]
    return coefficients, outcome - design @ coefficients


def profile(
    outcome: FloatArray, design: FloatArray, graph: Graph, process: Process
) -> tuple[FloatArray, float, float]:
    """Maximize the concentrated likelihood; return coefficients, spatial value, loglik."""
    outcome, design = np.asarray(outcome, float), np.asarray(design, float)
    count = len(outcome)
    lagged_y, lagged_x = graph.weights @ outcome, graph.weights @ design

    def fit(value: float) -> tuple[FloatArray, FloatArray]:
        if process == "lag":
            return _ols(design, outcome - value * lagged_y)
        return _ols(design - value * lagged_x, outcome - value * lagged_y)

    def loglik(value: float) -> float:
        residuals = fit(value)[1]
        variance = float(residuals @ residuals / count)
        return _logdet(graph, value) - count / 2 * (np.log(2 * np.pi * variance) + 1)

    low, high = graph.interval
    grid = np.linspace(low, high, 41)
    values = np.array([loglik(float(point)) for point in grid])
    best = int(np.argmax(values))
    bracket = (float(grid[max(best - 1, 0)]), float(grid[min(best + 1, len(grid) - 1)]))
    result = minimize_scalar(
        lambda value: -loglik(float(value)),
        bounds=bracket,
        method="bounded",
        options={"xatol": 1e-9},
    )
    value = float(result.x)
    return fit(value)[0], value, loglik(value)


def lag_iv(
    outcome: FloatArray, design: FloatArray, graph: Graph, instrument_columns: tuple[int, ...]
) -> tuple[FloatArray, float]:
    """Spatial 2SLS with instruments ``[X, W X_cols]``; returns coefficients and rho."""
    outcome, design = np.asarray(outcome, float), np.asarray(design, float)
    regressors = np.column_stack([design, graph.weights @ outcome])
    instruments = np.column_stack([design, graph.weights @ design[:, list(instrument_columns)]])
    projected = instruments @ np.linalg.lstsq(instruments, regressors, rcond=None)[0]
    coefficients = np.linalg.lstsq(projected, outcome, rcond=None)[0]
    return coefficients[:-1], float(coefficients[-1])


@dataclass(frozen=True)
class Period:
    """One quarter's sufficient vectors: outcomes, regressor, their lags and spectrum."""

    outcome: FloatArray
    regressor: FloatArray
    lagged_outcome: FloatArray
    lagged_regressor: FloatArray
    graph: Graph

    @classmethod
    def of(cls, outcome: FloatArray, regressor: FloatArray, weights: FloatArray) -> Period:
        """Keep the spectrum and lagged vectors; the dense graph is not retained."""
        graph = Graph.of(weights)
        return cls(
            np.asarray(outcome, float),
            np.asarray(regressor, float),
            weights @ outcome,
            weights @ regressor,
            Graph(np.empty((0, 0)), graph.spectrum),
        )


@dataclass(frozen=True)
class PanelFit:
    """Period-effects spatial panel at its profile maximum."""

    spatial: float
    slope: float
    variance: float
    loglik: float
    contributions: FloatArray
    spatial_se: float


def _within(values: FloatArray, sizes: FloatArray) -> FloatArray:
    """Remove each period's mean from stacked period vectors."""
    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(int)
    means = np.add.reduceat(values, starts) / sizes
    return values - np.repeat(means, sizes.astype(int))


def _panel_state(
    periods: list[Period], value: float, process: Process
) -> tuple[float, FloatArray, FloatArray, FloatArray]:
    """Slope, stacked residuals, period sizes and log-determinants at one coefficient."""
    outcomes: list[FloatArray] = []
    regressors: list[FloatArray] = []
    for period in periods:
        outcomes.append(period.outcome - value * period.lagged_outcome)
        regressors.append(
            period.regressor
            if process == "lag"
            else period.regressor - value * period.lagged_regressor
        )
    sizes = np.array([len(period.outcome) for period in periods], dtype=float)
    y = _within(np.concatenate(outcomes), sizes)
    z = _within(np.concatenate(regressors), sizes)
    slope = float(z @ y / (z @ z)) if z @ z > 0 else 0.0
    residuals = y - slope * z
    logdets = np.array([_logdet(period.graph, value) for period in periods])
    return slope, residuals, sizes, logdets


def _panel_loglik(periods: list[Period], value: float, process: Process) -> float:
    _, residuals, sizes, logdets = _panel_state(periods, value, process)
    count = sizes.sum()
    variance = float(residuals @ residuals / count)
    return float(logdets.sum() - count / 2 * (np.log(2 * np.pi * variance) + 1))


def panel_profile(periods: list[Period], process: Process) -> PanelFit:
    """Concentrated Gaussian likelihood with period effects and one common coefficient.

    Period effects are removed within each quarter. For the error model this uses
    ``W 1 = 1``, which holds for the row-normalized graphs without isolates used here.
    The standard error is the inverse curvature of the profile likelihood.
    """
    intervals = [period.graph.interval for period in periods]
    low = max(interval[0] for interval in intervals)
    high = min(interval[1] for interval in intervals)
    grid = np.linspace(low, high, 41)
    values = np.array([_panel_loglik(periods, float(point), process) for point in grid])
    best = int(np.argmax(values))
    bracket = (float(grid[max(best - 1, 0)]), float(grid[min(best + 1, len(grid) - 1)]))
    result = minimize_scalar(
        lambda value: -_panel_loglik(periods, float(value), process),
        bounds=bracket,
        method="bounded",
        options={"xatol": 1e-9},
    )
    value = float(result.x)
    slope, residuals, sizes, logdets = _panel_state(periods, value, process)
    count = sizes.sum()
    variance = float(residuals @ residuals / count)
    starts = np.concatenate([[0], np.cumsum(sizes)[:-1]]).astype(int)
    energy = np.add.reduceat(residuals**2, starts)
    contributions = logdets - sizes / 2 * np.log(2 * np.pi * variance) - energy / (2 * variance)
    step = 1e-4
    curvature = (
        _panel_loglik(periods, value + step, process)
        - 2 * _panel_loglik(periods, value, process)
        + _panel_loglik(periods, value - step, process)
    ) / step**2
    se = float(np.sqrt(-1 / curvature)) if curvature < 0 else float("nan")
    return PanelFit(value, slope, variance, float(contributions.sum()), contributions, se)
