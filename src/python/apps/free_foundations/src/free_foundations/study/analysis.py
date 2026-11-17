"""Matched quarterly Fernández exercises and separate past-only risk forecasts.

The descriptive CAPM-MM exercise deliberately uses the full feature-era panel.
Its estimates never enter a forecast: those use only the preceding twenty quarters.
No estimator changes the master roster or its observed-return mask.
"""

# Pivot must reject duplicate keys and preserve all-missing rows, without aggregation.
# ruff: noqa: PD010

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
import pandas as pd
from scipy.linalg import cho_factor, cho_solve
from scipy.spatial.distance import cdist
from sklearn.linear_model import Ridge, RidgeCV
from sklearn.preprocessing import StandardScaler

from free_foundations.data import write_json
from free_foundations.fernandez.diagnostics import information_criteria, residual_moran
from free_foundations.fernandez.evaluation import SCRIPT as MM_SCRIPT
from free_foundations.fernandez.evaluation import robust_betas
from free_foundations.fernandez.kernels import effective_neighbours, kernel_weights
from free_foundations.fernandez.models import (
    error_ml,
    lag_iv,
    maximize_profile,
    ols,
    symmetric_spectrum,
)
from free_foundations.panel.decoding import ALPHAS, folds
from free_foundations.panel.geometry import pcoa
from free_foundations.study.history import annual_history_slots
from free_foundations.study.inference import (
    generated_beta_indices,
    paired_intervals,
    summarize_generated,
)
from free_foundations.study.moments import (
    PairwiseMoments,
    exponential_weights,
    identity_shrink,
    pairwise_covariance,
    pairwise_spearman,
)
from free_foundations.study.source_io import atomic_copy, atomic_csv, atomic_output, atomic_parquet
from free_foundations.study.spec import (
    CHARACTERISTICS,
    StudySpec,
    digest_json,
    file_hash,
    frame_digest,
    panel_contract,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from numpy.typing import NDArray

FACTOR_NAMES = ("Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom")
ESTIMATORS = ("ols", "spatial_lag_iv", "spatial_error_ml")
COVARIANCE_ARMS = ("spatial", "spatial_matched", "gram")
CONTROL_MODELS = ("direct", "pca16", "supervised_mlp16")


def _quarter(values: object) -> pd.Timestamp:
    return pd.Period(str(values), freq="Q").end_time.normalize()


def validate_panel(panel: pd.DataFrame) -> pd.DataFrame:
    """Reject duplicate keys, ambiguous dates and changes to the observed-return mask."""
    required = {"issuer_id", "quarter", "total_return", "observed"}
    if not required.issubset(panel):
        msg = f"Master panel lacks {sorted(required - set(panel.columns))}."
        raise ValueError(msg)
    result = panel.copy()
    result["issuer_id"] = result["issuer_id"].astype(str)
    result["quarter"] = pd.to_datetime(result["quarter"])
    canonical = result["quarter"].dt.to_period("Q").dt.to_timestamp("Q")
    if not result["quarter"].eq(canonical).all():
        msg = "Master dates must be calendar quarter ends."
        raise ValueError(msg)
    if result.duplicated(["issuer_id", "quarter"]).any():
        msg = "Duplicate master issuer-quarter keys."
        raise ValueError(msg)
    if result["observed"].isna().any() or not result["observed"].isin([True, False]).all():
        msg = "Observed flags must be explicit booleans."
        raise ValueError(msg)
    result["observed"] = result["observed"].astype(bool)
    values = pd.to_numeric(result["total_return"], errors="raise").to_numpy(float)
    if np.isinf(values).any() or not np.array_equal(np.isfinite(values), result["observed"]):
        msg = "Observed flags and finite total returns disagree."
        raise ValueError(msg)
    return result


def _characteristics(frame: pd.DataFrame) -> pd.DataFrame:
    """Accept the SEC agent's audited long table or its lossless wide pivot."""
    result = frame.copy()
    if result.empty:
        return pd.DataFrame(columns=["issuer_id", "quarter", *CHARACTERISTICS]).astype(
            {"quarter": "datetime64[ns]"}
        )
    if "cutoff" in result:
        cutoff = pd.to_datetime(result["cutoff"], utc=True)
        start = (
            pd.to_datetime(result["quarter"]).dt.to_period("Q").dt.start_time.dt.tz_localize("UTC")
        )
        if (cutoff.notna() & cutoff.ge(start)).any():
            message = "Characteristic information cutoff reaches the forecast quarter."
            raise ValueError(message)
    if {"characteristic", "value"}.issubset(result):
        if result.duplicated(["issuer_id", "quarter", "characteristic"]).any():
            msg = "Duplicate characteristic observations."
            raise ValueError(msg)
        result = result.pivot(
            index=["issuer_id", "quarter"], columns="characteristic", values="value"
        ).reset_index()
    if not {"issuer_id", "quarter"}.issubset(result):
        msg = "Characteristics need issuer_id and quarter columns."
        raise ValueError(msg)
    result["issuer_id"] = result["issuer_id"].astype(str)
    result["quarter"] = pd.to_datetime(result["quarter"])
    if result.duplicated(["issuer_id", "quarter"]).any():
        msg = "Duplicate characteristic issuer-quarter keys."
        raise ValueError(msg)
    for name in CHARACTERISTICS:
        if name not in result:
            result[name] = np.nan
    return result


@dataclass(frozen=True)
class Geometry:
    """One geometry on exactly the ordered master roster."""

    distance: NDArray[np.float64]
    weights: NDArray[np.float64]
    gram: NDArray[np.float64]
    delta: float
    undefined_pairs: int
    bandwidth: float = 1.0
    spatial_metric: str = "raw_characteristic_distance"
    matched_weights: NDArray[np.float64] | None = None
    matched_bandwidth: float = float("nan")
    matched_target: float = float("nan")
    overlap_counts: NDArray[np.int64] | None = None
    overlap_defined: NDArray[np.bool_] | None = None
    raw_correlation: NDArray[np.float64] | None = None


def match_gram_geometry(geometry: Geometry, target: float) -> Geometry:
    """Derive a spatial kernel from exactly the Gram arm's repaired unit geometry.

    Original/native spatial weights remain separate. Matching the mean effective
    neighbour count uses only geometry, never return outcomes. Tied distances can
    make a target unattainable; the achieved count and gap remain in the audit.
    """
    distance = np.sqrt(np.maximum(2 * (1 - geometry.gram), 0))
    np.fill_diagonal(distance, 0)
    if len(distance) > 1:
        weights, bandwidth = kernel_weights(distance, "matched", target=target)
    else:
        weights, bandwidth = np.zeros_like(distance), 1.0
    return replace(
        geometry,
        matched_weights=weights,
        matched_bandwidth=bandwidth,
        matched_target=target,
    )


def _spatial_weights(geometry: Geometry, arm: str) -> NDArray[np.float64]:
    weights = geometry.weights if arm == "spatial" else geometry.matched_weights
    if weights is None:
        message = "Matched spatial weights were not constructed."
        raise ValueError(message)
    return weights


def fernandez_geometries(
    characteristics: pd.DataFrame,
    issuers: tuple[str, ...],
    quarter: object,
    spec: StudySpec,
) -> dict[str, Geometry]:
    """Annual-spaced pairwise Spearman histories and neutral unidentified links.

    Input quarter labels denote already available snapshots for that forecast
    quarter. The original spatial W uses the unshrunk neutral-completed distance;
    identity shrinkage belongs exclusively to the separate Gram covariance arm.
    """
    frame = _characteristics(characteristics)
    end = _quarter(quarter)
    queries = pd.DataFrame({"issuer_id": issuers, "quarter": end})
    slots = annual_history_slots(
        queries,
        frame.set_index(["issuer_id", "quarter"]),
        years=spec.characteristic_history_years,
    )
    result: dict[str, Geometry] = {}
    for name in CHARACTERISTICS:
        history = slots[
            [f"original:{name}:annual_lag{lag}" for lag in range(spec.characteristic_history_years)]
        ]
        moments = pairwise_spearman(history, min_eigenvalue=spec.min_eigenvalue)
        raw = np.asarray(moments.raw, dtype=float)
        distance = np.sqrt(np.maximum(2 * (1 - raw), 0))
        np.fill_diagonal(distance, 0)
        undefined = ~np.asarray(moments.defined, dtype=bool)
        np.fill_diagonal(undefined, val=False)
        result[f"fernandez_{name}"] = Geometry(
            distance,
            exponential_weights(distance),
            np.asarray(moments.correlation),
            float(moments.delta),
            int(np.triu(undefined, 1).sum()),
            overlap_counts=np.asarray(moments.counts),
            overlap_defined=np.asarray(moments.defined),
            raw_correlation=raw,
        )
    distances = np.sqrt(np.mean([item.distance**2 for item in result.values()], axis=0))
    joint_raw = np.mean([1 - item.distance**2 / 2 for item in result.values()], axis=0)
    joint, delta = identity_shrink(joint_raw, spec.min_eigenvalue)
    result["fernandez_joint"] = Geometry(
        distances,
        exponential_weights(distances),
        joint,
        delta,
        sum(item.undefined_pairs for item in result.values()),
        raw_correlation=joint_raw,
    )
    uniform = np.ones((len(issuers), len(issuers))) - np.eye(len(issuers))
    if len(issuers) > 1:
        uniform /= len(issuers) - 1
    result["uniform_network"] = Geometry(
        np.zeros_like(uniform),
        uniform,
        np.eye(len(issuers)),
        0,
        0,
        spatial_metric="uniform_network",
    )
    return result


def _native_geometry(values: NDArray[np.float64], reference: Geometry, spec: StudySpec) -> Geometry:
    distances = cdist(values, values)
    if len(values) > 1:
        target = effective_neighbours(reference.weights)
        weights, bandwidth = kernel_weights(distances, "matched", target=target)
    else:
        weights, bandwidth = np.zeros((len(values), len(values))), 1.0
    largest = np.max(np.abs(values), axis=1)
    normalized = np.divide(
        values, largest[:, None], out=np.zeros_like(values), where=largest[:, None] > 0
    )
    norms = np.linalg.norm(normalized, axis=1)
    normalized = np.divide(
        normalized, norms[:, None], out=np.zeros_like(values), where=norms[:, None] > 0
    )
    raw = normalized @ normalized.T
    np.fill_diagonal(raw, 1)
    gram, delta = identity_shrink(raw, spec.min_eigenvalue)
    missing = int(np.sum(norms == 0))
    undefined_pairs = missing * (len(values) - missing) + missing * (missing - 1) // 2
    return Geometry(
        distances,
        weights,
        gram,
        delta,
        undefined_pairs,
        bandwidth,
        spatial_metric="native_euclidean",
    )


def _representation_arrays(  # noqa: C901 -- recursive array and provenance payload adapter.
    representations: Mapping[object, object],
    quarter: pd.Timestamp,
    issuers: tuple[str, ...],
    contract: dict[str, Any],
) -> dict[str, NDArray[np.float64]]:
    candidates = [value for key, value in representations.items() if _quarter(key) == quarter]
    if len(candidates) > 1:
        msg = "Duplicate representation quarter keys."
        raise ValueError(msg)
    if not candidates:
        return {}
    result: dict[str, NDArray[np.float64]] = {}

    def visit(name: str, value: object) -> None:
        if isinstance(value, dict) and "values" not in value:
            for child, payload in value.items():
                visit(f"{name}/{child}" if name else str(child), payload)
            return
        if isinstance(value, dict):
            labels = tuple(map(str, value.get("issuer_ids", issuers)))
            if labels != issuers:
                msg = "Representation row IDs differ from the ordered master roster."
                raise ValueError(msg)
            if value.get("master_digest", contract["panel_sha256"]) != contract["panel_sha256"]:
                msg = "Representation belongs to a different master panel."
                raise ValueError(msg)
            value = value["values"]
        if isinstance(value, pd.DataFrame):
            if tuple(map(str, value.index)) != issuers:
                msg = "Representation dataframe rows differ from the master roster."
                raise ValueError(msg)
            value = value.to_numpy(float)
        array = np.asarray(value, dtype=float)
        if array.ndim != 2 or array.shape[0] != len(issuers) or array.shape[1] == 0:
            msg = "Representation shape differs from the master roster."
            raise ValueError(msg)
        if not np.isfinite(array).all():
            msg = "Native readouts must be finite; missing inputs belong in adapters."
            raise ValueError(msg)
        result[name] = array

    visit("", candidates[0])
    return result


def _factors(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    if result.empty:
        return pd.DataFrame(
            columns=["RF", *FACTOR_NAMES], index=pd.DatetimeIndex([], name="quarter")
        )
    if "quarter" not in result:
        result = result.rename_axis("quarter").reset_index()
    required = {"quarter", "RF", *FACTOR_NAMES}
    if not required.issubset(result):
        msg = f"Quarterly factors lack {sorted(required - set(result.columns))}."
        raise ValueError(msg)
    result["quarter"] = pd.to_datetime(result["quarter"])
    if result["quarter"].duplicated().any():
        msg = "Duplicate quarterly factor observations."
        raise ValueError(msg)
    return result.set_index("quarter").sort_index()


def _positive_variances(
    values: NDArray[np.float64], floor: float
) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    counts = np.isfinite(values).sum(axis=0)
    variances = np.full(values.shape[1], np.nan)
    for column in range(values.shape[1]):
        observed = values[np.isfinite(values[:, column]), column]
        if len(observed) > 1:
            variances[column] = np.var(observed, ddof=1)
    positive = variances[np.isfinite(variances) & (variances > 0)]
    prior = float(np.median(positive)) if len(positive) else floor
    missing = counts < 2
    return np.maximum(np.where(missing, prior, variances), floor), missing


def positive_covariance(
    values: NDArray[np.float64],
    floor: float = 1e-6,
    *,
    audit: dict[str, NDArray[Any]] | None = None,
    prefix: str = "returns",
) -> tuple[NDArray[np.float64], float]:
    """Pairwise moments plus declared identity correlation shrinkage; no outcome filling."""
    moments = pairwise_covariance(values, min_eigenvalue=floor)
    if audit is not None:
        audit.update(_moment_audit(moments, prefix))
    variances, _ = _positive_variances(values, floor)
    return np.asarray(moments.correlation) * np.sqrt(np.outer(variances, variances)), float(
        moments.delta
    )


def _moment_audit(moments: PairwiseMoments, prefix: str) -> dict[str, NDArray[Any]]:
    payload = {
        f"{prefix}__counts": np.asarray(moments.counts, dtype=np.int32),
        f"{prefix}__correlation_defined": np.asarray(moments.defined),
        f"{prefix}__raw_correlation": np.asarray(moments.raw),
        f"{prefix}__repaired_correlation": np.asarray(moments.correlation),
        f"{prefix}__identity_shrink": np.asarray(moments.delta),
    }
    if moments.covariance is not None:
        payload[f"{prefix}__raw_covariance"] = np.asarray(moments.covariance)
    if moments.covariance_defined is not None:
        payload[f"{prefix}__covariance_defined"] = np.asarray(moments.covariance_defined)
    return payload


def _save_pairwise_audit(  # noqa: PLR0913 -- one quarter's ordered inputs and exact moments.
    output: Path,
    quarter: pd.Timestamp,
    issuers: tuple[str, ...],
    geometries: dict[str, Geometry],
    *,
    payload: dict[str, NDArray[Any]],
    spec: StudySpec,
) -> dict[str, object]:
    """Archive exact arrays without rounding or retaining another quarter in memory."""
    folder = output / "pairwise"
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"{quarter.date()}.npz"
    arrays: dict[str, NDArray[Any]] = {"issuer_ids": np.asarray(issuers), **payload}
    for name in (*[f"fernandez_{item}" for item in CHARACTERISTICS], "fernandez_joint"):
        geometry = geometries[name]
        arrays |= {
            f"{name}__raw_distance": geometry.distance,
            f"{name}__raw_weights": geometry.weights,
            f"{name}__repaired_gram": geometry.gram,
            f"{name}__identity_shrink": np.asarray(geometry.delta),
        }
        if geometry.raw_correlation is not None:
            arrays[f"{name}__raw_correlation"] = geometry.raw_correlation
        if geometry.overlap_counts is not None:
            arrays[f"{name}__counts"] = geometry.overlap_counts.astype(np.int32)
        if geometry.overlap_defined is not None:
            arrays[f"{name}__defined"] = geometry.overlap_defined
        if geometry.matched_weights is not None:
            arrays[f"{name}__matched_weights"] = geometry.matched_weights
            arrays[f"{name}__matched_bandwidth"] = np.asarray(geometry.matched_bandwidth)
    with atomic_output(destination) as temporary, temporary.open("wb") as stream:
        np.savez_compressed(stream, allow_pickle=False, **arrays)
    record: dict[str, object] = {
        "quarter": str(quarter.date()),
        "file": str(destination.relative_to(output)),
        "sha256": file_hash(destination),
        "issuer_ids": list(issuers),
        "arrays": {
            name: {"shape": list(value.shape), "dtype": str(value.dtype)}
            for name, value in arrays.items()
        },
        "kernel": "zero diagonal exp(-distance/bandwidth), row normalized",
        "raw_characteristic_bandwidth": 1.0,
        "minimum_correlation_eigenvalue": spec.min_eigenvalue,
        "analysis_source_sha256": file_hash(Path(__file__)),
        "moments_source_sha256": file_hash(Path(__file__).with_name("moments.py")),
        "history_source_sha256": file_hash(Path(__file__).with_name("history.py")),
        "interpretation": "exact float64 computations; undefined pairs retain their flags",
    }
    write_json(destination.with_suffix(".json"), record)
    return record


def gaussian_observed(
    values: NDArray[np.float64],
    covariance: NDArray[np.float64],
    observed: NDArray[np.bool_] | None = None,
) -> tuple[float, int]:
    """Proper Gaussian marginal density of exactly the observed issuer subvector."""
    values = np.asarray(values, dtype=float)
    mask = np.isfinite(values) if observed is None else np.asarray(observed, dtype=bool)
    if mask.shape != values.shape or not np.array_equal(mask, np.isfinite(values)):
        msg = "Gaussian outcome values and observed mask disagree."
        raise ValueError(msg)
    if covariance.shape != (len(values), len(values)) or not np.isfinite(covariance).all():
        msg = "Covariance must match the full finite master roster."
        raise ValueError(msg)
    if not np.allclose(covariance, covariance.T, atol=1e-10):
        msg = "Covariance must be symmetric."
        raise ValueError(msg)
    count = int(mask.sum())
    if not count:
        return float("nan"), 0
    marginal = covariance[np.ix_(mask, mask)]
    factor = cho_factor(marginal, lower=True, check_finite=True)
    selected = values[mask]
    logdet = 2 * np.log(np.diag(factor[0])).sum()
    score = -0.5 * (count * np.log(2 * np.pi) + logdet + selected @ cho_solve(factor, selected))
    return float(score), count


@dataclass(frozen=True)
class ExposureFit:
    """Named published-factor exposure proxies, with individual availability statuses."""

    beta: NDArray[np.float64]
    residuals: NDArray[np.float64]
    factor_covariance: NDArray[np.float64]
    counts: NDArray[np.int64]
    statuses: tuple[str, ...]
    alphas: NDArray[np.float64]


def estimate_exposures(
    returns: NDArray[np.float64], factors: NDArray[np.float64], spec: StudySpec
) -> ExposureFit:
    """Fit ridge FF5+Mom proxies using each issuer's available past observations only."""
    returns, factors = np.asarray(returns, float), np.asarray(factors, float)
    if factors.shape != (len(returns), len(FACTOR_NAMES)):
        msg = "Exposure factors must have six named columns on the prior calendar."
        raise ValueError(msg)
    beta = np.full((returns.shape[1], len(FACTOR_NAMES)), np.nan)
    residuals = np.full_like(returns, np.nan)
    alphas = np.full(returns.shape[1], np.nan)
    counts = np.zeros(returns.shape[1], dtype=np.int64)
    statuses: list[str] = []
    for column in range(returns.shape[1]):
        mask = np.isfinite(returns[:, column]) & np.isfinite(factors).all(axis=1)
        count = int(mask.sum())
        counts[column] = count
        if not count:
            statuses.append("unavailable_no_factor_return_overlap")
            continue
        scaler = StandardScaler().fit(factors[mask])
        design = scaler.transform(factors[mask])
        model = RidgeCV(alphas=ALPHAS) if count > 1 else Ridge(alpha=float(ALPHAS[-1]))
        model.fit(design, returns[mask, column])
        beta[column] = np.asarray(model.coef_, dtype=float) / scaler.scale_
        residuals[mask, column] = returns[mask, column] - model.predict(design)
        alphas[column] = float(model.alpha_ if isinstance(model, RidgeCV) else ALPHAS[-1])
        rank = np.linalg.matrix_rank(np.column_stack([np.ones(count), factors[mask]]))
        statuses.append("regularized_proxy" if rank == 7 else "regularized_rank_deficient_proxy")
    factor_covariance, _ = positive_covariance(factors, spec.min_eigenvalue)
    return ExposureFit(beta, residuals, factor_covariance, counts, tuple(statuses), alphas)


def spatial_training_score(
    residuals: NDArray[np.float64],
    weights: NDArray[np.float64],
    variances: NDArray[np.float64],
    intensity: float,
) -> float:
    """Independent marginal-density reference, useful for checking the fast objective."""
    inverse = np.linalg.solve(np.eye(len(weights)) - intensity * weights, np.eye(len(weights)))
    covariance = (inverse * variances) @ inverse.T
    return sum(gaussian_observed(row, covariance)[0] for row in residuals if np.isfinite(row).any())


def fit_spatial(
    residuals: NDArray[np.float64],
    weights: NDArray[np.float64],
    variances: NDArray[np.float64],
) -> tuple[float, float]:
    """Fit one spatial coefficient by exact observed-subvector Gaussian likelihood.

    The precision Schur complement integrates unobserved returns. Internal zero
    coordinates merely embed the observed vector for this algebra; they are not
    imputed observations or scored zero returns. Innovation scales are fixed from
    the same prior window, rather than profiled using nonexistent complete rows.
    """
    if not np.isfinite(residuals).any():
        msg = "Spatial calibration has no observed prior residuals."
        raise ValueError(msg)
    spectrum = symmetric_spectrum(weights)
    complete = np.isfinite(residuals).all()
    if complete:
        lagged = residuals @ weights.T
        constant = residuals.size * np.log(2 * np.pi) + len(residuals) * np.log(variances).sum()

        def objective(value: float) -> float:
            jacobian = len(residuals) * np.log(np.abs(1 - value * spectrum)).sum()
            energy = np.sum((residuals - value * lagged) ** 2 / variances)
            return float(jacobian - 0.5 * (constant + energy))
    else:
        inverse_variance = 1 / variances
        linear = weights / variances[:, None] + weights.T / variances[None, :]
        quadratic = weights.T @ (weights / variances[:, None])
        patterns = []
        for row in residuals:
            observed = np.isfinite(row)
            if not observed.any():
                continue
            missing = ~observed
            full = np.where(observed, row, 0.0)
            patterns.append((int(observed.sum()), missing, full, weights @ full))

        def objective(value: float) -> float:
            logdet_precision = (
                2 * np.log(np.abs(1 - value * spectrum)).sum() - np.log(variances).sum()
            )
            total = 0.0
            for count, missing, full, lagged in patterns:
                filtered = full - value * lagged
                scaled = filtered * inverse_variance
                energy = float(filtered @ scaled)
                logdet_missing = 0.0
                if missing.any():
                    sub = np.ix_(missing, missing)
                    precision = (
                        np.diag(inverse_variance[missing])
                        - value * linear[sub]
                        + value**2 * quadratic[sub]
                    )
                    factor = cho_factor(precision, lower=True)
                    cross = (scaled - value * (weights.T @ scaled))[missing]
                    energy -= float(cross @ cho_solve(factor, cross))
                    logdet_missing = float(2 * np.log(np.diag(factor[0])).sum())
                total += 0.5 * (
                    logdet_precision - logdet_missing - count * np.log(2 * np.pi) - energy
                )
            return float(total)

    zero = objective(0)
    if max(abs(objective(-0.5) - zero), abs(objective(0.5) - zero)) < 1e-10:
        return 0.0, zero
    value, score = maximize_profile(objective, points=21, xatol=1e-6)
    candidates = [(value, score), (0.0, zero), (-0.99, objective(-0.99)), (0.99, objective(0.99))]
    return max(candidates, key=lambda item: item[1])


def fit_gram(
    residuals: NDArray[np.float64],
    gram: NDArray[np.float64],
    variances: NDArray[np.float64],
    floor: float,
) -> tuple[float, float]:
    """Fit direct signed-Gram dependence with exact unbalanced Gaussian marginals."""
    patterns: dict[bytes, list[int]] = {}
    for index, row in enumerate(residuals):
        mask = np.isfinite(row)
        if mask.any():
            patterns.setdefault(mask.tobytes(), []).append(index)
    if not patterns:
        msg = "Gram calibration has no observed prior residuals."
        raise ValueError(msg)
    sufficient = []
    for indices in patterns.values():
        mask = np.isfinite(residuals[indices[0]])
        eigenvalues, vectors = np.linalg.eigh(gram[np.ix_(mask, mask)])
        standardized = residuals[np.ix_(indices, mask)] / np.sqrt(variances[mask])
        energy = np.sum((standardized @ vectors) ** 2, axis=0)
        constant = len(indices) * (
            int(mask.sum()) * np.log(2 * np.pi) + np.log(variances[mask]).sum()
        )
        sufficient.append((len(indices), eigenvalues, energy, constant))

    def objective(value: float) -> float:
        result = 0.0
        for count, eigenvalues, energy, constant in sufficient:
            diagonal = 1 - value + value * eigenvalues
            result -= 0.5 * (constant + count * np.log(diagonal).sum() + np.sum(energy / diagonal))
        return float(result)

    zero = objective(0)
    if abs(objective(0.5) - zero) < 1e-10:
        return 0.0, zero
    value, score = maximize_profile(objective, bounds=(0, 1 - floor), points=21, xatol=1e-6)
    return max(
        [(value, score), (0.0, zero), (1 - floor, objective(1 - floor))], key=lambda item: item[1]
    )


def _decoded_states(
    values: NDArray[np.float64], beta: NDArray[np.float64], issuers: tuple[str, ...]
) -> tuple[NDArray[np.float64], float]:
    """Cross-fit on issuer identities, retaining queries whose own labels are missing."""
    predictions = np.full_like(beta, np.nan)
    labels = folds(issuers)
    finite = np.isfinite(beta).all(axis=1)
    for fold in np.unique(labels):
        test = labels == fold
        train = (labels != fold) & finite
        if not train.any():
            continue
        scaler = StandardScaler().fit(values[train])
        design = scaler.transform(values[train])
        held = np.clip(scaler.transform(values[test]), design.min(axis=0), design.max(axis=0))
        model = RidgeCV(alphas=ALPHAS) if train.sum() > 1 else Ridge(alpha=float(ALPHAS[-1]))
        model.fit(design, beta[train])
        predictions[test] = np.clip(
            model.predict(held), beta[train].min(axis=0), beta[train].max(axis=0)
        )
    evaluated = finite & np.isfinite(predictions).all(axis=1)
    total = (
        np.sum((beta[evaluated] - beta[evaluated].mean(axis=0)) ** 2) if evaluated.any() else 0.0
    )
    r2 = (
        1 - float(np.sum((beta[evaluated] - predictions[evaluated]) ** 2) / total)
        if total > 0
        else float("nan")
    )
    return predictions, r2


def _mm_estimates(
    sample: pd.DataFrame, calendar: pd.DatetimeIndex, spec: StudySpec, output: Path
) -> pd.DataFrame:
    """Reuse genuine R MM fits and retain nonconvergence rather than substitute OLS."""
    if sample.empty or not sample[["excess", "market"]].notna().all(axis=1).any():
        return pd.DataFrame(columns=["replicate", "ticker", "term", "estimate", "converged"])
    destination = output / "mm"
    destination.mkdir(parents=True, exist_ok=True)
    runtime_root = next(
        (
            parent
            for parent in Path(__file__).resolve().parents
            if (parent / "devenv.lock").is_file()
        ),
        None,
    )
    identity = {
        "sample": frame_digest(sample),
        "study": spec.digest,
        "quarters": calendar.astype(str).tolist(),
        "backend": "robustbase",
        "r_script_sha256": file_hash(MM_SCRIPT),
        "wrapper_sha256": file_hash(Path(__file__).parents[1] / "fernandez/evaluation.py"),
        "runtime_configuration": {
            name: file_hash(runtime_root / name)
            for name in ("devenv.nix", "devenv.lock")
            if runtime_root is not None and (runtime_root / name).is_file()
        },
    }
    record, saved = destination / "identity.json", destination / "estimates.parquet"
    if record.exists() and saved.exists() and json.loads(record.read_text()) == identity:
        return pd.read_parquet(saved)
    indices = generated_beta_indices(calendar, spec.generated_beta_draws, 4, spec.seed)
    # The legacy Python/R wrapper writes several files directly. Give it fresh
    # inodes, then replace completed artifacts instead of touching DVC cache links.
    with TemporaryDirectory(dir=destination, prefix=".mm-refit-") as directory:
        working = Path(directory)
        try:
            estimates = robust_betas(
                sample,
                working,
                terms=("market",),
                indices=indices,
                cores=6,
                tag="study-capm",
                backend="robustbase",
            )
        except RuntimeError as error:
            # The old wrapper raises after saving all rows if an original fit fails.
            # Preserve those statuses; runtime/backend failures still propagate.
            if "At least one robust MM fit on the original sample did not converge" not in str(
                error
            ):
                raise
            estimates = pd.read_csv(working / "cache/mm-study-capm-output.csv")
        for artifact in sorted(working.rglob("*")):
            if artifact.is_file():
                atomic_copy(destination / artifact.relative_to(working), artifact)
    atomic_parquet(destination / "indices.parquet", indices)
    atomic_parquet(saved, estimates)
    write_json(record, identity)
    return estimates


def _core_fit(  # noqa: PLR0913 -- fixed sample and estimator options.
    y: NDArray[np.float64],
    beta: NDArray[np.float64],
    weights: NDArray[np.float64],
    estimator: str,
    spectrum: NDArray[np.float64] | None = None,
    *,
    standard_errors: bool = True,
) -> dict[str, object]:
    base: dict[str, object] = {
        "estimator": estimator,
        "firms": len(y),
        "status": "unavailable",
        "reason": "",
        "premium_market": np.nan,
        "intensity": np.nan,
    }
    if not np.isfinite(y).all() or not np.isfinite(beta).all():
        return base | {"reason": "undefined MM exposure or median on unchanged roster"}
    x = beta[:, None]
    if len(y) <= 1 or np.linalg.matrix_rank(x) < 1:
        return base | {"reason": "cross-section not identified on unchanged roster"}
    try:
        if estimator == "ols":
            fitted = ols(y, x)
        elif estimator == "spatial_lag_iv":
            fitted = lag_iv(
                y,
                x,
                weights,
                standard_errors=standard_errors,
                reduced_mean=standard_errors,
            )
        else:
            fitted = error_ml(y, x, weights, eigenvalues=spectrum, standard_errors=standard_errors)
        if (
            not np.isfinite(fitted.premiums).all()
            or not np.isfinite(fitted.variance)
            or fitted.variance <= 0
        ):
            return base | {"reason": "degenerate fitted cross-section"}
        row = base | {
            "status": "available",
            "premium_market": fitted.premium,
            "intensity": fitted.intensity,
            "innovation_variance": fitted.variance,
            "premium_se": float(fitted.standard_errors[0]),
            "intensity_se": float(fitted.standard_errors[-1]),
            "log_likelihood": fitted.log_likelihood,
            "inference": "conditional in-sample; no second-stage intercept",
        }
        if fitted.log_likelihood is not None and fitted.parameters is not None:
            row |= information_criteria(fitted.log_likelihood, fitted.parameters, len(y))
        if (
            standard_errors
            and estimator == "ols"
            and np.sum(weights) > 0
            and fitted.innovations @ fitted.innovations > 0
        ):
            moran = residual_moran(fitted.innovations, x, weights)
            row |= {"moran_i": moran.statistic, "moran_p": moran.p_value}
    except (ValueError, np.linalg.LinAlgError, FloatingPointError, RuntimeError) as error:
        return base | {"reason": str(error)}
    else:
        return row


def _history_window(
    panel: pd.DataFrame,
    history: pd.DataFrame | None,
    quarter: pd.Timestamp,
    issuers: tuple[str, ...],
    spec: StudySpec,
) -> tuple[NDArray[np.float64], pd.DatetimeIndex]:
    prior = pd.period_range(
        end=quarter.to_period("Q") - 1, periods=spec.return_lookback_quarters, freq="Q"
    ).to_timestamp("Q")
    source = panel if history is None else history
    source = source.copy()
    source["quarter"] = pd.to_datetime(source["quarter"])
    if history is not None:
        year_key = next(
            (name for name in ("asof_year", "formation_year", "effective_year") if name in source),
            None,
        )
        if year_key is None:
            msg = "Warmup histories need an explicit annual formation year."
            raise ValueError(msg)
        source = source.loc[source[year_key].eq(quarter.year)]
    source = source.loc[source["quarter"].isin(prior) & source["issuer_id"].isin(issuers)]
    if source.duplicated(["quarter", "issuer_id"]).any():
        msg = "Duplicate formation-specific historical portfolio observations."
        raise ValueError(msg)
    if not np.array_equal(
        np.isfinite(source["total_return"].to_numpy(float)), source["observed"].to_numpy(bool)
    ):
        msg = "Historical observed flags and returns disagree."
        raise ValueError(msg)
    values = source.pivot(index="quarter", columns="issuer_id", values="total_return").reindex(
        index=prior, columns=issuers
    )
    return values.to_numpy(float), prior


def _geometry_tables(
    geometry: Geometry,
    quarter: pd.Timestamp,
    method: str,
    issuers: tuple[str, ...],
    outcome: NDArray[np.float64],
) -> tuple[
    dict[str, object], list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]
]:
    principal = pcoa(geometry.gram, tickers=issuers)
    achieved = (
        effective_neighbours(geometry.matched_weights)
        if geometry.matched_weights is not None and len(issuers) > 1
        else 0.0
    )
    audit: dict[str, object] = {
        "quarter": quarter,
        "method": method,
        "firms": len(issuers),
        "undefined_pairs": geometry.undefined_pairs,
        "identity_shrink": geometry.delta,
        "bandwidth": geometry.bandwidth,
        "spatial_metric": geometry.spatial_metric,
        "matched_spatial_metric": "repaired_gram_unit_chord",
        "matched_bandwidth": geometry.matched_bandwidth,
        "matched_target_neighbours": geometry.matched_target,
        "matched_effective_neighbours": achieved,
        "matched_neighbour_gap": achieved - geometry.matched_target,
        "matched_concentration_status": (
            "matched"
            if abs(achieved - geometry.matched_target) < 1e-7
            else "nearest_attainable_endpoint"
        ),
        "effective_neighbours": effective_neighbours(geometry.weights) if len(issuers) > 1 else 0.0,
        "positive_rank": principal.rank,
        "retained_components": principal.components,
        "cutoff_tied": principal.cutoff_tied,
        "cutoff_near_tied": principal.cutoff_near_tied,
        "interpretation": "quarter-specific descriptive coordinates; axes not pooled over time",
    }
    coordinates: list[dict[str, object]] = [
        {
            "quarter": quarter,
            "method": method,
            "issuer_id": issuer,
            "component": axis + 1,
            "coordinate": float(principal.coordinates[index, axis]),
            "portfolio_weight": float(principal.weights[index, axis]),
        }
        for index, issuer in enumerate(issuers)
        for axis in range(principal.components)
    ]
    spectrum: list[dict[str, object]] = [
        {"quarter": quarter, "method": method, "component": axis + 1, "eigenvalue": float(value)}
        for axis, value in enumerate(principal.eigenvalues)
    ]
    portfolios: list[dict[str, object]] = []
    for axis in range(principal.components):
        weights = principal.weights[:, axis]
        required = np.abs(weights) > 0
        available = np.isfinite(outcome[required]).all()
        portfolios.append(
            {
                "quarter": quarter,
                "method": method,
                "component": axis + 1,
                "excess_return": float(weights[required] @ outcome[required])
                if available
                else np.nan,
                "gross_weight": float(np.sum(np.abs(weights))),
                "net_weight": float(np.sum(weights)),
                "status": "available" if available else "unavailable_missing_constituent_return",
            }
        )
    return audit, coordinates, spectrum, portfolios


def _forecast_covariances(
    prior: NDArray[np.float64],
    fit: ExposureFit,
    geometries: dict[str, Geometry],
    spec: StudySpec,
    *,
    pairwise_audit: dict[str, NDArray[Any]] | None = None,
) -> tuple[dict[str, NDArray[np.float64]], list[dict[str, object]], NDArray[np.float64]]:
    raw_variance, raw_fallback = _positive_variances(prior, spec.min_eigenvalue)
    residual_variance, residual_fallback = _positive_variances(fit.residuals, spec.min_eigenvalue)
    beta = np.where(np.isfinite(fit.beta), fit.beta, 0.0)
    common = beta @ fit.factor_covariance @ beta.T
    raw_covariance, raw_delta = positive_covariance(
        prior, spec.min_eigenvalue, audit=pairwise_audit, prefix="prior_returns"
    )
    residual_covariance, residual_delta = positive_covariance(
        fit.residuals, spec.min_eigenvalue, audit=pairwise_audit, prefix="prior_residuals"
    )
    covariances = {
        "diagonal": np.diag(raw_variance),
        "pairwise_sample_covariance": raw_covariance,
        "ff5_mom_diagonal": common + np.diag(residual_variance),
        "ff5_mom_pairwise_residual": common + residual_covariance,
    }
    audits: list[dict[str, object]] = [
        {
            "method": name,
            "parameter": np.nan,
            "training_score": np.nan,
            "variance_fallbacks": int(
                raw_fallback.sum()
                if name in {"diagonal", "pairwise_sample_covariance"}
                else residual_fallback.sum()
            ),
            "exposure_fallbacks": int(np.sum(~np.isfinite(fit.beta).all(axis=1))),
            "identity_shrink": raw_delta
            if name == "pairwise_sample_covariance"
            else residual_delta
            if name == "ff5_mom_pairwise_residual"
            else 0.0,
            "status": "available",
            "reason": "",
        }
        for name in covariances
    ]
    if not np.isfinite(fit.residuals).any():
        return covariances, audits, raw_variance
    for name, geometry in geometries.items():
        for arm in COVARIANCE_ARMS:
            method = f"{name}|{arm}"
            try:
                if arm in {"spatial", "spatial_matched"}:
                    weights = _spatial_weights(geometry, arm)
                    parameter, score = fit_spatial(fit.residuals, weights, residual_variance)
                    inverse = np.linalg.solve(
                        np.eye(len(prior.T)) - parameter * weights, np.eye(len(prior.T))
                    )
                    covariance = (inverse * residual_variance) @ inverse.T
                else:
                    parameter, score = fit_gram(
                        fit.residuals, geometry.gram, residual_variance, spec.min_eigenvalue
                    )
                    correlation = (1 - parameter) * np.eye(len(prior.T)) + parameter * geometry.gram
                    covariance = correlation * np.sqrt(
                        np.outer(residual_variance, residual_variance)
                    )
                covariances[method] = common + covariance
                audits.append(
                    {
                        "method": method,
                        "parameter": parameter,
                        "training_score": score,
                        "variance_fallbacks": int(residual_fallback.sum()),
                        "exposure_fallbacks": int(np.sum(~np.isfinite(fit.beta).all(axis=1))),
                        "identity_shrink": geometry.delta
                        if arm in {"gram", "spatial_matched"}
                        else 0.0,
                        "geometry": geometry.spatial_metric
                        if arm == "spatial"
                        else "repaired_unit_gram",
                        "bandwidth": geometry.matched_bandwidth
                        if arm == "spatial_matched"
                        else geometry.bandwidth
                        if arm == "spatial"
                        else np.nan,
                        "target_neighbours": geometry.matched_target
                        if arm == "spatial_matched"
                        else np.nan,
                        "status": "available",
                        "reason": "",
                    }
                )
            except (ValueError, np.linalg.LinAlgError, RuntimeError) as error:
                audits.append({"method": method, "status": "unavailable", "reason": str(error)})
    return covariances, audits, raw_variance


def _generated_core(  # noqa: PLR0913 -- one unchanged quarterly roster and shared refits.
    quarter: pd.Timestamp,
    issuers: tuple[str, ...],
    geometries: dict[str, Geometry],
    *,
    betas: Mapping[int, pd.Series],
    medians: Mapping[int, pd.Series],
    spec: StudySpec,
) -> list[dict[str, object]]:
    """Finish one quarter's generated-beta refits before releasing its dense networks."""
    rows: list[dict[str, object]] = []
    spectra: dict[str, NDArray[np.float64]] = {}
    for replicate in range(1, spec.generated_beta_draws + 1):
        beta = betas.get(replicate, pd.Series(dtype=float)).reindex(issuers).to_numpy(float)
        y = medians[replicate].reindex(issuers).to_numpy(float)
        for name, item in geometries.items():
            spectrum = None
            if np.isfinite(beta).all() and np.isfinite(y).all():
                if name not in spectra:
                    spectra[name] = symmetric_spectrum(item.weights)
                spectrum = spectra[name]
            for estimator in ESTIMATORS:
                fitted = _core_fit(
                    y, beta, item.weights, estimator, spectrum=spectrum, standard_errors=False
                )
                rows.append({"quarter": quarter, "method": name, "replicate": replicate, **fitted})
    return rows


def run_analyses(  # noqa: PLR0912, PLR0913, PLR0915, PLR0917, C901 -- canonical matched pipeline.
    panel: pd.DataFrame,
    characteristics: pd.DataFrame,
    factors: pd.DataFrame,
    representations: Mapping[object, object],
    spec: StudySpec,
    output: Path,
    *,
    history: pd.DataFrame | None = None,
    tasks: Literal["all", "measurement", "replication"] = "all",
) -> dict[str, pd.DataFrame]:
    """Persist every analysis with a common roster, clock and observed-outcome mask.

    ``representations`` maps forecast quarters to rung/model arrays. Arrays use
    sorted issuer_id order; payloads with issuer_ids and master_digest additionally
    enforce those identities. Empty mappings run the core/control stage only.
    Formation-specific ``history`` supplies warmup returns of the currently selected
    share classes, keyed by asof_year; it never defines another evaluation cohort.
    """
    output.mkdir(parents=True, exist_ok=True)
    if tasks not in {"all", "measurement", "replication"}:
        message = "Unknown quarterly analysis stage."
        raise ValueError(message)
    measurement = tasks in {"all", "measurement"}
    replication = tasks in {"all", "replication"}
    master = validate_panel(panel)
    shared_contract = panel_contract(master, spec)
    contract = shared_contract.copy()
    factor_frame = _factors(factors)
    characteristic_frame = _characteristics(characteristics)
    calendar = pd.period_range(spec.feature_start, spec.archive_end, freq="Q").to_timestamp("Q")
    contract |= {
        "history_sha256": frame_digest(history) if history is not None else None,
        "characteristics_sha256": frame_digest(characteristics),
        "factors_sha256": frame_digest(factors),
        "analysis_calendar": calendar.astype(str).tolist(),
        "core": "full feature-era descriptive CAPM-MM; no second-stage intercept",
        "forecast": "strictly prior20 quarters; published FF5+Mom ridge proxies",
        "forecast_mean": "zero excess return, identical for every covariance procedure",
        "prior_fallbacks": {
            "variance": "cross-sectional median positive prior variance; otherwise explicit floor",
            "unavailable_factor_loading": "zero-loading prior; exposure_fallbacks counts retained",
            "interpretation": "declared model priors, not observed returns or identified exposures",
        },
        "representations_supplied": bool(representations),
        "spatial_arms": {
            "spatial": "original characteristic distance or native Euclidean distance",
            "spatial_matched": "unit-chord distance from exactly the Gram arm's repaired Gram",
            "concentration": "common Fernandez-joint mean effective-neighbour target",
            "primary_comparison": "Gram minus spatial_matched; common-marginal correlation scores",
        },
        "tasks": tasks,
    }
    write_json(output / "contract.json", contract)
    feature_panel = master.loc[master["quarter"].isin(calendar)].copy()
    sample = feature_panel[["issuer_id", "quarter", "total_return"]].rename(
        columns={"issuer_id": "ticker", "quarter": "date"}
    )
    sample["excess"] = sample["total_return"] - sample["date"].map(factor_frame["RF"])
    sample["market"] = sample["date"].map(factor_frame["Mkt-RF"])
    estimates = (
        _mm_estimates(sample, calendar, spec, output)
        if replication
        else pd.DataFrame(columns=["replicate", "ticker", "term", "estimate", "converged"])
    )
    wide = sample.pivot(index="date", columns="ticker", values="excess").reindex(calendar)
    median = wide.median(axis=0)
    indices = generated_beta_indices(calendar, spec.generated_beta_draws, 4, spec.seed)
    betas: dict[int, pd.Series] = {}
    for replicate, group in estimates.groupby("replicate", sort=True):
        slopes = group.loc[group["term"].eq("market")].copy()
        slopes["estimate"] = slopes["estimate"].where(slopes["converged"].eq(other=True))
        betas[int(float(str(replicate)))] = slopes.set_index("ticker")["estimate"]
    # The same resampled calendar drives both generated regressors and outcomes.
    # These small issuer vectors are shared across quarters; dense geometries are not.
    bootstrap_medians = {
        replicate: wide.reindex(
            pd.to_datetime(
                indices.loc[indices["replicate"].eq(replicate)].sort_values("position")["quarter"]
            )
        ).median(axis=0)
        for replicate in range(1, spec.generated_beta_draws + 1 if replication else 1)
    }
    tables: dict[str, list[dict[str, object]]] = {
        name: []
        for name in (
            "core",
            "core_roster",
            "generated_draws",
            "exposures",
            "decoder_quality",
            "scores",
            "forecasts",
            "geometry",
            "coordinates",
            "spectrum",
            "portfolios",
            "calendar",
            "var_audit",
        )
    }
    planned_geometries = {
        f"{rung}/{model}{decoded}"
        for rung in spec.rungs
        for model in (*spec.models, *CONTROL_MODELS)
        for decoded in ("", "@decoded")
    }
    pairwise_files: list[dict[str, object]] = []
    for quarter in calendar:
        current = feature_panel.loc[feature_panel["quarter"].eq(quarter)].sort_values("issuer_id")
        issuers = tuple(current["issuer_id"].astype(str))
        mask = current["observed"].to_numpy(bool)
        mask_digest = digest_json(list(zip(issuers, mask.tolist(), strict=True)))
        tables["calendar"].append(
            {
                "quarter": quarter,
                "firms": len(issuers),
                "observed_firms": int(mask.sum()),
                "mask_sha256": mask_digest,
                "status": "available" if issuers else "unavailable_no_xbrl_population",
            }
        )
        if not issuers:
            continue
        if replication:
            tables["var_audit"].append(
                {
                    "quarter": quarter,
                    "firms": len(issuers),
                    "status": "not_implemented_on_quarterly_master",
                    "reason": (
                        "Legacy equations8a/8b hypothetical simulation is not a matched "
                        "quarterly portfolio backtest."
                    ),
                }
            )
        risk_free = (
            float(factor_frame.reindex(index=[quarter])["RF"].to_numpy(float)[0])
            if quarter in factor_frame.index
            else float("nan")
        )
        if not np.isfinite(risk_free):
            msg = f"Missing quarterly RF would change the master outcome mask: {quarter}."
            raise ValueError(msg)
        outcome = current["total_return"].to_numpy(float) - risk_free
        geometry = fernandez_geometries(characteristic_frame, issuers, quarter, spec)
        arrays = (
            _representation_arrays(representations, quarter, issuers, contract)
            if measurement
            else {}
        )
        if measurement:
            raw_prior, prior_dates = _history_window(master, history, quarter, issuers, spec)
            factor_prior = factor_frame.reindex(prior_dates)
            prior = raw_prior - factor_prior["RF"].to_numpy(float)[:, None]
            exposures = estimate_exposures(
                prior, factor_prior[list(FACTOR_NAMES)].to_numpy(float), spec
            )
        else:
            prior, prior_dates = np.empty((0, len(issuers))), pd.DatetimeIndex([])
            exposures = ExposureFit(
                np.full((len(issuers), 6), np.nan),
                prior,
                np.eye(6),
                np.zeros(len(issuers), dtype=np.int64),
                tuple("not_requested" for _ in issuers),
                np.full(len(issuers), np.nan),
            )
        for position, issuer in enumerate(issuers if measurement else ()):
            tables["exposures"].append(
                {
                    "quarter": quarter,
                    "issuer_id": issuer,
                    "target": "published_FF5_Mom_20quarter_ridge",
                    "observations": int(exposures.counts[position]),
                    "status": exposures.statuses[position],
                    "alpha": float(exposures.alphas[position]),
                    **{
                        factor: float(exposures.beta[position, index])
                        for index, factor in enumerate(FACTOR_NAMES)
                    },
                }
            )
        eigenvalues, vectors = np.linalg.eigh(exposures.factor_covariance)
        factor_root = (vectors * np.sqrt(np.maximum(eigenvalues, 0))) @ vectors.T
        for name, values in arrays.items():
            geometry[name] = _native_geometry(values, geometry["fernandez_joint"], spec)
            decoded, r2 = _decoded_states(values, exposures.beta, issuers)
            available = np.isfinite(decoded).all()
            tables["decoder_quality"].append(
                {
                    "quarter": quarter,
                    "method": name,
                    "target": "published_FF5_Mom_20quarter_ridge",
                    "decoder_r2": r2,
                    "labeled_issuers": int(np.isfinite(exposures.beta).all(axis=1).sum()),
                    "query_issuers": len(issuers),
                    "status": "available" if available else "unavailable_training_labels",
                }
            )
            if available:
                geometry[f"{name}@decoded"] = _native_geometry(
                    decoded @ factor_root, geometry["fernandez_joint"], spec
                )
        target = (
            effective_neighbours(geometry["fernandez_joint"].weights) if len(issuers) > 1 else 0.0
        )
        if measurement:
            geometry = {name: match_gram_geometry(item, target) for name, item in geometry.items()}
        beta = betas.get(0, pd.Series(dtype=float)).reindex(issuers).to_numpy(float)
        y = median.reindex(issuers).to_numpy(float)
        for index, issuer in enumerate(issuers if replication else ()):
            tables["core_roster"].append(
                {
                    "quarter": quarter,
                    "issuer_id": issuer,
                    "mm_beta": beta[index],
                    "median_excess": y[index],
                    "status": "available"
                    if np.isfinite(beta[index]) and np.isfinite(y[index])
                    else "unavailable_MM_or_median",
                    "observed_core_quarters": int(wide[issuer].notna().sum())
                    if issuer in wide
                    else 0,
                }
            )
        for name, item in geometry.items():
            for estimator in ESTIMATORS if replication else ():
                tables["core"].append(
                    {
                        "quarter": quarter,
                        "method": name,
                        "panel_sha256": contract["panel_sha256"],
                        "mask_sha256": mask_digest,
                        **_core_fit(y, beta, item.weights, estimator),
                    }
                )
            if measurement:
                audit, coordinates, spectrum, portfolios = _geometry_tables(
                    item, quarter, name, issuers, outcome
                )
                tables["geometry"].append(audit)
                tables["coordinates"].extend(coordinates)
                tables["spectrum"].extend(spectrum)
                tables["portfolios"].extend(portfolios)
            else:
                tables["geometry"].append(
                    {
                        "quarter": quarter,
                        "method": name,
                        "firms": len(issuers),
                        "undefined_pairs": item.undefined_pairs,
                        "identity_shrink": item.delta,
                        "bandwidth": item.bandwidth,
                    }
                )
        covariance_models: list[str] = [
            "diagonal",
            "pairwise_sample_covariance",
            "ff5_mom_diagonal",
            "ff5_mom_pairwise_residual",
        ]
        geometry_names = sorted(set(geometry) | planned_geometries)
        covariance_models += [f"{name}|{arm}" for name in geometry_names for arm in COVARIANCE_ARMS]
        if not measurement:
            covariance_models = []
        covariances: dict[str, NDArray[np.float64]] = {}
        pairwise_payload = (
            {
                "prior_quarters": np.asarray(prior_dates.strftime("%Y-%m-%d"), dtype=str),
                "prior_excess_returns": prior,
                "prior_factor_residuals": exposures.residuals,
            }
            if measurement
            else {}
        )
        audits: list[dict[str, object]] = []
        if measurement and np.isfinite(prior).sum(axis=0).max(initial=0) >= 2:
            covariances, audits, raw_variance = _forecast_covariances(
                prior, exposures, geometry, spec, pairwise_audit=pairwise_payload
            )
        else:
            raw_variance = np.full(len(issuers), np.nan)
        forecast_audits = {str(audit["method"]): audit for audit in audits}
        for name in covariance_models:
            if name not in forecast_audits:
                geometry_name = name.rsplit("|", 1)[0]
                forecast_audits[name] = {
                    "method": name,
                    "status": "unavailable_prior_moments"
                    if geometry_name in geometry or "|" not in name
                    else "unavailable_decoder_labels"
                    if geometry_name.endswith("@decoded") and geometry_name[:-8] in geometry
                    else "unavailable_representation",
                    "reason": "Required geometry or past-only fitted moments are unavailable.",
                }
            tables["forecasts"].append(
                {
                    "quarter": quarter,
                    "prior_start": prior_dates[0],
                    "prior_end": prior_dates[-1],
                    **forecast_audits[name],
                }
            )
            for arm in ("covariance", "correlation"):
                row: dict[str, object] = {
                    "quarter": quarter,
                    "method": f"{name}|{arm}",
                    "firms": len(issuers),
                    "observed_firms": int(mask.sum()),
                    "mask_sha256": mask_digest,
                    "panel_sha256": contract["panel_sha256"],
                    "score": np.nan,
                    "score_per_issuer": np.nan,
                    "status": forecast_audits[name]["status"],
                    "reason": forecast_audits[name].get("reason", ""),
                }
                if name in covariances:
                    covariance = covariances[name]
                    if arm == "correlation":
                        scales = np.sqrt(raw_variance / np.diag(covariance))
                        covariance = covariance * np.outer(scales, scales)
                    score, count = gaussian_observed(outcome, covariance, mask)
                    row |= {
                        "score": score,
                        "score_per_issuer": score / count if count else np.nan,
                        "status": "available" if count else "unavailable_no_observed_returns",
                    }
                tables["scores"].append(row)
        if replication:
            # Failures remain rows on the unchanged roster, without spare-draw selection.
            tables["generated_draws"].extend(
                _generated_core(
                    quarter,
                    issuers,
                    geometry,
                    betas=betas,
                    medians=bootstrap_medians,
                    spec=spec,
                )
            )
        pairwise_files.append(
            _save_pairwise_audit(
                output, quarter, issuers, geometry, payload=pairwise_payload, spec=spec
            )
        )
    frames = {name: pd.DataFrame(rows) for name, rows in tables.items()}
    frames["mm_estimates"] = estimates
    frames["generated_intervals"] = summarize_generated(
        frames["generated_draws"], spec.generated_beta_draws
    )
    frames["conditional_intervals"] = paired_intervals(
        frames["scores"],
        calendar=calendar,
        draws=spec.bootstrap_draws,
        blocks=spec.bootstrap_blocks,
        seed=spec.seed,
    )
    for name, frame in frames.items():
        atomic_parquet(output / f"{name}.parquet", frame)
    atomic_csv(output / "estimates.csv", frames["core"])
    availability = (
        frames["core"]
        .groupby(["estimator", "status"])
        .size()
        .reset_index(name="rows")
        .to_dict("records")
        if not frames["core"].empty
        else []
    )
    write_json(
        output / "manifest.json",
        {
            "master": shared_contract,
            "status": "available" if len(feature_panel) else "unavailable_no_analytical_population",
            "files": {name: f"{name}.parquet" for name in frames}
            | {"estimates_csv": "estimates.csv"},
            "estimator_availability": availability,
            "pairwise_arrays": pairwise_files,
            "mm_artifacts": {
                str(path.relative_to(output)): file_hash(path)
                for path in sorted((output / "mm").rglob("*"))
                if path.is_file()
            },
            "history_sha256": contract["history_sha256"],
            "interpretation": "shared roster and masks; estimator undefined statuses retained",
            "tasks": tasks,
        },
    )
    summary = {
        "contract": contract,
        "rows": {name: len(frame) for name, frame in frames.items()},
        "status": "available" if len(feature_panel) else "unavailable_no_analytical_population",
        "scope": "descriptive full-era MM core; separate strictly past-only forecasts",
        "neutral_links": (
            "undefined characteristic pair correlation0; never a zero economic observation"
        ),
        "variance_floor": spec.min_eigenvalue,
        "matched_geometry": "spatial_matched and Gram use exactly the same repaired unit Gram",
        "planned_model_cells": "unavailable cells remain explicit score and forecast rows",
        "conditional_bootstrap": (
            "fixed fitted procedures; full quarterly calendar; observed-score estimand"
        ),
        "generated_bootstrap": (
            "999 requested by default; all MM failures retained; no spare-draw selection"
        ),
    }
    write_json(output / "summary.json", summary)
    return frames
