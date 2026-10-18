"""Explicit, labeled metrics for yearly firm embeddings."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist

from free_foundations.pilot.spatial import normalize_weights

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray

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


def distance_weights(distances: FloatArray) -> tuple[FloatArray, float]:
    """Map distances to a dense Gaussian W with a geometry-only median bandwidth."""
    squared = distances**2
    positive = squared[squared > 0]
    bandwidth = float(np.median(positive)) if positive.size else 1.0
    return normalize_weights(np.exp(-squared / bandwidth)), bandwidth


def save_distance(path: Path, distances: FloatArray, tickers: tuple[str, ...]) -> None:
    """Persist the matrix with identical ordered ticker labels on both axes."""
    if distances.shape != (len(tickers), len(tickers)) or len(set(tickers)) != len(tickers):
        message = "Distance dimensions and unique ticker labels must agree."
        raise ValueError(message)
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(distances, index=pd.Index(tickers, name="ticker"), columns=tickers).to_parquet(
        path
    )
