"""Out-of-sample spatial APT: does calibrated foundation-model geometry add to factors?

The comparison separates three changes that a single improvement could otherwise
conflate: CAPM to APT (more factors), a non-spatial to a spatial residual structure,
and how proximity between issuers is measured. One roster, one information set and
one train/test calendar are shared by every model.

- Training window: monthly excess returns of the primary formation's roster with no
  missing training month. Factor loadings ``B`` come from time-series OLS on the
  French five factors and momentum; risk-scaled exposures are ``a_i = Omega^1/2 b_i``
  with ``Omega`` the training factor covariance, so ``||a_i - a_j||`` is the standard
  deviation of the difference in the two issuers' common-shock responses.
- Geometries: Fernández's joint characteristic distance; raw frozen states (chord
  distance) and calibrated states (a ridge readout of exposures, cross-fitted over
  issuers, Euclidean distance) for every rung, model and the direct-feature control;
  estimated exposures themselves; same-SIC-2 industry; and a relabelled null. Every
  distance becomes the symmetrized, row-normalized k-NN graph of ``networks``.
- Covariance models: CAPM ``s_m^2 beta beta' + D``; APT ``B Omega B' + D``; and spatial
  APT ``B Omega B' + P D P'`` with ``P = (I - lambda W)^-1``, ``lambda`` and ``D``
  fitted by Gaussian likelihood to training residuals.
- Test window: each month's observed issuers score the Gaussian negative log
  likelihood of their excess returns (mean zero for every model) and the realized
  return of the global minimum-variance portfolio. Paired monthly score differences
  get stationary-bootstrap intervals and Holm-adjusted p-values.
- Recovery is evaluated separately: out-of-fold exposure R^2 for each readout and the
  Spearman Mantel correlation of each distance with the exposure distance.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
import yaml
from scipy.optimize import minimize_scalar
from scipy.stats import norm, rankdata

from free_foundations.data import write_json
from free_foundations.study import spatial_ml
from free_foundations.study.factors import parse_monthly
from free_foundations.study.inference import (
    block_length,
    holm,
    percentile_interval,
    stationary_orders,
)
from free_foundations.study.networks import (
    characteristic_distances,
    industry_weights,
    knn_weights,
    permuted,
    representation_distance,
)
from free_foundations.study.rosters import load
from free_foundations.study.source_io import atomic_parquet
from free_foundations.study.spec import digest_json

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray

FACTOR_FILES = ("F-F_Research_Data_5_Factors_2x3_CSV.zip", "F-F_Momentum_Factor_CSV.zip")


@dataclass(frozen=True)
class AptSpec:
    """The pre-specified train/test design, read from the ``apt`` block of params.yaml."""

    formation: int = 2015
    train_start: str = "2016-01"
    train_end: str = "2020-12"
    test_start: str = "2021-01"
    test_end: str = "2025-12"
    factors: tuple[str, ...] = ("Mkt-RF", "SMB", "HML", "RMW", "CMA", "Mom")
    neighbours: int = 10
    folds: int = 5
    ridge_alphas: tuple[float, ...] = field(
        default_factory=lambda: tuple(float(value) for value in np.logspace(-2, 4, 13))
    )
    clip: float = 10.0
    score_draws: int = 9999
    mantel_draws: int = 999
    seed: int = 42

    def __post_init__(self) -> None:
        """Training must end before testing starts; folds and k must be usable."""
        if not pd.Period(self.train_end, "M") < pd.Period(self.test_start, "M"):
            message = "The training window must end before the test window starts."
            raise ValueError(message)
        if self.folds < 2 or self.neighbours < 1 or not self.ridge_alphas:
            message = "APT needs at least two folds, one neighbour and one ridge penalty."
            raise ValueError(message)

    @classmethod
    def read(cls, params: Path) -> AptSpec:
        """The ``apt`` block; tuples stay tuples so the digest is stable."""
        payload = yaml.safe_load(params.read_text()).get("apt", {})
        values: dict[str, Any] = {
            key: tuple(value) if isinstance(value, list) else value
            for key, value in payload.items()
        }
        return cls(**values)

    def months(self, start: str, end: str) -> pd.DatetimeIndex:
        """Month-end calendar between two ``YYYY-MM`` labels, inclusive."""
        return pd.period_range(start, end, freq="M").to_timestamp(how="end").normalize()

    @property
    def digest(self) -> str:
        """Identity bound into the stage manifest."""
        return digest_json(asdict(self))


# --- Exposures and readouts ---------------------------------------------------------


def monthly_factors(sources: Path) -> pd.DataFrame:
    """French monthly five factors, momentum and RF, indexed by month end."""
    frames = [parse_monthly((sources / name).read_bytes()) for name in FACTOR_FILES]
    merged = frames[0].merge(frames[1], on="month", how="inner")
    merged.columns = [str(column).strip() for column in merged.columns]
    merged["month"] = pd.to_datetime(merged["month"]).dt.to_period("M").dt.to_timestamp(how="end")
    merged["month"] = merged["month"].dt.normalize()
    return merged.set_index("month").sort_index()


def factor_loadings(
    returns: FloatArray, factors: FloatArray
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Time-series OLS with an intercept: loadings (N x K), intercepts and residuals (T x N)."""
    design = np.column_stack([np.ones(len(factors)), factors])
    coefficients = np.linalg.lstsq(design, returns, rcond=None)[0]
    residuals = returns - design @ coefficients
    return coefficients[1:].T, coefficients[0], residuals


