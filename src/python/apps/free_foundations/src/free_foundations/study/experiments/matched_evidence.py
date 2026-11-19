"""Index the matched-comparison results for the workshop renderer."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from free_foundations.artifacts.hashes import file_hash
from free_foundations.artifacts.metadata import write_json

if TYPE_CHECKING:
    from pathlib import Path


FIT_TABLES = {"fits.parquet", "comparisons.parquet", "contributions.parquet"}


def required_artifacts(stage: str, manifest: dict[str, object]) -> set[str]:
    """Tables owned by each stage for its recorded outcome."""
    if stage == "sample":
        return {"sample.parquet", "ledger.parquet", "exposures.parquet"}
    if stage == "factors":
        return FIT_TABLES
    if stage == "kernels":
        return FIT_TABLES | {"graphs.parquet"}
    if stage == "encoders":
        return FIT_TABLES | {"selection.json"}
    if stage == "ablation":
        return (
            FIT_TABLES | {"peer_overlap.parquet"}
            if manifest["status"] in {"complete", "partial"}
            else set()
        )
    prefix = "selected" if stage == "geometry" else "historical_ratio"
    tables = ("coordinates", "spectrum", "associations")
    return (
        {f"{prefix}_{table}.parquet" for table in tables}
        if manifest["status"] == "complete"
        else set()
    )


def collect(results: Path, output: Path) -> None:
    """Record the result manifests and tabular evidence used for publication."""
    artifacts = {}
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
        paths = [
            path
            for path in sorted(directory.iterdir())
            if path.is_file() and path.suffix in (".json", ".parquet", ".csv")
        ]
        producer = json.loads((directory / "manifest.json").read_text())
        hashes = {path.name: file_hash(path) for path in paths}
        if set(hashes) != {"manifest.json", *required_artifacts(stage, producer)} or set(
            hashes
        ) != {"manifest.json", *producer["artifacts"]}:
            message = f"Unexpected matched-comparison artifact inventory for {stage}."
            raise ValueError(message)
        if any(
            hashes.get(name) != digest for name, digest in producer.get("artifacts", {}).items()
        ):
            message = f"Matched-comparison results disagree with the {stage} manifest."
            raise ValueError(message)
        artifacts[stage] = hashes
    output.mkdir(parents=True, exist_ok=True)
    write_json(output / "manifest.json", {"schema": 1, "artifacts": artifacts})
