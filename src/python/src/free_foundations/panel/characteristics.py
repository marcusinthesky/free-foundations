"""Full annual disclosures and strict Fernández characteristics from cached filings."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from free_foundations.fernandez.characteristics import CHARACTERISTICS, snapshot
from free_foundations.filings import broad_facts
from free_foundations.universe.sources import company_facts

LOGGER = logging.getLogger(__name__)
SOURCE = Path("research/universe/cache")
ROOT = Path("research/panel")
MULTICLASS = {"GOOG", "GOOGL", "BRK-B", "BRK-A", "FOX", "FOXA", "NWS", "NWSA"}


def markets() -> pd.DataFrame:
    """Reverse all splits through retrieval, including splits after the return sample."""
    cached = sorted(SOURCE.glob("market-*.parquet"))
    raw = pd.concat([pd.read_parquet(path) for path in cached], axis=1)
    tail = ROOT / "cache/market-tail.parquet"
    if not tail.exists():
        message = f"Missing frozen Yahoo snapshot: {tail}. Restore market_metadata with DVC."
        raise FileNotFoundError(message)
    return pd.concat([raw, pd.read_parquet(tail)]).sort_index()


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Save wide inputs plus each selected fact's original filing and accession."""
    cache = ROOT / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    if (cache / "four.parquet").exists():
        return pd.read_parquet(cache / "four.parquet"), pd.read_parquet(cache / "broad.parquet")
    market = markets()
    universe = pd.read_csv(SOURCE.parent / "universe.csv")
    pieces = cache / "characteristics"
    pieces.mkdir(exist_ok=True)
    for number, issuer in enumerate(universe.to_dict("records"), 1):
        ticker = issuer["ticker"]
        path = pieces / f"{ticker}.parquet"
        if path.exists():
            continue
        facts = broad_facts(company_facts(SOURCE, issuer["cik"], cached_only=True))
        payload = company_facts(SOURCE, issuer["cik"], cached_only=True)
        shares = payload["facts"].get("dei", {}).get("EntityCommonStockSharesOutstanding", {})
        shares = pd.DataFrame(shares.get("units", {}).get("shares", []))
        if not shares.empty:
            shares["tag"] = "EntityCommonStockSharesOutstanding"
            shares["concept"] = "dei:EntityCommonStockSharesOutstanding|shares|instant"
            shares["kind"] = "instant"
            for col in ("end", "filed"):
                shares[col] = pd.to_datetime(shares[col])
            shares = shares.loc[shares["form"].isin(["10-K", "10-K/A"])]
            facts = pd.concat([facts, shares], ignore_index=True)
        prices = pd.DataFrame(market.xs(ticker, level=1, axis=1)).dropna(subset=["Close"]).copy()
        splits = prices["Stock Splits"].fillna(0).replace(0, 1)
        prices["historical_close"] = (
            prices["Close"] * splits.iloc[::-1].cumprod().iloc[::-1] / splits
        )
        prices["trailing_dividends"] = prices["Dividends"].rolling("365D").sum()
        rows: list[dict[str, Any]] = []
        audits: list[pd.DataFrame] = []
        for year in range(2009, 2025):
            cutoff = pd.Timestamp(year, 12, 31)
            known = facts.loc[
                (facts["filed"] <= cutoff)
                & facts["end"].between(cutoff - pd.Timedelta(days=550), cutoff)
            ].copy()
            selected = known.sort_values(["end", "filed", "accn"]).drop_duplicates(
                "concept", keep="last"
            )
            selected = selected.assign(year=year, ticker=ticker)
            audits.append(selected)
            strict = (
                {}
                if ticker in MULTICLASS or prices.empty
                else snapshot(known.loc[known["kind"].eq("instant")], prices)
            )
            rows.append(
                {
                    "year": year,
                    "ticker": ticker,
                    **strict,
                    **dict(zip(selected["concept"], selected["val"], strict=True)),
                }
            )
        pd.DataFrame(rows).to_parquet(path, index=False)
        pd.concat(audits, ignore_index=True).to_parquet(
            pieces / f"{ticker}.audit.parquet", index=False
        )
        if number % 50 == 0:
            LOGGER.info("Full characteristics: %s / %s", number, len(universe))
    return assemble(universe)


