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
from free_foundations.fernandez.evaluation import (
    MMBackend,
    exposure_table,
    robust_betas,
    runtime_record,
)
from free_foundations.fernandez.models import paper_weights, rank_distance
from free_foundations.fernandez.replication_data import (
    ARMS,
    CUTOFF_YEAR,
    HISTORY,
    ROOT,
    TERMS,
    WINDOWS,
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


def sensitivity_cohorts(inputs: dict[str, Inputs]) -> dict[str, dict[str, tuple[str, ...]]]:
    """Eligible samples per window and the same firms for the matched timing contrast."""
    natural = {
        timing: {arm: cohort(data, names) for arm, names in ARMS.items()}
        for timing, data in inputs.items()
    }
    intersection = {
        arm: tuple(sorted(set.intersection(*(set(groups[arm]) for groups in natural.values()))))
        for arm in ARMS
    }
    return {
        timing: {
            f"common_{arm}|{sample}": names
            for arm, eligible in groups.items()
            for sample, names in (("natural", eligible), ("intersection", intersection[arm]))
        }
        for timing, groups in natural.items()
    }


def sensitivity_rows(
    inputs: Inputs,
    exposures: pd.DataFrame,
    groups: dict[str, tuple[str, ...]],
    backend: MMBackend,
) -> list[Row]:
    """Conditional second-stage sensitivity fits, rebuilding W for each reported cohort."""
    rows: list[Row] = []
    for label, tickers in groups.items():
        table, sample = label.split("|")
        if len(tickers) < 4:
            message = f"Too few complete firms for {inputs.timing}/{label}: {len(tickers)}."
            raise ValueError(message)
        shared: Row = {
            "table": table,
            "factors": "capm",
            "timing": inputs.timing,
            "backend": backend,
            "sample": sample,
            "sample_id": (
                f"{table}:intersection"
                if sample == "intersection"
                else f"{table}:{inputs.timing}:natural"
            ),
            "return_start": WINDOWS[inputs.timing][0],
            "return_end": WINDOWS[inputs.timing][1],
            "characteristic_start": 2015,
            "characteristic_end": 2024,
        }
        y = medians(inputs.quarters, tickers).to_numpy(dtype=float)
        x = exposures.loc[list(tickers), list(TERMS)].to_numpy(dtype=float)
        rows.append(shared | nonspatial(y, x, TERMS))
        names = ARMS[table.removeprefix("common_")]
        for name, distance in distances(inputs, names, tickers).items():
            weights = paper_weights(distance, self_links=False)
            identity: Row = {"network": name, "kernel": "exp", "self_links": False}
            rows += [shared | identity | row for row in spatial(y, x, weights, TERMS)]
    return rows


def sensitivity_contrasts(frame: pd.DataFrame) -> pd.DataFrame:
    """Right-minus-left point-estimate contrasts on exactly matched firms."""
    keys = ["table", "sample", "sample_id", "network", "estimator"]
    values = ["premium_market", "intensity", "pseudo_r2_structural", "pseudo_r2_reduced"]
    rows = []
    for (table, sample, sample_id, network, estimator), group in frame.groupby(keys):
        cells = {(r.timing, r.backend): r for r in group.itertuples(index=False)}
        comparisons = [
            ("software", (timing, "robustbase"), (timing, "robust"))
            for timing in WINDOWS
            if (timing, "robustbase") in cells and (timing, "robust") in cells
        ]
        if sample == "intersection":
            comparisons += [
                ("timing", ("shifted", backend), ("contemporaneous", backend))
                for backend in ("robustbase", "robust")
            ]
        for contrast, left, right in comparisons:
            first, second = cells[left], cells[right]
            if first.firms != second.firms:
                message = f"Unmatched sensitivity contrast: {left} versus {right}."
                raise ValueError(message)
            rows.append(
                {
                    "contrast": contrast,
                    "table": table,
                    "sample": sample,
                    "sample_id": sample_id,
                    "network": network,
                    "estimator": estimator,
                    "firms": first.firms,
                    "left_timing": left[0],
                    "right_timing": right[0],
                    "left_backend": left[1],
                    "right_backend": right[1],
                    "inference": "descriptive matched-sample point-estimate difference",
                    **{
                        f"delta_{name}": getattr(second, name) - getattr(first, name)
                        for name in values
                    },
                }
            )
    return pd.DataFrame(rows)


def sensitivities(inputs: Inputs, primary: pd.DataFrame, output: Path) -> None:
    """Cross return timing and software while retaining the primary bootstrap separately."""
    windows = {"shifted": inputs, "contemporaneous": load(timing="contemporaneous")}
    groups = sensitivity_cohorts(windows)
    write_json(
        output / "sensitivity-cohorts.json",
        {
            timing: {
                label: {"firms": len(tickers), "tickers": tickers}
                for label, tickers in samples.items()
            }
            for timing, samples in groups.items()
        },
    )
    rows: list[Row] = []
    estimates: list[pd.DataFrame] = []
    runtime = {}
    quarters = []
    backends: tuple[MMBackend, ...] = ("robustbase", "robust")
    for timing, data in windows.items():
        union = {ticker for sample in groups[timing].values() for ticker in sample}
        sample = data.quarters.loc[data.quarters["ticker"].isin(union)]
        quarters.append(sample.assign(timing=timing))
        for backend in backends:
            tag = f"sensitivity-{timing}"
            reuse_primary = timing == "shifted" and backend == "robustbase"
            fitted = (
                primary
                if reuse_primary
                else robust_betas(sample, output, terms=TERMS, backend=backend, tag=tag)
            )
            estimates.append(fitted.assign(timing=timing, backend=backend))
            runtime[f"{timing}|{backend}"] = runtime_record(
                output, "capm" if reuse_primary else tag, backend=backend
            )
            rows += sensitivity_rows(data, exposure_table(fitted), groups[timing], backend)
    frame = pd.DataFrame(rows)
    frame.to_csv(output / "sensitivity-estimates.csv", index=False)
    sensitivity_contrasts(frame).to_csv(output / "sensitivity-contrasts.csv", index=False)
    pd.concat(estimates, ignore_index=True).to_csv(output / "sensitivity-mm-betas.csv", index=False)
    pd.concat(quarters, ignore_index=True).to_csv(
        output / "sensitivity-quarterly-returns.csv", index=False
    )
    write_json(output / "sensitivity-mm-runtime.json", runtime)


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
            "timing_software_sensitivity": (
                "Shifted and contemporaneous windows crossed with robustbase and robust MM; "
                "natural and intersection cohorts; conditional inference only"
            ),
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
    sensitivities(inputs, estimates, ROOT)
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
