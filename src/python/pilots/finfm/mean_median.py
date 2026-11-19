"""Reconstruct the 2015 fixed-formation joint-graph outcome comparison."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.methods import spatial, spatial_ml
from free_foundations.methods.networks import characteristic_distances, exponential_weights
from free_foundations.study.experiments.inputs import load
from free_foundations.study.panel.cohorts import cohort_outcomes

ROOT = Path("data/research/crsp-sec/experiments/replication/summary")
OUT = Path("/tmp/finfm-swarm/mean-median")
OUT.mkdir(parents=True, exist_ok=True)
inputs = load(Path("data/processed/crsp-sec/panel"), None, Path("params.yaml"))
window = inputs.spec.window(2015)
rows = inputs.roster(window[0])
roster = pd.read_parquet(ROOT / "roster.parquet")
roster = roster.loc[(roster.formation == 2015) & (roster.status == "available")]
ids = tuple(roster.issuer_id.astype(str))
rows = rows.set_index("issuer_id").loc[list(ids)].reset_index()
assert tuple(rows.issuer_id.astype(str)) == ids
sample = cohort_outcomes(inputs.tables["cohorts"], inputs.factors, window, 2015, ids)
wide = sample.pivot(index="date", columns="ticker", values="excess").reindex(columns=list(ids))
median = wide.median().to_numpy(float)
assert len(ids) == 878 and np.allclose(median, roster.median_excess, rtol=1e-10, atol=1e-12)
beta = roster.mm_beta.to_numpy(float)
distance, neutral = characteristic_distances(inputs.histories(rows))["joint"]
weights = exponential_weights(distance)
graph = spatial_ml.Graph.of(weights)
saved = pd.read_parquet(ROOT / "estimates.parquet")
saved = saved.loc[(saved.formation == 2015) & (saved.network == "fernandez:joint|exp")]
fits = []
clipped = wide.clip(lower=wide.stack().quantile(0.01), upper=wide.stack().quantile(0.99))
outcomes = (
    ("median", median),
    ("mean", wide.mean().to_numpy(float)),
    ("median_clipped_1pct", clipped.median().to_numpy(float)),
    ("mean_clipped_1pct", clipped.mean().to_numpy(float)),
)
for name, outcome in outcomes:
    for intercept in (False, True):
        for estimator in ("lag_ml", "error_ml"):
            fit = spatial.cross_section(
                outcome, {"beta": beta}, weights, estimator, intercept=intercept
            )
            fit["outcome"] = name
            fits.append(fit)
            if name == "median":
                original = saved.loc[
                    (saved.estimator == estimator) & (saved.with_intercept == intercept)
                ]
                assert len(original) == 1
                fit["saved_status"] = original.iloc[0].status
                assert fit["status"] == fit["saved_status"]
                if fit["status"] == "available" and original.iloc[0].status == "available":
                    for key in ("beta", "spatial"):
                        assert abs(fit[key] - original.iloc[0][key]) <= 1e-4 * max(
                            1, abs(original.iloc[0][key])
                        )
pd.DataFrame(fits).to_json(OUT / "fits.json", orient="records", indent=2)
wide.to_parquet(OUT / "returns.parquet")
roster.to_parquet(OUT / "roster.parquet")
np.save(OUT / "weights.npy", weights)
(OUT / "metadata.json").write_text(
    json.dumps(
        {
            "neutral_component_max": neutral,
            "quarters": len(wide),
            "issuers": len(ids),
            "observed_issuer_quarters": int(wide.count().sum()),
            "clipping_low": float(wide.stack().quantile(0.01)),
            "clipping_high": float(wide.stack().quantile(0.99)),
        },
        indent=2,
    )
)