def symmetric_root(matrix: FloatArray) -> FloatArray:
    """Principal square root of a symmetric positive-semidefinite matrix."""
    values, vectors = np.linalg.eigh((matrix + matrix.T) / 2)
    return (vectors * np.sqrt(np.clip(values, 0, None))) @ vectors.T


def _standardize(train: FloatArray, test: FloatArray, clip: float) -> tuple[FloatArray, FloatArray]:
    """Training-fold scaling, clipped at ``clip`` standard deviations, then centred.

    Constant training columns are dropped. Clipping bounds the leverage of
    near-constant disclosure columns, whose held-out values can otherwise lie
    millions of training standard deviations away.
    """
    mean, scale = train.mean(axis=0), train.std(axis=0)
    keep = scale > 1e-12
    scaled = [
        np.clip((values[:, keep] - mean[keep]) / scale[keep], -clip, clip)
        for values in (train, test)
    ]
    # Clipping moves the training mean; re-centre so the leave-one-out leverage of the
    # intercept-free ridge on centred features stays exact.
    centre = scaled[0].mean(axis=0)
    return scaled[0] - centre, scaled[1] - centre


def _ridge_loo(features: FloatArray, target: FloatArray, alphas: tuple[float, ...]) -> float:
    """Penalty minimizing closed-form leave-one-out squared error over all target columns."""
    left, singular, _ = np.linalg.svd(features, full_matrices=False)
    centred = target - target.mean(axis=0)
    projected = left.T @ centred
    best, best_error = alphas[0], np.inf
    for alpha in alphas:
        shrink = singular**2 / (singular**2 + alpha)
        fitted = left @ (shrink[:, None] * projected)
        leverage = (left**2 * shrink).sum(axis=1) + 1 / len(features)
        error = float(np.sum(((centred - fitted) / (1 - leverage)[:, None]) ** 2))
        if error < best_error:
            best, best_error = alpha, error
    return best


def crossfit_readout(  # noqa: PLR0913 -- the readout's complete pre-specified settings.
    features: FloatArray,
    target: FloatArray,
    folds: int,
    alphas: tuple[float, ...],
    seed: int,
    *,
    clip: float = 10.0,
) -> tuple[FloatArray, list[float]]:
    """Out-of-fold ridge predictions of ``target`` from ``features``.

    Each held-out issuer's prediction uses a readout whose standardization and penalty
    were chosen on the other folds only, so no issuer's exposure enters its own
    prediction.
    """
    features, target = np.asarray(features, float), np.asarray(target, float)
    assignment = np.random.default_rng(seed).permutation(len(features)) % folds
    predictions = np.empty_like(target)
    chosen = []
    for fold in range(folds):
        held = assignment == fold
        train, test = _standardize(features[~held], features[held], clip)
        alpha = _ridge_loo(train, target[~held], alphas)
        chosen.append(alpha)
        mean = target[~held].mean(axis=0)
        gram = train @ train.T + alpha * np.eye(len(train))
        dual = np.linalg.solve(gram, target[~held] - mean)
        predictions[held] = test @ (train.T @ dual) + mean
    return predictions, chosen


