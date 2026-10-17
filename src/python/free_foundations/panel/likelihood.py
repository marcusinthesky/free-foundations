"""A single pooled spatial coefficient with annual networks and innovation scales."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

import numpy as np

from free_foundations.fernandez.models import maximize_profile, symmetric_spectrum

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

type Innovations = Literal["spherical", "diagonal"]
INNOVATIONS: tuple[Innovations, ...] = ("spherical", "diagonal")


@dataclass(frozen=True)
class Block:
    """Per-firm sufficient statistics for a daily residual block and fixed network.

    For A = I - lambda W, each firm's mean squared filtered residual is
    second - 2 lambda cross + lambda^2 spatial. Spherical innovations profile one
    variance, their mean; diagonal innovations profile one variance per firm.
    """

    days: int
    second: FloatArray
    cross: FloatArray
    spatial: FloatArray
    eigenvalues: FloatArray

    @property
    def firms(self) -> int:
        """Number of firms in this annual block."""
        return len(self.second)

    def filtered(self, intensity: float) -> FloatArray:
        """Mean squared innovation of each firm at a given spatial coefficient."""
        return self.second - 2 * intensity * self.cross + intensity**2 * self.spatial

    def variances(self, intensity: float, innovations: Innovations = "spherical") -> FloatArray:
        """Profiled innovation variances under the stated covariance restriction."""
        filtered = self.filtered(intensity)
        if innovations == "diagonal":
            return filtered
        return np.full(self.firms, filtered.mean())

    def score(
        self,
        intensity: float,
        innovations: Innovations = "spherical",
        variances: FloatArray | None = None,
    ) -> float:
        """Full Gaussian log density, with all constants and the spatial Jacobian."""
        scale = self.variances(intensity, innovations) if variances is None else variances
        jacobian = float(np.log(np.abs(1 - intensity * self.eigenvalues)).sum())
        return self.days * (
            jacobian
            - 0.5 * float(np.sum(np.log(2 * np.pi * scale) + self.filtered(intensity) / scale))
        )


def block(
    residuals: FloatArray, weights: FloatArray, eigenvalues: FloatArray | None = None
) -> Block:
    """Reduce repeated likelihood evaluations to three quadratic statistics per firm."""
    if not np.isfinite(residuals).all() or len(residuals) < 2:
        message = "Likelihood requires at least two complete finite daily observations."
        raise ValueError(message)
    weighted = residuals @ weights.T
    return Block(
        len(residuals),
        np.mean(residuals**2, axis=0),
        np.mean(residuals * weighted, axis=0),
        np.mean(weighted**2, axis=0),
        symmetric_spectrum(weights) if eigenvalues is None else eigenvalues,
    )


def fit(blocks: list[Block], innovations: Innovations = "spherical") -> tuple[float, float]:
    """Maximize pooled likelihood, profiling nuisance variances within each annual block."""
    return maximize_profile(
        lambda value: sum(item.score(value, innovations) for item in blocks), points=201
    )


def forecast_covariance(
    previous: Block,
    weights: FloatArray,
    intensity: float,
    factor_covariance: FloatArray,
    innovations: Innovations = "spherical",
) -> FloatArray:
    """B Cov(F) B' + A^-1 V A^-T, with V estimated from prior residuals at fixed lambda."""
    identity = np.eye(previous.firms)
    inverse = np.linalg.solve(identity - intensity * weights, identity)
    variances = previous.variances(intensity, innovations)
    if innovations == "spherical":
        return factor_covariance + float(variances[0]) * inverse @ inverse.T
    return factor_covariance + (inverse * variances) @ inverse.T


def correlation_only(covariance: FloatArray, raw_prior: FloatArray) -> FloatArray:
    """Keep the implied correlation; impose the prior raw sample variances for every model."""
    scale = np.sqrt(np.diag(covariance))
    correlation = covariance / np.outer(scale, scale)
    target = np.std(raw_prior, axis=0, ddof=1)
    return correlation * np.outer(target, target)


def gaussian_daily(values: FloatArray, covariance: FloatArray) -> FloatArray:
    """Daily zero-mean multivariate Gaussian log densities without hidden regularization."""
    factor = np.linalg.cholesky(covariance)
    innovations = np.linalg.solve(factor, values.T)
    constant = values.shape[1] * np.log(2 * np.pi) + 2 * np.log(np.diag(factor)).sum()
    return -0.5 * (constant + np.sum(innovations**2, axis=0))


def gaussian_score(values: FloatArray, covariance: FloatArray) -> float:
    """Evaluate a zero-mean multivariate Gaussian summed over days."""
    return float(gaussian_daily(values, covariance).sum())
