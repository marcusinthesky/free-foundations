"""Explicit, labeled metrics for yearly firm embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from scipy.spatial.distance import cdist

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray

Metric = Literal["chord", "euclidean"]


def pairwise_distance(vectors: FloatArray, metric: Metric = "chord") -> FloatArray:
    """Return true Euclidean or unit-sphere chord distances, never squared distances."""
    values = np.asarray(vectors, dtype=np.float64)
    if values.ndim != 2 or len(values) < 2 or not np.isfinite(values).all():
        message = "Expected at least two finite embedding rows."
        raise ValueError(message)
    if metric == "chord":
        lengths = np.linalg.norm(values, axis=1, keepdims=True)
        if (lengths <= np.finfo(float).eps).any():
            message = "Chord distance is undefined for a zero embedding."
            raise ValueError(message)
        values = values / lengths
    elif metric != "euclidean":
        message = f"Unknown metric: {metric}"
        raise ValueError(message)
    distances = np.asarray(cdist(values, values), dtype=np.float64)
    np.fill_diagonal(distances, 0)
    return distances
