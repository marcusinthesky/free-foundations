"""Calibrated readouts: decode prior-window reference-factor exposures from each representation.

Native distances compare hidden states directly. A calibrated readout instead fits a
declared statistical target and measures distance between the decoded targets
(``Measurement`` in the Lean library). The target is each cohort firm's loadings on the
leading principal components of the prior-window factor residuals of firms outside the
cohort. Those components are fixed before any fold is drawn, so each row of the target
depends only on its own firm's returns and the outside firms: a held-out firm's returns
never reach the targets its decoder is trained on, and every fold shares one coordinate
system. Decoders are ridge regressions fitted out of fold across firms. Everything uses
data before the return year only.

``covariance_exposures`` keeps the earlier in-panel construction, the rank-k coordinates
of the cohort's own prior residual covariance. Its eigendecomposition pools every cohort
firm, so it is a covariance control, not a held-out target.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

from free_foundations.expanded.distance import pairwise_distance

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

FACTORS = 5
# Ranks audited for target reliability and decoder quality; networks use FACTORS only.
RANKS = (3, 5, 8)
FOLDS = 5
ALPHAS = np.logspace(-2, 4, 13)


def covariance_exposures(prior: FloatArray, factors: int = FACTORS) -> FloatArray:
    """Rows of V_k Λ_k^½ from the cohort's own prior residual covariance (in-panel control).

    Distances between rows are the distances of its rank-k part, and are invariant to the
    sign and rotation indeterminacy of the eigenvectors.
    """
    values, vectors = np.linalg.eigh(np.cov(prior, rowvar=False))
    top = np.argsort(values)[::-1][:factors]
    return vectors[:, top] * np.sqrt(np.clip(values[top], 0, None))


def reference_factors(reference: FloatArray, factors: int = FACTORS) -> FloatArray:
    """Unit-variance leading principal components of standardized outside-firm residuals.

    Standardizing first stops a single high-variance firm from defining a factor.
    """
    scale = reference.std(axis=0)
    kept = reference[:, scale > 0] / scale[scale > 0]
    left, _, _ = np.linalg.svd(kept - kept.mean(axis=0), full_matrices=False)
    return left[:, :factors] * np.sqrt(len(kept))


def reference_exposures(prior: FloatArray, factors: FloatArray) -> FloatArray:
    """Each cohort firm's OLS loadings on fixed factor series; one row per firm."""
    return np.linalg.lstsq(factors, prior, rcond=None)[0].T


def commonality(prior: FloatArray, factors: FloatArray) -> FloatArray:
    """Share of each firm's prior residual variance that the factor series explain."""
    fitted = factors @ reference_exposures(prior, factors).T
    centered = prior - prior.mean(axis=0)
    return 1 - np.sum((prior - fitted) ** 2, axis=0) / np.sum(centered**2, axis=0)


@dataclass(frozen=True)
class Targets:
    """One year's calibration targets: reference exposures by rank and the in-panel control."""

    reference: dict[int, FloatArray]
    covariance: FloatArray


def targets(prior: FloatArray, reference: FloatArray, ranks: tuple[int, ...] = RANKS) -> Targets:
    """Nested reference targets at every audited rank, and the in-panel rank-5 control."""
    factors = reference_factors(reference, max(ranks))
    return Targets(
        reference={rank: reference_exposures(prior, factors[:, :rank]) for rank in ranks},
        covariance=covariance_exposures(prior),
    )


def _effective_firms(exposures: FloatArray) -> float:
    """Effective number of firms holding the target's squared mass, as a fraction of all."""
    mass = np.sum(exposures**2, axis=1)
    share = mass / mass.sum()
    return float(1 / np.sum(share**2) / len(share))


def _distance_agreement(first: FloatArray, second: FloatArray) -> float:
    upper = np.triu_indices(len(first), 1)
    return float(
        spearmanr(
            pairwise_distance(first, metric="euclidean")[upper],
            pairwise_distance(second, metric="euclidean")[upper],
        ).statistic
    )


