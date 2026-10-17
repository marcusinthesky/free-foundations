"""Small, model-independent contracts for row-aligned representations."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

type FloatArray = NDArray[np.float64]
type BoolArray = NDArray[np.bool_]


def frozen_array(values: FloatArray) -> FloatArray:
    """Own the data so a caller cannot mutate a recorded measurement."""
    result = np.array(values, dtype=np.float64, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True)
class PanelBatch:
    """One point-in-time numeric table; IDs identify firm-observations, not firms.

    The caller supplies values available by ``as_of``, with stable feature order.
    NaN denotes missing data. There is no implicit imputation or scaling.
    """

    values: FloatArray
    row_ids: tuple[str, ...]
    feature_names: tuple[str, ...]
    as_of: datetime

    def __post_init__(self) -> None:
        """Reject ambiguous alignment and unknown information cutoffs."""
        values = frozen_array(self.values)
        if values.ndim != 2 or values.shape != (len(self.row_ids), len(self.feature_names)):
            msg = "values must have shape (len(row_ids), len(feature_names))"
            raise ValueError(msg)
        if not self.row_ids or not self.feature_names:
            msg = "a panel batch needs at least one row and one feature"
            raise ValueError(msg)
        if len(set(self.row_ids)) != len(self.row_ids):
            msg = "row_ids must uniquely identify firm-observations"
            raise ValueError(msg)
        if len(set(self.feature_names)) != len(self.feature_names):
            msg = "feature_names must be unique and ordered"
            raise ValueError(msg)
        if self.as_of.utcoffset() is None or np.isinf(values).any():
            msg = "as_of must be timezone-aware and features must not contain infinity"
            raise ValueError(msg)
        object.__setattr__(self, "values", values)


@dataclass(frozen=True)
class Tokens:
    """Canonical shape: (query rows, tokens or ensemble members, channels).

    Masks select valid tokens. Adapters must remove context rows and padding,
    and name the chosen layer/readout; this contract never guesses model axes.
    """

    values: FloatArray
    mask: BoolArray | None = None

    def __post_init__(self) -> None:
        """Validate shape and valid-token finiteness before pooling."""
        values = frozen_array(self.values)
        if values.ndim != 3 or 0 in values.shape:
            msg = "tokens must have nonempty (rows, tokens, channels) axes"
            raise ValueError(msg)
        mask = (
            np.ones(values.shape[:2], dtype=np.bool_)
            if self.mask is None
            else np.array(
                self.mask,
                dtype=np.bool_,
                copy=True,
            )
        )
        if mask.shape != values.shape[:2] or not mask.any(axis=1).all():
            msg = "mask must match (rows, tokens), with at least one valid token per row"
            raise ValueError(msg)
        if not np.isfinite(values[mask]).all():
            msg = "valid token values must be finite"
            raise ValueError(msg)
        mask.setflags(write=False)
        object.__setattr__(self, "values", values)
        object.__setattr__(self, "mask", mask)


class Pooling(Protocol):
    """Reduce tokens to one vector per row without changing row order."""

    @property
    def name(self) -> str:
        """Stable description recorded with each result."""
        ...

    def __call__(self, tokens: Tokens) -> FloatArray:
        """Return a finite (rows, dimensions) array."""
        ...


type Extractor = Callable[[PanelBatch], Tokens]


@dataclass(frozen=True)
class Context:
    """Identity and information cutoff of a fixed, already-fitted support set.

    ``available_at`` includes label availability, not only filing availability.
    The identifier should address the data, labels and fitted preprocessing.
    """

    identifier: str
    available_at: datetime
    row_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        """Require a reproducible context and a comparable timestamp."""
        if (
            not self.identifier
            or self.available_at.utcoffset() is None
            or not self.row_ids
            or len(set(self.row_ids)) != len(self.row_ids)
        ):
            msg = "context needs an identifier and timezone-aware availability"
            raise ValueError(msg)


@dataclass(frozen=True)
class Provenance:
    """Choices that define a representation's geometry."""

    model: str
    checkpoint: str
    readout: str
    preprocessing: str
    context: Context | None
    pooling: str
    normalized: bool


@dataclass(frozen=True)
class Embeddings:
    """Row-aligned values and the recipe needed to interpret their distances."""

    values: FloatArray
    row_ids: tuple[str, ...]
    as_of: datetime
    feature_names: tuple[str, ...]
    provenance: Provenance


class Encoder(Protocol):
    """Sentence-transformers-like entry point with explicit panel provenance."""

    def encode(self, batch: PanelBatch) -> Embeddings:
        """Encode query rows against a fixed model, schema and context."""
        ...
