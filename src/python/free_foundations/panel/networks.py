"""Annual input ladders and cached foundation-model distance matrices."""

from __future__ import annotations

import gc
import hashlib
import json
import logging
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.expanded.baselines import compression_states
from free_foundations.expanded.disclosures import input_views
from free_foundations.expanded.distance import pairwise_distance, save_distance
from free_foundations.expanded.encoding import foundation_states, load_tabfm, prepare
from free_foundations.fernandez.characteristics import CHARACTERISTICS, history_view
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.panel.characteristics import ROOT
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")


def networks(
    four: pd.DataFrame, broad: pd.DataFrame, year: int, tickers: tuple[str, ...]
) -> dict[str, FloatArray]:
    """Persist the complete distance matrix for every model at every annual cutoff."""
    history = history_view(four, 3)
    query = history.xs(year - 1, level="year").loc[list(tickers)]
    distances = {
        f"fernandez_{name}": rank_distance(query.filter(like=f"{name}__").to_numpy(dtype=float))
        for name in CHARACTERISTICS
    }
    distances["fernandez_joint_four"] = np.sqrt(
        np.mean([value**2 for value in distances.values()], axis=0)
    )
    core = pd.DataFrame(index=four.index)
    core["log_assets"] = np.log(broad["us-gaap:Assets|USD|instant"].where(lambda x: x > 0))
    # Labels are next-year publicly disclosed capitalization/assets, never future returns.
    core["income"] = four["market_cap_assets"]
    core["operating_cash"] = core["income"]
    views = {
        "four": history,
        "broad": pd.concat([history, input_views(core, broad, year)["broad"]], axis=1),
        "metrics": pd.concat([history, input_views(core, broad, year)["metrics"]], axis=1),
    }
    for rung, view in views.items():
        data = prepare(view, core, tickers, year, "income")
        # Fixed, outcome-independent support cap for CPU tractability across all encoders.
        order = sorted(
            range(len(data.support_ids)),
            key=lambda i: hashlib.sha256(data.support_ids[i].encode()).hexdigest(),
        )[:256]
        digest = hashlib.sha256(
            (data.digest + repr(order) + "panel-support256-v1").encode()
        ).hexdigest()
        data = replace(
            data,
            support=data.support[order],
            targets=data.targets[order],
            support_ids=tuple(data.support_ids[i] for i in order),
            digest=digest,
        )
        context_path = ROOT / "contexts" / f"{year}-{rung}.json"
        if context_path.exists() and json.loads(context_path.read_text())["digest"] != data.digest:
            message = "Cached context changed; move the old panel output before rerunning."
            raise ValueError(message)
        write_json(
            context_path,
            {
                "support_ids": data.support_ids,
                "features": data.features,
                "tickers": tickers,
                "digest": data.digest,
                "target": "next annual snapshot market_cap_assets",
                "preprocessing": "fit on all past support rows; deterministic 256-row encoder cap",
                "cutoff": f"{year - 1}-12-31",
                "rows": len(data.support),
            },
        )
        methods = ("direct", "pca16", "autoencoder", "random_autoencoder", *MODELS)
        for method in methods:
            name = f"{rung}__{method}"
            path = ROOT / "distances" / str(year) / f"{name}.parquet"
            if path.exists():
                cached = pd.read_parquet(path)
                if tuple(cached.index) != tickers:
                    message = "Cached network cohort differs; use a fresh output directory."
                    raise ValueError(message)
                distances[name] = cached.to_numpy(dtype=float)
                continue
            LOGGER.info(
                "Encoding %s / %s: %s firms, %s features",
                year,
                name,
                len(tickers),
                len(data.features),
            )
            if method == "direct":
                vectors = np.column_stack([data.query, np.ones(len(tickers))])
            elif method in {"pca16", "autoencoder", "random_autoencoder"}:
                # Save the three controls together, fitting only on historical support.
                for control, states in compression_states(data).items():
                    distance = pairwise_distance(states)
                    distances[f"{rung}__{control}"] = distance
                    save_distance(
                        ROOT / "distances" / str(year) / f"{rung}__{control}.parquet",
                        distance,
                        tickers,
                    )
                continue
            else:
                vectors = foundation_states(
                    data, method, Path("research/expanded/cache"), Path("research/pilot/cache")
                )["late"]
                load_tabfm.cache_clear()
                gc.collect()
            distances[name] = pairwise_distance(vectors)
            save_distance(path, distances[name], tickers)
    for name, distance in distances.items():
        save_distance(ROOT / "distances" / str(year) / f"{name}.parquet", distance, tickers)
    return {name: paper_weights(distance) for name, distance in distances.items()}
