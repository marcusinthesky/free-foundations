---
type: task
title: t03 In-sample spatial inference
description: Estimate matched in-sample spatial effects and covariance components.
links:
- .context/plan/finfm-workshop/tasks/t03-spatial-inference/evidence/baseline.md
- src/python/apps/free_foundations/src/free_foundations/study/experiments/apt.py
- src/python/apps/free_foundations/src/free_foundations/study/experiments/replication.py
- src/python/apps/free_foundations/src/free_foundations/study/experiments/comovement.py
- src/python/apps/free_foundations/src/free_foundations/methods/spatial_ml.py
status: in-progress
---

# t03 In-sample spatial inference

## Goal

Estimate the Fernández baseline and the incremental effect of changing the network on a common population.

## Work and inputs

Start estimator and diagnostic tests with fixtures. Run financial estimates after [t02](../t02-data-cohorts/README.md) supplies the verified panel and states. Use [t01](../t01-theory/README.md) for interpretation. Own the replication, co-movement and APT experiments under `study/experiments/`, the spatial methods under `methods/`, and matching tests.

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

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t03.2 Verify estimator parity and comparison identities](tasks/t03-2-fit-parity/README.md) | Verify fit implementation parity and publish a comparison identity. |
| backlog | [t03.3 Compare native, calibrated and direct-input geometry](tasks/t03-3-geometry-contrasts/README.md) | Compare frozen and direct geometry on the same financial sample. |
| backlog | [t03.4 Separate exposure, residual covariance and risk](tasks/t03-4-covariance-and-risk/README.md) | Distinguish common exposure, spatial residual dependence and model-implied risk. |

`3 open; 1 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
