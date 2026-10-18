"""Pinned public checkpoints and explicitly current SIC metadata for reproducible runs."""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import UTC, datetime
from importlib.metadata import version
from pathlib import Path

import pandas as pd

from free_foundations.pilot.data import write_json

CHECKPOINTS = {
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


def ensure_checkpoints(output: Path) -> None:
    """Download immutable revisions anonymously; reuse and hash existing files."""
    from huggingface_hub import hf_hub_download  # noqa: PLC0415

    metadata = {}
    for name, (repository, revision, files) in CHECKPOINTS.items():
        root = output / "cache" / "models" / name
        hashes = {}
        for filename in files:
            destination = root / filename
            if not destination.exists():
                hf_hub_download(
                    repository, filename, revision=revision, token=False, local_dir=root
                )
            with destination.open("rb") as stream:
                hashes[filename] = hashlib.file_digest(stream, "sha256").hexdigest()
        record = {"repository": repository, "revision": revision, "files": files, "sha256": hashes}
        write_json(root / "provenance.json", record)
        metadata[name] = record
    write_json(output / "checkpoints.json", metadata)


def ensure_industry(source: Path, output: Path) -> None:
    """Use SEC submissions SIC as a current-vintage control, never label it historical."""
    if (output / "industry.csv").exists():
        return
    from edgar import set_identity  # noqa: PLC0415
    from edgar.httprequests import download_json  # noqa: PLC0415

    identity = os.environ.get("EDGAR_IDENTITY")
    if not identity:
        message = "Set EDGAR_IDENTITY before fetching the SIC control."
        raise RuntimeError(message)
    set_identity(identity)
    rows = []
    universe = pd.read_csv(source.parent / "universe.csv")
    for issuer in universe.to_dict("records"):
        time.sleep(0.25)
        data = download_json(f"https://data.sec.gov/submissions/CIK{issuer['cik']:010}.json")
        rows.append(
            {
                "ticker": issuer["ticker"],
                "sic": data.get("sic", ""),
                "description": data.get("sicDescription", ""),
                "classification_vintage": datetime.now(UTC).date().isoformat(),
            }
        )
    pd.DataFrame(rows).to_csv(output / "industry.csv", index=False)


def write_manifest(source: Path, output: Path) -> None:
    """Record fixed design choices, package versions, and original input provenance."""
    original = json.loads((source.parent / "manifest.json").read_text())
    project = Path(__file__).resolve().parents[2]
    source_hashes = {
        str(path.relative_to(project)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((project / "free_foundations").rglob("*.py"))
    }
    fast = json.loads((source / "checkpoint.json").read_text())
    with (source / fast["filename"]).open("rb") as stream:
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
