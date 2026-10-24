"""Recover observed quarterly stocks without changing complete annual snapshots."""

import warnings
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from free_foundations.filings import broad_facts, broad_facts_with_rejections
from free_foundations.panel import characteristics


def payload(*, annual_shares: bool = False, quarterly_equity: bool = True) -> dict[str, Any]:
    observations = {
        "Assets": [
            ("2019-12-31", "2020-02-01", "10-K", 100.0),
            ("2020-09-30", "2020-11-01", "10-Q", 200.0),
        ],
        "StockholdersEquity": [("2019-12-31", "2020-02-01", "10-K", 40.0)],
        "CommonStockSharesOutstanding": [("2020-09-30", "2020-11-01", "10-Q", 30.0)],
    }
    if annual_shares:
        observations["CommonStockSharesOutstanding"].append(
            ("2019-12-31", "2020-02-01", "10-K", 10.0)
        )
    if quarterly_equity:
        observations["StockholdersEquity"].append(("2020-09-30", "2020-11-01", "10-Q", 80.0))
    return {
        "facts": {
            "us-gaap": {
                tag: {
                    "units": {
                        "shares" if tag == "CommonStockSharesOutstanding" else "USD": [
                            {
                                "end": end,
                                "filed": filed,
                                "form": form,
                                "val": value,
                                "accn": f"{form}-{end}",
                            }
                            for end, filed, form, value in values
                        ]
                    }
                }
                for tag, values in observations.items()
            }
        }
    }


@pytest.fixture
def prices() -> pd.DataFrame:
    dates = pd.bdate_range("2019-01-01", "2020-12-31")
    return pd.DataFrame(
        {
            "Close": 2.0,
            "historical_close": 2.0,
            "trailing_dividends": 0.1,
            "Stock Splits": 0.0,
            "Dividends": 0.0,
        },
        index=dates,
    )


def select(
    data: dict[str, Any], prices: pd.DataFrame
) -> tuple[dict[str, Any], pd.DataFrame, pd.DataFrame]:
    return characteristics.annual_snapshot(
        characteristics.disclosure_facts(data),
        characteristics.disclosure_facts(data, quarterly_instants=True),
        prices,
        "TEST",
        2020,
    )


def test_complete_quarterly_snapshot_recovers_real_values_and_keeps_broad_annual(
    prices: pd.DataFrame,
) -> None:
    row, annual, evidence = select(payload(), prices)
    assert row["source_policy"] == "quarterly_recovery"
    assert row["period_end"] == "2020-09-30"
    assert row["market_cap_assets"] == pytest.approx(0.3)
    assert row["market_to_book"] == pytest.approx(0.75)
    assert row["dividend_yield"] == pytest.approx(0.05)
    assert row["us-gaap:Assets|USD|instant"] == 100.0
    assert set(annual["form"]) == {"10-K"}
    assert set(evidence["form"]) == {"10-Q"}
    assert set(evidence["end"]) == {pd.Timestamp("2020-09-30")}


def test_complete_annual_snapshot_is_preserved_even_with_more_recent_quarter(
    prices: pd.DataFrame,
) -> None:
    row, _, evidence = select(payload(annual_shares=True), prices)
    assert row["source_policy"] == "annual"
    assert row["period_end"] == "2019-12-31"
    assert row["market_cap_assets"] == pytest.approx(0.2)
    assert row["market_to_book"] == pytest.approx(0.5)
    assert set(evidence["form"]) == {"10-K"}


def test_fallback_cannot_splice_equity_from_a_different_balance_sheet(
    prices: pd.DataFrame,
) -> None:
    row, _, evidence = select(payload(quarterly_equity=False), prices)
    assert row["source_policy"] == "annual_incomplete"
    assert row["period_end"] == "2019-12-31"
    assert np.isnan(row["market_cap_assets"])
    assert np.isnan(row["market_to_book"])
    assert set(evidence["form"]) == {"10-K"}


@pytest.mark.parametrize("invalid", ["future_filing", "future_period", "too_old"])
def test_quarterly_recovery_respects_original_availability_and_age(
    prices: pd.DataFrame, invalid: str
) -> None:
    data = payload()
    for concept in data["facts"]["us-gaap"].values():
        for observation in next(iter(concept["units"].values())):
            if observation["form"] == "10-Q":
                if invalid == "future_filing":
                    observation["filed"] = "2021-01-01"
                elif invalid == "future_period":
                    observation["end"] = "2021-01-01"
                else:
                    observation["end"] = "2018-12-31"
    row, _, evidence = select(data, prices)
    assert row["source_policy"] == "annual_incomplete"
    assert np.isnan(row["market_cap_assets"])
    assert not evidence["form"].eq("10-Q").any()


