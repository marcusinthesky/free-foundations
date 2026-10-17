"""Dependence-aware paired uncertainty for daily held-out log-density differences."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from arch.bootstrap import MCS, StationaryBootstrap, optimal_block_length

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

BLOCKS = (21, 63)  # Declared: one and three trading months of expected block length.
REPLICATES = 9999


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
    """Summed daily differences with stationary-bootstrap percentile intervals."""
    columns = [column for column in map(str, daily.columns) if "__placebo" not in column]
    counts = {block: resample_counts(len(daily), block) for block in BLOCKS}
    rows = []
    for column in columns:
        for label, reference in reference_for(column).items():
            if reference not in daily or reference == column:
                continue
            difference = (daily[column] - daily[reference]).to_numpy(dtype=float)
            row: dict[str, str | float] = {
                "column": column,
                "versus": label,
                "reference": reference,
                "difference": float(difference.sum()),
                "politis_white_block": float(
                    optimal_block_length(difference)["stationary"].iloc[0]
                ),
            }
            for block, matrix in counts.items():
                sums = matrix @ difference
                row |= {
                    f"lower_{block}": float(np.percentile(sums, 2.5)),
                    f"upper_{block}": float(np.percentile(sums, 97.5)),
                    f"share_nonpositive_{block}": float(np.mean(sums <= 0)),
                }
            rows.append(row)
    return pd.DataFrame(rows)


def families(daily: pd.DataFrame) -> dict[str, list[str]]:
    """MCS families: networks within one kernel and innovation arm, plus the controls."""
    groups: dict[str, list[str]] = {}
    for column in map(str, daily.columns):
        name, kernel, innovation = column.split("|")
        if "__placebo" in name or innovation == "control":
            continue
        kernels = ("exp", "median", "matched") if kernel == "none" else (kernel,)
        for selected in kernels:
            groups.setdefault(f"{innovation}|{selected}", []).append(column)
    groups["controls|diagonal-exp"] = [
        column
        for column in map(str, daily.columns)
        if "__placebo" not in column and column.endswith(("|control", "|exp|diagonal"))
    ]
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
