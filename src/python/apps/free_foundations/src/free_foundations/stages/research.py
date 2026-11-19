"""Research layer: in-sample replication, co-movement, alignment and publication."""

from __future__ import annotations

from pathlib import Path

import typer

from free_foundations.study.spec import PARAMS

app = typer.Typer(no_args_is_help=True, help="In-sample estimates and the saved-result report.")
PANEL = Path("data/processed/crsp-sec/panel")
STATES = Path("data/processed/crsp-sec/representations")
RESULTS = Path("data/research/crsp-sec")


@app.command("replicate")
def replicate(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = RESULTS / "replication",
    params: Path = PARAMS,
) -> None:
    """Fernández cross-sections with MM betas, every network and generated-beta draws."""
    from free_foundations.study.replication import run  # noqa: PLC0415

    run(panel, representations, output, params)


@app.command("comovement")
def comovement(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = RESULTS / "comovement",
    params: Path = PARAMS,
) -> None:
    """Quarterly spatial panels of excess returns with period effects, by network."""
    from free_foundations.study.comovement import run  # noqa: PLC0415

    run(panel, representations, output, params)


@app.command("alignment")
def alignment(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = RESULTS / "alignment",
    params: Path = PARAMS,
) -> None:
    """Mantel association of network distances with realized return co-movement."""
    from free_foundations.study.alignment import run  # noqa: PLC0415

    run(panel, representations, output, params)


@app.command("publish")
def publish(  # noqa: PLR0913, PLR0917 -- Typer options, every saved input explicit.
    panel: Path = PANEL,
    replication: Path = RESULTS / "replication",
    comovement: Path = RESULTS / "comovement",
    alignment: Path = RESULTS / "alignment",
    output: Path = RESULTS / "publication",
    tex: Path = Path("src/latex/build/crsp-study.tex"),
    params: Path = PARAMS,
) -> None:
    """Render tables, figures and the claims audit from saved results only."""
    from free_foundations.study.publication import render  # noqa: PLC0415

    render(
        panel,
        replication=replication,
        comovement=comovement,
        alignment=alignment,
        output=output,
        tex=tex,
        params=params,
    )
