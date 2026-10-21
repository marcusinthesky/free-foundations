"""Protect frozen sources, numerical ownership and inference-free publication."""

from pathlib import Path

import yaml

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


def test_pipeline_contains_only_one_study_and_supporting_replication() -> None:
    assert set(PIPELINE) == {
        "universe",
        "pilot",
        "market_metadata",
        "model_checkpoints",
        "prepare",
        "representations",
        "measurement",
        "replication",
        "publication",
    }


def test_financial_sources_are_restored_without_running_acquisition() -> None:
    for name in ("universe", "pilot", "market_metadata"):
        assert PIPELINE[name]["frozen"] is True
        assert PIPELINE[name]["cmd"] == "false"
    assert outputs("pilot") == ["research/pilot/cache"]


def test_expensive_states_are_owned_separately_from_measurement() -> None:
    assert {
        "research/panel/representations",
        "research/panel/representation-manifest.json",
    } <= set(outputs("representations"))
    assert set(outputs("representations")) <= set(PIPELINE["measurement"]["deps"])
    assert "research/panel/prepared" in outputs("prepare")
    for stage in ("representations", "measurement"):
        assert "research/panel/prepared" in PIPELINE[stage]["deps"]
    assert "--extra" not in PIPELINE["measurement"]["cmd"]


def test_publication_reads_the_complete_retained_results_without_estimation() -> None:
    assert set(outputs("measurement")) <= set(PIPELINE["publication"]["deps"])
    assert "research/replication" in PIPELINE["publication"]["deps"]
    assert PIPELINE["publication"]["cmd"] == "${ff} panel report"
    assert all(path.startswith("src/latex/build/") for path in outputs("publication"))
    assert "src/latex/build/main.pdf" not in outputs("publication")
    assert not any("cache/models" in path for path in PIPELINE["publication"]["deps"])


def test_replication_has_no_model_or_discarded_experiment_dependency() -> None:
    dependencies = PIPELINE["replication"]["deps"]
    assert "research/panel/cache/four.parquet" in dependencies
    assert not any(
        "expanded" in path or "ladder" in path or "model-checkpoints" in path
        for path in dependencies
    )
    assert "--extra" not in PIPELINE["replication"]["cmd"]


def test_numerical_outputs_can_be_restored_from_the_dvc_cache() -> None:
    # This inexpensive audit is versioned with the source rather than in DVC.
    source_reports = {"research/panel/disclosure-audit.json"}
    uncached = set()
    for name in ("model_checkpoints", "prepare", "representations", "measurement", "replication"):
        for output in PIPELINE[name]["outs"]:
            if isinstance(output, dict) and not next(iter(output.values())).get("cache", True):
                uncached.add(next(iter(output)))
    assert uncached == source_reports
    assert all((ROOT / path).is_file() for path in source_reports)
