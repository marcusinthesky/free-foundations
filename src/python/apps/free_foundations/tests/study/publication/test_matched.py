"""Only indexed, unchanged evidence reaches the matched workshop output."""

import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

from free_foundations.study.experiments.matched_evidence import collect, required_artifacts
from free_foundations.study.publication.matched import render


@pytest.mark.integration
def test_render_reads_saved_results_and_refuses_changed_evidence(tmp_path: Path) -> None:
    # Arrange
    results = tmp_path / "results"
    evidence = results / "evidence"
    output = tmp_path / "publication"
    for stage in (
        "sample",
        "factors",
        "kernels",
        "encoders",
        "geometry",
        "historical-geometry",
        "ablation",
    ):
        directory = results / stage
        directory.mkdir(parents=True)
        manifest: dict[str, object] = {"status": "unavailable"}
        hashes = {}
        for name in required_artifacts(stage, manifest):
            path = directory / name
            if path.suffix == ".json":
                path.write_text("{}")
            else:
                pd.DataFrame({"factor": ["market"], "loglik": [-3.25]}).to_parquet(
                    path, index=False
                )
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (directory / "manifest.json").write_text(json.dumps(manifest | {"artifacts": hashes}))
    fits = results / "factors" / "fits.parquet"
    # Act
    collect(results, evidence)
    render(results, evidence, output)

    # Assert
    assert pd.read_csv(output / "factors" / "fits.csv").to_dict("records") == [
        {"factor": "market", "loglik": -3.25},
    ]
    fits.write_bytes(b"changed")
    with pytest.raises(ValueError, match="evidence changed"):
        render(results, evidence, output)
    with pytest.raises(ValueError, match="disagree"):
        collect(results, evidence)
    (results / "factors" / "unexpected.csv").write_text("stale")
    with pytest.raises(ValueError, match="inventory"):
        collect(results, evidence)
