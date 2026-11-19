"""Load the pinned LimiX regression model."""

from __future__ import annotations

from typing import Any

from free_foundations.encoders.runtime import inference_device


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
