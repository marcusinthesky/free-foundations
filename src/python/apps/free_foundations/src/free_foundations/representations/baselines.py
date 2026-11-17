"""Past-only compression and reporting-pattern controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.representations.encoding import Prepared


def supervised_states(data: Prepared) -> FloatArray:
    """A small network trained on the same support target as the foundation models.

    It shares the autoencoder's 64-16 encoder shape and a linear head, with its own
    random stream, so it controls for supervision without external pretraining.
    """
    import torch  # noqa: PLC0415
    from torch import nn  # noqa: PLC0415

    generator = torch.Generator().manual_seed(42)
    width = data.support.shape[1]
    encoder = nn.Sequential(nn.Linear(width, 64), nn.GELU(), nn.Linear(64, 16))
    head = nn.Linear(16, 1)
    with torch.no_grad():
        for parameter in [*encoder.parameters(), *head.parameters()]:
            parameter.copy_(torch.randn(parameter.shape, generator=generator) * 0.05)
    train = torch.tensor(data.support, dtype=torch.float32)
    scale = float(np.std(data.targets)) or 1.0
    target = torch.tensor((data.targets - np.mean(data.targets)) / scale, dtype=torch.float32)
    optimizer = torch.optim.AdamW(
        [*encoder.parameters(), *head.parameters()], lr=0.001, weight_decay=0.01
    )
    for _ in range(200):
        loss = (head(encoder(train)).squeeze(-1) - target).square().mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        return encoder(torch.tensor(data.query, dtype=torch.float32)).numpy().astype(float)
