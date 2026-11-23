"""Bind captured native readouts to the ordered query cohort."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from free_foundations.encoders.contracts import PanelBatch, Tokens
from free_foundations.encoders.encoding import TabularEncoder
from free_foundations.encoders.pooling import ConcatenatePooling

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray


from free_foundations.encoders.context import Prepared, provenance_context, query_batch


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
    return result.values
