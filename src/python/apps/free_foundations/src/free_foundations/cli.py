"""Command line for the CRSP-SEC study pipeline, organized by data layer."""

from __future__ import annotations

import logging

import typer

from free_foundations.stages import app as stages

app = typer.Typer(no_args_is_help=True)
app.add_typer(stages, name="stages")


@app.callback()
def configure() -> None:
    """Log numerical-stage progress with timestamps."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
