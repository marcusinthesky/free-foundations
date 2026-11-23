"""Protect the layered pipeline: frozen sources, one panel, in-sample research stages."""

from pathlib import Path

import pytest
import yaml

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "dvc.yaml").is_file())
AUTHORED = yaml.safe_load((ROOT / "dvc.yaml").read_text())["stages"]
PIPELINE = {key: value.get("do", value) for key, value in AUTHORED.items()}
PACKAGE = "src/python/apps/free_foundations/src/free_foundations"
PANEL = "data/processed/crsp-sec/panel"
STATES = "data/processed/crsp-sec/representations"
RESEARCH = (
    "research_collect_replication",
    "research_estimate_comovement",
    "research_measure_alignment",
    "research_estimate_apt",
)
# Git-tracked fingerprint JSON is a control output, not a numerical result.
EXPERIMENTS = {
    "research_collect_replication": "replication",
    "research_estimate_comovement": "comovement",
    "research_measure_alignment": "alignment",
    "research_estimate_apt": "apt",
}
CONTROL = {"semflow_refresh"}
COMMANDS = {
    "processed_prepare_panel": "processed/prepare-panel",
    "processed_prepare_contexts": "processed/prepare-contexts",
    "processed_encode": "processed/encode",
    "processed_direct": "processed/direct",
    "processed_assemble_states": "processed/assemble-states",
    "research_replicate": "research/replicate",
    "research_collect_replication": "research/collect-replication",
    "research_estimate_comovement": "research/estimate-comovement",
    "research_measure_alignment": "research/measure-alignment",
    "research_estimate_apt": "research/estimate-apt",
    "publication_render": "publication/render",
    "processed_prepare_matched_contexts": "processed/prepare-matched-contexts",
    "processed_matched_encode_legacy": "processed/encode-matched",
    "processed_matched_encode_operands": "processed/encode-matched",
    "processed_matched_encode_histories": "processed/encode-matched",
    "processed_matched_direct_legacy": "processed/encode-matched",
    "processed_matched_direct_operands": "processed/encode-matched",
    "research_prepare_matched_sample": "research/prepare-matched-sample",
    "research_matched_factors": "research/matched-factors",
    "research_matched_kernels": "research/matched-kernels",
    "research_matched_encoders": "research/matched-encoders",
    "research_matched_geometry": "research/matched-geometry",
    "research_matched_historical_geometry": "research/matched-historical-geometry",
    "research_matched_ablation": "research/matched-ablation",
    "research_collect_matched": "research/collect-matched",
    "publication_render_matched": "publication/render-matched",
}


VARIABLES = {
    name: value
    for item in yaml.safe_load((ROOT / "dvc.yaml").read_text())["vars"]
    for name, value in item.items()
}


def command(name: str) -> str:
    """A stage command with its DVC variables expanded."""
    text = PIPELINE[name]["cmd"]
    for variable, value in VARIABLES.items():
        text = text.replace(f"${{{variable}}}", value)
    return text


def outputs(name: str) -> list[str]:
    return [item if isinstance(item, str) else next(iter(item)) for item in PIPELINE[name]["outs"]]


@pytest.mark.unit
def test_each_output_has_one_owner_without_directory_overlap() -> None:
    # Arrange
    owned = [(Path(path), name) for name in PIPELINE for path in outputs(name)]

    # Act / Assert
    for i, (path, name) in enumerate(owned):
        for other, owner in owned[i + 1 :]:
            detail = (name, path, owner, other)
            assert path != other, detail
            assert path not in other.parents, detail
            assert other not in path.parents, detail


@pytest.mark.unit
def test_pipeline_has_the_four_study_layers_and_semflow_control() -> None:
    # Act / Assert
    assert set(PIPELINE) == {
        "semflow_refresh",
        "raw_sources",
        "raw_fetch_checkpoints",
        *COMMANDS,
    }
    for name, entry in COMMANDS.items():
        assert f"{entry.replace('/', ' ')}" in command(name)
        assert PIPELINE[name]["desc"]


@pytest.mark.unit
def test_financial_sources_are_restored_without_running_acquisition() -> None:
    # Arrange
    stage = PIPELINE["raw_sources"]

    # Act / Assert
    assert stage["frozen"] is True
    assert stage["cmd"] == "false"
    assert outputs("raw_sources") == ["data/raw/crsp-sec"]
    for item in PIPELINE.values():
        assert "raw acquire" not in item["cmd"]
        assert not any(path.startswith("data/staging") for path in item.get("deps", []))


