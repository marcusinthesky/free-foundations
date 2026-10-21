"""Fixed histories, valuation contexts, and distances from saved query states."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.data import write_json
from free_foundations.fernandez.characteristics import history_view
from free_foundations.fernandez.models import rank_distance
from free_foundations.panel.decoding import FACTORS, decode
from free_foundations.panel.design import CALIBRATION_SIZES, PRINCIPAL
from free_foundations.representations.distance import pairwise_distance
from free_foundations.representations.encoding import cap_support, prepare

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.panel.decoding import Targets
    from free_foundations.representations.encoding import Prepared

MODEL_CACHE, MODEL_SOURCE = Path("research/expanded/cache"), Path("research/pilot/cache")
ASSETS = "us-gaap:Assets|USD|instant"


def classical(
    four: pd.DataFrame,
    year: int,
    tickers: tuple[str, ...],
    characteristics: tuple[str, ...],
    history: int,
) -> dict[str, FloatArray]:
    """Original characteristic distances and the explicitly labeled RMS joint extension."""
    query = pd.DataFrame(
        history_view(four[list(characteristics)], history).xs(year - 1, level="year")
    ).loc[list(tickers)]
    distances = {
        f"fernandez_{name}": rank_distance(query.filter(like=f"{name}__").to_numpy(dtype=float))
        for name in characteristics
    }
    distances["fernandez_joint"] = np.sqrt(np.mean([d**2 for d in distances.values()], axis=0))
    return distances


def labels(four: pd.DataFrame, broad: pd.DataFrame) -> pd.DataFrame:
    """The original valuation label and support-row availability convention."""
    core = pd.DataFrame(index=four.index)
    core["log_assets"] = np.log(broad[ASSETS].where(lambda values: values > 0).reindex(four.index))
    core["income"] = four["market_cap_assets"]
    core["operating_cash"] = core["income"]
    return core.replace([np.inf, -np.inf], np.nan)


def context(
    view: pd.DataFrame, core: pd.DataFrame, tickers: tuple[str, ...], year: int, *, rows: int = 256
) -> Prepared:
    """Past-only fitted preprocessing with nested hash-ordered context examples."""
    return cap_support(prepare(view, core, tickers, year, "income"), rows=rows)


def record_context(path: Path, data: Prepared) -> None:
    """Record the actual ordered examples, predictors, and query cohort."""
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json(
        path,
        {
            "support_ids": data.support_ids,
            "features": data.features,
            "tickers": data.tickers,
            "digest": data.digest,
            "target": "next annual snapshot market_cap_assets",
            "preprocessing": "fit on all past support rows; nested hash-ordered encoder cap",
            "cutoff": f"{data.year - 1}-12-31",
            "rows": len(data.support),
        },
    )


def distances(  # noqa: PLR0913, PLR0917 -- common states, target, sample and audit.
    states: dict[str, FloatArray],
    calibration: Targets,
    tickers: tuple[str, ...],
    year: int,
    support: int,
    quality: list[dict[str, object]],
) -> dict[str, FloatArray]:
    """Principal distances and bounded sample-size comparisons from saved states."""
    label = "histories" if support == 256 else f"histories@support{support}"
    result: dict[str, FloatArray] = {}
    for name, values in states.items():
        if support != 256 and name == "direct":
            continue
        native = np.column_stack([values, np.ones(len(values))]) if name == "direct" else values
        result[f"{label}__{name}"] = pairwise_distance(native)
        predicted, fit = decode(values, calibration.reference[FACTORS], tickers)
        quality.append(
            {
                "year": year,
                "rung": label,
                "support_rows": support,
                "representation": name,
                "rank": FACTORS,
                **fit,
            }
        )
        result[f"{label}@decoded__{name}"] = pairwise_distance(predicted, metric="euclidean")
        if support == 256 and name in PRINCIPAL:
            for size in CALIBRATION_SIZES:
                predicted, fit = decode(
                    values, calibration.reference[FACTORS], tickers, training_size=size
                )
                rung = f"histories@calibration{size}"
                quality.append(
                    {
                        "year": year,
                        "rung": rung,
                        "support_rows": support,
                        "calibration_rows": size,
                        "representation": name,
                        "rank": FACTORS,
                        **fit,
                    }
                )
                result[f"{rung}@decoded__{name}"] = pairwise_distance(predicted, metric="euclidean")
    return result
