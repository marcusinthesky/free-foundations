"""Original networks and encoders consume identical annual-spaced observations."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest
from scipy.stats import spearmanr

from free_foundations.study.analysis import fernandez_geometries
from free_foundations.study.encoding import original_view
from free_foundations.study.history import annual_history_slots
from free_foundations.study.spec import CHARACTERISTICS, StudySpec


def _histories() -> tuple[pd.DataFrame, pd.DataFrame, StudySpec, np.ndarray]:
    dates = pd.date_range("2009-03-31", "2012-09-30", freq="QE")
    issuers = ("C", "A", "B")
    annual = {
        "A": [1, 2, 3, 4],
        "B": [4, 1, 3, 2],
        "C": [1, np.nan, 2, 3],
    }
    frame = pd.DataFrame(
        [
            {
                "issuer_id": issuer,
                "quarter": date,
                "characteristic": name,
                "value": annual[issuer][date.year - 2009]
                if date.quarter == 2
                else (date.year * date.quarter) % (index + 2),
            }
            for date in dates
            for index, issuer in enumerate(issuers)
            for name in CHARACTERISTICS
        ]
    )
    panel = pd.DataFrame({"issuer_id": issuers, "quarter": pd.Timestamp("2012-06-30")})
    expected = np.array([annual[issuer][::-1] for issuer in issuers], dtype=float)
    return panel, frame, replace(StudySpec(), characteristic_history_years=4), expected


def test_fernandez_network_and_encoder_use_the_same_annual_slots_and_pair_intersections() -> None:
    panel, characteristics, spec, expected = _histories()
    encoded = original_view(panel, characteristics, spec)
    network = fernandez_geometries(
        characteristics, tuple(panel["issuer_id"]), panel["quarter"].iloc[0], spec
    )
    for name in CHARACTERISTICS:
        selected = encoded[
            [f"original:{name}:annual_lag{lag}" for lag in range(spec.characteristic_history_years)]
        ].to_numpy(float)
        np.testing.assert_array_equal(selected, expected)
        item = network[f"fernandez_{name}"]
        assert item.overlap_counts is not None
        assert item.raw_correlation is not None
        for left in range(len(panel)):
            for right in range(len(panel)):
                overlap = np.isfinite(expected[left]) & np.isfinite(expected[right])
                assert item.overlap_counts[left, right] == int(overlap.sum())
                rho = float(spearmanr(expected[left, overlap], expected[right, overlap]).statistic)
                assert item.raw_correlation[left, right] == pytest.approx(rho)


def test_intervening_quarters_and_future_snapshots_cannot_change_original_histories() -> None:
    panel, characteristics, spec, _ = _histories()
    changed = characteristics.copy()
    irrelevant = changed["quarter"].dt.quarter.ne(2) | changed["quarter"].gt("2012-06-30")
    changed.loc[irrelevant, "value"] = np.arange(int(irrelevant.sum())) ** 3 + 1e6
    before = original_view(panel, characteristics, spec)
    after = original_view(panel, changed, spec)
    pd.testing.assert_frame_equal(before, after)
    issuers = tuple(panel["issuer_id"])
    first = fernandez_geometries(characteristics, issuers, "2012Q2", spec)
    second = fernandez_geometries(changed, issuers, "2012Q2", spec)
    for name in first:
        np.testing.assert_array_equal(first[name].distance, second[name].distance)
        np.testing.assert_array_equal(first[name].weights, second[name].weights)
        np.testing.assert_array_equal(first[name].gram, second[name].gram)


def test_missing_annual_snapshots_remain_missing_and_duplicate_snapshots_are_rejected() -> None:
    panel = pd.DataFrame({"issuer_id": ["C", "A"], "quarter": pd.Timestamp("2012-06-30")})
    current = pd.DataFrame(
        {"issuer_id": ["A"], "quarter": [pd.Timestamp("2012-06-30")], "debt_maturity": [0.5]}
    ).set_index(["issuer_id", "quarter"])
    result = annual_history_slots(panel, current, years=2)
    assert tuple(result.index.get_level_values("issuer_id")) == ("C", "A")
    assert result.iloc[0].isna().all()
    assert (
        result.loc[("A", pd.Timestamp("2012-06-30")), "original:debt_maturity:annual_lag0"] == 0.5
    )
    assert result.filter(like="annual_lag1").isna().all().all()
    with pytest.raises(ValueError, match="Duplicate accounting snapshots"):
        annual_history_slots(panel, pd.concat([current, current]), years=2)
