"""Annual input ladders and fingerprinted distance matrices for each panel design."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.disclosures import input_views
from free_foundations.expanded.distance import pairwise_distance, save_distance
from free_foundations.expanded.encoding import cap_support, prepare
from free_foundations.expanded.representations import (
    ARMS,
    MODELS,
    representation_distances,
    representation_states,
)
from free_foundations.fernandez.characteristics import history_view
from free_foundations.fernandez.models import rank_distance
from free_foundations.panel.decoding import FACTORS, decode
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from collections.abc import Mapping

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared
    from free_foundations.panel.decoding import Targets
    from free_foundations.panel.design import Design

LOGGER = logging.getLogger(__name__)
MODEL_CACHE, MODEL_SOURCE = Path("research/expanded/cache"), Path("research/pilot/cache")
INCOME = "us-gaap:NetIncomeLoss|USD|annual"
ASSETS = "us-gaap:Assets|USD|instant"
TARGETS = {
    "market_cap_assets": "next annual snapshot market_cap_assets",
    "income_assets": "next annual snapshot NetIncomeLoss / Assets",
}
# Distances computed from query rows and all-past preprocessing only: no support draw.
QUERY_ONLY = ("direct", "euclidean")
# Readouts that see support labels, so the two shared targets can differ.
LABELLED = frozenset(
    {name for name, arm in ARMS.items() if arm == "task"}
    | {"tabfm__early_concat", "tabfm__early_mean", "kumo__early_concat"}
)
CODE = (
    "expanded/encoding.py",
    "expanded/foundations.py",
    "expanded/baselines.py",
    "expanded/distance.py",
    "expanded/representations.py",
    "fernandez/models.py",
    "panel/networks.py",
    "panel/decoding.py",
)


def code_digest() -> str:
    """Hash every source file that can change a saved distance."""
    root = Path(__file__).parent.parent
    digest = hashlib.sha256()
    for name in CODE:
        digest.update((root / name).read_bytes())
    return digest.hexdigest()


def classical(
    four: pd.DataFrame,
    year: int,
    tickers: tuple[str, ...],
    characteristics: tuple[str, ...],
    history: int,
) -> dict[str, FloatArray]:
    """Equation (9) per characteristic and our RMS joint extension over the design's set."""
    query = pd.DataFrame(
        history_view(four[list(characteristics)], history).xs(year - 1, level="year")
    ).loc[list(tickers)]
    distances = {
        f"fernandez_{name}": rank_distance(query.filter(like=f"{name}__").to_numpy(dtype=float))
        for name in characteristics
    }
    distances["fernandez_joint"] = np.sqrt(np.mean([d**2 for d in distances.values()], axis=0))
    return distances


def labels(
    four: pd.DataFrame, broad: pd.DataFrame, target: str, *, shared: bool = False
) -> pd.DataFrame:
    """Support labels and log assets; ``income`` is the encoder interface's label column.

    Support rows need both label columns. ``shared`` puts the other target in the second
    column, so both targets select the same support rows and fit the same preprocessing.
    """
    core = pd.DataFrame(index=four.index)
    assets = broad[ASSETS].where(lambda values: values > 0).reindex(four.index)
    core["log_assets"] = np.log(assets)
    values = {
        "market_cap_assets": four["market_cap_assets"],
        "income_assets": broad[INCOME].reindex(four.index) / assets,
    }
    core["income"] = values[target]
    other = next(name for name in values if name != target)
    core["operating_cash"] = values[other] if shared else core["income"]
    return core.replace([np.inf, -np.inf], np.nan)


def shared_contexts(
    view: pd.DataFrame,
    four: pd.DataFrame,
    broad: pd.DataFrame,
    tickers: tuple[str, ...],
    year: int,
) -> dict[str, Prepared]:
    """Both support targets on identical support rows and inputs; only the labels differ."""
    contexts = {
        target: context(view, labels(four, broad, target, shared=True), tickers, year)
        for target in TARGETS
    }
    first, second = contexts.values()
    if (
        first.support_ids != second.support_ids
        or not np.array_equal(first.support, second.support)
        or not np.array_equal(first.query, second.query)
    ):
        message = f"Shared-support contexts differ beyond their labels in {year}."
        raise ValueError(message)
    return contexts


def rung_views(
    four: pd.DataFrame,
    broad: pd.DataFrame,
    year: int,
    characteristics: tuple[str, ...],
    history: int,
) -> dict[str, pd.DataFrame]:
    """Histories alone, plus broad signed-log levels, plus normalized metrics."""
    histories = history_view(four[list(characteristics)], history)
    core = labels(four, broad, "market_cap_assets")
    views = input_views(core, broad, year)
    return {
        "histories": histories,
        "broad": pd.concat([histories, views["broad"]], axis=1),
        "metrics": pd.concat([histories, views["metrics"]], axis=1),
    }