@pytest.mark.unit
def test_every_estimating_stage_declares_its_params() -> None:
    # Arrange
    blocks = yaml.safe_load((ROOT / "params.yaml").read_text())

    # Act / Assert
    for name in COMMANDS.keys() - {"research_collect_matched", "publication_render_matched"}:
        declared = PIPELINE[name]["params"]
        assert declared, name
        for key in declared:
            block, _, field = key.partition(".")
            assert block in blocks, (name, key)
            assert not field or field in blocks[block], (name, key)


@pytest.mark.unit
def test_matched_comparisons_depend_on_only_their_required_cells() -> None:
    # Arrange
    factors = PIPELINE["research_matched_factors"]["deps"]
    kernels = PIPELINE["research_matched_kernels"]["deps"]
    encoder = PIPELINE["research_matched_encoders"]["deps"]
    evidence = PIPELINE["research_collect_matched"]["deps"]
    renderer = PIPELINE["publication_render_matched"]["deps"]
    cell = "data/processed/crsp-sec/matched-comparisons/cells/"

    # Act / Assert
    assert [path.removeprefix(cell) for path in factors if path.startswith(cell)] == [
        "fernandez/tabpfn_full",
    ]
    assert len([path for path in kernels if path.startswith(cell)]) == 5
    assert {path.removeprefix(cell) for path in encoder if path.startswith(cell)} == {
        "fernandez",
        "operands",
        "standard_xbrl",
    }
    assert set(outputs("research_matched_ablation")) <= set(evidence) & set(renderer)
    assert set(outputs("research_collect_matched")) <= set(renderer)


@pytest.mark.unit
def test_states_are_computed_once_and_research_reads_saved_panels() -> None:
    # Act / Assert
    assert outputs("processed_prepare_panel") == [PANEL]
    assert outputs("processed_assemble_states") == [STATES]
    assert "--extra" in command("processed_encode")
    for name in RESEARCH:
        producer = "research_replicate" if name == "research_collect_replication" else name
        assert {PANEL, STATES} <= set(PIPELINE[producer]["deps"])
        assert outputs(name) == [f"data/research/crsp-sec/experiments/{EXPERIMENTS[name]}/summary"]
        assert "--extra" not in command(name)
    assert f"{PACKAGE}/methods/fernandez/betas.R" in PIPELINE["research_replicate"]["deps"]


@pytest.mark.unit
def test_publication_reads_every_saved_result_without_estimation() -> None:
    # Arrange
    dependencies = set(PIPELINE["publication_render"]["deps"])

    # Act / Assert
    for name in RESEARCH:
        assert set(outputs(name)) <= dependencies
    assert "data/research/crsp-sec/experiments/apt/summary" in dependencies
    assert f"{PANEL}/manifest.json" in dependencies
    assert "src/latex/projects/free-foundations/src/generated" in outputs("publication_render")
    # Metrics live inside the tracked output, so they are declared at the top level.
    metrics = "data/publication/crsp-sec/free-foundations/metrics.json"
    assert yaml.safe_load((ROOT / "dvc.yaml").read_text())["metrics"] == [metrics]
    assert "data/publication/crsp-sec/free-foundations" in outputs("publication_render")
    assert "metrics" not in PIPELINE["publication_render"]
    assert not any(
        path.startswith("data/raw/models/") and path.endswith("/") for path in dependencies
    )


@pytest.mark.unit
def test_numerical_outputs_can_be_restored_from_the_dvc_cache() -> None:
    # Act / Assert
    for name in set(PIPELINE) - CONTROL:
        for output in PIPELINE[name]["outs"]:
            if isinstance(output, dict):
                assert next(iter(output.values())).get("cache", True)


@pytest.mark.unit
def test_study_stages_bind_their_command_fingerprints() -> None:
    # Act / Assert
    for name, entry in COMMANDS.items():
        deps = PIPELINE[name]["deps"]
        assert f".semflow/hashes/entrypoints/free-foundations/{entry}.json" in deps


@pytest.mark.unit
def test_user_recipes_use_the_layered_stages_without_executing_the_wrds_script() -> None:
    # Arrange
    recipes = (ROOT / "justfile").read_text()

    # Act / Assert
    assert 'stages := "env -u PYTHONPATH' in recipes
    assert 'free-foundations"' in recipes
    assert "{{ stages }} raw acquire" in recipes
    assert "{{ stages }} raw freeze" in recipes
    assert "dvc commit -f raw_sources" in recipes
    for name in (
        "processed_assemble_states",
        "research_collect_replication",
        "research_estimate_comovement",
        "research_measure_alignment",
        "publication_render",
    ):
        assert f"dvc repro {name}" in recipes
    assert "study acquire" not in recipes
    assert "research/crsp-study" not in recipes
    assert "python .tmp/get_crsp_returns.py" not in recipes
