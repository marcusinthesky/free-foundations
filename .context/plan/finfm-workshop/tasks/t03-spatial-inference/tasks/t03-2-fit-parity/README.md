---
type: task
title: t03.2 Verify estimator parity and comparison identities
description: Verify fit implementation parity and publish a comparison identity.
links:
- .context/plan/finfm-workshop/tasks/t03-spatial-inference/evidence/baseline.md
- .context/plan/finfm-workshop/tasks/t03-spatial-inference/evidence/mean_median.md
status: in-progress
---

# t03.2 Verify estimator parity and comparison identities

## Goal

Verify fit implementation parity and publish a comparison identity.

## Work and inputs

Spatial worker. Use the existing statadic and profile-likelihood paths and the accepted t02 roster. Work against a fixture before opening real data.

## Acceptance

- [x] Show original-sample parity on the declared relative tolerance. Record ordered issuers, dates and masks and demonstrate rejection of a mismatched comparison.
- [ ] Retain the median-return fit as the Fernández benchmark. For the expected-return contrast, use each issuer’s arithmetic mean excess return over the same observed quarters, weighting issuers equally in the second stage. Hold the formation, ordered roster, masks, MM betas, graph, and intercept specification fixed within each contrast. Record available fits and boundary diagnostics. Pass paired quarter-block draws to t06.3, recomputing means, medians and betas on the same draws. Qualify the mean as conditional on observed returns and report sensitivity to influential issuer-quarters.

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
