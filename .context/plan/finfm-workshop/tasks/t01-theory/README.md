---
type: task
title: 01 Theory and economic identification
description: Check representability, neighbour certificates and the reversible spatial multiplier.
links:
- src/lean/FreeFoundations/Geometry.lean
- src/lean/FreeFoundations/Neighbours.lean
- src/lean/FreeFoundations/ReversibleNetwork.lean
- src/lean/FreeFoundations/EndToEnd.lean
- src/lean/FreeFoundations/Selection.lean
status: backlog
---

# 01 Theory and economic identification

## Goal

Establish which economic targets a frozen representation can recover and which graph and factor assumptions support spatial inference.

## Work and inputs

Start immediately from the existing Lean declarations and the [prior proof audit](../../audit.md). Own `src/lean/` proof sources, blueprint and their documentation. Give the empirical teams a premise checklist before completing formal checks.

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

`evidence/theory.md` in this task, with each statement, assumptions, declaration or written proof, and the observable diagnostic that could assess its premises.

## Acceptance

- [ ] Define the restricted-readout stabilizer using equality of classes. Demonstrate geometric non-identification and interpret an uncertified row as inconclusive about its true neighbours.
- [ ] Apply the reversible bound to the actual symmetrized, row-normalized graph. Specify degree ratios, boundary distance, innovation bounds and the extra factor, trading and no-arbitrage assumptions needed for pricing.
- [ ] Scope statistical learning claims to fitted components, dependence and loss assumptions. Verify blueprint statements and record `just lean::check` with the proof revision.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

_No open children._

`0 open; 0 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
