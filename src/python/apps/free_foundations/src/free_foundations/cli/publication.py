"""Render publication assets from saved research results."""

from __future__ import annotations

from pathlib import Path

import typer

from free_foundations.study.paths import (
    PANEL,
    PUBLICATION,
    RESULTS,
)
from free_foundations.study.spec import PARAMS

app = typer.Typer(
    no_args_is_help=True, help="Render manuscript assets from saved experiment results."
)


@app.command("render")
def render_paper(  # noqa: PLR0913, PLR0917 -- Typer options, every saved input explicit.
    panel: Path = PANEL,
    replication: Path = RESULTS / "replication" / "summary",
    comovement: Path = RESULTS / "comovement" / "summary",
    alignment: Path = RESULTS / "alignment" / "summary",
    apt: Path = RESULTS / "apt" / "summary",
    output: Path = PUBLICATION,
    generated: Path = Path("src/latex/projects/free-foundations/src/generated"),
    params: Path = PARAMS,
) -> None:
    """Render tables, figures and the claims audit from saved results only."""
    from free_foundations.study.publication.render import render  # noqa: PLC0415

    render(
        panel,
        replication=replication,
        comovement=comovement,
        alignment=alignment,
        apt=apt,
        output=output,
        generated=generated,
        params=params,
    )
