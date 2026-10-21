# Retained pretrained measurement study

This protocol, revised on 20 October 2026, reduces the existing retrospective
study to the comparisons used in the theory-led paper. It preserves the original
inputs, cohorts, target, information timing, estimation rules and retained
procedures. It does not create a new holdout: configurations were examined on
the evaluation years. Superseded experiments remain recoverable from history.

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
