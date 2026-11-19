---
description: "Typed measurements of firm proximity from tabular foundation models."
---

# Free Foundations

The [paper](src/latex/projects/free-foundations/src/body.tex), *Pretrained Tabular
Features and the Measurement of Financial Proximity*, studies economic measurement
with frozen tabular representations. Its shared outline is being developed for
arXiv and FinFM targets. The mathematical framework is checked in Lean; the
empirical study uses CRSP CIZ total returns and dated SEC CompanyFacts.

Each December's top 1,000 CRSP issuers form a cohort followed through exits. The
study replicates Fernández's characteristic-history spatial CAPM, then asks whether
networks built directly from four pinned tabular foundation models' representations
organize return premia and co-movement. Only the spatial coefficient is fitted to
returns; every estimate carries an in-sample interval.

| Directory | Purpose |
| --- | --- |
| `src/python` | The `free-foundations` study application in a uv workspace |
| `src/lean` | Lean definitions, proofs, frozen type contracts and the blueprint |
| `src/latex` | The manuscript and supplement |
| `data` | The layered DVC pipeline, study contract and data pointers |
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
just sources EXTRACT.csv EXTRACT.py  # deliberately recover sources, freeze, record
just build                    # check fingerprints, then run stale DVC stages
just latex::paper arxiv       # render saved results and compile the arXiv paper
```

The [data guide](data/README.md) describes every stage, acquisition rules
and artifact restoration from the private data remote.

## Find your way

- [The study contract](data/research/crsp-sec/README.md) governs every empirical stage.
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
