---
description: FinFM task dependencies, write ownership and evidence handoffs.
---

# FinFM work allocation

The [paper aims](paper-aims.md) and final in-sample protocol in the 19 November
Paper Overview govern the workshop study. The coordinator pins the revision and allocates one
child at a time to each of three GPT-6.1 Terra high workers. The first wave owns
theory, cohort validation, and the manuscript brief and sources. Subsequent
workers take the next ready child or an independent review. Stable task paths
use hyphenated slugs and dotted display IDs.

| Task | Inputs needed for use | Handoff |
| --- | --- | --- |
| [t01 Theory](tasks/t01-theory/README.md) | t01.1–t01.2 and checked declarations | Statement, proof, measured premises and maintained assumptions |
| [t02 Cohorts](tasks/t02-data-cohorts/README.md) | Frozen CRSP and verified prepared panel | Fixed formation-month sidecar, audited quarterly coverage and estimator denominators |
| [t03 Spatial inference](tasks/t03-spatial-inference/README.md) | t02.3 for baseline, plus matched states and t01.2 premises for frozen-geometry contrasts | Fit and diagnostics with ordered issuer and outcome-mask identity |
| [t04 Interpretation](tasks/t04-pcoa-interpretation/README.md) | t02.3 and verified states, then t03.2 for exposure alignment | Dated eigenspaces, their descriptors and any tested alignment |
| [t05 Pricing](tasks/t05-sapt-restrictions/README.md) | t01 and t03 fits, plus t04.3 for a mimicking-factor contrast | Specification-specific mean restrictions and pricing-error test |
| [t06 Uncertainty](tasks/t06-uncertainty-robustness/README.md) | t02 panel and actual estimation units, then each of t03–t05 as available | Refit parity, interval scope, sensitivities and fitted-parameter inventory |
| [t07 Manuscript](tasks/t07-submission-bundle/README.md) | Checked theory, accepted evidence for each retained result, all sections, and independent PDF review | Exact reviewed PDF and corresponding author handoff |

## Manuscript dependencies

t07.1 supplies the brief and page budget. t07.2 qualifies and renders exhibits,
while t07.3 verifies primary sources and writes Section 02. t07.4 owns Sections
03, 04 and 07. t07.5 writes Section 05 and captions from accepted results.
t07.6 owns Sections 00, 01 and 06 and assembles both targets. It finalizes the
abstract against the accepted Results. t07.7 independently reviews scientific
claims, data provenance, and the compiled PDF, routes corrections to each
owner, and rechecks the final candidate.

Freeze evidence on 20 November at 18:00 SAST and target author handoff on
21 November at 10:00 SAST. Reserve first the proof statements, the US design and
results table, and the estimation inventory. Include frozen geometry,
dependence, pricing or risk findings only when their individual gates clear.
Carry remaining work in its existing task record and the journal roadmap.

## Write ownership and compute

Give each worker its task record, base revision, repository and study contracts,
its TeX paragraph roles, source and test entry points, upstream contracts or
fixtures, and the exact write boundaries. Theory owns Lean and its blueprint.
Cohorts owns return and roster logic. Estimator, interpretation and inference
owners work in their corresponding study modules or in private pilot outputs.
A separate worker reviews each accepted result.

Use a private outcome sidecar bound to the existing prepared manifest and raw
CRSP digest. Keep the saved prepared panel and representation store read-only.
If scientific encoder inputs change, revalidate through the existing keyed
encoding path. Keep the audited ratio lane available independently. The
historical APT path stays available for its original purpose. The workshop
claim map determines which generated values are cited.

Share inputs and use task-specific scratch directories. The local queue permits
one CPU-heavy empirical or Lean job at a time. Start numerical pilots with one
BLAS thread per process and bound the pilot to 30 minutes, 16 GiB peak RSS and
20 GiB minimum free disk. Record measured costs before expansion. The
coordinator and t07.2 serialize shared CLI, DVC/Semflow and locking changes,
asset rendering and `just sync`.

## Artifact and review handoff

Each producer supplies the relative path, artifact and input digests, producing
revision, command and exit status, formation dates, ordered roster, outcome
mask, units, model and estimand, interval method and limitations. Consumers
verify these identities before joining or citing results. Keep numerical data
in the pipeline or private pilot directory and cite them from a separate task
receipt. Document unavailable evidence and the reason it remains unavailable.

A reviewer reproduces the smallest decisive check and records a disposition
beside the receipt. For the candidate, bind the claims ledger, both layout
builds, exact FinFM PDF hash, anonymity and page inspection, and full checks to
one source snapshot. Keep author decisions and upload with the authors.
