"""In-sample interval helpers: quarter resampling schedules, percentiles and Holm."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from collections.abc import Iterable

    from numpy.typing import NDArray


def block_length(series: NDArray[np.float64]) -> float:
    """Politis-White (Patton correction) expected stationary block length, at least one."""
    from statadic.inference.resampling.block_length import (  # noqa: PLC0415
        optimal_block_length_numpy,
    )

    values = np.asarray(series, dtype=float)
    values = values[np.isfinite(values)]
    if len(values) < 8:
        return 1.0
    return max(1.0, float(optimal_block_length_numpy(values, scheme="stationary")))


@lru_cache(maxsize=16)
def stationary_orders(periods: int, draws: int, block: float, seed: int) -> NDArray[np.int64]:
    """Politis-Romano stationary bootstrap orders over a quarterly calendar.

    Blocks continue with probability ``1 - 1/block`` and wrap around the calendar;
    new blocks start uniformly.
    """
    if periods < 0 or draws < 0 or block < 1:
        msg = "Calendar length/draws must be nonnegative and the block at least one."
        raise ValueError(msg)
    orders = np.empty((draws, periods), dtype=np.int64)
    if periods and draws:
        rng = np.random.default_rng(seed)
        orders[:, 0] = rng.integers(periods, size=draws)
        for position in range(1, periods):
            restart = rng.random(draws) < 1 / block
            starts = rng.integers(periods, size=draws)
            orders[:, position] = np.where(restart, starts, (orders[:, position - 1] + 1) % periods)
    orders.setflags(write=False)
    return orders


def generated_beta_indices(
    quarters: Iterable[object], draws: int, block: float, seed: int
) -> pd.DataFrame:
    """Replicate zero is the original calendar; later replicates resample quarters.

    Failed refits remain failed replicates; no spare draws replace them.
    """
    labels = pd.to_datetime([str(value) for value in quarters]).strftime("%Y-%m-%d").to_numpy()
    orders = stationary_orders(len(labels), draws, block, seed)
    all_orders = np.vstack([np.arange(len(labels), dtype=np.int64), orders])
    return pd.DataFrame(
        {
            "replicate": np.repeat(np.arange(draws + 1), len(labels)),
            "position": np.tile(np.arange(len(labels)), draws + 1),
            "quarter": labels[all_orders.ravel()],
        }
    )


def percentile_interval(values: NDArray[np.float64]) -> tuple[float, float, int]:
    """Two-sided 95% percentile interval over finite draws, with their count."""
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if not len(finite):
        return float("nan"), float("nan"), 0
    lower, upper = np.percentile(finite, [2.5, 97.5])
    return float(lower), float(upper), len(finite)


def holm(pvalues: pd.Series) -> pd.Series:
    """Holm step-down familywise adjustment; missing p-values stay missing."""
    finite = pvalues.dropna().sort_values()
    count = len(finite)
    adjusted = np.maximum.accumulate((count - np.arange(count)) * finite.to_numpy(float))
    result = pd.Series(np.minimum(adjusted, 1.0), index=finite.index)
    return result.reindex(pvalues.index)