def euclidean_distance(values: FloatArray) -> FloatArray:
    """Pairwise Euclidean distance between rows."""
    squared = np.sum(values**2, axis=1)
    gram = squared[:, None] + squared[None, :] - 2 * values @ values.T
    distance = np.sqrt(np.clip(gram, 0, None))
    np.fill_diagonal(distance, 0.0)
    return distance


def neighbour_sets(distance: FloatArray, neighbours: int) -> list[frozenset[int]]:
    """Each row's ``neighbours`` nearest other rows (ties broken by roster order)."""
    distance = np.array(distance, dtype=float)
    np.fill_diagonal(distance, np.inf)
    order = np.argsort(distance, axis=1, kind="stable")[:, :neighbours]
    return [frozenset(int(item) for item in row) for row in order]


def neighbour_margins(distance: FloatArray, neighbours: int) -> FloatArray:
    """Gap between each row's (k+1)-th and k-th nearest distances, ``gamma_i``."""
    distance = np.array(distance, dtype=float)
    np.fill_diagonal(distance, np.inf)
    ordered = np.sort(distance, axis=1)
    return ordered[:, neighbours] - ordered[:, neighbours - 1]


def certified_rows(distance: FloatArray, errors: FloatArray, neighbours: int) -> FloatArray:
    """Rows whose k-NN set provably equals the target geometry's.

    With exposure errors ``delta_j`` every distance in row ``i`` moves by at most
    ``delta_i + max_j delta_j``. The estimated margin exceeding twice that bound
    certifies the row (the neighbour-margin certificate, applied to estimates).
    """
    errors = np.asarray(errors, dtype=float)
    bound = errors + errors.max()
    return neighbour_margins(distance, neighbours) > 2 * bound


def spearman_mantel(left: FloatArray, right: FloatArray) -> float:
    """Spearman correlation of the strict upper triangles of two distance matrices."""
    upper = np.triu_indices(len(left), 1)
    a, b = rankdata(left[upper]), rankdata(right[upper])
    return float(np.corrcoef(a, b)[0, 1])


def knn_jaccard(left: FloatArray, right: FloatArray) -> float:
    """Jaccard overlap of the undirected edge sets of two graphs."""
    a, b = left > 0, right > 0
    union = np.logical_or(a, b).sum()
    return float(np.logical_and(a, b).sum() / union) if union else 1.0


# --- Covariance models --------------------------------------------------------------


@dataclass(frozen=True)
class Covariance:
    """A fitted training-window covariance and its estimation evidence."""

    name: str
    matrix: FloatArray
    spatial: float = float("nan")
    train_loglik: float = float("nan")


def factor_covariance(
    name: str, loadings: FloatArray, factor_cov: FloatArray, residuals: FloatArray
) -> Covariance:
    """``B Omega B' + diag(residual variances)``."""
    common = loadings @ factor_cov @ loadings.T
    return Covariance(name, common + np.diag(residuals.var(axis=0)))


def spatial_residual_fit(
    residuals: FloatArray, weights: FloatArray
) -> tuple[float, FloatArray, float]:
    """Gaussian ML of ``e_t = (I - lambda W)^-1 eps_t`` with ``eps_t ~ N(0, diag(d))``.

    Profiling out ``d_i = mean_t eps_it^2`` leaves
    ``T log|det(I - lambda W)| - T/2 sum_i log d_i(lambda)`` up to a constant.
    """
    graph = spatial_ml.Graph.of(weights)
    periods = len(residuals)
    lagged = residuals @ weights.T

    def loglik(value: float) -> float:
        innovations = residuals - value * lagged
        variance = np.mean(innovations**2, axis=0)
        logdet = float(np.log(np.abs(1 - value * graph.spectrum)).sum())
        return periods * logdet - periods / 2 * float(np.log(variance).sum())

    low, high = graph.interval
    grid = np.linspace(low, high, 81)
    values = np.array([loglik(float(point)) for point in grid])
    best = int(np.argmax(values))
    bracket = (float(grid[max(best - 1, 0)]), float(grid[min(best + 1, len(grid) - 1)]))
    result = minimize_scalar(
        lambda value: -loglik(float(value)),
        bounds=bracket,
        method="bounded",
        options={"xatol": 1e-9},
    )
    value = float(result.x)
    variance = np.mean((residuals - value * lagged) ** 2, axis=0)
    return value, variance, loglik(value)


