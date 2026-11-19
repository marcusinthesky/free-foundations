"""Raw layer: explicit source acquisition, freezing and pinned model weights.

Acquisition and linkage use the network and write only the staging directory.
``freeze`` promotes completed staging into the frozen DVC source snapshot.
"""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 -- Typer resolves annotations at runtime.
from typing import Annotated

import typer

from free_foundations.encoders.backends.setup import checkpoint_catalogue
from free_foundations.study.paths import (
    SOURCES,
    STAGING,
    WEIGHTS,
)
from free_foundations.study.sources import acquire as run
from free_foundations.study.sources import freeze as promotion
from free_foundations.study.spec import PARAMS

app = typer.Typer(no_args_is_help=True, help="Frozen sources and pinned model weights.")


@app.command("acquire")
def acquire(  # noqa: PLR0913, PLR0917 -- Typer options for acquisition inputs and modes.
    crsp_csv: Annotated[Path, typer.Option(help="Staged WRDS CRSP CIZ monthly extract.")],
    extraction_script: Annotated[Path, typer.Option(help="Script that produced the extract.")],
    staging: Path = STAGING,
    canonical: Path = SOURCES,
    params: Path = PARAMS,
    existing_cache: Annotated[
        Path | None, typer.Option(help="Earlier SEC cache to reuse before downloading.")
    ] = None,
    *,
    offline: bool = False,
    metadata_only: bool = False,
) -> None:
    """Recover CRSP, public SEC evidence and factors into staging, resumably."""
    run.acquire(
        crsp_csv,
        extraction_script,
        staging=staging,
        canonical=canonical,
        params=params,
        offline=offline,
        metadata_only=metadata_only,
        existing_cache=existing_cache,
    )


@app.command("link")
def link(
    crsp_csv: Annotated[Path, typer.Option(help="Staged WRDS CRSP CIZ monthly extract.")],
    staging: Path = STAGING,
    canonical: Path = SOURCES,
    params: Path = PARAMS,
    *,
    offline: bool = False,
) -> None:
    """Recover historical issuer identities from public SEC ownership metadata."""
    run.link(crsp_csv, staging=staging, canonical=canonical, params=params, offline=offline)


@app.command("freeze")
def freeze(staging: Path = STAGING, canonical: Path = SOURCES, params: Path = PARAMS) -> None:
    """Promote completed staged sources, keeping the previous snapshot in staging."""
    promotion.freeze(staging=staging, canonical=canonical, params=params)


@app.command("fetch-checkpoints")
def checkpoints(output: Path = WEIGHTS) -> None:
    """Acquire and verify the four pinned pretrained checkpoints."""
    checkpoint_catalogue(output)
