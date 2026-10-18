# free-foundations

A workspace for Python, Lean, TypeScript, and LaTeX.

| Directory | Purpose |
| --- | --- |
| `src/python` | Python packages and experiments |
| `src/lean` | Lean definitions and proofs |
| `src/typescript` | TypeScript libraries and applications |
| `src/latex` | Papers and mathematical writing |

## Development

Install the pinned devenv CLI with `bash nix/install-devenv.sh`, then run
`direnv allow` or `devenv shell`. Shell entry installs the locked repository
tooling and Git hooks. Run `just` to see available commands and `just check`
to run quality gates, including untracked source files.

Shared tools are supplied by `devenv.nix`; Nix inputs are pinned in
`devenv.lock`. Insitu is installed from our Git repository at the revision in
`pyproject.toml`, with its dependencies locked in `uv.lock`. Run `just insitu-sync`
to update projections and `just insitu-check` to detect stale output. Add models
and templates under `insitu/` as documentation projections become necessary.

Prek runs hygiene, Nix, Tombi, Markdown, spelling, external-link, Insitu,
Python, TypeScript, Lean, and LaTeX checks. Conventional commits are checked
at commit time. Lychee needs network access; the first Lean build downloads
the pinned toolchain through Elan. The first LaTeX build downloads Tectonic's
TeX bundle. Language checks run when their source files change.

Python dependencies and the typed model registry live in `src/python`; see
[the Python guide](src/python/README.md). Install the locked data and development
environment with `uv sync --project src/python --frozen`. TypeScript starts as a private,
dependency-free Bun workspace; add packages under its `apps/` or `packages/`
directories when needed. Run `just lean-build` and `just latex-build` to build
the starter proof library and document.

## Data and pipeline

