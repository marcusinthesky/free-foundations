"""Pin the encoder implementation, checkpoints and runtime."""

from __future__ import annotations

import json
import sys
from importlib import metadata as package_metadata
from pathlib import Path
from typing import Any

from free_foundations.encoders.backends import cache as state_cache
from free_foundations.encoders.backends.checkpoints import expected as checkpoint_expected
from free_foundations.study.spec import (
    StudySpec,
    file_hash,
)


def implementation(spec: StudySpec) -> dict[str, Any]:
    """Identify reviewed code and approved weights without importing model runtimes."""
    package = Path(__file__).resolve().parents[2]
    sources = {
        *state_cache.SOURCES,
        "encoders/backends/checkpoints.py",
        "encoders/backends/setup.py",
        "study/representations/encoding.py",
        "study/representations/contexts.py",
        "study/representations/arrays.py",
        "study/representations/provenance.py",
        "study/panel/features.py",
        "study/panel/history.py",
        "artifacts/atomic.py",
        "study/spec.py",
    }
    checkpoints = {}
    for model in spec.models:
        checkpoints[model] = (
            checkpoint_expected(model)
            if model in state_cache.RUNTIMES
            else {"status": "external_adapter"}
        )
    return {
        "schema": 1,
        "source_sha256": {name: file_hash(package / name) for name in sorted(sources)},
        "lock_sha256": file_hash(package.parents[3] / "uv.lock"),
        "checkpoints": checkpoints,
    }


def runtime(spec: StudySpec) -> dict[str, Any]:
    """Record extraction dependencies; financial loading does not require these packages."""
    names = {"numpy", "pandas", "pyarrow", "scipy", "scikit-learn", "torch", "huggingface-hub"}
    for model in spec.models:
        if model in state_cache.RUNTIMES:
            names.add(state_cache.RUNTIMES[model])
    runtimes = {}
    for name in sorted(names):
        try:
            package = package_metadata.distribution(name)
        except package_metadata.PackageNotFoundError:
            runtimes[name] = {"status": "not_installed"}
        else:
            runtimes[name] = {
                "status": "installed",
                "version": package.version,
                "direct_url": json.loads(package.read_text("direct_url.json") or "null"),
            }
    return {"python": sys.version, "packages": runtimes}
