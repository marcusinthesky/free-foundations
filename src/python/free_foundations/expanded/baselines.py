"""Past-only compression and reporting-pattern controls."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
from sklearn.decomposition import PCA

if TYPE_CHECKING:
    import pandas as pd

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.encoding import Prepared


def compression_states(data: Prepared) -> dict[str, FloatArray]:
    """Fit PCA and a small denoising autoencoder on past support rows only."""
    import torch  # noqa: PLC0415
    from torch import nn  # noqa: PLC0415

    torch.set_num_threads(2)
    torch.manual_seed(42)
    width = data.support.shape[1]
    encoder = nn.Sequential(nn.Linear(width, 64), nn.GELU(), nn.Linear(64, 16))
    decoder = nn.Sequential(nn.Linear(16, 64), nn.GELU(), nn.Linear(64, width))
    model = nn.Sequential(encoder, decoder)
    train = torch.tensor(data.support, dtype=torch.float32)
    query = torch.tensor(data.query, dtype=torch.float32)
    with torch.no_grad():
        random_states = encoder(query).numpy().astype(float)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    for _ in range(200):
        noisy = train * (torch.rand_like(train) >= 0.2)
        loss = (model(noisy) - train).square().mean()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    with torch.no_grad():
        learned = encoder(query).numpy().astype(float)
    pca = PCA(n_components=min(16, width, len(train)), random_state=42).fit(data.support)
    return {
        "pca16": np.asarray(pca.transform(data.query), dtype=np.float64),
        "autoencoder": learned,
        "random_autoencoder": random_states,
    }


def supervised_states(data: Prepared) -> FloatArray:
    """A small network trained on the same support target as the foundation models.

    It shares the autoencoder's 64-16 encoder shape and a linear head, with its own
    random stream, so it controls for supervision without external pretraining.
    """
    import torch  # noqa: PLC0415
    from torch import nn  # noqa: PLC0415

    torch.set_num_threads(2)
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


def industry_vectors(industry: pd.DataFrame, tickers: tuple[str, ...]) -> FloatArray:
    """Current two-digit SIC, explicitly a non-point-in-time robustness control."""
    groups = (
        industry.set_index("ticker")["sic"]
        .astype(str)
        .str.zfill(4)
        .str[:2]
        .reindex(tickers)
        .fillna("unknown")
    )
    return np.asarray(groups.to_numpy()[:, None] == np.unique(groups)[None, :], dtype=np.float64)


def group_permutation(groups: FloatArray, seed: int = 42) -> np.ndarray:
    """Shuffle firm identity only within an explicitly supplied category."""
    rng = np.random.default_rng(seed)
    permutation = np.arange(len(groups))
    for group in np.unique(groups):
        positions = np.flatnonzero(groups == group)
        permutation[positions] = rng.permutation(positions)
    return permutation
