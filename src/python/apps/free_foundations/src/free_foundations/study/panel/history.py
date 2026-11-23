"""The shared annual-spaced accounting history used by networks and encoders."""

from __future__ import annotations

import pandas as pd

from free_foundations.study.spec import CHARACTERISTICS

KEYS = ["issuer_id", "quarter"]


def annual_history_slots(panel: pd.DataFrame, current: pd.DataFrame, *, years: int) -> pd.DataFrame:
    """Select current and annual-lag snapshots, preserving query order and missing cells.

    ``current`` has a unique issuer/quarter MultiIndex and wide characteristic
    columns. Quarter labels already identify information available before that
    quarter begins. No intervening quarterly snapshots enter these histories.
    """
    if years < 1:
        message = "Accounting history needs a positive number of annual slots."
        raise ValueError(message)
    if not isinstance(current.index, pd.MultiIndex) or list(current.index.names) != KEYS:
        message = "Accounting snapshots need an issuer_id/quarter MultiIndex."
        raise ValueError(message)
    if current.index.has_duplicates:
        message = "Duplicate accounting snapshots cannot define annual history slots."
        raise ValueError(message)
    current = current.reindex(columns=list(CHARACTERISTICS))
    result = pd.DataFrame(index=pd.MultiIndex.from_frame(panel[KEYS]))
    for lag in range(years):
        earlier = pd.MultiIndex.from_arrays(
            [panel["issuer_id"], panel["quarter"] - pd.DateOffset(years=lag)], names=KEYS
        )
        values = current.reindex(earlier)
        for name in CHARACTERISTICS:
            result[f"original:{name}:annual_lag{lag}"] = values[name].to_numpy(dtype=float)
    return result
