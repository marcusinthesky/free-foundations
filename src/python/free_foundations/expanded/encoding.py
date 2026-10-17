"""Small audited adapters for frozen foundation-model readouts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from functools import lru_cache
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from free_foundations import (
    ConcatenatePooling,
    Context,
    PanelBatch,
    TabularEncoder,
    Tokens,
    from_fitted,
)
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from pathlib import Path

    from torch import Tensor
    from torch.nn import Module

    from free_foundations.contracts import FloatArray


@dataclass(frozen=True)
class Prepared:
    """One shared support/query table with past-only fitted preprocessing."""

    support: FloatArray
    query: FloatArray
    targets: FloatArray
    features: tuple[str, ...]
    support_ids: tuple[str, ...]
    tickers: tuple[str, ...]
    year: int
    digest: str


def prepare(
    view: pd.DataFrame, core: pd.DataFrame, tickers: tuple[str, ...], year: int, target: str
) -> Prepared:
    """Keep identical support rows across profitability and operating-cash contexts."""
    support = view.loc[year - 3 : year - 2].copy()
    labels = core[["income", "operating_cash"]].copy()
    labels.index = pd.MultiIndex.from_tuples(
        [(date - 1, ticker) for date, ticker in labels.index], names=labels.index.names
    )
    labels = labels.reindex(support.index)
    eligible = labels.notna().all(axis=1) & support.notna().any(axis=1)
    support, labels = support.loc[eligible], labels.loc[eligible]
    query = pd.DataFrame(view.xs(year - 1, level="year")).reindex(tickers)
    imputer = SimpleImputer(strategy="median", keep_empty_features=True, add_indicator=True)
    scaler = StandardScaler()
    x_support = np.clip(scaler.fit_transform(imputer.fit_transform(support)), -8, 8)
    x_query = np.clip(scaler.transform(imputer.transform(query)), -8, 8)
    y = labels[target].to_numpy(dtype=float)
    names = tuple(imputer.get_feature_names_out())
    support_ids = tuple(f"{ticker}:{date}" for date, ticker in support.index)
    digest = hashlib.sha256()
    for array in (x_support, x_query, y):
        digest.update(array.tobytes())
    digest.update(
        json.dumps(
            [names, support_ids, tickers, year, target, "median-indicators-zscore-clip8-v1"]
        ).encode()
    )
    return Prepared(x_support, x_query, y, names, support_ids, tickers, year, digest.hexdigest())


def provenance_context(data: Prepared) -> Context:
    """Include label availability and actual support-observation identities."""
    return Context(
        identifier=data.digest,
        available_at=datetime(data.year - 1, 12, 31, tzinfo=UTC),
        row_ids=data.support_ids,
    )


def query_batch(data: Prepared) -> PanelBatch:
    """Create a labeled query batch at the preceding year-end information cutoff."""
    return PanelBatch(
        data.query,
        tuple(f"{ticker}:{data.year - 1}" for ticker in data.tickers),
        data.features,
        datetime(data.year - 1, 12, 31, tzinfo=UTC),
    )


@dataclass(frozen=True)
class CapturedTokens:
    """Bind a reviewed forward-pass readout to exactly its original query cohort."""

    values: FloatArray
    row_ids: tuple[str, ...]

    def __call__(self, batch: PanelBatch) -> Tokens:
        """Reject accidental reassignment of captured row vectors."""
        if batch.row_ids != self.row_ids:
            message = "Captured model readout belongs to a different ordered query cohort."
            raise ValueError(message)
        return Tokens(self.values)


def wrap_readout(
    data: Prepared, values: FloatArray, model: str, checkpoint: str, readout: str
) -> FloatArray:
    """Validate custom native states through the existing common encoder interface."""
    batch = query_batch(data)
    encoder = TabularEncoder(
        model=model,
        extract=CapturedTokens(values[:, None, :], batch.row_ids),
        feature_names=data.features,
        checkpoint=checkpoint,
        readout=readout,
        preprocessing=f"support median+indicators+zscore+clip8:{data.digest}",
        context=provenance_context(data),
        pooling=ConcatenatePooling(),
    )
    result = encoder.encode(batch)
    return result.values  # noqa: PD011 -- our Embeddings contract.


def tabpfn_states(
    data: Prepared, path: str, checkpoint: str, *, fast: bool
) -> dict[str, FloatArray]:
    """Use the supported native query-embedding API, one ensemble member."""
    from tabpfn import TabPFNRegressor  # noqa: PLC0415
    from tabpfn.constants import ModelVersion  # noqa: PLC0415

    model = TabPFNRegressor.create_default_for_version(
        ModelVersion.V3_5_FAST if fast else ModelVersion.V3_5,
        model_path=path,
        n_estimators=1,
        device="cpu",
        random_state=42,
    )
    model.fit(data.support, data.targets)
    encoder = from_fitted(
        "tabpfn",
        model,
        feature_names=data.features,
        checkpoint=checkpoint,
        preprocessing=f"support-only:{data.digest}",
        context=provenance_context(data),
    )
    result = encoder.encode(query_batch(data))
    return {"late": result.values}  # noqa: PD011 -- our Embeddings contract.


@lru_cache(maxsize=1)
def load_tabfm(path: str) -> Any:  # noqa: ANN401 -- upstream architecture-specific modules.
    """Load the pinned 1.1 weights strictly through the runtime's generic HF loader."""
    import torch  # noqa: PLC0415
    from tabfm.src.pytorch.tabfm_v1_0_0 import TabFM_HF  # noqa: PLC0415

    return (
        TabFM_HF.from_pretrained(path, local_files_only=True, strict=True)
        .to(dtype=torch.bfloat16)
        .eval()
    )


