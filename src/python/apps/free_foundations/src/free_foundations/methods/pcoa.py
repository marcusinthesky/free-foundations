"""Principal coordinates and positive inertia on a declared distance matrix."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Coordinates:
    """Sorted eigenspectrum and coordinates on its positive subspace."""

    eigenvalues: np.ndarray
    coordinates: np.ndarray
    shares: np.ndarray
    tolerance: float

    @property
    def trigger(self) -> bool:
        """Interpret only geometries whose first coordinate exceeds 25%."""
        return bool(len(self.shares) and self.shares[0] > 0.25)


def principal_coordinates(distance: np.ndarray) -> Coordinates:
    """Double-center squared distances and retain strictly positive axes."""
    d = np.asarray(distance, dtype=float)
    if (
        d.ndim != 2
        or d.shape[0] != d.shape[1]
        or len(d) < 2
        or not np.isfinite(d).all()
        or (d < 0).any()
        or not np.allclose(np.diag(d), 0)
        or not np.allclose(d, d.T)
    ):
        msg = "PCoA requires a finite, symmetric, nonnegative distance matrix with zero diagonal."
        raise ValueError(msg)
    squared = d**2
    gram = -0.5 * (squared - squared.mean(axis=0) - squared.mean(axis=1)[:, None] + squared.mean())
    eigenvalues, vectors = np.linalg.eigh(gram)
    eigenvalues, vectors = eigenvalues[::-1], vectors[:, ::-1]
    tolerance = float(np.finfo(float).eps * len(d) * np.max(np.abs(eigenvalues)))
    positive = eigenvalues > tolerance
    inertia = eigenvalues[positive]
    vectors = vectors[:, positive]
    if len(inertia):
        largest = np.argmax(np.abs(vectors), axis=0)
        signs = np.sign(vectors[largest, np.arange(len(inertia))])
        vectors *= signs
    return Coordinates(eigenvalues, vectors * np.sqrt(inertia), inertia / inertia.sum(), tolerance)


def coordinate_distances(coordinates: np.ndarray) -> np.ndarray:
    """Euclidean distance between rows of a principal-coordinate projection."""
    gram = coordinates @ coordinates.T
    diag = np.diag(gram)
    distance = np.sqrt(np.maximum(diag[:, None] + diag - 2 * gram, 0))
    np.fill_diagonal(distance, 0)
    return distance
