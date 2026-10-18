"""Declared normalization, fold-assignment and intercept-only measurement diagnostics."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.distance import pairwise_distance
from free_foundations.expanded.representations import representation_states
from free_foundations.panel.decoding import decode, folds, intercept_only, targets
from free_foundations.panel.design import DESIGNS, FOUNDATION_MODELS
from free_foundations.panel.evaluation import (
    EVALUATION,
    Panel,
    daily_frame,
    update,
)
from free_foundations.panel.inference import contrasts
from free_foundations.panel.networks import (
    MODEL_CACHE,
    MODEL_SOURCE,
    classical,
    context,
    labels,
    rung_views,
)
from free_foundations.panel.observations import annual_data
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
OUTPUT = Path("research/panel/three-foundations-validation")
PRINCIPAL = (
    "direct",
    "pca16",
    "supervised_mlp16",
    "tabpfn_full__late",
    "tabfm__late",
    "kumo__late",
    "limix__late",
)
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
    return [p for p in pairs if p[1] in columns and p[2] in columns]


def main() -> None:
    """Refit a bounded diagnostic grid using verified states and frozen financial inputs."""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(
        OUTPUT / "configuration.json",
        {
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "protocol_sha256": hashlib.sha256((OUTPUT / "README.md").read_bytes()).hexdigest(),
            "partitions": SALTS,
            "principal": PRINCIPAL,
            "reset_controls": RANDOM,
            "encoder_support": 256,
            "rank": 5,
            "calibration": [2016, 2019],
            "evaluation": [2020, 2025],
            "bootstrap_blocks": [21, 63],
            "bootstrap_replicates": 9999,
            "bootstrap_seed": 42,
        },
    )
    design = DESIGNS["three-foundations"]
    four = pd.read_parquet("research/panel/cache/four.parquet")
    broad = pd.read_parquet("research/panel/cache/broad.parquet")
    panel = Panel(kernels=("matched",), include_placebos=False, diagonal_only=True)
    quality: list[dict[str, object]] = []
    checks: list[dict[str, object]] = []
    firm_days = 0
    for year in range(2016, 2026):
        LOGGER.info("Measurement diagnostics: %s", year)
        annual = annual_data(
            four,
            year,
            characteristics=design.characteristics,
            histories=design.cohort_histories,
            output=OUTPUT,
        )
        view = rung_views(four, broad, year, design.characteristics, design.history)["histories"]
        data = context(view, labels(four, broad, "market_cap_assets"), annual.tickers, year)
        states = representation_states(
            data, cache=MODEL_CACHE, source=MODEL_SOURCE, models=FOUNDATION_MODELS
        )
        exposure = targets(annual.prior, annual.reference, ranks=(5,)).reference[5]
        distances, rows, null = diagnostic_distances(states, exposure, annual.tickers, year)
        distances["fernandez_joint"] = classical(
            four, year, annual.tickers, design.characteristics, design.history
        )["fernandez_joint"]
        quality += rows
        checks += null
        update(panel, year, annual, distances, broad)
        if year in EVALUATION:
            firm_days += annual.raw_realized.size
    daily = daily_frame(panel)
    daily.to_parquet(OUTPUT / "daily-scores.parquet")
    # comparison expects registered representation names; all diagnostic rows share the
    # same estimator, so annual sums and explicit labels are the sufficient summary here.
    summary = pd.DataFrame({"column": daily.columns, "score": daily.sum().to_numpy()})
    summary["firm_days"] = firm_days
    summary["dates"] = len(daily)
    summary.to_csv(OUTPUT / "scores.csv", index=False)
    pd.DataFrame(panel.annual).to_csv(OUTPUT / "annual-scores.csv", index=False)
    pd.DataFrame(quality).to_csv(OUTPUT / "decoding.csv", index=False)
    pd.DataFrame(checks).to_csv(OUTPUT / "null-checks.csv", index=False)
    contrasts(daily, diagnostic_pairs(set(daily.columns))).to_csv(
        OUTPUT / "contrasts.csv", index=False
    )
    saved = pd.read_parquet(design.output / "daily-scores.parquet")
    principal_pairs = [
        (
            "calibrated vs native direct",
            f"histories@decoded__{name}|matched|{arm}",
            f"histories__direct|matched|{arm}",
        )
        for name in PRINCIPAL[3:]
        for arm in ("diagonal", "correlation")
    ]
    contrasts(saved, principal_pairs).to_csv(OUTPUT / "principal-contrasts.csv", index=False)
    if not daily.index.equals(saved.index):
        message = "Diagnostic dates differ from the principal experiment."
        raise ValueError(message)
    overlap = []
    for arm in ("diagonal", "correlation"):
        for name in PRINCIPAL:
            pairs = [
                (f"fold0@decoded__{name}|matched|{arm}", f"histories@decoded__{name}|matched|{arm}")
            ]
            if name != "direct":
                pairs.append(
                    (
                        f"normalization_native_chord__{name}|matched|{arm}",
                        f"histories__{name}|matched|{arm}",
                    )
                )
            for current, previous in pairs:
                error = float(np.max(np.abs(daily[current] - saved[previous])))
                np.testing.assert_allclose(daily[current], saved[previous], atol=1e-5, rtol=0)
                overlap.append({"current": current, "previous": previous, "max_daily_error": error})
        for suffix in ("", "43", "44"):
            np.testing.assert_allclose(
                daily[f"fold0@decoded__intercept_only|matched|{arm}"],
                saved[f"histories@decoded__kumo_random{suffix}__late|matched|{arm}"],
                atol=1e-5,
                rtol=0,
            )
    write_json(
        OUTPUT / "validation.json",
        {"overlap": overlap, "firm_days": firm_days, "dates": len(daily), "partitions": SALTS},
    )
