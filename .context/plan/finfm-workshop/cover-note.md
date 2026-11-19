---
description: Cover note for Marcus and Chun-Sung on the proposed FinFM submission and the decisions it needs.
---

# FinFM submission: cover note

**For:** Marcus and Chun-Sung.
**Deadline:** Friday 20 November 2026, 23:59 AoE, which is Saturday 21 November,
13:59 SAST, on OpenReview.
**Status:** nothing has been submitted, posted or emailed. The work is on the local
branch `paper-finfm-aaai27` and has not been pushed.

## The paper

*When Are Foundation-Model Neighbours Economic? Predictive Equivalence, Neighbour
Margins and a Spatial APT*: an anonymous long paper, at most 7 technical pages, on the
AAAI-27 template.

The argument has three parts.

1. **Theory.** Proximity is measured in common-shock exposure units.
   - Proposition 1: a prediction-preserving linear map can reverse nearest neighbours,
     even after unit normalisation or standardisation.
   - Proposition 2: a task identifies an economic target if and only if equal task
     statistics imply equal targets.
   - Theorem 3, new: a sharp neighbour-margin certificate says when an estimated k-NN
     network equals the economic one.

   Theorem 3, the alignment result and the covariance and score stability bounds are
   machine-checked in Lean. One unit-norm and one standardisation example are checked
   by tests, not Lean.
2. **Replication.** This reimplements Fernández's spatial CAPM on CRSP and SEC data,
   rather than replicating it exactly: her data are not available, and the sample and
   sources differ. A table in the paper lists what is kept and what changed. Without an
   intercept, ρ is about 0.86. That reflects a near-uniform kernel absorbing the
   cross-sectional mean. With an intercept, every spatial fit on her kernel reaches the
   boundary of the parameter space.
3. **Extension.** An out-of-sample spatial APT.
   - **Data and models:** loadings on five factors plus momentum, trained on
     2016–2020 and tested on 2021–2025.
   - **Networks compared:** characteristic, raw-TFM and exposure-calibrated-TFM
     networks, plus industry and null controls. All four TFMs are used, on both
     information rungs.
   - **Evaluation:** exposure recovery and out-of-sample covariance are evaluated
     separately.

   The results are in the audit and the paper.

The extension design was committed (`173ab93`) before its first DVC run. One bug fix
followed: re-centring clipped ridge features. It was diagnosed on training-window
recovery only and committed before the recorded run (`4473b6e`). The paper and the
audit disclose this.

## Decisions that need you

1. **Submit or not, and the author list.** OpenReview needs both authors' profiles. A
   new profile without an institutional email can take days to be moderated, so check
   now.
2. **In-person presentation.** FinFM requires a co-author to present in person in
   Montréal on 22 or 23 February 2027. Virtual presentation is not allowed. Who would
   go?
3. **Claims you are comfortable making.** The empirical section is one roster and one
   split, using revised (not as-filed) CompanyFacts and current SIC codes. It is
   labelled that way. Is that acceptable for a workshop paper, or should the
   application be framed as preliminary?
4. **Self-identifying tools.**
   - The statistics library (statadic) is cited anonymously.
   - MathEconLib is not cited in the anonymous version.
   - No repository link is given.
   - Supplementary material (anonymised code or Lean) is optional; reviewers need not
     read it. Do you want to prepare an anonymised supplement?
5. **arXiv.** Marcus wanted Chun-Sung to see the paper before any arXiv posting. The
   workshop is non-archival, so arXiv timing is your call.
6. **Licences.** TabPFN 3.5 and LimiX-2 weights are under non-commercial research
   licences. Academic use is fine, but please confirm you are content to name them.

## Preparing the revised submission

The findings and checks above describe the earlier candidate. Build the revised
paper with `just latex::paper finfm` and read
`src/latex/projects/free-foundations/build/finfm/finfm.pdf`. Use the plain-text
abstract matched to that revision. The [submission task](tasks/t07-submission-bundle/README.md)
owns the final checks, bundle contents and author decisions.
