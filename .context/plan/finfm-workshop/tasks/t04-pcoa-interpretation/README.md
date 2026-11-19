---
type: task
title: t04 PCoA and economic interpretation
description: Explain the geometry through principal coordinates, economic alignment and dated mimicking portfolios.
links:
- .context/plan/finfm-workshop/tasks/t04-pcoa-interpretation/evidence/interpretation.md
- src/python/apps/free_foundations/src/free_foundations/methods/networks.py
- src/python/apps/free_foundations/src/free_foundations/study/experiments/inputs.py
- src/python/apps/free_foundations/src/free_foundations/study/experiments/alignment.py
status: in-progress
---

# t04 PCoA and economic interpretation

## Goal

Determine which economic quantities align with stable directions in the frozen representations.

## Work and inputs

Develop decomposition, attribution and portfolio tests on fixed distance fixtures now. Run on verified [02](../t02-data-cohorts/README.md) rosters and representation states. Exposure overlays then consume [03](../t03-spatial-inference/README.md) estimates. Own proposed `study/pcoa.py`, its matching tests and the `pcoa/` research output.

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

`pcoa/` with dated coordinates, eigenvalues, economic alignments, stability comparisons and dated mimicking returns. Give submission the panel definitions and attribution target in `evidence/interpretation.md` here.

## Acceptance

- [ ] Record the chordal distance convention, negative inertia and retained eigenspaces. Check stability allowing sign and rotation ambiguity across dates.
- [ ] Quantify alignment with ratios and exposures against structured nulls. Attribute a defined distance or coordinate-derived quantity to financial inputs.
- [ ] For mimicking claims, save dated, normalized portfolio weights and returns with spanning evidence. Link any additional pricing claim to the test in [05](../t05-sapt-restrictions/README.md).

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t04.2 Audit subspaces and quantify economic alignment](tasks/t04-2-economic-alignment/README.md) | Link dated coordinates or subspaces to measured economics. |
| backlog | [t04.3 Evaluate dated factor-mimicking portfolios](tasks/t04-3-mimicking-portfolios/README.md) | Construct and test dated factor-mimicking portfolios. |

`2 open; 1 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
