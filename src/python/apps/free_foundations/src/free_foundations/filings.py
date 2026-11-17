"""Annual filing facts with explicit concepts, units, periods and original dates."""

from typing import Any

import numpy as np
import pandas as pd

UNITS = {"USD", "shares", "USD/shares", "pure"}


def validated_dates(
    frame: pd.DataFrame, *, instant_only: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Quarantine bad dates while retaining their original strings and reasons.

    Only an absent/null start denotes an instant. A malformed declared duration
    start must never be converted into an instant through date coercion.
    """
    frame = frame.copy()
    reasons: dict[str, pd.Series] = {}
    for name in ("start", "end", "filed"):
        raw = frame[name].astype("string")
        frame[f"raw_{name}"] = raw
        declared = raw.notna()
        shaped = raw.str.fullmatch(r"\d{4}-\d{2}-\d{2}", na=False)
        parsed = pd.to_datetime(raw.where(shaped), format="%Y-%m-%d", errors="coerce")
        if name != "start":
            missing = raw.isna() | raw.eq("")
            reasons[f"missing_{name}"] = missing
            declared = declared & ~missing
        elif instant_only:
            reasons["unexpected_start_for_instant"] = declared
        reasons[f"invalid_{name}"] = declared & parsed.isna()
        frame[name] = parsed
    invalid = pd.DataFrame(reasons).any(axis=1)
    rejected = frame.loc[invalid].copy()
    rejected["rejection_reason"] = pd.Series(
        [
            "|".join(reason for reason, mask in reasons.items() if mask.loc[index])
            for index in rejected.index
        ],
        index=rejected.index,
        dtype="string",
    )
    raw_columns = [f"raw_{name}" for name in ("start", "end", "filed")]
    rejected = rejected.drop(columns=["start", "end", "filed"])
    return frame.loc[~invalid].drop(columns=raw_columns).copy(), rejected


def broad_facts_with_rejections(
    payload: dict[str, Any], *, quarterly_instants: bool = False
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Preserve valid annual flows/stocks and record malformed source observations.

    Quarterly duration facts never enter the annual disclosure feature inventory.
    The optional instant observations are reserved for aligned snapshot recovery.
    """
    forms = {"10-K", "10-K/A"}
    if quarterly_instants:
        forms |= {"10-Q", "10-Q/A"}
    records = []
    for tag, concept in payload["facts"].get("us-gaap", {}).items():
        for unit, observations in concept["units"].items():
            if unit in UNITS:
                records.extend(
                    {"tag": tag, "unit": unit, **row}
                    for row in observations
                    if row.get("form") in forms
                )
    frame = pd.DataFrame(records).reindex(
        columns=["tag", "unit", "val", "start", "end", "filed", "accn", "form"]
    )
    frame, rejected = validated_dates(frame)
    rejected["namespace"] = "us-gaap"
    # Individually valid nanosecond dates can be farther apart than a signed
    # nanosecond timedelta permits. Duration selection only needs calendar days.
    days = frame["end"].to_numpy(dtype="datetime64[D]") - frame["start"].to_numpy(
        dtype="datetime64[D]"
    )
    annual_duration = (days >= np.timedelta64(300, "D")) & (days <= np.timedelta64(380, "D"))
    annual_flow = frame["form"].isin(["10-K", "10-K/A"]) & annual_duration
    frame = frame.loc[frame["start"].isna() | annual_flow].copy()
    frame["kind"] = np.where(frame["start"].isna(), "instant", "annual")
    frame["concept"] = (
        "us-gaap:"
        + frame["tag"].astype(str)
        + "|"
        + frame["unit"].astype(str)
        + "|"
        + frame["kind"]
    )
    return frame, rejected


def broad_facts(payload: dict[str, Any], *, quarterly_instants: bool = False) -> pd.DataFrame:
    """Return valid filing facts; the panel separately persists rejected source rows."""
    return broad_facts_with_rejections(payload, quarterly_instants=quarterly_instants)[0]
