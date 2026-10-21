"""Shared filing records, JSON metadata, and the HTTPS factor-data reader."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, override

import pandas as pd
from pandas_datareader.famafrench import FamaFrenchReader

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path


class FrenchReader(FamaFrenchReader):
    """Use the provider's HTTPS endpoint without mutating library globals."""

    @property
    @override
    def url(self) -> str:
        """Return the HTTPS download URL."""
        return str(super().url).replace("http:", "https:", 1)


def write_json(path: Path, value: object) -> None:
    """Write readable metadata, rejecting nonstandard numeric values."""
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def fact_rows(payload: Mapping[str, Any]) -> pd.DataFrame:
    """Keep USD GAAP facts with original accession, period and filing dates."""
    records = []
    for tag, concept in payload["facts"].get("us-gaap", {}).items():
        records.extend(
            {"tag": tag, **row}
            for row in concept["units"].get("USD", [])
            if row.get("form") in {"10-K", "10-K/A"}
        )
    frame = pd.DataFrame(records).reindex(
        columns=["tag", "val", "accn", "form", "start", "end", "filed"]
    )
    for column in ("start", "end", "filed"):
        frame[column] = pd.to_datetime(frame[column])
    return frame
