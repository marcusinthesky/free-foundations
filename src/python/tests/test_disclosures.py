"""A successful filing audit must establish key, missingness and value agreement."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.filings import broad_facts
from free_foundations.panel import characteristics

ASSETS = "us-gaap:Assets|USD|instant"
EQUITY = "us-gaap:StockholdersEquity|USD|instant"
DEBT = "us-gaap:LongTermDebt|USD|instant"
SHARES = "dei:EntityCommonStockSharesOutstanding|shares|instant"


@pytest.fixture
def disclosure_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path]:
    pieces = tmp_path / "cache/characteristics"
    pieces.mkdir(parents=True)
    wide = pd.DataFrame(
        {
            "year": [2020, 2021],
            "ticker": ["TEST", "TEST"],
            ASSETS: [100.0, 110.0],
            EQUITY: [40.0, np.nan],
            DEBT: [np.nan, 5.0],
            SHARES: [10.0, 12.0],
        }
    )
    records = [
        {
            "year": year,
            "ticker": "TEST",
            "concept": concept,
            "val": value,
            "filed": pd.Timestamp(year=year, month=10, day=1),
            "end": pd.Timestamp(year=year, month=6, day=30),
        }
        for year, values in (
            (2020, {ASSETS: 100.0, EQUITY: 40.0, SHARES: 10.0}),
            (2021, {ASSETS: 110.0, EQUITY: np.nan, DEBT: 5.0, SHARES: 12.0}),
        )
        for concept, value in values.items()
    ]
    snapshot, audit = pieces / "TEST.parquet", pieces / "TEST.audit.parquet"
    wide.to_parquet(snapshot, index=False)
    pd.DataFrame(records).to_parquet(audit, index=False)
    wide.set_index(["year", "ticker"])[[ASSETS, EQUITY, DEBT]].to_parquet(
        tmp_path / "cache/broad.parquet"
    )
    monkeypatch.setattr(characteristics, "ROOT", tmp_path)
    return snapshot, audit


def test_valid_records_allow_structural_missing_cells_and_selected_nulls(
    disclosure_files: tuple[Path, Path],
) -> None:
    assert all(path.is_file() for path in disclosure_files)
    result = characteristics.audit_disclosures()
    assert result["issuers"] == 1
    assert result["selected_facts"] == 7
    assert result["populated_snapshots"] == 2
    assert result["candidate_us_gaap_concepts"] == 3


def test_tenfold_value_error_cannot_pass_when_counts_match(
    disclosure_files: tuple[Path, Path],
) -> None:
    snapshot, _ = disclosure_files
    wide = pd.read_parquet(snapshot)
    wide.loc[wide["year"].eq(2020), ASSETS] = 1000.0
    wide.to_parquet(snapshot, index=False)
    with pytest.raises(ValueError, match="disagree in keys or values"):
        characteristics.audit_disclosures()


def test_substituted_concept_cannot_pass_when_counts_match(
    disclosure_files: tuple[Path, Path],
) -> None:
    _, audit = disclosure_files
    records = pd.read_parquet(audit)
    selected = records["year"].eq(2020) & records["concept"].eq(ASSETS)
    records.loc[selected, "concept"] = "us-gaap:CashAndCashEquivalents|USD|instant"
    records.to_parquet(audit, index=False)
    with pytest.raises(ValueError, match="disagree in keys or values"):
        characteristics.audit_disclosures()


def test_populated_snapshot_requires_its_selected_audit_record(
    disclosure_files: tuple[Path, Path],
) -> None:
    _, audit = disclosure_files
    records = pd.read_parquet(audit)
    records.iloc[1:].to_parquet(audit, index=False)
    with pytest.raises(ValueError, match="disagree in keys or values"):
        characteristics.audit_disclosures()


def test_every_issuer_snapshot_requires_an_audit_file(
    disclosure_files: tuple[Path, Path],
) -> None:
    _, audit = disclosure_files
    audit.unlink()
    with pytest.raises(ValueError, match="Missing filing audit record"):
        characteristics.audit_disclosures()


@pytest.mark.parametrize("change_snapshot", [True, False])
def test_selected_fact_and_snapshot_must_have_the_same_missingness(
    disclosure_files: tuple[Path, Path], *, change_snapshot: bool
) -> None:
    snapshot, audit = disclosure_files
    if change_snapshot:
        wide = pd.read_parquet(snapshot)
        wide.loc[wide["year"].eq(2020), ASSETS] = np.nan
        wide.to_parquet(snapshot, index=False)
    else:
        records = pd.read_parquet(audit)
        records.loc[records["year"].eq(2021) & records["concept"].eq(EQUITY), "val"] = 42.0
        records.to_parquet(audit, index=False)
    with pytest.raises(ValueError, match="disagree in keys or values"):
        characteristics.audit_disclosures()


@pytest.mark.parametrize("violation", ["future_filing", "future_period", "duplicate_key"])
def test_existing_timing_and_duplicate_guards_remain_effective(
    disclosure_files: tuple[Path, Path], violation: str
) -> None:
    _, audit = disclosure_files
    records = pd.read_parquet(audit)
    if violation == "duplicate_key":
        records = pd.concat([records, records.iloc[[0]]], ignore_index=True)
    else:
        records.loc[records.index == 0, "filed" if violation == "future_filing" else "end"] = (
            pd.Timestamp("2021-01-01")
        )
    records.to_parquet(audit, index=False)
    with pytest.raises(ValueError, match="Invalid point-in-time fact selection"):
        characteristics.audit_disclosures()


def test_broad_facts_do_not_mix_quarters_or_units() -> None:
    annual = {
        "start": "2020-01-01",
        "end": "2020-12-31",
        "filed": "2021-02-01",
        "val": 10,
        "form": "10-K",
    }
    quarter = {**annual, "start": "2020-10-01"}
    facts = broad_facts(
        {
            "facts": {
                "us-gaap": {
                    "Example": {
                        "units": {
                            "USD": [annual, quarter],
                            "USD/shares": [annual],
                            "JPY": [annual],
                        }
                    }
                }
            }
        }
    )
    assert len(facts) == 2
    assert set(facts["concept"]) == {
        "us-gaap:Example|USD|annual",
        "us-gaap:Example|USD/shares|annual",
    }
