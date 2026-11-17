---
description: Static Schematter contracts for plans, references and the repository changelog.
---

# Document schemas

`just context-check` selects schemas by record path. Plans and tasks share the
work-item contract; `type` asserts their physical role. References use flat CSL
metadata and derive citation keys from directory names. Local references are
validated when present.

Entry points and records have a 1,500-token budget. Schematter checks document
shape; the workflow helper checks containment, declared links and completion.

`just changelog-check` validates the root `CHANGELOG.md` using the
shared changelog contract, with `Unreleased` allowed for changes
awaiting a pull request. Published entries use `PR #NUMBER: Title` headings.
Categories are `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed` and `Security`,
each containing a bullet list. Frontmatter permits only `type` and `description`.
Both checks run in CI and through pre-commit hooks.

## Agent skills

`just skills-check` validates repository-owned `SKILL.md` files against
`documents/skill.document-schema.yaml`, including the parent-directory name and
500-line limit. It runs in pre-commit and CI. The standard's frontmatter fields
are closed and bounded; the token, heading and workflow limits are local rules.

Write a concise description of what the skill does and when it applies, with
examples of triggering and near-miss tasks where useful. Evaluate behavior on
realistic cases against a baseline; schema validity does not establish accurate
triggering, useful instructions or correct results. Keep the entry point focused;
put conditional detail in linked files and say when to read them. For bundled
scripts, use skill-relative paths, state prerequisites, pin dependencies and
provide clear failure messages. Include examples or edge cases when they help.

See the Agent Skills [specification](https://agentskills.io/specification),
[best practices](https://agentskills.io/skill-creation/best-practices),
[description guidance](https://agentskills.io/skill-creation/optimizing-descriptions),
[evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills), and
[script guidance](https://agentskills.io/skill-creation/using-scripts).
