# Representative pretrained measurement experiment

Declared on 2026-10-18 before examining Kumo or LimiX financial scores. This is
an extension of the retrospective development study, using its existing data
and evaluation years. The earlier `three-support` results remain separate.

## Fixed comparison

The core models are TabPFN 3.5, Google TabFM 1.1, Kumo-Tabular Large, and LimiX-2.
Primary features are the inputs to their regression prediction heads. TabFM and
Kumo also expose pre-prediction row features as a declared supplementary contrast.
Kumo uses its Large regression checkpoint, not the smaller variant. Each model
uses one member, frozen weights, the same prepared input table and support rows,
and the existing native chord distance and cross-fitted exposure calibration.
Adapters use upstream architecture code; no model is trained on evaluation returns.

The cohort, five-year histories of three characteristics, rank-five outside-firm
reference exposure target, 2016–2019 spatial fitting and 2020–2025 scoring follow
`three-support`. All three kernels and variance specifications remain available.
Direct, principal-component, supervised-network, historical-exposure and covariance
controls use the same comparison rules. Auxiliary three-year representations from
the earlier study are not recomputed; the five-year cohort is unchanged.

Encoder supports contain 32, 64, 128 or 256 nested observations. Independently,
financial calibration uses 32, 64, 128 or 256 nested training firms within each
of the existing five folds, holding encoder support at 256 and test firms fixed.
Calibration-size comparisons cover the four primary representations and the three
input/supervised controls. All preprocessing and clipping for that exercise are
fitted on the selected training firms only.

Weight controls use seeds 42, 43 and 44. TabPFN retains the earlier reinitialization
protocol (including the declared treatment of residual tensors and architectural
frequencies); Kumo uses the upstream architecture's fresh initialization. These
controls measure performance relative to their specified initialization procedures.
Seed-specific paired date-block intervals and variation across seeds are reported
separately. Native and calibrated performance, including unfavorable results, are
retained for every declared primary model.

## Execution and publication

Run models sequentially on CPU, retaining checkpoint hashes and cached row states.
Kumo and LimiX use query batches of 128 with the entire support table unchanged.
Verify row order, batch consistency, fixed weights, and prediction-head extraction
before the financial run. Missing mandatory model results prevent publication of
a completed four-model comparison.

The manuscript uses generated tables and native PGF figures. Model and numerical
selection follow this protocol, not the highest observed evaluation score.
