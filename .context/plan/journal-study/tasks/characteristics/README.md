---
type: task
title: Build Fernández characteristics from CRSP ME and SEC books
description: The four Fernández characteristics use CRSP market equity and SEC book values.
links: []
status: in-progress
---

# Build Fernández characteristics from CRSP ME and SEC books

## Goal

Market equity comes from CRSP issuer capitalization; accounting values from CompanyFacts; debt maturity excludes leases; missing tags stay missing.

## Acceptance

- [ ] Each value records its CRSP and SEC components.
- [ ] A coverage table by characteristic and year is reviewed before encoding.

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
