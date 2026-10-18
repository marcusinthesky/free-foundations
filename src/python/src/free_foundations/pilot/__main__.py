"""Run the pilot from the repository root: `free-foundations pilot STAGE`."""

from __future__ import annotations

import hashlib
import logging
import os
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pandas as pd

from free_foundations.pilot.data import market_inputs, sec_inputs, write_json
from free_foundations.pilot.experiment import run_experiment
from free_foundations.pilot.features import accounting_panel
from free_foundations.pilot.report import paired_comparisons, plot_summary, summarize

if TYPE_CHECKING:
    from pathlib import Path


def checkpoint_metadata(cache: Path) -> None:
    """Resolve and cache a pinned public Fast checkpoint, without implicit credentials."""
    from huggingface_hub import hf_hub_download, model_info  # noqa: PLC0415

    destination = cache / "checkpoint.json"
    if destination.exists():
        return
    repository = "Prior-Labs/tabpfn_3_5"
    revision = model_info(repository, token=False).sha
    filename = "tabpfn-v3.5-fast-20260909.safetensors"
    path = hf_hub_download(
        repository, filename, revision=revision, token=False, local_dir=cache / "checkpoint"
    )
    write_json(
        destination,
        {"repository": repository, "revision": revision, "filename": filename, "path": path},
    )


def manifest(cache: Path) -> None:
    """Hash cached research inputs and record package versions without personal identity."""
    from importlib.metadata import version  # noqa: PLC0415

    files = [*cache.glob("*.parquet"), *cache.glob("*.json"), *cache.glob("facts/*.json")]
    hashes = {}
    for path in files:
        with path.open("rb") as stream:
            hashes[str(path.relative_to(cache))] = hashlib.file_digest(stream, "sha256").hexdigest()
    write_json(
        cache.parent / "manifest.json",
        {
            "created_at": datetime.now(UTC).isoformat(),
            "sha256": hashes,
            "versions": {
                name: version(name)
                for name in ("yfinance", "edgartools", "pandas-datareader", "numpy", "scikit-learn")
            },
            "prices": "Yahoo adjusted daily closes; 2012-01-01 through 2025-12-31",
            "factors": "Ken French daily FF5 + momentum; percentages divided by 100",
            "accounting": "SEC companyfacts USD US-GAAP annual 10-K(/A); filed <= prior Dec 31",
        },
    )


def main(stage: str, output: Path, *, pretrained: bool) -> None:
    """Cache inputs, run the experiment and write compact reviewable artifacts."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    os.environ.setdefault("TABPFN_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    cache = output / "cache"
    prices, factors = market_inputs(cache)
    if stage == "markets":
        return
    if stage in {"data", "all"}:
        universe = sec_inputs(cache)
        accounting_panel(cache, universe)
        manifest(cache)
    if stage in {"run", "all"}:
        universe = pd.read_csv(output / "universe.csv")
        panel = pd.read_parquet(cache / "accounting.parquet")
        if pretrained:
            checkpoint_metadata(cache)
        run_experiment(prices[universe["ticker"]], factors, panel, cache, pretrained=pretrained)
        summarize(output)
        if pretrained:
            paired_comparisons(output)
            plot_summary(output)
        write_json(
            output / "execution-status.json",
            {
                "updated_at": datetime.now(UTC).isoformat(),
                "status": "complete",
                "empirical_spatial_results": True,
                "selected_firms": len(universe),
                "pretrained": pretrained,
            },
        )
        manifest(cache)
        logging.getLogger(__name__).info("Results: %s", output / "summary.csv")
