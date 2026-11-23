"""Reusable finite tensor and panel fixtures without model downloads."""

from datetime import UTC, datetime

import numpy as np
import pandas as pd
from hypothesis import strategies as st
from hypothesis.extra.numpy import arrays
from hypothesis.strategies import DrawFn, SearchStrategy

from free_foundations.encoders.contracts import FloatArray, PanelBatch, Tokens
from free_foundations.study.spec import StudySpec

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


def compact_spec(start: str, end: str, **changes: object) -> StudySpec:
    """A small valid study: the December before ``start`` forms one four-quarter cohort."""
    formation = pd.Timestamp(start).year - 1
    settings: dict[str, object] = {
        "archive_start": start,
        "archive_end": end,
        "feature_start": start,
        "panel_start": start,
        "window_quarters": 4,
        "formation_years": (formation,),
        "primary_formation": formation,
        "min_beta_quarters": 3,
    }
    return StudySpec(**(settings | changes))  # type: ignore[arg-type]
