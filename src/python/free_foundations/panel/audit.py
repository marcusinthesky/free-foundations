"""Measure how much frozen-model geometry depends on context, cohort and labels."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pandas as pd

from free_foundations.expanded.audit import (
    compare,
    context_audit,
    query_cohort_audit,
    support_label_audit,
    target_audit,
)
from free_foundations.expanded.encoding import cap_support, foundation_states, prepare
from free_foundations.expanded.representations import READOUTS
from free_foundations.panel.characteristics import ROOT, build
from free_foundations.panel.design import DESIGNS
from free_foundations.panel.networks import MODEL_CACHE, MODEL_SOURCE, context, labels, rung_views
from free_foundations.panel.observations import annual_data

if TYPE_CHECKING:
    from collections.abc import Mapping

LOGGER = logging.getLogger(__name__)
YEARS = (2016, 2020, 2025)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")


def run() -> None:
    """Query-cohort, support-draw, support-label and target checks on fixed cohorts."""
    four, broad = build()
    output = ROOT / "audit"
    output.mkdir(parents=True, exist_ok=True)
    contexts: list[Mapping[str, object]] = []
    records: list[Mapping[str, object]] = []
    for name in ("four", "three"):
        design = DESIGNS[name]
        for year in YEARS:
            tickers = annual_data(
                four,
                year,
                characteristics=design.characteristics,
                histories=design.cohort_histories,
                output=output / name,
            ).tickers
            views = rung_views(four, broad, year, design.characteristics, design.history)
            for rung in ("histories", "broad"):
                core = labels(four, broad, "market_cap_assets")
                data = context(views[rung], core, tickers, year)
                redraw = cap_support(
                    prepare(views[rung], core, tickers, year, "income"), salt="audit-redraw"
                )
                contexts.append({"design": name, "rung": rung} | context_audit(data))
                for model in MODELS:
                    LOGGER.info("Audit %s %s %s %s", name, year, rung, model)
                    found = [
                        *query_cohort_audit(data, model, MODEL_CACHE, MODEL_SOURCE),
                        *support_label_audit(data, model, MODEL_CACHE, MODEL_SOURCE),
                    ]
                    first = foundation_states(data, model, MODEL_CACHE, MODEL_SOURCE)
                    second = foundation_states(
                        redraw, model, MODEL_CACHE, MODEL_SOURCE, store=False
                    )
                    found += [
                        {
                            "check": "support_draw",
                            "variant": "salted_256",
                            "representation": label,
                            "arm": arm,
                            **compare(first[readout], second[readout]),
                        }
                        for readout, label, arm in READOUTS[model]
                    ]
                    if rung == "histories":
                        alternate = context(
                            views[rung], labels(four, broad, "income_assets"), tickers, year
                        )
                        found += target_audit(data, alternate, model, MODEL_CACHE, MODEL_SOURCE)
                    records += [
                        {"design": name, "year": year, "rung": rung, "model": model} | row
                        for row in found
                    ]
                pd.DataFrame(records).to_csv(output / "measurement-audit.csv", index=False)
    pd.DataFrame(contexts).to_csv(output / "contexts.csv", index=False)
    summary = (
        pd.DataFrame(records)
        .groupby(["design", "check", "representation", "arm"])
        .agg(
            distance_spearman_min=("distance_spearman", "min"),
            distance_spearman_median=("distance_spearman", "median"),
            max_relative_state_change=("max_relative_state_change", "max"),
            max_weight_change=("max_weight_change", "max"),
        )
        .reset_index()
    )
    summary.to_csv(output / "summary.csv", index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()
