"""Cached Yahoo, French, and SEC inputs; preserve the original filing dates."""

from __future__ import annotations

import json
import os
import time
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, cast, override

import pandas as pd
import yfinance as yf
from edgar import set_identity
from edgar.httprequests import download_json
from pandas_datareader.famafrench import FamaFrenchReader

if TYPE_CHECKING:
    from collections.abc import Mapping
    from pathlib import Path

START = "2012-01-01"
END = "2026-01-01"


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


def market_inputs(cache: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Cache a current US equity screen, adjusted daily closes and daily factors."""
    cache.mkdir(parents=True, exist_ok=True)
    screen = cache / "yahoo-screen.json"
    if not screen.exists():
        result = yf.screen(
            yf.EquityQuery(
                "and",
                [
                    yf.EquityQuery("eq", ["region", "us"]),
                    yf.EquityQuery("is-in", ["exchange", "NYQ", "NMS", "NGM", "NCM", "ASE"]),
                ],
            ),
            size=150,
            sortField="intradaymarketcap",
            sortAsc=False,
        )
        write_json(screen, {"retrieved_at": datetime.now(UTC).isoformat(), "response": result})
    quotes = json.loads(screen.read_text())["response"]["quotes"]
    prices_path = cache / "prices.parquet"
    if not prices_path.exists():
        prices = yf.download(
            [q["symbol"] for q in quotes],
            start=START,
            end=END,
            auto_adjust=True,
            progress=False,
            threads=4,
        )["Close"]
        prices.to_parquet(prices_path)
    factors_path = cache / "factors.parquet"
    if not factors_path.exists():
        tables = []
        for name in ("F-F_Research_Data_5_Factors_2x3_daily", "F-F_Momentum_Factor_daily"):
            reader = FrenchReader(name, start=START, end=END)
            dataset = cast("dict[int | str, Any]", reader.read())
            frame = pd.DataFrame(dataset[0])
            if isinstance(frame.index, pd.PeriodIndex):
                frame.index = frame.index.to_timestamp()
            frame.columns = frame.columns.str.strip()
            tables.append(frame / 100)
            (cache / f"{name}.txt").write_text(str(dataset["DESCR"]))
        pd.concat(tables, axis=1).dropna().to_parquet(factors_path)
    prices = pd.read_parquet(prices_path)
    # Batch endpoints can fail transiently for otherwise valid firms. Retry only gaps.
    for ticker in prices.columns[prices.isna().all()]:
        replacement = yf.download(
            ticker,
            start=START,
            end=END,
            auto_adjust=True,
            progress=False,
            threads=False,
        )["Close"]
        if not replacement.empty:
            prices[ticker] = replacement.iloc[:, 0].reindex(prices.index)
    prices.to_parquet(prices_path)
    write_json(
        cache.parent / "price-coverage.json",
        {ticker: int(prices[ticker].notna().sum()) for ticker in prices.columns},
    )
    return prices, pd.read_parquet(factors_path)


def sec_inputs(cache: Path) -> pd.DataFrame:
    """Select the first 100 distinct SEC issuers with US-GAAP assets, by Yahoo cap."""
    identity = os.environ.get("EDGAR_IDENTITY")
    if not identity:
        message = "Set EDGAR_IDENTITY to your name and email before requesting SEC data."
        raise RuntimeError(message)
    set_identity(identity)
    mapping_path = cache / "sec-tickers.json"
    if not mapping_path.exists():
        write_json(mapping_path, download_json("https://www.sec.gov/files/company_tickers.json"))
    mapping = {r["ticker"]: r for r in json.loads(mapping_path.read_text()).values()}
    quotes = json.loads((cache / "yahoo-screen.json").read_text())["response"]["quotes"]
    selected: list[dict[str, Any]] = []
    exclusions: list[dict[str, str]] = []
    seen: set[int] = set()
    facts_dir = cache / "facts"
    facts_dir.mkdir(exist_ok=True)
    for rank, quote in enumerate(quotes, 1):
        ticker = quote["symbol"]
        issuer = mapping.get(ticker)
        if issuer is None or issuer["cik_str"] in seen:
            exclusions.append(
                {"ticker": ticker, "reason": "no SEC ticker match or duplicate issuer"}
            )
            continue
        cik = int(issuer["cik_str"])
        path = facts_dir / f"{cik:010}.json"
        if not path.exists():
            time.sleep(0.25)
            write_json(
                path, download_json(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json")
            )
        facts = json.loads(path.read_text())
        assets = facts.get("facts", {}).get("us-gaap", {}).get("Assets", {})
        annual_assets = assets.get("units", {}).get("USD", [])
        if not any(row.get("form") in {"10-K", "10-K/A"} for row in annual_assets):
            exclusions.append({"ticker": ticker, "reason": "no USD US-GAAP annual 10-K assets"})
            continue
        seen.add(cik)
        selected.append(
            {
                "ticker": ticker,
                "cik": cik,
                "rank": rank,
                "market_cap": quote.get("marketCap"),
                "name": issuer["title"],
            }
        )
        if len(selected) == 100:
            break
    universe = pd.DataFrame(selected)
    universe.to_csv(cache.parent / "universe.csv", index=False)
    write_json(cache.parent / "universe-exclusions.json", exclusions)
    if len(universe) != 100:
        message = f"Only {len(universe)} eligible issuers in the cached Yahoo screen."
        raise ValueError(message)
    return universe


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
