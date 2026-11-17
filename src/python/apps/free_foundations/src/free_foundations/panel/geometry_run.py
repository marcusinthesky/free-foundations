"""Direct Gram covariances and descriptive coordinates from frozen feature states."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd
from scipy.linalg import orth, subspace_angles
from scipy.stats import spearmanr

from free_foundations.data import write_json
from free_foundations.panel import geometry
from free_foundations.panel.decoding import FACTORS, decode, intercept_only
from free_foundations.panel.design import FOUNDATION_READOUTS, STUDY
from free_foundations.panel.evaluation import (
    CALIBRATION,
    EVALUATION,
    Panel,
    daily_frame,
    update,
)
from free_foundations.panel.inference import BLOCKS, REPLICATES, contrasts
from free_foundations.panel.likelihood import correlation_only, gaussian_daily
from free_foundations.panel.networks import classical
from free_foundations.representations.cache import digest_file
from free_foundations.representations.distance import pairwise_distance

if TYPE_CHECKING:
    from free_foundations.contracts import FloatArray
    from free_foundations.panel.decoding import Targets
    from free_foundations.panel.observations import Annual

LOGGER = logging.getLogger(__name__)
OUTPUT = Path("research/panel/geometry")
ENERGY_RELATIVE_TOLERANCE = 1e-24
RANDOM_SUBSPACE_DRAWS, RANDOM_SUBSPACE_SEED = 199, 42
CLASSICAL = (*(f"fernandez_{name}" for name in STUDY.characteristics), "fernandez_joint")
APPROACHES = (
    *CLASSICAL,
    *(f"histories{suffix}__{name}" for name in FOUNDATION_READOUTS for suffix in ("", "@decoded")),
    "histories@decoded__intercept_only",
)
type Row = dict[str, Any]


def configuration() -> Row:
    """A bounded retrospective extension, independent of extraction identity."""
    return {
        "approaches": APPROACHES,
        "models": ("gram", "spatial"),
        "variance": ("full", "correlation"),
        "years": (*CALIBRATION, *EVALUATION),
        "calibration": [2016, 2019],
        "evaluation": [2020, 2025],
        "encoder_support": 256,
        "decoded_rank": FACTORS,
        "pcoa_rank": 5,
        "pcoa_cutoff": {
            "near_tie_relative_tolerance": geometry.CUTOFF_NEAR_TIE_RELATIVE_TOLERANCE,
            "tie_tolerance": "existing numerical eigenvalue tolerance",
            "tie_policy": "retain prescribed rank and flag nonunique subspace",
        },
        "energy_diagnostics": {
            "denominator": "uncentered total energy and cross-sectionally demeaned energy",
            "relative_energy_tolerance": ENERGY_RELATIVE_TOLERANCE,
            "random_subspace_draws": RANDOM_SUBSPACE_DRAWS,
            "random_subspace_seed": RANDOM_SUBSPACE_SEED,
            "random_subspace_quantiles": [0.025, 0.975],
            "random_subspace": "rank matched, centered Gaussian QR; return independent",
            "status": "additional declared diagnostics; original reconstruction shares retained",
        },
        "decoded_geometry": "unit-normalized exposures, distinct from principal Euclidean geometry",
        "native_direct": "original appended unit coordinate before row normalization",
        "theta_bounds": [0, geometry.THETA_MAX],
        "calibration_scales": "empirical RMS of each annual realized factor-residual block",
        "forecast_scales": "empirical RMS of the existing prior factor-residual window",
        "spatial_scales": "existing profiled diagonal innovation variances",
        "primary_variance": "correlation",
        "common_marginals": "prior raw-return sample standard deviations, ddof=1",
        "bootstrap": {"blocks": BLOCKS, "replicates": REPLICATES, "seed": 42},
        "pcoa_returns": "descriptive projection; annual axes are not pooled",
        "development": "retrospective extension, no new holdout or model selection",
    }


def construct(
    four: pd.DataFrame,
    year: int,
    tickers: tuple[str, ...],
    states: dict[str, FloatArray],
    calibration: Targets,
) -> tuple[dict[str, FloatArray], dict[str, FloatArray]]:
    """Pair each signed Gram matrix with distances of the identical unit geometry."""
    distances = classical(four, year, tickers, STUDY.characteristics, STUDY.history)
    grams = {name: geometry.chord_gram(distance) for name, distance in distances.items()}
    individual = [grams[f"fernandez_{name}"] for name in STUDY.characteristics]
    np.testing.assert_allclose(
        grams["fernandez_joint"], geometry.joint_gram(individual), atol=1e-12
    )
    for name in FOUNDATION_READOUTS:
        values = states[name]
        native = np.column_stack([values, np.ones(len(values))]) if name == "direct" else values
        predicted, _ = decode(values, calibration.reference[FACTORS], tickers)
        for suffix, vectors in (("", native), ("@decoded", predicted)):
            label = f"histories{suffix}__{name}"
            grams[label] = geometry.unit_gram(vectors)
            distances[label] = pairwise_distance(vectors)
            np.testing.assert_allclose(
                grams[label], 1 - distances[label] ** 2 / 2, atol=1e-10, rtol=0
            )
    label = "histories@decoded__intercept_only"
    null = intercept_only(calibration.reference[FACTORS], tickers)
    grams[label], distances[label] = geometry.unit_gram(null), pairwise_distance(null)
    for suffix in ("", "43", "44"):
        np.testing.assert_allclose(
            grams[f"histories@decoded__kumo_random{suffix}__late"], grams[label], atol=1e-10
        )
    if set(grams) != set(APPROACHES):
        message = "Incomplete direct geometry inventory."
        raise ValueError(message)
    return grams, distances


def declared_pairs() -> list[tuple[str, str, str]]:
    """Prescribed model, representation, decoding, and reset comparisons."""
    pairs: list[tuple[str, str, str]] = []
    for variance in ("full", "correlation"):
        pairs.extend(
            ("gram vs spatial", f"{name}|gram|{variance}", f"{name}|spatial|{variance}")
            for name in APPROACHES
        )
        for model in ("gram", "spatial"):
            reference = f"fernandez_joint|{model}|{variance}"
            pairs.extend(
                ("geometry vs joint", f"{name}|{model}|{variance}", reference)
                for name in APPROACHES
                if name != "fernandez_joint"
            )
            for name in FOUNDATION_READOUTS:
                decoded = f"histories@decoded__{name}|{model}|{variance}"
                pairs.extend(
                    (
                        ("decoded vs native", decoded, f"histories__{name}|{model}|{variance}"),
                        (
                            "decoded vs intercept only",
                            decoded,
                            f"histories@decoded__intercept_only|{model}|{variance}",
                        ),
                    )
                )
                if "_random" in name:
                    trained = name.partition("_random")[0] + "__late"
                    pairs.extend(
                        (
                            "pretrained vs reset",
                            f"histories{suffix}__{trained}|{model}|{variance}",
                            f"histories{suffix}__{name}|{model}|{variance}",
                        )
                        for suffix in ("", "@decoded")
                    )
    return pairs


def energy_diagnostics(values: FloatArray, projected: FloatArray) -> dict[str, float | bool]:
    """Separate total return energy from cross-sectionally relative return energy.

    The retained centered characteristic space excludes uniform cross-sectional
    loadings. Neither projection ratio is a conventional factor-covariance R-squared.
    """
    total = float(np.sum(values**2))
    relative = values - values.mean(axis=1, keepdims=True)
    centered = float(np.sum(relative**2))
    explained = float(np.sum(projected**2))
    total_defined = total > 0
    relative_defined = total_defined and centered > ENERGY_RELATIVE_TOLERANCE * total
    return {
        "total_energy": total,
        "relative_energy": centered,
        "projected_energy": explained,
        "energy_defined": total_defined,
        "relative_defined": relative_defined,
        "reconstruction_share": 1 - float(np.sum((values - projected) ** 2)) / total
        if total_defined
        else np.nan,
        "relative_reconstruction_share": explained / centered if relative_defined else np.nan,
        "relative_energy_share": centered / total if total_defined else np.nan,
    }


def random_reference(annual: Annual, rank: int) -> dict[str, float]:
    """Reference bands from fixed return-independent centered orthonormal subspaces.

    Raw and residual blocks share frames, as do all geometries with the same
    cohort and retained rank. Ranks use nested columns of each random frame.
    The quantiles describe random directions, not sampling uncertainty of PCoA.
    """
    firms = len(annual.tickers)
    if not 0 <= rank <= min(5, firms - 1):
        message = "Random reference rank must fit the retained centered ambient space."
        raise ValueError(message)
    order = np.argsort(np.asarray(annual.tickers))
    raw = annual.raw_realized[:, order]
    residual = annual.realized[:, order]
    centered = [values - values.mean(axis=1, keepdims=True) for values in (raw, residual)]
    rng = np.random.default_rng(RANDOM_SUBSPACE_SEED)
    frames: list[FloatArray] = []
    if rank:
        for _ in range(RANDOM_SUBSPACE_DRAWS):
            gaussian = rng.normal(size=(firms, min(5, firms - 1)))
            gaussian -= gaussian.mean(axis=0)
            frame, _ = np.linalg.qr(gaussian, mode="reduced")
            frames.append(frame[:, :rank])
    result = {"random_relative_expectation": rank / (firms - 1) if firms > 1 else np.nan}
    for prefix, values, original in zip(
        ("raw", "residual"), centered, (raw, residual), strict=True
    ):
        energy = float(np.sum(values**2))
        total = float(np.sum(original**2))
        if energy <= ENERGY_RELATIVE_TOLERANCE * total:
            mean, lower, upper = np.nan, np.nan, np.nan
        elif rank:
            scores = (
                np.sum(
                    (values @ np.column_stack(frames)).reshape(
                        len(values), RANDOM_SUBSPACE_DRAWS, rank
                    )
                    ** 2,
                    axis=(0, 2),
                )
                / energy
            )
            mean = float(scores.mean())
            lower, upper = map(float, np.percentile(scores, [2.5, 97.5]))
        else:
            mean, lower, upper = 0.0, 0.0, 0.0
        result.update(
            {
                f"{prefix}_random_relative_mean": mean,
                f"{prefix}_random_relative_lower": lower,
                f"{prefix}_random_relative_upper": upper,
            }
        )
    return result


def describe(  # noqa: PLR0913, PLR0917 -- paired geometry, sample and archive metadata.
    gram: FloatArray,
    annual: Annual,
    characteristics: pd.DataFrame,
    year: int,
    approach: str,
    records: dict[str, list[Row]],
    *,
    references: dict[int, dict[str, float]] | None = None,
) -> tuple[tuple[str, ...], FloatArray]:
    """Archive spectral coordinates, unit-exposure portfolios, and interpretation."""
    fitted = geometry.pcoa(gram, tickers=annual.tickers)
    coordinates, weights = fitted.coordinates, fitted.weights
    positive = fitted.eigenvalues > fitted.tolerance
    total = float(fitted.eigenvalues[positive].sum())
    share = np.where(positive, fitted.eigenvalues, 0) / total if total else np.zeros(len(gram))
    common = {"approach": approach, "year": year}
    records["spectrum"].extend(
        common
        | {
            "component": index + 1,
            "eigenvalue": float(value),
            "positive": bool(positive[index]),
            "variance_share": float(share[index]),
            "cumulative_variance_share": float(share[: index + 1].sum()),
        }
        for index, value in enumerate(fitted.eigenvalues)
    )
    raw = annual.raw_realized @ weights
    residual = annual.realized @ weights
    projected = (raw @ coordinates.T, residual @ coordinates.T)
    energies = {
        f"{prefix}_{key}": value
        for prefix, values, estimate in zip(
            ("raw", "residual"), (annual.raw_realized, annual.realized), projected, strict=True
        )
        for key, value in energy_diagnostics(values, estimate).items()
    }
    retained = coordinates.shape[1]
    references = {} if references is None else references
    if retained not in references:
        references[retained] = random_reference(annual, retained)
    records["pcoa-summary"].append(
        common
        | {
            "firms": len(annual.tickers),
            "requested_rank": 5,
            "rank": retained,
            "positive_rank": fitted.rank,
            "rank_shortfall": retained < 5,
            "tolerance": fitted.tolerance,
            "variance_share": fitted.variance_share,
            **energies,
            **references[retained],
            "cutoff_applicable": fitted.cutoff_applicable,
            "cutoff_gap": fitted.cutoff_gap,
            "cutoff_relative_gap": fitted.cutoff_relative_gap,
            "cutoff_tied": fitted.cutoff_tied,
            "cutoff_near_tied": fitted.cutoff_near_tied,
            "subspace_unique": fitted.subspace_unique,
            "max_gross_weight": float(np.abs(weights).sum(axis=0).max()) if retained else 0,
        }
    )
    for index, ticker in enumerate(annual.tickers):
        fields = {"ticker": ticker, **common}
        records["coordinates"].append(
            fields
            | {
                f"component_{axis + 1}": float(value)
                for axis, value in enumerate(coordinates[index])
            }
        )
        records["weights"].append(
            fields
            | {f"component_{axis + 1}": float(value) for axis, value in enumerate(weights[index])}
        )
    latest = characteristics.xs(year - 1, level="year").loc[list(annual.tickers)]
    for axis in range(retained):
        for name in STUDY.characteristics:
            values = latest[name].to_numpy(dtype=float)
            association = (
                float(spearmanr(coordinates[:, axis], values).statistic)
                if np.ptp(values) > 0
                else np.nan
            )
            records["characteristic-associations"].append(
                common | {"component": axis + 1, "characteristic": name, "spearman": association}
            )
        order = np.lexsort((np.asarray(annual.tickers), coordinates[:, axis]))
        for side, selected in (("low", order[:5]), ("high", order[-5:][::-1])):
            records["extremes"].extend(
                common
                | {
                    "component": axis + 1,
                    "side": side,
                    "position": position + 1,
                    "ticker": annual.tickers[index],
                    "coordinate": float(coordinates[index, axis]),
                }
                for position, index in enumerate(selected)
            )
        records["component-returns"].extend(
            common
            | {
                "component": axis + 1,
                "date": date,
                "excess": float(raw[index, axis]),
                "residual": float(residual[index, axis]),
            }
            for index, date in enumerate(annual.dates)
        )
        for other in range(retained):
            records["component-covariance"].append(
                common
                | {
                    "component": axis + 1,
                    "other": other + 1,
                    "excess_covariance": float(np.cov(raw[:, axis], raw[:, other])[0, 1]),
                    "residual_covariance": float(
                        np.cov(residual[:, axis], residual[:, other])[0, 1]
                    ),
                }
            )
    return annual.tickers, coordinates


def stability(
    previous: tuple[tuple[str, ...], FloatArray],
    current: tuple[tuple[str, ...], FloatArray],
    year: int,
    approach: str,
) -> Row:
    """Compare centered coordinate subspaces on the shared firms, without matching axes."""
    common = sorted(set(previous[0]) & set(current[0]))
    bases = []
    for tickers, coordinates in (previous, current):
        rows = [tickers.index(ticker) for ticker in common]
        values = coordinates[rows]
        bases.append(
            orth(values - values.mean(axis=0), rcond=1e-10) if common else np.empty((0, 0))
        )
    angles = subspace_angles(*bases) if all(base.shape[1] for base in bases) else np.array([])
    return {
        "approach": approach,
        "year": year,
        "previous_year": year - 1,
        "common_firms": len(common),
        "previous_rank": bases[0].shape[1],
        "current_rank": bases[1].shape[1],
        "maximum_angle_radians": float(angles.max()) if len(angles) else np.nan,
        "mean_squared_cosine": float(np.mean(np.cos(angles) ** 2)) if len(angles) else np.nan,
    }


def reconcile(daily: pd.DataFrame) -> list[Row]:
    """The same native geometry must reproduce the recorded principal spatial scores."""
    original = pd.read_parquet(STUDY.output / "daily-scores.parquet")
    if not daily.index.equals(original.index):
        message = "Direct geometry evaluation dates differ from the retained study."
        raise ValueError(message)
    rows = []
    for name in (*CLASSICAL, *(f"histories__{name}" for name in FOUNDATION_READOUTS)):
        kernel = "exp" if name in CLASSICAL else "matched"
        for variance, innovation in (("full", "diagonal"), ("correlation", "correlation")):
            left, right = f"{name}|spatial|{variance}", f"{name}|{kernel}|{innovation}"
            np.testing.assert_allclose(daily[left], original[right], atol=1e-5, rtol=0)
            rows.append(
                {
                    "current": left,
                    "original": right,
                    "max_daily_error": float(np.abs(daily[left] - original[right]).max()),
                }
            )
    return rows


def boundary(coefficient: float, model: str) -> bool:
    """Flag either endpoint of the maintained dependence parameter interval."""
    if model == "gram":
        return coefficient <= 1e-8 or coefficient >= geometry.THETA_MAX - 1e-5
    return abs(coefficient) >= 0.985


def main() -> None:  # noqa: C901, PLR0912, PLR0915 -- one bounded saved-state extension.
    """Run the new comparisons without changing financial inputs or extracting features."""
    from free_foundations.panel.run import (  # noqa: PLC0415 -- orchestration avoids a module cycle.
        MANIFEST,
        financial_sources,
        load_states,
        prepared,
    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    four = pd.read_parquet("research/panel/cache/four.parquet")
    spatial = Panel()
    blocks: dict[str, list[geometry.GramBlock]] = {name: [] for name in APPROACHES}
    coefficients: dict[str, tuple[float, float]] = {}
    scores: dict[str, list[FloatArray]] = {}
    dates: list[str] = []
    records: dict[str, list[Row]] = {
        name: []
        for name in (
            "spectrum",
            "pcoa-summary",
            "coordinates",
            "weights",
            "component-returns",
            "component-covariance",
            "characteristic-associations",
            "extremes",
            "stability",
        )
    }
    previous: dict[str, tuple[tuple[str, ...], FloatArray]] = {}
    previous_unique: dict[str, bool] = {}
    firm_days = 0
    for year in (*CALIBRATION, *EVALUATION):
        annual, calibration = prepared(year)
        grams, distances = construct(four, year, annual.tickers, load_states(year), calibration)
        update(spatial, year, annual, distances)
        references: dict[int, dict[str, float]] = {}
        for approach, gram in grams.items():
            coordinates = describe(
                gram, annual, four, year, approach, records, references=references
            )
            unique = bool(records["pcoa-summary"][-1]["subspace_unique"])
            if approach in previous:
                records["stability"].append(
                    stability(previous[approach], coordinates, year, approach)
                    | {
                        "previous_subspace_unique": previous_unique[approach],
                        "current_subspace_unique": unique,
                        "identified_subspaces": previous_unique[approach] and unique,
                    }
                )
            previous[approach] = coordinates
            previous_unique[approach] = unique
            if year in CALIBRATION:
                blocks[approach].append(geometry.block(annual.realized, gram))
            else:
                covariance = geometry.forecast_covariance(
                    annual.prior, gram, coefficients[approach][0], annual.factor_covariance
                )
                values = annual.raw_realized - annual.raw_prior.mean(axis=0)
                for variance, matrix in (
                    ("full", covariance),
                    ("correlation", correlation_only(covariance, annual.raw_prior)),
                ):
                    column = f"{approach}|gram|{variance}"
                    scores.setdefault(column, []).append(gaussian_daily(values, matrix))
        if year == CALIBRATION[-1]:
            coefficients = {name: geometry.fit(items) for name, items in blocks.items()}
        if year in EVALUATION:
            dates.extend(annual.dates)
            firm_days += annual.raw_realized.size
        LOGGER.info("Direct geometry and PCoA %s: %s approaches", year, len(grams))
    daily = pd.DataFrame(
        {name: np.concatenate(parts) for name, parts in scores.items()},
        index=pd.Index(dates, name="date"),
    )
    spatial_daily = daily_frame(spatial)
    for name in APPROACHES:
        kernel = "exp" if name in CLASSICAL else "matched"
        for variance, innovation in (("full", "diagonal"), ("correlation", "correlation")):
            daily[f"{name}|spatial|{variance}"] = spatial_daily[f"{name}|{kernel}|{innovation}"]
    overlap = reconcile(daily)
    daily.to_parquet(OUTPUT / "daily-scores.parquet")
    annual_rows = [
        {"column": column, "year": year, "score": float(values.sum())}
        for year, group in daily.groupby(pd.to_datetime(daily.index).year)
        for column, values in group.items()
    ]
    pd.DataFrame(annual_rows).to_csv(OUTPUT / "annual-scores.csv", index=False)
    comparisons = []
    for column in daily:
        name, model, variance = str(column).split("|")
        kernel = "exp" if name in CLASSICAL else "matched"
        coefficient, likelihood = (
            coefficients[name] if model == "gram" else spatial.intensities[name, kernel, "diagonal"]
        )
        comparisons.append(
            {
                "column": column,
                "approach": name,
                "model": model,
                "variance": variance,
                "theta": coefficient if model == "gram" else np.nan,
                "lambda": coefficient if model == "spatial" else np.nan,
                "calibration_log_likelihood": likelihood,
                "heldout_log_likelihood": float(daily[column].sum()),
                "score_per_firm_day": float(daily[column].sum()) / firm_days,
                "firm_days": firm_days,
                "boundary": boundary(coefficient, model),
            }
        )
    pd.DataFrame(comparisons).to_csv(OUTPUT / "comparison.csv", index=False)
    contrasts(daily, declared_pairs()).to_csv(OUTPUT / "contrasts.csv", index=False)
    for name, rows in records.items():
        frame = pd.DataFrame(rows)
        if name in {"coordinates", "weights", "component-returns"}:
            frame.to_parquet(OUTPUT / f"{name}.parquet", index=False)
        else:
            frame.to_csv(OUTPUT / f"{name}.csv", index=False)
    write_json(
        OUTPUT / "configuration.json",
        configuration() | {"spatial_reconciliation": overlap, "firm_days": firm_days},
    )
    files = [
        path
        for path in sorted(OUTPUT.iterdir())
        if path.suffix in {".csv", ".json", ".parquet"} and path.name != "manifest.json"
    ]
    write_json(
        OUTPUT / "manifest.json",
        {
            "sha256": {str(path): digest_file(path) for path in files},
            "source_sha256": financial_sources(),
            "representation_manifest_sha256": digest_file(MANIFEST),
            "protocol_sha256": digest_file(OUTPUT / "README.md"),
        },
    )
