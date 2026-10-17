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


def group_permutation(groups: FloatArray) -> np.ndarray:
    """Shuffle firm identity only within an explicitly supplied category."""
    rng = np.random.default_rng(42)
    permutation = np.arange(len(groups))
    for group in np.unique(groups):
        positions = np.flatnonzero(groups == group)
        permutation[positions] = rng.permutation(positions)
    return permutation
