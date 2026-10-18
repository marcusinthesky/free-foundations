"""One command line for every study; each DVC stage runs exactly one of these commands.

Run from the repository root, for example `free-foundations panel run --design four`.
semflow fingerprints the code each command reaches, so a stage reruns only when it changes.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer

from free_foundations.expanded import report as expanded_report
from free_foundations.expanded import run as expanded_run
from free_foundations.expanded.setup import checkpoint_catalogue
from free_foundations.fernandez import combined as fernandez_combined
from free_foundations.fernandez import report as fernandez_report
from free_foundations.fernandez import run as fernandez_run
from free_foundations.fernandez import simulation as fernandez_simulation
from free_foundations.ladder import report as ladder_report
from free_foundations.ladder import run as ladder_run
from free_foundations.ladder.data import ARMS
from free_foundations.panel import audit as panel_audit
from free_foundations.panel import inference as panel_inference
from free_foundations.panel import report as panel_report
from free_foundations.panel import run as panel_run
from free_foundations.panel.design import DESIGNS
from free_foundations.pilot import __main__ as pilot_run
from free_foundations.universe import run as universe_run

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

YEARS = list(range(2016, 2026))
FERNANDEZ = Path("research/fernandez")

app = typer.Typer(no_args_is_help=True, help=__doc__)
universe = typer.Typer(no_args_is_help=True, help="Larger public-data universe.")
pilot = typer.Typer(no_args_is_help=True, help="Original pilot inputs and experiment.")
expanded = typer.Typer(no_args_is_help=True, help="Expanded representation and metric grid.")
fernandez = typer.Typer(no_args_is_help=True, help="Paper-aligned replication and ladder.")
ladder = typer.Typer(no_args_is_help=True, help="Matched cross-sectional ladder.")
panel = typer.Typer(no_args_is_help=True, help="Chronological panel designs.")
for name, group in {
    "universe": universe,
    "pilot": pilot,
    "expanded": expanded,
    "fernandez": fernandez,
    "ladder": ladder,
    "panel": panel,
}.items():
    app.add_typer(group, name=name)


type Values = str | list[str] | None


def among(allowed: Iterable[str]) -> Callable[[Values], Values]:
    """Reject values outside a declared set, as argparse `choices` did."""
    names = tuple(allowed)

    def check(value: Values) -> Values:
        values = [value] if isinstance(value, str) else value or []
        unknown = [item for item in values if item not in names]
        if unknown:
            message = f"{', '.join(unknown)} not in {', '.join(names)}."
            raise typer.BadParameter(message)
        return value

    return check


@app.callback()
def configure() -> None:
    """Log progress with timestamps."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")


@universe.command("run")
def universe_acquire(  # noqa: PLR0913, PLR0917 -- one option per acquisition setting.
    size: int = 1000,
    candidates: int = 2000,
    start: str = "2008-01-01",
    end: str = "2026-01-01",
    first_snapshot: int = 2009,
    last_snapshot: int = 2024,
    output: Path = Path("research/universe"),
) -> None:
    """Cache immutable inputs, then report achievable annual sample sizes and history."""
    universe_run.main(
        universe_run.Acquisition(
            size, candidates, start, end, first_snapshot, last_snapshot, output
        )
    )


@pilot.command("run")
def pilot_stage(
    stage: Annotated[str, typer.Option(callback=among(("markets", "data", "run", "all")))] = "all",
    output: Path = Path("research/pilot"),
    *,
    pretrained: bool = False,
) -> None:
    """Cache inputs, run the experiment and write compact reviewable artifacts."""
    pilot_run.main(stage, output, pretrained=pretrained)


@expanded.command("checkpoints")
def expanded_checkpoints() -> None:
    """Restore pinned model weights and record their content hashes."""
    checkpoint_catalogue()


@expanded.command("run")
def expanded_experiment(
    output: Path = Path("research/expanded"),
    source: Path = Path("research/pilot/cache"),
    years: Annotated[list[int] | None, typer.Option("--year")] = None,
) -> None:
    """Run a bounded development comparison without refreshing original inputs."""
    expanded_run.main(output, source, years or YEARS)


@expanded.command("report")
def expanded_results(output: Path = Path("research/expanded")) -> None:
    """Audit a finished run and regenerate its compact reports."""
    expanded_report.main(output)


@fernandez.command("run")
def fernandez_experiment(
    output: Path = FERNANDEZ,
    years: Annotated[list[int] | None, typer.Option("--year")] = None,
) -> None:
    """Reuse immutable market, factor and model caches; results live separately."""
    fernandez_run.main(output, years or YEARS)


@fernandez.command("simulate")
def fernandez_simulate() -> None:
    """Simulate portfolio risk under the paper's spatial weights."""
    fernandez_simulation.simulate(FERNANDEZ)


@fernandez.command("report")
def fernandez_results() -> None:
    """Write the replication's comparison tables and report."""
    fernandez_report.report(FERNANDEZ)


@fernandez.command("combined")
def fernandez_combined_networks() -> None:
    """One spatial-error likelihood per combined network on a fixed common cohort."""
    fernandez_combined.run()


@ladder.command("run")
def ladder_experiment(
    stages: Annotated[list[str] | None, typer.Option("--stage")] = None,
    arms: Annotated[list[str] | None, typer.Option("--arm", callback=among(ARMS))] = None,
    models: Annotated[list[str] | None, typer.Option("--model")] = None,
) -> None:
    """Run R0 and the ladder; R0 needs Rscript but no foundation models."""
    ladder_run.main(stages or ["r0", "ladder", "bootstrap"], arms or list(ARMS), models)


@ladder.command("report")
def ladder_results() -> None:
    """Write every available ladder report."""
    ladder_report.main()


@panel.command("prepare")
def panel_prepare() -> None:
    """Build the shared point-in-time characteristics and audit every price break."""
    panel_run.prepare()


@panel.command("run")
def panel_design(
    designs: Annotated[list[str], typer.Option("--design", callback=among(DESIGNS))],
    models: Annotated[list[str] | None, typer.Option("--model")] = None,
) -> None:
    """Run the requested designs; foundation-model readouts are cached by context."""
    panel_run.main(designs, models)


@panel.command("report")
def panel_results(
    designs: Annotated[list[str], typer.Option("--design", callback=among(DESIGNS))],
) -> None:
    """Report requested designs and shared provenance records."""
    panel_report.main(designs)


@panel.command("audit")
def panel_measurement_audit() -> None:
    """Query-cohort, support-draw, support-label and target sensitivity of model geometry."""
    panel_audit.run()


@panel.command("intervals")
def panel_intervals(
    designs: Annotated[list[str], typer.Option("--design", callback=among(DESIGNS))],
) -> None:
    """Recompute paired intervals, contrasts and confidence sets from saved daily scores."""
    panel_inference.main(designs)
