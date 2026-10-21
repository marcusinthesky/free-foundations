"""Dependence-aware paired uncertainty for daily held-out log-density differences."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from arch.bootstrap import MCS, StationaryBootstrap, optimal_block_length

from free_foundations.panel.design import PRINCIPAL, RESET_MODELS

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

BLOCKS = (21, 63)  # Declared: one and three trading months of expected block length.
REPLICATES = 9999


@lru_cache(maxsize=2)
def resample_counts(
    days: int, block: int, replicates: int = REPLICATES, seed: int = 42
) -> FloatArray:
    """How often each day appears in each stationary-bootstrap replicate.

    Every comparison reuses the same replicates, so differences remain paired across
    approaches and their bootstrap sums are a single matrix product.
    """
    bootstrap = StationaryBootstrap(block, np.arange(days), seed=seed)
    counts = np.zeros((replicates, days))
    for row, (arguments, _) in enumerate(bootstrap.bootstrap(replicates)):
        counts[row] = np.bincount(arguments[0], minlength=days)
    counts.setflags(write=False)
    return counts


def reference_for(column: str) -> dict[str, str]:
    """The joint Fernández benchmark and the uniform network within the same arm."""
    _, _, innovation = column.split("|")
    if innovation == "control":
        return {"joint": "fernandez_joint|exp|diagonal"}
    return {
        "joint": f"fernandez_joint|exp|{innovation}",
        "uniform": f"uniform_network|none|{innovation}",
    }


def paired(daily: pd.DataFrame) -> pd.DataFrame:
    """Principal daily differences against joint and uniform financial benchmarks."""
    principal = {column for columns in families(daily).values() for column in columns}
    resets = {
        f"histories{suffix}__{model}__late|matched|{arm}"
        for model in RESET_MODELS
        for suffix in ("", "@decoded")
        for arm in ("diagonal", "correlation")
    }
    pairs = [
        (label, column, reference)
        for column in map(str, daily.columns)
        if column in principal | resets
        for label, reference in reference_for(column).items()
        if reference in daily and reference != column
    ]
    if not pairs:
        return pd.DataFrame()
    differences = np.column_stack(
        [(daily[left] - daily[right]).to_numpy(dtype=float) for _, left, right in pairs]
    )
    rows: list[dict[str, str | float]] = [
        {
            "column": left,
            "versus": label,
            "reference": right,
            "difference": float(differences[:, index].sum()),
            "politis_white_block": float(
                optimal_block_length(differences[:, index])["stationary"].iloc[0]
            ),
        }
        for index, (label, left, right) in enumerate(pairs)
    ]
    for block in BLOCKS:
        sums = resample_counts(len(daily), block) @ differences
        lower, upper = np.percentile(sums, [2.5, 97.5], axis=0)
        for index, row in enumerate(rows):
            row |= {
                f"lower_{block}": float(lower[index]),
                f"upper_{block}": float(upper[index]),
                f"share_nonpositive_{block}": float(np.mean(sums[:, index] <= 0)),
            }
    return pd.DataFrame(rows)


def declared_contrasts(columns: set[str]) -> list[tuple[str, str, str]]:
    """Full-context calibration, direct-input and learned-weight comparisons."""
    pairs: list[tuple[str, str, str]] = []
    for arm in ("diagonal", "correlation"):
        for name in PRINCIPAL:
            left = f"histories@decoded__{name}|matched|{arm}"
            pairs.append(("decoded vs native", left, f"histories__{name}|matched|{arm}"))
            if name != "direct":
                pairs.append(("decoded vs native inputs", left, f"histories__direct|matched|{arm}"))
        for model in RESET_MODELS:
            trained = model.partition("_random")[0]
            pairs.extend(
                (
                    "pretrained vs reset",
                    f"histories{suffix}__{trained}__late|matched|{arm}",
                    f"histories{suffix}__{model}__late|matched|{arm}",
                )
                for suffix in ("", "@decoded")
            )
    return [pair for pair in pairs if pair[1] in columns and pair[2] in columns]


def contrasts(daily: pd.DataFrame, pairs: list[tuple[str, str, str]] | None = None) -> pd.DataFrame:
    """Fixed-procedure paired intervals and yearly totals using common time resamples."""
    years = pd.to_datetime(daily.index).year
    selected = declared_contrasts(set(map(str, daily.columns))) if pairs is None else pairs
    if not selected:
        return pd.DataFrame()
    missing = {column for _, left, right in selected for column in (left, right)} - set(
        daily.columns
    )
    if missing:
        message = f"Missing declared contrast scores: {sorted(missing)}"
        raise ValueError(message)
    differences = np.column_stack(
        [(daily[left] - daily[right]).to_numpy(dtype=float) for _, left, right in selected]
    )
    rows: list[dict[str, str | float]] = [
        {
            "contrast": label,
            "left": left,
            "right": right,
            "difference": float(differences[:, index].sum()),
            **{
                f"year_{year}": float(differences[years == year, index].sum())
                for year in sorted(set(years))
            },
        }
        for index, (label, left, right) in enumerate(selected)
    ]
    for block in BLOCKS:
        sums = resample_counts(len(daily), block) @ differences
        lower, upper = np.percentile(sums, [2.5, 97.5], axis=0)
        for index, row in enumerate(rows):
            row |= {f"lower_{block}": float(lower[index]), f"upper_{block}": float(upper[index])}
    return pd.DataFrame(rows)


def families(daily: pd.DataFrame) -> dict[str, list[str]]:
    """Principal matched procedures and the same financial benchmarks in each arm."""
    names = {f"histories{suffix}__{name}" for name in PRINCIPAL for suffix in ("", "@decoded")}
    names |= {
        "zero_network",
        "uniform_network",
        "fernandez_joint",
        "reference_exposures",
        "covariance_exposures",
        "raw_sample_covariance",
        "ff5_mom_diagonal",
        "ff5_mom_sample_residual_covariance",
    }
    groups: dict[str, list[str]] = {}
    for column in map(str, daily.columns):
        name, kernel, innovation = column.split("|")
        arm = "diagonal" if innovation == "control" else innovation
        if name not in names or arm not in ("diagonal", "correlation"):
            continue
        if kernel in {"matched", "none"} or (name == "fernandez_joint" and kernel == "exp"):
            groups.setdefault(f"{arm}|matched", []).append(column)
    return groups


def confidence_set(daily: pd.DataFrame, size: float = 0.10) -> pd.DataFrame:
    """Hansen-Lunde-Nason model confidence sets on daily negative log densities."""
    rows = []
    for family, columns in families(daily).items():
        losses = -daily[columns]
        procedure = MCS(
            losses,
            size=size,
            reps=1000,
            block_size=21,
            method="max",
            bootstrap="stationary",
            seed=42,
        )
        procedure.compute()
        included = set(procedure.included)
        pvalues = procedure.pvalues.iloc[:, 0].to_dict()
        rows.extend(
            {
                "family": family,
                "column": column,
                "p_value": float(pvalues[column]),
                "included": column in included,
            }
            for column in columns
        )
    return pd.DataFrame(rows)
