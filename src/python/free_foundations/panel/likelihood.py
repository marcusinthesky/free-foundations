"""A single pooled spatial coefficient with annual networks and innovation scales."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray


@dataclass(frozen=True)
class Block:
    """Sufficient statistics for an observed daily residual block and fixed network."""

    days: int
    firms: int
    second: float
    cross: float
    spatial: float
    eigenvalues: FloatArray

    def variance(self, intensity: float) -> float:
        """Profile the spherical innovation variance."""
        return self.second - 2 * intensity * self.cross + intensity**2 * self.spatial

    def score(self, intensity: float, variance: float | None = None) -> float:
        """Full Gaussian log density, with all constants and the spatial Jacobian."""
        scale = self.variance(intensity) if variance is None else variance
        jacobian = float(np.log(np.abs(1 - intensity * self.eigenvalues)).sum())
        return self.days * (
            jacobian
            - self.firms / 2 * (np.log(2 * np.pi * scale) + self.variance(intensity) / scale)
        )


def block(residuals: FloatArray, weights: FloatArray) -> Block:
    """Reduce repeated likelihood evaluations to three quadratic statistics."""
    if not np.isfinite(residuals).all() or len(residuals) < 2:
        message = "Likelihood requires at least two complete finite daily observations."
        raise ValueError(message)
    weighted = residuals @ weights.T
    eigenvalues = np.linalg.eigvals(weights)
    if np.max(np.abs(eigenvalues.imag)) > 1e-8:
        message = "Expected a row-normalized symmetric affinity with real eigenvalues."
        raise ValueError(message)
    return Block(
        len(residuals),
        residuals.shape[1],
        float(np.mean(residuals**2)),
        float(np.mean(residuals * weighted)),
        float(np.mean(weighted**2)),
        np.asarray(eigenvalues.real, dtype=float),
    )


def fit(blocks: list[Block]) -> tuple[float, float]:
    """Maximize pooled likelihood, profiling one nuisance variance per annual block."""

    def objective(value: float) -> float:
        return -sum(item.score(value) for item in blocks)

    grid = np.linspace(-0.99, 0.99, 201)
    values = np.array([objective(float(point)) for point in grid])
    best = int(np.argmin(values))
    result = minimize_scalar(
        objective,
        bounds=(float(grid[max(0, best - 1)]), float(grid[min(len(grid) - 1, best + 1)])),
        method="bounded",
    )
    if not result.success:
        message = "Pooled spatial coefficient optimization failed."
        raise RuntimeError(message)
    return float(result.x), -float(result.fun)


def gaussian_score(values: FloatArray, covariance: FloatArray) -> float:
    """Evaluate a zero-mean multivariate Gaussian without hidden regularization."""
    factor = np.linalg.cholesky(covariance)
    innovations = np.linalg.solve(factor, values.T)
    return float(
        -0.5
        * (
            len(values) * (values.shape[1] * np.log(2 * np.pi) + 2 * np.log(np.diag(factor)).sum())
            + np.sum(innovations**2)
        )
    )
