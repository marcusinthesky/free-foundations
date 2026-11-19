"""Offline January 2016 PCoA receipt; run from repository root as documented."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from free_foundations.methods.networks import representation_distance
from free_foundations.study.experiments.inputs import load
from free_foundations.study.spec import file_hash

panel = Path('data/processed/crsp-sec/panel')
representations = Path('data/processed/crsp-sec/representations')
inputs = load(panel, representations, Path('params.yaml'))
quarter = pd.Timestamp('2016-03-31')
rows = inputs.roster(quarter)
ids = tuple(rows.issuer_id.astype(str))
assert len(ids) == len(set(ids)) == 967
saved = pd.read_parquet('data/research/crsp-sec/experiments/replication/summary/roster.parquet')
est = set(saved.loc[(saved.formation == 2015) & (saved.status == 'available'), 'issuer_id'])
assert len(est) == 878 and est.issubset(ids)
# Store checks the manifest, extraction provenance, file hashes, inventory, shape and row order.
inputs.store.records[str(quarter.date())] = [r for r in inputs.store.records[str(quarter.date())] if r['rung'] == 'fernandez']
states = inputs.store.states(quarter, ids)
x = states['fernandez:tabpfn_full']
d = representation_distance(x)
n = len(d)
d2 = d * d
b = -0.5 * (d2 - d2.mean(axis=0)[None, :] - d2.mean(axis=1)[:, None] + d2.mean())
w, v = np.linalg.eigh(b)
order = np.argsort(w)[::-1]
w, v = w[order], v[:, order]
tol = np.finfo(float).eps * n * max(abs(w))
pos = w > tol
neg = w < -tol
coords = v[:, pos] * np.sqrt(w[pos])
# Avoid allocating n*n*rank.
gram = coords @ coords.T
rd2 = np.maximum(np.diag(gram)[:, None] + np.diag(gram)[None, :] - 2 * gram, 0)
tri = np.triu_indices(n, 1)
error = np.sqrt(rd2[tri]) - d[tri]
k = 3
z = coords[:, :k]
theta = 0.73
rotation = np.array([[np.cos(theta), -np.sin(theta), 0], [np.sin(theta), np.cos(theta), 0], [0, 0, -1]])
rot = z @ rotation
zg, rg = z @ z.T, rot @ rot.T
histories = inputs.histories(rows)
align = {}
for name, history in histories.items():
    # Latest available as-of annual slot; no interpolation or imputation.
    valid = np.isfinite(history)
    has = valid.any(axis=1)
    latest = np.full(n, np.nan)
    latest[has] = history[has, :][np.arange(has.sum()), history.shape[1] - 1 - np.argmax(valid[has, ::-1], axis=1)]
    mask = np.isfinite(latest)
    y = rankdata(latest[mask])
    axes = z[mask]
    rho = [float(spearmanr(axes[:, i], y).statistic) for i in range(k)]
    # Rank-transformed y and coordinates: R² invariant to rotations of this subspace.
    # Use raw coordinates for the subspace regression to preserve rotation invariance.
    design = np.column_stack((np.ones(mask.sum()), axes))
    fit = design @ np.linalg.lstsq(design, y, rcond=None)[0]
    r2 = 1 - np.sum((y-fit)**2) / np.sum((y-y.mean())**2)
    design_rot = np.column_stack((np.ones(mask.sum()), rot[mask]))
    fit_rot = design_rot @ np.linalg.lstsq(design_rot, y, rcond=None)[0]
    r2_rot = 1 - np.sum((y-fit_rot)**2) / np.sum((y-y.mean())**2)
    align[name] = {'n': int(mask.sum()), 'spearman_axes_1_3': rho, 'top3_rank_response_r2': float(r2), 'rotated_r2_difference': float(r2_rot-r2)}
record = next(r for r in inputs.store.records[str(quarter.date())] if 'tabpfn_full' in r.get('models', []))
result = {'quarter': str(quarter.date()), 'analytical_n': n, 'estimated_n': len(est), 'ordered_issuer_sha256': hashlib.sha256('\n'.join(ids).encode()).hexdigest(), 'panel_manifest_sha256': file_hash(panel/'manifest.json'), 'representation_manifest_sha256': file_hash(representations/'manifest.json'), 'state_path': record['path'], 'state_sha256': record['sha256'], 'shape': list(x.shape), 'eigenvalues_first_5': w[:5].tolist(), 'positive_count': int(pos.sum()), 'negative_count_over_tolerance': int(neg.sum()), 'tolerance': float(tol), 'smallest_eigenvalue': float(w[-1]), 'raw_negative_absolute_inertia': float(-w[w < 0].sum()), 'negative_absolute_inertia': float(-w[neg].sum()), 'negative_fraction_absolute_inertia': float(-w[neg].sum()/np.abs(w).sum()), 'positive_inertia_top3_fraction': float(w[:3].sum()/w[pos].sum()), 'max_abs_centered_gram_row_sum': float(np.abs(b.sum(axis=1)).max()), 'distance_reconstruction_rmse': float(np.sqrt(np.mean(error**2))), 'distance_reconstruction_max_abs': float(np.max(np.abs(error))), 'rotation_gram_max_abs_difference': float(np.abs(zg-rg).max()), 'alignment': align}
print(json.dumps(result, indent=2, sort_keys=True))
