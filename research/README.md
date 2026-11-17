---
description: The DVC research pipeline, artifact storage and restoration.
---

# Research pipeline

The [study contract](crsp-study/README.md) and
[versioned specification](crsp-study/study.json) govern every active empirical
stage. Earlier current-survivor results remain only in the Git history.

## Data and pipeline

[DVC](https://dvc.org) records the stages in `dvc.yaml`:

| Stages | Responsibility |
| --- | --- |
| `semflow_refresh` | Semantic code fingerprints the study stages depend on |
| `sources` | Frozen CRSP bytes, public SEC evidence and factor archives |
| `model_checkpoints` | Four pinned pretrained checkpoints and verified hashes |
| `prepare` | One quarterly master panel, source-coverage ledger and as-of features |
| `representations` | Saved full-column states for every information rung |
| `measurement` | Exposure readouts, quarterly risk comparisons, geometry and paired inference |
| `replication` | Quarterly MM CAPM, spatial estimates and generated-beta uncertainty |
| `publication` | Saved-result tables, source availability and claims audit |

Acquisition is an explicit, resumable operation. It never runs the staged WRDS
extraction script. Public SEC evidence is the only identifier/accounting fallback;
no quote-service substitution is used. Set `EDGAR_IDENTITY` to a contact name and
email, or use the public author contact in the manuscript.

```sh
just python-universe          # deliberately recover sources and record the frozen stage
just python-panel             # reproduce quarterly measurement
just python-fernandez         # reproduce the matched supporting replication
just python-publication       # render saved results and coverage
just latex::paper             # render saved results and compile the paper
```

Routine numerical stages never access the network. Missing or unverifiable
source evidence remains visible in the availability ledger. Unresolved historical
PERMNO–CIK links are distinguished from absent XBRL; neither current ticker
matches nor old empirical results certify the new study. The staged CRSP extract
also lacks terminal-return flags, so this migration does not certify complete
delisting coverage merely because it uses CRSP.

`just latex::paper` does not estimate models. `just build` checks fingerprints and
runs stale DVC stages, including representation extraction if its inputs change.
[semflow](https://github.com/marcusinthesky/semflow) fingerprints the code each
stage command reaches; the `semflow_refresh` stage regenerates those fingerprints
before dependent stages run, and `just semflow-check` gates commits. After code
changes run `just semflow-refresh`; after changing stage commands review
`just semflow-patch`, then run `just semflow-apply`.

Checkpoint expectations are versioned in
`src/python/apps/free_foundations/src/free_foundations/checkpoints.json`. Loading
verifies pinned revision and bytes. Model extraction is separate from financial
estimation; readouts and reports consume saved states without loading local weights.

## Artifact storage and restoration

Numerical results, states, contexts and detailed manifests live in DVC's cache
and the private Hugging Face bucket `marcusinthesky/free-foundations`. Git stores
source, protocols, checkpoint expectations and pipeline pointers. Model weights
remain local reproducible downloads and are not uploaded to the data remote.

To access the bucket, create S3 credentials in the Hugging Face account settings
and store them outside Git:

```sh
just dvc remote modify --local hf-bucket access_key_id HFAK...
just dvc remote modify --local hf-bucket secret_access_key ...
just data-pull
```

Run DVC inside the devenv shell, which supplies the gateway checksum settings.
`just data-push` uploads newly recorded artifacts. Restoring sources, regenerating
numbers and compiling the manuscript are distinct checks; a clean local DVC
status does not establish that the remote archive is complete.

The financial source stage is frozen under routine reproduction.
`just python-universe` explicitly resumes SEC recovery and records the source
vintage. Replacing CRSP bytes requires a separate vintage; changing source evidence
invalidates dependent results. Reviewers can request the private publication
archive. See [the publication guide](../src/latex/README.md) for rendering details.
