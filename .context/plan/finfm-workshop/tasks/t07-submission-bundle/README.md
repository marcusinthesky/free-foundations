---
type: task
title: t07 Write, review and package the FinFM paper
description: Plan the argument, write the shared sections, render verified results and prepare the reviewed FinFM bundle for the authors.
links:
- .context/plan/finfm-workshop/tasks/t07-submission-bundle/evidence/candidate.md
- dvc.yaml
- src/latex/ARCHITECTURE.md
- .context/plan/finfm-workshop/audit.md
status: in-progress
---

# t07 Write, review and package the FinFM paper

## Goal

Deliver an anonymous FinFM paper and matching submission materials for author
review. Start the manuscript brief, asset interfaces and source verification
alongside research. The children own the sections and evidence. The bundle
owner owns the FinFM target, audit, roadmap, cover note and release files.
See [work allocation](../../work-allocation.md) for dependencies.
The [candidate handoff](evidence/candidate.md) records the exact local PDF,
matching title and abstract, and open author decisions.

## Acceptance

- [x] Receive complete section drafts and independent review dispositions on the revised candidate. Reconcile all four aims with the evidence selected in the editorial brief.
- [ ] Rebuild from saved outputs in a clean build directory with `just latex::paper finfm` and run `just check`. Inspect PDF text, metadata, links, dimensions and technical page count against the verified venue instructions. Check permitted contents, anonymity, rights and disclosures for any supplement.
- [ ] Assemble the reviewed PDF, matching plain-text title and abstract, required form fields and approved supplement if applicable. Record filenames, hashes, source revision and checks. Keep the audit, roadmap and cover note in the internal author handoff.
- [ ] Record author list and order, OpenReview readiness, presenter availability, supplement choice and the authors' submit decision. Flag pending decisions and the verified deadline.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [t07.1 Plan the manuscript and page budget](tasks/a-manuscript-plan/README.md) | Turn the shared section outline into a seven-page workshop argument and exhibit budget. |
| in-progress | [t07.2 Integrate evidence and render exhibits](tasks/b-evidence-exhibits/README.md) | Deliver reproducible publication assets and an exhibit inventory keyed to accepted results. |
| in-progress | [t07.4 Write methodology, data and appendices](tasks/d-methods-data/README.md) | Draft the formal argument, empirical design and technical appendix against verified inputs. |
| in-progress | [t07.7 Independently review and revise the candidate](tasks/g-review/README.md) | Independently audit the rendered candidate and track author revisions through closure. |

`4 open; 3 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
