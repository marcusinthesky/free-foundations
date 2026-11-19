---
type: task
title: Review CRSP-SEC evidence and test reparametrization robustness
description: Gate the saved CRSP–SEC results and run the out-of-sample spatial APT extension.
links: []
status: in-progress
---

# Review CRSP-SEC evidence and test reparametrization robustness

## Goal

Review the saved study before any number is quoted, then run the pre-specified out-of-sample spatial APT stage (`apt`) with raw and calibrated TFM geometry. Review notes: [gate](gate.md).

## Acceptance

- [x] Study digests agree across stage manifests, and each stage re-verifies the panel inventory and master contract.
- [x] Each model's pretraining data and cutoff are documented from its card or paper.
- [x] The bootstrap-centring anomaly is explained or reported as a limitation.
- [x] The APT extension specification is committed before its DVC run, and its outputs are rendered from saved files.

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
