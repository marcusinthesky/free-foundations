"""Core characteristic-history CAPM replication and the stated portfolio-VaR audit."""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from scipy.stats import norm

from free_foundations.data import write_json
from free_foundations.fernandez import manifest
from free_foundations.fernandez.bootstrap import network_draws, quarter_indices, resample, summarize
from free_foundations.fernandez.characteristics import history_view
from free_foundations.fernandez.estimates import nonspatial, spatial
from free_foundations.fernandez.evaluation import exposure_table, robust_betas, runtime_record
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.fernandez.replication_data import (
    ARMS,
    CUTOFF_YEAR,
    HISTORY,
    ROOT,
    TERMS,
    Inputs,
    cohort,
    load,
    medians,
)
from free_foundations.fernandez.simulation import simulate

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray
    from free_foundations.fernandez.estimates import Row


def distances(
    inputs: Inputs, characteristics: tuple[str, ...], tickers: tuple[str, ...]
) -> dict[str, FloatArray]:
    """Original single-characteristic rank distances and the joint RMS extension."""
    histories = pd.DataFrame(
        history_view(inputs.four[list(characteristics)], HISTORY).xs(CUTOFF_YEAR - 1, level="year")
    ).loc[list(tickers)]
    result = {
        f"fernandez_{name}": rank_distance(histories.filter(like=f"{name}__").to_numpy(dtype=float))
        for name in characteristics
    }
    result["fernandez_joint"] = np.sqrt(np.mean([value**2 for value in result.values()], axis=0))
    return result


def replication(
    inputs: Inputs, exposures: pd.DataFrame, output: Path
) -> tuple[dict[str, FloatArray], dict[str, tuple[str, ...]]]:
    """Fit both common cohorts; self-links change only the sensitivity specification."""
    rows: list[Row] = []
    bootstrap_networks: dict[str, FloatArray] = {}
    cohorts = {f"common_{arm}": cohort(inputs, names) for arm, names in ARMS.items()}
    write_json(
        output / "cohorts.json",
        {
            label: {
                "characteristics": ARMS[label.removeprefix("common_")],
                "firms": len(names),
                "tickers": names,
            }
            for label, names in cohorts.items()
        },
    )
    for label, tickers in cohorts.items():
        if len(tickers) < 4:
            message = f"Too few complete firms for {label}: {len(tickers)}."
            raise ValueError(message)
        y = medians(inputs.quarters, tickers).to_numpy(dtype=float)
        x = exposures.loc[list(tickers), list(TERMS)].to_numpy(dtype=float)
        shared = {"table": label, "factors": "capm"}
        rows.append(shared | nonspatial(y, x, TERMS))
        for name, distance in distances(
            inputs, ARMS[label.removeprefix("common_")], tickers
        ).items():
            for links in (False, True):
                weights = paper_weights(distance, self_links=links)
                identity = {"network": name, "kernel": "exp", "self_links": links}
                rows += [shared | identity | row for row in spatial(y, x, weights, TERMS)]
                if not links:
                    bootstrap_networks[f"{label}|{name}"] = weights
    pd.DataFrame(rows).to_csv(output / "estimates.csv", index=False)
    return bootstrap_networks, cohorts


def generated_betas(
    inputs: Inputs,
    networks: dict[str, FloatArray],
    cohorts: dict[str, tuple[str, ...]],
    output: Path,
) -> None:
    """Resample shared quarters, re-estimate CAPM betas, and hold each network fixed."""
    quarters = tuple(sorted(inputs.quarters["date"].dt.strftime("%Y-%m-%d").unique()))
    union = tuple(sorted({ticker for group in cohorts.values() for ticker in group}))
    exposures, outcomes, rejected = resample(
        inputs.quarters,
        tickers=union,
        terms=TERMS,
        indices=quarter_indices(quarters),
        output=output,
        tag="capm-bootstrap",
    )
    summaries = [
        summarize(network_draws({key: weights}, cohorts[key.split("|")[0]], exposures, outcomes))
        for key, weights in networks.items()
    ]
    frame = pd.concat(summaries, ignore_index=True).assign(factors="capm", rejected=rejected)
    frame[["table", "network"]] = frame["network"].str.split("|", n=1, expand=True)
    frame.to_csv(output / "bootstrap.csv", index=False)


def audit(output: Path) -> None:
    """Record substitutions and the Table 6 discrepancy without tuning the simulation."""
    manifest.write(output)
    maximum = 1000 * float(norm.ppf(0.95)) * 0.01 * np.sqrt(1 + 1 / 20)
    write_json(
        output / "audit.json",
        {
            "replication": "Core characteristic-history spatial CAPM on new US data",
            "cohorts": ["common_four", "common_three"],
            "primary": "zero diagonal, exp(-distance), row normalized; CAPM MM betas",
            "sensitivity": "positive diagonal under the same exponential kernel",
            "joint_network": "RMS extension of the individual characteristic distances",
            "generated_beta_inference": "199 valid shared-quarter bootstrap draws; networks fixed",
            "var_audit": {
                "source": "Fernández (2011), equations (8a)-(8b) and Table 6",
                "firms": 20,
                "spatial_coefficient": 0,
                "beta_interval": [0.5, 1],
                "maximum_under_stated_calibration": float(maximum),
                "published_value": 36.27,
                "reconciled": False,
                "reason": (
                    "At zero spatial dependence W disappears; "
                    "seeds and self-links cannot reconcile this bound."
                ),
            },
        },
    )


def main() -> None:
    """Run the retained replication without models, expanded inputs or ladder variants."""
    ROOT.mkdir(parents=True, exist_ok=True)
    inputs = load()
    cohorts = [cohort(inputs, names) for names in ARMS.values()]
    union = tuple(sorted({ticker for group in cohorts for ticker in group}))
    quarters = inputs.quarters.loc[inputs.quarters["ticker"].isin(union)]
    quarters.to_csv(ROOT / "quarterly-returns.csv", index=False)
    estimates = robust_betas(quarters, ROOT, terms=TERMS)
    estimates.to_csv(ROOT / "mm-betas.csv", index=False)
    write_json(ROOT / "mm-runtime.json", runtime_record(ROOT))
    networks, names = replication(inputs, exposure_table(estimates), ROOT)
    generated_betas(inputs, networks, names, ROOT)
    simulate(ROOT)
    audit(ROOT)
    paths = [*sorted(ROOT.glob("*.csv")), *sorted(ROOT.glob("*.json"))]
    write_json(
        ROOT / "manifest.json",
        {
            str(path): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in paths
            if path.name != "manifest.json"
        },
    )
