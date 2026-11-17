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

### Changed

- The Python package moved into a uv workspace under `src/python/apps/free_foundations`.
- Tests mirror the source modules they exercise.
- Language checks run through per-language justfile modules.
- Nix definitions moved under `infra/nix`; shell entry no longer installs tools.
- DVC runs from the locked Python workspace rather than a separate root project.

### Removed

- The unused TypeScript placeholder workspace.
