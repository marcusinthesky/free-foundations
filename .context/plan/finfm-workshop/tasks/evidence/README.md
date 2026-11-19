---
type: task
title: Review CRSP-SEC evidence and test reparametrization robustness
description: Gate the saved CRSP–SEC results and test whether FM geometry survives prediction-preserving reparametrisation.
links: []
status: in-progress
---

# Review CRSP-SEC evidence and test reparametrization robustness

## Goal

Review the saved study before any number is quoted, then run a pre-specified, outcome-free reparametrisation stage on the saved 2016 states.

## Acceptance

- [ ] Roster, mask and spec hashes agree across the stage manifests.
- [ ] Each model's pretraining data and cutoff are documented from its card or paper.
- [ ] The bootstrap-centring anomaly is explained or reported as a limitation.
- [ ] The reparametrisation specification is committed before its DVC run, and its outputs are rendered from saved files.

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