def test_quarterly_duration_facts_never_enter_recovery_inventory() -> None:
    instant = {"end": "2020-09-30", "filed": "2020-11-01", "form": "10-Q", "val": 5}
    data = {
        "facts": {
            "us-gaap": {
                "Example": {
                    "units": {
                        "USD": [
                            instant,
                            {**instant, "start": "2020-07-01"},
                            {**instant, "start": "2019-10-01"},
                        ]
                    }
                }
            }
        }
    }
    assert broad_facts(data).empty
    recovered = broad_facts(data, quarterly_instants=True)
    assert len(recovered) == 1
    assert recovered.iloc[0]["kind"] == "instant"


def test_component_audit_rejects_altered_ratios_and_fact_values(
    prices: pd.DataFrame, tmp_path: Path
) -> None:
    row, _, evidence = select(payload(), prices)
    path = tmp_path / "TEST.recovery.parquet"
    evidence.to_parquet(path, index=False)
    wide = pd.DataFrame([row])
    assert characteristics.audit_ratio_components(wide, path) == (len(evidence), len(evidence))
    original = float(row["market_to_book"])
    wide.loc[0, "market_to_book"] = original * 10
    with pytest.raises(ValueError, match="ratio values and component audit disagree"):
        characteristics.audit_ratio_components(wide, path)
    wide.loc[0, "market_to_book"] = original
    evidence.loc[evidence["component"].eq("assets"), "val"] *= 10
    evidence.to_parquet(path, index=False)
    with pytest.raises(ValueError, match="fact values and ratio components disagree"):
        characteristics.audit_ratio_components(wide, path)


@pytest.mark.parametrize("damaged", ["aggregate_values", "issuer_evidence", "aggregate_metadata"])
def test_recovery_cache_is_versioned_and_assembly_uses_actual_year_count(
    prices: pd.DataFrame, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, damaged: str
) -> None:
    root, source = tmp_path / "panel", tmp_path / "universe/cache"
    source.mkdir(parents=True)
    pd.DataFrame({"ticker": ["TEST"], "cik": [1]}).to_csv(
        source.parent / "universe.csv", index=False
    )
    monkeypatch.setattr(characteristics, "ROOT", root)
    monkeypatch.setattr(characteristics, "SOURCE", source)
    monkeypatch.setattr(characteristics, "YEARS", (2020,))
    market = prices.drop(columns=["historical_close", "trailing_dividends"]).copy()
    market.columns = pd.MultiIndex.from_product([market.columns, ["TEST"]])
    monkeypatch.setattr(characteristics, "markets", lambda: market)
    calls = []

    def read_facts(*_: object, cached_only: bool) -> dict[str, Any]:
        assert cached_only
        calls.append(True)
        return payload()

    monkeypatch.setattr(characteristics, "company_facts", read_facts)
    first, _ = characteristics.build()
    assert len(first) == 1
    assert len(calls) == 1
    assert characteristics.audit_disclosures()["annual_states"] == 1
    characteristics.build()
    assert len(calls) == 1
    cache = root / "cache"
    if damaged == "aggregate_values":
        changed = first.copy()
        changed["market_to_book"] *= 10
        changed.to_parquet(cache / "four.parquet")
    elif damaged == "aggregate_metadata":
        (cache / "characteristic-audit.parquet").unlink()
    else:
        (cache / "characteristics/TEST.recovery.parquet").unlink()
    repaired, _ = characteristics.build()
    pd.testing.assert_frame_equal(first, repaired)
    expected_calls = 2 if damaged == "issuer_evidence" else 1
    assert len(calls) == expected_calls
    monkeypatch.setattr(characteristics, "POLICY", "changed-policy")
    characteristics.build()
    assert len(calls) == expected_calls + 1
    contract = root / "cache/characteristic-contract.json"
    assert characteristics.matches_contract(contract, characteristics.cache_contract())
    assert (root / "source-recovery.json").is_file()
    pd.DataFrame({"obsolete": [True]}).to_parquet(cache / "characteristics/STALE.rejected.parquet")
    characteristics.build()
    assert characteristics.audit_disclosures()["issuers"] == 1


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    [
        ("end", "6016-06-30", "invalid_end"),
        ("filed", "6016-06-30", "invalid_filed"),
        ("end", None, "missing_end"),
        ("filed", None, "missing_filed"),
        ("start", "not-a-date", "invalid_start"),
        ("start", "6016-06-30", "invalid_start"),
    ],
)
def test_malformed_source_dates_are_quarantined_with_original_evidence(
    field: str, value: str | None, reason: str
) -> None:
    observation = {
        "end": "2020-09-30",
        "filed": "2020-11-01",
        "form": "10-Q",
        "val": 200.0,
        "accn": "original-accession",
        field: value,
    }
    data = {"facts": {"us-gaap": {"Assets": {"units": {"USD": [observation]}}}}}
    valid, rejected = broad_facts_with_rejections(data, quarterly_instants=True)
    assert valid.empty
    assert len(rejected) == 1
    assert rejected.iloc[0]["rejection_reason"] == reason
    assert rejected.iloc[0]["accn"] == "original-accession"
    assert rejected.iloc[0]["namespace"] == "us-gaap"
    if value is not None:
        assert rejected.iloc[0][f"raw_{field}"] == value


