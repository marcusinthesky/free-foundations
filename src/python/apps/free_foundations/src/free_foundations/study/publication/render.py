"""Render shared manuscript values, tables, figure and audit from saved results.

Nothing is estimated here. Generated TeX stays under the paper project and every
reported value is also recorded in the publication claims ledger.
"""

from __future__ import annotations

import json
import re
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from free_foundations.artifacts.atomic import atomic_bytes, atomic_csv
from free_foundations.artifacts.metadata import write_json
from free_foundations.study.publication import apt as publication_apt
from free_foundations.study.publication.formatting import (
    _escape,
    _number,
)
from free_foundations.study.publication.quarterly import (
    Report,
    _alignment,
    _comovement,
    _figure,
    _matched,
    _replication,
    _sample,
)
from free_foundations.study.spec import StudySpec

if TYPE_CHECKING:
    from pathlib import Path


def _macro_name(key: str) -> str:
    words = re.split(r"[^A-Za-z]+", key)
    return "\\ff" + "".join(word[:1].upper() + word[1:] for word in words if word)


def _value_binding(key: str, display: str, raw: float | str) -> str:
    """Emit a checked display value and, when numeric, a raw rounding operand."""
    binding = f"\\ffDeclareValue{{{key}}}{{{display}}}\n"
    if isinstance(raw, (int, float)) and np.isfinite(raw):
        binding += f"\\ffDeclareNumber{{{key}}}{{{raw}}}\n"
    return binding


def _table_name(body: str) -> str:
    match = re.search(r"(?m)^% ff-table:([A-Za-z0-9-]+)$", body)
    if match is None:
        message = "generated table has no ff-table marker"
        raise ValueError(message)
    return match.group(1)


def render(  # noqa: PLR0913 -- every saved input of the report is explicit.
    panel: Path,
    *,
    replication: Path,
    comovement: Path,
    alignment: Path,
    apt: Path | None = None,
    output: Path,
    generated: Path,
    params: Path,
) -> None:
    """Write one paper-wide catalog and audit from the saved research layers."""
    spec = StudySpec.read(params)
    output.mkdir(parents=True, exist_ok=True)
    report = Report()
    _sample(report, replication, comovement, spec)
    membership = pd.read_parquet(panel / "membership.parquet", columns=["formation_year", "permco"])
    formation = membership.loc[membership["formation_year"].eq(spec.primary_formation)]
    report.claim("primary population issuers", int(formation["permco"].nunique()))
    _replication(report, replication, spec)
    _matched(report, replication, spec)
    _comovement(report, comovement, spec)
    _alignment(report, alignment)
    tables = generated / "tables"
    figures = generated / "figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    for body in report.parts:
        atomic_bytes(tables / f"quarterly-{_table_name(body)}.tex", body.encode())
    atomic_bytes(figures / "rolling-rho.tex", _figure(replication, figures, spec).encode())
    apt_report = publication_apt.Workshop()
    if apt is not None:
        publication_apt.replication(apt_report, replication, spec)
        publication_apt.apt(apt_report, apt)
        publication_apt.insample(apt_report, comovement, alignment)
        for name, body in apt_report.tables.items():
            atomic_bytes(tables / f"apt-{name}.tex", body.encode())
    bindings = [
        _value_binding(
            f"quarterly-{key.replace('_', '-')}",
            _escape(
                value
                if isinstance(value, str)
                else f"{value:,}"
                if isinstance(value, int)
                else _number(value)
            ),
            value,
        )
        for key, value in sorted(report.metrics.items())
    ]
    bindings.extend(
        _value_binding(f"apt-{key.replace(' ', '-')}", apt_report.macros[key], value)
        for key, value in sorted(apt_report.values.items())  # noqa: PD011 -- result mapping
    )
    atomic_bytes(generated / "numbers.tex", "".join(bindings).encode())
    prepared = json.loads((panel / "manifest.json").read_text())
    metrics: dict[str, Any] = dict(report.metrics) | {
        "analytical_issuer_quarters": prepared["analytical_issuer_quarters"],
        "population_issuer_quarters": prepared["population_issuer_quarters"],
        "unresolved_linkage_issuer_quarters": prepared["source_recovery"][
            "unresolved_linkage_issuer_quarters"
        ],
    }
    write_json(output / "metrics.json", metrics)
    write_json(output / "apt_claims.json", apt_report.values)
    atomic_csv(
        output / "claims.csv",
        pd.DataFrame(
            [
                {"macro": _macro_name(key), "key": key, "value": value}
                for key, value in report.metrics.items()
            ]
        ),
    )