def tabfm_states(data: Prepared, path: str, checkpoint: str) -> dict[str, FloatArray]:
    """Capture pre-ICL row summaries and post-ICL normalized states in one forward pass."""
    import torch  # noqa: PLC0415

    model = load_tabfm(path)
    captured: dict[str, FloatArray] = {}
    count = len(data.support)

    def capture_early(_module: Module, _inputs: tuple[Tensor, ...], result: Tensor) -> None:
        captured["early_concat"] = result[0, count:].detach().float().numpy().astype(float)

    def capture_late(_module: Module, _inputs: tuple[Tensor, ...], result: Tensor) -> None:
        captured["late"] = result[0, count:].detach().float().numpy().astype(float)

    handles = [
        model.row_interactor_2.register_forward_hook(capture_early),
        model.icl_predictor.ln.register_forward_hook(capture_late),
    ]
    features = torch.tensor(np.vstack([data.support, data.query]), dtype=torch.float32)[None]
    labels = StandardScaler().fit_transform(data.targets[:, None]).ravel()
    targets = torch.tensor(
        np.concatenate([labels, np.zeros(len(data.query))]), dtype=torch.float32
    )[None]
    try:
        with torch.inference_mode():
            model(features, targets, torch.tensor([count]), d=torch.tensor([features.shape[-1]]))
    finally:
        for handle in handles:
            handle.remove()
    tokens = int(model.cls_tokens.shape[0])
    captured["early_mean"] = (
        captured["early_concat"].reshape(len(data.query), tokens, -1).mean(axis=1)
    )
    return {
        name: wrap_readout(data, values, "tabfm", checkpoint, name)
        for name, values in captured.items()
    }


def exaone_states(data: Prepared, path: str, checkpoint: str) -> dict[str, FloatArray]:
    """Capture the query label-token state entering the regression decoder."""
    from exaonetabular import EXAONETabularRegressor, released_manifest  # noqa: PLC0415

    manifest = released_manifest("regression")
    regression = replace(manifest.regression, n_svd=0, member_weighting="uniform")
    manifest = replace(manifest, regression=regression)
    model = EXAONETabularRegressor.from_pretrained(
        weights=path,
        manifest=manifest,
        device="cpu",
        ensemble_count=1,
        compute_dtype="float32",
        seed=42,
    )
    model.fit(data.support, data.targets)
    chunks: list[FloatArray] = []

    def capture(_module: Module, arguments: tuple[Tensor, ...]) -> None:
        chunks.append(
            arguments[0].detach().float().numpy().reshape(-1, manifest.model.width).astype(float)
        )

    handle = model.model.transformer.classification_heads["standard"].register_forward_pre_hook(
        capture
    )
    try:
        model.predict(data.query)
    finally:
        handle.remove()
    values = np.concatenate(chunks, axis=0)
    if len(values) != len(data.query):
        message = "EXAONE decoder hook did not return exactly one state per query."
        raise ValueError(message)
    return {
        "late": wrap_readout(
            data, values, "exaone", checkpoint, "query label token before quantile decoder"
        )
    }


def foundation_states(
    data: Prepared, model: str, cache: Path, source: Path
) -> dict[str, FloatArray]:
    """Cache numerical readouts with checkpoint, context, schema and cohort provenance."""
    import torch  # noqa: PLC0415

    torch.set_num_threads(2)
    if model == "tabpfn_fast":
        metadata = json.loads((source / "checkpoint.json").read_text())
        path = metadata["path"]
        checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['filename']}"
    else:
        root = cache / "models" / model
        metadata = json.loads((root / "provenance.json").read_text())
        path = str(root / ("regression" if model == "tabfm" else metadata["files"][0]))
        checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['files']}"
    key = hashlib.sha256(f"{data.digest}:{checkpoint}:{model}:readout-v1".encode()).hexdigest()
    destination = cache / "embeddings" / f"{model}-{key}.npz"
    if destination.exists():
        with np.load(destination) as arrays:
            return {name: arrays[name] for name in arrays.files if arrays[name].size}
    if model.startswith("tabpfn"):
        result = tabpfn_states(data, path, checkpoint, fast=model == "tabpfn_fast")
    elif model == "tabfm":
        result = tabfm_states(data, path, checkpoint)
    elif model == "exaone":
        result = exaone_states(data, path, checkpoint)
    else:
        message = f"Unsupported experiment model: {model}"
        raise ValueError(message)
    destination.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        destination,
        late=result["late"],
        early_concat=result.get("early_concat", np.empty((0, 0))),
        early_mean=result.get("early_mean", np.empty((0, 0))),
    )
    write_json(
        destination.with_suffix(".json"),
        {
            "checkpoint": checkpoint,
            "context_digest": data.digest,
            "year": data.year,
            "support_rows": len(data.support),
            "support_ids": data.support_ids,
            "features": data.features,
            "tickers": data.tickers,
            "readout_shapes": {name: list(values.shape) for name, values in result.items()},
            "seed": 42,
            "preprocessing": "support median, indicators, standardize, clip [-8,8]",
        },
    )
    return result
