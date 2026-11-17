---
description: "Typed measurements of firm proximity from tabular foundation models."
---

# Free Foundations

The [paper](src/latex/main.tex), *Pretrained Tabular Features and the Measurement of
Financial Proximity*, separates predictive information, economic alignment and
exposure estimation. Its mathematical framework is checked in Lean while the
empirical study migrates to CRSP CIZ total returns and dated SEC disclosures.
Numerical conclusions from the earlier current-survivor experiment remain only in
the Git history; they are not findings of this study.

Annual membership selects the prior-December top 1,000 CRSP securities, then groups
selected classes into issuer portfolios. All analyses use the same quarterly issuer
roster, calendar and observed return mask; missing characteristics do not create
separate complete-case samples. The original Fernández characteristic-history
spatial CAPM is the replication benchmark. A ladder adds standard entity-wide XBRL
facts and then all structured scalar facts, and four pinned pretrained tabular
models and conventional controls share each information rung.

| Directory | Purpose |
| --- | --- |
| `src/python` | The `free-foundations` study application in a uv workspace |
| `src/lean` | Lean definitions, proofs, frozen type contracts and the blueprint |
| `src/latex` | The manuscript and supplement |
| `research` | The DVC pipeline, study contract and archived evidence |
| `.context` | Project plans and reference records |

## Get ready

Use Linux x86-64 or ARM64 with Git and Nix. Initial setup downloads locked
dependencies, model runtimes and TeX resources; later checks use prepared inputs.

```bash
bash infra/nix/install-devenv.sh
devenv shell
just setup
just check
```

Run `just --list` to discover commands; each language has a module, for example
`just python::test`, `just lean::proof-audit` and `just latex::build`.

## Study and pipeline

[DVC](https://dvc.org) stages in `dvc.yaml` reproduce the study from frozen sources.
[semflow](https://github.com/marcusinthesky/semflow) fingerprints the code each
stage reaches, so documentation edits do not rerun model inference.

```sh
just python-universe          # deliberately recover sources and record the frozen stage
just build                    # check fingerprints, then run stale DVC stages
just latex::paper             # render saved results and compile the paper
```

The [research guide](research/README.md) describes every stage, acquisition rules
and artifact restoration from the private data remote.

## Find your way

- [The study contract](research/crsp-study/README.md) governs every empirical stage.
- [The Python workspace](src/python/README.md) explains code and commands.
- [The Lean workspace](src/lean/README.md) records proof assumptions and audits.
- [The LaTeX workspace](src/latex/README.md) explains rendering and compilation.
- [Project context](.context/README.md) explains plans and references.
- [AgentSync](.agents/README.md) manages shared agent instructions and skills.
- [Architecture](ARCHITECTURE.md) explains ownership and updates.

Edit source, run `just sync`, then `just check`. Formatting and synchronization
are explicit writes. External links run separately through `just links`.

## Update

Commit local work, then run:

```bash
env -u PYTHONPATH -u PYTHONHOME uvx --from copier==9.16.0 copier update
```

Review the diff and conflicts, then run setup, sync and check. Copier selects the
latest stable tag from the source saved in `.copier-answers.yml`; add
`--vcs-ref TAG` to choose a specific release. Removing capabilities requires
manual migration because Copier can remove previously owned paths.

This project uses [Exordio](https://github.com/marcusinthesky/exordio).
