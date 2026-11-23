"""CRSP memberships, lagged selected-class portfolios and unknown observations."""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.study.sources.crsp import build_crsp
from free_foundations.study.spec import StudySpec, frame_digest
from tests._strategies import compact_spec


def spec(*, archive_end: str = "2003-12-31") -> StudySpec:
    return compact_spec(
        "2001-01-01", archive_end, top_n=2, formation_years=(2001,), primary_formation=2001
    )


def source() -> pd.DataFrame:
    rows = []
    for date in pd.date_range("2001-01-31", "2003-12-31", freq="ME"):
        for permno, permco, cap, ret in (
            (10, 100, 10.0, 0.1),
            (11, 100, 30.0, 0.2),
            (20, 200, 5.0, 0.3),
        ):
            rows.append((permno, permco, f"T{permno}", date, ret, cap))
    return pd.DataFrame(
        rows, columns=["permno", "permco", "ticker", "date", "total_return", "market_cap"]
    )


def run(
    tmp_path: Path, frame: pd.DataFrame, study: StudySpec | None = None
) -> dict[str, pd.DataFrame]:
    path = tmp_path / "returns.csv"
    frame.to_csv(path, index=False)
    return build_crsp(path, study or spec())


def cell(
    frame: pd.DataFrame, date: str, *, column: str = "month", issuer: str = "PERMCO:100"
) -> pd.Series:
    return frame.loc[frame["issuer_id"].eq(issuer) & frame[column].eq(date)].iloc[0]


def test_december_ranks_are_lagged_and_ties_use_permno(tmp_path: Path) -> None:
    frame = source()
    frame.loc[frame["date"].eq("2002-12-31") & frame["permno"].isin([10, 20]), "market_cap"] = 50
    result = run(tmp_path, frame)
    membership = result["membership"]
    assert membership.loc[membership["formation_year"].eq(2001), "permno"].tolist() == [11, 10]
    assert membership.loc[membership["formation_year"].eq(2002), "permno"].tolist() == [10, 20]
    assert membership.loc[membership["formation_year"].eq(2002), "effective_year"].eq(2003).all()
    assert membership.loc[membership["formation_year"].eq(2003), "effective_year"].eq(2004).all()
    assert result["quarterly"]["quarter"].min() == pd.Timestamp("2002-03-31")
    assert result["quarterly"]["quarter"].max() == pd.Timestamp("2003-12-31")
    year = result["issuer_monthly"].query("month.dt.year == 2002")
    assert "PERMCO:200" not in year["issuer_id"].tolist()
    assert len(result["monthly"]) == len(frame)


def test_portfolios_use_previous_calendar_month_caps_and_exact_compounding(tmp_path: Path) -> None:
    frame = source()
    january = frame["date"].eq("2002-01-31")
    frame.loc[january & frame["permno"].eq(10), "market_cap"] = 90
    frame.loc[january & frame["permno"].eq(11), "market_cap"] = 10
    result = run(tmp_path, frame)
    monthly = result["issuer_monthly"]
    jan = cell(monthly, "2002-01-31")
    feb = cell(monthly, "2002-02-28")
    mar = cell(monthly, "2002-03-31")
    assert jan["total_return"] == pytest.approx(0.25 * 0.1 + 0.75 * 0.2)
    assert feb["total_return"] == pytest.approx(0.9 * 0.1 + 0.1 * 0.2)
    assert jan["market_cap_usd"] == 100_000
    assert json.loads(jan["constituents"]) == [10, 11]
    assert json.loads(jan["constituent_weights"]) == [
        {"permno": 10, "weight": 0.25},
        {"permno": 11, "weight": 0.75},
    ]
    quarter = cell(result["quarterly"], "2002-03-31", column="quarter")
    assert quarter["total_return"] == pytest.approx(
        (1 + jan["total_return"]) * (1 + feb["total_return"]) * (1 + mar["total_return"]) - 1
    )
    assert quarter["source_count"] == 6
    assert quarter["market_cap_usd"] == mar["market_cap_usd"]
    assert quarter["observed"]


