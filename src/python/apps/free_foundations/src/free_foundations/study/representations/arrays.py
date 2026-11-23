"""Serialization and validation of representation arrays."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from free_foundations.artifacts.atomic import atomic_output

if TYPE_CHECKING:
    from pathlib import Path


def _validate_embeddings(values: np.ndarray, rows: int) -> None:
    if values.ndim != 2 or values.shape[0] != rows or not values.shape[1]:
        message = "Adapter embeddings must be nonempty and preserve every ordered query row."
        raise ValueError(message)
    if not np.isfinite(values).all():
        message = "Adapter embeddings must be finite; native missing features cannot pass through."
        raise ValueError(message)


def _save_states(destination: Path, states: dict[str, np.ndarray]) -> None:
    # The typed payload makes it explicit that no array can bind NumPy's allow_pickle argument.
    payload: dict[str, Any] = dict(states)
    with atomic_output(destination) as temporary, temporary.open("wb") as stream:
        np.savez_compressed(stream, allow_pickle=False, **payload)
