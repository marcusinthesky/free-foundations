"""Bind verified native methods or explicit readouts to one encoding interface."""

from dataclasses import dataclass, field
from typing import Literal, Protocol

import numpy as np

from free_foundations.contracts import (
    Context,
    Embeddings,
    Extractor,
    FloatArray,
    PanelBatch,
    Pooling,
    Provenance,
    Tokens,
    frozen_array,
)
from free_foundations.pooling import ConcatenatePooling
from free_foundations.registry import model_spec


@dataclass(frozen=True, kw_only=True)
class TabularEncoder:
    """An immutable measurement recipe around a caller-owned inference backend.

    No fitting, batching, imputation or hidden-layer selection happens here.
    In particular, splitting a query table can change contextual embeddings.
    """

    model: str
    extract: Extractor
    feature_names: tuple[str, ...]
    checkpoint: str
    readout: str
    preprocessing: str
    context: Context | None = None
    pooling: Pooling = field(default_factory=ConcatenatePooling)
    normalize: bool = False

    def __post_init__(self) -> None:
        """Require the choices necessary to interpret an embedding."""
        model_spec(self.model)
        if not all((self.feature_names, self.checkpoint, self.readout, self.preprocessing)):
            msg = "schema, checkpoint revision, readout and preprocessing must be explicit"
            raise ValueError(msg)

    def encode(self, batch: PanelBatch) -> Embeddings:
        """Return one vector per query row, preserving its observation ID."""
        if batch.feature_names != self.feature_names:
            msg = "query feature order differs from the fitted schema"
            raise ValueError(msg)
        if self.context is not None:
            if self.context.available_at > batch.as_of:
                msg = "context or its labels became available after the query cutoff"
                raise ValueError(msg)
            if set(self.context.row_ids).intersection(batch.row_ids):
                msg = "query observations overlap labeled context; use held-out observations"
                raise ValueError(msg)
        tokens = self.extract(batch)
        if tokens.values.shape[0] != len(batch.row_ids):
            msg = "extractor changed the number of query rows"
            raise ValueError(msg)
        vectors = np.array(self.pooling(tokens), dtype=np.float64, copy=True)
        if vectors.ndim != 2 or vectors.shape[0] != len(batch.row_ids) or not vectors.shape[1]:
            msg = "pooling must return a nonempty (query rows, dimensions) array"
            raise ValueError(msg)
        if not np.isfinite(vectors).all():
            msg = "pooled embeddings must be finite"
            raise ValueError(msg)
        if self.normalize:
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            if np.any(norms == 0) or not np.isfinite(norms).all():
                msg = "cannot normalize a zero vector or an overflowing norm"
                raise ValueError(msg)
            vectors /= norms
        return Embeddings(
            frozen_array(vectors),
            batch.row_ids,
            batch.as_of,
            batch.feature_names,
            Provenance(
                self.model,
                self.checkpoint,
                self.readout,
                self.preprocessing,
                self.context,
                self.pooling.name,
                self.normalize,
            ),
        )


class NativeEmbeddingModel(Protocol):
    """Already-fitted TabPFN surface; fitting remains a separate operation."""

    def get_embeddings(
        self,
        features: FloatArray,
        /,
        *,
        data_source: Literal["test"] = "test",
    ) -> FloatArray:
        """Return (ensemble members, query rows, channels)."""
        ...


@dataclass(frozen=True)
class NativeReadout:
    """Convert the verified TabPFN ensemble layout without mixing rows."""

    backend: NativeEmbeddingModel

    def __call__(self, batch: PanelBatch) -> Tokens:
        """Extract query representations, never labeled training representations."""
        values = np.asarray(
            self.backend.get_embeddings(batch.values, data_source="test"), dtype=np.float64
        )
        # TabPFN's squeeze() removes the sample axis for a one-row query.
        if values.ndim == 2 and len(batch.row_ids) == 1:
            values = values[:, None, :]
        if values.ndim != 3 or values.shape[1] != len(batch.row_ids):
            msg = "native embeddings must have (ensemble, query rows, channels) shape"
            raise ValueError(msg)
        return Tokens(values.transpose(1, 0, 2))


def from_fitted(  # noqa: PLR0913 -- explicit measurement provenance is intentional.
    name: str,
    backend: NativeEmbeddingModel,
    *,
    feature_names: tuple[str, ...],
    checkpoint: str,
    preprocessing: str,
    context: Context,
    pooling: Pooling | None = None,
) -> TabularEncoder:
    """Wrap a fitted TabPFN 3.5 model without changing its context.

    Other models require an explicit ``TabularEncoder(extract=...)`` readout.
    Prediction vectors are never silently substituted for latent states.
    """
    if model_spec(name).extraction != "native":
        msg = f"{name} needs an explicit readout; its public API has no verified row embeddings"
        raise NotImplementedError(msg)
    return TabularEncoder(
        model=name,
        extract=NativeReadout(backend),
        feature_names=feature_names,
        checkpoint=checkpoint,
        readout="get_embeddings:test",
        preprocessing=preprocessing,
        context=context,
        pooling=ConcatenatePooling() if pooling is None else pooling,
    )
