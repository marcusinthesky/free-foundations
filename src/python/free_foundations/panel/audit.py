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
from free_foundations.expanded.encoding import foundation_states
from free_foundations.expanded.representations import READOUTS
from free_foundations.fernandez.kernels import effective_neighbours, kernel_weights
from free_foundations.fernandez.models import paper_weights
from free_foundations.panel.characteristics import ROOT, build
from free_foundations.panel.design import DESIGNS, DRAWS
from free_foundations.panel.networks import (
    MODEL_CACHE,
    MODEL_SOURCE,
    classical,
    context,
    labels,
    rung_views,
)
from free_foundations.panel.observations import annual_data

if TYPE_CHECKING:
    from collections.abc import Mapping

    from free_foundations.contracts import FloatArray
    from free_foundations.expanded.audit import Networks

LOGGER = logging.getLogger(__name__)
YEARS = (2016, 2020, 2025)
MODELS = ("tabpfn_fast", "tabpfn_full", "tabfm", "exaone")


def adaptive(joint: FloatArray) -> Networks:
    """The panel's median kernel and its matched kernel, at the joint network's fraction.

    The matched target is the joint Fernández network's mean effective-neighbour fraction
    under exp, scaled to each compared cohort's size.
    """
    fraction = effective_neighbours(paper_weights(joint)) / (len(joint) - 1)

    def networks(distance: FloatArray) -> dict[str, FloatArray]:
        target = fraction * (len(distance) - 1)
        return {
            "median": kernel_weights(distance, "median")[0],
            "matched": kernel_weights(distance, "matched", target=target)[0],
        }

    return networks


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
            joint = classical(four, year, tickers, design.characteristics, design.history)
            networks = adaptive(joint["fernandez_joint"])
            for rung in ("histories", "broad"):
                core = labels(four, broad, "market_cap_assets")
                data = context(views[rung], core, tickers, year)
                # The panel's first redraw, so its cached history-rung readouts are reused.
                redraw = context(views[rung], core, tickers, year, DRAWS[0])
                contexts.append({"design": name, "rung": rung} | context_audit(data))
                for model in MODELS:
                    LOGGER.info("Audit %s %s %s %s", name, year, rung, model)
                    found = [
                        *query_cohort_audit(data, model, MODEL_CACHE, MODEL_SOURCE, networks),
                        *support_label_audit(data, model, MODEL_CACHE, MODEL_SOURCE, networks),
                    ]
                    first = foundation_states(data, model, MODEL_CACHE, MODEL_SOURCE)
                    second = foundation_states(
                        redraw, model, MODEL_CACHE, MODEL_SOURCE, store=False
                    )
                    found += [
                        {
                            "check": "support_draw",
                            "variant": DRAWS[0],
                            "representation": label,
                            "arm": arm,
                            **compare(first[readout], second[readout], networks),
                        }
                        for readout, label, arm in READOUTS[model]
                    ]
                    if rung == "histories":
                        alternate = context(
                            views[rung], labels(four, broad, "income_assets"), tickers, year
                        )
                        found += target_audit(
                            data, alternate, model, MODEL_CACHE, MODEL_SOURCE, networks
                        )
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
            max_weight_change_median=("max_weight_change_median", "max"),
            max_weight_change_matched=("max_weight_change_matched", "max"),
        )
        .reset_index()
    )
    summary.to_csv(output / "summary.csv", index=False)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    run()
