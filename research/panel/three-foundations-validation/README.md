# Measurement construction diagnostics

Declared on 2026-10-18 before inspecting these diagnostic outcomes. This extends
the existing retrospective development experiment; it does not create a new
holdout or select a replacement principal specification.

## Fixed design

Use the three-foundations annual cohorts, five-year histories, 256-row encoder
context, rank-five outside-firm reference exposure targets, 2016–2019 spatial
fitting and 2020–2025 forecasting. Financial source snapshots remain frozen.

Cross native features and decoded exposures with Euclidean and chord distance
for direct inputs, PCA, the valuation-task neural network, TabPFN, TabFM, Kumo,
and LimiX. Use the principal final features. Decode before choosing the distance;
normalization does not alter decoder fitting. The crossed direct-input cells
use the prepared vector; retain the published appended-unit-coordinate distance
separately. Undefined chord distances stop the run without an artificial offset.

Keep the original five-fold assignment and add the fixed salts fold-audit-1
through fold-audit-4. Each assignment balances ticker-hash ranks across five
folds. For the seven principal representations, three TabPFN reset controls,
and an intercept-only predictor, refit scaling, penalty selection and clipping
on the remaining firms. Keep reference-factor coordinates and encoder states
fixed. The null predictor is each held-out group's training-target mean;
verify it against all three Kumo reset encoders in all ten years.

All diagnostics match the joint characteristic reference's effective neighbor
count. Each new network receives its own spatial coefficient fitted using the
original likelihood on 2016–2019. Score fitted diagonal innovation variances
and the existing common-marginal rescaling. Retain the original joint reference
with unit bandwidth for aggregate score comparisons.

## Inference and reconciliation

Use 9,999 paired stationary-bootstrap draws, seed 42, and expected blocks of
21 and 63 scored dates. Report calibration within each metric, normalization
within each coordinate system, calibrated versus native direct and intercept-only
controls, fold-assignment contrasts, and TabPFN learned-minus-reset contrasts.
Partition variation is descriptive construction sensitivity, distinct from the
conditional date-block intervals. Retain every prescribed outcome.

Reconcile overlapping principal cells and Kumo null forecasts to the recorded
daily scores, with absolute tolerance 0.00001 per daily joint score. Verify
cohort identities, date order, annual sums and pooled counts. Numerical outputs
are DVC-cached; this protocol is Git-tracked. Publication tables are generated
with pandas and numerical bindings with Jinja; figures remain native PGF.
