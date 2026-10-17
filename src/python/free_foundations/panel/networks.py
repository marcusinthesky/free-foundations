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
from free_foundations.expanded.distance import save_distance
from free_foundations.expanded.encoding import cap_support, prepare
from free_foundations.expanded.representations import ARMS, representation_distances
from free_foundations.fernandez.characteristics import history_view
from free_foundations.fernandez.models import rank_distance
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from collections.abc import Mapping

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared
    from free_foundations.panel.design import Design

LOGGER = logging.getLogger(__name__)
MODEL_CACHE, MODEL_SOURCE = Path("research/expanded/cache"), Path("research/pilot/cache")
INCOME = "us-gaap:NetIncomeLoss|USD|annual"
ASSETS = "us-gaap:Assets|USD|instant"
TARGETS = {
    "market_cap_assets": "next annual snapshot market_cap_assets",
    "income_assets": "next annual snapshot NetIncomeLoss / Assets",
}
CODE = (
    "expanded/encoding.py",
    "expanded/baselines.py",
    "expanded/distance.py",
    "expanded/representations.py",
    "fernandez/models.py",
    "panel/networks.py",
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


def context(
    view: pd.DataFrame,
    core: pd.DataFrame,
    tickers: tuple[str, ...],
    year: int,
) -> Prepared:
    """Past-only preprocessing, then the shared deterministic 256-row support cap."""
    return cap_support(prepare(view, core, tickers, year, "income"))


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


def distances(  # noqa: PLR0913 -- design inputs plus an optional model subset.
    four: pd.DataFrame,
    broad: pd.DataFrame,
    year: int,
    tickers: tuple[str, ...],
    design: Design,
    *,
    models: tuple[str, ...] | None = None,
) -> dict[str, FloatArray]:
    """Recompute every network from fingerprinted caches; never reuse a saved matrix."""
    root = design.output
    fingerprint = {"design": design.name, "year": year, "code_sha256": code_digest()}
    result: dict[str, FloatArray] = {}
    for history in (design.history, *design.extra_histories):
        prefix = "" if history == design.history else f"h{history}__"
        for name, distance in classical(
            four, year, tickers, design.characteristics, history
        ).items():
            result[prefix + name] = distance
            save(
                root / "distances" / str(year) / f"{prefix}{name}.parquet",
                distance,
                tickers,
                fingerprint
                | {
                    "history": history,
                    "representation": name,
                    "arm": "fernandez",
                    "metric": "spearman_chord",
                },
                matrix=design.save_matrices,
            )
        views = rung_views(four, broad, year, design.characteristics, history)
        passes = [(rung, "market_cap_assets", rung) for rung in design.rungs]
        shared: dict[str, Prepared] = {}
        if history != design.history:
            passes = [("histories", "market_cap_assets", "histories")]
        elif design.alternate_target:
            # The alternative task pipeline changes support rows and preprocessing with the
            # target; the shared pair changes only the labels.
            passes.append(("histories", "income_assets", "histories@income_assets"))
            shared = shared_contexts(views["histories"], four, broad, tickers, year)
            passes += [("histories", target, f"histories@shared_{target}") for target in shared]
        for rung, target, label in passes:
            data = (
                shared[target]
                if label.startswith(f"{rung}@shared_")
                else context(views[rung], labels(four, broad, target), tickers, year)
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
            options = {} if models is None else {"models": models}
            encoded = representation_distances(
                data, cache=MODEL_CACHE, source=MODEL_SOURCE, **options
            )
            for representation, distance in encoded.items():
                name = f"{prefix}{label}__{representation}"
                result[name] = distance
                save(
                    root / "distances" / str(year) / f"{name}.parquet",
                    distance,
                    tickers,
                    fingerprint
                    | {
                        "history": history,
                        "rung": rung,
                        "target": target,
                        "representation": representation,
                        "arm": ARMS[representation],
                        "context_digest": data.digest,
                        "metric": "euclidean"
                        if representation == "mahalanobis_lw"
                        or representation.startswith("euclidean")
                        else "chord",
                    },
                    matrix=design.save_matrices,
                )
    return result
