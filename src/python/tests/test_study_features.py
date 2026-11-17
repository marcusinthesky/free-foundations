"""Information-set fixtures distinguish raw availability from identified baseline geometry."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.study.features import build_features
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


def test_available_xbrl_does_not_imply_observed_prices_or_full_class_cap(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {"units": {"USD": [_fact(100)]}},
                "StockholdersEquity": {"units": {"USD": [_fact(70)]}},
                "LongTermDebtAndCapitalLeaseObligations": {"units": {"USD": [_fact(20)]}},
                "DebtAndCapitalLeaseObligations": {"units": {"USD": [_fact(40)]}},
            }
        },
    )
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec(feature_start="2009-01-01"))
    assert bool(result["availability"].iloc[0]["xbrl_available"])
    values = result["characteristics"].set_index("characteristic")["value"]
    assert values["debt_maturity"] == 0.5
    assert np.isnan(values["market_cap_assets"])
    assert np.isnan(values["market_to_book"])
    assert np.isnan(values["dividend_yield"])
    assert result["availability"].iloc[0]["original_characteristics_available"] == 1


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


def test_public_float_is_not_promoted_to_market_cap_even_by_catalog(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {"Assets": {"units": {"USD": [_fact(100)]}}},
            "dei": {"EntityPublicFloat": {"units": {"USD": [_fact(1000)]}}},
        },
    )
    pd.DataFrame(
        [
            {
                "concept": "dei:EntityPublicFloat",
                "component": "market_cap",
                "unit": "USD",
                "scope": "entire_common_equity",
                "status": "verified",
                "evidence_url": "https://www.sec.gov/Archives/a",
            }
        ]
    ).to_csv(root / "metadata/component-semantics.csv", index=False)
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    assert (
        result["characteristics"]
        .loc[result["characteristics"]["characteristic"].eq("market_cap_assets"), "value"]
        .isna()
        .all()
    )


def test_reviewed_sec_market_components_can_identify_original_ratios(tmp_path: Path) -> None:
    root = _sources(
        tmp_path,
        {
            "us-gaap": {
                "Assets": {"units": {"USD": [_fact(100)]}},
                "StockholdersEquity": {"units": {"USD": [_fact(50)]}},
                "CommonStockDividendsPerShareCashPaid": {
                    "units": {"USD/shares": [_fact(1, start="2023-01-01")]}
                },
            },
            "acme": {
                "FullIssuerMarketCapitalization": {"units": {"USD": [_fact(1000)]}},
                "ReportedCommonShareMarketPrice": {"units": {"USD/shares": [_fact(10)]}},
            },
        },
    )
    pd.DataFrame(
        [
            {
                "concept": "acme:FullIssuerMarketCapitalization",
                "component": "market_cap",
                "unit": "USD",
                "scope": "entire_common_equity",
                "status": "verified",
                "evidence_url": "https://www.sec.gov/Archives/a",
            },
            {
                "concept": "acme:ReportedCommonShareMarketPrice",
                "component": "market_price",
                "unit": "USD/shares",
                "scope": "single_common_class",
                "status": "verified",
                "evidence_url": "https://www.sec.gov/Archives/a",
            },
        ]
    ).to_csv(root / "metadata/component-semantics.csv", index=False)
    quarterly, monthly = _panels()
    result = build_features(quarterly, monthly, root, StudySpec())
    values = result["characteristics"].set_index("characteristic")["value"]
    assert values["market_cap_assets"] == 10
    assert values["market_to_book"] == 20
    assert values["dividend_yield"] == 0.1


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