def spatial_covariance(
    name: str,
    loadings: FloatArray,
    factor_cov: FloatArray,
    residuals: FloatArray,
    weights: FloatArray,
) -> Covariance:
    """``B Omega B' + P D P'`` with the training-window spatial fit."""
    value, variance, loglik = spatial_residual_fit(residuals, weights)
    inverse = np.linalg.inv(np.eye(len(weights)) - value * weights)
    residual = (inverse * variance) @ inverse.T
    common = loadings @ factor_cov @ loadings.T
    return Covariance(name, common + residual, value, loglik)


def monthly_scores(covariance: FloatArray, returns: FloatArray) -> tuple[FloatArray, FloatArray]:
    """Per-month mean Gaussian negative log score and GMV realized return.

    Each month uses only its observed issuers: the score is the marginal Gaussian
    density on that subset, divided by its size, and the minimum-variance weights are
    computed from the same sub-covariance. Months without two observed issuers are NaN.
    """
    scores = np.full(len(returns), np.nan)
    portfolio = np.full(len(returns), np.nan)
    for month, row in enumerate(returns):
        observed = np.isfinite(row)
        if observed.sum() < 2:
            continue
        sub = covariance[np.ix_(observed, observed)]
        factor = np.linalg.cholesky(sub)
        values = row[observed]
        whitened = np.linalg.solve(factor, values)
        logdet = 2 * np.log(np.diag(factor)).sum()
        scores[month] = 0.5 * (logdet + whitened @ whitened + observed.sum() * np.log(2 * np.pi))
        scores[month] /= observed.sum()
        ones = np.linalg.solve(factor.T, np.linalg.solve(factor, np.ones(observed.sum())))
        portfolio[month] = float(ones @ values / ones.sum())
    return scores, portfolio


# --- Stage --------------------------------------------------------------------------


def _paired(
    scores: dict[str, FloatArray], pairs: list[tuple[str, str]], spec: AptSpec
) -> pd.DataFrame:
    """Monthly score-difference means with stationary-bootstrap intervals and Holm."""
    rows = []
    for name, reference in pairs:
        difference = scores[reference] - scores[name]  # positive favours ``name``.
        difference = difference[np.isfinite(difference)]
        block = block_length(difference)
        orders = stationary_orders(len(difference), spec.score_draws, block, spec.seed)
        means = difference[orders].mean(axis=1)
        low, high, count = percentile_interval(means)
        standard = means.std(ddof=1)
        statistic = difference.mean() / standard if standard > 0 else np.nan
        rows.append(
            {
                "model": name,
                "reference": reference,
                "mean_improvement": float(difference.mean()),
                "low": low,
                "high": high,
                "draws": count,
                "block": block,
                "p_value": float(2 * norm.sf(abs(statistic))) if np.isfinite(statistic) else np.nan,
            }
        )
    frame = pd.DataFrame(rows)
    frame["p_holm"] = holm(frame["p_value"])
    return frame


def _returns(
    monthly: pd.DataFrame, issuers: tuple[str, ...], months: pd.DatetimeIndex, rf: pd.Series
) -> pd.DataFrame:
    frame = monthly.loc[monthly["observed"].astype(bool)].copy()
    frame["month"] = pd.to_datetime(frame["month"]).dt.to_period("M").dt.to_timestamp(how="end")
    frame["month"] = frame["month"].dt.normalize()
    wide = frame.pivot_table(index="month", columns="issuer_id", values="total_return")
    wide = wide.reindex(index=months, columns=list(issuers))
    return wide.sub(rf.reindex(months), axis=0)


