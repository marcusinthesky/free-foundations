"""One distance matrix per representation of a shared prepared support/query table."""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING, Literal

import numpy as np
from sklearn.covariance import LedoitWolf

from free_foundations.expanded.baselines import compression_states, supervised_states
from free_foundations.expanded.distance import pairwise_distance
from free_foundations.expanded.encoding import foundation_states, load_tabfm

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared

type Arm = Literal["classical", "control", "state", "task"]
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "tabfm_labelnull", "exaone")
# Readouts per model run, with the published name and interpretive arm of each.
READOUTS: dict[str, tuple[tuple[str, str, Arm], ...]] = {
    "tabpfn_fast": (("late", "tabpfn_fast__late", "task"),),
    "tabpfn_full": (("late", "tabpfn_full__late", "task"),),
    "tabfm": (
        ("early_concat", "tabfm__early_concat", "state"),
        ("early_mean", "tabfm__early_mean", "state"),
        ("late", "tabfm__late", "task"),
    ),
    "tabfm_labelnull": (("early_concat", "tabfm__early_concat_labelnull", "state"),),
    "exaone": (
        ("late", "exaone__late", "task"),
        ("item_first_concat", "exaone__item_first_concat", "state"),
        ("item_first_mean", "exaone__item_first_mean", "state"),
        ("item_last_concat", "exaone__item_last_concat", "task"),
    ),
}
# Direct-distance ablations: which feature groups a classical distance keeps. Size is
# log assets and share counts; indicators are the imputer's missingness columns.
ABLATIONS: dict[str, tuple[str, ...]] = {
    "": (),
    "_no_indicators": ("missingindicator_",),
    "_no_size": ("log_assets", "|shares|"),
    "_no_changes": ("|change_1y",),
}
CLASSICAL: Arm = "classical"
ARMS: dict[str, Arm] = {
    "direct": "classical",
    "mahalanobis_lw": "classical",
    **{
        f"{metric}{suffix}": CLASSICAL
        for metric in ("direct", "euclidean")
        for suffix in ABLATIONS
        if f"{metric}{suffix}" != "direct"
    },
    "pca16": "control",
    "autoencoder": "control",
    "random_autoencoder": "control",
    "supervised_mlp16": "task",
    **{name: arm for readouts in READOUTS.values() for _, name, arm in readouts},
}


def mahalanobis_distance(data: Prepared) -> FloatArray:
    """Euclidean distance after whitening by a Ledoit-Wolf covariance of support rows."""
    estimate = LedoitWolf().fit(data.support)
    factor = np.linalg.cholesky(estimate.covariance_)
    whitened = np.linalg.solve(factor, (data.query - estimate.location_).T).T
    return pairwise_distance(whitened, metric="euclidean")


def ablated_distances(data: Prepared) -> dict[str, FloatArray]:
    """Standardized Euclidean distance, and both direct metrics without each feature group.

    ``direct`` is the chord distance on ``[x, 1]``: angular, so firms with proportional
    standardized vectors are close. ``euclidean`` keeps magnitude.
    """
    distances = {}
    for suffix, dropped in ABLATIONS.items():
        keep = [
            position
            for position, name in enumerate(data.features)
            if not any(part in name for part in dropped)
        ]
        if not suffix:
            distances["euclidean"] = pairwise_distance(data.query, metric="euclidean")
        elif len(keep) < len(data.features):
            query = data.query[:, keep]
            distances[f"direct{suffix}"] = pairwise_distance(
                np.column_stack([query, np.ones(len(query))])
            )
            distances[f"euclidean{suffix}"] = pairwise_distance(query, metric="euclidean")
    return distances


def representation_distances(
    data: Prepared,
    *,
    cache: Path,
    source: Path,
    models: tuple[str, ...] = MODELS,
) -> dict[str, FloatArray]:
    """Classical, control and frozen-model distances; learned rows use chord distance."""
    distances = {
        "direct": pairwise_distance(np.column_stack([data.query, np.ones(len(data.query))])),
        "mahalanobis_lw": mahalanobis_distance(data),
        **ablated_distances(data),
    }
    for name, states in compression_states(data).items():
        distances[name] = pairwise_distance(states)
    distances["supervised_mlp16"] = pairwise_distance(supervised_states(data))
    for model in models:
        states = foundation_states(data, model, cache, source)
        for readout, name, _ in READOUTS[model]:
            distances[name] = pairwise_distance(states[readout])
        load_tabfm.cache_clear()
        gc.collect()
    return distances
