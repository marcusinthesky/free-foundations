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


def _digest(data: Prepared, tag: str) -> str:
    digest = hashlib.sha256((data.digest + tag).encode())
    for array in (data.support, data.query, data.targets):
        digest.update(np.ascontiguousarray(array).tobytes())
    digest.update(json.dumps([data.support_ids, data.tickers]).encode())
    return digest.hexdigest()


def cap_support(
    data: Prepared, rows: int = 256, tag: str = "panel-support256-v1", salt: str = ""
) -> Prepared:
    """Deterministic, outcome-independent support cap shared by every encoder in a rung.

    A nonempty ``salt`` draws a different, equally outcome-independent support set.
    """
    order = sorted(
        range(len(data.support_ids)),
        key=lambda i: hashlib.sha256((salt + data.support_ids[i]).encode()).hexdigest(),
    )[:rows]
    digest = hashlib.sha256((data.digest + repr(order) + tag + salt).encode()).hexdigest()
    return replace(
        data,
        support=data.support[order],
        targets=data.targets[order],
        support_ids=tuple(data.support_ids[i] for i in order),
        digest=digest,
    )


def variant(data: Prepared, tag: str, **changes: Any) -> Prepared:  # noqa: ANN401
    """An audit variant (query subset, support draw or labels) with a fresh digest."""
    changed = replace(data, **changes)
    return replace(changed, digest=_digest(changed, tag))


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


def randomize(network: Any) -> None:  # noqa: ANN401 -- upstream architecture module.
    """Replace pretrained weights in place, keeping the architecture.

    Every module with ``reset_parameters`` takes its default initializer (99.98% of
    TabPFN 3.5 weights). The remaining learned tensors, CLS tokens and inducing vectors,
    are redrawn as i.i.d. Gaussians at their pretrained mean and scale; positional and
    Fourier frequencies are architecture constants and are kept.
    """
    import torch  # noqa: PLC0415

    torch.manual_seed(42)
    reset: set[str] = set()
    for name, module in network.named_modules():
        if callable(getattr(module, "reset_parameters", None)):
            module.reset_parameters()
            reset |= {
                f"{name}.{child}" if name else child
                for child, _ in module.named_parameters(recurse=False)
            }
    with torch.no_grad():
        for name, parameter in network.named_parameters():
            if name not in reset and not name.endswith(("freqs", "frequencies")):
                mean, scale = parameter.mean(), parameter.std()
                parameter.copy_(mean + scale * torch.randn_like(parameter))


def tabpfn_states(
    data: Prepared, path: str, checkpoint: str, *, fast: bool, random: bool = False
) -> dict[str, FloatArray]:
    """Use the supported native query-embedding API, one ensemble member.

    ``random`` re-initializes the fitted network's weights before encoding (`randomize`).
    """
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
    if random:
        randomize(model.models_[0])
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


def tabfm_states(
    data: Prepared, path: str, checkpoint: str, *, null_labels: bool = False
) -> dict[str, FloatArray]:
    """Capture pre-ICL row summaries and post-ICL normalized states in one forward pass.

    Support labels enter TabFM cell embeddings before column attention, so ``early``
    states are not label-free; ``null_labels`` sets every support label to zero.
    """
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
    labels = (
        np.zeros(len(data.targets))
        if null_labels
        else StandardScaler().fit_transform(data.targets[:, None]).ravel()
    )
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


def query_rows(output: Tensor, support_size: int, kwargs: dict[str, Any]) -> Tensor:
    """Query rows of a layer output: compact calls hold queries only, others are joined."""
    if kwargs.get("compact_cached_support", False):
        return output
    return output[:, support_size:]


