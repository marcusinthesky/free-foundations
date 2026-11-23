---
description: The layered DVC pipeline, its data directories, storage and restoration.
---

# Data and pipeline

[DVC](https://dvc.org) runs the study in four layers, configured by
[`params.yaml`](../params.yaml). The [study contract](research/crsp-sec/README.md)
states every scientific choice.

| Layer | Directory | Stages |
| --- | --- | --- |
| Raw | `data/raw/{crsp-sec,models}` | Frozen source inventory and verified checkpoint manifest |
| Processed | `data/processed/crsp-sec/{panel,contexts,state-parts,representations}` | Shared contexts, eight rung/model cells, two direct controls and assembled states |
| Research | `data/research/crsp-sec/experiments/<experiment>/` | Formation-specific replications and each experiment’s summary |
| Publication | `data/publication/crsp-sec/free-foundations/` | Metrics, claims and generated manuscript exhibits |

`data/staging` holds explicit source acquisition and stays outside DVC inputs. The
representation state cache under `data/cache/crsp-sec/state-cache` and the model
weights under `data/raw/models/*/` are local, verified and reproducible.

```sh
just sources EXTRACT.csv EXTRACT.py  # stage SEC and factor recovery, freeze, record
just representations                 # encode both rungs (GPU; hours)
just replication                     # Fernández cross-sections and generated-beta draws
just comovement                      # quarterly spatial panels
just alignment                       # Mantel alignment
just publication                     # tables, figure and metrics from saved results
just matched-comparisons             # FinFM matched fits, interpretation and evidence
```

Run one encoding cell with `just dvc repro processed_encode@fernandez-tabpfn_full`
or a formation with `just dvc repro research_replicate@2015`. The full groups
use the rung, model and formation lists in `params.yaml`. Each worker owns a
separate directory. Collectors verify input identity and publish the common
representation store and replication summary used downstream.

Each command line is `free-foundations <layer> <command>` with explicit inputs
and outputs; `just build` checks fingerprints and reruns stale stages. Every stage
declares the `params.yaml` keys it reads. [semflow](https://github.com/marcusinthesky/semflow)
fingerprints the code each command reaches, so documentation edits do not rerun model
inference. After code changes run `just semflow-refresh`; after changing stage
commands review `just semflow-patch`, then run `just semflow-apply`.

## FinFM matched comparisons

The T08 stages consume the verified panel and keep their contexts, model cells,
fits and publication evidence in dedicated directories. The first targets to
run are `research_prepare_matched_sample` and
`processed_prepare_matched_contexts`. Then run `research_matched_factors`,
`research_matched_kernels` and `research_matched_encoders` as their model cells
become available. Verify PyTorch CUDA in the pinned devenv shell before launching
new model cells. The model stage records its device and checkpoint identity.

`just matched-comparisons` runs the full evidence chain, including the dated
geometry and its recorded ablation decision. The workshop renderer reads the
research evidence index and writes the review tables to
`data/publication/crsp-sec/finfm-matched/`.

The encoder stage also compares broad-input TabPFN with its corresponding
direct-feature graph under Market, FF5 and FF5 plus momentum controls. It
reuses the same matched issuer-quarters, saved representations, peer graphs
and stationary-quarter draws across the three controls. Each control refits
the return model; the intervals remain conditional on fitted loadings and
parameters. The original market-only ranking and geometry selection are unchanged.

After restoring the private study artifacts, regenerate this comparison and
its paper table from the repository root inside pinned devenv:

```sh
just semflow-refresh
just dvc repro publication_render_matched
just latex::paper finfm
```

The table is generated as `generated/tables/matched-broad-factors.tex` in
the manuscript project and included in the matched-factor appendix. Older
encoder results without the additional comparisons are rejected by the
exhibit renderer. Numerical findings require the recorded fits; neither
the source build nor the tests supply research estimates.

Acquisition archives the supplied WRDS extraction script. Raw source recovery
and checkpoint downloads use the network. Each estimator
uses verified local inputs. Set `EDGAR_IDENTITY` to a contact name and email for SEC requests.

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
