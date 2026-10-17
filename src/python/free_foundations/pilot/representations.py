"""Condition one frozen pretrained readout on past accounting examples."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from free_foundations import Context, PanelBatch, from_fitted
from free_foundations.pilot.data import write_json
from free_foundations.pilot.features import FEATURES

if TYPE_CHECKING:
    from pathlib import Path

    import pandas as pd

    from free_foundations.contracts import FloatArray


def standardized(values: FloatArray) -> FloatArray:
    """Mean-impute and scale using the currently available cross-section only."""
    imputed = SimpleImputer(strategy="mean", keep_empty_features=True).fit_transform(values)
    return np.asarray(StandardScaler().fit_transform(imputed), dtype=np.float64)


def pretrained_vectors(
    panel: pd.DataFrame, query: pd.DataFrame, year: int, cache: Path
) -> FloatArray:
    """Extract TabPFN states using prior-year features to predict subsequent known ROA."""
    # Optional heavyweight imports belong at the explicitly requested inference boundary.
    import torch  # noqa: PLC0415
    from tabpfn import TabPFNRegressor  # noqa: PLC0415
    from tabpfn.constants import ModelVersion  # noqa: PLC0415

    torch.set_num_threads(2)
    checkpoint = json.loads((cache / "checkpoint.json").read_text())
    support = panel.loc[year - 3 : year - 2].copy()
    targets = panel["income"].copy()
    targets.index = pd_index_previous_year(targets.index)
    support["target"] = targets.reindex(support.index)
    support = support.dropna(subset=["target"])
    imputer = SimpleImputer(strategy="mean", keep_empty_features=True, add_indicator=True)
    scaler = StandardScaler()
    x_train = scaler.fit_transform(imputer.fit_transform(support[list(FEATURES)]))
    x_query = scaler.transform(imputer.transform(query[list(FEATURES)]))
    y_train = support["target"].to_numpy(dtype=float)
    digest = hashlib.sha256()
    for values in (x_train, y_train, x_query):
        digest.update(values.tobytes())
    digest.update(checkpoint["revision"].encode())
    key = digest.hexdigest()
    output = cache / f"tabpfn-{year}-{key[:12]}.npz"
    if output.exists():
        return np.asarray(np.load(output)["values"], dtype=np.float64)
    model = TabPFNRegressor.create_default_for_version(
        ModelVersion.V3_5_FAST,
        model_path=checkpoint["path"],
        n_estimators=1,
        device="cpu",
        random_state=42,
    )
    model.fit(x_train, y_train)
    names = tuple(str(name) for name in imputer.get_feature_names_out())
    cutoff = datetime(year - 1, 12, 31, tzinfo=UTC)
    context = Context(
        identifier=key,
        available_at=cutoff,
        row_ids=tuple(f"{ticker}:{date}" for date, ticker in support.index),
    )
    encoder = from_fitted(
        "tabpfn",
        model,
        feature_names=names,
        checkpoint=f"{checkpoint['repository']}@{checkpoint['revision']}:{checkpoint['filename']}",
        preprocessing=f"support-only mean+missingness+standardization:{key}",
        context=context,
    )
    encoded = encoder.encode(
        PanelBatch(
            values=x_query,
            row_ids=tuple(f"{ticker}:{year - 1}" for ticker in query.index),
            feature_names=names,
            as_of=cutoff,
        )
    )
    vectors = encoded.values  # noqa: PD011 -- our typed Embeddings object.
    np.savez_compressed(output, values=vectors)
    write_json(
        output.with_suffix(".json"),
        {
            "year": year,
            "checkpoint": encoder.checkpoint,
            "context_digest": key,
            "support_rows": len(support),
            "query_rows": len(query),
            "dimensions": vectors.shape[1],
            "label": "next-year annual net income/assets; known before evaluation",
            "seed": 42,
            "estimators": 1,
            "pooling": "concatenate",
            "preprocessing": encoder.preprocessing,
        },
    )
    return vectors


def pd_index_previous_year(index: pd.Index) -> pd.MultiIndex:
    """Align an available next-year profitability label with its preceding state."""
    import pandas as pd  # noqa: PLC0415

    return pd.MultiIndex.from_tuples(
        [(year - 1, ticker) for year, ticker in index], names=index.names
    )
