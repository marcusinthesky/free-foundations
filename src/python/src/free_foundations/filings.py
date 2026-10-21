"""Annual filing facts with explicit concepts, units, periods and original dates."""

from typing import Any

import numpy as np
import pandas as pd

UNITS = {"USD", "shares", "USD/shares", "pure"}


def broad_facts(payload: dict[str, Any]) -> pd.DataFrame:
    """Preserve concept, unit, and stock/annual-flow distinctions; discard other durations."""
    records = []
    for tag, concept in payload["facts"].get("us-gaap", {}).items():
        for unit, observations in concept["units"].items():
            if unit in UNITS:
                records.extend(
                    {"tag": tag, "unit": unit, **row}
                    for row in observations
                    if row.get("form") in {"10-K", "10-K/A"}
                )
    frame = pd.DataFrame(records).reindex(
        columns=["tag", "unit", "val", "start", "end", "filed", "accn"]
    )
    for name in ("start", "end", "filed"):
        frame[name] = pd.to_datetime(frame[name])
    days = (frame["end"] - frame["start"]).dt.days
    frame = frame.loc[frame["start"].isna() | days.between(300, 380)].copy()
    frame["kind"] = np.where(frame["start"].isna(), "instant", "annual")
    frame["concept"] = "us-gaap:" + frame["tag"] + "|" + frame["unit"] + "|" + frame["kind"]
    return frame
