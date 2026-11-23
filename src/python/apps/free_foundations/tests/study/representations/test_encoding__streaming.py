"""Streamed contexts preserve matched inputs, native NA and as-of column scope."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.study.panel.features import _write_partition
from free_foundations.study.representations import contexts
from free_foundations.study.representations.contexts import _context_panel, _quarter_facts
from free_foundations.study.spec import CHARACTERISTICS, StudySpec

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.encoders.context import Prepared


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, StudySpec, pd.Timestamp]:
    dates = pd.date_range("2010-03-31", periods=10, freq="QE")
    panel = pd.DataFrame(
        [
            {"issuer_id": issuer, "quarter": quarter, "total_return": 0.01, "observed": True}
            for quarter in dates
            for issuer in ("A", "B", "C")
        ]
    )
    chars: list[dict[str, object]] = []
    broad: list[dict[str, object]] = []
    for position, quarter in enumerate(dates):
        cutoff = quarter.to_period("Q").start_time.tz_localize("UTC") - pd.Timedelta(days=1)
        for index, issuer in enumerate(("A", "B", "C")):
            base: dict[str, object] = {
                "issuer_id": issuer,
                "quarter": quarter,
                "cutoff": cutoff,
                "fact_available_at": cutoff - pd.Timedelta(days=1),
            }
            for name in CHARACTERISTICS:
                value = float(position + index + 1)
                if issuer == "C" and name == "market_to_book":
                    value = np.nan
                chars.append(base | {"characteristic": name, "value": value})
            broad.append(
                base
                | {
                    "feature_id": "Assets",
                    "value": float(100 + position + index),
                    "value_type": "numeric",
                    "is_standard": True,
                    "entity_wide": True,
                    "dimensions": "{}",
                }
            )
            broad.append(
                base
                | {
                    "feature_id": "Policy",
                    "value": "cash" if index == 0 else "equity",
                    "value_type": "categorical",
                    "is_standard": False,
                    "entity_wide": True,
                    "dimensions": "{}",
                }
            )
            broad.append(
                base
                | {
                    "feature_id": "Audited",
                    "value": index == 0,
                    "value_type": "categorical",
                    "is_standard": True,
                    "entity_wide": True,
                    "dimensions": "{}",
                }
            )
            broad.append(
                base
                | {
                    "feature_id": "IndustryCode",
                    "value": "0010" if index == 0 else "0020",
                    "value_type": "categorical",
                    "is_standard": True,
                    "entity_wide": True,
                    "dimensions": "{}",
                }
            )
    spec = replace(StudySpec(), support_rows=2)
    return panel, pd.DataFrame(chars), pd.DataFrame(broad), spec, dates[-2]


def _schema(broad: pd.DataFrame) -> pd.DataFrame:
    return (
        broad.groupby("feature_id", sort=True)
        .agg(
            quarter=("quarter", "min"),
            is_standard=("is_standard", "first"),
            entity_wide=("entity_wide", "first"),
            dimensions=("dimensions", "first"),
            value_type=("value_type", "first"),
        )
        .reset_index()
    )


def _save(broad: pd.DataFrame, root: Path) -> Path:
    target = root / "broad"
    for number, (_, group) in enumerate(broad.groupby("issuer_id", sort=True)):
        _write_partition(group, target, number)
    _schema(broad).to_parquet(root / "schema.parquet", index=False)
    return target


def _context(  # noqa: PLR0913, PLR0917
    broad: pd.DataFrame | Path,
    panel: pd.DataFrame,
    chars: pd.DataFrame,
    spec: StudySpec,
    quarter: pd.Timestamp,
    rung: str,
) -> Prepared:
    selected = _context_panel(panel, chars, quarter, spec)
    assert len(selected) <= spec.support_rows + 3
    facts, schema = _quarter_facts(broad, selected, quarter)
    actual = pd.MultiIndex.from_frame(facts[contexts.KEYS])
    expected = pd.MultiIndex.from_frame(selected[contexts.KEYS])
    assert actual.isin(expected).all()
    view = contexts.rung_view(selected, chars, facts, spec, rung, schema=schema)
    result = contexts.prepare_quarter(view, chars, panel, quarter, spec)
    assert result is not None
    return result


def test_path_and_memory_contexts_have_identical_inputs_and_support_for_every_rung(
    tmp_path: Path,
) -> None:
    panel, chars, broad, spec, quarter = _inputs()
    path = _save(broad, tmp_path)
    identities = []
    for rung in spec.rungs:
        memory = _context(broad, panel, chars, spec, quarter, rung)
        streamed = _context(path, panel, chars, spec, quarter, rung)
        assert memory.features == streamed.features
        assert memory.support_ids == streamed.support_ids
        assert memory.tickers == streamed.tickers == ("A", "B", "C")
        assert memory.available_at == streamed.available_at
        assert memory.digest == streamed.digest
        np.testing.assert_allclose(memory.support, streamed.support, equal_nan=True)
        np.testing.assert_allclose(memory.query, streamed.query, equal_nan=True)
        np.testing.assert_array_equal(memory.targets, streamed.targets)
        assert np.isnan(streamed.query).any()
        if rung != "fernandez":
            assert "xbrl:IndustryCode:category=0010" in streamed.features
            assert "xbrl:IndustryCode:category=0020" in streamed.features
            assert "xbrl:Audited:category=True" in streamed.features
        identities.append((streamed.support_ids, streamed.tickers))
    assert identities[0] == identities[1]


@pytest.mark.component
def test_fields_never_reported_in_the_context_are_not_encoded(tmp_path: Path) -> None:
    # Arrange: a standard field reported only as missing, outside the selected rows.
    panel, chars, broad, spec, quarter = _inputs()
    selected = _context_panel(panel, chars, quarter, spec)
    selected_keys = pd.MultiIndex.from_frame(selected[contexts.KEYS])
    other = panel.loc[
        panel["quarter"].lt(quarter)
        & ~pd.MultiIndex.from_frame(panel[contexts.KEYS]).isin(selected_keys)
    ].iloc[0]
    base = broad.iloc[0].to_dict()
    base.update(
        issuer_id=other["issuer_id"],
        quarter=other["quarter"],
        feature_id="ReportedNil",
        value=None,
        is_standard=True,
        value_type="numeric",
    )
    path = _save(pd.concat([broad, pd.DataFrame([base])], ignore_index=True), tmp_path)

    # Act
    context = _context(path, panel, chars, spec, quarter, "standard_xbrl")

    # Assert: below the coverage floor, the field never becomes a model column.
    assert "xbrl:ReportedNil" not in context.features


def test_future_columns_and_categories_do_not_change_an_earlier_streamed_context(
    tmp_path: Path,
) -> None:
    panel, chars, broad, spec, quarter = _inputs()
    historical = broad.loc[broad["quarter"].le(quarter)].copy()
    path = _save(historical, tmp_path)
    before = _context(path, panel, chars, spec, quarter, "standard_xbrl")
    future = broad.loc[broad["quarter"].gt(quarter)].copy()
    future.loc[future["feature_id"].eq("Policy"), "value"] = "future-only-category"
    added = future.iloc[[0]].assign(feature_id="FutureOnly", value="future-only-field")
    future = pd.concat([future, added], ignore_index=True)
    _write_partition(future, path, 999)
    _schema(pd.concat([historical, future], ignore_index=True)).to_parquet(
        tmp_path / "schema.parquet", index=False
    )
    after = _context(path, panel, chars, spec, quarter, "standard_xbrl")
    assert before.features == after.features
    assert before.digest == after.digest
    assert all(
        "FutureOnly" not in name and "future-only-category" not in name for name in after.features
    )
    np.testing.assert_allclose(before.query, after.query, equal_nan=True)


@pytest.mark.component
def test_streamed_reader_reads_each_part_with_only_support_and_query_keys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange: one source part per issuer.
    panel, chars, broad, spec, quarter = _inputs()
    path = _save(broad, tmp_path)
    original = contexts.read_feature_rows
    observed: list[tuple[str, pd.MultiIndex]] = []

    def capture(source: Path, keys: pd.MultiIndex) -> pd.DataFrame:
        observed.append((source.name, keys))
        return original(source, keys)

    monkeypatch.setattr(contexts, "read_feature_rows", capture)

    # Act
    _context(path, panel, chars, spec, quarter, "standard_xbrl")

    # Assert: every part is read once, in order, for the selected keys only.
    assert [name for name, _ in observed] == [
        "part-000000.parquet",
        "part-000001.parquet",
        "part-000002.parquet",
    ]
    assert all(len(keys) == spec.support_rows + 3 < len(panel) for _, keys in observed)


@pytest.mark.component
def test_streamed_latest_fact_matches_one_pass_when_an_issuer_spans_parts(
    tmp_path: Path,
) -> None:
    # Arrange: a later part restates A's query-quarter Assets at the same filing
    # time, and adds an older B Assets lag that the original filing supersedes.
    panel, chars, broad, spec, quarter = _inputs()
    original = broad.loc[broad["feature_id"].eq("Assets") & broad["quarter"].eq(quarter)]
    restated = original.loc[original["issuer_id"].eq("A")].assign(value=999.0)
    lagged = original.loc[original["issuer_id"].eq("B")].assign(
        value=-1.0,
        fact_available_at=lambda frame: frame["fact_available_at"] - pd.Timedelta(1, "D"),
    )
    extra = pd.concat([restated, lagged], ignore_index=True)
    path = _save(broad, tmp_path)
    _write_partition(extra, path, 999)
    combined = pd.concat([broad, extra], ignore_index=True)
    selected = _context_panel(panel, chars, quarter, spec)

    # Act
    views = []
    for source in (combined, path):
        facts, schema = _quarter_facts(source, selected, quarter)
        views.append(
            contexts.rung_view(selected, chars, facts, spec, "standard_xbrl", schema=schema)
        )
    memory, streamed = views

    # Assert: the tie takes the later part and the older lag never wins.
    assert streamed.loc[("A", quarter), "xbrl:Assets"] == 999.0
    assert (
        streamed.loc[("B", quarter), "xbrl:Assets"]
        == original.set_index("issuer_id").loc["B", "value"]
    )
    pd.testing.assert_frame_equal(memory, streamed)
    assert memory.attrs == streamed.attrs


def test_conflicting_declared_types_are_rejected_in_context_and_catalogue(tmp_path: Path) -> None:
    panel, chars, broad, spec, quarter = _inputs()
    broad.loc[broad["feature_id"].eq("Assets") & broad["issuer_id"].eq("A"), "value_type"] = (
        "categorical"
    )
    with pytest.raises(ValueError, match="exactly one declared"):
        _context(broad, panel, chars, spec, quarter, "standard_xbrl")
    path = _save(broad, tmp_path)
    with pytest.raises(ValueError, match=r"exactly one declared|disagrees"):
        _context(path, panel, chars, spec, quarter, "standard_xbrl")


def test_declared_numeric_feature_rejects_nonnumeric_values() -> None:
    panel, chars, broad, spec, quarter = _inputs()
    broad.loc[broad["feature_id"].eq("Assets"), "value"] = "nonnumeric"
    with pytest.raises(ValueError, match="Declared numeric XBRL"):
        _context(broad, panel, chars, spec, quarter, "standard_xbrl")
