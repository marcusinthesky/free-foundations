"""Describe fixed-formation MM beta alignment with frozen PCoA coordinates."""
import hashlib
import json
import resource
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import rankdata, spearmanr

from free_foundations.study.experiments.inputs import load
from free_foundations.study.spec import file_hash


panel = Path('data/processed/crsp-sec/panel')
representations = Path('data/processed/crsp-sec/representations')
saved_path = Path('data/research/crsp-sec/experiments/replication/summary/roster.parquet')
handoff_path = Path('/tmp/finfm-swarm/mean-median/roster.parquet')
saved = pd.read_parquet(saved_path)
saved = saved.loc[(saved.formation == 2015) & (saved.status == 'available')].sort_values('issuer_id').reset_index(drop=True)
handoff = pd.read_parquet(handoff_path).sort_values('issuer_id').reset_index(drop=True)
pd.testing.assert_frame_equal(saved, handoff)
assert len(saved) == 878 and saved.issuer_id.is_unique and np.isfinite(saved.mm_beta).all()

inputs = load(panel, representations, Path('params.yaml'))
date = pd.Timestamp('2016-03-31')
roster = inputs.roster(date)
ids = tuple(roster.issuer_id.astype(str))
assert len(ids) == len(set(ids)) == 967
inputs.store.records[str(date.date())] = [r for r in inputs.store.records[str(date.date())] if r['rung'] == 'fernandez']
states = inputs.store.states(date, ids)['fernandez:tabpfn_full']
states = states / np.linalg.norm(states, axis=1, keepdims=True)
states -= states.mean(axis=0)
u, singular, _ = np.linalg.svd(states, full_matrices=False)
coordinates = u[:, :3] * singular[:3]
positions = {issuer: index for index, issuer in enumerate(ids)}
assert set(saved.issuer_id).issubset(positions)
axes = coordinates[[positions[issuer] for issuer in saved.issuer_id]]
y = rankdata(saved.mm_beta.to_numpy())
design = np.column_stack([np.ones(len(y)), axes])
predicted = design @ np.linalg.lstsq(design, y, rcond=None)[0]
r2 = 1 - np.sum((y - predicted) ** 2) / np.sum((y - y.mean()) ** 2)
rotation = np.array([[0, -1, 0], [1, 0, 0], [0, 0, -1]])
rotated = np.column_stack([np.ones(len(y)), axes @ rotation])
rotfit = rotated @ np.linalg.lstsq(rotated, y, rcond=None)[0]
assert np.allclose(predicted, rotfit)
record = next(r for r in inputs.store.records[str(date.date())] if 'tabpfn_full' in r.get('models', []))
print(json.dumps({'formation': 2015, 'quarter': str(date.date()), 'geometry_n': len(ids), 'beta_n': len(saved), 'beta_ordered_issuer_sha256': hashlib.sha256('\n'.join(saved.issuer_id).encode()).hexdigest(), 'saved_roster_sha256': file_hash(saved_path), 'handoff_roster_sha256': file_hash(handoff_path), 'panel_manifest_sha256': file_hash(panel / 'manifest.json'), 'representation_manifest_sha256': file_hash(representations / 'manifest.json'), 'state_sha256': record['sha256'], 'pc_spearman': [float(spearmanr(axes[:, i], y).statistic) for i in range(3)], 'top3_rank_response_r2': float(r2), 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, indent=2))
