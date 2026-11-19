"""Research layer: in-sample layers, the out-of-sample spatial APT and publication."""

from __future__ import annotations

from pathlib import Path

import typer

from free_foundations.study.paths import (
    PANEL,
    RESULTS,
    STATES,
)
from free_foundations.study.spec import PARAMS

app = typer.Typer(no_args_is_help=True, help="In-sample estimates and the saved-result report.")


@app.command("replicate")
def replicate(
    formation: int = typer.Option(...),
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path | None = None,
    params: Path = PARAMS,
) -> None:
    """Fernández cross-sections with MM betas, every network and generated-beta draws."""
    from free_foundations.study.experiments.replication import run  # noqa: PLC0415

    output = output or RESULTS / "replication" / "formations" / str(formation)
    run(panel, representations, output, params, formation_year=formation)


@app.command("estimate-comovement")
def comovement(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = RESULTS / "comovement" / "summary",
    params: Path = PARAMS,
) -> None:
    """Quarterly spatial panels of excess returns with period effects, by network."""
    from free_foundations.study.experiments.comovement import run  # noqa: PLC0415

    run(panel, representations, output, params)


@app.command("measure-alignment")
def alignment(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = RESULTS / "alignment" / "summary",
    params: Path = PARAMS,
) -> None:
    """Mantel association of network distances with realized return co-movement."""
    from free_foundations.study.experiments.alignment import run  # noqa: PLC0415

    run(panel, representations, output, params)


@app.command("estimate-apt")
def apt(
    panel: Path = PANEL,
    representations: Path = STATES,
    factors: Path = Path("data/raw/crsp-sec/factors"),
    output: Path = RESULTS / "apt" / "summary",
    params: Path = PARAMS,
) -> None:
    """Out-of-sample CAPM, APT and spatial APT covariances on raw and calibrated geometry."""
    from free_foundations.study.experiments.apt import run  # noqa: PLC0415

    run(panel, representations, factors, output, params)


@app.command("collect-replication")
def collect_replication(
    formations: Path = RESULTS / "replication" / "formations",
    output: Path = RESULTS / "replication" / "summary",
    params: Path = PARAMS,
) -> None:
    """Combine the independent formation runs."""
    from free_foundations.study.experiments.replication import collect  # noqa: PLC0415

    collect(formations, output, params)
