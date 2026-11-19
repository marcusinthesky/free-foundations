---
type: plan
title: Journal-ready in-sample CRSP–SEC study
description: In-sample, parameter-light CRSP–SEC study and manuscript ready for journal submission.
links: []
status: in-progress
---

# Journal-ready in-sample CRSP–SEC study

## Goal

Replace forecast evaluation with in-sample inference: a faithful Fernández (2011) spatial CAPM on the full point-in-time population, a quarterly spatial panel of co-movement and parameter-free alignment, where each tabular foundation model's internal representation defines W directly and only the spatial coefficient is fitted. The approved design is in [design.md](design.md).

## Acceptance

- [ ] Every manuscript number traces to a saved in-sample estimate with its interval.
- [ ] No forecast, cross-fitted decoder, bandwidth or Gram parameter remains.
- [ ] `just check` passes.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [Estimate the Fernández, panel and alignment layers in sample](tasks/analysis/README.md) | In-sample estimates with intervals for every layer and network. |
| in-progress | [Build Fernández characteristics from CRSP ME and SEC books](tasks/characteristics/README.md) | The four Fernández characteristics use CRSP market equity and SEC book values. |
| backlog | [Encode two rungs with the direct control only](tasks/encoding/README.md) | Representations exist for both rungs, every model and the direct control. |
| backlog | [Render saved results and rewrite the manuscript](tasks/manuscript/README.md) | The manuscript reports the in-sample study from saved results. |
| in-progress | [Rewire DVC, semflow, Tach and documentation](tasks/pipeline/README.md) | DVC, semflow, Tach and documentation match the new stages. |
| in-progress | [Version the in-sample study specification](tasks/spec-v2/README.md) | One versioned specification declares the in-sample design. |

`6 open; 3 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
