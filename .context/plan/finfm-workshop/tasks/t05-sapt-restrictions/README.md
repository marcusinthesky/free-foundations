---
type: task
title: t05 Spatial APT pricing restrictions
description: Evaluate model-specific pricing restrictions and pricing errors in sample.
links:
- .context/plan/finfm-workshop/tasks/t05-sapt-restrictions/evidence/restriction.md
- src/python/apps/free_foundations/src/free_foundations/study/experiments/apt.py
- src/python/apps/free_foundations/src/free_foundations/study/sources/factors.py
- src/lean/FreeFoundations/ReversibleNetwork.lean
status: in-progress
---

# t05 Spatial APT pricing restrictions

## Goal

Test the approximate pricing restrictions associated with the maintained factor and network model.

## Work and inputs

Develop a known-restriction fixture while [01](../t01-theory/README.md) specifies the maintained assumptions. Empirical tests require [03](../t03-spatial-inference/README.md) dated loadings, graph identities and estimates on the verified cohort. Only the optional mimicking-factor contrast waits for [04](../t04-pcoa-interpretation/README.md). Own proposed `study/pricing.py`, matching tests and `pricing/` research outputs.

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

`pricing/` with model, formation, factor ordering, structural and effective exposures, estimated premia, pricing errors and restriction statistics. Record the tested null, units and reference model in `evidence/restrictions.md` here.

## Acceptance

- [ ] Derive the tested mean restriction for each included SAR, factor-SLX or spatial-error specification and identify the tradability and identification assumptions.
- [ ] Estimate risk prices and report cross-sectional pricing-error RMS and the relevant joint restriction test with its regularity conditions. Retain issuer or date contributions for uncertainty analysis.
- [ ] Recover a known restricted case on synthetic inputs and demonstrate sensitivity to an injected pricing error. Tie each empirical comparison to the fitted model and exact roster.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t05.2 Estimate and test in-sample pricing restrictions](tasks/t05-2-primary-pricing-test/README.md) | Evaluate pricing restrictions for one accepted in-sample fit. |
| backlog | [t05.3 Evaluate the mimicking-factor pricing contrast](tasks/t05-3-mimicking-pricing/README.md) | Test pricing with an additional mimicking factor. |

`2 open; 1 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
