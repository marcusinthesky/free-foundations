---
description: Audit of saved generated-beta refits and their inferential limits.
---

# Primary-formation refit audit

The saved 2015 replication has 999 stationary-quarter draws, with expected
block length 2.218 quarters. Each draw resamples the common quarter calendar,
refits MM betas and median excess returns, then fits spatial models on the
formation graph. For missing draw-specific betas or medians, it drops issuers,
restricts the graph and renormalizes its rows. Dropped counts range from 0 to
98, with median 0 and 97.5th percentile 68.3. The interval is conditional on
the selected original graph and cohort, but draw attrition can change the
effective roster and graph; it does not incorporate graph estimation.

For joint `exp(-d)` no-intercept lag ML, the saved point is 0.859996 and draw
median 0.857707, with 95% percentile interval [0.224658, 0.964480] over 999
finite draws. The statadic model-based Wald interval [0.727213, 0.992778]
conditions on the generated regressors and graph. These are different
uncertainty procedures and neither establishes coverage by itself. The saved
intercept fit is invalid/boundary, so the fast refit's numerical intercept
draws must not be treated as an interval for a valid fitted intercept model.

Shrinkage is visible for matched 10-NN lag ML with intercept: size has point
0.247817 and draw median 0.134242, percentile interval [−0.030845, 0.252200];
joint ratios have point −0.165355 and median −0.068757, percentile interval
[−0.227105, 0.136389]. These observations do not identify a cause. Do not
present the matched 10-NN percentile intervals as validated until original
sample parity and attrition, refitting and boundary effects are investigated.
Basic or BCa intervals require their own validation and do not automatically
resolve the anomaly.

## Parity scope

The code computes a replicate-zero refit and invokes `_parity` before creating
draws, comparing available statadic spatial and premium estimates at relative
tolerance `1e-4 * max(1, abs(expected))`; unavailable fits are skipped. The
saved artifact is consistent with that guard completing under the recorded
code, but does not itself retain the original fast refit values. A bounded
offline reconstruction of the joint `exp(-d)` graph and no-intercept lag ML
profile on saved original betas and medians gives 0.8599956361 versus saved
0.8599956767; the premium differs by 6.34 × 10⁻¹⁰. This independently checks
that one graph and profile fit, but does not rerun MM betas or check all
estimators and graphs. It cannot diagnose 10-NN shrinkage, prove coverage, or
assess the consequences of draw-specific roster changes.
