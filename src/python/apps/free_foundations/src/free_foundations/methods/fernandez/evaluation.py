"""Separate the paper's cross-sectional exercise from ex ante covariance forecasts."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Literal

import pandas as pd

SCRIPT = Path(__file__).with_name("betas.R")
type MMBackend = Literal["robustbase", "robust"]


FACTOR_NAMES = {
    "Mkt-RF": "market",
    "SMB": "smb",
    "HML": "hml",
    "RMW": "rmw",
    "CMA": "cma",
    "Mom": "mom",
}


def robust_betas(  # noqa: PLR0913 -- keyword-only R runtime options.
    quarters: pd.DataFrame,
    output: Path,
    *,
    terms: tuple[str, ...] = ("market",),
    indices: pd.DataFrame | None = None,
    cores: int = 1,
    tag: str = "capm",
    backend: MMBackend = "robustbase",
) -> pd.DataFrame:
    """Call the established MM implementation rather than relabel OLS or Huber estimates.

    Returns long estimates with one row per replicate, firm and term. Replicate 0 is the
    original sample; ``indices`` lists resampled quarters for bootstrap replicates.
    """
    if backend not in ("robustbase", "robust"):
        message = f"Unknown MM backend: {backend}."
        raise ValueError(message)
    executable = shutil.which("Rscript")
    if executable is None:
        message = "Run inside devenv shell: the pinned robustbase and robust R runtime is required."
        raise RuntimeError(message)
    cache = output / "cache"
    cache.mkdir(parents=True, exist_ok=True)
    # Preserve the primary backend's cache names, including the existing bootstrap.
    identity = tag if backend == "robustbase" else f"{backend}-{tag}"
    source = cache / f"mm-{identity}-input.csv"
    destination = cache / f"mm-{identity}-output.csv"
    frame = quarters[["date", "ticker", "excess", *terms]].rename(columns={"date": "quarter"})
    frame.assign(quarter=frame["quarter"].astype(str).str[:10]).to_csv(source, index=False)
    arguments = [executable, str(SCRIPT), str(source), str(destination), ",".join(terms)]
    if indices is not None:
        path = cache / f"mm-{identity}-indices.csv"
        indices.assign(quarter=indices["quarter"].astype(str).str[:10]).to_csv(path, index=False)
        arguments += [str(path), str(cores)]
    else:
        arguments += ["", str(cores)]
    arguments.append(backend)
    subprocess.run(arguments, check=True)  # noqa: S603 -- fixed local R script and generated paths.
    result = pd.read_csv(destination)
    original = result.loc[result["replicate"].eq(0)]
    if not original.empty and not original["converged"].all():
        message = "At least one robust MM fit on the original sample did not converge."
        raise RuntimeError(message)
    return result


def runtime_record(
    output: Path, tag: str = "capm", *, backend: MMBackend = "robustbase"
) -> dict[str, str]:
    """R, package version, controls and completion rules recorded by the last MM call."""
    identity = tag if backend == "robustbase" else f"{backend}-{tag}"
    path = output / "cache" / f"mm-{identity}-output-runtime.csv"
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    return dict(zip(frame["name"], frame["value"], strict=True))


def exposure_table(estimates: pd.DataFrame, replicate: int = 0) -> pd.DataFrame:
    """Wide factor exposures for one replicate, indexed by ticker, excluding intercepts."""
    selected = estimates.loc[
        estimates["replicate"].eq(replicate) & estimates["term"].ne("intercept")
    ]
    terms = list(dict.fromkeys(selected["term"]))
    return selected.pivot_table(index="ticker", columns="term", values="estimate")[terms]
