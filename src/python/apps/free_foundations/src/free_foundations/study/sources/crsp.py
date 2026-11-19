"""Frozen CRSP monthly securities, lagged annual membership and selected-class portfolios."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.study.spec import StudySpec

SOURCE_COLUMNS = ("permno", "permco", "ticker", "date", "total_return", "market_cap")
MEMBERSHIP_COLUMNS = (
    "formation_year",
    "effective_year",
    "permno",
    "permco",
    "size_rank",
    "market_cap_usd",
)
PORTFOLIO_COLUMNS = (
    "issuer_id",
    "permco",
    "month",
    "total_return",
    "observed",
    "status",
    "constituents",
    "market_cap_usd",
    "source_count",
    "selected_count",
    "issuer_identity_changed",
    "missing_source_count",
    "missing_return_count",
    "invalid_return_count",
    "missing_lagged_cap_count",
    "constituent_weights",
)
QUARTER_COLUMNS = (
    "issuer_id",
    "permco",
    "quarter",
    "total_return",
    "observed",
    "status",
    "constituents",
    "market_cap_usd",
    "source_count",
    "selected_count",
    "issuer_identity_changed",
    "months",
    "observed_months",
)
STATUS = {
    0: "observed",
    1: "missing_lagged_market_cap",
    2: "missing_return",
    3: "invalid_return",
    4: "missing_source_month_unknown_exit_or_gap",
    5: "incomplete_calendar_quarter",
}


def _source(csv: Path, spec: StudySpec) -> pd.DataFrame:
    """Retain every source row; reject ambiguous keys rather than silently deduplicate."""
    monthly = pd.read_csv(csv, dtype={"ticker": "string"})
    missing = set(SOURCE_COLUMNS) - set(monthly.columns)
    if missing:
        message = f"CRSP source lacks required columns: {sorted(missing)}."
        raise ValueError(message)
    monthly = monthly.copy()
    for name in ("permno", "permco"):
        values = pd.to_numeric(monthly[name], errors="raise")
        if (
            not np.isfinite(values).all()
            or not np.equal(values, np.floor(values)).all()
            or (values <= 0).any()
        ):
            message = f"CRSP {name} identifiers must be positive observed integers."
            raise ValueError(message)
        monthly[name] = values.astype("int64")
    monthly["date"] = pd.to_datetime(monthly["date"], errors="raise")
    if monthly["date"].isna().any():
        message = "CRSP dates must be observed."
        raise ValueError(message)
    if not monthly["date"].between(spec.archive_start, spec.archive_end).all():
        message = "CRSP source dates lie outside the declared return archive."
        raise ValueError(message)
    monthly["month"] = monthly["date"].dt.to_period("M").dt.to_timestamp("M")
    if monthly.duplicated(["permno", "month"]).any():
        message = "CRSP has duplicate PERMNO-month keys."
        raise ValueError(message)
    for name in ("total_return", "market_cap"):
        monthly[name] = pd.to_numeric(monthly[name], errors="raise")
    if not (np.isfinite(monthly["market_cap"]) & monthly["market_cap"].gt(0)).all():
        message = "The supplied positive-cap CRSP extract contains invalid market capitalization."
        raise ValueError(message)
    # mthcap is reported in thousands of dollars in the staged CRSP extract.
    monthly["market_cap_usd"] = monthly["market_cap"] * 1000.0
    if not np.isfinite(monthly["market_cap_usd"]).all():
        message = "CRSP capitalization overflows the USD representation."
        raise ValueError(message)
    valid = np.isfinite(monthly["total_return"]) & monthly["total_return"].ge(-1)
    monthly["observed"] = valid
    monthly["status"] = np.select(
        [valid, monthly["total_return"].isna()],
        ["observed", "missing_return"],
        default="invalid_return",
    )
    return monthly.sort_values(["permno", "month"], kind="stable").reset_index(drop=True)


def _membership(monthly: pd.DataFrame, spec: StudySpec) -> pd.DataFrame:
    """Rank each December on that month's cap, then admit only in the following year."""
    december = monthly.loc[monthly["month"].dt.month.eq(12)].copy()
    december["formation_year"] = december["month"].dt.year
    december = december.sort_values(
        ["formation_year", "market_cap", "permno"], ascending=[True, False, True]
    )
    december["size_rank"] = december.groupby("formation_year").cumcount() + 1
    december["effective_year"] = december["formation_year"] + 1
    return (
        december.loc[december["size_rank"].le(spec.top_n), list(MEMBERSHIP_COLUMNS)]
        .sort_values(["formation_year", "size_rank"])
        .reset_index(drop=True)
    )


