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

## One measurement study

The [paper](src/latex/main.tex), *Pretrained Tabular Features and the Measurement of
Financial Proximity*, develops a measurement argument and tests its implications
with one retrospective financial study. Frozen features can make an exposure target easier
to estimate while their native distances remain unsuitable for a financial use.
The common-marginal covariance comparison qualifies the principal forecasting
result; it is part of the central evidence. The main text develops this argument
through the introduction, framework, empirical design, results, and conclusion;
exact propositions and proofs appear in the mathematical appendix.

The [direct-geometry extension](research/panel/geometry/README.md) compares signed
Gram covariances with spatial covariances on the same financial geometry, leading
with common marginal variances. Rank-five principal coordinates provide
descriptive characteristic portfolios. The replication appendix also crosses
calendar timing with two documented MM software implementations.

The [study protocol](research/panel/three-foundations/README.md) fixes financial
histories, four pretrained models, conventional and reset controls, and a separate
cross-fitted exposure readout. The retained checks address metric choice,
fold-induced geometry, encoder context versus financial calibration size, and
covariance specification. The supporting appendix replicates the core Fernández
spatial-CAPM procedure on common US cohorts and audits its stated VaR calibration.
Pilot grids, input ladders, alternative tasks and historical model variants are
available in Git history rather than supported as live experiments.

## Data and pipeline

[DVC](https://dvc.org) records nine stages in `dvc.yaml`:

| Stages | Responsibility |
| --- | --- |
| `universe`, `pilot`, `market_metadata` | Frozen financial source snapshots; restored without acquisition |
| `model_checkpoints` | Four pinned pretrained checkpoints and verified hashes |
| `prepare` | Filing and price audits, characteristics, shared annual observations |
| `representations` | Frozen feature states and declared baseline states |
| `measurement` | Exposure readouts, forecasts, decisive checks and paired inference |
| `replication` | CAPM replication, generated-beta uncertainty and VaR audit |
| `publication` | Tables, figure, scalar bindings and source/claim audit |

Model extraction is separate from financial calibration. Recomputing economic
readouts or publication assets consumes saved states and requires no local model
weights. Numerical stages reject missing frozen inputs rather than refetching
them. Original pilot data remain a raw source snapshot; no pilot forecasting
command remains.

```sh
just data-pull                 # restore recorded results and financial sources
just python-panel              # reproduce the retained measurement stage
just python-fernandez          # reproduce the supporting CAPM/VaR appendix
just python-publication        # reproduce saved-result publication assets
just latex-build               # render saved results and compile the paper
```

`just latex-build` does not run empirical estimation. Missing artifacts fail with
an explicit restoration instruction. `just build` checks fingerprints and runs
all stale DVC stages, including expensive extraction when its inputs changed.
[semflow](https://github.com/marcusinthesky/semflow) fingerprints each command's
reachable code. After code changes run `just semflow-refresh`; after changing
commands run `uv run --project src/python semflow patch --apply` first.

Checkpoint expectations are versioned in
`src/python/src/free_foundations/checkpoints.json`. Loading verifies the pinned
revision and bytes; locally observed files cannot update those expectations.
State cache contracts also bind extraction source, installed/locked runtime,
context, ordered firms and readouts. Moving adapters or changing runtime settings
invalidates extraction identity. Historical arrays cannot be relabeled as newly
computed results.

## Artifact storage and restoration

Numerical results, states, contexts and detailed manifests live in DVC's cache
and the private Hugging Face bucket `marcusinthesky/free-foundations`. Git stores
source, protocols, checkpoint expectations and pipeline pointers. Model weights
remain local reproducible downloads and are not uploaded to the data remote.

To access the bucket, create S3 credentials in the Hugging Face account settings
and store them outside Git:

```sh
dvc remote modify --local hf-bucket access_key_id HFAK...
dvc remote modify --local hf-bucket secret_access_key ...
just data-pull
```

Run DVC inside the devenv shell, which supplies the gateway checksum settings.
`just data-push` uploads newly recorded artifacts. Restoring sources, regenerating
numbers and compiling the manuscript are distinct checks; a clean local DVC
status does not establish that the remote archive is complete.

The three financial sources use frozen stages with no acquisition command.
`just python-universe` deliberately reacquires and records the universe snapshot;
set `EDGAR_IDENTITY` for that operation. Replacing a source vintage requires
regenerating its dependent results. Reviewers can request the private publication
archive. See [the publication guide](src/latex/README.md) for rendering details.
