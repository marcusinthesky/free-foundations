"""Broad annual standard-taxonomy disclosures with explicit units and periods."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from pathlib import Path

LOGGER = logging.getLogger(__name__)
UNITS = {"USD", "shares", "USD/shares", "pure"}


def broad_facts(payload: dict[str, Any]) -> pd.DataFrame:
    """Preserve concept, unit, and stock/annual-flow distinctions; discard other durations."""
    records = []
    for tag, concept in payload["facts"].get("us-gaap", {}).items():
        for unit, observations in concept["units"].items():
            if unit in UNITS:
                records.extend(
                    {"tag": tag, "unit": unit, **row}
                    for row in observations
                    if row.get("form") in {"10-K", "10-K/A"}
                )
    frame = pd.DataFrame(records).reindex(
        columns=["tag", "unit", "val", "start", "end", "filed", "accn"]
    )
    for name in ("start", "end", "filed"):
        frame[name] = pd.to_datetime(frame[name])
    days = (frame["end"] - frame["start"]).dt.days
    frame = frame.loc[frame["start"].isna() | days.between(300, 380)].copy()
    frame["kind"] = np.where(frame["start"].isna(), "instant", "annual")
    frame["concept"] = "us-gaap:" + frame["tag"] + "|" + frame["unit"] + "|" + frame["kind"]
    return frame


def build_disclosures(source: Path, output: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cache broad snapshots; never backfill a snapshot with a later filing."""
    path = output / "broad.parquet"
    if path.exists():
        return pd.read_parquet(path), pd.read_parquet(output / "ages.parquet")
    universe = pd.read_csv(source.parent / "universe.csv")
    records: list[dict[str, Any]] = []
    audits: list[pd.DataFrame] = []
    for number, issuer in enumerate(universe.to_dict("records"), 1):
        facts = broad_facts(
            json.loads((source / "facts" / f"{issuer['cik']:010}.json").read_text())
        )
        for year in range(2012, 2025):
            cutoff = pd.Timestamp(year=year, month=12, day=31)
            available = facts.loc[
                (facts["filed"] <= cutoff)
                & (facts["end"] <= cutoff)
                & (facts["end"] >= cutoff - pd.Timedelta(days=550))
            ]
            selected = (
                available.sort_values(["end", "filed", "accn"])
                .drop_duplicates("concept", keep="last")
                .copy()
            )
            selected["ticker"], selected["year"] = issuer["ticker"], year
            selected["age"] = (cutoff - selected["end"]).dt.days
            audits.append(selected)
            records.append(
                {
                    "year": year,
                    "ticker": issuer["ticker"],
                    **dict(zip(selected["concept"], selected["val"], strict=True)),
                }
            )
        if number % 10 == 0:
            LOGGER.info("Broad facts: %s/100 issuers", number)
    panel = pd.DataFrame(records).set_index(["year", "ticker"]).sort_index()
    audit = pd.concat(audits, ignore_index=True)
    ages = audit.pivot_table(index=["year", "ticker"], columns="concept", values="age")
    output.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(path)
    ages.to_parquet(output / "ages.parquet")
    audit.to_parquet(output / "broad-audit.parquet", index=False)
    cutoff = pd.to_datetime(audit["year"].astype(str) + "-12-31")
    write_json(
        output.parent / "disclosure-audit.json",
        {
            "states": len(panel),
            "candidate_concepts": len(panel.columns),
            "selected_facts": len(audit),
            "future_filings": int((audit["filed"] > cutoff).sum()),
            "future_periods": int((audit["end"] > cutoff).sum()),
            "units": sorted(UNITS),
            "scope": "entity-wide standard US-GAAP, annual 10-K only",
        },
    )
    return panel, ages


def select_schema(panel: pd.DataFrame, year: int, limit: int = 200) -> tuple[str, ...]:
    """Select by support-period coverage only; break ties deterministically by concept."""
    support = panel.loc[year - 3 : year - 2]
    coverage = support.notna().mean().sort_index().sort_values(ascending=False, kind="stable")
    return tuple(coverage.loc[coverage >= 0.2].head(limit).index)


def input_views(core: pd.DataFrame, broad: pd.DataFrame, year: int) -> dict[str, pd.DataFrame]:
    """Return original ratios, broad reported values, and broad normalized metrics."""
    columns = select_schema(broad, year)
    raw = broad[list(columns)].copy()
    # Preserve signed reported levels; only the numerical conditioning is transformed.
    raw = pd.DataFrame(
        np.sign(raw.to_numpy()) * np.log1p(raw.abs().to_numpy()),
        index=raw.index,
        columns=raw.columns,
    )
    metrics = broad[list(columns[:100])].copy()
    assets = pd.Series(np.exp(core["log_assets"].to_numpy()), index=core.index).reindex(
        metrics.index
    )
    for column in columns[:100]:
        if "|USD|" in column:
            metrics[column] = metrics[column] / assets
        elif "|shares|" in column:
            metrics[column] = np.log1p(metrics[column].clip(lower=0))
    previous = metrics.copy()
    previous.index = pd.MultiIndex.from_tuples(
        [(date + 1, ticker) for date, ticker in metrics.index], names=metrics.index.names
    )
    changes = (metrics - previous.reindex(metrics.index)).add_suffix("|change_1y")
    metrics = pd.concat([metrics, changes, core[["log_assets"]].reindex(metrics.index)], axis=1)
    return {"core19": core, "broad": raw, "metrics": metrics}
