---
type: plan
title: FinFM AAAI-27 workshop submission
description: Theory and in-sample CRSP–SEC evidence for an anonymous FinFM workshop paper on economic measurement with frozen tabular representations.
links:
- .context/plan/journal-study/README.md
status: in-progress
---

# FinFM AAAI-27 workshop submission

## Goal

Prepare an anonymous AAAI-27 FinFM long paper on what frozen tabular representations
measure about firms. Ground the descriptive and inferential study in a US
reimplementation of Fernández using CRSP–SEC formation cohorts. Use frozen
encoders, economically calibrated readouts and in-sample spatial inference.
Keep pretrained weights fixed. Estimate every financial contrast in sample on its declared roster and outcome mask. The workshop excludes train/test splits, forecasting and portfolio backtests. Authors control submission by 20 Nov 2026
23:59 AoE and the in-person presentation in Montréal.

Use the [work allocation](work-allocation.md) to find each task's inputs, write
scope, dependencies and handoff. The [journal plan](../journal-study/README.md)
records the broader programme.

## Acceptance

- [ ] Every claim in the submission maps to a checked proof, a compiled Lean declaration or a saved stage output (audit claim map).
- [ ] Each numbered research task supplies evidence or a documented limitation. Empirical claims identify their cohort, estimand and uncertainty.
- [ ] The complete manuscript implements the workshop brief and has been independently reviewed on the bundled revision. The [paper aims](paper-aims.md) account for the evidence behind each headline contribution.
- [ ] The anonymous PDF builds from a clean directory with no undefined references, at most 7 technical pages, and passes the anonymity checks.
- [ ] The audit, journal roadmap, cover note and OpenReview abstract exist and state what remains unresolved.
- [ ] `just check` passes, or every check that could not run is reported.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t03 In-sample spatial inference](tasks/t03-spatial-inference/README.md) | Estimate matched in-sample spatial effects and covariance components. |
| in-progress | [t04 PCoA and economic interpretation](tasks/t04-pcoa-interpretation/README.md) | Explain the geometry through principal coordinates, economic alignment and dated mimicking portfolios. |
| backlog | [t05 Spatial APT pricing restrictions](tasks/t05-sapt-restrictions/README.md) | Evaluate model-specific pricing restrictions and pricing errors in sample. |
| in-progress | [t06 Uncertainty and robustness](tasks/t06-uncertainty-robustness/README.md) | Quantify dependence-aware uncertainty and document the estimation burden conditional on frozen encoder weights. |
| in-progress | [t07 Write, review and package the FinFM paper](tasks/t07-submission-bundle/README.md) | Plan the argument, write the shared sections, render verified results and prepare the reviewed FinFM bundle for the authors. |

`5 open; 2 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
