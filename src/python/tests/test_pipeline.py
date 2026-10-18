"""Protect data ownership and restoration guarantees of the research DAG."""

from pathlib import Path

import pytest
import yaml

from free_foundations.panel.report import audit_checkpoints

ROOT = Path(__file__).resolve().parents[3]
PIPELINE = yaml.safe_load((ROOT / "dvc.yaml").read_text())["stages"]


def outputs(name: str) -> list[str]:
    return [item if isinstance(item, str) else next(iter(item)) for item in PIPELINE[name]["outs"]]


def test_each_output_has_one_owner_without_directory_overlap() -> None:
    owned = [(Path(path), name) for name in PIPELINE for path in outputs(name)]
    for i, (path, name) in enumerate(owned):
        for other, owner in owned[i + 1 :]:
            detail = (name, path, owner, other)
            assert path != other, detail
            assert path not in other.parents, detail
            assert other not in path.parents, detail


def test_numerical_stages_can_use_the_run_cache() -> None:
    names = {
        "expanded_run",
        "fernandez_run",
        "fernandez_simulate",
        "fernandez_combined",
        "panel_prepare",
        "panel_audit",
        "ladder_run",
        "model_checkpoints",
    } | {name for name in PIPELINE if name.startswith("panel_run_")}
    for name in names:
        for output in PIPELINE[name]["outs"]:
            if isinstance(output, dict):
                assert next(iter(output.values())).get("cache", True), (name, output)


def test_reports_depend_on_all_numerical_artifacts_they_inventory() -> None:
    for name, stage in PIPELINE.items():
        if name.startswith("panel_report_"):
            producer = name.replace("panel_report_", "panel_run_")
            assert set(outputs(producer)) <= set(stage["deps"])
            assert "research/model-checkpoints.json" in stage["deps"]
            assert "research/universe/cache/prices.parquet" in stage["deps"]
            assert "research/universe/cache/factors.parquet" in stage["deps"]
            assert "research/panel/cache/characteristics" in stage["deps"]
    assert {
        "research/fernandez/quarterly-returns.csv",
        "research/fernandez/mm-betas.csv",
        "research/fernandez/cache/characteristics.parquet",
    } <= set(PIPELINE["fernandez_combined"]["deps"])
    assert "research/expanded/cache/broad-audit.parquet" in PIPELINE["fernandez_run"]["deps"]
    assert "research/universe/universe.csv" in PIPELINE["panel_prepare"]["deps"]


def test_checkpoint_report_works_without_local_model_weights(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "research").mkdir()
    catalogue = tmp_path / "research/model-checkpoints.json"
    catalogue.write_text('{"example": {"revision": "pinned", "sha256": {"weight": "verified"}}}')
    assert audit_checkpoints()["example"]["revision"] == "pinned"
    assert not (tmp_path / "research/expanded/cache/models").exists()


def test_financial_sources_remain_frozen() -> None:
    for name in ("universe", "pilot", "market_metadata"):
        assert PIPELINE[name]["frozen"] is True
