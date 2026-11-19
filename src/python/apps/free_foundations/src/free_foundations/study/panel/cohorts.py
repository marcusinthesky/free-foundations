"""Formation-cohort outcomes on the verified study calendar."""

from __future__ import annotations

import pandas as pd


def cohort_outcomes(
    cohorts: pd.DataFrame,
    factors: pd.DataFrame,
    window: pd.DatetimeIndex,
    formation: int,
    issuers: tuple[str, ...],
) -> pd.DataFrame:
    """Long quarterly excess returns of the formation cohort over its window."""
    frame = cohorts.loc[
        cohorts["formation_year"].eq(formation) & cohorts["issuer_id"].isin(issuers)
    ].copy()
    frame["quarter"] = pd.to_datetime(frame["quarter"]).dt.to_period("Q").dt.to_timestamp("Q")
    frame = frame.loc[frame["quarter"].isin(window) & frame["observed"].astype(bool)]
    factors = factors.reindex(window)
    if factors[["RF", "Mkt-RF"]].isna().any().any():
        message = f"Quarterly factors are incomplete in the {formation} window."
        raise ValueError(message)
    frame["excess"] = frame["total_return"] - frame["quarter"].map(factors["RF"])
    frame["market"] = frame["quarter"].map(factors["Mkt-RF"])
    return frame.rename(columns={"issuer_id": "ticker", "quarter": "date"})[
        ["ticker", "date", "excess", "market"]
    ].reset_index(drop=True)
