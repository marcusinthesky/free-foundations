"""R0 replication and the R1-R4 cross-sectional ladder, one outcome and cohort per table."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.fernandez.evaluation import exposure_table, robust_betas, runtime_record
from free_foundations.fernandez.kernels import KERNELS, geometry, placebo, size_groups
from free_foundations.fernandez.models import error_ml, ols, symmetric_spectrum
from free_foundations.ladder import manifest
from free_foundations.ladder.bootstrap import network_draws, quarter_indices, resample, summarize
from free_foundations.ladder.data import ARMS, ROOT, TERMS, cohort, load, medians
from free_foundations.ladder.estimates import nonspatial, spatial
from free_foundations.ladder.networks import (
    fernandez_distances,
    ladder_distances,
    log_assets,
    rung_of,
    weights,
)
from free_foundations.pilot.data import write_json

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.ladder.data import Inputs
    from free_foundations.ladder.estimates import Row
    from free_foundations.ladder.networks import Network

LOGGER = logging.getLogger(__name__)
PLACEBOS = 99


def table(
    y: FloatArray,
    x: FloatArray,
    networks: dict[Network, FloatArray],
    terms: tuple[str, ...],
    labels: dict[str, str],
) -> list[Row]:
    """The nonspatial benchmark, then every network's S2SLS, SEM and lag-ML fits."""
    rows = [labels | nonspatial(y, x, terms)]
    for (name, kernel, links), matrix in networks.items():
        identity = {"network": name, "kernel": kernel, "self_links": links}
        rows += [labels | identity | row for row in spatial(y, x, matrix, terms)]
    return rows


def replication(inputs: Inputs, exposures: pd.DataFrame, output: Path) -> dict[str, FloatArray]:
    """R0: each arm's common cohort, then each characteristic's maximal cohort."""
    tables: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
        f"common_{arm}": (characteristics, cohort(inputs, characteristics))
        for arm, characteristics in ARMS.items()
    }
    tables |= {f"coverage_{name}": ((name,), cohort(inputs, (name,))) for name in ARMS["four"]}
    write_json(
        output / "cohorts.json",
        {
            label: {"characteristics": c, "firms": len(t), "tickers": t}
            for label, (c, t) in tables.items()
        },
    )
    rows: list[Row] = []
    bootstrap_networks: dict[str, FloatArray] = {}
    for label, (characteristics, tickers) in tables.items():
        LOGGER.info("R0 %s: %s firms", label, len(tickers))
        distances = {
            name: value
            for name, value in fernandez_distances(inputs, characteristics, tickers).items()
            if name != "fernandez_joint"
        }
        networks = weights(distances, ("exp", "median"), self_links=(False, True))
        y = medians(inputs.quarters, tickers).to_numpy(dtype=float)
        x = exposures.loc[list(tickers), ["market"]].to_numpy(dtype=float)
        rows += table(y, x, networks, ("market",), {"table": label, "factors": "capm"})
        for (name, kernel, links), matrix in networks.items():
            if kernel == "exp" and not links:
                bootstrap_networks[f"{label}|{name}"] = matrix
    pd.DataFrame(rows).to_csv(output / "estimates.csv", index=False)
    manifest.write(output)
    return bootstrap_networks


def ladder(
    inputs: Inputs,
    arm: str,
    exposures: dict[str, pd.DataFrame],
    output: Path,
    models: tuple[str, ...] | None,
) -> dict[str, FloatArray]:
    """R1-R4 on one arm's common cohort; every row shares firms, outcome and estimator."""
    characteristics = ARMS[arm]
    tickers = cohort(inputs, characteristics)
    distances = ladder_distances(inputs, arm, characteristics, tickers, output, models=models)
    networks = weights(distances, KERNELS)
    firms = len(tickers)
    networks["uniform_network", "none", False] = (np.ones((firms, firms)) - np.eye(firms)) / (
        firms - 1
    )
    y = medians(inputs.quarters, tickers).to_numpy(dtype=float)
    rows: list[Row] = []
    for factors, terms in TERMS.items():
        LOGGER.info("Ladder %s %s: %s firms, %s networks", arm, factors, firms, len(networks))
        x = exposures[factors].loc[list(tickers), list(terms)].to_numpy(dtype=float)
        rows += table(y, x, networks, terms, {"table": arm, "factors": factors})
    frame = pd.DataFrame(rows)
    frame["rung"] = [
        "reference" if n in {"nonspatial", "uniform_network"} else rung_of(str(n))
        for n in frame["network"]
    ]
    frame.to_csv(output / "estimates.csv", index=False)
    pd.DataFrame(
        [
            {"network": name, "kernel": kernel} | geometry(distances.get(name), matrix)
            for (name, kernel, _), matrix in networks.items()
        ]
    ).to_csv(output / "geometry.csv", index=False)
    placebos(
        y,
        exposures["capm"].loc[list(tickers), ["market"]].to_numpy(dtype=float),
        networks,
        size_groups(log_assets(inputs, tickers)),
    ).to_csv(output / "placebo.csv", index=False)
    return {
        f"{arm}|{name}": matrix
        for (name, kernel, _), matrix in networks.items()
        if kernel in {"exp", "none"}
    }


