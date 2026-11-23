"""DVC stage commands by data layer: raw sources, processed panels, research results."""

from __future__ import annotations

import logging

import typer

from free_foundations.cli import processed, publication, raw, research

app = typer.Typer(no_args_is_help=True, help="Pipeline stages by data layer.")
app.add_typer(raw.app, name="raw")
app.add_typer(processed.app, name="processed")
app.add_typer(research.app, name="research")
app.add_typer(publication.app, name="publication")


@app.callback()
def configure() -> None:
    """Log numerical-stage progress with timestamps."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
