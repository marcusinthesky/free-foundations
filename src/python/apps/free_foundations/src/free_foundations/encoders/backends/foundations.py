"""Shared head-input extraction for Kumo and LimiX."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from free_foundations.encoders.runtime import inference_device

if TYPE_CHECKING:
    from free_foundations.encoders.context import Prepared
    from free_foundations.encoders.contracts import FloatArray


from free_foundations.encoders.backends.kumo import load_kumo
from free_foundations.encoders.backends.limix import load_limix


def states(
    data: Prepared,
    path: str,
    checkpoint: str,
    model_name: str,
    *,
    batch_size: int = 128,
) -> dict[str, FloatArray]:
    """Capture ordered query representations; batching never changes the support table."""
    import torch  # noqa: PLC0415

    from free_foundations.encoders.readout import wrap_readout  # noqa: PLC0415

    model = load_kumo(path) if model_name == "kumo" else load_limix(path)
    count = len(data.support)
    labels = StandardScaler().fit_transform(data.targets[:, None]).ravel()
    captured: dict[str, list[FloatArray]] = {"late": []}

    def late(_module: Any, arguments: Any) -> None:  # noqa: ANN401
        value = arguments[0].detach().float().cpu().numpy()
        captured["late"].append(value.reshape(value.shape[1], -1).astype(float))

    head = model.icl_block.head if model_name == "kumo" else model.reg_y_decoder
    handles = [head.register_forward_pre_hook(late)]
    try:
        with torch.inference_mode():
            for start in range(0, len(data.query), batch_size):
                query = data.query[start : start + batch_size]
                x = torch.as_tensor(
                    np.vstack([data.support, query]), dtype=torch.float32, device=inference_device()
                )[None]
                if model_name == "kumo":
                    model(
                        x=x,
                        y=torch.as_tensor(labels, dtype=torch.float32, device=inference_device())[
                            None
                        ],
                        categorical_mask=torch.zeros(
                            (1, x.shape[-1]), dtype=torch.bool, device=x.device
                        ),
                    )
                else:
                    y = torch.as_tensor(
                        np.concatenate([labels, np.full(len(query), np.nan)]),
                        dtype=torch.float32,
                        device=x.device,
                    )[None]
                    model(
                        x=x,
                        y=y,
                        eval_pos=count,
                        task_type="Regression",
                        feature_positional_embedding_generator=torch.Generator(
                            device=x.device
                        ).manual_seed(42),
                    )
    finally:
        for handle in handles:
            handle.remove()
    return {
        name: wrap_readout(data, np.concatenate(parts), model_name, checkpoint, name)
        for name, parts in captured.items()
    }
