"""Validated numerical-state cache identities, independent of outer pipeline status."""

from __future__ import annotations

import hashlib
import json
from importlib.metadata import distribution
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from free_foundations.encoders.runtime import inference_device

if TYPE_CHECKING:
    from free_foundations.encoders.context import Prepared
    from free_foundations.encoders.contracts import FloatArray

SOURCES = (
    "encoders/encoding.py",
    "encoders/contracts.py",
    "encoders/pooling.py",
    "encoders/registry.py",
    "encoders/backends/encoding.py",
    "encoders/context.py",
    "encoders/readout.py",
    "encoders/backends/tabfm.py",
    "encoders/backends/tabpfn.py",
    "encoders/backends/kumo.py",
    "encoders/backends/limix.py",
    "encoders/backends/foundations.py",
    "encoders/backends/cache.py",
    "encoders/runtime.py",
)
RUNTIMES = {
    "tabpfn_full": "tabpfn",
    "tabfm": "tabfm",
    "kumo": "structured-data-models",
    "limix": "LimiX",
}
READOUTS = dict.fromkeys(RUNTIMES, ("late",))


def digest_file(path: Path) -> str:
    """Stream a file's digest without loading large artifacts into memory."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def identity(data: Prepared, model: str, checkpoint: dict[str, Any]) -> dict[str, Any]:
    """Bind inputs, extraction implementation, runtime, checkpoint and execution settings."""
    import torch  # noqa: PLC0415 -- optional model runtime.

    root = Path(__file__).resolve().parents[2]
    runtimes = {}
    for name in ("numpy", "scipy", "scikit-learn", "torch", "huggingface-hub", RUNTIMES[model]):
        package = distribution(name)
        runtimes[name] = {
            "version": package.version,
            "direct_url": json.loads(package.read_text("direct_url.json") or "null"),
        }
    readouts = READOUTS[model]
    return {
        "schema": 2,
        "model": model,
        "context_digest": data.digest,
        "checkpoint": {key: checkpoint[key] for key in ("repository", "revision", "sha256")},
        "source_sha256": {name: digest_file(root / name) for name in SOURCES},
        "lock_sha256": digest_file(root.parents[3] / "uv.lock"),
        "runtimes": runtimes,
        "tickers": list(data.tickers),
        "support_ids": list(data.support_ids),
        "features": list(data.features),
        "year": data.year,
        "readouts": sorted(readouts),
        "execution": {
            "device": inference_device(),
            "threads": torch.get_num_threads(),
            "members": 1,
            "storage": "float32",
        },
    }


def location(cache: Path, contract: dict[str, Any]) -> Path:
    """Content-addressed cache namespace; legacy states cannot satisfy this contract."""
    key = hashlib.sha256(json.dumps(contract, sort_keys=True).encode()).hexdigest()
    return cache / f"{contract['model']}-v2-{key}.npz"


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
