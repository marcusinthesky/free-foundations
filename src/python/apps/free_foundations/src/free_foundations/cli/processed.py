"""Processed layer: the master issuer-quarter panel and frozen representation states."""

from __future__ import annotations

from pathlib import Path  # noqa: TC003 -- Typer resolves annotations at runtime.

import typer

from free_foundations.study.panel import prepare as panel_prepare
from free_foundations.study.panel.store import inputs
from free_foundations.study.paths import (
    CACHE,
    CONTEXTS,
    PANEL,
    PARTS,
    SOURCES,
    STATES,
    WEIGHTS,
)
from free_foundations.study.representations.run import encode as encode_cell
from free_foundations.study.spec import PARAMS

app = typer.Typer(no_args_is_help=True, help="Master panel and representation states.")


@app.command("prepare-panel")
def prepare(
    sources: Path = SOURCES,
    output: Path = PANEL,
    params: Path = PARAMS,
) -> None:
    """Build the roster, outcome mask, cohorts, characteristics and as-of XBRL facts."""
    panel_prepare.prepare(sources, output, params)


@app.command("encode")
def encode(  # noqa: PLR0913, PLR0917 -- Typer options.
    rung: str = typer.Option(...),
    model: str = typer.Option(...),
    contexts: Path = CONTEXTS,
    panel: Path = PANEL,
    weights: Path = WEIGHTS,
    states: Path = CACHE,
    output: Path | None = None,
    params: Path = PARAMS,
) -> None:
    """Encode one frozen model on one verified information rung."""
    if output is None:
        output = PARTS / rung / model
    encode_cell(panel, weights, states, output, params, rung=rung, model=model, contexts=contexts)


@app.command("assemble-states")
def assemble_states(
    parts: Path = PARTS,
    output: Path = STATES,
    params: Path = PARAMS,
) -> None:
    """Assemble the independently verified representation cells."""
    from free_foundations.study.representations.assemble import assemble  # noqa: PLC0415

    assemble(parts, output, params)


@app.command("prepare-contexts")
def prepare_contexts(
    panel: Path = PANEL,
    output: Path = CONTEXTS,
    params: Path = PARAMS,
) -> None:
    """Materialize common context arrays for each information rung."""
    from free_foundations.study.representations.contexts import save_contexts  # noqa: PLC0415
    from free_foundations.study.spec import file_hash  # noqa: PLC0415

    spec, tables = inputs(panel, params)
    save_contexts(
        tables["panel"],
        tables["characteristics"],
        panel / "broad",
        spec,
        output,
        file_hash(panel / "manifest.json"),
    )


@app.command("direct")
def direct(
    rung: str = typer.Option(...),
    contexts: Path = CONTEXTS,
    panel: Path = PANEL,
    output: Path | None = None,
    params: Path = PARAMS,
) -> None:
    """Compute the direct feature control for one verified information rung."""
    destination = output or PARTS / rung / "direct"
    encode_cell(
        panel,
        WEIGHTS,
        CACHE,
        destination,
        params,
        rung=rung,
        model="direct",
        contexts=contexts,
    )
