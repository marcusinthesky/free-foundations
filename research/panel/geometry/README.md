# Direct financial geometry and descriptive coordinates

Declared on 23 October 2026 as a bounded retrospective extension of the retained
measurement study. This adds no new holdout or configuration-selection claim.
Financial sources, feature states, annual cohorts and return dates remain fixed.

## Fixed comparison

Use encoder context 256, all seven principal representations, the six existing
reset encoders, and the decoded intercept-only predictor. Native features and
decoded rank-five exposures are normalized separately to unit length. Native
direct inputs retain their original appended unit coordinate. These decoded
chord distances differ from the principal study's Euclidean decoded distances.
Individual Spearman-history Gram matrices and their joint arithmetic mean are
the classical controls. Retain signed similarities and unit diagonals.

For each geometry, fit the direct residual covariance
`S [(1 - theta) I + theta C] S`. One coefficient pools 2016–2019; empirical
residual root-mean-square scales are fixed separately within each calibration
year. Search from zero through `1 - 1e-6`, including the endpoints. Forecast
scales use the existing prior residual window. Financial-factor covariance is
unchanged. The spatial comparison uses the identical chord distances, original
exponential characteristic kernels, concentration-matched feature kernels, and
the existing profiled diagonal innovation variances. Its nuisance-scale
estimation therefore differs from the direct model.

Score 2020–2025 on the retained study's daily outcomes. Lead with complete
covariances rescaled to the same prior raw-return marginal standard deviations;
archive full covariance scores as supporting results. Prescribe model contrasts
within geometry, geometry versus the joint characteristic benchmark within model,
decoded versus native, decoded versus intercept-only, and learned versus reset
contrasts. Use the existing paired stationary bootstrap: 9,999 draws, seed 42,
expected blocks of 21 and 63 dates. These conditional contrasts do not expand
the existing model confidence-set family.

## Descriptive coordinates

PCoA diagonalizes `J C J`. Archive the full spectrum and retain at most five
positive axes using tolerance `1e-10 * max(1, largest eigenvalue)`. Record rank
shortfalls and rank-zero geometries. Orient axes by their largest absolute
coordinate, resolving ties by ticker. Report coordinates, latest-characteristic
Spearman associations, five firms at each extreme, and common-firm principal
angles between consecutive years. Annual component identities are not pooled.

Portfolio weights are `A = Z (Z' Z)^-1`, retaining unit characteristic exposure
and zero net investment. Archive gross weights, excess and factor-residual
component returns, component-return covariance and reconstruction shares.
Reconstruction is descriptive projection, not independent evidence of factor
validity or trading performance. The publication's scree display uses the latest
year, 2025, for the seven principal native geometries and joint characteristic
control; all years, controls and adverse outcomes remain in the archive.

## Ownership and provenance

`panel run` owns these results as part of the existing measurement DVC stage.
The publication renderer consumes saved results only. Configurations, numerical
outputs and manifests are DVC-cached; this protocol remains Git-tracked. Native
spatial scores must reconcile to the retained study within `1e-5` per daily joint
score. No feature extraction or financial-source acquisition is part of this
extension.
