---
type: task
title: 02 Data and formation cohorts
description: Validate fixed formation rosters, issuer histories, terminal returns and coverage.
links:
- data/research/crsp-sec/README.md
- src/python/apps/free_foundations/src/free_foundations/study/crsp.py
- src/python/apps/free_foundations/src/free_foundations/study/run.py
- src/python/apps/free_foundations/src/free_foundations/study/rosters.py
status: backlog
---

# 02 Data and formation cohorts

## Goal

Follow each December formation through the observation horizon and quantify which US observations support the Fernández reimplementation.

## Work and inputs

Start immediately. Own `study/crsp.py`, `study/rosters.py`, the preparation and input verification in `study/run.py`, the CRSP–SEC data guide and their corresponding tests. Coordinate the cohort accessor migration through the integration owner in [work allocation](../../work-allocation.md).

Read the shared [module and artifact contracts](../../work-allocation.md) before integrating changes.

## Handoff

The prepared panel's proposed `cohort_monthly.parquet`, its verified manifest, quarterly cohort outcomes, and `evidence/coverage.md` here. Publish the column names and a small worked example first so consumers can build fixtures.

## Acceptance

- [ ] Key each monthly outcome by formation, issuer and month. Document the selected security classes, weights, rank changes, observed returns, missing returns and available terminal evidence.
- [ ] Test a selected security continuing outside the next roster and a partial quarter containing a documented terminal loss. Preserve unresolved exits as unknown and apply CRSP delisting returns once.
- [ ] Reconcile monthly and quarterly counts to the manifest and give publication a Fernández-to-US coverage table with denominators, exclusions and revised CompanyFacts limitations.

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