def test_missing_class_never_renormalizes_or_truncates_future_calendar(tmp_path: Path) -> None:
    frame = source()
    frame = frame.loc[~(frame["permno"].eq(11) & frame["date"].between("2002-02-01", "2002-12-31"))]
    result = run(tmp_path, frame)
    feb = cell(result["issuer_monthly"], "2002-02-28")
    assert not feb["observed"]
    assert pd.isna(feb["total_return"])
    assert feb["source_count"] == 1
    assert feb["selected_count"] == 2
    assert feb["status"] == "missing_source_month_unknown_exit_or_gap"
    assert pd.isna(feb["market_cap_usd"])
    first = cell(result["quarterly"], "2002-03-31", column="quarter")
    last = cell(result["quarterly"], "2002-12-31", column="quarter")
    assert not first["observed"]
    assert not last["observed"]
    assert pd.isna(first["total_return"])
    assert pd.isna(last["total_return"])
    assert json.loads(last["constituents"]) == [10, 11]


def test_missing_lag_cap_does_not_reach_across_a_source_gap(tmp_path: Path) -> None:
    frame = source()
    frame = frame.loc[~(frame["permno"].eq(10) & frame["date"].eq("2002-01-31"))]
    result = run(tmp_path, frame)
    feb = cell(result["issuer_monthly"], "2002-02-28")
    assert not feb["observed"]
    assert feb["status"] == "missing_lagged_market_cap"
    assert all(item["weight"] is None for item in json.loads(feb["constituent_weights"]))
    assert cell(result["issuer_monthly"], "2002-03-31")["observed"]


def test_missing_and_invalid_returns_are_retained_without_partial_portfolio(tmp_path: Path) -> None:
    frame = source()
    frame.loc[frame["permno"].eq(10) & frame["date"].eq("2002-01-31"), "total_return"] = np.nan
    frame.loc[frame["permno"].eq(10) & frame["date"].eq("2002-02-28"), "total_return"] = -1.1
    frame.loc[frame["permno"].eq(10) & frame["date"].eq("2002-03-31"), "total_return"] = -1
    result = run(tmp_path, frame)
    assert len(result["monthly"]) == len(frame)
    january = cell(result["issuer_monthly"], "2002-01-31")
    february = cell(result["issuer_monthly"], "2002-02-28")
    assert january["status"] == "missing_return"
    assert pd.isna(january["total_return"])
    assert february["status"] == "invalid_return"
    assert pd.isna(february["total_return"])
    assert cell(result["issuer_monthly"], "2002-03-31")["observed"]


def test_formation_identity_stays_fixed_and_change_is_visible(tmp_path: Path) -> None:
    frame = source()
    frame.loc[frame["permno"].eq(10) & frame["date"].eq("2002-02-28"), "permco"] = 999
    result = run(tmp_path, frame)
    changed = cell(result["issuer_monthly"], "2002-02-28")
    assert changed["observed"]
    assert changed["issuer_identity_changed"]
    assert changed["status"] == "observed_issuer_identity_changed"
    assert cell(result["quarterly"], "2002-03-31", column="quarter")["issuer_identity_changed"]


@pytest.mark.unit
def test_cohort_follows_formation_classes_through_its_window(tmp_path: Path) -> None:
    # Arrange: the December 2001 top two are both PERMCO 100 classes.
    frame = source()

    # Act
    cohort = run(tmp_path, frame)["cohorts"]

    # Assert: one issuer, followed for exactly the four quarters of 2002.
    assert set(cohort["formation_year"]) == {2001}
    assert set(cohort["issuer_id"]) == {"PERMCO:100"}
    assert cohort["quarter"].tolist() == list(pd.date_range("2002-03-31", periods=4, freq="QE"))
    assert cohort["observed"].all()


@pytest.mark.unit
def test_cohort_exit_leaves_later_quarters_unobserved(tmp_path: Path) -> None:
    # Arrange: both selected classes stop trading after June 2002.
    frame = source()
    frame = frame.loc[~(frame["permco"].eq(100) & frame["date"].gt("2002-06-30"))]

    # Act
    cohort = run(tmp_path, frame)["cohorts"].set_index("quarter")

    # Assert: the exit removes outcomes without dropping the issuer's rows.
    assert cohort["observed"].tolist() == [True, True, False, False]
    assert cohort["total_return"].iloc[2:].isna().all()


