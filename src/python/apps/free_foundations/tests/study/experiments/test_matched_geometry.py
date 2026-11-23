"""Publish the PCoA gate disposition without initiating a below-threshold ablation."""

import json
from pathlib import Path

import pytest

from free_foundations.artifacts.hashes import file_hash
from free_foundations.study.experiments.matched_geometry import ablate


@pytest.mark.integration
def test_below_threshold_writes_decision_without_accessing_model_inputs(tmp_path: Path) -> None:
    # Arrange
    panel = tmp_path / "panel"
    panel.mkdir()
    (panel / "manifest.json").write_text("{}")
    selection = tmp_path / "selection.json"
    selection.write_text('{"status": "selected"}')
    geometry = tmp_path / "geometry"
    geometry.mkdir()
    (geometry / "manifest.json").write_text(
        json.dumps(
            {
                "selection_sha256": file_hash(selection),
                "panel_manifest_sha256": file_hash(panel / "manifest.json"),
                "status": "complete",
                "selected": {"trigger": False},
            }
        )
    )
    missing = tmp_path / "missing"
    output = tmp_path / "ablation"

    # Act
    ablate(panel, missing, selection, geometry, missing, missing, missing, missing, output, missing)

    # Assert
    manifest = json.loads((output / "manifest.json").read_text())
    assert manifest["status"] == "not_triggered"
    assert manifest["geometry_sha256"] == file_hash(geometry / "manifest.json")
    assert list(output.iterdir()) == [output / "manifest.json"]
