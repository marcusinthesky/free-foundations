# Reduced-study revision and reproduction record

Revision date: 20 October 2026. The source tree was revised from commit
`55aff9664eda629afa4f30af8cf402315965bf81`, including the author's existing
uncommitted changes. This is a working-tree revision, not a claim that the
completed work has been committed.

## Retained argument and empirical scope

The paper develops task information, target recovery and geometry, restricted
readout estimation, and financial use. The empirical application retains the
four frozen pretrained models, direct/PCA/valuation-task controls, exposure
calibration, sample-size comparisons, learned-weight controls, and the decisive
variance, normalization and fold checks. Strong return-based covariance
benchmarks remain in the comparison. Removing exploratory procedures neither
creates a new holdout nor changes the retrospective interpretation.

The Fernández support retains common-four and common-three cohorts, robust MM
betas, spatial lag IV and spatial-error ML, generated-beta inference, self-link
sensitivity, and the published-calibration VaR audit. The paper states the
partial replication's scope and the original table's unresolved VaR discrepancy.

## Execution changes

The DVC graph has nine stages, reduced from 27. Preparation constructs shared
annual samples and target coordinates once. Extraction saves a fixed inventory
of 40 model contexts. Financial estimation consumes these verified states and
produces the principal study and bounded diagnostics together. Publication only
reads saved estimates. The auxiliary replication runs independently of model
inference.

Retired pilot/expanded/ladder execution branches, intermediate readouts,
unsupported models, duplicate experiment grids and their publication machinery
were removed. The initial source tree and retained numerical baseline were
preserved before pruning. Raw financial snapshots and the content-addressed DVC
object cache were retained; no cache garbage collection was performed.

Filing audits now compare keys, missingness and values rather than populated-cell
counts. The canonical study has no subset-run option. Representation contracts
bind ordered contexts, source and dependency hashes, checkpoints, actual device,
runtime and payload checksums. Network reuse preserves separately calibrated
spatial coefficients even when current weights coincide. Matched networks record
requested and achieved concentration, including unattainable targets.

## Regeneration and verification

The four pinned checkpoint integrations passed. All 40 representation contexts
were freshly extracted and verified under the retained implementation. CUDA was
unavailable on this host, so model inference used the recorded CPU fallback.
Financial estimation used one BLAS thread after a host-specific benchmark found
large overhead from the default 12-thread backend. This is an execution setting,
not a change in the estimator or a restriction imposed on other hosts.

The supporting replication was regenerated with 199 valid generated-beta draws
per procedure; one inadmissible draw was rejected before reaching that target.
The eleven shared common-four point estimates reproduce the retained baseline
exactly. The zero-dependence VaR bound remains approximately 16.85 dollars,
incompatible with the published 36.27-dollar cell under the stated calibration.

The complete Python suite passed 129 tests, with two optional checkpoint
integration tests passing separately. Strict type checking, formatting, dependency
checks and dead-code checks passed. The Lean library and all fifteen manuscript
declaration references passed. The revised manuscript has approximately 3,300
main-text words including headings and captions, a 187-word abstract, two main
tables and one figure; mathematical development precedes empirical diagnostics
and the concise replication appendix.

Fresh financial estimation completed in 117.6 seconds on 1,502 dates and
642,024 firm-days, producing 138 principal and 180 diagnostic score columns.
The retained date index and target-reliability estimates match the baseline.
Fresh model outputs are not asserted to equal historical cache entries: the
largest principal daily score difference is 47.52, and the largest full-period
score difference is 351.50, both in random TabPFN controls. The migration record
retains the complete discrepancies rather than suppressing changed estimates.
A separate cache audit reproduces the archived 2020 exposure fits from the
preserved CUDA states and the fresh fits from the current CPU states, using the
same context and financial target. The numerical differences already reside in the extracted features, before
financial estimation. Adapter source identities also changed during pruning,
so this cache comparison does not isolate the effect of device alone.
Historical GPU and fresh CPU inference are not claimed to be numerically
interchangeable. `src/latex/build/device-audit.json`
records the cached-state comparison without rerunning model inference.
The four principal fitted-variance calibration gains remain positive; all four
common-marginal point estimates remain negative with paired intervals spanning
zero. Every main table and scalar claim is generated from the fresh results.

