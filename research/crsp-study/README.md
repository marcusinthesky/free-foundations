# Quarterly CRSP–SEC study

This is the active empirical contract. The previous current-survivor study is
[archived](../archive/current-survivor). Its source snapshots, code and results
remain historical evidence; they do not supply findings for this migration.

## Population and returns

The staged CRSP CIZ extract covers January 2001 through December 2025 and stores
`mthret` as decimal total returns. It is copied byte-for-byte into the frozen
source archive; the staged extraction script is saved as text and never run.
No second dividend, split or delisting adjustment is applied. Capitalizations
are converted once from USD thousands to USD.

Each December selects the largest 1,000 securities, breaking capitalization ties
by PERMNO, for the following calendar year. The extract has no December 2000,
so 2001 is warmup, not an invented formation cohort. Selected classes are grouped
by their formation PERMCO. Issuer returns use lagged selected-class capitalization
weights. Missing component returns make the issuer outcome missing; known returns
are not silently renormalized over the surviving classes. Membership remains
through the formation year even if a security disappears from the extract.
Three monthly returns compound once into a quarterly outcome.

The full population ledger starts in 2009. The analytical panel retains each
issuer-quarter with verified, as-of scalar XBRL availability; missing individual
features and missing return cells remain. An unresolved PERMNO–CIK link is a
source-recovery gap, not evidence of missing XBRL. All empirical procedures use
one master issuer-quarter roster, quarterly calendar and observed-return mask.
No method constructs a complete-case company sample. Estimators unable to fit
report unavailability on that common experiment.

Historical support uses up to 20 prior quarters of the current formation-year
selected-class portfolio, including CRSP observations before its top-1,000
membership. This permits the earliest feasible rolling quarter rather than
imposing a 2016 or 2020 start. The history table is separately hashed.

## SEC information and characteristic semantics

Public SEC submissions, CompanyFacts and original filing documents are frozen
separately. Original XML/inline XBRL preserves custom concepts, dimensions,
units, context periods, accession numbers and accepted timestamps. Narrative
text is archived but excluded from model inputs. CompanyFacts alone cannot
certify full filing-level coverage.

Official SEC bulk archives seed CompanyFacts and current/historical submissions;
the archived ownership datasets supply historical issuer identifiers. Individual
filing recovery then fetches primary HTML and instance XML for actual XBRL filings
from 2009 onward, preserving narrative documents and skipping taxonomy linkbases.
Raw snapshots retain response metadata and hashes. New textual responses and
parsed facts use deterministic gzip. Atomic replacement preserves earlier DVC
cache bytes; a free-space reserve stops recovery before exhausting storage.
Public SEC requests share a five-request-per-second limit across workers.

Current SEC ticker matches generate candidates only. Verified links require
SEC accession evidence and explicit validity dates. Ticker reuse and conflicting
CIKs are flagged. Acquisition failures, unresolved linkage and absent native
XBRL have separate statuses. Quarter-start information uses the preceding CRSP
trading close at 16:00 New York time; a filing date without an accepted timestamp
is conservatively available at the next midnight.

The original four characteristics are market capitalization/assets,
market-to-book, dividend yield and debt maturity. Accounting components must
match their intended periods and dimensions. Selected-class capitalization is
not assumed to equal full-issuer capitalization. Public float and par value are
not market capitalization or price. Custom market quantities require explicit
SEC-backed semantics in `sources/sec/metadata/component-semantics.csv`.
Unsupported components remain missing instead of changing characteristic
definitions. Original characteristic histories use ten annual-spaced as-of
slots; broad rungs retain all eligible scalar history in the archived window.

The default component-semantics catalogue is empty. Ordinary CompanyFacts does
not supply verified market prices or full-issuer capitalization. Until those
components are recovered with dated SEC evidence, the original valuation labels
and their encoder contexts remain unavailable. This is an explicit source-to-label
gap, not a completed representation experiment. A complete share-class inventory
could justify summing all matching own-issuer CRSP classes, including classes
outside the formation portfolio; exchange listings alone do not certify that
inventory. No alternative auxiliary target is selected implicitly.

## Matched information and estimation

The three information rungs are `fernandez`, `standard_xbrl` (standard entity-wide
concepts) and `full_xbrl` (all structured scalar facts, custom concepts and
dimensions included). Native NaNs pass to tabular models. Conventional controls
use past-context medians and missingness indicators, recorded separately.
No future-only concept or category enters an earlier schema. Full deterministic
column blocks are encoded separately and their dense states concatenated when
model feature budgets require it. No eligible column is silently subsampled.

The replication uses quarterly MM CAPM betas and median quarterly excess returns.
The full-era fit is descriptive. Forecasts and named FF5-plus-momentum exposure
targets use only prior-quarter information. Model context labels must themselves
be available strictly before the query quarter. Context unavailability is
reported separately from financial estimator failure.

Pairwise Spearman correlations rerank both histories on their intersection.
Covariances also use each pair's common dates. Fewer than two common observations
or a constant pair implies neutral correlation zero and distance square-root two,
with overlap counts and defined flags archived. Raw pairwise matrices may be
indefinite. The original Fernández distance kernel uses raw distances; covariance
and Gram uses explicitly shrink toward identity to minimum eigenvalue 1e-6.
Matched Gram/spatial comparisons share that repaired geometry.

Risk scores use the exact observed subvector of each quarterly covariance, not
complete rows or conditional precision subblocks. Innovation scales are fixed
from prior data for common-marginal comparisons. Paired fixed-forecast bootstrap
inference uses 9,999 draws, expected blocks of 4 quarters and 2/8 sensitivities;
the generated-beta bootstrap uses 999 draws. The fixed seed is 42. French factor
series and the risk-free series are archived monthly and aggregated once; the
quarterly factor construction and long-short compounding convention are explicit
in their manifest.

## Execution and evidence

```sh
# Explicit network operation; successful files are reused on subsequent invocations.
# Acquisition writes to recovery/sources and leaves the active snapshot unchanged.
free-foundations study acquire
# Promote only after complete source recovery; retain the previous snapshot.
free-foundations study freeze
# Record the promoted source bytes in the local DVC cache.
dvc commit -f sources
# Offline re-preparation and all downstream work use frozen bytes.
free-foundations study prepare
free-foundations study encode
free-foundations study run
free-foundations study replicate
free-foundations study report
```

`just python-universe` resumes acquisition, validates and promotes completed
sources, then records the DVC frozen source stage. Incomplete recovery cannot be
promoted. Preparation holds a shared source lock; promotion waits for active
readers and keeps the preceding snapshot under `recovery/snapshots`.
`dvc repro` never reacquires financial sources; the separate checkpoint stage
can acquire the four pinned model weights. An alternative staged CSV must use
a separate source vintage; existing CRSP hashes cannot be overwritten. Source
manifests bind archived bytes; prepared and downstream manifests bind the study,
master panel, ordered roster and return mask. Representation manifests also bind
checkpoint revisions, model runtime, context and state checksums. Publication
reads saved artifacts only and records pending stages explicitly.

The CRSP extract lacks terminal-return flags and full issue-history metadata.
Public SEC evidence cannot guarantee a complete historical CRSP link for every
security. Revised CompanyFacts and current pretrained weights create a
retrospective information limitation. None of these is certified away by a
successful pipeline run, and no old model ranking is transferred into this study.
