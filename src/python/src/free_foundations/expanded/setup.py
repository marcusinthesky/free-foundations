"""Pinned public checkpoints and frozen SIC metadata for reproducible runs."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path
from typing import Any

from free_foundations.expanded.checkpoints import expected, resolve
from free_foundations.pilot.data import write_json

CHECKPOINTS = {
    "kumo": (
        "nvidia/Kumo-Tabular",
        "c5893d418e162b9f841ae179dc767afefff73831",
        ("large/regressor.pt",),
    ),
    "limix": (
        "stable-ai/LimiX-2",
        "de07b679e74a41b50b9de18251a8fa245e537440",
        ("LimiX-2.ckpt",),
    ),
    "tabpfn_full": (
        "Prior-Labs/tabpfn_3_5",
        "06bf2ba35c80a92a3b9abb436b99cf49e7a0365e",
        ("tabpfn-v3.5-20260909.safetensors",),
    ),
    "tabfm": (
        "google/tabfm-1.1.0-pytorch",
        "d7cfd3b8d184d7c8fed4210aeba9e1c967d45f2a",
        ("regression/config.json", "regression/model.safetensors"),
    ),
    "exaone": (
        "LG-AI-Research/EXAONE-Tabular",
        "093ad1c2613e1e95d26df8610451d2e02ed53cbe",
        ("exaone-tabular-regressor-v1_default.safetensors",),
    ),
}


def ensure_checkpoints(
    output: Path,
    models: tuple[str, ...] = ("tabpfn_full", "tabfm", "exaone"),
    *,
    write_catalogue: bool = True,
) -> dict[str, dict[str, object]]:
    """Verify pinned bytes before reuse; acquire missing revision-specific snapshots."""
    metadata: dict[str, dict[str, object]] = {}
    for name in models:
        repository, revision, files = CHECKPOINTS[name]
        record = expected(name)
        if (repository, revision, list(files)) != (
            record["repository"],
            record["revision"],
            record["files"],
        ):
            message = f"Checkpoint declaration differs from approved inventory: {name}"
            raise ValueError(message)
        metadata[name] = resolve(name, output / "cache")
    if write_catalogue:
        manifest = output / "checkpoints.json"
        previous = json.loads(manifest.read_text()) if manifest.exists() else {}
        write_json(manifest, previous | metadata)
    return metadata


def ensure_industry(output: Path) -> None:
    """Require the frozen SIC snapshot; numerical reproduction never queries SEC."""
    if not (output / "industry.csv").is_file():
        message = (
            "Missing frozen industry snapshot. Restore research/expanded/industry.csv "
            "from version control before reproduction; SEC acquisition is disabled here."
        )
        raise FileNotFoundError(message)


def write_manifest(source: Path, output: Path) -> None:
    """Record fixed design choices, package versions, and original input provenance."""
    original = json.loads((source.parent / "manifest.json").read_text())
    project = Path(__file__).resolve().parents[3]
    source_hashes = {
        str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((project / "src" / "free_foundations").rglob("*.py"))
    }
    fast = json.loads((source / "checkpoint.json").read_text())
    with fast_checkpoint(source).open("rb") as stream:
        fast_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    write_json(
        output / "manifest.json",
        {
            "created_at": datetime.now(UTC).isoformat(),
            "original_pilot_artifact_hashes": original["sha256"],
            "python_source_sha256": source_hashes,
            "python_lock_sha256": hashlib.sha256((project / "uv.lock").read_bytes()).hexdigest(),
            "tabpfn_fast": {
                "repository": fast["repository"],
                "revision": fast["revision"],
                "filename": fast["filename"],
                "sha256": fast_hash,
            },
            "versions": {
                name: version(name)
                for name in (
                    "numpy",
                    "pandas",
                    "scipy",
                    "scikit-learn",
                    "matplotlib",
                    "torch",
                    "tabpfn",
                    "tabfm",
                    "exaonetabular",
                )
            },
            "vocabulary": "support-period coverage >=20%; top 200 concepts, alphabetical tie-break",
            "metrics_view": (
                "first 100 concepts: USD/assets, log1p shares, plus one-year changes and log assets"
            ),
            "context": (
                "two past snapshots; next-snapshot ROA or operating cash/assets, "
                "common support rows"
            ),
            "preprocessing": "support median, missingness indicators, standardization, clip [-8,8]",
            "primary_distance": "Euclidean chord on unit-normalized vectors: sqrt(2*(1-cosine))",
            "sensitivity_distance": (
                "ordinary Euclidean distance without embedding coordinate rescaling"
            ),
            "kernel": (
                "exp(-distance^2 / median positive distance^2), zero diagonal, row normalization"
            ),
            "autoencoder": (
                "d-64-16-64-d, 20% corruption, AdamW lr=.001 weight_decay=.01, 200 epochs, seed42"
            ),
            "classification": "development study, not a newly untouched holdout",
            "industry": "current 2-digit SIC; not point-in-time",
        },
    )


def checkpoint_catalogue() -> None:
    """Acquire pinned model weights separately from financial estimation and reporting."""
    output = Path("research/expanded")
    records = ensure_checkpoints(output, tuple(CHECKPOINTS), write_catalogue=False)
    source = Path("research/pilot/cache")
    fast = json.loads((source / "checkpoint.json").read_text())
    path = fast_checkpoint(source)
    with path.open("rb") as stream:
        fast["observed_sha256"] = hashlib.file_digest(stream, "sha256").hexdigest()
    fast["path"] = str(path)
    records["tabpfn_fast"] = expected("tabpfn_fast") | {
        "path": str(path),
        "observed_sha256": fast["observed_sha256"],
    }
    write_json(Path("research/model-checkpoints.json"), records)


def fast_checkpoint(source: Path) -> Path:
    """Verify Fast weights without modifying the frozen acquisition directory."""
    metadata = json.loads((source / "checkpoint.json").read_text())
    record = expected("tabpfn_fast")
    if (metadata["repository"], metadata["revision"], [metadata["filename"]]) != (
        record["repository"],
        record["revision"],
        record["files"],
    ):
        message = "Frozen Fast descriptor differs from the approved checkpoint inventory."
        raise ValueError(message)
    legacy = source if (source / metadata["filename"]).exists() else source / "checkpoint"
    found = resolve("tabpfn_fast", Path("research/expanded/cache"), legacy)
    return Path(found["root"]) / metadata["filename"]


def local_checkpoint(cache: Path, name: str) -> dict[str, Any]:
    """Verify immutable identity and file contents before every reuse."""
    records = ensure_checkpoints(cache.parent, (name,), write_catalogue=False)
    return records[name]
