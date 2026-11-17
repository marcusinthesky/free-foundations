"""Chronology checks for an unbalanced public-data universe."""

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pytest

from free_foundations.universe.coverage import coverage, snapshots


def test_snapshots_use_filing_dates_and_do_not_turn_missing_debt_into_zero(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = {
        "facts": {
            "us-gaap": {
                "Assets": {
                    "units": {
                        "USD": [
                            {
                                "form": "10-K",
                                "end": "2011-12-31",
                                "filed": "2012-03-01",
                                "val": 100,
                                "accn": "a",
                            },
                            {
                                "form": "10-K",
                                "end": "2012-12-31",
                                "filed": "2013-03-01",
                                "val": 200,
                                "accn": "b",
                            },
                        ]
                    }
                }
            }
        }
    }

    def fixture_facts(_cache: Path, _cik: int) -> dict[str, Any]:
        return payload

    monkeypatch.setattr("free_foundations.universe.coverage.company_facts", fixture_facts)
    universe = pd.DataFrame({"ticker": ["A"], "cik": [1]})
    frame = snapshots(tmp_path, universe, 2011, 2013)
    assert frame.year.tolist() == [2012, 2013]
    assert frame.assets.tolist() == [100, 200]
    assert frame.debt_maturity.isna().all()
    pd.testing.assert_frame_equal(frame, snapshots(tmp_path, universe, 2011, 2013))


def test_future_price_missingness_does_not_select_the_historical_cohort() -> None:
    dates = pd.bdate_range("2017-01-01", "2020-12-31")
    prices = pd.DataFrame({"A": np.arange(len(dates), dtype=float) + 100}, index=dates)
    panel = pd.DataFrame(
        {
            "year": [2019],
            "ticker": ["A"],
            "assets": [100],
            "equity": [40],
            "debt_maturity": [np.nan],
        }
    )
    complete = coverage(panel, prices)
    prices.loc["2020":, "A"] = np.nan
    missing = coverage(panel, prices)
    assert complete.assets_and_500_prior_returns.iloc[0] == 1
    assert missing.assets_and_500_prior_returns.iloc[0] == 1
    assert missing.following_year_any_price.iloc[0] == 0
