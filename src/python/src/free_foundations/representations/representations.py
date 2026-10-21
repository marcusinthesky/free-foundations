"""Declared frozen features and matched conventional controls."""

from __future__ import annotations

import gc
from typing import TYPE_CHECKING, Literal

from free_foundations.representations.baselines import compression_states, supervised_states
from free_foundations.representations.encoding import foundation_states, load_tabfm

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray
    from free_foundations.representations.encoding import Prepared

type Arm = Literal["classical", "control", "task"]
TASK: Arm = "task"
CONTROL: Arm = "control"
MODELS = ("tabpfn_full", "tabfm", "kumo", "limix")
READOUTS: dict[str, tuple[tuple[str, str, Arm], ...]] = {
    **{name: (("late", f"{name}__late", TASK),) for name in MODELS},
    **{
        f"{model}_random{suffix}": (("late", f"{model}_random{suffix}__late", CONTROL),)
        for model in ("tabpfn_full", "kumo")
        for suffix in ("", "43", "44")
    },
}
ARMS: dict[str, Arm] = {
    "direct": "classical",
    "pca16": "control",
    "supervised_mlp16": "task",
    **{name: arm for readouts in READOUTS.values() for _, name, arm in readouts},
}


def representation_states(
    data: Prepared, *, cache: Path, source: Path, models: tuple[str, ...] = MODELS
) -> dict[str, FloatArray]:
    """Construct only the declared controls and prediction-head representations."""
    states = {
        "direct": data.query,
        **compression_states(data),
        "supervised_mlp16": supervised_states(data),
    }
    for model in models:
        readouts = foundation_states(data, model, cache, source)
        for readout, name, _ in READOUTS[model]:
            states[name] = readouts[readout]
        load_tabfm.cache_clear()
        gc.collect()
    return states
