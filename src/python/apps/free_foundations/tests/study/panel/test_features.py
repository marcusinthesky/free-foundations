"""Information-set fixtures distinguish raw availability from identified baseline geometry."""

import json
from pathlib import Path

import pandas as pd
import pytest

from free_foundations.study.panel.features import build_features
from free_foundations.study.spec import StudySpec


def _sources(tmp_path: Path, facts: dict[str, object]) -> Path:
    root = tmp_path / "sec"
    (root / "companyfacts").mkdir(parents=True)
    (root / "metadata").mkdir()
    (root / "companyfacts/0000000042.json").write_text(json.dumps({"cik": 42, "facts": facts}))
    pd.DataFrame(
        [
            {
                "permno": 1,
                "permco": 2,
                "ticker": "ABC",
                "cik": 42,
                "effective_from": "2009-01-01",
                "effective_to": "2025-12-31",
                "status": "verified_interval",
                "evidence_url": "https://www.sec.gov/Archives/a",
                "accession": "a",
                "evidence_type": "reviewed_filing",
                "reason": "",
            }
        ]
    ).to_csv(root / "crosswalk.csv", index=False)
    return root


def _fact(
    value: object, *, end: str = "2023-12-31", filed: str = "2024-02-01", start: str | None = None
) -> dict[str, object]:
    result = {"val": value, "end": end, "filed": filed, "accn": "a", "form": "10-K"}
    if start is not None:
        result["start"] = start
    return result


def _equity_panels(equity: float = 1000.0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """One issuer-quarter whose CRSP market equity is known at the fiscal year end."""
    quarters, monthly = _panels()
    december = monthly.assign(date="2023-12-29", market_cap_usd=equity)
    return quarters, pd.concat([december, monthly], ignore_index=True)


@pytest.mark.component
def test_crsp_equity_and_sec_books_define_the_four_ratios(tmp_path: Path) -> None:
    # Arrange: CRSP equity 1,000 at December 2023 and fiscal-2023 SEC books.
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {"units": {"USD": [_fact(100)]}},
                "StockholdersEquity": {"units": {"USD": [_fact(50)]}},
                "PaymentsOfDividendsCommonStock": {
                    "units": {"USD": [_fact(10, start="2023-01-01")]}
                },
                "LongTermDebtNoncurrent": {"units": {"USD": [_fact(30)]}},
                "DebtCurrent": {"units": {"USD": [_fact(10)]}},
                "FinanceLeaseLiabilityNoncurrent": {"units": {"USD": [_fact(500)]}},
            },
            "dei": {"EntityPublicFloat": {"units": {"USD": [_fact(99999)]}}},
        },
    )
    quarterly, monthly = _equity_panels()

    # Act
    result = build_features(quarterly, monthly, root, StudySpec())

    # Assert: public float and lease liabilities never enter the ratios.
    values = result["characteristics"].set_index("characteristic")["value"]
    assert values["market_cap_assets"] == pytest.approx(10.0)
    assert values["market_to_book"] == pytest.approx(20.0)
    assert values["dividend_yield"] == pytest.approx(0.01)
    assert values["debt_maturity"] == pytest.approx(0.75)
    assert result["availability"].iloc[0]["original_characteristics_available"] == 4


@pytest.mark.component
def test_missing_components_and_scale_errors_stay_missing(tmp_path: Path) -> None:
    # Arrange: assets tagged in millions by mistake, no dividend or debt tags.
    root = _sources(tmp_path, {"us-gaap": {"Assets": {"units": {"USD": [_fact(0.0001)]}}}})
    quarterly, monthly = _equity_panels()

    # Act
    rows = build_features(quarterly, monthly, root, StudySpec())["characteristics"]

    # Assert
    reasons = rows.set_index("characteristic")["reason"]
    assert rows["value"].isna().all()
    assert reasons["market_cap_assets"] == "outside_plausible_range"
    assert reasons["dividend_yield"] == "crsp_market_equity_or_annual_common_dividends_unavailable"
    assert reasons["debt_maturity"] == "noncurrent_and_total_reported_debt_unavailable"


def _panels() -> tuple[pd.DataFrame, pd.DataFrame]:
    quarters = pd.DataFrame(
        {"issuer_id": ["PERMCO:2"], "permco": [2], "quarter": [pd.Timestamp("2024-06-30")]}
    )
    monthly = pd.DataFrame(
        {
            "date": ["2024-03-28"],
            "permno": [1],
            "permco": [2],
            "ticker": ["ABC"],
            "market_cap_usd": [1000000],
        }
    )
    return quarters, monthly


