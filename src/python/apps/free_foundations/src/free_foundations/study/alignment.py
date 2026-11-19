"""Layer C: parameter-free alignment of network distances with realized co-movement.

For the primary formation, the target is the chord distance of pairwise Pearson
correlations of quarterly excess returns over the window, each pair on its common
quarters. Every network distance (Fernández joint, the direct control, each
foundation model and size) is compared with the target by a Spearman Mantel
correlation. Node-bootstrap intervals resample issuers; paired gaps share draws.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import jax
import numpy as np
import pandas as pd

jax.config.update("jax_enable_x64", True)  # noqa: FBT003 -- statadic numerics need float64.

from statadic.inference.independence import (  # noqa: E402
    mantel_bootstrap_ci,
    mantel_permutation_kernel,
    paired_mantel_bootstrap,
)

from free_foundations.data import write_json  # noqa: E402
from free_foundations.study.inference import holm  # noqa: E402
from free_foundations.study.moments import pairwise_pearson  # noqa: E402
from free_foundations.study.networks import (  # noqa: E402
    characteristic_distances,
    representation_distance,
    size_distance,
)
from free_foundations.study.replication import cohort_outcomes  # noqa: E402
from free_foundations.study.rosters import load  # noqa: E402
from free_foundations.study.source_io import atomic_parquet  # noqa: E402

if TYPE_CHECKING:
    from pathlib import Path

    from free_foundations.contracts import FloatArray

PERMUTATIONS = 999


def _distances(
    histories: dict[str, FloatArray], states: dict[str, FloatArray], equity: FloatArray
) -> dict[str, FloatArray]:
    result = {"fernandez:joint": characteristic_distances(histories)["joint"][0]}
    for key, values in states.items():
        result[key] = representation_distance(values)
    if np.all(equity > 0):
        result["size"] = size_distance(equity)
    return result


def run(panel: Path, representations: Path | None, output: Path, params: Path) -> None:
    """Mantel correlations, node-bootstrap intervals and paired gaps for the primary window."""
    inputs = load(panel, representations, params)
    spec = inputs.spec
    output.mkdir(parents=True, exist_ok=True)
    formation = spec.primary_formation
    window = spec.window(formation)
    rows = inputs.roster(window[0])
    sample = cohort_outcomes(inputs, formation, tuple(rows["issuer_id"].astype(str)))
    counts = sample.groupby("ticker").size()
    rows = rows.loc[rows["issuer_id"].map(counts).ge(spec.min_beta_quarters)].reset_index(drop=True)
    issuers = tuple(rows["issuer_id"].astype(str))
    returns = sample.pivot_table(index="date", columns="ticker", values="excess").reindex(
        index=window, columns=list(issuers)
    )
    target = pairwise_pearson(returns.to_numpy(float))
    store = inputs.store
    states = store.states(window[0], issuers) if store is not None else {}
    distances = _distances(
        inputs.histories(rows), states, inputs.formation_equity(formation, issuers)
    )
    rng = np.random.default_rng(spec.seed)
    indices = rng.integers(len(issuers), size=(spec.mantel_draws, len(issuers)))
    permutations = np.argsort(rng.random((PERMUTATIONS, len(issuers))), axis=1)
    estimates = []
    for name, distance in distances.items():
        observed, null = mantel_permutation_kernel(
            distance, target.distance, permutations, method="spearman"
        )
        interval = mantel_bootstrap_ci(distance, target.distance, indices, method="spearman")
        null_values = np.asarray(null)
        estimates.append(
            {
                "network": name,
                "mantel": float(observed),
                "low": interval.lower,
                "high": interval.upper,
                "permutation_p": float(
                    (1 + np.sum(np.abs(null_values) >= abs(float(observed))))
                    / (1 + len(null_values))
                ),
            }
        )
    frame = pd.DataFrame(estimates)
    frame["p_holm"] = holm(frame["permutation_p"])
    gaps = []
    for name, distance in distances.items():
        if name.endswith(":direct") or name in {"fernandez:joint", "size"}:
            continue
        rung = name.split(":", 1)[0]
        for reference in ("fernandez:joint", f"{rung}:direct"):
            if reference not in distances:
                continue
            result = paired_mantel_bootstrap(
                distances[reference], distance, target.distance, indices, method="spearman"
            )
            gaps.append(
                {
                    "network": name,
                    "reference": reference,
                    "gap": result.gap_mean,
                    "low": result.gap_ci_low,
                    "high": result.gap_ci_high,
                    "probability_not_positive": result.gap_prob_le_zero,
                    "draws": result.gap_n_boot,
                }
            )
    atomic_parquet(output / "mantel.parquet", frame)
    atomic_parquet(output / "gaps.parquet", pd.DataFrame(gaps))
    write_json(
        output / "manifest.json",
        {
            "study_sha256": spec.digest,
            "formation": formation,
            "issuers": len(issuers),
            "target": "chord distance of pairwise Pearson excess-return correlations",
            "undefined_target_pairs": target.neutral_pairs,
            "node_bootstrap_draws": spec.mantel_draws,
            "permutations": PERMUTATIONS,
        },
    )
