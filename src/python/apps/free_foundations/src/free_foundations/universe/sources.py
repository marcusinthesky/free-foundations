"""Resumable public-data acquisition with compressed SEC snapshots."""

from __future__ import annotations

import gzip
import json
import logging
import shutil
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from functools import partial
from pathlib import Path
from typing import Any, cast

import pandas as pd
import yfinance as yf
from edgar.httprequests import download_json
from httpx import HTTPStatusError

from free_foundations.data import FrenchReader, write_json

LOGGER = logging.getLogger(__name__)


def screen(cache: Path, limit: int) -> list[dict[str, Any]]:
    """Freeze paginated current US exchange listings ranked by current capitalization."""
    query = yf.EquityQuery(
        "and",
        [
            yf.EquityQuery("eq", ["region", "us"]),
            yf.EquityQuery("is-in", ["exchange", "NYQ", "NMS", "NGM", "NCM", "ASE"]),
        ],
    )
    quotes: list[dict[str, Any]] = []
    for offset in range(0, limit, 250):
        path = cache / f"screen-{offset}.json"
        if not path.exists():
            response = yf.screen(
                query,
                offset=offset,
                size=min(250, limit - offset),
                sortField="intradaymarketcap",
                sortAsc=False,
            )
            write_json(path, {"retrieved_at": datetime.now(UTC).isoformat(), "response": response})
        page = json.loads(path.read_text())["response"]["quotes"]
        quotes.extend(page)
        LOGGER.info("Screen: %s candidates", len(quotes))
        if len(page) < min(250, limit - offset):
            break
    return quotes[:limit]


def company_facts(cache: Path, cik: int, *, cached_only: bool = False) -> dict[str, Any]:
    """Reuse the pilot cache; download at most three concurrently with per-call pacing."""
    path = cache / "facts" / f"{cik:010}.json.gz"
    if path.exists():
        with gzip.open(path, "rt") as stream:
            return json.load(stream)
    if cached_only:
        message = f"Missing frozen SEC snapshot: {path}. Restore the universe data with DVC."
        raise FileNotFoundError(message)
    if shutil.disk_usage(cache).free < 500_000_000:
        message = "Less than 500 MB disk space remains; cached progress is preserved."
        raise OSError(message)
    previous = Path("research/pilot/cache/facts") / f"{cik:010}.json"
    if previous.exists():
        payload = json.loads(previous.read_text())
    else:
        time.sleep(0.4)
        try:
            payload = download_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json")
        except HTTPStatusError as error:
            if error.response.status_code != 404:
                raise
            payload = {"cik": cik, "source_status": 404}
    temporary = path.with_suffix(".tmp")
    with gzip.open(temporary, "wt") as stream:
        json.dump(payload, stream, separators=(",", ":"))
    temporary.replace(path)
    return payload


def issuers(cache: Path, size: int, candidates: int) -> pd.DataFrame:
    """Retain one share class per CIK and audit exclusions without balancing on future data."""
    (cache / "facts").mkdir(exist_ok=True)
    mapping_path = cache / "sec-tickers.json"
    if not mapping_path.exists():
        write_json(mapping_path, download_json("https://www.sec.gov/files/company_tickers.json"))
    mapping = {row["ticker"]: row for row in json.loads(mapping_path.read_text()).values()}
    selected: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    pending: list[dict[str, Any]] = []
    seen = set()
    for rank, quote in enumerate(screen(cache, candidates), 1):
        ticker = quote["symbol"]
        issuer = mapping.get(ticker)
        if issuer is None or int(issuer["cik_str"]) in seen:
            excluded.append({"ticker": ticker, "reason": "unmatched SEC ticker or duplicate CIK"})
            continue
        cik = int(issuer["cik_str"])
        seen.add(cik)
        pending.append(
            {
                "ticker": ticker,
                "cik": cik,
                "rank": rank,
                "market_cap": quote.get("marketCap"),
                "name": issuer["title"],
            }
        )
    with ThreadPoolExecutor(max_workers=3) as workers:
        for start in range(0, len(pending), 25):
            batch = pending[start : start + 25]
            payloads = workers.map(
                partial(company_facts, cache), (int(row["cik"]) for row in batch)
            )
            for issuer, payload in zip(batch, payloads, strict=True):
                assets = (
                    payload.get("facts", {})
                    .get("us-gaap", {})
                    .get("Assets", {})
                    .get("units", {})
                    .get("USD", [])
                )
                if any(row.get("form") in {"10-K", "10-K/A"} for row in assets):
                    selected.append(issuer)
                else:
                    excluded.append(
                        {
                            "ticker": issuer["ticker"],
                            "reason": "companyfacts unavailable (404)"
                            if payload.get("source_status") == 404
                            else "no USD US-GAAP annual 10-K assets",
                        }
                    )
            pd.DataFrame(selected[:size]).to_csv(cache.parent / "universe.csv", index=False)
            write_json(cache.parent / "universe-exclusions.json", excluded)
            LOGGER.info("SEC: %s eligible issuers / %s assessed", len(selected), start + len(batch))
            if len(selected) >= size:
                break
    if len(selected) < size:
        message = f"Only {len(selected)} eligible issuers; increase --candidates."
        raise ValueError(message)
    return pd.DataFrame(selected[:size])


def prices(cache: Path, universe: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Save unbalanced price/action histories without backfilling prelisting observations."""
    tickers = universe["ticker"].tolist()
    frames = []
    failures: list[str] = []
    for offset in range(0, len(tickers), 50):
        batch = tickers[offset : offset + 50]
        path = cache / f"market-{offset}-{start}-{end}.parquet"
        if path.exists():
            raw = pd.read_parquet(path)
        else:
            raw = yf.download(
                batch,
                start=start,
                end=end,
                auto_adjust=False,
                actions=True,
                progress=False,
                threads=3,
                timeout=30,
            )
            if raw.empty:
                message = f"Empty Yahoo batch at {offset}; rerun to resume."
                raise RuntimeError(message)
            raw.to_parquet(path)
        adjusted = pd.DataFrame(raw["Adj Close"]).reindex(columns=batch)
        failures.extend(adjusted.columns[adjusted.notna().sum() == 0].tolist())
        frames.append(adjusted)
        LOGGER.info("Prices: %s / %s issuers", min(offset + 50, len(tickers)), len(tickers))
    result = pd.concat(frames, axis=1)
    result.to_parquet(cache / "prices.parquet")
    write_json(cache.parent / "price-failures.json", failures)
    return result


def factors(cache: Path, start: str, end: str) -> pd.DataFrame:
    """Extend FF5 and momentum alongside returns, preserving the provider descriptions."""
    path = cache / "factors.parquet"
    if path.exists():
        return pd.read_parquet(path)
    frames = []
    for name in ("F-F_Research_Data_5_Factors_2x3_daily", "F-F_Momentum_Factor_daily"):
        reader = FrenchReader(name, start=start, end=end)
        dataset = cast("dict[int | str, Any]", reader.read())
        frame = pd.DataFrame(dataset[0])
        if isinstance(frame.index, pd.PeriodIndex):
            frame.index = frame.index.to_timestamp()
        frame.columns = frame.columns.str.strip()
        frames.append(frame / 100)
        (cache / f"{name}.txt").write_text(str(dataset["DESCR"]))
    result = pd.concat(frames, axis=1).dropna()
    result = result.loc[(result.index >= start) & (result.index < end)]
    result.to_parquet(path)
    return result
