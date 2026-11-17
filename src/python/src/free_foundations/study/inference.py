"""Quarterly paired inference without deleting missing calendar observations."""

from __future__ import annotations

# Pivot rejects duplicate keys; aggregation would obscure mismatched score rows.
# ruff: noqa: PD010
from functools import lru_cache
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

from free_foundations.study.spec import RUNGS

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence

    from numpy.typing import NDArray


@lru_cache(maxsize=16)
def stationary_orders(
    periods: int, draws: int = 9999, block: int = 4, seed: int = 42
) -> NDArray[np.int64]:
    """Resample the full quarterly clock, including positions with missing scores.

    All procedures reuse these orders. Continuations wrap around the calendar;
    new blocks start uniformly, as in the stationary bootstrap.
    """
    if periods < 0 or draws < 0 or block < 1:
        msg = "Calendar length/draws must be nonnegative and block positive."
        raise ValueError(msg)
    orders = np.empty((draws, periods), dtype=np.int64)
    if periods and draws:
        rng = np.random.default_rng(seed)
        orders[:, 0] = rng.integers(periods, size=draws)
        for position in range(1, periods):
            restart = rng.random(draws) < 1 / block
            starts = rng.integers(periods, size=draws)
            orders[:, position] = np.where(restart, starts, (orders[:, position - 1] + 1) % periods)
    orders.setflags(write=False)
    return orders


def generated_beta_indices(
    quarters: Iterable[object], draws: int = 999, block: int = 4, seed: int = 42
) -> pd.DataFrame:
    """Include the original order as replicate zero and every requested MM refit.

    Failed bootstrap fits remain failed replicates. There is no spare-draw search
    that selects the first converged estimates.
    """
    labels = pd.to_datetime([str(value) for value in quarters]).strftime("%Y-%m-%d").to_numpy()
    orders = stationary_orders(len(labels), draws, block, seed)
    all_orders = np.vstack([np.arange(len(labels), dtype=np.int64), orders])
    return pd.DataFrame(
        {
            "replicate": np.repeat(np.arange(draws + 1), len(labels)),
            "position": np.tile(np.arange(len(labels)), draws + 1),
            "quarter": labels[all_orders.ravel()],
        }
    )


def _interval(values: NDArray[np.float64]) -> tuple[float, float, int]:
    finite = values[np.isfinite(values)]
    if not len(finite):
        return float("nan"), float("nan"), 0
    lower, upper = np.percentile(finite, [2.5, 97.5])
    return float(lower), float(upper), len(finite)


def scientific_contrasts(methods: Iterable[str]) -> list[tuple[str, str, str]]:
    """Declare direct scientific comparisons, always within one variance treatment.

    Planned unavailable score cells belong in ``methods`` too, so an unidentified
    comparison remains an explicit unavailable interval rather than disappearing.
    Correlation scores, whose forecasts share raw-return marginal variances, lead
    each family. The spatial-matched arm uses the exact Gram chord geometry.
    """
    names = set(methods)
    contrasts: set[tuple[str, str, str]] = set()

    def add(left: str, right: str, family: str) -> None:
        if left in names and right in names and left != right:
            contrasts.add((left, right, family))

    for method in names:
        variance = method.rsplit("|", 1)[-1]
        reference = f"ff5_mom_diagonal|{variance}"
        add(method, reference, "factor_reference")
        parts = method.rsplit("|", 2)
        if len(parts) != 3:
            continue
        geometry, arm, variance = parts
        if arm == "gram":
            add(
                method,
                f"{geometry}|spatial_matched|{variance}",
                "gram_minus_matched_spatial",
            )
        if arm == "spatial_matched":
            add(method, f"{geometry}|spatial|{variance}", "spatial_geometry_sensitivity")
        if geometry.endswith("@decoded"):
            add(method, f"{geometry[:-8]}|{arm}|{variance}", "decoded_minus_native")
        if "/" not in geometry:
            continue
        rung, model = geometry.split("/", 1)
        add(method, f"fernandez_joint|{arm}|{variance}", "learned_minus_fernandez")
        if rung in RUNGS[1:]:
            previous = RUNGS[RUNGS.index(rung) - 1]
            add(method, f"{previous}/{model}|{arm}|{variance}", "adjacent_information_rungs")
    return sorted(
        contrasts,
        key=lambda item: (item[0].rsplit("|", 1)[-1] != "correlation", item[2], item[0], item[1]),
    )


