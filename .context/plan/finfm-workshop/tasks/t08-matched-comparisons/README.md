---
type: task
title: t08 Matched financial and encoder comparisons
description: Establish how factor controls, graph weights, financial inputs and encoder choice affect in-sample spatial fit.
links:
- .context/plan/finfm-workshop/tasks/t08-matched-comparisons/evidence/implementation.md
status: in-progress
---

# t08 Matched financial and encoder comparisons

## Goal

Establish how factor controls, graph weights, financial inputs and encoder choice affect in-sample spatial fit.

## Acceptance

- [ ] Complete the matched comparisons and record the conditional interpretation decision before submission.
- [ ] Deliver saved estimates, sample identities, uncertainty and claim limits to the submission-bundle owner for manuscript integration and review.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t08.4 Compare frozen encoders on matched inputs](tasks/encoder-comparison/README.md) | Evaluate the same financial panels across pinned encoders. |
| in-progress | [t08.1 Matched Fama–French benchmarks](tasks/factor-benchmarks/README.md) | Estimate joint and separate factor comparisons on the spatial panel. |
| in-progress | [t08.3 Build three matched financial input sets](tasks/financial-inputs/README.md) | Construct ratio, underlying-financial and broad financial panels. |
| in-progress | [t08.5 Explain relationships in the selected geometry](tasks/geometry-interpretation/README.md) | Apply the 25% PCoA criterion to the selected financial model. |
| in-progress | [t08.2 Compare spatial weighting rules](tasks/kernel-weights/README.md) | Separate the effect of distance construction from the effect of weighting. |

`5 open; 0 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
