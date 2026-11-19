---
type: task
title: t02.1 Audit a fixed formation-month ledger
description: Verify monthly outcomes for the fixed December 2015 cohort.
links:
- .context/plan/finfm-workshop/tasks/t02-data-cohorts/evidence/coverage.md
status: done
---

# t02.1 Audit a fixed formation-month ledger

## Goal

Verify monthly outcomes for the fixed December 2015 cohort.

## Work and inputs

Cohort worker. Use the frozen input and the existing selection and issuer-weight logic. Build a private sidecar keyed by formation, issuer and month and bound to input hashes.

## Acceptance

- [x] Check a security that remains traded after rank-out. Reconcile selected PERMNOs and formation PERMCOs without altering the prepared manifest.

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
