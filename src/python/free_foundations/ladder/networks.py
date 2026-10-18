"""R0 single-characteristic networks and the R1-R3 matched-information distance ladder."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from free_foundations.expanded.representations import ARMS, MODELS, representation_distances
from free_foundations.fernandez.kernels import effective_neighbours, kernel_weights
from free_foundations.fernandez.models import paper_weights
from free_foundations.ladder.data import CUTOFF_YEAR, HISTORY
from free_foundations.panel.networks import (
    MODEL_CACHE,
    MODEL_SOURCE,
    classical,
    code_digest,
    context,
    labels,
    record_context,
    rung_views,
    save,
)

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray
    from free_foundations.fernandez.kernels import Kernel
    from free_foundations.ladder.data import Inputs

LOGGER = logging.getLogger(__name__)
JOINT = "fernandez_joint"
# Rung label, input view and declared support target.
PASSES = (
    ("r2_histories", "histories", "market_cap_assets"),
    ("r3_broad", "broad", "market_cap_assets"),
    ("r2_histories@income_assets", "histories", "income_assets"),
)
type Network = tuple[str, str, bool]


def fernandez_distances(
    inputs: Inputs, characteristics: tuple[str, ...], tickers: tuple[str, ...]
) -> dict[str, FloatArray]:
    """Equation (9) on the 2015-2024 histories, plus the RMS joint extension."""
    return classical(inputs.four, CUTOFF_YEAR, tickers, characteristics, HISTORY)


def weights(
    distances: dict[str, FloatArray],
    kernels: tuple[Kernel, ...],
    *,
    self_links: tuple[bool, ...] = (False,),
) -> dict[Network, FloatArray]:
    """Every distance under each kernel; matched kernels copy the joint network's spread."""
    target = effective_neighbours(paper_weights(distances[JOINT])) if JOINT in distances else None
    result: dict[Network, FloatArray] = {}
    for name, distance in distances.items():
        for kernel in kernels:
            if kernel == "matched" and target is None:
                continue
            for links in self_links:
                result[name, kernel, links] = kernel_weights(
                    distance, kernel, self_links=links, target=target
                )[0]
    return result


def ladder_distances(  # noqa: PLR0913 -- one arm's inputs plus an optional model subset.
    inputs: Inputs,
    arm: str,
    characteristics: tuple[str, ...],
    tickers: tuple[str, ...],
    output: Path,
    *,
    models: tuple[str, ...] | None = None,
) -> dict[str, FloatArray]:
    """R1 classical controls and R2/R3 representations of the same firms' inputs."""
    result = fernandez_distances(inputs, characteristics, tickers)
    fingerprint = {"arm": arm, "cutoff_year": CUTOFF_YEAR, "code_sha256": code_digest()}
    for name, distance in result.items():
        save(
            output / "distances" / f"{name}.parquet",
            distance,
            tickers,
            fingerprint | {"representation": name, "arm": "fernandez"},
        )
    views = rung_views(inputs.four, inputs.broad, CUTOFF_YEAR, characteristics, HISTORY)
    for label, view, target in PASSES:
        data = context(views[view], labels(inputs.four, inputs.broad, target), tickers, CUTOFF_YEAR)
        record_context(output / "contexts" / f"{label}.json", data, target)
        LOGGER.info(
            "Ladder %s %s: %s firms, %s features", arm, label, len(tickers), len(data.features)
        )
        encoded = representation_distances(
            data, cache=MODEL_CACHE, source=MODEL_SOURCE, models=models or MODELS
        )
        for representation, distance in encoded.items():
            name = f"{label}__{representation}"
            result[name] = distance
            sidecar = fingerprint | {
                "rung": label,
                "target": target,
                "representation": representation,
                "arm": ARMS[representation],
                "context_digest": data.digest,
            }
            save(output / "distances" / f"{name}.parquet", distance, tickers, sidecar)
    return result


def rung_of(name: str) -> str:
    """R1 for classical joint controls, R0 references, else the representation's rung."""
    if name == JOINT:
        return "r1_joint"
    if name.startswith("fernandez_"):
        return "r0_single"
    label, representation = name.split("__", 1)
    if representation in {"direct", "mahalanobis_lw"} and label == "r2_histories":
        return "r1_joint"
    return label


def log_assets(inputs: Inputs, tickers: tuple[str, ...]) -> FloatArray:
    """Point-in-time 2024 log assets, for size-restricted placebo permutations."""
    frame = labels(inputs.four, inputs.broad, "market_cap_assets")
    values = frame["log_assets"].xs(CUTOFF_YEAR - 1, level="year").reindex(list(tickers))
    return values.to_numpy(dtype=float)