def _calendar(membership: pd.DataFrame, spec: StudySpec, *, cohort: bool = False) -> pd.DataFrame:
    """Keep all twelve eligible months, or one formation cohort's whole outcome window."""
    start = pd.Timestamp(spec.archive_start).to_period("M").to_timestamp("M")
    end = pd.Timestamp(spec.archive_end).to_period("M").to_timestamp("M")
    active = membership.loc[membership["effective_year"].between(start.year, end.year)].copy()
    if cohort:
        if active.empty or not active["formation_year"].eq(active["formation_year"].iloc[0]).all():
            message = "A cohort calendar needs exactly one formation year."
            raise ValueError(message)
        window = spec.window(int(active["formation_year"].iloc[0]))
        first = window[0].to_period("Q").start_time.to_period("M").to_timestamp("M")
        months = pd.date_range(max(start, first), min(end, window[-1]), freq="ME")
        return active.merge(pd.DataFrame({"month": months}), how="cross")
    grid = active.merge(pd.DataFrame({"month_number": range(1, 13)}), how="cross")
    grid["month"] = pd.to_datetime(
        {"year": grid["effective_year"], "month": grid["month_number"], "day": 1}
    ) + pd.offsets.MonthEnd(0)
    return grid.loc[grid["month"].between(start, end)].reset_index(drop=True)


def _weights_json(group: pd.DataFrame) -> str:
    return json.dumps(
        [
            {"permno": int(permno), "weight": float(weight) if np.isfinite(weight) else None}
            for permno, weight in zip(group["permno"], group["weight"], strict=True)
        ],
        separators=(",", ":"),
        allow_nan=False,
    )


def _constituents_json(values: pd.Series) -> str:
    return json.dumps([int(value) for value in values], separators=(",", ":"))


def _issuer_monthly(
    monthly: pd.DataFrame,
    membership: pd.DataFrame,
    spec: StudySpec,
    *,
    cohort: bool = False,
) -> pd.DataFrame:
    """Portfolio only selected classes, using every class's preceding calendar-month cap.

    Formation PERMCO fixes the annual portfolio identity. Subsequent source-PERMCO
    changes are reported without losing known returns of its selected PERMNOs.
    An absent class row does not identify a delisting or its settlement proceeds.
    """
    grid = _calendar(membership, spec, cohort=cohort)
    if grid.empty:
        return pd.DataFrame(columns=PORTFOLIO_COLUMNS)
    current = monthly[
        ["permno", "permco", "month", "total_return", "market_cap_usd", "observed"]
    ].rename(columns={"permco": "source_permco", "market_cap_usd": "current_cap_usd"})
    current["source_present"] = True
    grid = grid.merge(current, on=["permno", "month"], how="left", validate="one_to_one")
    lagged = monthly[["permno", "month", "market_cap_usd"]].rename(
        columns={"market_cap_usd": "lagged_cap_usd"}
    )
    lagged["month"] = lagged["month"] + pd.offsets.MonthEnd(1)
    grid = grid.merge(lagged, on=["permno", "month"], how="left", validate="one_to_one")
    grid = grid.sort_values(["permco", "month", "permno"]).reset_index(drop=True)
    present = grid["source_present"].notna()
    lag_valid = np.isfinite(grid["lagged_cap_usd"]) & grid["lagged_cap_usd"].gt(0)
    return_missing = present & grid["total_return"].isna()
    return_invalid = (
        present
        & ~return_missing
        & (~np.isfinite(grid["total_return"]) | grid["total_return"].lt(-1))
    )
    grid["source_count"] = present.astype(int)
    grid["missing_source_count"] = (~present).astype(int)
    grid["missing_return_count"] = return_missing.astype(int)
    grid["invalid_return_count"] = return_invalid.astype(int)
    grid["missing_lagged_cap_count"] = (~lag_valid).astype(int)
    grid["issuer_identity_changed"] = present & grid["source_permco"].ne(grid["permco"])
    grid["status_code"] = np.select(
        [~present, return_invalid, return_missing, ~lag_valid], [4, 3, 2, 1], default=0
    )
    keys = ["permco", "month"]
    grouped = grid.groupby(keys, sort=True, observed=True)
    denominator = grouped["lagged_cap_usd"].transform("sum")
    missing_lag = grouped["missing_lagged_cap_count"].transform("sum").gt(0)
    grid["weight"] = (grid["lagged_cap_usd"] / denominator).mask(missing_lag)
    grid["contribution"] = grid["weight"] * grid["total_return"]
    grid["contribution"] = grid["contribution"].mask(grid["status_code"].ne(0))
    grouped = grid.groupby(keys, sort=True, observed=True)
    result = grouped.agg(
        total_return=("contribution", "sum"),
        status_code=("status_code", "max"),
        source_count=("source_count", "sum"),
        selected_count=("permno", "size"),
        issuer_identity_changed=("issuer_identity_changed", "max"),
        missing_source_count=("missing_source_count", "sum"),
        missing_return_count=("missing_return_count", "sum"),
        invalid_return_count=("invalid_return_count", "sum"),
        missing_lagged_cap_count=("missing_lagged_cap_count", "sum"),
    )
    result["market_cap_usd"] = (
        grouped["current_cap_usd"]
        .sum()
        .where(grouped["current_cap_usd"].count().eq(result["selected_count"]))
    )
    result["observed"] = result["status_code"].eq(0)
    result["total_return"] = result["total_return"].where(result["observed"])
    result["status"] = result["status_code"].map(STATUS)
    result.loc[result["observed"] & result["issuer_identity_changed"], "status"] = (
        "observed_issuer_identity_changed"
    )
    first_permno = grouped["permno"].first().astype(str)
    result["constituents"] = "[" + first_permno + "]"
    first_weight = np.where(grouped["weight"].first().notna(), "1.0", "null")
    result["constituent_weights"] = (
        '[{"permno":' + first_permno + ',"weight":' + first_weight + "}]"
    )
    # Most portfolios contain one selected class. Avoid a Python group callback for
    # every singleton month in the annual backcast while preserving exact JSON order.
    multiple = grouped["permno"].transform("size").gt(1)
    if multiple.any():
        multi = grid.loc[multiple].groupby(keys, sort=True, observed=True)
        constituents = multi["permno"].agg(_constituents_json)
        weights = multi[["permno", "weight"]].apply(_weights_json)
        result.loc[constituents.index, "constituents"] = constituents
        result.loc[weights.index, "constituent_weights"] = weights
    result = result.reset_index()
    result["issuer_id"] = "PERMCO:" + result["permco"].astype(str)
    return (
        result[list(PORTFOLIO_COLUMNS)].sort_values(["issuer_id", "month"]).reset_index(drop=True)
    )