def placebos(
    y: FloatArray, x: FloatArray, networks: dict[Network, FloatArray], groups: FloatArray
) -> pd.DataFrame:
    """SEM log-likelihood gain over OLS versus size-restricted label permutations."""
    base = ols(y, x).log_likelihood or 0.0
    rows = []
    for (name, kernel, _), matrix in networks.items():
        if name == "uniform_network":
            continue
        spectrum = symmetric_spectrum(matrix)

        def gain(candidate: FloatArray, spectrum: FloatArray = spectrum) -> float:
            fit = error_ml(y, x, candidate, eigenvalues=spectrum, standard_errors=False, xatol=None)
            return (fit.log_likelihood or 0.0) - base

        observed = gain(matrix)
        draws = np.array([gain(placebo(matrix, groups, seed)) for seed in range(PLACEBOS)])
        rows.append(
            {
                "network": name,
                "kernel": kernel,
                "observed_gain": observed,
                "placebo_mean_gain": float(draws.mean()),
                "placebo_max_gain": float(draws.max()),
                "rank_p_value": (1 + int((draws >= observed).sum())) / (PLACEBOS + 1),
            }
        )
    return pd.DataFrame(rows)


def generated_betas(
    inputs: Inputs, networks: dict[str, FloatArray], tickers: dict[str, tuple[str, ...]]
) -> None:
    """Resample quarters jointly for returns and factors; refit each fixed network."""
    quarters = tuple(sorted(inputs.quarters["date"].dt.strftime("%Y-%m-%d").unique()))
    indices = quarter_indices(quarters)
    union = tuple(sorted({ticker for group in tickers.values() for ticker in group}))
    summaries = []
    for factors, terms in TERMS.items():
        sample = union if factors == "capm" else tickers["three"]
        LOGGER.info("Bootstrap %s: %s firms", factors, len(sample))
        exposures, outcomes, rejected = resample(
            inputs.quarters,
            tickers=sample,
            terms=terms,
            indices=indices,
            output=ROOT,
            tag=f"{factors}-bootstrap",
        )
        for key, matrix in networks.items():
            table_name = key.split("|")[0]
            if factors == "ff6" and table_name not in ARMS:
                continue
            draws = network_draws({key: matrix}, tickers[table_name], exposures, outcomes)
            summaries.append(summarize(draws).assign(factors=factors, rejected=rejected))
    frame = pd.concat(summaries, ignore_index=True)
    frame[["table", "network"]] = frame["network"].str.split("|", n=1, expand=True)
    frame["directory"] = ["r0" if name not in ARMS else name for name in frame["table"]]
    for directory, group in frame.groupby("directory"):
        group.drop(columns="directory").to_csv(ROOT / str(directory) / "bootstrap.csv", index=False)


def main(stages: list[str], arms_run: list[str], models_run: list[str] | None) -> None:
    """Run R0 and the ladder; R0 needs Rscript but no foundation models."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    inputs = load()
    arms = {arm: cohort(inputs, ARMS[arm]) for arm in ARMS}
    coverage = {f"coverage_{name}": cohort(inputs, (name,)) for name in ARMS["four"]}
    union = tuple(sorted({t for group in [*arms.values(), *coverage.values()] for t in group}))
    ROOT.mkdir(parents=True, exist_ok=True)
    exposures = {
        "capm": exposure_table(
            robust_betas(
                inputs.quarters.loc[inputs.quarters["ticker"].isin(union)], ROOT, tag="capm"
            )
        ),
        "ff6": exposure_table(
            robust_betas(
                inputs.quarters.loc[inputs.quarters["ticker"].isin(arms["three"])],
                ROOT,
                terms=TERMS["ff6"],
                tag="ff6",
            )
        ),
    }
    wide = pd.concat(
        [exposures["capm"].add_prefix("capm_"), exposures["ff6"].add_prefix("ff6_")], axis=1
    )
    wide.rename_axis("ticker").reset_index().to_csv(ROOT / "mm-betas.csv", index=False)
    write_json(ROOT / "mm-runtime.json", runtime_record(ROOT, "capm"))
    networks: dict[str, FloatArray] = {}
    if "r0" in stages:
        (ROOT / "r0").mkdir(exist_ok=True)
        networks |= replication(inputs, exposures["capm"], ROOT / "r0")
    models = None if models_run is None else tuple(models_run)
    for arm in arms_run if "ladder" in stages else ():
        (ROOT / arm).mkdir(exist_ok=True)
        networks |= ladder(inputs, arm, exposures, ROOT / arm, models)
    if "bootstrap" in stages and networks:
        generated_betas(
            inputs, networks, {**arms, **coverage, **{f"common_{a}": t for a, t in arms.items()}}
        )
    paths = [
        *sorted(Path(__file__).parent.parent.rglob("*.py")),
        *sorted(Path(__file__).parent.parent.rglob("*.R")),
        *sorted(path for path in ROOT.rglob("*") if path.is_file() and "cache" not in path.parts),
    ]
    write_json(
        ROOT / "manifest.json",
        {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths
            if path.name != "manifest.json"
        },
    )
