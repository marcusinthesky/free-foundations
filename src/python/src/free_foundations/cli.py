"""Commands for one frozen-feature measurement study and its replication appendix."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from free_foundations.fernandez import replication
from free_foundations.panel import report as panel_report
from free_foundations.panel import run as panel_run
from free_foundations.representations.setup import checkpoint_catalogue
from free_foundations.universe import run as universe_run

app = typer.Typer(no_args_is_help=True)
universe = typer.Typer(no_args_is_help=True, help="Explicit financial-data acquisition.")
models = typer.Typer(no_args_is_help=True, help="Pinned checkpoints for the four retained models.")
fernandez = typer.Typer(no_args_is_help=True, help="Core spatial-CAPM replication and VaR audit.")
panel = typer.Typer(no_args_is_help=True, help="The frozen-feature measurement study.")
for name, group in {
    "universe": universe,
    "models": models,
    "fernandez": fernandez,
    "panel": panel,
}.items():
    app.add_typer(group, name=name)


@app.callback()
def configure() -> None:
    """Log numerical-stage progress with timestamps."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


@universe.command("run")
def universe_acquire(  # noqa: PLR0913, PLR0917 -- explicit acquisition settings.
    size: int = 1000,
    candidates: int = 2000,
    start: str = "2008-01-01",
    end: str = "2026-01-01",
    first_snapshot: int = 2009,
    last_snapshot: int = 2024,
    output: Path = Path("research/universe"),
) -> None:
    """Acquire source snapshots deliberately; routine DVC reproduction restores them."""
    universe_run.main(
        universe_run.Acquisition(
            size, candidates, start, end, first_snapshot, last_snapshot, output
        )
    )


@models.command("checkpoints")
def models_checkpoints() -> None:
    """Acquire pinned weights separately from financial estimation and publication."""
    checkpoint_catalogue()


@panel.command("prepare")
def panel_prepare() -> None:
    """Prepare characteristics and audited financial observations from frozen inputs."""
    panel_run.prepare()


@panel.command("encode")
def panel_encode() -> None:
    """Extract the declared representations once, with verified checkpoint provenance."""
    panel_run.encode()


@panel.command("run")
def panel_measurement() -> None:
    """Estimate financial readouts and score the fixed study and decisive diagnostics."""
    panel_run.main()


@panel.command("report")
def panel_publication() -> None:
    """Render publication assets from saved numerical results without inference."""
    panel_report.main()


@fernandez.command("run")
def fernandez_replication() -> None:
    """Run the CAPM replication, generated-beta inference and stated VaR calibration."""
    replication.main()
