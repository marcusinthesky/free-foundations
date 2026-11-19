---
type: task
title: 03 In-sample spatial inference
description: Estimate matched in-sample spatial effects and covariance components.
links:
- src/python/apps/free_foundations/src/free_foundations/study/apt.py
- src/python/apps/free_foundations/src/free_foundations/study/replication.py
- src/python/apps/free_foundations/src/free_foundations/study/comovement.py
- src/python/apps/free_foundations/src/free_foundations/study/spatial_ml.py
status: backlog
---

# 03 In-sample spatial inference

## Goal

Estimate the Fernández baseline and the incremental effect of changing the network on a common population.

## Work and inputs

Start estimator and diagnostic tests with fixtures. Run financial estimates after [02](../t02-data-cohorts/README.md) supplies the verified panel and states. Use [01](../t01-theory/README.md) for interpretation. Own `study/replication.py`, `comovement.py`, `apt.py`, `spatial.py`, `spatial_ml.py` and proposed `study/spatial_fit.py`, plus matching tests. Keep the historical APT comparison identifiable.

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

Existing replication/co-movement outputs and proposed `spatial_fit/` research outputs. Provide dated issuer exposures, factor order, graph identities, fitted spatial parameters, covariance components, diagnostics and per-period paired contrasts for 04–06. Document keys and units in `evidence/estimands.md` here.

## Acceptance

- [ ] Compare faithful ratios, direct inputs, native and calibrated TFM networks, industry, return-based and null controls on identical masks. Inventory fitted preprocessing, readouts, betas, variances and spatial parameters.
- [ ] Evaluate exposure alignment and residual dependence as distinct hypotheses. Compare fitted and common marginal variances. Record convergence, boundary reasons, degree ratios and multiplier conditioning.
- [ ] Record how estimated exposures enter ridge calibration and evaluation, including cross-fitting where targets are reused. Pair native and calibrated distances with the same direct-input baseline. Report proxy-graph overlap separately from the sufficient certificate.
- [ ] Report historical portfolio variance and plug-in VaR with distribution, holdings date and exit convention. Supply corrected estimates and exclusions for the baseline table and financial-effect figure.

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