def test_valid_future_filing_is_retained_in_source_and_excluded_by_cutoff() -> None:
    data = {
        "facts": {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            {
                                "end": "2025-12-31",
                                "filed": "2026-02-01",
                                "form": "10-K",
                                "val": 200.0,
                                "accn": "future-filing",
                            }
                        ]
                    }
                }
            }
        }
    }
    valid, rejected = broad_facts_with_rejections(data, quarterly_instants=True)
    assert len(valid) == 1
    assert rejected.empty
    assert characteristics.known_facts(valid, 2025).empty


@pytest.mark.parametrize("form", ["10-K", "10-Q"])
def test_long_valid_date_span_is_a_nonannual_duration_without_timedelta_overflow(form: str) -> None:
    data = {
        "facts": {
            "us-gaap": {
                "Example": {
                    "units": {
                        "USD": [
                            {
                                "start": "1700-01-01",
                                "end": "2020-09-30",
                                "filed": "2020-11-01",
                                "form": form,
                                "val": 200.0,
                                "accn": "long-valid-duration",
                            }
                        ]
                    }
                }
            }
        }
    }
    valid, rejected = broad_facts_with_rejections(data, quarterly_instants=True)
    assert valid.empty
    assert rejected.empty


@pytest.mark.parametrize("field", ["end", "filed", "start"])
def test_dei_shares_use_the_same_date_quarantine(field: str) -> None:
    bad = {
        "end": "2020-09-30",
        "filed": "2020-11-01",
        "form": "10-Q",
        "val": 20.0,
        "accn": "bad-shares",
        field: "6016-06-30",
    }
    good = {
        "end": "2020-09-30",
        "filed": "2020-11-01",
        "form": "10-Q",
        "val": 30.0,
        "accn": "good-shares",
    }
    data = {
        "facts": {
            "dei": {
                "EntityCommonStockSharesOutstanding": {
                    "units": {"shares": [bad, good]},
                }
            }
        }
    }
    valid, rejected = characteristics.disclosure_facts_with_rejections(
        data, quarterly_instants=True
    )
    assert len(valid) == 1
    assert valid.iloc[0]["val"] == 30
    assert len(rejected) == 1
    assert rejected.iloc[0]["namespace"] == "dei"
    assert f"invalid_{field}" in rejected.iloc[0]["rejection_reason"]
    assert rejected.iloc[0][f"raw_{field}"] == "6016-06-30"


def test_component_audit_cannot_ignore_missing_constituents(
    prices: pd.DataFrame, tmp_path: Path
) -> None:
    row, _, evidence = select(payload(), prices)
    missing = evidence.loc[evidence["component"].eq("assets")].copy()
    missing["val"] = np.nan
    evidence = pd.concat([evidence, missing], ignore_index=True)
    path = tmp_path / "TEST.recovery.parquet"
    evidence.to_parquet(path, index=False)
    with pytest.raises(ValueError, match="missing or invalid fact evidence"):
        characteristics.audit_ratio_components(pd.DataFrame([row]), path)


def test_empty_record_concatenation_keeps_schema_without_dtype_inference_warnings() -> None:
    empty = pd.DataFrame(columns=["component", "val"])
    populated = pd.DataFrame({"component": ["assets"], "val": [100.0]})
    with warnings.catch_warnings():
        warnings.simplefilter("error", FutureWarning)
        result = characteristics.concat_records([empty, populated, empty])
        all_empty = characteristics.concat_records([empty, empty])
    pd.testing.assert_frame_equal(result, populated)
    assert all_empty.empty
    assert list(all_empty) == ["component", "val"]


