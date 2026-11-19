"""Historical ownership identifiers cannot be extrapolated or merged across conflicts."""

import zipfile
from pathlib import Path

import pandas as pd

from free_foundations.study.sources.linkage import (
    OBS_COLUMNS,
    infer_intervals,
    materialize_linkage,
    read_identifier_archive,
)


def _monthly() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "permno": [1] * 12,
            "permco": [2] * 12,
            "ticker": ["ABC"] * 12,
            "date": pd.date_range("2020-01-31", periods=12, freq="ME"),
        }
    )


def _observation(
    day: str, cik: int = 42, accession: str = "a", form: str = "4"
) -> dict[str, object]:
    return {
        "accession": accession,
        "filed_date": pd.Timestamp(day),
        "observation_date": pd.Timestamp(day),
        "period_of_report": pd.Timestamp(day),
        "original_submission_date": pd.NaT,
        "form": form,
        "cik": cik,
        "issuer_name": "ABC Inc",
        "ticker": "ABC",
        "symbol_key": "ABC",
        "source_url": "https://www.sec.gov/files/structureddata/data/insider-transactions-data-sets/2020q1_form345.zip",
        "source_sha256": "fixture",
        "archive_period": "2020q1",
        "scope": "issuer_identity_only",
    }


def test_interval_needs_distinct_dates_and_never_extrapolates() -> None:
    observations = pd.DataFrame(
        [_observation("2020-03-01", accession="a"), _observation("2020-10-01", accession="b")]
    )
    links, _ = infer_intervals(_monthly(), observations)
    row = links.loc[links["status"].eq("verified_interval")].iloc[0]
    assert row["effective_from"] == pd.Timestamp("2020-03-01")
    assert row["effective_to"] == pd.Timestamp("2020-10-01")
    same_day = observations.copy()
    same_day["observation_date"] = pd.Timestamp("2020-03-01")
    links, _ = infer_intervals(_monthly(), same_day)
    assert not links["status"].eq("verified_interval").any()


def test_reused_ticker_and_cik_changes_split_identity_intervals() -> None:
    observations = pd.DataFrame(
        [
            _observation("2020-02-01", 42, "a"),
            _observation("2020-03-01", 42, "b"),
            _observation("2020-06-01", 99, "c"),
            _observation("2020-07-01", 99, "d"),
            _observation("2020-11-01", 42, "e"),
        ]
    )
    links, _ = infer_intervals(_monthly(), observations)
    verified = links.loc[links["status"].eq("verified_interval")]
    assert list(verified["cik"]) == [42, 99]
    assert verified.iloc[0]["effective_to"] == pd.Timestamp("2020-03-01")
    assert verified.iloc[1]["effective_from"] == pd.Timestamp("2020-06-01")


def test_conflicting_same_day_and_amendment_do_not_supply_fake_corroboration() -> None:
    observations = pd.DataFrame(
        [
            _observation("2020-02-01", 42, "a"),
            _observation("2020-03-01", 99, "b"),
            _observation("2020-03-01", 42, "c"),
            _observation("2020-04-01", 42, "d"),
            _observation("2020-05-01", 42, "e", "4/A"),
        ]
    )
    links, coverage = infer_intervals(_monthly(), observations)
    assert not links["status"].eq("verified_interval").any()
    assert coverage.iloc[0]["conflicting_dates"] == 1


def test_crsp_history_gaps_cannot_be_bridged_by_sec_observations() -> None:
    monthly = _monthly().drop(index=5)
    observations = pd.DataFrame(
        [_observation("2020-03-01", accession="a"), _observation("2020-10-01", accession="b")]
    )
    links, coverage = infer_intervals(monthly, observations)
    assert len(coverage) == 2
    assert not links["status"].eq("verified_interval").any()


def test_archive_reads_issuer_cik_and_preserves_amendments(tmp_path: Path) -> None:
    table = pd.DataFrame(
        {
            "ACCESSION_NUMBER": ["a", "b"],
            "FILING_DATE": ["01-MAR-2020", "01-OCT-2020"],
            "PERIOD_OF_REPORT": ["28-FEB-2020", "30-SEP-2020"],
            "DOCUMENT_TYPE": ["4", "4/A"],
            "ISSUERCIK": ["0000000042", "0000000042"],
            "ISSUERNAME": ["ABC Inc", "ABC Inc"],
            "ISSUERTRADINGSYMBOL": ["ABC", "ABC"],
            "RPTOWNERCIK": ["999", "999"],
        }
    )
    filename = tmp_path / "2020q1_form345.zip"
    with zipfile.ZipFile(filename, "w") as archive:
        archive.writestr("SUBMISSION.tsv", table.to_csv(sep="\t", index=False))
    result = read_identifier_archive(filename, {"ABC"})
    assert list(result["cik"]) == [42, 42]
    assert set(result["form"]) == {"4", "4/A"}
    assert result.iloc[0]["observation_date"] == pd.Timestamp("2020-03-01")
    assert result["source_sha256"].str.len().eq(64).all()


def test_materialization_does_not_overwrite_running_acquirer_crosswalk(tmp_path: Path) -> None:
    root = tmp_path / "sec"
    root.mkdir()
    original = root / "crosswalk.csv"
    original.write_text("unchanged\n")
    result = materialize_linkage(_monthly(), root)
    assert original.read_text() == "unchanged\n"
    assert result["observations"].columns.tolist() == OBS_COLUMNS
    assert result["evidence"].empty
    assert len(result["coverage"]) == 1
