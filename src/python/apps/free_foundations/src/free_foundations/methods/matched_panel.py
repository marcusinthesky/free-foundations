"""Concentrated Gaussian likelihood for matched spatial panels with quarter effects."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order

from free_foundations.methods.spatial_ml import Graph

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from free_foundations.encoders.contracts import FloatArray

type Process = Literal["none", "lag", "error"]
BOUNDARY_TOLERANCE = 1e-4


def prepare_graph(weights: FloatArray) -> Graph:
    """Validate detailed balance and cache a real spectrum for design reuse."""
    n = len(weights)
    if (
        weights.shape != (n, n)
        or not np.isfinite(weights).all()
        or (weights < 0).any()
        or not np.all(np.diag(weights) == 0)
        or not np.allclose(weights.sum(axis=1), 1)
    ):
        msg = "Spatial comparison requires a finite nonnegative row-stochastic graph."
        raise ValueError(msg)
    source, target = np.nonzero(weights)
    reverse = weights[target, source]
    if (reverse == 0).any():
        msg = "Spatial comparison requires symmetric graph support."
        raise ValueError(msg)
    adjacency = csr_matrix(weights)
    balance = np.full(n, np.nan)
    for root in range(n):
        if np.isfinite(balance[root]):
            continue
        nodes, parents = breadth_first_order(adjacency, root, directed=False)
        balance[root] = 0
        for node in nodes[1:]:
            parent = parents[node]
            ratio = weights[parent, node] / weights[node, parent]
            balance[node] = balance[parent] + np.log(ratio)
    if not np.allclose(
        balance[source] - balance[target], np.log(reverse / weights[source, target])
    ):
        msg = "Spatial comparison requires reversible graph weights."
        raise ValueError(msg)
    return Graph.of(weights)


@dataclass(frozen=True)
class Period:
    """One fixed-effects block and its within-quarter transformation moments."""

    count: int
    gram: FloatArray
    cross: FloatArray
    lagged_gram: FloatArray
    graph: Graph | None

    @classmethod
    def of(
        cls, outcome: FloatArray, design: FloatArray, weights: FloatArray | Graph | None = None
    ) -> Period:
        """Prepare a finite design and optional reversible, row-stochastic graph."""
        outcome = np.asarray(outcome, dtype=float)
        design = np.asarray(design, dtype=float)
        if design.ndim == 1:
            design = design[:, None]
        n = len(outcome)
        if (
            outcome.shape != (n,)
            or design.ndim != 2
            or design.shape[0] != n
            or n < 2
            or not np.isfinite(outcome).all()
            or not np.isfinite(design).all()
        ):
            msg = "A matched quarter needs aligned, finite outcomes and design rows."
            raise ValueError(msg)
        values = np.column_stack((design, outcome))
        within = values - values.mean(axis=0)
        if weights is None:
            return cls(n, within.T @ within, np.zeros((0, 0)), np.zeros((0, 0)), None)
        graph = weights if isinstance(weights, Graph) else prepare_graph(weights)
        if graph.weights.shape != (n, n):
            msg = "Graph weights must match the ordered outcomes."
            raise ValueError(msg)
        lagged = graph.weights @ values
        lagged -= lagged.mean(axis=0)
        return cls(
            n,
            within.T @ within,
            within.T @ lagged,
            lagged.T @ lagged,
            Graph(np.empty((0, 0)), graph.spectrum),
        )


@dataclass(frozen=True)
class Fit:
    """A comparable point likelihood, accounting for period intercepts and innovation variance."""

    process: Process
    coefficients: FloatArray
    spatial: float
    variance: float
    loglik: float
    contributions: FloatArray
    observations: int
    parameters: int
    lower: float
    upper: float
    boundary: bool
    flat_profile: bool
    profile_range: float

    @property
    def aic(self) -> float:
        """Conditional AIC with quarter intercepts included."""
        return 2 * self.parameters - 2 * self.loglik

    @property
    def bic(self) -> float:
        """Conditional BIC with the same parameter count."""
        return self.parameters * float(np.log(self.observations)) - 2 * self.loglik


def _matrices(
    periods: Sequence[Period], process: Process
) -> tuple[FloatArray, FloatArray, FloatArray]:
    grams = np.stack([period.gram for period in periods])
    if process == "none":
        return grams, np.zeros_like(grams), np.zeros_like(grams)
    cross = np.stack([period.cross for period in periods])
    lagged = np.stack([period.lagged_gram for period in periods])
    if process == "lag":
        cross[:, :, :-1] = 0
        lagged[:, :-1, :] = 0
        lagged[:, :, :-1] = 0
    return grams, cross + cross.transpose(0, 2, 1), lagged


def _maximize(
    graphs: Sequence[Graph], objective: Callable[[float], float]
) -> tuple[float, float, float, float]:
    low = max(graph.interval[0] for graph in graphs)
    high = min(graph.interval[1] for graph in graphs)
    grid = np.linspace(low, high, 41)
    values = np.array([objective(float(point)) for point in grid])
    if not np.isfinite(values).all():
        msg = "The spatial profile cannot be evaluated on its interval."
        raise ValueError(msg)
    best = int(np.argmin(values))
    result = minimize_scalar(
        objective,
        bounds=(grid[max(best - 1, 0)], grid[min(best + 1, len(grid) - 1)]),
        method="bounded",
        options={"xatol": 1e-9},
    )
    if not result.success:
        msg = "The spatial profile optimizer did not converge."
        raise ValueError(msg)
    value = min((float(result.x), float(grid[best]), 0.0), key=objective)
    return low, high, value, float(np.ptp(values))


def fit(periods: Sequence[Period], process: Process = "lag") -> Fit:
    """Profile a common spatial coefficient and slopes with one intercept per occurrence."""
    if not periods or process not in ("none", "lag", "error"):
        msg = "A matched fit requires a nonempty panel and a valid process."
        raise ValueError(msg)
    graphs = [period.graph for period in periods if period.graph is not None]
    if process != "none" and len(graphs) != len(periods):
        msg = "Spatial fits require a graph for every period."
        raise ValueError(msg)
    sizes = np.array([period.count for period in periods])
    observations = int(sizes.sum())
    grams, crosses, lagged = _matrices(periods, process)
    base, cross, lag = grams.sum(axis=0), crosses.sum(axis=0), lagged.sum(axis=0)
    design = base[:-1, :-1]
    columns = len(design)
    if (columns and np.linalg.matrix_rank(design) != columns) or observations <= columns + len(
        periods
    ):
        msg = "The within-quarter design is rank deficient or has no residual degrees of freedom."
        raise ValueError(msg)
    spectrum = (
        np.concatenate([graph.spectrum for graph in graphs]) if process != "none" else np.array([])
    )

    def state(value: float) -> tuple[FloatArray, float]:
        moment = base - value * cross + value**2 * lag
        coefficient = np.linalg.solve(moment[:-1, :-1], moment[:-1, -1])
        residual = moment[-1, -1] - coefficient @ moment[:-1, -1]
        return coefficient, float(residual / observations)

    def objective(value: float) -> float:
        _, variance = state(value)
        if variance <= 0 or not np.isfinite(variance):
            return np.inf
        logdet = np.log1p(-value * spectrum).sum()
        return float(observations / 2 * (np.log(2 * np.pi * variance) + 1) - logdet)

    low = high = value = spread = 0.0
    if process != "none":
        low, high, value, spread = _maximize(graphs, objective)

    coefficients, variance = state(value)
    if variance <= 0 or not np.isfinite(variance):
        msg = "A matched fit requires positive finite innovation variance."
        raise ValueError(msg)
    residual_vector = np.append(-coefficients, 1)
    moments = grams - value * crosses + value**2 * lagged
    energy = np.einsum("i,tij,j->t", residual_vector, moments, residual_vector)
    logdets = (
        np.array([np.log1p(-value * graph.spectrum).sum() for graph in graphs])
        if process != "none"
        else np.zeros(len(periods))
    )
    contributions = logdets - sizes / 2 * np.log(2 * np.pi * variance) - energy / (2 * variance)
    return Fit(
        process,
        coefficients,
        value,
        variance,
        float(contributions.sum()),
        contributions,
        observations,
        columns + len(periods) + 1 + (process != "none"),
        low,
        high,
        process != "none" and min(value - low, high - value) <= BOUNDARY_TOLERANCE,
        process != "none" and spread <= 1e-8,
        spread,
    )