def reliability(
    prior: FloatArray, reference: FloatArray, rank: int
) -> list[dict[str, float | str | int]]:
    """Split-half reliability, commonality and mass concentration of both targets.

    Each half of the prior window gives its own estimate. For the reference target both
    halves share the full-window factor series, so their coordinates are comparable; the
    Spearman-Brown value is the reliability of the full-window target and bounds the R^2 any
    decoder can reach against it. The in-panel coordinates rotate between halves, so only
    their distances are compared.
    """
    half = len(prior) // 2
    factors = reference_factors(reference, rank)
    first = reference_exposures(prior[:half], factors[:half])
    second = reference_exposures(prior[half:], factors[half:])
    centered = (first - first.mean(axis=0), second - second.mean(axis=0))
    correlation = float(
        np.sum(centered[0] * centered[1])
        / np.sqrt(np.sum(centered[0] ** 2) * np.sum(centered[1] ** 2))
    )
    full = reference_exposures(prior, factors)
    shares = commonality(prior, factors)
    in_panel = covariance_exposures(prior, rank)
    panel_shares = np.sum(in_panel**2, axis=1) / np.var(prior, axis=0, ddof=1)
    return [
        {
            "target": "reference",
            "rank": rank,
            "reference_firms": reference.shape[1],
            "half_correlation": correlation,
            "spearman_brown": 2 * correlation / (1 + correlation),
            "distance_reliability": _distance_agreement(first, second),
            "commonality_mean": float(shares.mean()),
            "commonality_median": float(np.median(shares)),
            "effective_firm_fraction": _effective_firms(full),
        },
        {
            "target": "covariance",
            "rank": rank,
            "reference_firms": reference.shape[1],
            "half_correlation": np.nan,
            "spearman_brown": np.nan,
            "distance_reliability": _distance_agreement(
                covariance_exposures(prior[:half], rank), covariance_exposures(prior[half:], rank)
            ),
            "commonality_mean": float(panel_shares.mean()),
            "commonality_median": float(np.median(panel_shares)),
            "effective_firm_fraction": _effective_firms(in_panel),
        },
    ]


def folds(tickers: tuple[str, ...], count: int = FOLDS) -> FloatArray:
    """Deterministic, outcome-independent fold labels from ticker hashes."""
    order = sorted(range(len(tickers)), key=lambda i: hashlib.sha256(tickers[i].encode()).digest())
    labels = np.empty(len(tickers), dtype=float)
    labels[order] = np.arange(len(tickers)) % count
    return labels


def decode(
    states: FloatArray, exposures: FloatArray, tickers: tuple[str, ...]
) -> tuple[FloatArray, dict[str, float]]:
    """Out-of-fold ridge predictions of exposures, with fit and distance agreement.

    The readout never extrapolates beyond its training fold: standardized held-out states
    are clipped to the training range and predictions to the training targets' range.
    Without this, one firm far outside a near-degenerate state cloud (BKH's first-layer
    EXAONE states in 2017, up to 190 training standard deviations out) decided the fit.
    """
    predictions = np.zeros_like(exposures)
    labels = folds(tickers)
    for fold in np.unique(labels):
        test = labels == fold
        scaler = StandardScaler().fit(states[~test])
        train = scaler.transform(states[~test])
        held = np.clip(scaler.transform(states[test]), train.min(axis=0), train.max(axis=0))
        model = RidgeCV(alphas=ALPHAS).fit(train, exposures[~test])
        predictions[test] = np.clip(
            model.predict(held), exposures[~test].min(axis=0), exposures[~test].max(axis=0)
        )
    total = float(np.sum((exposures - exposures.mean(axis=0)) ** 2))
    return predictions, {
        "decoder_r2": 1 - float(np.sum((exposures - predictions) ** 2)) / total,
        "exposure_distance_spearman": _distance_agreement(exposures, predictions),
    }
