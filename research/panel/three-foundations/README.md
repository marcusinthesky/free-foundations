# Retained pretrained measurement study

This protocol, revised on 23 October 2026, retains the comparisons used in the
theory-led paper and adds observed-data recovery from the frozen public
disclosures. The target, information cutoffs, estimation rules and retained
procedures remain fixed; recovered observations can enlarge annual cohorts.
This does not create a new holdout: configurations were examined on the
evaluation years. Superseded experiments remain recoverable from history.

## Fixed comparison

TabPFN 3.5, Google TabFM 1.1, Kumo-Tabular Large and LimiX-2 supply frozen
prediction-head features. Direct inputs, PCA and a neural network trained on the
same auxiliary valuation task provide conventional controls. The network is not
trained directly on exposure labels. Models receive identical prepared
five-year histories of three characteristics and the same valuation examples.
All models use one member and their independently verified pinned checkpoints.

Annual cohorts retain the original completeness and nonconstant-history checks
at both three and five years. Outside-firm reference factors define a common
rank-five historical exposure proxy. Five-fold ridge calibration holds out firms;
scaling, penalty selection and clipping use the training firms only. Decoder
means cover 2016–2025. Spatial coefficients use 2016–2019; forecasts are scored
on 2020–2025 after excluding the first return of each year.

## Observed-data recovery

Recover all 17 year-end characteristic snapshots from 2009 through 2025, using
the public SEC and market snapshots. The 2025 source snapshot is retained for
coverage; the main 2025 return comparison uses information through 2024.
Preserve a complete annual-disclosure snapshot for
the three main characteristics. If it is incomplete, consider annual and
quarterly instant disclosures and replace it only with one complete snapshot.
Select the ratios together rather than filling individual ratios from different
periods. Broader model-input disclosures retain their annual-only convention.
Record the selected source policy, reporting period, separate outstanding-share
date, filing dates, accessions, tags and component values.

For an annual snapshot whose first three ratios are complete but whose debt
maturity is missing, also consider quarterly instant facts at exactly the
same balance-sheet date. Complete the debt ratio only when those observed,
period-aligned components suffice under the same lease-inclusive definition.
Keep the first three ratios and every existing date unchanged, and record
the quarterly debt components and their filing dates separately. This adds
observed debt information without replacing the annual snapshot or mixing
balance-sheet periods.

Every selected fact must have been filed by the snapshot year-end, and its
reporting period must be no more than 550 days old. Keep the existing market
date and split-basis checks. Accounting-tag fallbacks must preserve the meaning
and reporting period of the required quantity. Do not replace outstanding
shares with weighted-average earnings-per-share denominators, consolidated
equity with parent equity without the required reconciliation, or missing debt
and leases with assumed zeros. Unresolved share classes and entity changes
remain excluded rather than joined by ticker alone.

One unresolved acquisition case is BlackRock: its
[predecessor filing](https://www.sec.gov/Archives/edgar/data/1364742/000119312524229654/d856279d8k.htm)
and [successor filing](https://www.sec.gov/Archives/edgar/data/2012383/000119312524229601/d856271d8k12b.htm)
establish a one-for-one share conversion and uninterrupted BLK trading on
1 October 2024. The predecessor's CompanyFacts are absent from the frozen
cache. Direct SEC and company-archive downloads returned HTTP 403 during the
23 October 2026 recovery; no predecessor financial observations were added.
Recovering them requires acquiring and auditing those original source records.

This recovery changes the disclosure-selection policy; it is an adaptation to
the US source data. It introduces no numerical imputation into the strict
characteristic controls and does not relax their complete, nonconstant-history
requirements. Retain the existing three-year return window and minimum of 500
observed prior daily returns. Missing prelisting returns are never synthesized.
Report the shared annual cohorts and their intersection across years; do not
force an identical cohort across all years or across the separate strict
four-characteristic Fernández replication.

The measurement window remains 2016–2025, with 2016–2019 calibration and
2020–2025 financial evaluation. Five-year query histories are not the only
warmup requirement: the two earlier support years also need historical
features. The 2016 support rows use histories beginning in 2009. Extending the
same encoder design to earlier measurement years would introduce unavailable
pre-2009 support lags. No earlier accounting acquisition, revised calibration
window, or relaxed missing-history experiment is part of this recovery.

## Distance and covariance comparisons

Principal native distances use chord distance; the original direct benchmark
appends a unit coordinate. Calibrated distances use Euclidean separation between
predicted exposures. Match the joint characteristic reference's effective
neighbor count, with zero self-links, and record unattainable matching targets.
Retain fitted diagonal innovation variances and common-marginal rescaling.
The joint characteristic reference uses its original unit-bandwidth exponential
kernel. Raw sample covariance, factor-plus-diagonal and factor-plus-sample
residual covariance remain financial benchmarks.

## Bounded interpretation checks

Encoder contexts contain 32, 64, 128 or 256 nested examples. Separately, financial
calibration uses 32, 64, 128 or 256 nested training firms per fold with encoder
context fixed at 256. These curves use matched networks and fitted innovation
variances; they are not crossed with every kernel or control configuration.

Reset-weight controls use seeds 42, 43 and 44 for TabPFN and Kumo at context 256
only. Preserve native and calibrated forecasts, with both variance treatments.
Kumo's constant features are checked against the cross-fitted intercept-only
predictor rather than interpreted as learned financial geometry. The companion
[construction protocol](../three-foundations-validation/README.md) crosses
normalization and coordinates and retains five fixed fold assignments.
Target reliability is audited at ranks three, five and eight; forecasts use
rank five. All outcomes of the retained comparisons, including adverse ones,
remain in the numerical archive.

## Execution and provenance

`panel prepare` audits filing values and saves annual financial inputs. `panel
encode` extracts verified states once. `panel run` estimates financial procedures
from those saved states and never invokes a model. `panel report` validates and
renders saved results. DVC owns each stage's outputs separately.

The runtime uses an explicit `FF_DEVICE` override when supplied, otherwise CUDA
when available and CPU as fallback. Record the actual device, threads, installed
versions, lockfile, extraction code, checkpoints, ordered contexts and payload
checksums. A changed extraction identity requires fresh states; old arrays are
not relabeled. Adapters preserve query order and frozen weights, and Kumo/LimiX
use query batches of 128 without changing support rows.

Paired stationary-bootstrap intervals use 9,999 draws, seed 42, and expected
blocks of 21 and 63 dates. Confidence sets compare principal procedures and
financial benchmarks, excluding sample-size and reset grids. All inference is
conditional on fitted procedures and omits configuration-search uncertainty.
Missing retained models or score years prevent publication. Tables, scalar
claims and native PGF figures are generated from recorded artifacts.
