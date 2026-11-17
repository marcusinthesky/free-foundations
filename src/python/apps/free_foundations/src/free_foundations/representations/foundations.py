"""Frozen Kumo and LimiX readouts through their pinned upstream architectures.

One member, shared prepared inputs, support-standardized outcomes, and no feature
search. Hooks observe the head input without replacing any prediction operation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np
from sklearn.preprocessing import StandardScaler

from free_foundations.runtime import inference_device

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.representations.encoding import Prepared


def load_kumo(path: str, seed: int | None = None) -> Any:  # noqa: ANN401
    """Use the upstream Large regression architecture and strictly load pinned weights."""
    import torch  # noqa: PLC0415
    from sdm.models.kumo.tabular.model import MODEL_KWARGS, _KumoTabular  # noqa: PLC0415

    torch.manual_seed(42 if seed is None else seed)
    model = _KumoTabular(
        num_classes=0, num_quantiles=999, device=inference_device(), **MODEL_KWARGS["large"]
    )
    if seed is None:
        model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True), strict=True)
    return model.to(inference_device()).eval().requires_grad_(requires_grad=False)


def load_limix(path: str) -> Any:  # noqa: ANN401
    """Use portable Torch normalization and preserve all checkpoint parameters."""
    import torch  # noqa: PLC0415
    from model.v2_0.loading import load_from_checkpoint  # noqa: PLC0415

    state = torch.load(path, map_location="cpu", weights_only=False)
    state["config"]["rmsnorm_impl"] = "torch"
    state["config"]["layer_recompute"] = False
    model, _ = load_from_checkpoint(state, deterministic=True)
    # Upstream CPU Q/K normalization reads the Triton spelling of this metadata.
    # Its Torch class stores the same dimension in normalized_shape; no weights or
    # mathematical operations change when supplying the missing alias.
    for module in model.modules():
        if isinstance(module, torch.nn.RMSNorm):
            norm: Any = module
            norm.hs = module.normalized_shape[0]
    return model.to(inference_device()).eval().requires_grad_(requires_grad=False)


def states(  # noqa: PLR0913
    data: Prepared,
    path: str,
    checkpoint: str,
    model_name: str,
    *,
    seed: int | None = None,
    batch_size: int = 128,
) -> dict[str, FloatArray]:
    """Capture ordered query representations; batching never changes the support table."""
    import torch  # noqa: PLC0415

    from free_foundations.representations.encoding import wrap_readout  # noqa: PLC0415

    model = load_kumo(path, seed) if model_name == "kumo" else load_limix(path)
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
