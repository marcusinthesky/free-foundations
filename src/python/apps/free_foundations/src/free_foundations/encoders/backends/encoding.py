"""Dispatch verified frozen readouts and manage their numerical cache."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from free_foundations.encoders.backends import cache as state_cache
from free_foundations.encoders.backends.setup import local_checkpoint

if TYPE_CHECKING:
    from free_foundations.encoders.context import Prepared
    from free_foundations.encoders.contracts import FloatArray


from free_foundations.encoders.backends.tabfm import tabfm_states
from free_foundations.encoders.backends.tabpfn import tabpfn_states


def foundation_states(
    data: Prepared, model: str, weights: Path, states: Path
) -> dict[str, FloatArray]:
    """Cache numerical readouts with checkpoint, context, schema and cohort provenance.

    ``weights`` holds verified checkpoint snapshots; ``states`` caches readouts.

    """
    metadata = local_checkpoint(weights, model)
    root = Path(metadata["root"])
    path = str(root / ("regression" if model == "tabfm" else metadata["files"][0]))
    checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['files']}"
    contract = state_cache.identity(data, model, metadata)
    destination = state_cache.location(states, contract)
    if destination.exists():
        return state_cache.load(destination, contract)
    if model.startswith("tabpfn"):
        result = tabpfn_states(data, path, checkpoint)
    elif model in {"kumo", "limix"}:
        from free_foundations.encoders.backends.foundations import states  # noqa: PLC0415

        result = states(data, path, checkpoint, model)
    elif model == "tabfm":
        result = tabfm_states(data, path, checkpoint)
    else:
        message = f"Unsupported experiment model: {model}"
        raise ValueError(message)
    # New readouts are kept at float32 precision whether or not they are stored, so a
    # rerun from cache reproduces a fresh run exactly. Earlier float64 files are unchanged.
    result = {name: values.astype(np.float32).astype(np.float64) for name, values in result.items()}
    state_cache.save(destination, contract, result)
    return result
