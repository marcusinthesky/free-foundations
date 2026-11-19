"""Replay two saved-state quarterly graphs and compare likelihood conventions."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize_scalar

from free_foundations.methods import spatial_ml
from free_foundations.methods.networks import knn_weights, representation_distance
from free_foundations.study.experiments.inputs import load
from panel_contrast import contrast_loglik

root = Path('/tmp/finfm-swarm/panel')
root.mkdir(parents=True, exist_ok=True)
base = Path('data/research/crsp-sec/experiments/comovement/summary')
inputs = load(Path('data/processed/crsp-sec/panel'), Path('data/processed/crsp-sec/representations'), Path('params.yaml'))
betas = pd.read_parquet(base / 'betas.parquet').set_index('ticker')['mm_beta']
ledger = pd.read_parquet(base / 'ledger.parquet').set_index('quarter')
names = ['fernandez:direct', 'fernandez:tabpfn_full']
periods = {name: [] for name in names}
records = []
for quarter in inputs.spec.panel_calendar:
    formation = pd.Timestamp(year=quarter.year, month=3, day=31)
    formed = set(inputs.roster(formation)['issuer_id'].astype(str))
    roster = inputs.roster(quarter)
    beta = roster['issuer_id'].map(betas)
    keep = roster['observed'].astype(bool) & beta.notna() & roster['issuer_id'].isin(formed)
    rows = roster.loc[keep].reset_index(drop=True)
    assert len(rows) == ledger.loc[quarter, 'issuers']
    issuers = tuple(rows['issuer_id'].astype(str))
    assert len(set(issuers)) == len(issuers)
    states = inputs.store.states(formation, issuers)
    rate, market = inputs.factors.loc[quarter, ['RF', 'Mkt-RF']]
    y = rows['total_return'].to_numpy(float) - rate
    x = beta.loc[keep].to_numpy(float) * market
    mask = hashlib.sha256(json.dumps(issuers).encode()).hexdigest()
    for name in names:
        w = knn_weights(representation_distance(states[name]), 10)
        assert np.allclose(w.sum(axis=1), 1) and np.all(np.diag(w) == 0)
        assert np.array_equal(w > 0, w.T > 0)
        graph_hash = hashlib.sha256(w.tobytes()).hexdigest()
        periods[name].append(spatial_ml.Period.of(y, x, w))
        records.append({'quarter': str(quarter.date()), 'network': name, 'n': len(rows), 'mask_sha256': mask, 'graph_sha256': graph_hash, 'isolates': int((w.sum(axis=1) == 0).sum()), 'row_error': float(abs(w.sum(axis=1)-1).max())})
    print(quarter.date(), len(rows), flush=True)
pd.DataFrame(records).to_csv(root / 'graphs.csv', index=False)
fits = []
contrib = []
for name, items in periods.items():
    for process in ('error', 'lag'):
        full = spatial_ml.panel_profile(items, process)
        saved = pd.read_parquet(base / 'estimates.parquet')
        saved = saved[(saved.network == name + '|knn10') & (saved.process == process)].iloc[0]
        assert abs(full.spatial - saved.spatial) < 1e-5
        assert abs(full.loglik - saved.log_likelihood) < 1e-3
        low = max(p.graph.interval[0] for p in items)
        high = min(p.graph.interval[1] for p in items)
        def contrast(rho):
            return contrast_loglik(items, rho, process)
        grid = np.linspace(low, high, 101)
        best = int(np.argmax([contrast(v) for v in grid]))
        result = minimize_scalar(lambda v: -contrast(v), bounds=(grid[max(0,best-1)], grid[min(100,best+1)]), method='bounded')
        fits.append({'network': name, 'process': process, 'full_spatial': full.spatial, 'contrast_spatial': result.x, 'full_loglik': full.loglik, 'contrast_loglik': -result.fun, 'slope': full.slope, 'variance': full.variance, 'low': low, 'high': high})
        for q, value in zip(inputs.spec.panel_calendar, full.contributions, strict=True):
            contrib.append({'network': name, 'process': process, 'quarter': str(q.date()), 'log_likelihood': value})
pd.DataFrame(fits).to_csv(root / 'fits.csv', index=False)
pd.DataFrame(contrib).to_csv(root / 'contributions.csv', index=False)
print('DONE', flush=True)
