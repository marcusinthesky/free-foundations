---
description: Prioritised post-workshop research plan toward a JFEC/JFE submission.
---

# From the FinFM paper to a finance journal

## Deferred deep-learning experiment

Reserve encoder fine-tuning, training neural baselines from scratch and their learning curves for a later study. The comparison would vary the amount of dated financial training information, match targets, inputs and label access, and evaluate held-out exposure error with dependence-aware intervals. It would test comparative sample efficiency. The FinFM paper studies native frozen states, non-deep readouts and econometric fits.

## Background from the earlier workshop candidate

The earlier workshop candidate made three claims:

1. Predictive content does not fix firm geometry.
2. Neighbour networks can be certified by margins.
3. In one formation, TFM networks add nothing to an out-of-sample five-factor plus
   momentum APT, while industry links do.

A journal paper needs the empirical claim to survive design variation, and it needs the
theory tied to estimands a finance referee will accept. The priorities below are in
order.

## 1. Make the extension a full design (highest priority)

- **Formations.** Repeat the APT ladder for every December formation from 2010 to 2015,
  each with its own five-year train and test windows. Then pool, or meta-analyse, the
  paired score differences. One split is the main weakness of the workshop evidence.
- **As-filed information.** Replace revised CompanyFacts values with as-filed values
  from the original filings. That needs the stalled original-filing recovery: 661 of
  3,357 CIKs were done, with 113,441 filings pending. Budget its download time and SEC
  rate limits, and report which issuers stay unrecovered.
- **Point-in-time industry.** Use historical SIC codes, for example CRSP `siccd`, so the
  industry comparator no longer uses current codes.
- **Training-sample conditioning.** Drop the requirement that every training month be
  observed. Estimate loadings on unbalanced histories with shrinkage, and report how
  sensitive the results are to survival.
- **Exposure target quality.** Sixty monthly observations for six loadings is noisy.
  - Add daily-return loadings within each month, or shrink toward cross-sectional means.
  - Report the target's own reliability (split-half loadings).
  - Readout R² is bounded by that reliability.

## 2. Separate the three changes cleanly

The paper's ladder already separates three steps: CAPM to APT, adding a spatial term,
and how proximity is measured. For the journal, add:

- a non-spatial APT with characteristic-based loadings, in the style of a conditional
  APT, to separate richer exposures from spatial structure;
- spatial-lag and spatial-error versions, alongside a dynamic factor covariance
  benchmark (rolling or DCC);
- economic metrics beyond the Gaussian score:
  - realised minimum-variance volatility with turnover;
  - tracking error of hedged peer portfolios;
  - Diebold–Mariano-type tests with the block bootstrap.

## 3. Theory for the journal version

- **A dimension-free kernel bound.** The exponential-kernel bound carries `√N` from a
  norm conversion. Write `Ŵ/W` entrywise as within `[e^{-2b}, e^{2b}]` and bound the
  in-degree by the degree ratio. That gives
  `‖Ŵ−W‖₂ ≤ √(r(b)(e^{2b}−1)·s_max/s_min)`, which has no `N`. Prove it and formalise
  it in Lean.
- **The symmetrised k-NN case.** Extend the `√(2m/k)` count to symmetrised graphs,
  where a changed edge also renormalises its partner's row. Formalise the resulting
  Frobenius bound.
- **Probabilistic certificates.** Turn the deterministic margin certificate into a
  probability statement under a readout error model. Uniform exposure error with high
  probability gives the share of rows certified with high probability.
- **Wire the resolvent bound.** Connect `ReversibleNetwork.exponential_resolvent_l2_bound`
  into `EndToEnd`, so `M` is derived rather than assumed for symmetric kernels.
- **Prove what the blueprint asserts.** Prove that linear maps preserving the Gram
  matrix are orthogonal; the blueprint currently states it without proof.

## 4. Replication

- **Original design.** Contact the original author, or find a dataset close to hers,
  to reproduce her published tables before reimplementing. Keep "reimplementation" in
  the title until that is done.
- **Cross-section inference.** Diagnose the cross-section bootstrap shrinkage. For the
  size network with an intercept, the point estimate is 0.248 but the draw median is
  0.134. Report basic or BCa intervals as well.
- **The intercept finding.** With a near-uniform kernel, the no-intercept spatial lag
  absorbs the cross-sectional mean. That is a stand-alone methodological finding for a
  spatial-econometrics audience.

## 5. Representation design

- **Prompts.** Encode with other support tasks besides the ME/Assets label, such as
  return volatility or past betas. This tests Proposition 2 directly: if a task closer
  to the exposures is used, calibration should matter less.
- **Fine-tuning.** Compare frozen states with lightly fine-tuned ones, holding the
  information set fixed.
- **Random-weight controls.** Report random-weight and label-null controls; the
  registry already supports `_random` and `_labelnull` variants.

## Positioning

- **JFEC:** a measurement-and-identification paper with formal results and a
  replication.
- **JFE:** needs a stronger economic result, for example where TFM proximity does carry
  information beyond industry and characteristics, or a clean negative result that holds
  across formations, as-filed data and economic loss functions.
- **Lean appendix:** keep the formalisation as an online appendix. The paper must stand
  without it.
