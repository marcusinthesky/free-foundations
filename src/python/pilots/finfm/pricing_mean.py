"""Price the verified 2015 cohort using observed quarterly mean returns."""

import argparse
import hashlib
import json
import resource
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.study.experiments.inputs import load

parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
parser.add_argument("--output", required=True, type=Path)
args = parser.parse_args()
source, output = args.source, args.output
output.mkdir(parents=True, exist_ok=True)
expected = {
    "returns.parquet": "b0b414f35dee4e723350936b14348aa03be2685ed080530ac6ecdfd68d4dc76b",
    "roster.parquet": "655caeef7d9c353feec5913f77c8ea9bd92f0382a10788fc917864859ab2c4a0",
}
for name, digest in expected.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest

returns = pd.read_parquet(source / "returns.parquet")
roster = pd.read_parquet(source / "roster.parquet")
assert len(roster) == 878 and roster.issuer_id.is_unique
assert list(returns.columns) == roster.issuer_id.astype(str).tolist()
assert returns.shape == (40, 878)
assert np.array_equal(returns.count().to_numpy(), roster.observed_quarters.to_numpy())
assert np.allclose(
    returns.median().to_numpy(), roster.median_excess.to_numpy(), rtol=1e-10, atol=1e-12
)
beta = roster.mm_beta.to_numpy(dtype=float)
mean = returns.mean().to_numpy(dtype=float)
assert np.isfinite(beta).all() and np.isfinite(mean).all()
price = float(beta @ mean / (beta @ beta))
errors = mean - beta * price
inputs = load(Path("data/processed/crsp-sec/panel"), None, Path("params.yaml"))
window = inputs.spec.window(2015)
assert pd.DatetimeIndex(returns.index).equals(window)
factor = inputs.factors["Mkt-RF"].reindex(window)
assert np.isfinite(factor.to_numpy()).all()
factor_mean = float(factor.mean())
traded_errors = mean - beta * factor_mean
result = {
    "formation": 2015,
    "issuers": len(beta),
    "quarters": len(returns),
    "observed_issuer_quarters": int(returns.count().sum()),
    "slope": price,
    "factor_mean": factor_mean,
    "slope_minus_factor_mean": price - factor_mean,
    "traded_factor_error_rms": float(np.sqrt(np.mean(traded_errors**2))),
    "pricing_error_rms": float(np.sqrt(np.mean(errors**2))),
    "loading_rank": int(np.linalg.matrix_rank(beta[:, None])),
    "input_sha256": expected,
}
contributions = pd.DataFrame(
    {
        "issuer_id": roster.issuer_id,
        "observed_quarters": returns.count().to_numpy(),
        "mm_beta": beta,
        "mean_excess": mean,
        "pricing_error": errors,
        "traded_factor_pricing_error": traded_errors,
    }
)
contributions.to_csv(output / "issuer_contributions.csv", index=False, float_format="%.17g")
result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
