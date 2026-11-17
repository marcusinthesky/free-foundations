"""Small audited adapters for frozen foundation-model readouts."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
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
from free_foundations.representations import cache as state_cache
from free_foundations.representations.setup import local_checkpoint
from free_foundations.runtime import inference_device

if TYPE_CHECKING:
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
    available_at: datetime | None = None
    preprocessing: str = "median-indicators-zscore-clip8-v1"
    query_period: str | None = None


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


def provenance_context(data: Prepared) -> Context:
    """Include label availability and actual support-observation identities."""
    return Context(
        identifier=data.digest,
        available_at=data.available_at or datetime(data.year - 1, 12, 31, tzinfo=UTC),
        row_ids=data.support_ids,
    )


def query_batch(data: Prepared) -> PanelBatch:
    """Bind query identities to their quarterly or legacy annual information vintage."""
    period = data.query_period or str(data.year - 1)
    return PanelBatch(
        data.query,
        tuple(f"{ticker}:{period}" for ticker in data.tickers),
        data.features,
        data.available_at or datetime(data.year - 1, 12, 31, tzinfo=UTC),
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
        preprocessing=f"{data.preprocessing}:{data.digest}",
        context=provenance_context(data),
        pooling=ConcatenatePooling(),
    )
    result = encoder.encode(batch)
    return result.values  # noqa: PD011 -- our Embeddings contract.


def randomize(network: Any, seed: int = 42) -> None:  # noqa: ANN401 -- upstream module.
    """Replace pretrained weights in place, keeping the architecture.

    Every module with ``reset_parameters`` takes its default initializer (99.98% of
    TabPFN 3.5 weights). The remaining learned tensors, CLS tokens and inducing vectors,
    are redrawn as i.i.d. Gaussians at their pretrained mean and scale; positional and
    Fourier frequencies are architecture constants and are kept.
    """
    import torch  # noqa: PLC0415

    torch.manual_seed(seed)
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
    data: Prepared,
    path: str,
    checkpoint: str,
    *,
    random: bool = False,
    seed: int = 42,
) -> dict[str, FloatArray]:
    """Use the supported native query-embedding API, one ensemble member.

    ``random`` re-initializes the fitted network's weights before encoding (`randomize`).
    """
    from tabpfn import TabPFNRegressor  # noqa: PLC0415
    from tabpfn.constants import ModelVersion  # noqa: PLC0415

    options: dict[str, Any] = {}
    if data.preprocessing.startswith("native-na"):
        from tabpfn.preprocessing.configs import PreprocessorConfig  # noqa: PLC0415

        # The wide-XBRL adapter partitions columns explicitly. Disable hidden column
        # expansion/subsampling so one member consumes the entire declared block.
        options["inference_config"] = {
            "PREPROCESS_TRANSFORMS": [
                PreprocessorConfig(
                    "none", append_original=False, max_features_per_estimator=len(data.features)
                )
            ],
            "FINGERPRINT_FEATURE": False,
            "POLYNOMIAL_FEATURES": "no",
            "FEATURE_SHIFT_METHOD": None,
            "SUBSAMPLE_SAMPLES": None,
            "OUTLIER_REMOVAL_STD": None,
            "REGRESSION_Y_PREPROCESS_TRANSFORMS": (None,),
        }
    model = TabPFNRegressor.create_default_for_version(
        ModelVersion.V3_5,
        model_path=path,
        n_estimators=1,
        device=inference_device(),
        random_state=42,
        **options,
    )
    model.fit(data.support, data.targets)
    if random:
        randomize(model.models_[0], seed)
    encoder = from_fitted(
        "tabpfn",
        model,
        feature_names=data.features,
        checkpoint=checkpoint,
        preprocessing=f"{data.preprocessing}:{data.digest}",
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
        .to(device=inference_device(), dtype=torch.bfloat16)
        .eval()
    )


def tabfm_states(data: Prepared, path: str, checkpoint: str) -> dict[str, FloatArray]:
    """Capture the post-ICL normalized prediction-head input."""
    import torch  # noqa: PLC0415

    model = load_tabfm(path)
    captured: dict[str, FloatArray] = {}
    count = len(data.support)

    def capture(_module: Module, _inputs: tuple[Tensor, ...], result: Tensor) -> None:
        captured["late"] = result[0, count:].detach().float().cpu().numpy().astype(float)

    handle = model.icl_predictor.ln.register_forward_hook(capture)
    features = torch.tensor(
        np.vstack([data.support, data.query]), dtype=torch.float32, device=inference_device()
    )[None]
    labels = StandardScaler().fit_transform(data.targets[:, None]).ravel()
    targets = torch.tensor(
        np.concatenate([labels, np.zeros(len(data.query))]),
        dtype=torch.float32,
        device=inference_device(),
    )[None]
    try:
        with torch.inference_mode():
            model(
                features,
                targets,
                torch.tensor([count], device=features.device),
                d=torch.tensor([features.shape[-1]], device=features.device),
            )
    finally:
        handle.remove()
    return {
        name: wrap_readout(data, values, "tabfm", checkpoint, name)
        for name, values in captured.items()
    }


def foundation_states(
    data: Prepared, model: str, cache: Path, _source: Path, *, store: bool = True
) -> dict[str, FloatArray]:
    """Cache numerical readouts with checkpoint, context, schema and cohort provenance.

    Audit variants pass ``store=False``: they reuse cached readouts but never add files.
    """
    base, random_marker, seed_text = model.partition("_random")
    seed = int(seed_text) if seed_text else 42
    metadata = local_checkpoint(cache, base)
    root = Path(metadata["root"])
    path = str(root / ("regression" if base == "tabfm" else metadata["files"][0]))
    checkpoint = f"{metadata['repository']}@{metadata['revision']}:{metadata['files']}"
    contract = state_cache.identity(data, model, metadata)
    destination = state_cache.location(cache, contract)
    if destination.exists():
        return state_cache.load(destination, contract)
    if model.startswith("tabpfn"):
        result = tabpfn_states(
            data,
            path,
            checkpoint,
            random=bool(random_marker),
            seed=seed,
        )
    elif base in {"kumo", "limix"}:
        from free_foundations.representations.foundations import states  # noqa: PLC0415

        result = states(data, path, checkpoint, base, seed=seed if random_marker else None)
    elif model == "tabfm":
        result = tabfm_states(data, path, checkpoint)
    else:
        message = f"Unsupported experiment model: {model}"
        raise ValueError(message)
    # New readouts are kept at float32 precision whether or not they are stored, so a
    # rerun from cache reproduces a fresh run exactly. Earlier float64 files are unchanged.
    result = {name: values.astype(np.float32).astype(np.float64) for name, values in result.items()}
    if not store:
        return result
    state_cache.save(destination, contract, result)
    return result
