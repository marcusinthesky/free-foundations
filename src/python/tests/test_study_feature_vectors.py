"""Vectorized feature preparation preserves source clocks, periods and interval evidence."""

from __future__ import annotations

import numpy as np
import pandas as pd

from free_foundations.study.features import _normalized_facts, _population_links


def _facts(rows: list[dict[str, object]]) -> pd.DataFrame:
    base = {
        "cik": 42,
        "concept": "us-gaap:Assets",
        "namespace": "us-gaap",
        "tag": "Assets",
        "unit": "USD",
        "value": 100.0,
        "value_type": "numeric",
        "start": "",
        "end": "2023-12-31",
        "filed": "2024-02-01",
        "accepted": "",
        "dimensions": "{}",
        "status": "observed",
    }
    return pd.DataFrame([base | row for row in rows])


def test_bare_acceptance_is_eastern_and_filing_fallback_is_next_local_midnight() -> None:
    raw = _facts(
        [
            {"accepted": "2024-01-15T15:59:00"},
            {"accepted": "2024-07-15T15:59:00"},
            {"accepted": "2024-07-15T15:59:00Z"},
            {"accepted": "2024-07-15T15:59:00+02:00"},
            {"accepted": "invalid", "filed": "2024-03-09"},
            {"accepted": None, "filed": "2024-03-10"},
            {"accepted": "", "filed": "2024-11-03"},
            {"accepted": np.nan, "filed": None},
        ]
    )
    # Duplicate SEC clocks occur across thousands of facts from the same accession.
    repeated = pd.concat([raw, raw], ignore_index=True)
    actual = _normalized_facts(repeated)["fact_available_at"]
    expected = pd.Series(
        pd.to_datetime(
            [
                "2024-01-15T20:59:00Z",
                "2024-07-15T19:59:00Z",
                "2024-07-15T15:59:00Z",
                "2024-07-15T13:59:00Z",
                "2024-03-10T05:00:00Z",
                "2024-03-11T04:00:00Z",
                "2024-11-04T05:00:00Z",
                "NaT",
            ]
            * 2,
            utc=True,
        ),
        name="fact_available_at",
    )
    pd.testing.assert_series_equal(actual, expected)


def test_duration_boundaries_keep_annual_priority_at_three_hundred_days() -> None:
    days = [0, 59, 60, 120, 121, 149, 150, 210, 211, 239, 240, 299, 300, 380, 381]
    end = pd.Timestamp("2023-12-31")
    rows: list[dict[str, object]] = [
        {"start": str((end - pd.Timedelta(days=duration)).date())} for duration in days
    ]
    rows.extend([{"start": ""}, {"start": "invalid"}, {"start": "2023-01-01", "end": "invalid"}])
    normalized = _normalized_facts(_facts(rows))
    assert normalized["period_kind"].tolist() == [
        "duration_0d",
        "duration_59d",
        "quarter",
        "quarter",
        "duration_121d",
        "duration_149d",
        "ytd_2q",
        "ytd_2q",
        "duration_211d",
        "duration_239d",
        "ytd_3q",
        "ytd_3q",
        "annual",
        "annual",
        "duration_381d",
        "instant",
        "instant",
        "duration_nand",
    ]
    assert normalized.iloc[-2:]["status"].eq("invalid_period").all()


def test_population_interval_join_keeps_duplicates_conflicts_and_inclusive_boundaries() -> None:
    quarter = pd.Timestamp("2024-06-30")
    day = pd.Timestamp("2024-03-31")
    population = pd.DataFrame(
        {"issuer_id": list("ABCDE"), "permco": range(1, 6), "quarter": quarter}
    )
    common: dict[str, object] = {
        "effective_from": "2024-03-31",
        "effective_to": "2024-03-31",
        "status": "verified_interval",
        "evidence_url": "https://www.sec.gov/Archives/a",
        "accession": "a",
    }
    rows: list[dict[str, object]] = [
        {"permco": "1", "cik": "42"},
        {"permco": "1", "cik": "42"},
        {"permco": "2", "cik": "43"},
        {"permco": "2", "cik": "44"},
        {"permco": "3", "cik": "45", "effective_to": "2024-03-30"},
        {"permco": "4", "cik": "46", "evidence_url": "https://example.com/a"},
        {"permco": "5", "cik": "47", "accession": None},
    ]
    crosswalk = pd.DataFrame([common | row for row in rows])
    actual = _population_links(population, crosswalk, {quarter: (day, day.tz_localize("UTC"))})
    assert actual == {
        ("A", quarter): (42, "verified"),
        ("B", quarter): (None, "linkage_conflict"),
        ("C", quarter): (None, "linkage_unresolved"),
        ("D", quarter): (None, "linkage_unresolved"),
        ("E", quarter): (None, "linkage_unresolved"),
    }


def test_normalized_facts_do_not_reindex_duplicate_source_rows() -> None:
    raw = _facts([{"accepted": "2024-07-15T15:59:00"}, {"accepted": ""}])
    raw.index = [7, 7]
    normalized = _normalized_facts(raw)
    assert normalized.index.tolist() == [7, 7]
    assert normalized["fact_available_at"].tolist() == [
        pd.Timestamp("2024-07-15T19:59:00Z"),
        pd.Timestamp("2024-02-02T05:00:00Z"),
    ]
