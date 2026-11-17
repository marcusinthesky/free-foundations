# Current-survivor study archive

These byte-for-byte snapshots preserve the DVC graph and locked artifact hashes
immediately before the quarterly CRSP–SEC migration:

- `pipeline.yaml.snapshot`: the previous nine-stage DVC configuration.
- `pipeline.lock.snapshot`: its recorded source and numerical artifact hashes.

The snapshots are historical provenance, not active DVC configurations. Their
names deliberately do not match DVC pipeline or lock filenames. Existing source
and result directories were not moved or deleted by this archival step; the lock
snapshot retains their cache identities.

The active root pipeline now uses `research/crsp-study/study.json` and the single
quarterly master panel. It does not reproduce the archived Yahoo/current-survivor
study or publish its saved estimates as CRSP results. Use a separate historical
checkout when reproducing this archived pipeline.
