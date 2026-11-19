"""Compare frozen TabPFN chord-distance subspaces on the common roster."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

from free_foundations.study.experiments.inputs import load
from free_foundations.study.spec import file_hash


def basis(x):
    x = x / np.linalg.norm(x, axis=1, keepdims=True)
    x = x - x.mean(axis=0)
    u, s, _ = np.linalg.svd(x, full_matrices=False)
    return u[:, :3], s[:4]


def angles(a, b):
    return np.degrees(np.arccos(np.clip(np.linalg.svd(a.T @ b, compute_uv=False), 0, 1)))


# Sign and rotation leave the principal angles unchanged.
fixture = np.eye(6)[:, :3]
rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, -1]])
assert np.max(angles(fixture, fixture @ rotation)) < 1e-5

panel = Path('data/processed/crsp-sec/panel')
representations = Path('data/processed/crsp-sec/representations')
inputs = load(panel, representations, Path('params.yaml'))
dates = [pd.Timestamp('2016-03-31'), pd.Timestamp('2017-03-31')]
rows = [inputs.roster(date) for date in dates]
ids = sorted(set(rows[0].issuer_id.astype(str)) & set(rows[1].issuer_id.astype(str)))
assert len(ids) > 3
bases = []
records = []
for date, roster in zip(dates, rows, strict=True):
    original = tuple(roster.issuer_id.astype(str))
    inputs.store.records[str(date.date())] = [r for r in inputs.store.records[str(date.date())] if r['rung'] == 'fernandez']
    state = inputs.store.states(date, original)['fernandez:tabpfn_full']
    indices = {issuer: i for i, issuer in enumerate(original)}
    subset = state[[indices[issuer] for issuer in ids]]
    assert np.isfinite(subset).all() and np.all(np.linalg.norm(subset, axis=1) > 0)
    u, singular = basis(subset)
    bases.append(u)
    record = next(r for r in inputs.store.records[str(date.date())] if 'tabpfn_full' in r.get('models', []))
    records.append({'date': str(date.date()), 'roster_n': len(original), 'state_sha256': record['sha256'], 'singular_values_first4': singular.tolist()})

print(json.dumps({'common_n': len(ids), 'common_issuer_sha256': hashlib.sha256('\n'.join(ids).encode()).hexdigest(), 'panel_manifest_sha256': file_hash(panel / 'manifest.json'), 'representation_manifest_sha256': file_hash(representations / 'manifest.json'), 'dates': records, 'principal_angles_degrees': angles(*bases).tolist()}, indent=2))