def context(  # noqa: PLR0913 -- the support draw and size are keyword options.
    view: pd.DataFrame,
    core: pd.DataFrame,
    tickers: tuple[str, ...],
    year: int,
    salt: str = "",
    *,
    rows: int = 256,
) -> Prepared:
    """Past-only preprocessing, then the shared deterministic 256-row support cap.

    A ``salt`` draws a different, equally outcome-independent set of 256 support rows.
    A smaller ``rows`` keeps a prefix of the same hash order, so supports are nested.
    """
    return cap_support(prepare(view, core, tickers, year, "income"), rows=rows, salt=salt)


def combined(first: FloatArray, second: FloatArray) -> FloatArray:
    """RMS of two distances: the chord distance of concatenated, separately normalized states.

    For unit vectors, |[u, v] - [u', v']|^2 / 2 = (|u - u'|^2 + |v - v'|^2) / 2.
    """
    return np.sqrt((first**2 + second**2) / 2)


def record_context(path: Path, data: Prepared, target: str) -> None:
    """Refuse to silently mix outputs from a different context in one directory."""
    if path.exists() and json.loads(path.read_text())["digest"] != data.digest:
        message = f"Context changed for {path}; move the old design output before rerunning."
        raise ValueError(message)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        path,
        {
            "support_ids": data.support_ids,
            "features": data.features,
            "tickers": data.tickers,
            "digest": data.digest,
            "target": TARGETS[target],
            "preprocessing": "fit on all past support rows; deterministic 256-row encoder cap",
            "cutoff": f"{data.year - 1}-12-31",
            "rows": len(data.support),
        },
    )


def save(
    path: Path,
    distance: FloatArray,
    tickers: tuple[str, ...],
    sidecar: Mapping[str, object],
    *,
    matrix: bool = True,
) -> None:
    """Persist the fingerprint that produced a distance and, optionally, the float32 matrix."""
    if matrix:
        save_distance(path, distance.astype(np.float32).astype(float), tickers)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(path.with_suffix(".json"), dict(sidecar))