@pytest.mark.unit
def test_cohort_keeps_class_after_it_leaves_annual_top_rank(tmp_path: Path) -> None:
    # Arrange: one formation class falls below the next December's top two.
    frame = source()
    frame.loc[frame["date"].eq("2002-12-31") & frame["permno"].eq(20), "market_cap"] = 50
    study = compact_spec(
        "2001-01-01",
        "2003-12-31",
        top_n=2,
        formation_years=(2001,),
        primary_formation=2001,
        window_quarters=8,
    )

    # Act
    result = run(tmp_path, frame, study)

    # Assert: the fixed cohort retains both classes and their observed returns.
    assert set(result["membership"].query("formation_year == 2002")["permno"]) == {11, 20}
    quarter = cell(result["cohorts"], "2003-03-31", column="quarter")
    assert json.loads(quarter["constituents"]) == [10, 11]
    assert quarter["observed"]
    assert quarter["total_return"] == pytest.approx(1.175**3 - 1)


@pytest.mark.unit
def test_partial_quarter_after_total_loss_remains_unknown(tmp_path: Path) -> None:
    # Arrange: a selected class has a CIZ total loss before its source rows stop.
    frame = source()
    frame.loc[frame["permno"].eq(11) & frame["date"].eq("2002-02-28"), "total_return"] = -1
    frame = frame.loc[~(frame["permno"].eq(11) & frame["date"].ge("2002-03-31"))]

    # Act
    result = run(tmp_path, frame)

    # Assert: the loss is used once; the absent March does not become a zero return.
    february = cell(result["issuer_monthly"], "2002-02-28")
    assert february["total_return"] == pytest.approx(0.25 * 0.1 + 0.75 * -1)
    quarter = cell(result["cohorts"], "2002-03-31", column="quarter")
    assert not quarter["observed"]
    assert pd.isna(quarter["total_return"])
    assert quarter["status"] == "missing_source_month_unknown_exit_or_gap"


def test_order_and_future_caps_cannot_change_earlier_weights(tmp_path: Path) -> None:
    frame = source()
    original = run(tmp_path, frame)
    shuffled = run(tmp_path, frame.sample(frac=1, random_state=5))
    for key in original:
        assert frame_digest(original[key]) == frame_digest(shuffled[key])
    frame.loc[frame["date"].eq("2002-02-28"), "market_cap"] *= 100
    changed = run(tmp_path, frame)
    expected = cell(original["issuer_monthly"], "2002-01-31")["total_return"]
    assert cell(changed["issuer_monthly"], "2002-01-31")["total_return"] == expected


def test_partial_archive_quarter_and_duplicate_keys_are_explicit(tmp_path: Path) -> None:
    frame = source().loc[lambda x: x["date"].le("2002-08-31")]
    result = run(tmp_path, frame, spec(archive_end="2002-08-31"))
    last = cell(result["quarterly"], "2002-09-30", column="quarter")
    assert last["status"] == "incomplete_calendar_quarter"
    assert last["months"] == 2
    assert not last["observed"]
    with pytest.raises(ValueError, match="duplicate PERMNO-month"):
        run(tmp_path, pd.concat([frame, frame.iloc[:1]], ignore_index=True))


def test_business_month_dates_and_ticker_reuse_do_not_change_identity(tmp_path: Path) -> None:
    frame = source()
    frame.loc[frame["date"].eq("2002-03-31"), "date"] = pd.Timestamp("2002-03-28")
    frame["ticker"] = "REUSED"
    result = run(tmp_path, frame)
    assert result["monthly"]["ticker"].eq("REUSED").all()
    assert result["monthly"]["date"].eq("2002-03-28").sum() == 3
    march = cell(result["issuer_monthly"], "2002-03-31")
    assert march["observed"]
    assert json.loads(march["constituents"]) == [10, 11]
    assert cell(result["quarterly"], "2002-03-31", column="quarter")["observed"]


def test_empty_source_preserves_schemas(tmp_path: Path) -> None:
    result = run(tmp_path, source().iloc[:0])
    assert all(frame.empty for frame in result.values())
    assert set(result) == {"monthly", "membership", "issuer_monthly", "quarterly", "cohorts"}
    assert {"issuer_id", "quarter", "total_return", "observed"} <= set(result["quarterly"])
