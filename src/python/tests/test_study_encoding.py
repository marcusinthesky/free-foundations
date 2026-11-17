"""Native missingness, shared observations and quarter-specific encoding provenance."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from types import ModuleType, SimpleNamespace
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
import pytest

from free_foundations.representations import encoding as native
from free_foundations.representations.encoding import Prepared, provenance_context, query_batch
from free_foundations.study import encoding
from free_foundations.study.spec import CHARACTERISTICS, StudySpec

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import PanelBatch


def fixture() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    dates = pd.date_range("2009-03-31", periods=6, freq="QE")
    panel = pd.DataFrame(
        [(issuer, date, 0.01, True) for date in dates for issuer in ("C", "A", "B")],
        columns=["issuer_id", "quarter", "total_return", "observed"],
    )
    chars = []
    broad = []
    for position, date in enumerate(dates):
        cutoff = (date.to_period("Q").start_time.to_pydatetime() - timedelta(days=1)).replace(
            tzinfo=UTC
        )
        for index, issuer in enumerate(("A", "B", "C")):
            base = {
                "issuer_id": issuer,
                "quarter": date,
                "cutoff": cutoff,
                "fact_available_at": cutoff - timedelta(days=1),
            }
            for name in CHARACTERISTICS:
                value = float(position + index + 1)
                if issuer == "A" and position == 0:
                    value = np.nan
                if issuer == "B" and position == 1 and name == "market_cap_assets":
                    value = np.nan
                chars.append(base | {"characteristic": name, "value": value})
            for name, value, standard, entity in (
                ("Assets", float(10 + position + index), True, True),
                ("ReportedNil", None, True, True),
                ("Segment", float(index), True, False),
                ("Custom", "red" if index == 0 else "blue", False, True),
            ):
                broad.append(
                    base
                    | {
                        "feature_id": name,
                        "value": value,
                        "is_standard": standard,
                        "entity_wide": entity,
                        "dimensions": "{}",
                    }
                )
    return panel, pd.DataFrame(chars), pd.DataFrame(broad)


def prepared() -> Prepared:
    support = np.arange(3 * 1001, dtype=float).reshape(3, 1001)
    query = np.arange(2 * 1001, dtype=float).reshape(2, 1001)
    support[:, ::7] = np.nan
    query[:, ::11] = np.nan
    return Prepared(
        support,
        query,
        np.array([1.0, 2.0, 3.0]),
        tuple(f"field:{i}" for i in range(1001)),
        ("A:old", "B:old", "C:old"),
        ("A", "B"),
        2020,
        "fixture",
        available_at=datetime(2020, 3, 31, 20, tzinfo=UTC),
        preprocessing="native-na-full-coverage-v1",
        query_period="2020-06-30",
    )


def test_rungs_share_all_query_and_label_conditioned_support_ids() -> None:
    panel, chars, broad = fixture()
    spec = StudySpec()
    contexts = []
    for rung in spec.rungs:
        view = encoding.rung_view(panel, chars, broad, spec, rung)
        data = encoding.prepare_quarter(view, chars, panel, pd.Timestamp("2010-03-31"), spec)
        assert data is not None
        contexts.append(data)
    first = contexts[0]
    for data in contexts:
        assert data.tickers == ("A", "B", "C")
        assert data.support_ids == first.support_ids
        np.testing.assert_array_equal(data.targets, first.targets)
        assert "A:2009-03-31" in data.support_ids
        assert "B:2009-03-31" not in data.support_ids  # Its next-quarter label is missing.
    row = first.support_ids.index("A:2009-03-31")
    assert np.isnan(first.support[row]).all()  # Missing features never remove a support row.


def test_future_concepts_categories_and_labels_cannot_change_earlier_context() -> None:
    panel, chars, broad = fixture()
    spec = StudySpec()
    quarter = pd.Timestamp("2010-03-31")
    view = encoding.rung_view(panel, chars, broad, spec, "full_xbrl")
    before = encoding.prepare_quarter(view, chars, panel, quarter, spec)
    assert before is not None
    extra = broad.loc[broad["quarter"].gt(quarter)].copy()
    extra["feature_id"] = "future_concept"
    extra["value"] = "future_category"
    extra = extra.drop_duplicates(["issuer_id", "quarter", "feature_id"])
    changed = pd.concat([broad, extra], ignore_index=True)
    changed.loc[changed["quarter"].gt(quarter) & changed["feature_id"].eq("Custom"), "value"] = (
        "new"
    )
    changed_chars = chars.copy()
    changed_chars.loc[changed_chars["quarter"].gt(quarter), "value"] = 1e8
    future_view = encoding.rung_view(panel, changed_chars, changed, spec, "full_xbrl")
    after = encoding.prepare_quarter(future_view, changed_chars, panel, quarter, spec)
    assert after is not None
    assert after.digest == before.digest
    assert after.features == before.features
    np.testing.assert_array_equal(after.support, before.support)
    np.testing.assert_array_equal(after.query, before.query)
    assert not any("future_concept" in name for name in after.features)
    assert not any("category=new" in name for name in after.features)


def test_reported_all_missing_fields_stay_and_standard_rung_is_entity_wide() -> None:
    panel, chars, broad = fixture()
    spec = StudySpec()
    standard = encoding.rung_view(panel, chars, broad, spec, "standard_xbrl")
    full = encoding.rung_view(panel, chars, broad, spec, "full_xbrl")
    assert "xbrl:Segment" not in standard
    assert "xbrl:Custom" not in standard
    assert {"xbrl:Segment", "xbrl:Custom"} <= set(full.columns)
    data = encoding.prepare_quarter(standard, chars, panel, pd.Timestamp("2010-03-31"), spec)
    assert data is not None
    column = data.features.index("xbrl:ReportedNil")
    assert np.isnan(data.support[:, column]).all()
    assert np.isnan(data.query[:, column]).all()


def test_scalar_categories_and_all_missing_columns_preserve_native_missingness() -> None:
    frame = pd.DataFrame(
        {
            "number": [1, np.nan, 3],
            "category": ["red", None, "blue"],
            "empty": [np.nan, np.nan, np.nan],
        }
    )
    matrix, names = encoding.scalar_matrix(frame)
    assert names == ("category:category=blue", "category:category=red", "empty", "number")
    assert np.isnan(matrix[1]).all()
    assert np.isnan(matrix[:, 2]).all()
    np.testing.assert_array_equal(matrix[[0, 2], :2], [[0, 1], [1, 0]])
    with pytest.raises(ValueError, match="Infinite model features"):
        encoding.scalar_matrix(pd.DataFrame({"bad": [np.inf]}))


def test_blocks_cover_every_column_once_without_filling_or_changing_rows() -> None:
    data = prepared()
    blocks = encoding.feature_blocks(data, 500)
    assert [len(block.features) for block in blocks] == [500, 500, 1]
    assert tuple(name for block in blocks for name in block.features) == data.features
    np.testing.assert_array_equal(np.concatenate([x.support for x in blocks], axis=1), data.support)
    np.testing.assert_array_equal(np.concatenate([x.query for x in blocks], axis=1), data.query)
    for block in blocks:
        assert block.support_ids == data.support_ids
        assert block.tickers == data.tickers
        assert block.available_at == data.available_at
        assert block.query_period == data.query_period
    with pytest.raises(ValueError, match="Block width"):
        encoding.feature_blocks(data, 0)


def test_quarterly_query_identity_and_cutoff_are_not_annual_aliases() -> None:
    data = prepared()
    batch = query_batch(data)
    assert batch.row_ids == ("A:2020-06-30", "B:2020-06-30")
    assert batch.as_of == data.available_at
    assert provenance_context(data).available_at == data.available_at
    annual = query_batch(replace(data, query_period=None, available_at=None))
    assert annual.row_ids == ("A:2019", "B:2019")
    assert annual.as_of == datetime(2019, 12, 31, tzinfo=UTC)


def test_no_labels_or_future_filing_evidence_never_reach_models() -> None:
    panel, chars, broad = fixture()
    chars["value"] = np.nan
    spec = StudySpec()
    for rung in spec.rungs:
        view = encoding.rung_view(panel, chars, broad, spec, rung)
        assert (
            encoding.prepare_quarter(view, chars, panel, pd.Timestamp("2010-03-31"), spec) is None
        )
    cutoff = pd.Timestamp(str(broad.loc[0, "cutoff"])).to_pydatetime()
    broad.loc[0, "fact_available_at"] = cutoff + timedelta(days=1)
    with pytest.raises(ValueError, match="published after"):
        encoding.rung_view(panel, chars, broad, spec, "full_xbrl")


def test_encode_manifest_keeps_shared_rows_and_model_failures_explicit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, chars, broad = fixture()
    spec = replace(StudySpec(), models=("mock",), block_columns=20)
    seen = []

    def controls(data: Prepared) -> dict[str, np.ndarray]:
        return {
            name: np.ones((len(data.tickers), 2))
            for name in ("direct", "pca16", "supervised_mlp16")
        }

    def model(data: Prepared, _model: str, _cache: Path, _source: Path) -> dict[str, np.ndarray]:
        seen.append(data)
        return {"late": np.ones((len(data.tickers), 2))}

    monkeypatch.setattr(encoding, "conventional_states", controls)
    monkeypatch.setattr(encoding, "foundation_states", model)
    encoding.encode_panel(panel, chars, broad, spec, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["status"] == "incomplete"  # Early queries have no available training labels.
    assert seen
    assert any(np.isnan(data.support).any() for data in seen)
    contexts = [record for record in manifest["states"] if "path" in record]
    assert all(record["issuer_ids"] == ["A", "B", "C"] for record in contexts)
    for quarter in {record["quarter"] for record in contexts}:
        rows = [record for record in contexts if record["quarter"] == quarter]
        assert len({tuple(record["support_ids"]) for record in rows}) == 1
        assert {record["rung"] for record in rows} == set(spec.rungs)
    restored = encoding.load_representations(tmp_path, panel, spec)
    assert all(set(rungs) == set(spec.rungs) for rungs in restored.values())
    changed = panel.copy()
    changed.loc[0, "observed"] = False
    changed.loc[0, "total_return"] = np.nan
    with pytest.raises(ValueError, match="different master"):
        encoding.load_representations(tmp_path, changed, spec)
    contexts[0]["issuer_ids"] = ["C", "B", "A"]
    (tmp_path / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="rows or rung"):
        encoding.load_representations(tmp_path, panel, spec)


def test_unavailable_training_context_is_reported_without_calling_any_adapter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, chars, broad = fixture()
    chars["value"] = np.nan

    def unexpected(*_args: object) -> None:
        pytest.fail("An unavailable context must not load a model.")

    monkeypatch.setattr(encoding, "conventional_states", unexpected)
    monkeypatch.setattr(encoding, "foundation_states", unexpected)
    monkeypatch.setattr(encoding, "_quarter_facts", unexpected)
    encoding.encode_panel(panel, chars, broad, StudySpec(), tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["status"] == "unavailable"
    assert {record["status"] for record in manifest["states"]} == {"training_context_unavailable"}


def test_invalid_model_rows_are_statuses_without_changing_the_cohort(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, chars, broad = fixture()
    spec = replace(StudySpec(), models=("bad",))

    def controls(data: Prepared) -> dict[str, np.ndarray]:
        return {
            name: np.ones((len(data.tickers), 2))
            for name in ("direct", "pca16", "supervised_mlp16")
        }

    def invalid(data: Prepared, _model: str, _cache: Path, _source: Path) -> dict[str, np.ndarray]:
        return {"late": np.ones((len(data.tickers) - 1, 2))}

    monkeypatch.setattr(encoding, "conventional_states", controls)
    monkeypatch.setattr(encoding, "foundation_states", invalid)
    encoding.encode_panel(panel, chars, broad, spec, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    failures = [record for record in manifest["states"] if record.get("model") == "bad"]
    assert failures
    assert {record["status"] for record in failures} == {"model_rung_unavailable"}
    contexts = [record for record in manifest["states"] if "path" in record]
    assert all(record["issuer_ids"] == ["A", "B", "C"] for record in contexts)
    assert all("bad" not in record["models"] for record in contexts)


def test_native_tabpfn_passes_full_blocks_and_declares_no_hidden_column_subsampling(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    @dataclass
    class Preprocessor:
        name: str
        append_original: bool
        max_features_per_estimator: int

    class Regressor:
        @classmethod
        def create_default_for_version(cls, version: str, **options: object) -> Regressor:
            captured["version"] = version
            captured.update(options)
            return cls()

        def fit(self, support: np.ndarray, target: np.ndarray) -> None:
            captured["support"] = support.copy()
            captured["target"] = target.copy()

    class Encoder:
        def encode(self, batch: PanelBatch) -> SimpleNamespace:
            captured["batch"] = batch
            return SimpleNamespace(values=np.ones((len(batch.row_ids), 2)))

    def fitted(*_args: object, **metadata: object) -> Encoder:
        captured["metadata"] = metadata
        return Encoder()

    package = ModuleType("tabpfn")
    package.__dict__["TabPFNRegressor"] = Regressor
    constants = ModuleType("tabpfn.constants")
    constants.__dict__["ModelVersion"] = SimpleNamespace(V3_5="3.5")
    preprocessing = ModuleType("tabpfn.preprocessing.configs")
    preprocessing.__dict__["PreprocessorConfig"] = Preprocessor
    monkeypatch.setitem(sys.modules, "tabpfn", package)
    monkeypatch.setitem(sys.modules, "tabpfn.constants", constants)
    monkeypatch.setitem(sys.modules, "tabpfn.preprocessing.configs", preprocessing)
    monkeypatch.setattr(native, "from_fitted", fitted)
    monkeypatch.setattr(native, "inference_device", lambda: "cpu")
    data = encoding.feature_blocks(prepared(), 500)[0]
    result = native.tabpfn_states(data, "unused-local-checkpoint", "mock-pinned-revision")
    np.testing.assert_array_equal(captured["support"], data.support)
    assert result["late"].shape == (2, 2)
    config = captured["inference_config"]
    assert isinstance(config, dict)
    assert config["FINGERPRINT_FEATURE"] is False
    assert config["FEATURE_SHIFT_METHOD"] is None
    assert config["SUBSAMPLE_SAMPLES"] is None
    assert config["POLYNOMIAL_FEATURES"] == "no"
    transform = config["PREPROCESS_TRANSFORMS"][0]
    assert isinstance(transform, Preprocessor)
    assert transform.max_features_per_estimator == 500
    assert not transform.append_original
    assert transform.name == "none"
    metadata = captured["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["preprocessing"] == f"{data.preprocessing}:{data.digest}"


def _mock_states(monkeypatch: pytest.MonkeyPatch, calls: list[Prepared]) -> None:
    def controls(data: Prepared) -> dict[str, np.ndarray]:
        return {
            name: np.ones((len(data.tickers), 2))
            for name in ("direct", "pca16", "supervised_mlp16")
        }

    def model(data: Prepared, _model: str, _cache: Path, _source: Path) -> dict[str, np.ndarray]:
        calls.append(data)
        return {"late": np.ones((len(data.tickers), 2))}

    monkeypatch.setattr(encoding, "conventional_states", controls)
    monkeypatch.setattr(encoding, "foundation_states", model)


@pytest.mark.parametrize("component", ["source_sha256", "lock_sha256", "checkpoints"])
def test_aggregate_states_reject_stale_inputs_and_implementation_without_runtime_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, component: str
) -> None:
    panel, chars, broad = fixture()
    spec = replace(StudySpec(), models=("mock",))
    calls = []
    _mock_states(monkeypatch, calls)
    encoding.encode_panel(panel, chars, broad, spec, tmp_path, input_digest="feature-vintage-a")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["input_digest"] == "feature-vintage-a"
    implementation = manifest["provenance"]["implementation"]
    assert "study/encoding.py" in implementation["source_sha256"]
    assert len(implementation["lock_sha256"]) == 64
    assert "numpy" in manifest["provenance"]["runtimes"]["packages"]

    def forbidden(_spec: StudySpec) -> dict[str, object]:
        pytest.fail("Financial loading must not inspect installed model runtimes.")

    monkeypatch.setattr(encoding, "_runtime_provenance", forbidden)
    assert encoding.load_representations(
        tmp_path, panel, spec, expected_input_digest="feature-vintage-a"
    )
    with pytest.raises(ValueError, match="feature vintage"):
        encoding.load_representations(
            tmp_path, panel, spec, expected_input_digest="feature-vintage-b"
        )
    with pytest.raises(ValueError, match="feature vintage"):
        encoding.load_representations(tmp_path, panel, spec)

    def changed(_spec: StudySpec) -> dict[str, object]:
        return implementation | {component: "changed"}

    monkeypatch.setattr(encoding, "_implementation_provenance", changed)
    with pytest.raises(ValueError, match="implementation, lock or approved checkpoints"):
        encoding.load_representations(
            tmp_path, panel, spec, expected_input_digest="feature-vintage-a"
        )


def test_native_cache_contracts_record_approved_weights_without_duplicate_inference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    panel, chars, broad = fixture()
    spec = replace(StudySpec(), models=("tabpfn_full",), block_columns=20)
    calls = []
    _mock_states(monkeypatch, calls)
    approved: dict[str, object] = {
        "repository": "fixture/model",
        "revision": "pinned-revision",
        "files": ["weights.ckpt"],
        "sha256": {"weights.ckpt": "0" * 64},
    }

    def checkpoint(_model: str) -> dict[str, object]:
        return approved

    def identity(data: Prepared, model: str, checkpoint: dict[str, object]) -> dict[str, object]:
        return {
            "model": model,
            "context_digest": data.digest,
            "checkpoint": checkpoint,
            "execution": {"device": "mock", "members": 1},
        }

    monkeypatch.setattr(encoding, "checkpoint_expected", checkpoint)
    monkeypatch.setattr(encoding.state_cache, "identity", identity)
    encoding.encode_panel(panel, chars, broad, spec, tmp_path, input_digest="prepared-manifest")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["provenance"]["implementation"]["checkpoints"]["tabpfn_full"] == approved
    contexts = [row for row in manifest["states"] if "path" in row]
    assert sum(len(row["native_cache_contracts"]["tabpfn_full"]) for row in contexts) == len(calls)
    for row in contexts:
        records = row["native_cache_contracts"]["tabpfn_full"]
        assert len(records) == len(row["blocks"])
        assert all(len(record["cache_contract_sha256"]) == 64 for record in records)

    def forbidden(*_args: object) -> None:
        pytest.fail("Loading aggregate states must not resolve a native cache or load a model.")

    monkeypatch.setattr(encoding.state_cache, "identity", forbidden)
    assert encoding.load_representations(
        tmp_path, panel, spec, expected_input_digest="prepared-manifest"
    )
    approved["revision"] = "different-revision"
    with pytest.raises(ValueError, match="approved checkpoints"):
        encoding.load_representations(
            tmp_path, panel, spec, expected_input_digest="prepared-manifest"
        )


def test_streamed_quarter_facts_preserve_asof_schema_and_native_values(tmp_path: Path) -> None:
    panel, chars, broad = fixture()
    broad["value"] = broad["value"].astype("string")
    source = tmp_path / "broad"
    source.mkdir()
    broad.to_parquet(source / "part-0.parquet", index=False)
    schema = broad.groupby(["feature_id", "is_standard", "entity_wide"], as_index=False).agg(
        quarter=("quarter", "min"), dimensions=("dimensions", "first")
    )
    schema.to_parquet(tmp_path / "schema.parquet", index=False)
    quarter = pd.Timestamp("2010-03-31")
    spec = StudySpec()
    context = encoding._context_panel(  # noqa: SLF001 -- exercise the streaming boundary.
        panel, chars, quarter, spec
    )
    streamed_facts, catalogue = encoding._quarter_facts(  # noqa: SLF001 -- bounded source read.
        source, context, quarter
    )
    assert streamed_facts["quarter"].le(quarter).all()
    view = encoding.rung_view(context, chars, streamed_facts, spec, "full_xbrl", schema=catalogue)
    streamed = encoding.prepare_quarter(view, chars, panel, quarter, spec)
    dense_view = encoding.rung_view(panel, chars, broad, spec, "full_xbrl")
    dense = encoding.prepare_quarter(dense_view, chars, panel, quarter, spec)
    assert streamed is not None
    assert dense is not None
    assert streamed.features == dense.features
    assert streamed.support_ids == dense.support_ids
    np.testing.assert_array_equal(streamed.support, dense.support)
    np.testing.assert_array_equal(streamed.query, dense.query)