def _quarterly(issuer_monthly: pd.DataFrame) -> pd.DataFrame:
    """Compound exactly three observed monthly portfolios; never skip an absent month."""
    if issuer_monthly.empty:
        return pd.DataFrame(columns=QUARTER_COLUMNS)
    frame = issuer_monthly.sort_values(["issuer_id", "month"]).copy()
    frame["quarter"] = frame["month"].dt.to_period("Q").dt.to_timestamp("Q")
    codes = {value: key for key, value in STATUS.items()}
    frame["status_code"] = frame["status"].map(codes).fillna(0).astype(int)
    frame["gross_return"] = 1 + frame["total_return"]
    frame["quarter_end_cap"] = frame["market_cap_usd"].where(frame["month"].eq(frame["quarter"]))
    grouped = frame.groupby(["issuer_id", "quarter"], sort=True, observed=True)
    result = grouped.agg(
        permco=("permco", "first"),
        constituents=("constituents", "first"),
        selected_count=("selected_count", "first"),
        source_count=("source_count", "sum"),
        months=("month", "size"),
        observed_months=("observed", "sum"),
        status_code=("status_code", "max"),
        issuer_identity_changed=("issuer_identity_changed", "max"),
    )
    result["observed"] = result["months"].eq(3) & result["observed_months"].eq(3)
    result["total_return"] = (grouped["gross_return"].prod(min_count=3) - 1).where(
        result["observed"]
    )
    result["market_cap_usd"] = grouped["quarter_end_cap"].sum(min_count=1)
    result.loc[result["months"].ne(3), "status_code"] = 5
    result["status"] = result["status_code"].map(STATUS)
    result.loc[result["observed"] & result["issuer_identity_changed"], "status"] = (
        "observed_issuer_identity_changed"
    )
    return result.reset_index()[list(QUARTER_COLUMNS)]


def build_crsp(csv: Path, spec: StudySpec) -> dict[str, pd.DataFrame]:
    """Build deterministic master inputs without acquisition or feature-era filtering.

    The monthly table retains the source's business dates and original cap units.
    December 2001 first supplies membership for 2002; no 2000 universe is invented.
    December 2025 membership is retained as provenance, even though its 2026 return
    calendar lies outside the declared archive. Feature eligibility is a later task.
    """
    monthly = _source(csv, spec)
    membership = _membership(monthly, spec)
    issuer_monthly = _issuer_monthly(monthly, membership, spec)
    return {
        "monthly": monthly,
        "membership": membership,
        "issuer_monthly": issuer_monthly,
        "quarterly": _quarterly(issuer_monthly),
        "cohorts": build_cohorts(monthly, membership, spec),
    }


def build_cohorts(monthly: pd.DataFrame, membership: pd.DataFrame, spec: StudySpec) -> pd.DataFrame:
    """Follow each declared December formation cohort through its outcome window.

    Selected classes keep their formation PERMCO identity and lagged-cap weights after
    leaving the top-``top_n``. CRSP CIZ returns include delisting returns; months
    after a class's final source row are unobserved, never filled.
    """
    pieces = []
    for formation in spec.formation_years:
        selected = membership.loc[membership["formation_year"].eq(formation)]
        if selected.empty:
            continue
        piece = _quarterly(_issuer_monthly(monthly, selected, spec, cohort=True))
        piece.insert(0, "formation_year", formation)
        pieces.append(piece)
    if not pieces:
        return pd.DataFrame(columns=["formation_year", *QUARTER_COLUMNS])
    return pd.concat(pieces, ignore_index=True).sort_values(
        ["formation_year", "issuer_id", "quarter"], ignore_index=True
    )
