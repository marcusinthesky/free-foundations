---
type: changelog
description: Changes to the Free Foundations study, proofs, manuscript and repository tooling.
---

# CHANGELOG

## Unreleased

### Added

- Exordio v0.1.1-alpha configuration with planning and reference workflows.
- Schematter contracts for work items, references, budgets, skills and this changelog.
- AgentSync-managed shared instructions and skills for Codex and Claude Code.
- Python testing and architecture-layout agent skills.
- pytest-layout-enforcer for source-aligned test paths and registered test markers.
- A `semflow_refresh` DVC control stage and semflow patch, apply and refresh recipes.
- Batteries Lean linter with a recorded baseline of existing findings.
- GitHub Actions CI and workflow security audit.
- In-sample research stages: Fernández cross-sections with generated-beta intervals,
  quarterly spatial co-movement panels and Mantel alignment.
- Parameter-free k-nearest-neighbour networks from frozen representations, with size,
  industry and permutation-null comparators.
- statadic for spatial estimation, diagnostics, Mantel association and block lengths.
- `params.yaml` as the single study configuration (`crsp-sec-quarterly-v2`).
- Reference records for every manuscript citation and a generated `refs.bib`.

### Changed

- The Python package moved into a uv workspace under `src/python/apps/free_foundations`.
- Tests mirror the source modules they exercise.
- Language checks run through per-language justfile modules.
- Nix definitions moved under `infra/nix`; shell entry no longer installs tools.
- DVC runs from the locked Python workspace rather than a separate root project.
- `dvc.lock` records the pinned `model_checkpoints` stage.
- Fernández characteristics use CRSP market equity with SEC books; debt maturity
  excludes leases; scale errors and stale balance sheets stay unavailable.
- Data moved into `data/raw`, `data/processed` and `data/research` layers, and the
  CLI into `free-foundations stages <layer> <command>`.
- Formation cohorts follow each December roster forward through exits.
- Preparation identity binds only population settings.

### Removed

- The unused TypeScript placeholder workspace.
- The current-survivor study archive and the universe, panel and Fernández pipelines
  that only served it, with their CLI commands, tests and result rendering; Git
  history keeps them.
- Forecast scoring, cross-fitted decoders, Gram covariance, PCoA geometry and the
  PCA and supervised controls.
- The full-filing XBRL rung; the study uses CompanyFacts.

### Fixed

- The manuscript's undefined `eq:forecast` reference; the forecast covariance is
  now stated inline.
- Encoding collapses each fact part to its latest standard values before combining,
  so late quarters fit in memory (2019 peaks at 7.4 GB instead of over 24 GB).
- Tables label Fernández-rung model networks by model rather than as her
  characteristics.
- Publication metrics are declared at the DVC top level, since they sit inside the
  stage's tracked output.
