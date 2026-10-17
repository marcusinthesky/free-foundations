"""Metric invariants, label preservation and past-only feature/target preparation."""

import hashlib
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from hypothesis import given
from numpy.testing import assert_allclose

from free_foundations.contracts import FloatArray
from free_foundations.expanded.baselines import supervised_states
from free_foundations.expanded.disclosures import broad_facts, select_schema
from free_foundations.expanded.distance import distance_weights, pairwise_distance, save_distance
from free_foundations.expanded.encoding import (
    Prepared,
    cap_support,
    prepare,
    query_rows,
    variant,
)
from tests.strategies import token_arrays


@given(token_arrays())
def test_chord_is_a_metric_and_ignores_individual_vector_length(values: FloatArray) -> None:
    rows = values.reshape(len(values), -1)
    if len(rows) < 2:
        return
    rows = np.column_stack([rows, np.ones(len(rows))])
    distance = pairwise_distance(rows)
    assert_allclose(distance, distance.T)
    assert_allclose(distance.diagonal(), 0)
    assert np.all((distance >= 0) & (distance <= 2 + 1e-12))
    assert_allclose(
        distance, pairwise_distance(rows * np.arange(1, len(rows) + 1)[:, None]), atol=1e-12
    )
    assert_allclose(distance[::-1, ::-1], pairwise_distance(rows[::-1]), atol=1e-12)
    assert_allclose(distance, pairwise_distance(-rows[:, ::-1]), atol=1e-12)
    for index in range(len(rows)):
        assert np.all(distance <= distance[:, index, None] + distance[index, None, :] + 1e-12)
    weights, bandwidth = distance_weights(distance)
    assert bandwidth > 0
    assert_allclose(weights.sum(axis=1), 1)
    assert_allclose(weights.diagonal(), 0)


def test_distance_export_preserves_both_axes_and_rejects_zero_vectors(tmp_path: Path) -> None:
    values = np.array([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    distance = pairwise_distance(values)
    assert_allclose(distance[0], [0, np.sqrt(2), 2])
    destination = tmp_path / "distance.parquet"
    save_distance(destination, distance, ("C", "A", "B"))
    stored = pd.read_parquet(destination)
    assert stored.index.tolist() == stored.columns.tolist() == ["C", "A", "B"]
    assert_allclose(stored.to_numpy(), distance)
    with pytest.raises(ValueError, match="zero embedding"):
        pairwise_distance(np.zeros((2, 3)))
    assert_allclose(pairwise_distance(np.zeros((2, 3)), "euclidean"), 0)


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


def test_future_data_cannot_change_schema_context_or_scaling() -> None:
    index = pd.MultiIndex.from_product(
        [range(2012, 2025), ["A", "B", "C"]], names=["year", "ticker"]
    )
    rng = np.random.default_rng(42)
    core = pd.DataFrame(
        rng.normal(size=(len(index), 3)),
        index=index,
        columns=["income", "operating_cash", "feature"],
    )
    core["future_concept"] = np.nan
    core.loc[(2020, slice(None)), "future_concept"] = 1
    assert "future_concept" not in select_schema(core, 2016)
    view = core[["feature"]]
    first = prepare(view, core, ("A", "B", "C"), 2016, "income")
    changed = core.copy()
    changed.loc[2016:, :] = 1e6
    second = prepare(changed[["feature"]], changed, ("A", "B", "C"), 2016, "income")
    assert first.digest == second.digest
    assert_allclose(first.support, second.support)
    assert_allclose(first.targets, second.targets)
    assert_allclose(first.query, second.query)


def _prepared(seed: int = 0) -> Prepared:
    rng = np.random.default_rng(seed)
    index = pd.MultiIndex.from_product(
        [range(2015, 2021), list("ABCDEF")], names=["year", "ticker"]
    )
    view = pd.DataFrame(rng.normal(size=(len(index), 4)), index=index, columns=list("abcd"))
    labels = pd.DataFrame(
        rng.normal(size=(len(index), 2)), index=index, columns=["income", "operating_cash"]
    )
    return prepare(view, labels, tuple("ABCDEF"), 2020, "income")


def test_support_cap_keeps_the_original_panel_digest_rule() -> None:
    data = _prepared()
    capped = cap_support(data, rows=5)
    order = sorted(
        range(len(data.support_ids)),
        key=lambda i: hashlib.sha256(data.support_ids[i].encode()).hexdigest(),
    )[:5]
    expected = hashlib.sha256((data.digest + repr(order) + "panel-support256-v1").encode())
    assert capped.digest == expected.hexdigest()
    assert capped.support_ids == tuple(data.support_ids[i] for i in order)
    redraw = cap_support(data, rows=5, salt="audit")
    assert redraw.digest != capped.digest


def test_variants_recompute_digests_and_keep_query_order() -> None:
    data = _prepared()
    subset = variant(data, "query:half", query=data.query[[2, 0]], tickers=("C", "A"))
    assert subset.digest != data.digest
    assert subset.tickers == ("C", "A")
    shuffled = variant(data, "labels", targets=data.targets[::-1])
    assert shuffled.digest not in {data.digest, subset.digest}


def test_query_rows_handles_joined_and_compact_layouts() -> None:
    import torch  # noqa: PLC0415

    joined = torch.arange(2 * 7 * 3).reshape(1, 7, 6)
    assert query_rows(joined, 4, {}).shape == (1, 3, 6)
    assert query_rows(joined, 4, {"compact_cached_support": True}).shape == (1, 7, 6)


def test_supervised_states_use_support_rows_only() -> None:
    data = _prepared(1)
    first = supervised_states(data)
    assert first.shape == (len(data.query), 16)
    assert_allclose(supervised_states(data), first)
    # Training sees support rows only: re-encoding a query subset gives the same rows.
    subset = replace(data, query=data.query[[3, 1]], tickers=("D", "B"))
    assert_allclose(supervised_states(subset), first[[3, 1]], atol=1e-6)
