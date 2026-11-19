---
description: The layered DVC pipeline, its data directories, storage and restoration.
---

# Data and pipeline

[DVC](https://dvc.org) runs the study in three layers, configured by
[`params.yaml`](../params.yaml). The [study contract](research/crsp-sec/README.md)
states every scientific choice.

| Layer | Directory | Stages |
| --- | --- | --- |
| Raw | `data/raw/crsp-sec`, `data/raw/models` | `crsp_sec_sources` (frozen), `model_checkpoints` |
| Processed | `data/processed/crsp-sec/{panel,representations}` | `prepare`, `representations` |
| Research | `data/research/crsp-sec/{replication,comovement,alignment,publication}` | `replication`, `comovement`, `alignment`, `publication` |

`data/staging` holds explicit source acquisition and is never a DVC input. The
representation state cache under `data/processed/crsp-sec/state-cache` and the model
weights under `data/raw/models/*/` are local, verified and reproducible.

```sh
just sources EXTRACT.csv EXTRACT.py  # stage SEC and factor recovery, freeze, record
just representations                 # encode both rungs (GPU; hours)
just replication                     # Fernández cross-sections and generated-beta draws
just comovement                      # quarterly spatial panels
just alignment                       # Mantel alignment
just publication                     # tables, figure and metrics from saved results
```

Each command line is `free-foundations stages <layer> <command>` with explicit inputs
and outputs; `just build` checks fingerprints and reruns stale stages. Every stage
declares the `params.yaml` keys it reads. [semflow](https://github.com/marcusinthesky/semflow)
fingerprints the code each command reaches, so documentation edits do not rerun model
inference. After code changes run `just semflow-refresh`; after changing stage
commands review `just semflow-patch`, then run `just semflow-apply`.

Acquisition never runs the staged WRDS extraction script and is the only networked
operation. Set `EDGAR_IDENTITY` to a contact name and email for SEC requests.
Routine stages never access the network.

## Storage and restoration

Numerical results live in DVC's cache and the private Hugging Face bucket
`marcusinthesky/free-foundations`; Git stores source, parameters and pointers. Model
weights are not uploaded. Store bucket credentials outside Git:

```sh
just dvc remote modify --local hf-bucket access_key_id HFAK...
just dvc remote modify --local hf-bucket secret_access_key ...
just data-pull
```

Run DVC inside the devenv shell, which supplies the gateway checksum settings.
`just data-push` uploads newly recorded artifacts. A clean local DVC status does not
establish that the remote archive is complete.
