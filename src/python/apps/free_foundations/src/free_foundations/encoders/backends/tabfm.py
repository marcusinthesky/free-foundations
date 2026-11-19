"""Frozen TabFM query-row states."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from free_foundations.encoders.runtime import inference_device

if TYPE_CHECKING:
    from torch import Tensor
    from torch.nn import Module

    from free_foundations.encoders.context import Prepared
    from free_foundations.encoders.contracts import FloatArray


from free_foundations.encoders.readout import wrap_readout


@lru_cache(maxsize=1)
def load_tabfm(path: str) -> Any:  # noqa: ANN401 -- upstream architecture-specific modules.
    """Load the pinned 1.1 weights strictly through the runtime's generic HF loader."""
    import torch  # noqa: PLC0415
    from tabfm.src.pytorch.tabfm_v1_0_0 import TabFM_HF  # noqa: PLC0415

    return (
        TabFM_HF.from_pretrained(path, local_files_only=True, strict=True)
        .to(device=inference_device(), dtype=torch.bfloat16)
        .eval()
    )


def tabfm_states(data: Prepared, path: str, checkpoint: str) -> dict[str, FloatArray]:
    """Capture the post-ICL normalized prediction-head input."""
    import torch  # noqa: PLC0415

    model = load_tabfm(path)
    captured: dict[str, FloatArray] = {}
    count = len(data.support)

    def capture(_module: Module, _inputs: tuple[Tensor, ...], result: Tensor) -> None:
        captured["late"] = result[0, count:].detach().float().cpu().numpy().astype(float)

    handle = model.icl_predictor.ln.register_forward_hook(capture)
    features = torch.tensor(
        np.vstack([data.support, data.query]), dtype=torch.float32, device=inference_device()
    )[None]
    labels = StandardScaler().fit_transform(data.targets[:, None]).ravel()
    targets = torch.tensor(
        np.concatenate([labels, np.zeros(len(data.query))]),
        dtype=torch.float32,
        device=inference_device(),
    )[None]
    try:
        with torch.inference_mode():
            model(
                features,
                targets,
                torch.tensor([count], device=features.device),
                d=torch.tensor([features.shape[-1]], device=features.device),
            )
    finally:
        handle.remove()
    return {
        name: wrap_readout(data, values, "tabfm", checkpoint, name)
        for name, values in captured.items()
    }
