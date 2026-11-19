---
type: plan
title: FinFM AAAI-27 workshop submission
description: Anonymous, theory-led FinFM workshop paper on when foundation-model geometry is economic, due 20 Nov 2026 AoE.
links:
- .context/plan/journal-study/README.md
status: in-progress
---

# FinFM AAAI-27 workshop submission

## Goal

Prepare, but do not submit, an anonymous AAAI-27 FinFM long paper (at most 7 technical pages) arguing that predictive content fixes a representation only up to the transformations its readout class can undo. It pairs that with a neighbour-margin certificate for k-NN networks and CRSP–SEC evidence labelled retrospective and in sample. The deadline is 20 Nov 2026 23:59 AoE; in-person presentation in Montréal is required. The journal study continues in [journal-study](../journal-study/README.md).

## Acceptance

- [ ] Every claim in the submission maps to a checked proof, a compiled Lean declaration or a saved stage output (audit claim map).
- [ ] The anonymous PDF builds from a clean directory with no undefined references, at most 7 technical pages, and passes the anonymity checks.
- [ ] The audit, journal roadmap, cover note and OpenReview abstract exist and state what remains unresolved.
- [ ] `just check` passes, or every check that could not run is reported.

<!-- insitu:begin sql
id = "planning-children"
model = "children"
template = "children.md.j2"
-->

| Status | Item | Description |
| --- | --- | --- |
| in-progress | [Review CRSP-SEC evidence and test reparametrization robustness](tasks/evidence/README.md) | Gate the saved CRSP–SEC results and run the out-of-sample spatial APT extension. |
| in-progress | [Write the audit, roadmap and cover note](tasks/handoff/README.md) | Research audit, claim-to-evidence map, journal roadmap and cover note. |
| in-progress | [Verify and extend references for the workshop paper](tasks/references/README.md) | Verify every citation against primary sources and add the closest competing work. |
| in-progress | [Write and build the anonymous AAAI-27 submission](tasks/submission/README.md) | Anonymous AAAI-27 LaTeX source, compiled PDF and OpenReview abstract. |
| in-progress | [Verify and extend the theory with a neighbour-margin certificate](tasks/theory/README.md) | Check the counterexample, alignment and stability claims; add the neighbour-margin certificate in prose and Lean. |

`5 open; 0 terminal`

<!-- insitu:end -->

## Backlinks

<!-- insitu:begin sql
id = "reference-backlinks"
model = "backlinks"
template = "backlinks.md.j2"
-->

_No declared backlinks._

<!-- insitu:end -->