## Machine-readable evidence

`src/latex/build/claims-audit.json` binds reported quantities and publication
selectors to their numerical inputs. `src/latex/build/migration-audit.json`
compares fresh retained results with the pre-pruning baseline, including exact
date alignment and maximum numerical discrepancies. These are separate checks:
artifact agreement does not independently certify the financial source data.

`src/latex/build/restoration-certification.json` records the completed archive
check and its actual outcomes: final source inventory, an independent empty DVC
cache, restored numerical inputs, guarded model-free/offline rendering, asset
comparison and cached manuscript compilation. Consult the record for the exact
source hash and restoration status. It lives outside the publication stage's
outputs so producing the certification cannot alter the source snapshot it
certifies. An absent or failed record must not be interpreted as a successful
restoration.

## Editorial revision: 21 October 2026

The later editorial revision retitles the manuscript *Pretrained Tabular Features
and the Measurement of Financial Proximity* and organizes its main argument into
Introduction, Framework, Empirical design, Results, and Conclusion. It targets
approximately 3,800 main-text words, with a 4,000-word ceiling including headings
and captions, and a 180–220-word abstract. Exact task–target alignment and
calibrated-risk propositions move to the mathematical appendix with their proofs
and declaration tags; the fixed-parameter restrictions on covariance stability
remain explicit.

The revision brings the return-based benchmarks into a separate panel of the
principal comparison, places exposure-prediction R² first, and gives the
fitted-innovation and common-marginal contrasts separate panels with both 21-day
and 63-day bootstrap intervals. These presentation changes use saved numerical
inputs. They do not rerun extraction or financial estimation, alter the analysis
chronology, or create a new holdout.

Editorial verification is complete. TeXcount reports 3,249 main-text prose
words, 39 heading words and 203 caption words: 3,491 in total, below the
4,000-word ceiling. The abstract contains 181 words. The revised source is
identified by SHA-256
`d1593ef4b68ceca22fe53eba99aadd99dd6b2938a24b156c5058ee8c58baf313`.

The publication build and Lean blueprint declaration checks pass. Comparison
with the saved pre-edit working source preserves all three exact proposition
statements, 21 labels and 11 declaration tags. All 49 existing numerical claims
and the recorded numerical input hashes are unchanged. The claims audit binds
the final manuscript and renderer sources. The four targeted publication tests,
renderer lint and formatting checks, and focused repository gates pass.

The rendered 21-page PDF was inspected on main-text pages 1–9 and affected
appendix pages 10–13 and 19–20. Tables and the figure are legible, with complete
paragraphs around the main exhibits. Compilation reports no warnings, overfull
boxes or undefined references. An independent editorial and claim-scope review
found no unresolved correctness findings; it checked the saved evidence rather
than independently re-estimating the study or verifying external literature.

The two added table panels are declared in the publication stage and recorded
in the DVC lock. Only `dvc repro --single-item publication` was run for pipeline
closure; model extraction and financial estimation were not rerun. The 20 October
execution and reproduction results above describe that earlier analysis run.
The existing restoration certification remains tied to its recorded source hash
and does not certify the later editorial source.

## Authorship follow-up: 21 October 2026

Added Chun-Sung Huang after Marcus Gawronsky in the author block, retaining
Marcus's correspondence address. The PDF was rebuilt and its title page
visually checked; the LaTeX lint check passes. The publication-only DVC stage
was refreshed to bind the author change, with no empirical re-estimation.
The manuscript source SHA-256 after this metadata change is
`e9e1adc19e2e11e3299efe7d1c3a918fc5588d37df2de63ef5edffe89691678a`.
The preceding editorial source hash identifies the version before this
authorship update.
