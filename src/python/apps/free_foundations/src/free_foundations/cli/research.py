"""Research layer: in-sample layers, the out-of-sample spatial APT and publication."""

from __future__ import annotations

from pathlib import Path

import typer

from free_foundations.study.matched_paths import (
    MATCHED_CACHE,
    MATCHED_CELLS,
    MATCHED_CONTEXTS,
    MATCHED_RESULTS,
    MATCHED_WEIGHTS,
)
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


@app.command("prepare-matched-sample")
def prepare_matched_sample(
    panel: Path = PANEL,
    output: Path = MATCHED_RESULTS / "sample",
    params: Path = PARAMS,
) -> None:
    """Fit the factor exposures and freeze one ordered quarterly analysis mask."""
    from free_foundations.study.experiments.matched_factors import prepare_sample  # noqa: PLC0415

    prepare_sample(panel, output, params)


@app.command("matched-factors")
def matched_factors(
    panel: Path = PANEL,
    sample: Path = MATCHED_RESULTS / "sample",
    cells: Path = MATCHED_CELLS,
    output: Path = MATCHED_RESULTS / "factors",
    params: Path = PARAMS,
) -> None:
    """Cross the quarterly factor controls with three spatial specifications."""
    from free_foundations.study.experiments.matched_factors import run  # noqa: PLC0415

    run(panel, sample, cells, output, params)


@app.command("matched-kernels")
def matched_kernels(
    panel: Path = PANEL,
    sample: Path = MATCHED_RESULTS / "sample",
    cells: Path = MATCHED_CELLS,
    output: Path = MATCHED_RESULTS / "kernels",
    params: Path = PARAMS,
) -> None:
    """Compare three weighting rules on both distances and five history sets."""
    from free_foundations.study.experiments.matched_kernels import run  # noqa: PLC0415

    run(panel, sample, cells, output, params)


@app.command("matched-encoders")
def matched_encoders(
    sample: Path = MATCHED_RESULTS / "sample",
    cells: Path = MATCHED_CELLS,
    output: Path = MATCHED_RESULTS / "encoders",
    params: Path = PARAMS,
) -> None:
    """Compare frozen states to same-input controls and record the selection."""
    from free_foundations.study.experiments.matched_encoders import run  # noqa: PLC0415

    run(sample, cells, output, params)


@app.command("matched-geometry")
def matched_geometry(
    panel: Path = PANEL,
    selection: Path = MATCHED_RESULTS / "encoders" / "selection.json",
    cells: Path = MATCHED_CELLS,
    output: Path = MATCHED_RESULTS / "geometry",
    params: Path = PARAMS,
) -> None:
    """Save dated principal coordinates and the conditional interpretation decision."""
    from free_foundations.study.experiments.matched_geometry import run  # noqa: PLC0415

    run(panel, selection, cells, output, params)


@app.command("matched-historical-geometry")
def matched_historical_geometry(
    panel: Path = PANEL,
    representations: Path = STATES,
    output: Path = MATCHED_RESULTS / "historical-geometry",
    params: Path = PARAMS,
) -> None:
    """Save the workshop's dated ratio geometry from its audited frozen state."""
    from free_foundations.study.experiments.matched_geometry import historical  # noqa: PLC0415

    historical(panel, representations, output, params)


@app.command("matched-ablation")
def matched_ablation(  # noqa: PLR0913, PLR0917 -- explicit DVC artifact paths.
    panel: Path = PANEL,
    sample: Path = MATCHED_RESULTS / "sample",
    selection: Path = MATCHED_RESULTS / "encoders" / "selection.json",
    geometry: Path = MATCHED_RESULTS / "geometry",
    contexts: Path = MATCHED_CONTEXTS,
    cells: Path = MATCHED_CELLS,
    weights: Path = MATCHED_WEIGHTS,
    cache: Path = MATCHED_CACHE,
    output: Path = MATCHED_RESULTS / "ablation",
    params: Path = PARAMS,
    device: str = "cuda",
) -> None:
    """Run feature and coordinate ablations when the saved inertia decision triggers."""
    from free_foundations.study.experiments.matched_geometry import ablate  # noqa: PLC0415

    ablate(
        panel,
        sample,
        selection,
        geometry,
        contexts,
        cells,
        weights,
        cache,
        output,
        params,
        device=device,
    )


@app.command("collect-matched")
def collect_matched(
    results: Path = MATCHED_RESULTS,
    output: Path = MATCHED_RESULTS / "evidence",
) -> None:
    """Index the verified DVC outputs for publication."""
    from free_foundations.study.experiments.matched_evidence import collect  # noqa: PLC0415

    collect(results, output)
