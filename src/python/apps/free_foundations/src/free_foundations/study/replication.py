"""Layer A: Fernández's characteristic-history spatial CAPM, in sample, per formation.

For each December formation, the full top-``top_n`` roster with verified SEC
information at the window start is followed for ``window_quarters`` quarters,
including exits and CRSP delisting returns. Stage one fits MM CAPM betas on each
issuer's observed quarterly excess returns; the outcome is the issuer's median
quarterly excess return. Stage two regresses outcomes on betas: OLS, the spatial
lag by 2SLS (her estimator) and ML, and the spatial error by ML, each without an
intercept (her specification) and with one (identified). Networks are fixed at
formation from information available then. Intervals are Wald intervals from
statadic and, for the primary formation, a stationary quarter bootstrap that
refits betas, medians and every spatial model (generated-regressor robust).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from scipy.stats import norm

from free_foundations.data import write_json
from free_foundations.fernandez.evaluation import robust_betas
from free_foundations.study import spatial, spatial_ml
from free_foundations.study.inference import (
    block_length,
    generated_beta_indices,
    percentile_interval,
)
from free_foundations.study.networks import (
    CHARACTERISTICS,
    Network,
    characteristic_distances,
    exponential_weights,
)
from free_foundations.study.rosters import StudyInputs, load
from free_foundations.study.source_io import atomic_parquet

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

LOGGER = logging.getLogger(__name__)
ESTIMATORS = ("lag_iv", "lag_ml", "error_ml")
# Parity between statadic and the resampling refits on the original sample.
PARITY_TOLERANCE = 1e-4
VAR_LEVEL = 0.95
VAR_VALUE = 1000.0
# A bootstrap draw keeps issuers whose MM refit and median exist; below this many
# the draw is recorded as unavailable rather than fitted.
MIN_DRAW_ISSUERS = 10


def cohort_outcomes(inputs: StudyInputs, formation: int, issuers: tuple[str, ...]) -> pd.DataFrame:
    """Long quarterly excess returns of the formation cohort over its window."""
    cohorts = inputs.tables["cohorts"]
    window = inputs.spec.window(formation)
    frame = cohorts.loc[
        cohorts["formation_year"].eq(formation) & cohorts["issuer_id"].isin(issuers)
    ].copy()
    frame["quarter"] = pd.to_datetime(frame["quarter"]).dt.to_period("Q").dt.to_timestamp("Q")
    frame = frame.loc[frame["quarter"].isin(window) & frame["observed"].astype(bool)]
    factors = inputs.factors.reindex(window)
    if factors[["RF", "Mkt-RF"]].isna().any().any():
        message = f"Quarterly factors are incomplete in the {formation} window."
        raise ValueError(message)
    frame["excess"] = frame["total_return"] - frame["quarter"].map(factors["RF"])
    frame["market"] = frame["quarter"].map(factors["Mkt-RF"])
    return frame.rename(columns={"issuer_id": "ticker", "quarter": "date"})[
        ["ticker", "date", "excess", "market"]
    ].reset_index(drop=True)


def _mm(sample: pd.DataFrame, indices: pd.DataFrame | None, output: Path, tag: str) -> pd.DataFrame:
    """R robustbase MM CAPM fits; original-sample failures stay as unconverged rows."""
    with TemporaryDirectory(dir=output, prefix=".mm-") as directory:
        try:
            return robust_betas(
                sample, Path(directory), terms=("market",), indices=indices, cores=6, tag=tag
            )
        except RuntimeError as error:
            if "did not converge" not in str(error):
                raise
            return pd.read_csv(Path(directory) / f"cache/mm-{tag}-output.csv")


def _betas(estimates: pd.DataFrame, replicate: int) -> pd.Series:
    selected = estimates.loc[estimates["replicate"].eq(replicate) & estimates["term"].eq("market")]
    return selected.set_index("ticker")["estimate"].where(
        selected.set_index("ticker")["converged"].astype(bool)
    )


def _contemporaneous(
    inputs: StudyInputs, formation: int, issuers: tuple[str, ...]
) -> dict[str, Network]:
    """Her timing: histories as of each issuer's last analytical quarter in the window."""
    panel = inputs.tables["panel"]
    window = inputs.spec.window(formation)
    rows = panel.loc[
        panel["issuer_id"].isin(issuers) & pd.to_datetime(panel["quarter"]).isin(window)
    ]
    rows = (
        rows.sort_values("quarter")
        .groupby("issuer_id", sort=False)
        .tail(1)
        .set_index("issuer_id")
        .reindex(list(issuers))
        .reset_index()
    )
    distances = characteristic_distances(inputs.histories(rows))
    return {
        f"fernandez:{name}|exp@contemporaneous": Network(
            f"fernandez:{name}|exp@contemporaneous",
            "replication",
            "exp(-d), window-end histories",
            issuers,
            exponential_weights(distance),
            distance,
            neutral,
        )
        for name, (distance, neutral) in distances.items()
    }


