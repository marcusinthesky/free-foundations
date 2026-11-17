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
at commit time. Lychee needs network access. Lean is supplied by the pinned Nix development
environment. The first LaTeX build downloads Tectonic's TeX bundle. Language checks run when their source files change.

Python dependencies and the typed model registry live in `src/python`; see
[the Python guide](src/python/README.md). Install the locked data and development
environment with `uv sync --project src/python --frozen`. TypeScript starts as a private,
dependency-free Bun workspace; add packages under its `apps/` or `packages/`
directories when needed. Run `just lean-build` and `just latex-build` to build
the proof library and document. The Lean build includes frozen manuscript type
contracts; `just proof-audit` checks every project proof source and its axiom
dependencies. See the [Lean guide](src/lean/README.md) for coverage and assumptions.

## One quarterly CRSP–SEC study

The [paper](src/latex/main.tex), *Pretrained Tabular Features and the Measurement of
Financial Proximity*, separates predictive information, economic alignment and
exposure estimation. Its mathematical framework is retained while the empirical
study migrates to CRSP CIZ total returns and dated SEC disclosures. Numerical
conclusions from the earlier current-survivor experiment are archived in
[research/archive/current-survivor](research/archive/current-survivor).

The [study contract](research/crsp-study/README.md) and
[versioned specification](research/crsp-study/study.json) govern every active
empirical stage. Annual membership selects the prior-December top 1,000 CRSP
securities, then groups selected classes into issuer portfolios. The archive
covers 2001–2025; accounting features begin with actual XBRL availability from
2009. All analyses use the same quarterly issuer roster, calendar and observed
return mask. Missing characteristics do not create separate complete-case samples.

The original Fernández characteristic-history spatial CAPM is the replication
benchmark. A ladder adds standard entity-wide XBRL facts and then all structured
scalar facts, including custom concepts and dimensional contexts. Four pinned
pretrained tabular models and conventional controls share each information rung.
Correlations and covariances use pairwise overlapping observations; undefined
pairs and any positive-semidefinite repair are explicit in the audit.

## Data and pipeline

[DVC](https://dvc.org) records seven stages in `dvc.yaml`:

| Stages | Responsibility |
| --- | --- |
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
just latex-build              # render saved results and compile the paper
```

Routine numerical stages never access the network. Missing or unverifiable
source evidence remains visible in the availability ledger. Unresolved historical
PERMNO–CIK links are distinguished from absent XBRL; neither current ticker
matches nor old empirical results certify the new study. The staged CRSP extract
also lacks terminal-return flags, so this migration does not certify complete
delisting coverage merely because it uses CRSP.

`just latex-build` does not estimate models. `just build` checks fingerprints and
runs stale DVC stages, including representation extraction if its inputs change.
[semflow](https://github.com/marcusinthesky/semflow) fingerprints reachable code.
After code changes run `just semflow-refresh`; after changing commands run
`uv run --project src/python semflow patch --apply` first.

Checkpoint expectations are versioned in
`src/python/src/free_foundations/checkpoints.json`. Loading verifies pinned
revision and bytes. Model extraction is separate from financial estimation;
readouts and reports consume saved states without loading local weights.

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

The financial source stage is frozen under routine reproduction.
`just python-universe` explicitly resumes SEC recovery and records the source
vintage. Replacing CRSP bytes requires a separate vintage; changing source evidence
invalidates dependent results. Reviewers can request the private publication
archive. See [the publication guide](src/latex/README.md) for rendering details.
