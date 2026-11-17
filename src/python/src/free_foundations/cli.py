"""Commands for one frozen-feature measurement study and its replication appendix."""

from __future__ import annotations

import logging
from pathlib import Path

import typer

from free_foundations.fernandez import replication
from free_foundations.panel import report as panel_report
from free_foundations.panel import run as panel_run
from free_foundations.representations.setup import checkpoint_catalogue
from free_foundations.study import run as study_run
from free_foundations.universe import run as universe_run

app = typer.Typer(no_args_is_help=True)
universe = typer.Typer(no_args_is_help=True, help="Explicit financial-data acquisition.")
models = typer.Typer(no_args_is_help=True, help="Pinned checkpoints for the four retained models.")
fernandez = typer.Typer(no_args_is_help=True, help="Core spatial-CAPM replication and VaR audit.")
panel = typer.Typer(no_args_is_help=True, help="The frozen-feature measurement study.")
study = typer.Typer(no_args_is_help=True, help="Matched quarterly CRSP-SEC replication and ladder.")
for name, group in {
    "universe": universe,
    "models": models,
    "fernandez": fernandez,
    "panel": panel,
    "study": study,
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


@study.command("acquire")
def study_acquire(
    crsp_csv: Path = Path(".tmp/crsp_top1000_2001_2025.csv"),
    extraction_script: Path = Path(".tmp/get_crsp_returns.py"),
    output: Path = Path("research/crsp-study/recovery"),
    *,
    offline: bool = False,
    metadata_only: bool = False,
) -> None:
    """Recover staged CRSP and public SEC evidence explicitly and resumably."""
    study_run.acquire(
        crsp_csv, extraction_script, output=output, offline=offline, metadata_only=metadata_only
    )


@study.command("link")
def study_link(
    crsp_csv: Path = Path(".tmp/crsp_top1000_2001_2025.csv"),
    output: Path = Path("research/crsp-study/recovery"),
    *,
    offline: bool = False,
) -> None:
    """Recover historical issuer identities using public SEC ownership filing metadata."""
    study_run.link(crsp_csv, output=output, offline=offline)


@study.command("freeze")
def study_freeze(
    staging: Path = Path("research/crsp-study/recovery"),
    output: Path = Path("research/crsp-study"),
) -> None:
    """Validate and promote completed staged sources, retaining the previous snapshot."""
    study_run.freeze(staging=staging, output=output)


@study.command("prepare")
def study_prepare() -> None:
    """Prepare one quarterly roster, observation mask and as-of XBRL information ladder."""
    study_run.prepare()


@study.command("encode")
def study_encode() -> None:
    """Encode all eligible scalar fields with audited native-NA column blocks."""
    study_run.encode()


@study.command("run")
def study_measurement() -> None:
    """Estimate every matched representation and covariance comparison from saved states."""
    study_run.analyze()


@study.command("replicate")
def study_replication() -> None:
    """Run the descriptive Fernández core on the common quarterly master panel."""
    study_run.analyze(replication_only=True)


@study.command("report")
def study_publication() -> None:
    """Render source coverage, matched estimates and audited claims without estimation."""
    study_run.report()
