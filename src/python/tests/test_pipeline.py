"""Protect the common quarterly panel, frozen sources and saved-result publication."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
PIPELINE = yaml.safe_load((ROOT / "dvc.yaml").read_text())["stages"]
STUDY = "research/crsp-study"
SPEC = f"{STUDY}/study.json"
ARCHIVE = ROOT / "research/archive/current-survivor"


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
        "sources",
        "model_checkpoints",
        "prepare",
        "representations",
        "measurement",
        "replication",
        "publication",
    }
    assert PIPELINE["prepare"]["cmd"] == "${ff} study prepare"
    assert PIPELINE["representations"]["cmd"] == "${models} study encode"
    assert PIPELINE["measurement"]["cmd"] == "${ff} study run"
    assert PIPELINE["replication"]["cmd"] == "${ff} study replicate"


def test_financial_sources_are_restored_without_running_acquisition() -> None:
    assert PIPELINE["sources"]["frozen"] is True
    assert PIPELINE["sources"]["cmd"] == "false"
    assert outputs("sources") == [f"{STUDY}/sources"]
    assert SPEC in PIPELINE["sources"]["deps"]
    assert "src/python/uv.lock" in PIPELINE["sources"]["deps"]
    for stage in PIPELINE.values():
        assert not any(".tmp/" in path for path in stage.get("deps", []))
        assert "study acquire" not in stage["cmd"]


def test_expensive_states_are_owned_separately_from_measurement() -> None:
    assert outputs("representations") == [f"{STUDY}/representations"]
    assert set(outputs("representations")) <= set(PIPELINE["measurement"]["deps"])
    assert outputs("prepare") == [f"{STUDY}/prepared"]
    assert f"{STUDY}/sources" in PIPELINE["prepare"]["deps"]
    for stage in ("representations", "measurement", "replication"):
        assert f"{STUDY}/prepared" in PIPELINE[stage]["deps"]
    assert "research/model-checkpoints.json" in PIPELINE["representations"]["deps"]
    assert "--extra" not in PIPELINE["measurement"]["cmd"]


def test_publication_reads_the_complete_retained_results_without_estimation() -> None:
    dependencies = set(PIPELINE["publication"]["deps"])
    for stage in ("model_checkpoints", "representations", "measurement", "replication"):
        assert set(outputs(stage)) <= dependencies
    assert f"{STUDY}/prepared/manifest.json" in dependencies
    assert "src/latex/main.tex" in dependencies
    assert PIPELINE["publication"]["cmd"] == "${ff} study report"
    assert outputs("publication") == [
        "src/latex/build/crsp-study.tex",
        f"{STUDY}/publication",
    ]
    assert "src/latex/build/main.pdf" not in outputs("publication")
    assert not any("cache/models" in path for path in dependencies)


def test_replication_has_no_model_or_discarded_experiment_dependency() -> None:
    dependencies = PIPELINE["replication"]["deps"]
    assert f"{STUDY}/prepared" in dependencies
    assert "src/python/src/free_foundations/fernandez/betas.R" in dependencies
    assert "devenv.nix" in dependencies
    assert "devenv.lock" in dependencies
    assert not any(
        "representations" in path or "model-checkpoints" in path for path in dependencies
    )
    assert "--extra" not in PIPELINE["replication"]["cmd"]


def test_geometry_is_a_saved_result_extension_of_the_measurement_stage() -> None:
    # The directory has one owner, including its saved geometry and inference artifacts.
    assert outputs("measurement") == [f"{STUDY}/measurement"]
    assert f"{STUDY}/measurement" in PIPELINE["publication"]["deps"]
    assert "geometry" not in PIPELINE
    for stage in PIPELINE.values():
        assert not any("daily-scores" in path for path in stage.get("deps", []))


def test_numerical_outputs_can_be_restored_from_the_dvc_cache() -> None:
    for name in PIPELINE:
        for output in PIPELINE[name]["outs"]:
            if isinstance(output, dict):
                assert next(iter(output.values())).get("cache", True)
    assert outputs("sources") == [f"{STUDY}/sources"]
    assert outputs("replication") == [f"{STUDY}/replication"]


def test_all_study_stages_bind_the_same_spec_and_command_fingerprints() -> None:
    commands = {
        "prepare": "prepare",
        "representations": "encode",
        "measurement": "run",
        "replication": "replicate",
        "publication": "report",
    }
    for stage, command in commands.items():
        assert SPEC in PIPELINE[stage]["deps"]
        assert "src/python/uv.lock" in PIPELINE[stage]["deps"]
        assert (
            f".semflow/hashes/entrypoints/free-foundations/study/{command}.json"
            in PIPELINE[stage]["deps"]
        )
    legacy = ("research/universe/", "research/panel/", "research/replication/")
    for stage in PIPELINE.values():
        assert not any(path.startswith(legacy) for path in stage.get("deps", []))


def test_legacy_pipeline_is_archived_without_changing_checkpoint_pins() -> None:
    previous = yaml.safe_load((ARCHIVE / "pipeline.yaml.snapshot").read_text())["stages"]
    locked = yaml.safe_load((ARCHIVE / "pipeline.lock.snapshot").read_text())["stages"]
    assert len(previous) == 9
    assert set(previous) == set(locked)
    assert {"universe", "pilot", "market_metadata"} <= set(previous)
    assert PIPELINE["model_checkpoints"] == previous["model_checkpoints"]
    assert not (ARCHIVE / "dvc.yaml").exists()
    assert not (ARCHIVE / "dvc.lock").exists()
    assert (ARCHIVE / "README.md").is_file()


def test_user_recipes_use_the_active_study_without_executing_wrds_script() -> None:
    recipes = (ROOT / "justfile").read_text()
    assert "free-foundations study acquire" in recipes
    assert "study acquire --output research/crsp-study/recovery" in recipes
    assert "free-foundations study freeze" in recipes
    assert "dvc unprotect" not in recipes
    assert "free-foundations study report" in recipes
    assert "dvc commit -f sources" in recipes
    assert "dvc repro measurement" in recipes
    assert "dvc repro representations" in recipes
    assert "dvc repro replication" in recipes
    assert "dvc repro publication" in recipes
    assert "free-foundations universe run" not in recipes
    assert "python src/latex/render_results.py" not in recipes
    assert "python .tmp/get_crsp_returns.py" not in recipes
