"""Workshop evidence tables from verified matched-comparison results."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes, atomic_csv
from free_foundations.artifacts.hashes import file_hash
from free_foundations.artifacts.metadata import write_json

STAGES = ("sample", "factors", "kernels", "encoders", "geometry", "historical-geometry", "ablation")


def verify_evidence(results: Path, manifest: Path) -> dict[str, dict[str, str]]:
    """Verify indexed artifacts before binding results to publication outputs."""
    document = json.loads(manifest.read_text())
    if document["schema"] != 1:
        message = "Unknown matched-comparison evidence schema."
        raise ValueError(message)
    artifacts = document["artifacts"]
    if set(artifacts) != set(STAGES):
        message = "Incomplete matched-comparison evidence index."
        raise ValueError(message)
    for stage, files in artifacts.items():
        if "manifest.json" not in files:
            message = f"Missing manifest in matched-comparison evidence for {stage}."
            raise ValueError(message)
        for name, digest in files.items():
            if Path(name).name != name or name in {".", ".."}:
                message = f"Invalid matched-comparison evidence path: {stage}/{name}."
                raise ValueError(message)
            if file_hash(results / stage / name) != digest:
                message = f"Matched-comparison evidence changed: {stage}/{name}."
                raise ValueError(message)
    return artifacts


def render(results: Path, evidence: Path, output: Path) -> None:
    """Check the evidence index before copying or formatting any saved findings."""
    manifest = evidence / "manifest.json"
    artifacts = verify_evidence(results, manifest)
    for stage in STAGES[1:]:
        for name in artifacts[stage]:
            source = results / stage / name
            if source.suffix == ".parquet" and name != "contributions.parquet":
                destination = output / stage / source.with_suffix(".csv").name
                atomic_csv(destination, pd.read_parquet(source))
            elif source.suffix in (".json", ".csv"):
                atomic_bytes(output / stage / name, source.read_bytes())
    write_json(
        output / "manifest.json",
        {"schema": 1, "evidence_sha256": file_hash(manifest), "source_artifacts": artifacts},
    )