def test_rejected_fact_audit_recomputes_reasons(tmp_path: Path) -> None:
    data = {
        "facts": {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            {
                                "end": "6016-06-30",
                                "filed": "2020-11-01",
                                "form": "10-Q",
                                "val": 200.0,
                                "accn": "bad-period",
                            }
                        ]
                    }
                }
            }
        }
    }
    _, rejected = characteristics.disclosure_facts_with_rejections(data, quarterly_instants=True)
    path = tmp_path / "TEST.rejected.parquet"
    rejected.to_parquet(path, index=False)
    wide = pd.DataFrame({"source_policy": ["annual_incomplete"]})
    assert characteristics.audit_rejected_facts(wide, path) == 1
    rejected["rejection_reason"] = "missing_end"
    rejected.to_parquet(path, index=False)
    with pytest.raises(ValueError, match="validation reasons"):
        characteristics.audit_rejected_facts(wide, path)


def debt_payload(
    *, annual_debt: bool = False, period: str = "2019-12-31", filed: str = "2020-11-01"
) -> dict[str, Any]:
    data = payload(annual_shares=True)
    for tag, value in (
        ("LongTermDebtAndCapitalLeaseObligations", 80.0),
        ("DebtAndCapitalLeaseObligations", 100.0),
    ):
        facts = [{"end": period, "filed": filed, "form": "10-Q", "val": value, "accn": "q-debt"}]
        if annual_debt:
            facts.append(
                {
                    "end": "2019-12-31",
                    "filed": "2020-02-01",
                    "form": "10-K",
                    "val": 10.0 if tag.startswith("LongTerm") else 20.0,
                    "accn": "k-debt",
                }
            )
        data["facts"]["us-gaap"][tag] = {"units": {"USD": facts}}
    return data


def test_aligned_quarterly_debt_fill_preserves_annual_ratios_dates_and_market_metadata(
    prices: pd.DataFrame, tmp_path: Path
) -> None:
    original, _, _ = select(payload(annual_shares=True), prices)
    completed, _, evidence = select(debt_payload(), prices)
    assert completed["source_policy"] == "annual"
    assert completed["aligned_quarterly_debt_recovery"]
    assert completed["debt_maturity"] == pytest.approx(0.8)
    unchanged = [
        *characteristics.FIRST_THREE,
        "period_end",
        "share_date",
        "market_date",
        "market_close",
        "market_historical_close",
        "trailing_dividends",
        "latest_filed",
    ]
    assert {key: completed[key] for key in unchanged} == {key: original[key] for key in unchanged}
    quarterly = evidence.loc[evidence["form"].eq("10-Q")]
    assert set(quarterly["component"]) == {"debt_noncurrent", "debt_total"}
    assert set(quarterly["end"]) == {pd.Timestamp("2019-12-31")}
    path = tmp_path / "TEST.recovery.parquet"
    evidence.to_parquet(path, index=False)
    assert characteristics.audit_ratio_components(pd.DataFrame([completed]), path)[1] == len(
        quarterly
    )
    evidence.loc[evidence["form"].eq("10-Q"), "aligned_quarterly_debt_recovery"] = False
    evidence.to_parquet(path, index=False)
    with pytest.raises(ValueError, match="Invalid point-in-time"):
        characteristics.audit_ratio_components(pd.DataFrame([completed]), path)


@pytest.mark.parametrize("failure", ["different_period", "future_filing", "existing_annual_debt"])
def test_aligned_debt_fill_requires_same_period_known_facts_and_missing_annual_debt(
    prices: pd.DataFrame, failure: str
) -> None:
    data = debt_payload(
        annual_debt=failure == "existing_annual_debt",
        period="2020-09-30" if failure == "different_period" else "2019-12-31",
        filed="2021-01-01" if failure == "future_filing" else "2020-11-01",
    )
    row, _, evidence = select(data, prices)
    assert row["source_policy"] == "annual"
    assert not row["aligned_quarterly_debt_recovery"]
    assert not evidence["form"].eq("10-Q").any()
    if failure == "existing_annual_debt":
        assert row["debt_maturity"] == pytest.approx(0.5)
    else:
        assert np.isnan(row["debt_maturity"])
