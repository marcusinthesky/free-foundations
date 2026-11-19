"""Processed layer: the master issuer-quarter panel and frozen representation states."""

from __future__ import annotations

from pathlib import Path

import typer

from free_foundations.study import run
from free_foundations.study.spec import PARAMS

app = typer.Typer(no_args_is_help=True, help="Master panel and representation states.")
PANEL = Path("data/processed/crsp-sec/panel")


@app.command("prepare")
def prepare(
    sources: Path = Path("data/raw/crsp-sec"),
    output: Path = PANEL,
    params: Path = PARAMS,
) -> None:
    """Build the roster, outcome mask, cohorts, characteristics and as-of XBRL facts."""
    run.prepare(sources, output, params)


@app.command("encode")
def encode(
    panel: Path = PANEL,
    weights: Path = Path("data/raw/models"),
    states: Path = Path("data/processed/crsp-sec/state-cache"),
    output: Path = Path("data/processed/crsp-sec/representations"),
    params: Path = PARAMS,
) -> None:
    """Encode both information rungs with every pinned model and the direct control."""
    run.encode(panel, weights, states, output, params)
