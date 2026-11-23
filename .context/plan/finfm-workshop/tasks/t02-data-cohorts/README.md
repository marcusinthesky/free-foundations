---
type: task
title: t02 Data and formation cohorts
description: Validate fixed formation rosters, issuer histories, terminal returns and coverage.
links:
- .context/plan/finfm-workshop/tasks/t02-data-cohorts/evidence/coverage.md
- data/research/crsp-sec/README.md
- src/python/apps/free_foundations/src/free_foundations/study/sources/crsp.py
- src/python/apps/free_foundations/src/free_foundations/study/panel/prepare.py
- src/python/apps/free_foundations/src/free_foundations/study/experiments/inputs.py
status: done
---

# t02 Data and formation cohorts

## Goal

Follow each December formation through the observation horizon and quantify which US observations support the Fernández reimplementation.

## Work and inputs

Own `study/sources/crsp.py`, `study/experiments/inputs.py`, the preparation and input verification in `study/run.py`, the CRSP–SEC data guide and their corresponding tests. Coordinate cohort accessor changes through the integration owner in [work allocation](../../work-allocation.md).

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

The [coverage receipt](evidence/coverage.md) binds the private 2015 formation-month
sidecar to the frozen inputs and verifies its reconstructed quarterly outcomes
against the prepared panel. It documents which findings the observed-quarter
design supports and which exit information remains unavailable.

## Acceptance

- [x] Key each monthly outcome by formation, issuer and month. Document the selected security classes, weights, rank changes, observed returns, missing returns and available terminal evidence.
- [x] Test a selected security continuing outside the next roster and a partial quarter with a known total loss. Preserve unresolved exits and avoid adding delisting returns to CIZ total returns.
- [x] Reconcile monthly and quarterly counts to the manifest and give publication the Fernández-to-US coverage bridge with denominators, exclusions and revised CompanyFacts limitations.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

_No open children._

`0 open; 3 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
