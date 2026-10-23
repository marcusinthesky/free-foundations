"""Signed financial Gram geometry, direct covariance, and descriptive coordinates.

A Gram matrix is deliberately distinct from a spatial weighting matrix: its
diagonal is one, entries may be negative, and no row normalization is applied.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.optimize import minimize_scalar

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

THETA_MAX = 1 - 1e-6
EIGEN_TOLERANCE = 1e-10


def _square(values: FloatArray, label: str) -> FloatArray:
    """Require a finite, nonempty, symmetric square matrix."""
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 2 or array.shape[0] != array.shape[1] or not len(array):
        message = f"{label} must be a nonempty square matrix."
        raise ValueError(message)
    if not np.isfinite(array).all() or not np.allclose(array, array.T, atol=1e-10, rtol=0):
        message = f"{label} must be finite and symmetric."
        raise ValueError(message)
    return array


def validate_gram(gram: FloatArray) -> FloatArray:
    """Reject invalid unit Gram matrices without clipping or PSD repair."""
    array = _square(gram, "Gram matrix")
    if not np.allclose(np.diag(array), 1, atol=1e-10, rtol=0):
        message = "Gram matrix must have a unit diagonal."
        raise ValueError(message)
    eigenvalues = np.linalg.eigvalsh(array)
    tolerance = EIGEN_TOLERANCE * max(1.0, float(eigenvalues[-1]))
    if eigenvalues[0] < -tolerance:
        message = "Gram matrix has materially negative eigenvalues."
        raise ValueError(message)
    return array


def unit_gram(vectors: FloatArray) -> FloatArray:
    """Normalize nonzero firm vectors and return their signed dot products."""
    values = np.asarray(vectors, dtype=np.float64)
    if values.ndim != 2 or 0 in values.shape or not np.isfinite(values).all():
        message = "Firm vectors must be a nonempty finite two-dimensional matrix."
        raise ValueError(message)
    # Rescale before the norm so very large or very small finite features remain valid.
    largest = np.max(np.abs(values), axis=1)
    if np.any(largest == 0):
        message = "Unit Gram geometry is undefined for zero firm vectors."
        raise ValueError(message)
    normalized = values / largest[:, None]
    normalized /= np.linalg.norm(normalized, axis=1, keepdims=True)
    return validate_gram(normalized @ normalized.T)


def chord_gram(distances: FloatArray) -> FloatArray:
    """Recover C=1-D^2/2 only when distances admit unit-sphere chord geometry."""
    values = _square(distances, "Chord distances")
    if np.any(values < 0) or not np.allclose(np.diag(values), 0, atol=1e-10, rtol=0):
        message = "Chord distances must be nonnegative with a zero diagonal."
        raise ValueError(message)
    return validate_gram(1 - values**2 / 2)


def joint_gram(grams: list[FloatArray]) -> FloatArray:
    """Arithmetic Gram average corresponding to an RMS joint chord distance."""
    if not grams:
        message = "Joint geometry requires at least one Gram matrix."
        raise ValueError(message)
    validated = [validate_gram(item) for item in grams]
    if any(item.shape != validated[0].shape for item in validated):
        message = "Joint Gram matrices must use the same ordered firm cohort."
        raise ValueError(message)
    return validate_gram(np.mean(validated, axis=0))


def rms_scales(residuals: FloatArray) -> FloatArray:
    """Empirical residual RMS scales without centering or hidden regularization."""
    values = np.asarray(residuals, dtype=np.float64)
    if values.ndim != 2 or len(values) < 2 or not values.shape[1] or not np.isfinite(values).all():
        message = "Residual scales require at least two complete finite daily observations."
        raise ValueError(message)
    scales = np.sqrt(np.mean(values**2, axis=0))
    if not np.isfinite(scales).all() or np.any(scales <= 0):
        message = "Direct covariance requires strictly positive finite residual RMS scales."
        raise ValueError(message)
    return scales


def _theta(theta: float) -> None:
    """Enforce the prespecified closed calibration interval."""
    if not np.isfinite(theta) or theta < 0 or theta > THETA_MAX:
        message = f"Dependence theta must lie in [0, {THETA_MAX}]."
        raise ValueError(message)


def covariance(gram: FloatArray, scales: FloatArray, theta: float) -> FloatArray:
    """S[(1-theta)I+theta C]S with unchanged positive marginal variances."""
    _theta(theta)
    values = validate_gram(gram)
    scale = np.asarray(scales, dtype=np.float64)
    if scale.shape != (len(values),) or not np.isfinite(scale).all() or np.any(scale <= 0):
        message = "Residual scales must be a positive finite vector matching the Gram cohort."
        raise ValueError(message)
    correlation = (1 - theta) * np.eye(len(values)) + theta * values
    return correlation * np.outer(scale, scale)


@dataclass(frozen=True)
class GramBlock:
    """Fixed RMS scales and spectral sufficient statistics for one calibration block."""

    days: int
    scales: FloatArray
    eigenvalues: FloatArray
    energy: FloatArray

    @property
    def firms(self) -> int:
        """Number of ordered firms in this block."""
        return len(self.scales)

    def score(self, theta: float) -> float:
        """Full Gaussian log likelihood at fixed empirical RMS scales."""
        _theta(theta)
        diagonal = 1 - theta + theta * self.eigenvalues
        constant = self.firms * np.log(2 * np.pi) + 2 * np.log(self.scales).sum()
        return -0.5 * float(
            self.days * (constant + np.log(diagonal).sum()) + np.sum(self.energy / diagonal)
        )


def block(residuals: FloatArray, gram: FloatArray) -> GramBlock:
    """Reduce the fixed-scale likelihood to a Gram eigensystem and projected energy."""
    values = validate_gram(gram)
    scales = rms_scales(residuals)
    if len(scales) != len(values):
        message = "Residual columns must match the ordered Gram cohort."
        raise ValueError(message)
    eigenvalues, vectors = np.linalg.eigh(values)
    projected = (residuals / scales) @ vectors
    return GramBlock(len(residuals), scales, eigenvalues, np.sum(projected**2, axis=0))


def fit(blocks: list[GramBlock]) -> tuple[float, float]:
    """Fit one pooled theta, checking endpoints and returning zero for flat likelihood."""
    if not blocks:
        message = "Pooled Gram calibration requires at least one residual block."
        raise ValueError(message)

    def objective(value: float) -> float:
        return sum(item.score(value) for item in blocks)

    grid = np.linspace(0, THETA_MAX, 201)
    scores = np.array([objective(float(value)) for value in grid])
    if np.ptp(scores) <= 1e-10 * max(1.0, abs(float(scores[0]))):
        return 0.0, float(scores[0])
    best = int(np.argmax(scores))
    candidates = [(float(grid[best]), float(scores[best])), (0.0, float(scores[0]))]
    # The endpoints remain candidates: bounded optimization alone never attains them.
    candidates.append((THETA_MAX, float(scores[-1])))
    lower, upper = float(grid[max(0, best - 1)]), float(grid[min(len(grid) - 1, best + 1)])
    result = minimize_scalar(
        lambda value: -objective(float(value)),
        bounds=(lower, upper),
        method="bounded",
        options={"xatol": 1e-12},
    )
    if not result.success:
        message = "Pooled Gram likelihood optimization failed."
        raise RuntimeError(message)
    candidates.append((float(result.x), -float(result.fun)))
    return max(candidates, key=lambda item: (item[1], -item[0]))


def forecast_covariance(
    prior: FloatArray, gram: FloatArray, theta: float, factor_covariance: FloatArray
) -> FloatArray:
    """Add the unchanged financial-factor covariance to prior-RMS residual covariance."""
    residual = covariance(gram, rms_scales(prior), theta)
    factor = _square(factor_covariance, "Financial-factor covariance")
    if factor.shape != residual.shape:
        message = "Factor covariance must match the ordered Gram cohort."
        raise ValueError(message)
    return factor + residual


@dataclass(frozen=True)
class PCoA:
    """Full centered spectrum and selected descriptive principal coordinates."""

    gram: FloatArray
    eigenvalues: FloatArray
    coordinates: FloatArray
    weights: FloatArray
    tolerance: float

    @property
    def rank(self) -> int:
        """Full positive rank before the prescribed component cap."""
        return int(np.sum(self.eigenvalues > self.tolerance))

    @property
    def components(self) -> int:
        """Number of retained positive directions."""
        return self.coordinates.shape[1]

    @property
    def variance_share(self) -> float:
        """Retained share of positive characteristic variation, zero for rank zero."""
        positive = self.eigenvalues[self.eigenvalues > self.tolerance]
        return float(positive[: self.components].sum() / positive.sum()) if len(positive) else 0.0


def pcoa(gram: FloatArray, *, tickers: tuple[str, ...] | None = None, components: int = 5) -> PCoA:
    """Center a signed Gram matrix and orient its leading positive directions by ticker."""
    values = validate_gram(gram)
    if components < 1:
        message = "PCoA component target must be positive."
        raise ValueError(message)
    labels = tuple(str(index) for index in range(len(values))) if tickers is None else tickers
    if len(labels) != len(values) or len(set(labels)) != len(labels):
        message = "PCoA tickers must uniquely label the ordered Gram cohort."
        raise ValueError(message)
    centered = values - values.mean(axis=0)[None, :] - values.mean(axis=1)[:, None] + values.mean()
    eigenvalues, vectors = np.linalg.eigh(centered)
    eigenvalues, vectors = eigenvalues[::-1], vectors[:, ::-1]
    tolerance = EIGEN_TOLERANCE * max(1.0, float(eigenvalues[0]))
    if eigenvalues[-1] < -tolerance:
        message = "Centered Gram matrix has materially negative eigenvalues."
        raise ValueError(message)
    # Only numerical negative roundoff is suppressed; no positive direction is inflated.
    eigenvalues = np.maximum(eigenvalues, 0)
    count = min(components, int(np.sum(eigenvalues > tolerance)))
    coordinates = vectors[:, :count] * np.sqrt(eigenvalues[:count])
    for axis in range(count):
        column = coordinates[:, axis]
        anchors = np.flatnonzero(np.abs(column) == np.max(np.abs(column)))
        anchor = min(anchors, key=lambda index: labels[int(index)])
        if column[anchor] < 0:
            coordinates[:, axis] *= -1
    weights = coordinates / eigenvalues[:count]
    return PCoA(centered, eigenvalues, coordinates, weights, tolerance)
