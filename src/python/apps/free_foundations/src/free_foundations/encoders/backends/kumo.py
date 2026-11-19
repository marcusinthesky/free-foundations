"""Load the pinned Kumo regression model."""

from __future__ import annotations

from typing import Any

from free_foundations.encoders.runtime import inference_device


def load_kumo(path: str) -> Any:  # noqa: ANN401
    """Use the upstream Large regression architecture and strictly load pinned weights."""
    import torch  # noqa: PLC0415
    from sdm.models.kumo.tabular.model import MODEL_KWARGS, _KumoTabular  # noqa: PLC0415

    torch.manual_seed(42)
    model = _KumoTabular(
        num_classes=0, num_quantiles=999, device=inference_device(), **MODEL_KWARGS["large"]
    )
    model.load_state_dict(torch.load(path, map_location="cpu", weights_only=True), strict=True)
    return model.to(inference_device()).eval().requires_grad_(requires_grad=False)
