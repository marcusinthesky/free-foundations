---
type: task
title: t03.3 Compare native, calibrated and direct-input geometry
description: Compare frozen and direct geometry on the same financial sample.
links:
- .context/plan/finfm-workshop/tasks/t03-spatial-inference/evidence/panel_jacobian.md
status: in-progress
---

# t03.3 Compare native, calibrated and direct-input geometry

## Goal

Compare frozen and direct geometry on the same financial sample.

## Work and inputs

Spatial worker. Consume t03.2 and verified state identities. Pilot the original characteristic rung and use a direct-input readout on the same cohort and targets.

## Acceptance

- [ ] Bind native frozen-state, calibrated frozen-state and direct-input geometries to the same formation, ordered issuers, mask, exposure target and dated fitting information. Record their identities and reject mismatches.
- [ ] Document proxy reliability, estimated loadings, readout specification and any reuse of its calibration target. Interpret agreement on a reused target as descriptive in-sample fit. Report observed neighbourhood agreement separately from its sufficient certificate.
- [ ] Hand t06.3 the paired contrasts, estimation units and fixed or refitted quantities for dependence-aware uncertainty. Include this comparison in FinFM only after these checks.

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
