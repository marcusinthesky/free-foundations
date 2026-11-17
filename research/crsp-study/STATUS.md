# Migration checkpoint, 30 October 2026

The quarterly migration is implemented, but the new empirical study is not yet
complete. Old numerical findings remain only in the Git history rather than
carried forward.

## Frozen source checkpoint

The current `sources` DVC stage records the staged CRSP bytes, official SEC bulk
metadata, historical identifier evidence and French factor archives. Its detailed
receipts and byte hashes live in `sources/manifest.json`.

| Item | Observed at this checkpoint |
| --- | ---: |
| CRSP monthly security observations | 477,653 |
| Distinct PERMNOs | 2,781 |
| Raw PERMCOs | 2,716 |
| Monthly dates | 300 |
| Missing monthly returns | 59 |
| Historical SEC ownership ZIPs, 2006–2025 | 80 |
| Matching historical issuer attestations | 2,107,218 |
| Bounded historical identifier intervals | 3,314 |
| Candidate SEC CIKs | 3,357 |
| CIKs present in the official CompanyFacts snapshot | 2,881 |
| Candidate submission/current-history JSON documents | 5,696 |
| Archived native facts before as-of filtering | 48,725,217 |
| Filing ledger entries | 232,314 |
| Original XBRL filings pending recovery | 113,441 |

These are source inventory counts, not estimation sample sizes or findings.
Ticker candidates and bulk-snapshot absence do not certify historical issuer
identity or genuine absence of XBRL. A raw CRSP PERMCO is not automatically a
verified historical SEC issuer.

## Work in progress

The latest runtime check found no completed master-panel manifest or downstream
representation, measurement, replication or publication artifacts. The overnight
preparation stopped after 2,096 of 2,168 issuer batches: an Oracle source fact
spanning 1900–2199 overflowed nanosecond duration arithmetic. The repair preserves
the raw fact and existing information cutoffs; the full Oracle batch now passes.
Offline preparation has been restarted. No new empirical estimates or model
rankings are available yet.

Preparation reads only the frozen source checkpoint. Original-filing recovery
runs separately under `recovery/sources`, preserving the active inputs. The full
rung stays unavailable while that recovery is incomplete. Successful downloads
are reusable; failed requests and disk-space stops remain explicit.

The current recovery and preparation workers write separate progress logs under
`recovery/logs/recover.log` and `recovery/logs/prepare.log`, with PID files beside
them. Recovery promotes sources and records the DVC source stage only if all
completion and byte-integrity checks pass. Promotion waits for preparation's
source read lock and preserves the previous snapshot. `just python-universe`
resumes interrupted recovery using the same safeguards.

The observed source-to-label gap is substantive: ordinary CompanyFacts supplies
neither verified closing prices nor full-issuer market capitalization. The
original characteristic definitions and valuation task are preserved; unavailable
labels do not become a different auxiliary task. A date-bounded, complete SEC
share-class inventory could support summing all matching CRSP issue caps. Public
float, exchange-list counts, par values and selected-class caps are insufficient
by themselves.

The current empirical publication gate requires finite core and forecasting
results, completed model stages, completed original-filing recovery and resolved
historical source linkage. Decoder quality or a successfully executed stage alone
cannot establish completed findings. The legacy hypothetical VaR simulation is
not relabeled as a matched quarterly backtest.

## Verification completed

Focused fixtures cover CRSP formation and compounding, missing classes/outcomes,
as-of SEC cutoffs, historical ticker conflicts, scalar types and native NaNs,
streamed contexts, full-column blocks, pairwise moments and repairs, exact
observed-subvector Gaussian scoring, matched Gram/spatial comparisons, bootstrap
coupling, artifact provenance and publication gates. The complete Python suite,
strict types, import boundaries and lint are checked as part of this migration.
The latest Python run reports 449 passed and two optional integration tests skipped.
All four pinned pretrained models also produced finite local embeddings in a
native-NA smoke test using existing weights. This is an adapter check, not an
empirical result.

The revised manuscript compiles, and its Lean declaration list is identical to
the archived manuscript. The Lean 4.35 build and both blueprint/manuscript compiled
declaration checks pass. No theorem or proof source was changed in this migration.
