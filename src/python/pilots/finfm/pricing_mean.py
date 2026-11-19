"""Price the verified 2015 cohort using observed quarterly mean returns."""

import hashlib
import json
import resource
from pathlib import Path

import numpy as np
import pandas as pd

source = Path('/tmp/finfm-swarm/mean-median')
output = Path('/tmp/finfm-swarm/pricing')
output.mkdir(parents=True, exist_ok=True)
expected = {
    'returns.parquet': 'b0b414f35dee4e723350936b14348aa03be2685ed080530ac6ecdfd68d4dc76b',
    'roster.parquet': '655caeef7d9c353feec5913f77c8ea9bd92f0382a10788fc917864859ab2c4a0',
}
for name, digest in expected.items():
    assert hashlib.sha256((source / name).read_bytes()).hexdigest() == digest

returns = pd.read_parquet(source / 'returns.parquet')
roster = pd.read_parquet(source / 'roster.parquet')
assert len(roster) == 878 and roster.issuer_id.is_unique
assert list(returns.columns) == roster.issuer_id.astype(str).tolist()
assert returns.shape == (40, 878)
assert np.array_equal(returns.count().to_numpy(), roster.observed_quarters.to_numpy())
assert np.allclose(returns.median().to_numpy(), roster.median_excess.to_numpy(), rtol=1e-10, atol=1e-12)
beta = roster.mm_beta.to_numpy(dtype=float)
mean = returns.mean().to_numpy(dtype=float)
assert np.isfinite(beta).all() and np.isfinite(mean).all()
price = float(beta @ mean / (beta @ beta))
errors = mean - beta * price
result = {
    'formation': 2015,
    'issuers': len(beta),
    'quarters': len(returns),
    'observed_issuer_quarters': int(returns.count().sum()),
    'slope': price,
    'pricing_error_rms': float(np.sqrt(np.mean(errors**2))),
    'loading_rank': int(np.linalg.matrix_rank(beta[:, None])),
    'input_sha256': expected,
}
contributions = pd.DataFrame({'issuer_id': roster.issuer_id, 'observed_quarters': returns.count().to_numpy(), 'mm_beta': beta, 'mean_excess': mean, 'pricing_error': errors})
contributions.to_csv(output / 'issuer_contributions.csv', index=False, float_format='%.17g')
result['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
(output / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
