---
type: task
title: t06 Uncertainty and robustness
description: Quantify dependence-aware uncertainty and document the estimation burden conditional on frozen encoder weights.
links:
- .context/plan/finfm-workshop/tasks/t06-uncertainty-robustness/evidence/refit.md
- .context/plan/finfm-workshop/tasks/t06-uncertainty-robustness/evidence/resampling.md
- src/python/apps/free_foundations/src/free_foundations/methods/inference.py
- src/lean/FreeFoundations/ReadoutStability.lean
- .context/plan/finfm-workshop/tasks/t06-uncertainty-robustness/evidence/historical-gate.md
status: in-progress
---

# t06 Uncertainty and robustness

## Goal

Measure how sensitive the paper's conclusions are to dependence, generated quantities, formation choice and estimation burden.

## Work and inputs

Design resampling fixtures immediately. Use the corrected data from [t02](../t02-data-cohorts/README.md) and the estimands from [t03](../t03-spatial-inference/README.md), [t04](../t04-pcoa-interpretation/README.md) and [t05](../t05-sapt-restrictions/README.md) as each arrives. Own `methods/inference.py`, the corresponding tests and any verified robustness output.

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

`robustness/` with contrasts, effect sizes, interval endpoints, refitted quantities, resampling units, multiplicity family and formation sensitivity. Document the results and limits in `evidence/uncertainty.md` here.

## Acceptance

- [ ] Diagnose matched 10-NN bootstrap shrinkage against a refit on the original sample. Label conditional and refitted intervals and distinguish interval coverage from Holm-adjusted tests.
- [ ] Use paired, dependence-aware intervals with the financial effects, PCoA alignments and pricing errors. Report robustness across formations, network choices and overlap requirements.
- [ ] Use 03's estimation inventory to identify the observation unit, dependence, conditioning and uncertainty for each fitted readout or financial parameter. Limit the complexity claim to what freezing the encoder establishes.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t06.3 Qualify intervals, sensitivity and estimation burden](tasks/t06-3-intervals-and-sensitivity/README.md) | Attach validated uncertainty to available workshop endpoints. |

`1 open; 2 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
