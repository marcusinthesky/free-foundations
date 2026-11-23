---
description: Why Python libraries and applications share one uv workspace and lock.
---

# Python workspace

Libraries and executable consumers have separate package boundaries. A single
uv workspace resolves cross-package imports locally and locks test, build
and runtime dependencies together. This keeps the example runnable and lets the
project grow without publishing internal packages.

| Tool | Responsibility |
| --- | --- |
| uv | Dependency resolution, installation and packaging |
| Ruff | Lint and formatting |
| Pyrefly | Static type checking |
| pytest | Behavior and entry-point tests |

The pinned Nix environment supplies native Ruff and Pyrefly executables. This
avoids Python wheels whose ELF interpreter assumes a conventional Linux layout,
so the checker commands also work on NixOS without a machine-level loader service.

Python commands scrub inherited `PYTHONPATH` and `PYTHONHOME` so an unrelated Nix
or user environment cannot inject incompatible Python packages. Setup is the
network boundary; checks use frozen, offline dependencies and never update locks.

## Study package

The Typer entry point exposes raw acquisition, processed measurements, research
experiments and publication. CLI defaults live in `study.paths`. DVC owns the
artifact dependencies and Semflow fingerprints the callback for each stage.
The root Python API exports the encoder contracts independently of the CLI.

Research pilots live under `pilots/` and run through the locked study
environment. Keep a pilot when it reproduces cited evidence or supports an
active experiment. Task evidence records link to their commands and retain
the inputs, results and verification limits.

| Package | Responsibility |
| --- | --- |
| `encoders` | Typed batches, contexts, pooling, frozen backend adapters and verified readout caches |
| `methods` | Distance, graph, factor, spatial and resampling operations on explicit numerical inputs |
| `artifacts` | Atomic file replacement, inventories and content hashes |
| `study.sources`, `study.panel` | Source promotion, dated panels, population identities and verified panel access |
| `study.representations` | Shared context construction, independent model cells, assembly and the saved-state reader |
| `study.experiments` | Verified inputs and study-specific estimators for each research result |
| `study.publication` | Tables, figures and individual manuscript values derived from saved results |

One representation cell owns all dates for one rung and model. The assembly
stage verifies the roster, input digest, quarter coverage and payloads. One
replication cell owns a formation and all of its paired draws. The collection
stage restores the declared formation order. Co-movement, alignment and the
historical APT comparison each own the draws and fits shared by their contrasts.