def run(  # noqa: PLR0915 -- one pre-specified comparison, kept in one place.
    panel: Path,
    representations: Path,
    factors: Path,
    output: Path,
    params: Path,
) -> None:
    """Train on 2016-2020 monthly returns, score 2021-2025, and save every comparison."""
    inputs = load(panel, representations, params)
    spec = AptSpec.read(params)
    output.mkdir(parents=True, exist_ok=True)
    study = inputs.spec
    quarter = study.window(spec.formation)[0]
    train_months = spec.months(spec.train_start, spec.train_end)
    test_months = spec.months(spec.test_start, spec.test_end)
    french = monthly_factors(factors)
    missing = train_months.union(test_months).difference(pd.DatetimeIndex(french.index))
    if len(missing):
        message = f"French factors are missing {len(missing)} study months."
        raise ValueError(message)
    rows = inputs.roster(quarter)
    # The prepared inventory (verified by ``load``) includes the issuer-month ledger.
    monthly = pd.read_parquet(panel / "issuer_monthly.parquet")
    train = _returns(monthly, tuple(rows["issuer_id"].astype(str)), train_months, french["RF"])
    complete = train.notna().all(axis=0)
    rows = rows.loc[rows["issuer_id"].isin(complete.index[complete])].reset_index(drop=True)
    issuers = tuple(rows["issuer_id"].astype(str))
    train = train[list(issuers)]
    test = _returns(monthly, issuers, test_months, french["RF"])
    factor_values = french.loc[train_months, list(spec.factors)].to_numpy(float)
    omega = np.cov(factor_values, rowvar=False)
    loadings, _, residuals = factor_loadings(train.to_numpy(float), factor_values)
    exposures = loadings @ symmetric_root(omega)
    market = french.loc[train_months, ["Mkt-RF"]].to_numpy(float)
    beta, _, capm_residuals = factor_loadings(train.to_numpy(float), market)

    states = inputs.store.states(quarter, issuers) if inputs.store is not None else {}
    distances: dict[str, FloatArray] = {
        "characteristics:fernandez_joint": characteristic_distances(inputs.histories(rows))[
            "joint"
        ][0],
        "exposures:estimated": euclidean_distance(exposures),
    }
    recovery = []
    readouts: dict[str, FloatArray] = {}
    for key, state in sorted(states.items()):
        values = np.asarray(state, float)
        if not np.isfinite(values).all():
            message = f"{key}: frozen states must be finite."
            raise ValueError(message)
        distances[f"{key}:raw"] = representation_distance(values)
        predicted, alphas = crossfit_readout(
            values, exposures, spec.folds, spec.ridge_alphas, spec.seed, clip=spec.clip
        )
        readouts[key] = predicted
        distances[f"{key}:calibrated"] = euclidean_distance(predicted)
        total = np.sum((exposures - exposures.mean(axis=0)) ** 2, axis=0)
        error = np.sum((exposures - predicted) ** 2, axis=0)
        residual = np.linalg.norm(exposures - predicted, axis=1)
        certified = certified_rows(distances[f"{key}:calibrated"], residual, spec.neighbours)
        recovery.append(
            {
                "representation": key,
                "certified_share": float(certified.mean()),
                "rms_error": float(np.sqrt(np.mean(residual**2))),
                "median_margin": float(
                    np.median(neighbour_margins(distances[f"{key}:calibrated"], spec.neighbours))
                ),
                "r_squared": float(1 - error.sum() / total.sum()),
                **{
                    f"r_squared:{name}": float(1 - error[index] / total[index])
                    for index, name in enumerate(spec.factors)
                },
                "alphas": [float(alpha) for alpha in alphas],
            }
        )

    graphs = {name: knn_weights(distance, spec.neighbours) for name, distance in distances.items()}
    graphs["industry:sic2"] = industry_weights(rows["sic"])
    graphs["null:relabelled"] = permuted(graphs["characteristics:fernandez_joint"], spec.seed)
    exposure_distance = distances["exposures:estimated"]
    exposure_graph = graphs["exposures:estimated"]
    rng = np.random.default_rng(spec.seed)
    nodes = rng.integers(len(issuers), size=(spec.mantel_draws, len(issuers)))
    alignment = []
    for name, distance in distances.items():
        if name == "exposures:estimated":
            continue
        draws = np.array(
            [
                spearman_mantel(distance[np.ix_(row, row)], exposure_distance[np.ix_(row, row)])
                for row in nodes
            ]
        )
        low, high, _ = percentile_interval(draws)
        alignment.append(
            {
                "geometry": name,
                "mantel_exposure": spearman_mantel(distance, exposure_distance),
                "low": low,
                "high": high,
                "knn_jaccard_exposure": knn_jaccard(graphs[name], exposure_graph),
            }
        )

    models = [
        factor_covariance("capm", beta, np.atleast_2d(np.var(market, ddof=1)), capm_residuals),
        factor_covariance("apt", loadings, omega, residuals),
    ]
    models += [
        spatial_covariance(f"spatial_apt|{name}", loadings, omega, residuals, weights)
        for name, weights in graphs.items()
    ]
    test_values = test.to_numpy(float)
    scores: dict[str, FloatArray] = {}
    portfolios: dict[str, FloatArray] = {}
    summary: list[dict[str, Any]] = []
    for model in models:
        score, portfolio = monthly_scores(model.matrix, test_values)
        scores[model.name], portfolios[model.name] = score, portfolio
        summary.append(
            {
                "model": model.name,
                "spatial": model.spatial,
                "train_loglik": model.train_loglik,
                "test_score": float(np.nanmean(score)),
                "gmv_volatility_annual": float(np.nanstd(portfolio, ddof=1) * np.sqrt(12)),
                "test_months": int(np.isfinite(score).sum()),
            }
        )
    names = [model.name for model in models]
    pairs = [(name, "apt") for name in names if name != "apt"]
    pairs += [
        (name, "spatial_apt|characteristics:fernandez_joint")
        for name in names
        if name.startswith("spatial_apt|") and name != "spatial_apt|characteristics:fernandez_joint"
    ]
    for key in states:
        pairs.append((f"spatial_apt|{key}:calibrated", f"spatial_apt|{key}:raw"))
        rung = key.split(":", 1)[0]
        if not key.endswith(":direct"):
            for kind in ("raw", "calibrated"):
                pairs.append((f"spatial_apt|{key}:{kind}", f"spatial_apt|{rung}:direct:{kind}"))
    comparisons = _paired(scores, list(dict.fromkeys(pairs)), spec)

    observed = test.notna()
    atomic_parquet(output / "models.parquet", pd.DataFrame(summary))
    atomic_parquet(output / "comparisons.parquet", comparisons)
    atomic_parquet(output / "recovery.parquet", pd.DataFrame(recovery))
    atomic_parquet(output / "alignment.parquet", pd.DataFrame(alignment))
    atomic_parquet(
        output / "monthly.parquet",
        pd.DataFrame(
            {
                "month": np.repeat(test_months, len(names)),
                "model": np.tile(names, len(test_months)),
                "score": np.column_stack([scores[name] for name in names]).ravel(),
                "gmv_return": np.column_stack([portfolios[name] for name in names]).ravel(),
            }
        ),
    )
    atomic_parquet(
        output / "exposures.parquet",
        pd.DataFrame(exposures, columns=list(spec.factors)).assign(issuer_id=list(issuers)),
    )
    manifest: dict[str, Any] = {
        "apt_sha256": spec.digest,
        "study_sha256": study.digest,
        "apt": asdict(spec),
        "formation": spec.formation,
        "states_quarter": quarter.strftime("%Y-%m-%d"),
        "roster_issuers": len(inputs.roster(quarter)),
        "issuers": len(issuers),
        "train_months": len(train_months),
        "test_months": len(test_months),
        "test_issuer_months": int(observed.to_numpy().sum()),
        "test_issuers_exiting": int((~observed.iloc[-1]).sum()),
        "representations": sorted(states),
        "selection": "roster issuers at the window start with every training month observed",
        "mean": "zero for every model; scores compare second moments",
    }
    write_json(output / "manifest.json", manifest)
