"""Distance-to-network kernels and the geometry needed to compare their concentration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

import numpy as np
from scipy.optimize import brentq

from free_foundations.expanded.baselines import group_permutation
from free_foundations.fernandez.models import paper_weights, symmetric_spectrum

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

type Kernel = Literal["exp", "median", "matched"]
KERNELS: tuple[Kernel, ...] = ("exp", "median", "matched")


def scaled_weights(
    distance: FloatArray, bandwidth: float, *, self_links: bool = False
) -> FloatArray:
    """Row-normalized exp(-d / h); a row offset cancels and prevents underflow."""
    if bandwidth <= 0 or not np.isfinite(bandwidth):
        message = "Kernel bandwidth must be positive and finite."
        raise ValueError(message)
    shifted = np.array(distance, dtype=float, copy=True)
    if not self_links:
        np.fill_diagonal(shifted, np.inf)
    shifted -= shifted.min(axis=1, keepdims=True)
    affinity = np.exp(-shifted / bandwidth)
    return affinity / affinity.sum(axis=1, keepdims=True)


def median_scale(distance: FloatArray) -> float:
    """Median positive off-diagonal distance, a geometry-only scale with no returns."""
    values = distance[~np.eye(len(distance), dtype=bool)]
    positive = values[values > 0]
    return float(np.median(positive)) if positive.size else 1.0


def effective_neighbours(weights: FloatArray) -> float:
    """Mean inverse Herfindahl index of each firm's neighbour weights; NaN for empty rows."""
    herfindahl = np.sum(weights**2, axis=1)
    if (herfindahl <= 0).any():
        return float("nan")
    return float(np.mean(1 / herfindahl))


def matched_scale(distance: FloatArray, target: float) -> float:
    """Bandwidth whose mean effective neighbour count equals ``target``.

    The count increases monotonically with h, from the number of tied nearest neighbours
    to N - 1. Unattainable targets return the nearest endpoint; callers record the gap.
    """
    reference = median_scale(distance)

    def gap(log_scale: float) -> float:
        return (
            effective_neighbours(scaled_weights(distance, reference * np.exp(log_scale))) - target
        )

    low, high = -12.0, 12.0
    if gap(low) >= 0:
        return reference * float(np.exp(low))
    if gap(high) <= 0:
        return reference * float(np.exp(high))
    return reference * float(np.exp(brentq(gap, low, high, xtol=1e-10)))


def kernel_weights(
    distance: FloatArray,
    kernel: Kernel,
    *,
    self_links: bool = False,
    target: float | None = None,
) -> tuple[FloatArray, float]:
    """Return W and its bandwidth; ``exp`` is equation (10) exactly, with h = 1."""
    if kernel == "exp":
        weights = paper_weights(distance, self_links=self_links)
        if not np.isfinite(weights).all():
            # Unbounded metrics can underflow every off-diagonal exp(-d); the offset form
            # is algebraically identical after row normalization.
            weights = scaled_weights(distance, 1.0, self_links=self_links)
        return weights, 1.0
    if kernel == "median":
        scale = median_scale(distance)
    else:
        if target is None:
            message = "A matched kernel needs a target effective neighbour count."
            raise ValueError(message)
        scale = matched_scale(distance, target)
    return scaled_weights(distance, scale, self_links=self_links), scale


def geometry(distance: FloatArray | None, weights: FloatArray) -> dict[str, float]:
    """Dispersion, concentration and distance from the uniform network."""
    firms = len(weights)
    off = ~np.eye(firms, dtype=bool)
    uniform = off / (firms - 1)
    spectrum = np.sort(np.abs(symmetric_spectrum(weights)))
    record = {
        "firms": float(firms),
        "effective_neighbours": effective_neighbours(weights),
        "effective_fraction": effective_neighbours(weights) / (firms - 1),
        # The likelihood's neighbour-noise cost scales with the mean Herfindahl index,
        # 1/effective neighbours averaged over rows (Lean `Likelihood.herfindahl_ge`).
        "mean_herfindahl": float(np.mean(np.sum(weights**2, axis=1))),
        "frobenius_gap": float(np.linalg.norm(weights - uniform)),
        "row_total_variation_gap": float(np.mean(0.5 * np.abs(weights - uniform).sum(axis=1))),
        "second_eigenvalue": float(spectrum[-2]) if firms > 1 else 0.0,
    }
    if distance is not None:
        values = distance[off]
        record |= {
            "mean_distance": float(values.mean()),
            "sd_distance": float(values.std()),
            "cv_distance": float(values.std() / values.mean()) if values.mean() > 0 else np.nan,
            "distinct_distances": float(np.unique(np.round(values, 10)).size),
        }
    return record


def size_groups(values: FloatArray, groups: int = 3) -> FloatArray:
    """Quantile groups of a point-in-time size measure; missing sizes form their own group."""
    result = np.full(len(values), -1.0)
    finite = np.isfinite(values)
    ranks = np.argsort(np.argsort(values[finite]))
    result[finite] = np.floor(ranks * groups / finite.sum())
    return result


def placebo(weights: FloatArray, groups: FloatArray, seed: int) -> FloatArray:
    """P W P' with permutations restricted within groups; the spectrum is unchanged."""
    order = group_permutation(groups, seed=seed)
    return weights[np.ix_(order, order)]
