"""Frozen French monthly factors and explicitly defined quarterly aggregates."""

from __future__ import annotations

import io
import re
import zipfile
from typing import TYPE_CHECKING

import httpx
import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes, atomic_parquet
from free_foundations.artifacts.metadata import write_json
from free_foundations.study.spec import StudySpec, file_hash

if TYPE_CHECKING:
    from pathlib import Path

FILES = {
    "ff5": "F-F_Research_Data_5_Factors_2x3_CSV.zip",
    "momentum": "F-F_Momentum_Factor_CSV.zip",
}
BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"


def parse_monthly(payload: bytes) -> pd.DataFrame:
    """Read only YYYYMM rows; annual summaries must not masquerade as monthly data."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if len(names) != 1:
            msg = "French source must contain exactly one CSV."
            raise ValueError(msg)
        lines = archive.read(names[0]).decode("utf-8-sig").splitlines()
    first = next((i for i, line in enumerate(lines) if re.match(r"\s*\d{6}\s*,", line)), None)
    if first is None or first == 0:
        msg = "French source has no headed monthly YYYYMM section."
        raise ValueError(msg)
    header = lines[first - 1].split(",")
    names = [item.strip() for item in header[1:]]
    if not names or any(not name for name in names) or len(set(names)) != len(names):
        msg = "French monthly factor names must be nonempty and unique."
        raise ValueError(msg)
    rows = []
    for line in lines[first:]:
        if not re.match(r"\s*\d{6}\s*,", line):
            break
        rows.append(line.split(","))
    result = pd.DataFrame(rows, columns=["month", *names])
    result["month"] = pd.to_datetime(result["month"].str.strip(), format="%Y%m")
    for column in result.columns.difference(["month"]):
        values = pd.to_numeric(result[column], errors="raise")
        result[column] = values.mask(values.isin([-99.99, -999])) / 100
    return result


def quarterly_factors(monthly: pd.DataFrame) -> pd.DataFrame:
    """Compound market total returns and RF separately; label long-short proxies."""
    if not {"month", "RF", "Mkt-RF"}.issubset(monthly):
        msg = "Monthly factors require month, RF and market-excess columns."
        raise ValueError(msg)
    frame = monthly.copy()
    frame["month"] = pd.to_datetime(frame["month"]).dt.to_period("M").dt.to_timestamp()
    frame = frame.set_index("month").sort_index()
    if frame.index.has_duplicates:
        msg = "Duplicate monthly factor dates."
        raise ValueError(msg)
    periods = pd.DatetimeIndex(frame.index).to_period("Q")
    complete = frame.groupby(periods).size().eq(3)
    result = (1 + frame).groupby(periods).prod(min_count=3) - 1
    market = (1 + frame["Mkt-RF"] + frame["RF"]).groupby(periods).prod(min_count=3) - 1
    result["Mkt-RF"] = market - result["RF"]
    result = result.where(complete, axis=0)
    result.index = pd.PeriodIndex(result.index, freq="Q").to_timestamp(how="end").normalize()
    return result.rename_axis("quarter").reset_index()


def acquire_factors(destination: Path, spec: StudySpec, *, offline: bool = False) -> bool:
    """Reuse immutable bytes; routine preparation never calls this acquisition function."""
    destination.mkdir(parents=True, exist_ok=True)
    paths = {name: destination / filename for name, filename in FILES.items()}
    missing = [name for name, path in paths.items() if not path.is_file()]
    if missing and offline:
        write_json(destination / "status.json", {"status": "not_acquired", "missing": missing})
        return False
    for name in missing:
        response = httpx.get(BASE + FILES[name], timeout=120, follow_redirects=True)
        response.raise_for_status()
        path = paths[name]
        parse_monthly(response.content)
        atomic_bytes(path, response.content)
    frames = [parse_monthly(path.read_bytes()).set_index("month") for path in paths.values()]
    monthly = pd.concat(frames, axis=1).reset_index()
    if monthly.columns.has_duplicates:
        msg = "French source files have overlapping factor columns."
        raise ValueError(msg)
    monthly = monthly.loc[monthly["month"].between(spec.archive_start, spec.archive_end)]
    atomic_parquet(destination / "monthly.parquet", monthly)
    atomic_parquet(destination / "quarterly.parquet", quarterly_factors(monthly))
    expected = pd.period_range(spec.archive_start, spec.archive_end, freq="M").to_timestamp()
    missing_months = expected.difference(pd.DatetimeIndex(monthly["month"]))
    missing_cells = int(monthly.drop(columns="month").isna().sum().sum())
    complete = not len(missing_months) and not missing_cells
    write_json(
        destination / "status.json",
        {
            "status": "complete" if complete else "incomplete_factor_history",
            "sha256": {path.name: file_hash(path) for path in paths.values()},
            "units": "decimal returns",
            "vintage": "frozen downloaded CIZ research-return files; not historical vintages",
            "market": "compound monthly market total return, subtract compounded RF",
            "other_factors": "prod(1+monthly_factor)-1; compounded long-short factor proxies",
            "missing_months": missing_months.strftime("%Y-%m").tolist(),
            "missing_factor_cells": missing_cells,
        },
    )
    return complete
