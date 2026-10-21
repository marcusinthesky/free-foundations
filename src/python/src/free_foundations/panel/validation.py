"""Declared normalization, fold-assignment and intercept-only measurement diagnostics."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from free_foundations.panel.decoding import decode, folds, intercept_only
from free_foundations.panel.design import PRINCIPAL
from free_foundations.representations.distance import pairwise_distance

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

RANDOM = tuple(f"tabpfn_full_random{seed}__late" for seed in ("", "43", "44"))
SALTS = ("", "fold-audit-1", "fold-audit-2", "fold-audit-3", "fold-audit-4")


def diagnostic_distances(
    states: dict[str, FloatArray],
    exposure: FloatArray,
    tickers: tuple[str, ...],
    year: int,
) -> tuple[dict[str, FloatArray], list[dict[str, object]], list[dict[str, object]]]:
    """Cross normalization on the original partition; refit readouts on four fixed partitions."""
    distances: dict[str, FloatArray] = {}
    quality: list[dict[str, object]] = []
    null_checks: list[dict[str, object]] = []
    null = intercept_only(exposure, tickers)
    null_distances = pairwise_distance(null, metric="euclidean")
    for suffix in ("", "43", "44"):
        name = f"kumo_random{suffix}__late"
        predicted, _ = decode(states[name], exposure, tickers)
        np.testing.assert_allclose(predicted, null, atol=1e-12, rtol=0)
        np.testing.assert_allclose(
            pairwise_distance(predicted, metric="euclidean"), null_distances, atol=1e-12, rtol=0
        )
        null_checks.append(
            {
                "year": year,
                "representation": name,
                "feature_spread": float(np.ptp(states[name], axis=0).max()),
                "prediction_max_error": float(np.abs(predicted - null).max()),
                "prediction_vectors": len(np.unique(predicted, axis=0)),
            }
        )
    baseline: dict[str, FloatArray] = {}
    for partition, salt in enumerate(SALTS):
        assigned = folds(tickers, salt=salt)
        for name in (*PRINCIPAL, *RANDOM, "intercept_only"):
            if name == "intercept_only":
                predicted = intercept_only(exposure, tickers, fold_salt=salt)
                fit = {
                    "decoder_r2": 1
                    - float(
                        np.sum((exposure - predicted) ** 2)
                        / np.sum((exposure - exposure.mean(axis=0)) ** 2)
                    )
                }
            else:
                predicted, fit = decode(states[name], exposure, tickers, fold_salt=salt)
            distance = pairwise_distance(predicted, metric="euclidean")
            label = f"fold{partition}@decoded__{name}"
            distances[label] = distance
            if partition == 0:
                baseline[name] = distance
            same = assigned[:, None] == assigned[None, :]
            np.fill_diagonal(same, val=False)
            quality.append(
                {
                    "year": year,
                    "partition": partition,
                    "salt": salt,
                    "representation": name,
                    "within_fold_distance": float(distance[same].mean()),
                    "between_fold_distance": float(
                        distance[~(assigned[:, None] == assigned[None, :])].mean()
                    ),
                    "distance_rmse_vs_original": float(
                        np.sqrt(np.mean((distance - baseline[name]) ** 2))
                    ),
                    **fit,
                }
            )
            if partition == 0 and name in PRINCIPAL:
                for kind, values in (("native", states[name]), ("decoded", predicted)):
                    for metric in ("euclidean", "chord"):
                        distances[f"normalization_{kind}_{metric}__{name}"] = pairwise_distance(
                            values, metric=metric
                        )
    distances["published_native__direct"] = pairwise_distance(
        np.column_stack([states["direct"], np.ones(len(tickers))])
    )
    return distances, quality, null_checks


def diagnostic_pairs(columns: set[str]) -> list[tuple[str, str, str]]:
    """Pair specified contrasts, preserving covariance arms and daily observations."""
    pairs: list[tuple[str, str, str]] = []
    for arm in ("diagonal", "correlation"):

        def column(name: str, arm: str = arm) -> str:
            return f"{name}|matched|{arm}"

        for name in PRINCIPAL:
            pairs.extend(
                (
                    "normalization",
                    column(f"normalization_{kind}_euclidean__{name}"),
                    column(f"normalization_{kind}_chord__{name}"),
                )
                for kind in ("native", "decoded")
            )
            pairs.extend(
                (
                    "calibration within metric",
                    column(f"normalization_decoded_{metric}__{name}"),
                    column(f"normalization_native_{metric}__{name}"),
                )
                for metric in ("euclidean", "chord")
            )
            for partition in range(len(SALTS)):
                left = column(f"fold{partition}@decoded__{name}")
                pairs.append(
                    ("calibrated vs native direct", left, column("published_native__direct"))
                )
                pairs.append(
                    (
                        "calibrated vs intercept only",
                        left,
                        column(f"fold{partition}@decoded__intercept_only"),
                    )
                )
                if partition:
                    pairs.append(("fold assignment", left, column(f"fold0@decoded__{name}")))
        pairs.extend(
            (
                "pretrained vs reset",
                column(f"fold{partition}@decoded__tabpfn_full__late"),
                column(f"fold{partition}@decoded__{name}"),
            )
            for partition in range(len(SALTS))
            for name in RANDOM
        )
        pairs.append(
            (
                "direct unit coordinate",
                column("published_native__direct"),
                column("normalization_native_chord__direct"),
            )
        )
    required = {column for _, left, right in pairs for column in (left, right)}
    if missing := required - columns:
        message = f"Incomplete diagnostic scores: {sorted(missing)}"
        raise ValueError(message)
    return pairs
