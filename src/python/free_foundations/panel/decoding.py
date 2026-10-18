"""Calibrated readouts: decode prior-window covariance exposures from each representation.

Native distances compare hidden states directly. A calibrated readout instead fits a
declared economic target, here the exposures implied by the prior three years of factor
residuals, and measures distance between the decoded exposures (``Measurement`` in the
Lean library). Decoders are ridge regressions fitted out of fold across firms, so a
firm's own returns never decode its own exposure. Everything uses data before the
return year only.
"""

from __future__ import annotations

import hashlib
from typing import TYPE_CHECKING

import numpy as np
from scipy.stats import spearmanr
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler

from free_foundations.expanded.distance import pairwise_distance

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray

FACTORS = 5
FOLDS = 5
ALPHAS = np.logspace(-2, 4, 13)


def covariance_exposures(prior: FloatArray, factors: int = FACTORS) -> FloatArray:
    """Rows of V_k Λ_k^½ from the prior residual covariance: its rank-k common part.

    Distances between rows are the exposure distances of that common part, and are
    invariant to the sign and rotation indeterminacy of the eigenvectors.
    """
    values, vectors = np.linalg.eigh(np.cov(prior, rowvar=False))
    top = np.argsort(values)[::-1][:factors]
    return vectors[:, top] * np.sqrt(np.clip(values[top], 0, None))


def folds(tickers: tuple[str, ...], count: int = FOLDS) -> FloatArray:
    """Deterministic, outcome-independent fold labels from ticker hashes."""
    order = sorted(range(len(tickers)), key=lambda i: hashlib.sha256(tickers[i].encode()).digest())
    labels = np.empty(len(tickers), dtype=float)
    labels[order] = np.arange(len(tickers)) % count
    return labels


def decode(
    states: FloatArray, exposures: FloatArray, tickers: tuple[str, ...]
) -> tuple[FloatArray, dict[str, float]]:
    """Out-of-fold ridge predictions of exposures, with fit and distance agreement."""
    predictions = np.zeros_like(exposures)
    labels = folds(tickers)
    for fold in np.unique(labels):
        test = labels == fold
        scaler = StandardScaler().fit(states[~test])
        model = RidgeCV(alphas=ALPHAS).fit(scaler.transform(states[~test]), exposures[~test])
        predictions[test] = model.predict(scaler.transform(states[test]))
    total = float(np.sum((exposures - exposures.mean(axis=0)) ** 2))
    target = pairwise_distance(exposures, metric="euclidean")
    decoded = pairwise_distance(predictions, metric="euclidean")
    upper = np.triu_indices(len(tickers), 1)
    return predictions, {
        "decoder_r2": 1 - float(np.sum((exposures - predictions) ** 2)) / total,
        "exposure_distance_spearman": float(spearmanr(target[upper], decoded[upper]).statistic),
    }
