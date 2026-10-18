"""Validated numerical-state cache identities, independent of outer pipeline status."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import distribution
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared

SOURCES = (
    "encoding.py",
    "contracts.py",
    "pooling.py",
    "registry.py",
    "expanded/encoding.py",
    "expanded/foundations.py",
    "expanded/cache.py",
)
RUNTIMES = {
    "tabpfn_full": "tabpfn",
    "tabpfn_fast": "tabpfn",
    "tabfm": "tabfm",
    "kumo": "structured-data-models",
    "limix": "LimiX",
    "exaone": "exaonetabular",
}
READOUTS = {
    "tabpfn_full": ("late",),
    "tabpfn_fast": ("late",),
    "tabfm": ("early_concat", "early_mean", "late"),
    "kumo": ("early_concat", "late"),
    "limix": ("late",),
    "exaone": ("late", "item_first_concat", "item_first_mean", "item_last_concat"),
}


def digest_file(path: Path) -> str:
    """Stream a file's digest without loading large artifacts into memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(data: Prepared, model: str, checkpoint: dict[str, Any]) -> dict[str, Any]:
    """Bind inputs, extraction implementation, runtime, checkpoint and execution settings."""
    root = Path(__file__).resolve().parents[1]
    base = model.partition("_random")[0].removesuffix("_labelnull")
    runtimes = {}
    for name in ("numpy", "scipy", "scikit-learn", "torch", "huggingface-hub", RUNTIMES[base]):
        package = distribution(name)
        runtimes[name] = {
            "version": package.version,
            "direct_url": json.loads(package.read_text("direct_url.json") or "null"),
        }
    readouts = READOUTS[base]
    return {
        "schema": 2,
        "model": model,
        "context_digest": data.digest,
        "checkpoint": {key: checkpoint[key] for key in ("repository", "revision", "sha256")},
        "source_sha256": {name: digest_file(root / name) for name in SOURCES},
        "lock_sha256": digest_file(root.parents[1] / "uv.lock"),
        "runtimes": runtimes,
        "tickers": list(data.tickers),
        "support_ids": list(data.support_ids),
        "features": list(data.features),
        "year": data.year,
        "readouts": sorted(readouts),
        "execution": {"device": "cpu", "threads": 2, "members": 1, "storage": "float32"},
    }


def location(cache: Path, contract: dict[str, Any]) -> Path:
    """Content-addressed cache namespace; legacy states cannot satisfy this contract."""
    key = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return cache / "embeddings" / f"{contract['model']}-v2-{key}.npz"


def load(path: Path, contract: dict[str, Any]) -> dict[str, FloatArray]:
    """Validate metadata, payload integrity and ordered cohort before using any array."""
    metadata = json.loads(path.with_suffix(".json").read_text())
    if metadata.get("contract") != contract or metadata.get("sha256") != digest_file(path):
        message = f"Embedding cache identity or checksum mismatch: {path}"
        raise ValueError(message)
    with np.load(path, allow_pickle=False) as arrays:
        if sorted(arrays.files) != contract["readouts"]:
            message = f"Embedding cache readouts disagree: {path}"
            raise ValueError(message)
        result = {name: arrays[name].astype(np.float64) for name in arrays.files}
    for name, values in result.items():
        if (
            values.ndim != 2
            or values.shape[0] != len(contract["tickers"])
            or values.shape[1] == 0
            or not np.isfinite(values).all()
            or list(values.shape) != metadata["shapes"].get(name)
        ):
            message = f"Invalid embedding shape or values: {path}, {name}"
            raise ValueError(message)
    return result


def save(path: Path, contract: dict[str, Any], values: dict[str, FloatArray]) -> None:
    """Write arrays and their independently checked reuse contract."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {name: array.astype(np.float32) for name, array in values.items()}
    np.savez_compressed(path, **payload)
    path.with_suffix(".json").write_text(
        json.dumps(
            {
                "contract": contract,
                "sha256": digest_file(path),
                "shapes": {name: list(array.shape) for name, array in values.items()},
            },
            indent=2,
        )
        + "\n"
    )
    load(path, contract)
