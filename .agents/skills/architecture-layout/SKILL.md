---
name: architecture-layout
description: Use when evaluating or designing where Free Foundations code, data stages, tests, documents or infrastructure belong, including module boundaries and repository restructures.
---

# Architecture layout

## Workflow

1. Establish the requested scope and outcome: evaluate the current layout,
   design a layout, or implement an authorized change. Read nearby README and
   ARCHITECTURE files. Identify existing owners and consumers before proposing
   a new abstraction; reuse an existing module or library when it satisfies the
   contract. File size alone is not a reason to split or create a package.
2. Examine the relevant boundaries using evidence:
   - **Ownership and cohesion:** Can a contributor find the owner, and do things
     that change together live together? Keep each unit's responsibility clear.
   - **Dependencies and encapsulation:** Trace relevant imports and public
     interfaces. Keep intended dependency direction clear and cycles forbidden;
     avoid reaching into another module's internals without a reason.
   - **Coupling:** Identify changes that force unrelated owners to change.
     Share a contract only when consumers actually need the same behavior; a
     little local duplication may be preferable to coupling distinct contracts.
   - **Discoverability:** Make CLI commands, transformations, schemas, tests,
     fixtures and documents easy to find from their owning area.
3. Choose the smallest useful boundary: a function, module, package or separate
   workspace project. A package or project should reflect an actual dependency,
   distribution, build or ownership need. Organize by layer, capability or a
   combination according to the work; do not impose a universal directory tree.
4. For pipeline work, preserve the established DVC stage ownership in `dvc.yaml`:
   frozen `sources`, then `prepare`, the expensive `representations`, `measurement`
   and `replication`, and saved-result `publication`. Organize capabilities within
   the `study`, `representations`, `fernandez` and `panel` subpackages as they arise.
   Distinguish Python imports from DVC artifact dependencies: the latter connect
   producers and consumers without requiring cross-layer Python imports. Apply
   Tach rules to durable module boundaries and DVC to artifact dependencies.
5. For a move or split, trace the affected consumers before changing paths:
   imports and public APIs, CLI registration, package configuration, tests and
   fixtures, Tach, DVC and Semflow dependencies, and documentation links as
   applicable. Preserve behavior and scientific contracts unless the user asks
   for a change; report any intended behavior change separately. Do not treat
   missing static references as proof that dynamic or external consumers do not
   exist.
6. Use the repository's existing gates rather than adding tests that merely
   assert a directory tree or private call sequence. For tests and fixtures,
   follow [Python testing](../python-testing/SKILL.md). Run focused checks while
   working and `just check` before handoff; report checks that could not run.

## Results

For an evaluation, report concrete findings with locations, effects and ranked
recommendations. For a design, show the proposed ownership and dependency
boundaries, explain meaningful tradeoffs and how they are enforced. For an
implementation, summarize what moved, whether behavior changed and the evidence
from verification. Keep the review proportional to the requested change.

For example, if both `study.features` and `panel.characteristics` need the same
as-of filing cutoff, first inspect its existing owner and date semantics. Share it
only if both consumers require the same contract; keep separate rules when their
treatment of missing, late or amended filings differs.
