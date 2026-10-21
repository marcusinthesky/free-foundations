"""Acquire a larger unbalanced public-data universe before fitting any return models."""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from edgar import set_identity

from free_foundations.data import write_json
from free_foundations.universe.coverage import coverage, snapshots
from free_foundations.universe.report import write_report
from free_foundations.universe.sources import factors, issuers, prices


@dataclass(frozen=True)
class Acquisition:
    """The universe's acquisition configuration; a different one needs its own output."""

    size: int = 1000
    candidates: int = 2000
    start: str = "2008-01-01"
    end: str = "2026-01-01"
    first_snapshot: int = 2009
    last_snapshot: int = 2024
    output: Path = Path("research/universe")


def main(args: Acquisition) -> None:
    """Cache immutable inputs, then report achievable annual sample sizes and history."""
    identity = os.environ.get("EDGAR_IDENTITY")
    if not identity:
        message = "Set EDGAR_IDENTITY to your name and email."
        raise ValueError(message)
    set_identity(identity)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    cache = args.output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    config = {
        "size": args.size,
        "candidates": args.candidates,
        "start": args.start,
        "end_exclusive": args.end,
        "first_snapshot": args.first_snapshot,
        "last_snapshot": args.last_snapshot,
    }
    config_path = args.output / "configuration.json"
    if config_path.exists() and json.loads(config_path.read_text()) != config:
        message = "Use a different --output for a different acquisition configuration."
        raise ValueError(message)
    write_json(config_path, config)
    write_json(args.output / "status.json", {"status": "acquiring", "requested_issuers": args.size})
    factors(cache, args.start, args.end)
    universe = issuers(cache, args.size, args.candidates)
    market = prices(cache, universe, args.start, args.end)
    panel = snapshots(cache, universe, args.first_snapshot, args.last_snapshot)
    summary = coverage(panel, market)
    summary.to_csv(args.output / "coverage.csv", index=False)
    price_summary = []
    for ticker in market:
        valid = market[ticker].dropna()
        price_summary.append(
            {
                "ticker": ticker,
                "observations": len(valid),
                "first_observation": str(valid.index.min().date()) if len(valid) else None,
                "last_observation": str(valid.index.max().date()) if len(valid) else None,
            }
        )
    write_json(args.output / "price-coverage.json", price_summary)
    hashes = {}
    for path in sorted(cache.rglob("*")):
        if path.is_file():
            with path.open("rb") as stream:
                hashes[str(path.relative_to(cache))] = hashlib.file_digest(
                    stream, "sha256"
                ).hexdigest()
    write_json(
        args.output / "manifest.json",
        {
            "retrieved_at": datetime.now(UTC).isoformat(),
            "sha256": hashes,
            "selection": "current-cap ranked, distinct current SEC issuers; survivorship-biased",
            "prices": "Yahoo adjusted closes, raw OHLC and corporate actions retained",
            "accounting": "US-GAAP annual 10-K facts with filed <= snapshot cutoff",
        },
    )
    write_json(
        args.output / "status.json",
        {
            "status": "complete",
            "issuers": len(universe),
            "with_prices": int(market.notna().any().sum()),
            "accounting_snapshots": len(panel),
            "first_price": str(market.index.min().date()),
            "last_price": str(market.index.max().date()),
            "first_snapshot": int(panel.year.min()),
            "last_snapshot": int(panel.year.max()),
        },
    )
    write_report(args.output)
    logging.getLogger(__name__).info(
        "Completed acquisition: %s issuers; coverage in %s", len(universe), args.output
    )