def _var(
    beta: FloatArray, weights: FloatArray | None, estimator: str, row: dict[str, Any], market: float
) -> float:
    """Her equations (8a)/(8b) at fitted parameters: equal-weight portfolio VaR."""
    count = len(beta)
    allocation = np.full(count, 1 / count)
    spatial_value = float(row.get("spatial", 0.0)) if estimator != "ols" else 0.0
    innovation = float(row.get("sigma2", np.nan))
    if weights is None or estimator == "ols":
        exposure, filtered = allocation @ beta, allocation
    else:
        inverse_t = np.linalg.solve((np.eye(count) - spatial_value * weights).T, allocation)
        exposure = inverse_t @ beta if estimator.startswith("lag") else allocation @ beta
        filtered = inverse_t
    variance = exposure**2 * market + innovation * float(filtered @ filtered)
    return float(VAR_VALUE * norm.ppf(VAR_LEVEL) * np.sqrt(variance))


def _fit_network(
    y: FloatArray, beta: FloatArray, network: Network | None, market: float
) -> list[dict[str, Any]]:
    rows = []
    estimators = ("ols",) if network is None else ESTIMATORS
    for estimator in estimators:
        for intercept in (False, True):
            row = spatial.cross_section(
                y,
                {"beta": beta},
                None if network is None else network.weights,
                estimator,
                intercept=intercept,
            )
            if estimator == "ols" and row["status"] == "available":
                design = np.column_stack([np.ones_like(beta), beta]) if intercept else beta[:, None]
                residuals = y - design @ np.linalg.lstsq(design, y, rcond=None)[0]
                row["sigma2"] = float(residuals @ residuals / len(y))
            if estimator != "lag_iv" and row["status"] == "available":
                row["var_95"] = _var(
                    beta, None if network is None else network.weights, estimator, row, market
                )
            rows.append({"network": "none" if network is None else network.name} | row)
    return rows


def _restrict(weights: FloatArray, keep: np.ndarray) -> FloatArray:
    """Drop issuers whose draw refit failed and renormalize the fixed graph's rows."""
    selected = weights[np.ix_(keep, keep)]
    sums = selected.sum(axis=1, keepdims=True)
    return np.divide(selected, sums, out=np.zeros_like(selected), where=sums > 0)


def _refit(
    y: FloatArray, beta: FloatArray, graph: spatial_ml.Graph, *, intercept: bool
) -> dict[str, float]:
    """Fast refits of every spatial estimator on one draw (fixed graph)."""
    design = np.column_stack([np.ones_like(beta), beta]) if intercept else beta[:, None]
    result = {}
    for process in ("lag", "error"):
        coefficients, value, _ = spatial_ml.profile(y, design, graph, process)
        result[f"{process}_ml:premium"] = float(coefficients[-1])
        result[f"{process}_ml:spatial"] = value
    coefficients, value = spatial_ml.lag_iv(y, design, graph, (int(intercept),))
    result["lag_iv:premium"] = float(coefficients[-1])
    result["lag_iv:spatial"] = value
    return result


