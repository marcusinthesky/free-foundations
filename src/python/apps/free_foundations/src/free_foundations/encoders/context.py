"""Prepared support/query arrays and their observation identities."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from free_foundations.encoders.contracts import (
    Context,
    PanelBatch,
)

if TYPE_CHECKING:
    from free_foundations.encoders.contracts import FloatArray


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
