"""SEC source periods can exceed nanosecond timedelta limits without being invalid dates."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from free_foundations.study.panel.features import (
    _broad_frame,
    _current,
    _elapsed_days,
    _normalized_facts,
    _period_kind,
)


def test_elapsed_days_handles_full_timestamp_range_missing_values_and_intraday_floor() -> None:
    earlier = pd.Series(
        [
            pd.Timestamp("1900-01-01"),
            pd.Timestamp("2199-12-31"),
            pd.Timestamp.min,
            pd.Timestamp.max,
            pd.Timestamp("2020-01-01T23:59:59.999999999"),
            pd.Timestamp("2020-01-02T23:59:59.999999998"),
            pd.NaT,
            pd.Timestamp("2020-01-01"),
        ]
    )
    later = pd.Series(
        [
            pd.Timestamp("2199-12-31"),
            pd.Timestamp("1900-01-01"),
            pd.Timestamp.max,
            pd.Timestamp.min,
            pd.Timestamp("2020-01-02T23:59:59.999999998"),
            pd.Timestamp("2020-01-01T23:59:59.999999999"),
            pd.Timestamp("2020-01-01"),
            pd.NaT,
        ]
    )
    expected = pd.Series([109572.0, -109572.0, 213503.0, -213504.0, 0.0, -1.0, np.nan, np.nan])
    pd.testing.assert_series_equal(_elapsed_days(later, earlier), expected)


def _source_periods() -> pd.DataFrame:
    base: dict[str, object] = {
        "cik": 1341439,
        "concept": "us-gaap:RestructuringAndRelatedCostExpectedCost",
        "namespace": "us-gaap",
        "tag": "RestructuringAndRelatedCostExpectedCost",
        "value": 1097000000.0,
        "value_type": "numeric",
        "unit": "USD",
        "start": "1900-01-01",
        "end": "2199-12-31",
        "accession": "0001193125-10-219697",
        "filed": "2010-09-29",
        "accepted": "",
        "source_url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0001341439.json",
        "source_kind": "companyfacts",
        "dimensions": "{}",
        "status": "observed",
    }
    rows: list[dict[str, object]] = [
        {},
        {"concept": "custom:LongDuration", "start": "1700-01-01", "end": "2010-12-31"},
        {"concept": "custom:Reversed", "start": "2199-12-31", "end": "1900-01-01"},
        {"concept": "custom:Instant", "start": "", "end": "2010-12-31"},
        {"concept": "custom:MissingEnd", "end": None},
    ]
    return pd.DataFrame([base | row for row in rows])


def test_oracle_source_period_normalizes_without_discarding_raw_dates_or_values() -> None:
    raw = _source_periods()
    normalized = _normalized_facts(raw)
    assert len(normalized) == len(raw)
    assert normalized["raw_start"].tolist() == raw["start"].tolist()
    assert normalized["raw_end"].tolist() == raw["end"].tolist()
    assert normalized["value"].tolist() == raw["value"].tolist()
    assert normalized["status"].tolist() == [
        "observed",
        "observed",
        "invalid_period",
        "observed",
        "invalid_period",
    ]
    assert normalized.iloc[0]["period_kind"] == "duration_109572d"
    assert _period_kind(normalized.iloc[0]) == "duration_109572d"
    assert normalized.iloc[3]["period_kind"] == "instant"


def test_long_eligible_duration_survives_asof_selection_and_broad_identifier() -> None:
    normalized = _normalized_facts(_source_periods())
    day = pd.Timestamp("2011-03-31")
    cutoff = pd.Timestamp("2011-03-31T20:00:00Z")
    selected = _current(normalized, 1341439, cutoff, day, pd.Timestamp("2001-01-01"))
    assert set(selected["concept"]) == {"custom:LongDuration", "custom:Instant"}
    assert selected["fact_age_days"].eq(90).all()
    base = {
        "issuer_id": "PERMCO:1",
        "permco": 1,
        "quarter": pd.Timestamp("2011-06-30"),
        "cutoff": cutoff,
    }
    broad = _broad_frame(selected, base, day)
    long = broad.loc[broad["concept"].eq("custom:LongDuration")].iloc[0]
    duration = (date(2010, 12, 31) - date(1700, 1, 1)).days
    assert (
        long["feature_id"]
        == f"custom:LongDuration|USD|{{}}|duration_{duration}d|lag1|end_offset0|span{duration}"
    )
    assert long["start"] == pd.Timestamp("1700-01-01")
    assert long["value"] == 1097000000.0


def test_elapsed_days_matches_existing_intraday_semantics_and_integer_dtype() -> None:
    earlier = pd.Series(
        pd.to_datetime(
            [
                "2020-01-01T12:00:00",
                "2020-01-01T23:00:00",
                "2020-01-02T00:00:00",
                "2020-01-02T00:00:00",
            ]
        )
    )
    later = pd.Series(
        pd.to_datetime(
            [
                "2020-01-02T11:59:59",
                "2020-01-02T01:00:00",
                "2020-01-01T23:59:59",
                "2020-01-01T00:00:01",
            ]
        )
    )
    pd.testing.assert_series_equal(_elapsed_days(later, earlier), (later - earlier).dt.days)