def distances(  # noqa: C901, PLR0912, PLR0913, PLR0915 -- design inputs, model subset and targets.
    four: pd.DataFrame,
    broad: pd.DataFrame,
    year: int,
    tickers: tuple[str, ...],
    design: Design,
    *,
    models: tuple[str, ...] | None = None,
    targets: Targets | None = None,
    quality: list[dict[str, float | str | int]] | None = None,
) -> dict[str, FloatArray]:
    """Recompute every network from fingerprinted caches; never reuse a saved matrix.

    ``targets`` are the year's calibration targets for ``tickers``. With them, the design's
    primary history rung and each smaller support yield decoded networks, alongside the
    ``reference_exposures`` and in-panel ``covariance_exposures`` controls. Decoder quality
    at every audited rank is appended to ``quality``.
    """
    root = design.output
    fingerprint = {"design": design.name, "year": year, "code_sha256": code_digest()}
    result: dict[str, FloatArray] = {}

    def wanted(representation: str) -> bool:
        return design.representations is None or representation in design.representations

    def keep(name: str, distance: FloatArray, sidecar: Mapping[str, object]) -> None:
        result[name] = distance
        save(
            root / "distances" / str(year) / f"{name}.parquet",
            distance,
            tickers,
            fingerprint | dict(sidecar),
            matrix=design.save_matrices,
        )

    if targets is not None:
        keep(
            "covariance_exposures",
            pairwise_distance(targets.covariance, metric="euclidean"),
            {
                "representation": "covariance_exposures",
                "target": f"rank-{FACTORS} coordinates of prior residual covariance (in-panel)",
                "arm": "control",
                "metric": "euclidean",
            },
        )
        keep(
            "reference_exposures",
            pairwise_distance(targets.reference[FACTORS], metric="euclidean"),
            {
                "representation": "reference_exposures",
                "target": f"exposures to rank-{FACTORS} reference residual factors",
                "arm": "control",
                "metric": "euclidean",
            },
        )
    for history in (design.history, *design.extra_histories):
        prefix = "" if history == design.history else f"h{history}__"
        for name, distance in classical(
            four, year, tickers, design.characteristics, history
        ).items():
            keep(
                prefix + name,
                distance,
                {
                    "history": history,
                    "representation": name,
                    "arm": "fernandez",
                    "metric": "spearman_chord",
                },
            )
        if history != design.history and not design.encode_extra_histories:
            continue
        views = rung_views(four, broad, year, design.characteristics, history)
        passes = [(rung, "market_cap_assets", rung, "") for rung in design.rungs]
        shared: dict[str, Prepared] = {}
        if history != design.history:
            passes = [("histories", "market_cap_assets", "histories", "")]
        else:
            if design.alternate_target:
                # The alternative task pipeline changes support rows and preprocessing with
                # the target; the shared pair changes only the labels.
                passes.append(("histories", "income_assets", "histories@income_assets", ""))
                shared = shared_contexts(views["histories"], four, broad, tickers, year)
                passes += [
                    ("histories", target, f"histories@shared_{target}", "") for target in shared
                ]
            passes += [
                ("histories", "market_cap_assets", f"histories@{salt}", salt)
                for salt in design.support_draws
            ]
            passes += [
                ("histories", "market_cap_assets", f"histories@support{rows}", "")
                for rows in design.support_sizes
            ]
        encodings: dict[str, dict[str, FloatArray]] = {}
        for rung, target, label, salt in passes:
            rows = int(label.removeprefix("histories@support")) if "@support" in label else 256
            data = (
                shared[target]
                if label.startswith(f"{rung}@shared_")
                else context(
                    views[rung], labels(four, broad, target), tickers, year, salt, rows=rows
                )
            )
            record_context(root / "contexts" / f"{year}-{prefix}{label}.json", data, target)
            LOGGER.info(
                "%s %s %s: %s firms, %s features",
                design.name,
                year,
                prefix + label,
                len(tickers),
                len(data.features),
            )
            selected = models or design.models or MODELS
            states = None
            # Query-only rows do not depend on the support, so smaller supports skip them.
            resized = rows != 256
            if targets is not None and not prefix and (label == "histories" or resized):
                states = representation_states(
                    data, cache=MODEL_CACHE, source=MODEL_SOURCE, models=selected
                )
                for representation, values in states.items():
                    if not wanted(representation) or (
                        resized and representation.startswith(QUERY_ONLY)
                    ):
                        continue
                    for rank, exposures in sorted(targets.reference.items()):
                        decoded, fit = decode(values, exposures, tickers)
                        if quality is not None:
                            quality.append(
                                {
                                    "year": year,
                                    "rung": label,
                                    "support_rows": len(data.support),
                                    "representation": representation,
                                    "rank": rank,
                                }
                                | fit
                            )
                        if rank != FACTORS:
                            continue
                        keep(
                            f"{label}@decoded__{representation}",
                            pairwise_distance(decoded, metric="euclidean"),
                            {
                                "history": history,
                                "rung": rung,
                                "target": f"exposures to rank-{FACTORS} reference residual factors",
                                "representation": representation,
                                "arm": "calibrated",
                                "context_digest": data.digest,
                                "support_rows": len(data.support),
                                "metric": "euclidean",
                            }
                            | fit,
                        )
                    # Vary financial calibration independently of encoder support.
                    if label == "histories" and representation in {
                        "direct",
                        "pca16",
                        "supervised_mlp16",
                        "tabpfn_full__late",
                        "tabfm__late",
                        "kumo__late",
                        "limix__late",
                    }:
                        for size in design.calibration_sizes:
                            decoded, fit = decode(
                                values,
                                targets.reference[FACTORS],
                                tickers,
                                training_size=size,
                            )
                            calibration_label = f"histories@calibration{size}"
                            if quality is not None:
                                quality.append(
                                    {
                                        "year": year,
                                        "rung": calibration_label,
                                        "support_rows": len(data.support),
                                        "calibration_rows": size,
                                        "representation": representation,
                                        "rank": FACTORS,
                                    }
                                    | fit
                                )
                            keep(
                                f"{calibration_label}@decoded__{representation}",
                                pairwise_distance(decoded, metric="euclidean"),
                                {
                                    "history": history,
                                    "rung": rung,
                                    "representation": representation,
                                    "arm": "calibrated",
                                    "context_digest": data.digest,
                                    "support_rows": len(data.support),
                                    "calibration_rows": size,
                                    "metric": "euclidean",
                                }
                                | fit,
                            )
            encoded = representation_distances(
                data, cache=MODEL_CACHE, source=MODEL_SOURCE, states=states, models=selected
            )
            encodings[label] = encoded
            for representation, distance in encoded.items():
                if not wanted(representation):
                    continue
                # A redraw or smaller support changes only support-fitted representations.
                if (salt or resized) and representation.startswith(QUERY_ONLY):
                    continue
                keep(
                    f"{prefix}{label}__{representation}",
                    distance,
                    {
                        "history": history,
                        "rung": rung,
                        "target": target,
                        "representation": representation,
                        "arm": ARMS[representation],
                        "context_digest": data.digest,
                        "support_salt": salt,
                        "metric": "euclidean"
                        if representation == "mahalanobis_lw"
                        or representation.startswith("euclidean")
                        else "chord",
                    },
                )
        if shared:
            first, second = (encodings[f"histories@shared_{target}"] for target in shared)
            for representation, distance in first.items():
                # Label-free readouts are identical across the pair; only combine the rest.
                if representation in LABELLED:
                    keep(
                        f"histories@shared_both__{representation}",
                        combined(distance, second[representation]),
                        {
                            "history": history,
                            "rung": "histories",
                            "target": "both shared targets (RMS of distances)",
                            "representation": representation,
                            "arm": ARMS[representation],
                            "metric": "rms_of_two",
                        },
                    )
    return result