def assemble(universe: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Assemble issuer snapshots into one allocation, avoiding a wide-frame concat spike."""
    cache = ROOT / "cache"
    paths = [cache / "characteristics" / f"{ticker}.parquet" for ticker in universe["ticker"]]
    concepts = sorted(
        {
            name
            for path in paths
            for name in pq.read_schema(path).names
            if name.startswith("us-gaap:")
        }
    )
    positions = {name: number for number, name in enumerate(concepts)}
    values = np.full((len(paths) * 16, len(concepts)), np.nan)
    indices: list[tuple[int, str]] = []
    audits = []
    for number, path in enumerate(paths):
        frame = pd.read_parquet(path, use_threads=False)
        columns = [name for name in frame.columns if str(name) in positions]
        values[number * 16 : (number + 1) * 16, [positions[str(name)] for name in columns]] = frame[
            columns
        ].to_numpy(dtype=float)
        indices.extend(zip(frame["year"], frame["ticker"], strict=True))
        audits.append(frame[[name for name in frame if str(name) not in positions]])
    index = pd.MultiIndex.from_tuples(indices, names=["year", "ticker"])
    broad = pd.DataFrame(values, index=index, columns=concepts).sort_index()
    audit = pd.concat(audits, ignore_index=True).set_index(["year", "ticker"]).sort_index()
    audit.to_parquet(cache / "characteristic-audit.parquet")
    four = audit[list(CHARACTERISTICS)].astype(float).replace([np.inf, -np.inf], np.nan)
    four.to_parquet(cache / "four.parquet")
    broad.to_parquet(cache / "broad.parquet")
    four.notna().groupby("year").sum().to_csv(ROOT / "characteristic-coverage.csv")
    return four, broad


def audit_disclosures() -> dict[str, int]:
    """Validate filing timing and agreement between wide snapshots and their audit trail."""
    pieces = ROOT / "cache/characteristics"
    wide_paths = [p for p in pieces.glob("*.parquet") if not p.name.endswith(".audit.parquet")]
    if not wide_paths:
        message = "No frozen disclosure snapshots to audit. Restore the preparation inputs."
        raise FileNotFoundError(message)
    for wide_path in wide_paths:
        if not wide_path.with_name(wide_path.stem + ".audit.parquet").is_file():
            message = f"Missing filing audit record: {wide_path}"
            raise ValueError(message)
    selected_facts = 0
    populated_snapshots = 0
    issuers = 0
    for path in sorted((ROOT / "cache/characteristics").glob("*.audit.parquet")):
        frame = pd.read_parquet(
            path,
            columns=["year", "filed", "end", "concept", "ticker", "val"],
            use_threads=False,
        )
        cutoff = pd.to_datetime(frame["year"].astype(str) + "-12-31")
        valid = (
            (frame["filed"] <= cutoff)
            & (frame["end"] <= cutoff)
            & ((cutoff - frame["end"]).dt.days <= 550)
        )
        if not valid.all() or frame.duplicated(["year", "ticker", "concept"]).any():
            message = f"Invalid point-in-time fact selection: {path}"
            raise ValueError(message)
        wide = pd.read_parquet(path.with_name(path.name.replace(".audit", "")), use_threads=False)
        concepts = [name for name in wide if str(name).startswith(("us-gaap:", "dei:"))]
        keys = ["year", "ticker", "concept"]
        if wide.duplicated(["year", "ticker"]).any():
            message = f"Duplicate wide snapshots: {path}"
            raise ValueError(message)
        expected = wide.melt(
            id_vars=["year", "ticker"],
            value_vars=concepts,
            var_name="concept",
            value_name="snapshot",
        )
        # Wide tables have structural missing cells for concepts absent in a year.
        # Match every selected audit record (including selected missing values), and
        # reject populated wide cells without an audit key.
        actual = frame[[*keys, "val"]]
        joined = expected.merge(actual, on=keys, how="outer", validate="one_to_one", indicator=True)
        unmatched = (joined["_merge"].eq("left_only") & joined["snapshot"].notna()) | joined[
            "_merge"
        ].eq("right_only")
        both = joined["_merge"].eq("both")
        values_equal = (joined["snapshot"].isna() & joined["val"].isna()) | joined["snapshot"].eq(
            joined["val"]
        )
        if unmatched.any() or not values_equal[both].all():
            message = f"Wide characteristics and filing audit disagree in keys or values: {path}"
            raise ValueError(message)
        issuers += 1
        selected_facts += len(frame)
        populated_snapshots += int(frame["year"].nunique())
    return {
        "issuers": issuers,
        "annual_states": issuers * 16,
        "populated_snapshots": populated_snapshots,
        "candidate_us_gaap_concepts": len(pq.read_schema(ROOT / "cache/broad.parquet").names) - 2,
        "selected_facts": selected_facts,
        "future_filings": 0,
        "future_periods": 0,
        "duplicate_concepts_per_snapshot": 0,
        "maximum_age_days": 550,
    }
