"""Paired mean-minus-median refits on the fixed 2015 formation."""

import argparse
import hashlib
import json
import math
import resource
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pandas as pd

from free_foundations.methods import spatial_ml
from free_foundations.methods.fernandez.evaluation import robust_betas
from free_foundations.methods.inference import generated_beta_indices
from free_foundations.study.experiments.inputs import load
from free_foundations.study.experiments.replication import _betas, _refit, _restrict
from free_foundations.study.panel.cohorts import cohort_outcomes


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--draws", type=int, default=99)
    parser.add_argument("--block", type=float, default=2.218)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source", type=Path, default=Path("/tmp/finfm-swarm/mean-median"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    source = args.source
    paths = [
        source / name for name in ("returns.parquet", "roster.parquet", "weights.npy", "fits.json")
    ]
    wide = pd.read_parquet(paths[0])
    roster = pd.read_parquet(paths[1])
    ids = tuple(roster.issuer_id.astype(str))
    assert tuple(wide.columns.astype(str)) == ids and len(ids) == 878
    weights = np.load(paths[2])
    assert weights.shape == (len(ids), len(ids))
    inputs = load(Path("data/processed/crsp-sec/panel"), None, Path("params.yaml"))
    window = inputs.spec.window(2015)
    assert np.array_equal(pd.to_datetime(wide.index), window)
    sample = cohort_outcomes(inputs.tables["cohorts"], inputs.factors, window, 2015, ids)
    rebuilt = sample.pivot(index="date", columns="ticker", values="excess").reindex(
        index=window, columns=ids
    )
    assert np.allclose(rebuilt, wide, equal_nan=True)
    del inputs, rebuilt
    indices = generated_beta_indices(window, args.draws, args.block, 42)
    with TemporaryDirectory(dir=args.output, prefix=".mm-") as directory:
        try:
            mm = robust_betas(
                sample, Path(directory), terms=("market",), indices=indices, cores=1, tag="paired"
            )
        except RuntimeError as error:
            if "did not converge" not in str(error):
                raise
            mm = pd.read_csv(Path(directory) / "cache/mm-paired-output.csv")
    mm.to_parquet(args.output / "mm.parquet", index=False)
    graph = spatial_ml.Graph.of(weights)
    original_beta = _betas(mm, 0).reindex(ids).to_numpy(float)
    assert np.allclose(original_beta, roster.mm_beta, rtol=1e-4, atol=1e-6)
    fits = json.loads(paths[3].read_text())
    original = {}
    for label, outcome in (("mean", wide.mean().to_numpy()), ("median", wide.median().to_numpy())):
        original[label] = _refit(outcome, original_beta, graph, intercept=False)
        for fit in fits:
            if (
                fit["outcome"] == label
                and not fit["with_intercept"]
                and fit["status"] == "available"
            ):
                for field, key in (("beta", "premium"), ("spatial", "spatial")):
                    expected = fit[field]
                    observed = original[label][f"{fit['estimator']}:{key}"]
                    assert abs(expected - observed) <= 1e-4 * max(1, abs(expected))
    rows = []
    for draw in range(1, args.draws + 1):
        schedule = indices.loc[indices.replicate.eq(draw)].sort_values("position")
        assert np.array_equal(schedule.position.to_numpy(), np.arange(len(window)))
        values = wide.reindex(pd.to_datetime(schedule.quarter))
        beta = _betas(mm, draw).reindex(ids).to_numpy(float)
        mean = values.mean().to_numpy(float)
        median = values.median().to_numpy(float)
        keep = np.isfinite(beta) & np.isfinite(mean) & np.isfinite(median)
        record = {"draw": draw, "dropped": int((~keep).sum()), "status": "insufficient"}
        if keep.sum() >= 10:
            restricted = graph if keep.all() else spatial_ml.Graph.of(_restrict(weights, keep))
            try:
                arms = {
                    name: _refit(y[keep], beta[keep], restricted, intercept=False)
                    for name, y in (("mean", mean), ("median", median))
                }
                for estimator in ("lag_ml", "error_ml", "lag_iv"):
                    endpoints = [f"{estimator}:premium", f"{estimator}:spatial"]
                    valid = all(np.isfinite(arms[arm][key]) for arm in arms for key in endpoints)
                    if estimator.endswith("_ml"):
                        low, high = restricted.interval
                        valid = valid and all(
                            low + 1e-4 < arms[arm][endpoints[1]] < high - 1e-4 for arm in arms
                        )
                    for endpoint in endpoints:
                        record[endpoint + ":valid"] = bool(valid)
                        record[endpoint + ":difference"] = (
                            arms["mean"][endpoint] - arms["median"][endpoint] if valid else np.nan
                        )
                record["status"] = "available"
            except (ValueError, np.linalg.LinAlgError, FloatingPointError) as error:
                record["status"] = type(error).__name__
        rows.append(record)
    result = pd.DataFrame(rows)
    result.to_parquet(args.output / "draws.parquet", index=False)
    summary = []
    for column in result.filter(like=":difference"):
        for population, selected in (
            ("all_shared_masks", result),
            ("fixed_roster", result.loc[result.dropped.eq(0)]),
        ):
            values = selected[column].dropna()
            threshold = math.ceil(0.8 * args.draws)
            summary.append(
                {
                    "endpoint": column,
                    "population": population,
                    "attempted": len(result),
                    "eligible_population": len(selected),
                    "joint_success": len(values),
                    "joint_failures": len(result) - len(values),
                    "minimum_success": threshold,
                    "low": values.quantile(0.025) if len(values) >= threshold else None,
                    "high": values.quantile(0.975) if len(values) >= threshold else None,
                }
            )
    pd.DataFrame(summary).to_csv(args.output / "intervals.csv", index=False)
    (args.output / "metadata.json").write_text(
        json.dumps(
            {
                "revision": "b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda",
                "seed": 42,
                "block": args.block,
                "draws": args.draws,
                "input_sha256": {str(path): digest(path) for path in paths},
                "original": original,
                "intercept": "unavailable, median point fit invalid",
                "graph": "fixed formation graph, restricted and renormalized on shared draw mask",
                "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                "child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
