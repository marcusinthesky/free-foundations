"""Matched ablations preserve the dated comparison rows."""

import numpy as np
import pytest

from free_foundations.encoders.context import Prepared
from free_foundations.study.representations.matched_contexts import select_columns


@pytest.mark.unit
def test_broad_ablation_removes_only_the_engineered_history_from_both_tables() -> None:
    # Arrange
    data = Prepared(
        support=np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
        query=np.array([[7.0, 8.0, 9.0]]),
        targets=np.array([0.1, 0.3]),
        features=(
            "original:market_cap_assets:annual_lag0",
            "original:debt_maturity:annual_lag0",
            "xbrl:us-gaap:Assets|USD|instant",
        ),
        support_ids=("A:2015-03-31", "B:2015-03-31"),
        tickers=("A",),
        year=2016,
        digest="parent",
        query_period="2016-03-31",
    )

    # Act
    ablated = select_columns(data, "market_cap_assets", omit=True)

    # Assert
    np.testing.assert_array_equal(ablated.support, [[2, 3], [5, 6]])
    np.testing.assert_array_equal(ablated.query, [[8, 9]])
    np.testing.assert_array_equal(ablated.targets, data.targets)
    assert ablated.features == data.features[1:]
    assert ablated.support_ids == data.support_ids
    assert ablated.tickers == data.tickers
    assert ablated.query_period == data.query_period
    assert ablated.digest != data.digest
