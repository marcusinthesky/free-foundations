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

The [expanded experiment](research/expanded/README.md) compares accounting input
views and four pretrained models, retaining ticker-labeled annual distance matrices.

The [Fernández replication ladder](research/fernandez/README.md) separates the
published two-stage spatial CAPM from matched-input foundation models and
full-return covariance forecasts.

The [larger-universe coverage audit](research/universe/README.md) documents
1,000 distinct SEC issuers, extended Yahoo and French histories, and annual
filing availability. Run `just python-universe` with `EDGAR_IDENTITY` set to
resume its cached acquisition. Its changing annual cohorts are distinct from
the six-firm complete-history demonstration.

The [working paper](src/latex/main.tex) develops the measurement question,
chronological panel design, and conditional network-to-covariance stability
argument, with Finance Research Letters as a provisional outlet.
Build the PDF with `just latex-build`; empirical conclusions remain open.

The [chronological panel comparison](research/panel/RESULTS.md) constructs full
point-in-time characteristics, calibrates one spatial coefficient per approach
on 2016-2019, and scores 2020-2025 on matched annual cohorts. Run
`just python-panel` to reproduce its cached input ladder and annual distance matrices.