def _parity(estimates: pd.DataFrame, refits: dict[str, dict[str, float]]) -> None:
    """The resampling refits must reproduce statadic on the original sample."""
    for row in estimates.loc[estimates["status"].eq("available")].to_dict("records"):
        if row["network"] not in refits or row["estimator"] == "ols":
            continue
        fast = refits[row["network"]]
        label = "with" if row["with_intercept"] else "without"
        for name in ("premium", "spatial"):
            expected = row.get("beta" if name == "premium" else "spatial")
            observed = fast.get(f"{row['estimator']}:{name}:{label}")
            if observed is None or expected is None:
                continue
            if abs(observed - expected) > PARITY_TOLERANCE * max(1.0, abs(expected)):
                message = (
                    f"Resampling refit disagrees with statadic for {row['network']} "
                    f"{row['estimator']} {label} {name}: {observed} vs {expected}."
                )
                raise ValueError(message)


def _bootstrap(  # noqa: PLR0913 -- one formation's draws, networks and outputs.
    estimates: pd.DataFrame,
    *,
    sample: pd.DataFrame,
    window: pd.DatetimeIndex,
    issuers: tuple[str, ...],
    networks: dict[str, Network],
    inputs: StudyInputs,
    output: Path,
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Generated-regressor bootstrap: resample quarters, refit betas, medians and models."""
    spec = inputs.spec
    market = sample.drop_duplicates("date").set_index("date")["market"].reindex(window)
    block = block_length(market.to_numpy(float))
    indices = generated_beta_indices(window, spec.generated_beta_draws, block, spec.seed)
    mm = _mm(sample, indices, output, f"formation-{window[0].year - 1}-draws")
    wide = sample.pivot_table(index="date", columns="ticker", values="excess").reindex(
        index=window, columns=list(issuers)
    )
    graphs = {name: spatial_ml.Graph.of(network.weights) for name, network in networks.items()}
    original_y = wide.median(axis=0).to_numpy(float)
    original_beta = _betas(mm, 0).reindex(list(issuers)).to_numpy(float)
    originals = {
        name: {
            f"{key}:{'with' if intercept else 'without'}": value
            for intercept in (False, True)
            for key, value in _refit(original_y, original_beta, graph, intercept=intercept).items()
        }
        for name, graph in graphs.items()
    }
    _parity(estimates, originals)
    draws: list[dict[str, Any]] = []
    for replicate in range(1, spec.generated_beta_draws + 1):
        order = pd.to_datetime(
            indices.loc[indices["replicate"].eq(replicate)].sort_values("position")["quarter"]
        )
        y = wide.reindex(order).median(axis=0).to_numpy(float)
        beta = _betas(mm, replicate).reindex(list(issuers)).to_numpy(float)
        keep = np.isfinite(y) & np.isfinite(beta)
        if keep.sum() < MIN_DRAW_ISSUERS:
            draws.append({"replicate": replicate, "status": "unavailable_mm_or_median"})
            continue
        y, beta = y[keep], beta[keep]
        draws.append(
            {
                "replicate": replicate,
                "status": "available",
                "dropped_issuers": int((~keep).sum()),
                "ols:premium:without": float(np.linalg.lstsq(beta[:, None], y, rcond=None)[0][0]),
            }
        )
        for name, full in graphs.items():
            graph = (
                full if keep.all() else spatial_ml.Graph.of(_restrict(networks[name].weights, keep))
            )
            for intercept in (False, True):
                label = "with" if intercept else "without"
                for key, value in _refit(y, beta, graph, intercept=intercept).items():
                    draws[-1][f"{name}|{key}:{label}"] = value
    frame = pd.DataFrame(draws)
    intervals = []
    for column in frame.columns.drop(["replicate", "status"]):
        low, high, count = percentile_interval(frame[column].to_numpy(float))
        intervals.append({"quantity": column, "low": low, "high": high, "draws": count})
    record = {"expected_block_quarters": block, "requested_draws": spec.generated_beta_draws}
    return frame, pd.DataFrame(intervals), record


def run(panel: Path, representations: Path | None, output: Path, params: Path) -> None:
    """Estimate every formation; bootstrap the primary formation; save all tables."""
    inputs = load(panel, representations, params)
    spec = inputs.spec
    output.mkdir(parents=True, exist_ok=True)
    tables: dict[str, list[pd.DataFrame]] = {
        name: [] for name in ("estimates", "diagnostics", "networks", "roster", "mm")
    }
    manifest: dict[str, Any] = {"study_sha256": spec.digest, "formations": {}}
    for formation in spec.formation_years:
        window = spec.window(formation)
        rows = inputs.roster(window[0])
        issuers = tuple(rows["issuer_id"].astype(str))
        sample = cohort_outcomes(inputs, formation, issuers)
        counts = sample.groupby("ticker").size().reindex(list(issuers), fill_value=0)
        eligible = sample.loc[sample["ticker"].map(counts).ge(spec.min_beta_quarters)]
        mm = _mm(eligible, None, output, f"formation-{formation}")
        beta = _betas(mm, 0).reindex(list(issuers))
        median = sample.groupby("ticker")["excess"].median().reindex(list(issuers))
        available = beta.notna() & median.notna() & counts.ge(spec.min_beta_quarters)
        roster = pd.DataFrame(
            {
                "formation": formation,
                "issuer_id": issuers,
                "observed_quarters": counts.to_numpy(),
                "mm_beta": beta.to_numpy(float),
                "median_excess": median.to_numpy(float),
                "status": np.where(available, "available", "unavailable_mm_or_quarters"),
            }
        )
        tables["roster"].append(roster)
        tables["mm"].append(mm.assign(formation=formation))
        estimation = rows.loc[available.to_numpy()].reset_index(drop=True)
        selected = tuple(estimation["issuer_id"].astype(str))
        y = median.reindex(list(selected)).to_numpy(float)
        b = beta.reindex(list(selected)).to_numpy(float)
        neighbours = (
            (spec.neighbours, *spec.neighbour_sensitivities)
            if formation == spec.primary_formation
            else (spec.neighbours,)
        )
        networks = inputs.networks(window[0], estimation, neighbours) | _contemporaneous(
            inputs, formation, selected
        )
        market = float(sample.drop_duplicates("date")["market"].var(ddof=1))
        LOGGER.info(
            "Formation %s: %s of %s issuers, %s networks",
            formation,
            len(selected),
            len(issuers),
            len(networks),
        )
        estimates = [pd.DataFrame(_fit_network(y, b, None, market))]
        diagnostics = []
        for network in networks.values():
            estimates.append(pd.DataFrame(_fit_network(y, b, network, market)))
            diagnostics.append(
                {"network": network.name} | spatial.diagnostics(y, {"beta": b}, network.weights)
            )
            tables["networks"].append(pd.DataFrame([network.summary() | {"formation": formation}]))
        frame = pd.concat(estimates, ignore_index=True).assign(formation=formation)
        tables["estimates"].append(frame)
        tables["diagnostics"].append(pd.DataFrame(diagnostics).assign(formation=formation))
        record: dict[str, Any] = {
            "window": [str(window[0].date()), str(window[-1].date())],
            "roster": len(issuers),
            "estimation_issuers": len(selected),
            "networks": sorted(networks),
            "market_variance": market,
        }
        if formation == spec.primary_formation and spec.generated_beta_draws:
            primary = {
                name: network
                for name, network in networks.items()
                if "@contemporaneous" not in name
            }
            draws, intervals, details = _bootstrap(
                frame,
                sample=eligible.loc[eligible["ticker"].isin(selected)],
                window=window,
                issuers=selected,
                networks=primary,
                inputs=inputs,
                output=output,
            )
            atomic_parquet(output / "draws.parquet", draws)
            atomic_parquet(output / "intervals.parquet", intervals)
            record["bootstrap"] = details
        manifest["formations"][str(formation)] = record
    for name, pieces in tables.items():
        atomic_parquet(output / f"{name}.parquet", pd.concat(pieces, ignore_index=True))
    manifest["characteristics"] = list(CHARACTERISTICS)
    write_json(output / "manifest.json", json.loads(json.dumps(manifest, default=str)))
