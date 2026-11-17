"""Reusable finite tensor and panel fixtures without model downloads."""

from datetime import UTC, datetime

import numpy as np
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
from hypothesis.strategies import DrawFn, SearchStrategy

from free_foundations.contracts import FloatArray, PanelBatch, Tokens

CUTOFF = datetime(2025, 1, 1, tzinfo=UTC)


@st.composite
def token_arrays(draw: DrawFn) -> FloatArray:
    """Exercise independent row, token and channel axes, including singletons."""
    shape = tuple(draw(st.integers(1, 5)) for _ in range(3))
    return draw(
        arrays(
            np.float64, shape, elements=st.floats(-100, 100, allow_nan=False, allow_infinity=False)
        )
    )


def tokens() -> SearchStrategy[Tokens]:
    """Validated token batches for pooling and encoder properties."""
    return token_arrays().map(Tokens)


def panel(rows: int, *, cutoff: datetime = CUTOFF) -> PanelBatch:
    """Stable observation IDs and schema for contract tests."""
    return PanelBatch(
        np.ones((rows, 2)),
        tuple(f"firm-{i}:2024-Q3" for i in range(rows)),
        ("assets", "debt"),
        cutoff,
    )