def paired_intervals(  # noqa: PLR0913 -- declared resampling settings.
    scores: pd.DataFrame,
    *,
    calendar: Iterable[object] | None = None,
    pairs: Sequence[tuple[str, str]] | None = None,
    draws: int = 9999,
    blocks: tuple[int, ...] = (4, 2, 8),
    seed: int = 42,
) -> pd.DataFrame:
    """Conditional intervals for mean paired per-issuer Gaussian score differences.

    The roster and observed-outcome mask must agree within every quarter. Missing
    score pairs retain their calendar positions. Intervals describe the observed
    paired-score estimand; they do not identify risk for unobserved returns.
    """
    columns = [
        "left",
        "right",
        "contrast_family",
        "calendar_quarters",
        "defined_quarters",
        "difference",
        "block_quarters",
        "requested_draws",
        "defined_draws",
        "lower",
        "upper",
        "share_nonpositive",
        "status",
        "inference",
    ]
    if scores.empty:
        return pd.DataFrame(columns=columns)
    required = {"quarter", "method", "score_per_issuer", "mask_sha256"}
    if not required.issubset(scores):
        msg = f"Score table lacks {sorted(required - set(scores.columns))}."
        raise ValueError(msg)
    if scores.duplicated(["quarter", "method"]).any():
        msg = "Duplicate quarterly method scores."
        raise ValueError(msg)
    if scores.groupby("quarter")["mask_sha256"].nunique().gt(1).any():
        msg = "Paired methods have different observed outcome masks."
        raise ValueError(msg)
    wide = scores.pivot(index="quarter", columns="method", values="score_per_issuer")
    wide.index = pd.DatetimeIndex(wide.index)
    dates = (
        pd.DatetimeIndex(pd.to_datetime([str(value) for value in calendar]))
        if calendar is not None
        else pd.DatetimeIndex(sorted(wide.index))
    )
    wide = wide.reindex(dates)
    names = sorted(map(str, wide.columns))
    if pairs is None:
        selected = scientific_contrasts(names)
        if not selected:
            selected = [(name, names[0], "declared_reference") for name in names[1:]]
    else:
        selected = [(left, right, "declared_pair") for left, right in pairs]
    rows: list[dict[str, object]] = []
    for left, right, family in selected:
        if left not in wide or right not in wide:
            msg = f"Missing declared score contrast: {left}, {right}."
            raise ValueError(msg)
        differences = (wide[left] - wide[right]).to_numpy(dtype=float)
        defined = np.isfinite(differences)
        mean = float(differences[defined].mean()) if defined.any() else float("nan")
        for block in blocks:
            orders = stationary_orders(len(dates), draws, block, seed)
            sampled = differences[orders]
            counts = np.isfinite(sampled).sum(axis=1)
            totals = np.where(np.isfinite(sampled), sampled, 0).sum(axis=1)
            means = np.divide(totals, counts, out=np.full(draws, np.nan), where=counts > 0)
            lower, upper, completed = _interval(means)
            rows.append(
                {
                    "left": left,
                    "right": right,
                    "contrast_family": family,
                    "calendar_quarters": len(dates),
                    "defined_quarters": int(defined.sum()),
                    "difference": mean,
                    "block_quarters": block,
                    "requested_draws": draws,
                    "defined_draws": completed,
                    "lower": lower,
                    "upper": upper,
                    "share_nonpositive": (
                        float(np.mean(means[np.isfinite(means)] <= 0))
                        if completed
                        else float("nan")
                    ),
                    "status": "available" if completed else "unavailable",
                    "inference": "conditional on fitted procedures; paired quarterly calendar",
                }
            )
    return pd.DataFrame(rows, columns=columns)


def summarize_generated(draws: pd.DataFrame, requested_draws: int) -> pd.DataFrame:
    """Report every requested generated-beta replicate, including convergence failures."""
    keys = ["quarter", "method", "estimator"]
    columns = [
        *keys,
        "parameter",
        "requested_draws",
        "defined_draws",
        "failed_draws",
        "bootstrap_se",
        "lower",
        "upper",
        "status",
        "inference",
    ]
    if draws.empty:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, object]] = []
    for identifiers, group in draws.groupby(keys, dropna=False, sort=True):
        for parameter in ("premium_market", "intensity"):
            if parameter not in group:
                continue
            values = group[parameter].where(group["status"].eq("available")).to_numpy(float)
            lower, upper, completed = _interval(values)
            valid = values[np.isfinite(values)]
            rows.append(
                dict(zip(keys, identifiers, strict=True))
                | {
                    "parameter": parameter,
                    "requested_draws": requested_draws,
                    "defined_draws": completed,
                    "failed_draws": requested_draws - completed,
                    "bootstrap_se": float(valid.std(ddof=1)) if completed > 1 else float("nan"),
                    "lower": lower,
                    "upper": upper,
                    "status": "available"
                    if completed == requested_draws and completed
                    else "incomplete",
                    "inference": "MM reestimated; fixed network; intervals over defined refits",
                }
            )
    return pd.DataFrame(rows, columns=columns)