def exaone_states(data: Prepared, path: str, checkpoint: str) -> dict[str, FloatArray]:
    """Capture the decoder-input label token and first/last-layer row summary tokens.

    First-layer item summaries attend within each row before any item attention, so they
    see support labels only through preprocessing; last-layer summaries are conditioned
    on support labels after item attention.
    """
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
    chunks: dict[str, list[FloatArray]] = {"late": [], "item_first": [], "item_last": []}

    def capture(_module: Module, arguments: tuple[Tensor, ...]) -> None:
        chunks["late"].append(
            arguments[0].detach().float().numpy().reshape(-1, manifest.model.width).astype(float)
        )

    def items(name: str) -> Any:  # noqa: ANN401 -- torch hook signature.
        def hook(
            _module: Module,
            arguments: tuple[Any, ...],
            kwargs: dict[str, Any],
            output: tuple[Tensor, Tensor, Tensor],
        ) -> None:
            support = int(arguments[3]) if len(arguments) > 3 else int(kwargs["support_size"])
            rows = query_rows(output[2], support, kwargs)
            if rows.shape[0] != 1:
                message = "EXAONE item summaries expected exactly one ensemble member."
                raise ValueError(message)
            chunks[name].append(rows[0].detach().float().numpy().reshape(rows.shape[1], -1))

        return hook

    transformer = model.model.transformer
    handles = [
        transformer.classification_heads["standard"].register_forward_pre_hook(capture),
        transformer.layers[0].register_forward_hook(items("item_first"), with_kwargs=True),
        transformer.layers[-1].register_forward_hook(items("item_last"), with_kwargs=True),
    ]
    try:
        model.predict(data.query)
    finally:
        for handle in handles:
            handle.remove()
    values = {name: np.concatenate(parts, axis=0).astype(float) for name, parts in chunks.items()}
    if any(len(array) != len(data.query) for array in values.values()):
        message = "EXAONE hooks did not return exactly one state per query."
        raise ValueError(message)
    tokens = int(transformer.item_summary_tokens.shape[2])
    readouts = {
        "late": values["late"],
        "item_first_concat": values["item_first"],
        "item_first_mean": values["item_first"].reshape(len(data.query), tokens, -1).mean(axis=1),
        "item_last_concat": values["item_last"],
    }
    labels = {
        "late": "query label token before quantile decoder",
        "item_first_concat": "first-layer item summary tokens, concatenated",
        "item_first_mean": "first-layer item summary tokens, mean",
        "item_last_concat": "last-layer item summary tokens, concatenated",
    }
    return {
        name: wrap_readout(data, array, "exaone", checkpoint, labels[name])
        for name, array in readouts.items()
    }


READOUT_VERSION = {"exaone": "readout-v2"}


def embedding_path(
    data: Prepared, model: str, checkpoint: str, cache: Path, version: str | None = None
) -> Path:
    """Cache key: context digest, checkpoint, model and that model's readout version."""
    readout = version or READOUT_VERSION.get(model, "readout-v1")
    key = hashlib.sha256(f"{data.digest}:{checkpoint}:{model}:{readout}".encode()).hexdigest()
    return cache / "embeddings" / f"{model}-{key}.npz"


def foundation_states(
    data: Prepared, model: str, cache: Path, source: Path, *, store: bool = True
) -> dict[str, FloatArray]:
    """Cache numerical readouts with checkpoint, context, schema and cohort provenance.

    Audit variants pass ``store=False``: they reuse cached readouts but never add files.
    """
    import torch  # noqa: PLC0415

    torch.set_num_threads(2)
    if model == "tabpfn_fast":
        metadata = json.loads((source / "checkpoint.json").read_text())
        path = metadata["path"]
        checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['filename']}"
    else:
        root = cache / "models" / model.removesuffix("_labelnull").removesuffix("_random")
        metadata = json.loads((root / "provenance.json").read_text())
        path = str(root / ("regression" if model.startswith("tabfm") else metadata["files"][0]))
        checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['files']}"
    destination = embedding_path(data, model, checkpoint, cache)
    if destination.exists():
        with np.load(destination) as arrays:
            return {
                name: arrays[name].astype(np.float64) for name in arrays.files if arrays[name].size
            }
    if model.startswith("tabpfn"):
        result = tabpfn_states(
            data, path, checkpoint, fast=model == "tabpfn_fast", random=model.endswith("_random")
        )
    elif model in {"tabfm", "tabfm_labelnull"}:
        result = tabfm_states(data, path, checkpoint, null_labels=model == "tabfm_labelnull")
    elif model == "exaone":
        result = exaone_states(data, path, checkpoint)
        previous = embedding_path(data, model, checkpoint, cache, version="readout-v1")
        if previous.exists():
            with np.load(previous) as arrays:
                if not np.allclose(arrays["late"], result["late"], atol=1e-6):
                    message = "EXAONE v2 label-token readout differs from the cached v1 readout."
                    raise ValueError(message)
    else:
        message = f"Unsupported experiment model: {model}"
        raise ValueError(message)
    # New readouts are kept at float32 precision whether or not they are stored, so a
    # rerun from cache reproduces a fresh run exactly. Earlier float64 files are unchanged.
    result = {name: values.astype(np.float32).astype(np.float64) for name, values in result.items()}
    if not store:
        return result
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {name: values.astype(np.float32) for name, values in result.items()}
    np.savez_compressed(destination, **payload)
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
