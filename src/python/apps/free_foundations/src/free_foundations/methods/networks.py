"""Networks on one issuer roster, each built without parameters fitted to returns.

Two constructions share one roster. Fernández's replication keeps her literal
``W = rownorm(exp(-d))`` on chord distances (her equations 9 and 10). Comparison
networks are k-nearest-neighbour graphs: each issuer links to its ``k`` closest
issuers, links are symmetrized, and rows are normalized. A k-NN graph depends only
on the order of distances, so it survives the concentration of high-dimensional
embedding distances that makes any smooth kernel nearly uniform. Industry links
same-SIC-2 issuers, and the permutation null relabels the Fernández joint graph.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

from free_foundations.methods.distances import pairwise_distance
from free_foundations.methods.moments import pairwise_spearman

if TYPE_CHECKING:
    from collections.abc import Mapping

    import pandas as pd

    from free_foundations.encoders.contracts import FloatArray

CHARACTERISTICS = ("market_cap_assets", "market_to_book", "dividend_yield", "debt_maturity")


@dataclass(frozen=True)
class Network:
    """Row-normalized weights on an ordered roster, with their construction evidence."""

    name: str
    family: str
    construction: str
    issuers: tuple[str, ...]
    weights: FloatArray
    distance: FloatArray | None = None
    neutral_pairs: int = 0

    def __post_init__(self) -> None:
        """Require a square, nonnegative, zero-diagonal, row-normalized or isolated W."""
        weights = self.weights
        if weights.shape != (len(self.issuers), len(self.issuers)):
            message = "Network weights must match the ordered roster."
            raise ValueError(message)
        sums = weights.sum(axis=1)
        if (
            not np.isfinite(weights).all()
            or (weights < 0).any()
            or np.any(np.diag(weights) != 0)
            or not np.all(np.isclose(sums, 1) | (sums == 0))
        ):
            message = f"{self.name}: weights must be finite, nonnegative and row-normalized."
            raise ValueError(message)

    @property
    def isolates(self) -> int:
        """Issuers without any neighbour."""
        return int(np.count_nonzero(self.weights.sum(axis=1) == 0))

    @property
    def effective_neighbours(self) -> float:
        """Mean inverse Herfindahl index of nonisolated rows."""
        rows = self.weights[self.weights.sum(axis=1) > 0]
        return float(np.mean(1 / np.sum(rows**2, axis=1))) if len(rows) else 0.0

    @property
    def uniformity(self) -> float:
        """Mean total-variation distance of rows from the uniform average (0 = uniform)."""
        n = len(self.issuers)
        uniform = (1 - np.eye(n)) / (n - 1)
        rows = self.weights.sum(axis=1) > 0
        return float(0.5 * np.abs(self.weights - uniform)[rows].sum(axis=1).mean())

    def summary(self) -> dict[str, object]:
        """Construction and shape evidence recorded beside every estimate."""
        return {
            "network": self.name,
            "family": self.family,
            "construction": self.construction,
            "issuers": len(self.issuers),
            "isolates": self.isolates,
            "effective_neighbours": self.effective_neighbours,
            "distance_from_uniform": self.uniformity,
            "neutral_pairs": self.neutral_pairs,
        }


def _row_normalize(adjacency: FloatArray) -> FloatArray:
    adjacency = np.array(adjacency, dtype=float)
    np.fill_diagonal(adjacency, 0.0)
    sums = adjacency.sum(axis=1, keepdims=True)
    return np.divide(adjacency, sums, out=np.zeros_like(adjacency), where=sums > 0)


def exponential_weights(distance: FloatArray) -> FloatArray:
    """Fernández equation (10): ``rownorm(exp(-d))`` with a zero diagonal."""
    return _row_normalize(np.exp(-np.asarray(distance, dtype=float)))


def knn_weights(distance: FloatArray, neighbours: int) -> FloatArray:
    """Symmetrized k-nearest-neighbour graph; ties break by roster order."""
    distance = np.array(distance, dtype=float)
    n = len(distance)
    if not 1 <= neighbours < n:
        message = "The neighbour count must lie between one and the roster size."
        raise ValueError(message)
    np.fill_diagonal(distance, np.inf)
    nearest = np.argsort(distance, axis=1, kind="stable")[:, :neighbours]
    adjacency = np.zeros((n, n))
    adjacency[np.repeat(np.arange(n), neighbours), nearest.ravel()] = 1.0
    return _row_normalize(np.maximum(adjacency, adjacency.T))


def characteristic_distances(
    histories: Mapping[str, FloatArray],
) -> dict[str, tuple[FloatArray, int]]:
    """Fernández's per-characteristic Spearman chord distances and their RMS joint.

    Each history array has issuers in rows and annual slots in columns. Pairs with
    fewer than two common slots or a constant history take the neutral distance.
    """
    result: dict[str, tuple[FloatArray, int]] = {}
    for name in CHARACTERISTICS:
        moments = pairwise_spearman(histories[name])
        result[name] = (moments.distance, moments.neutral_pairs)
    joint = np.sqrt(np.mean([result[name][0] ** 2 for name in CHARACTERISTICS], axis=0))
    result["joint"] = (joint, max(result[name][1] for name in CHARACTERISTICS))
    return result


def representation_distance(values: FloatArray) -> FloatArray:
    """Chord distance between frozen representation rows."""
    return pairwise_distance(values, "chord")


def size_distance(market_equity: FloatArray) -> FloatArray:
    """Absolute difference in log market equity at formation."""
    log_size = np.log(np.asarray(market_equity, dtype=float))
    if not np.isfinite(log_size).all():
        message = "Size distance needs positive market equity for every issuer."
        raise ValueError(message)
    return np.abs(log_size[:, None] - log_size[None, :])


def industry_weights(codes: pd.Series) -> FloatArray:
    """Same-SIC-2 links, row-normalized; issuers without a code or peer are isolated."""
    groups = np.array(
        [code[:2] if isinstance(code, str) and len(code) >= 2 else None for code in codes],
        dtype=object,
    )
    known = np.array([code is not None for code in groups])
    adjacency = (groups[:, None] == groups[None, :]) & known[:, None] & known[None, :]
    return _row_normalize(adjacency.astype(float))


def permuted(weights: FloatArray, seed: int) -> FloatArray:
    """Relabel a graph: identical degree structure, uninformative identities."""
    order = np.random.default_rng(seed).permutation(len(weights))
    return weights[np.ix_(order, order)]


def roster_networks(  # noqa: PLR0913 -- one roster's complete information sets.
    issuers: tuple[str, ...],
    histories: Mapping[str, FloatArray],
    states: Mapping[str, FloatArray],
    market_equity: FloatArray,
    sic: pd.Series,
    *,
    neighbours: tuple[int, ...],
    seed: int,
) -> dict[str, Network]:
    """Every replication and comparison network on one ordered roster.

    ``states`` maps ``rung:model`` (including ``rung:direct``) to rows aligned with
    ``issuers``. ``neighbours`` lists k values; the first is the primary graph.
    Unavailable inputs simply produce no network; callers record the absence.
    """
    networks: list[Network] = []
    characteristic = characteristic_distances(histories)
    for name, (distance, neutral) in characteristic.items():
        networks.append(
            Network(
                f"fernandez:{name}|exp",
                "replication",
                "exp(-d)",
                issuers,
                exponential_weights(distance),
                distance,
                neutral,
            )
        )
    distances: dict[str, tuple[str, FloatArray, int]] = {
        "fernandez:joint": ("matched", characteristic["joint"][0], characteristic["joint"][1]),
    }
    for key, values in states.items():
        family = "control" if key.endswith(":direct") else "foundation"
        distances[key] = (family, representation_distance(values), 0)
    if np.all(np.asarray(market_equity) > 0):
        distances["size"] = ("comparator", size_distance(market_equity), 0)
    for k in neighbours:
        for key, (family, distance, neutral) in distances.items():
            networks.append(
                Network(
                    f"{key}|knn{k}",
                    family,
                    f"symmetrized {k}-NN",
                    issuers,
                    knn_weights(distance, k),
                    distance,
                    neutral,
                )
            )
        joint = knn_weights(characteristic["joint"][0], k)
        networks.append(
            Network(f"null|knn{k}", "null", f"relabelled {k}-NN", issuers, permuted(joint, seed))
        )
    industry = industry_weights(sic)
    if industry.any():
        networks.append(Network("industry|sic2", "comparator", "same SIC-2", issuers, industry))
    return {network.name: network for network in networks}
