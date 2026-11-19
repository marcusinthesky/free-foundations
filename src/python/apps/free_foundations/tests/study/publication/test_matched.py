"""Only indexed, unchanged evidence reaches the matched workshop output."""

from pathlib import Path

import pandas as pd
import pytest

from free_foundations.study.experiments.matched_evidence import collect
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
        (directory / "manifest.json").write_text("{}")
    fits = results / "factors" / "fits.parquet"
    pd.DataFrame({"factor": ["market"], "loglik": [-3.25]}).to_parquet(fits, index=False)

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