Every research run is a [DVC](https://dvc.org) stage in `dvc.yaml`, one per
`free-foundations` command. [semflow](https://github.com/marcusinthesky/semflow)
replaces each stage's Python dependency with a fingerprint of the code its command
reaches (`.semflow/hashes/`), so comment, docstring and annotation edits rerun
nothing. `dvc.lock` records the inputs, code and outputs of every result. Generated numerical CSV/JSON outputs, matrices, embeddings and daily scores
live in DVC's cache and in the private Hugging Face bucket
`marcusinthesky/free-foundations`. Git retains protocols, expected checkpoint
identities, pipeline metadata and human-readable reports. Model weights are
never pushed: verified snapshots can be restored at pinned revisions.

To read or write the bucket, generate S3 credentials from a Hugging Face access
token (Settings, Access Tokens, "Generate S3 credentials"; use a write token to
push), then store them outside Git:

```sh
dvc remote modify --local hf-bucket access_key_id HFAK...
dvc remote modify --local hf-bucket secret_access_key ...
just data-pull                 # or: dvc pull research/panel/four
```

`just python-panel four` and the other `python-*` recipes run `dvc repro`, which
skips any stage whose code and inputs are unchanged. `just build` reruns every
stale stage. After changing code, run `just semflow-refresh`. If a stage's
command changed, run `uv run --project src/python semflow patch` first: it prints
the change to `dvc.yaml`, and `--apply` writes it. Prek's `semflow check` blocks
commits with stale fingerprints. `just data-push` uploads new results;
`just data-snapshot` re-records the shared model-state cache after a run. Run
DVC inside the devenv shell, which sets the checksum options the bucket's S3
gateway needs.

The [expanded experiment](research/expanded/README.md) compares accounting input
views and four pretrained models, retaining ticker-labeled annual distance matrices.

The [Fernández replication ladder](research/fernandez/README.md) separates the
published two-stage spatial CAPM from matched-input foundation models and
full-return covariance forecasts.

The [larger-universe coverage audit](research/universe/README.md) documents
1,000 distinct SEC issuers, extended Yahoo and French histories, and annual
filing availability. Run `just python-universe` with `EDGAR_IDENTITY` set to
resume its cached acquisition; the recipe reruns the frozen DVC stage and records it. Its changing annual cohorts are distinct from
the six-firm complete-history demonstration.

The [paper](src/latex/main.tex), *Do Pretrained Tabular Models Measure Financial
Proximity?*, distinguishes pretrained information from native distance geometry
through a practical replication and a controlled retrospective experiment.
Run `just latex-build` for the combined paper and supplement, with tables,
native PGF figures, and numerical bindings generated from recorded results.
The supplement develops the economic motivation, assumptions, and proofs for
the measurement argument; the complete Lean blueprint remains available separately.
`just latex-count` reports word counts; the
[publication workflow](src/latex/README.md) describes the source audit and tools.

The [chronological panel comparison](research/panel/RESULTS.md) constructs full
point-in-time characteristics, calibrates one spatial coefficient per approach
on 2016-2019, and scores 2020-2025 on matched annual cohorts. Run
`just python-panel` to reproduce its cached input ladder and annual distance matrices.

## Frozen financial inputs

Ordinary `dvc repro` reuses the recorded SEC and Yahoo Finance snapshots.
The `universe`, `pilot`, and `market_metadata` stages are frozen. The last stage
owns the supplemental Yahoo histories, post-sample corporate actions, and the
recorded SEC industry classification, so recomputing representations cannot
delete or refresh them. Numerical stages reject missing snapshots rather than
silently downloading current data.

Restore large cached inputs with `dvc checkout universe pilot market_metadata`
(or `dvc pull` for the same targets when the local cache is unavailable).
The small industry CSV remains versioned in Git. Data acquisition is an
explicit maintenance operation through the acquisition recipes, separate from
reproducing estimates. Replacing a vintage requires deliberately recording the
new snapshot and regenerating its dependent results.

The representative foundation-model extension is available through
`just python-panel three-foundations`; its protocol and ten-model landscape
are recorded in `research/panel/three-foundations/`. Publication assets use
pandas, Jinja2 and Matplotlib PGF; `just latex-build` reads the saved results.

## Pipeline ownership and artifact storage

Each numerical stage owns its generated tables, contexts, configuration records,
and detailed provenance. These outputs use the DVC cache regardless of file size,
so a completed run can be restored without estimation. Git stores the source,
protocols, pipeline definitions and pointers, plus inexpensive reporting-stage
summaries. Moving an existing output into the cache preserves its recorded
numerical contents and does not certify it against newer source code.

The `model_checkpoints` stage resolves pinned model revisions and records their
verified hashes in `research/model-checkpoints.json`. Model weights remain a
local, reproducible download cache and are not uploaded to the data remote.
Reports consume the recorded catalogue and financial artifacts, so reporting
requires no local model weights. Missing local weights can be restored through
`free-foundations expanded checkpoints` with the TabPFN extra installed.

Shared embedding caches remain explicit DVC snapshots because several numerical
stages reuse them. Temporary robust-regression exchange files are implementation
scratch space; the ladder retains its runtime records and bootstrap artifacts.
Use `dvc pull` to restore cached results before building the manuscript.

## Measurement-construction revision

The supplementary `panel validate` command crosses native and calibrated
coordinates with Euclidean and chord distance, checks the intercept-only
identity of Kumo's reset controls, and repeats calibration under five fixed
fold assignments. Its protocol and separately owned DVC outputs reside under
`research/panel/three-foundations-validation`. The original specification stays
identifiable; the additional assignments are development diagnostics rather
than independent test samples.

Run `dvc repro panel_validate_measurement panel_report_three_foundations` to
reproduce the principal experiment, diagnostics and report together, then
`just latex-build` to render the revised publication from those artifacts.

Checkpoint identity comes from `src/python/src/free_foundations/checkpoints.json`,
whose expected hashes were independently checked against public metadata at the
declared immutable revisions. Acquisition and loading verify those expectations;
observing new local bytes cannot update them. Revision-specific directories
reuse verified immutable files by hard link where supported. Restoring missing
models uses the Hugging Face snapshot downloader. This model acquisition is
separate from the frozen SEC and Yahoo snapshots.

Embedding cache contracts include the extraction source, locked and installed
runtimes, verified checkpoint bytes, context, ordered cohorts and readouts. Reuse
checks the sidecar, payload checksum, shapes and finite values. Older cache
entries remain archival and do not satisfy the new contract. A changed adapter
or runtime therefore requires fresh extraction even when an outer pipeline
stage is otherwise reproducible.

Publication artifacts in the private archive are available to reviewers on
request. A publication restoration check uses a separate checkout and empty
DVC cache; source restoration, numerical regeneration and LaTeX compilation
are recorded separately. A clean local DVC status alone does not establish
remote availability.