def test_last_trading_day_filing_and_future_restatement_cannot_leak(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            _fact(100),
                            _fact(200, filed="2024-03-28"),
                            _fact(999, filed="2024-05-01"),
                        ]
                    }
                }
            }
        },
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert result["broad"].iloc[0]["value"] == 100
    cutoff = result["availability"].iloc[0]["cutoff"]
    assert cutoff == pd.Timestamp("2024-03-28T20:00:00Z")
    assert result["broad"]["fact_available_at"].le(cutoff).all()


def test_native_custom_categorical_missing_and_dimensions_survive(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "custom": {
                "Missing": {"units": {"USD": [_fact(None)]}},
                "Policy": {"units": {"pure": [_fact("Cash settlement")]}},
            }
        },
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert len(result["broad"]) == 2
    assert not result["broad"]["is_standard"].any()
    assert set(result["broad"]["value_type"]) == {"numeric", "categorical"}
    assert (
        result["broad"].loc[result["broad"]["concept"].eq("custom:Missing"), "value"].isna().all()
    )
    assert result["broad"]["feature_id"].str.contains("|lag1|", regex=False).all()


def test_candidate_identity_does_not_become_xbrl_availability(tmp_path: Path) -> None:
    root = _sources(tmp_path, {"us-gaap": {"Assets": {"units": {"USD": [_fact(100)]}}}})
    crosswalk = pd.read_csv(root / "crosswalk.csv")
    crosswalk["status"] = "candidate_only"
    crosswalk.to_csv(root / "crosswalk.csv", index=False)
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert not bool(result["availability"].iloc[0]["xbrl_available"])
    assert result["availability"].iloc[0]["reason"] == "linkage_unresolved"
    assert len(result["characteristics"]) == 4


def test_full_rung_retains_old_periods_and_revises_only_asof(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            _fact(90, end="2020-12-31", filed="2021-02-01"),
                            _fact(95, end="2020-12-31", filed="2024-02-01"),
                            _fact(999, end="2020-12-31", filed="2024-05-01"),
                            _fact(100),
                        ]
                    }
                }
            }
        },
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert sorted(result["broad"]["value"]) == [95, 100]
    assert result["broad"]["feature_id"].nunique() == 2
    assert bool(result["availability"].iloc[0]["xbrl_available"])


def test_network_failure_has_its_own_availability_reason(tmp_path: Path) -> None:
    root = _sources(tmp_path, {})
    (root / "acquisition.json").write_text(
        json.dumps(
            {
                "requests": [
                    {
                        "url": "https://data.sec.gov/api/xbrl/companyfacts/CIK0000000042.json",
                        "status": "access_denied",
                    },
                ]
            }
        )
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert result["availability"].iloc[0]["reason"] == "sec_access_denied"


def test_malformed_duration_never_becomes_an_instant(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            _fact(100, start="not-a-date"),
                        ]
                    }
                }
            }
        },
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert result["facts"].iloc[0]["status"] == "invalid_period"
    assert result["broad"].empty
    assert not bool(result["availability"].iloc[0]["xbrl_available"])


def test_dimensional_standard_concept_is_full_rung_only(tmp_path: Path) -> None:
    root = _sources(tmp_path, {})
    folder = root / "filings/0000000042/a"
    folder.mkdir(parents=True)
    (folder / "facts.json").write_text(
        json.dumps(
            [
                {
                    "cik": 42,
                    "concept": "us-gaap:Assets",
                    "namespace": "us-gaap",
                    "tag": "Assets",
                    "unit": "USD",
                    "value": 100,
                    "value_type": "numeric",
                    "raw_value": "100",
                    "start": "",
                    "end": "2023-12-31",
                    "filed": "2024-02-01",
                    "accepted": "",
                    "accession": "a",
                    "form": "10-K",
                    "dimensions": '{"acme:RegionAxis":"acme:West"}',
                    "context_id": "c",
                    "entity_identifier": "42",
                    "decimals": "0",
                    "scale": "0",
                    "source_url": "https://www.sec.gov/Archives/a",
                    "source_kind": "original_filing",
                    "source_sha256": "fixture",
                    "status": "observed",
                }
            ]
        )
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert len(result["broad"]) == 1
    assert not bool(result["broad"].iloc[0]["is_standard"])
    assert not bool(result["broad"].iloc[0]["entity_wide"])
    assert bool(result["availability"].iloc[0]["xbrl_available"])
