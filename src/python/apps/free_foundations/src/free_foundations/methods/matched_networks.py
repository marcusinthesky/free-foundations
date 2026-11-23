"""Weighting rules for the matched financial graph comparison."""

from __future__ import annotations

import numpy as np

from free_foundations.methods.networks import exponential_weights, knn_weights


def gaussian_weights(distance: np.ndarray) -> tuple[np.ndarray, float | None]:
    """Use the median positive off-diagonal distance as Gaussian bandwidth.

    Coincident distinct issuers receive unit affinity. If every issuer coincides,
    the graph is uniform and the bandwidth is undefined.
    """
    values = np.asarray(distance, dtype=float)
    positive = values[np.triu_indices(len(values), k=1)]
    positive = positive[positive > 0]
    if not len(positive):
        weights = np.ones_like(values) - np.eye(len(values))
        return weights / (len(values) - 1), None
    bandwidth = float(np.median(positive))
    # Shifting each row's log affinities leaves its normalized weights unchanged.
    squared = ((values / bandwidth) ** 2) / 2
    np.fill_diagonal(squared, np.inf)
    squared -= squared.min(axis=1, keepdims=True)
    affinity = np.exp(-squared)
    return affinity / affinity.sum(axis=1, keepdims=True), bandwidth


def kernel_weights(distance: np.ndarray, kernel: str) -> tuple[np.ndarray, float | None]:
    """Construct a zero-diagonal row-normalized graph on an ordered roster."""
    if kernel == "exp":
        return exponential_weights(distance), None
    if kernel == "gaussian":
        return gaussian_weights(distance)
    if kernel == "knn10":
        return knn_weights(distance, 10), None
    msg = f"Unknown matched weighting rule: {kernel}."
    raise ValueError(msg)
