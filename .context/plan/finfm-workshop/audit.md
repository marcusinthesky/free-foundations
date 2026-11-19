---
description: Current claim map and limitations with the earlier FinFM audit preserved for provenance.
---

# Research audit (2026-11-19)

## Current in-sample candidate

The two propositions, the US characteristic reimplementation and the dated
TabPFN interpretation are the retained claims. These are the current receipts:

| Claim | Evidence and qualification |
| --- | --- |
| Recoverability and reversible spatial stability | [Theory handoff](tasks/t01-theory/evidence/theory.md) distinguishes compiled components from written arguments and maintained economic premises. |
| Fixed 2015 cohort and analytical selection | [Coverage audit](tasks/t02-data-cohorts/evidence/coverage.md) rebuilds all 39,600 quarterly records. The estimand uses observed complete quarters. Unresolved exits stay unknown. |
| Joint ratio kernel, original-sample fit and bootstrap percentiles | [Baseline audit](tasks/t03-spatial-inference/evidence/baseline.md) reproduces the point fit from saved inputs. [Refit audit](tasks/t06-uncertainty-robustness/evidence/refit.md) documents draw attrition, interval scope and unresolved matched 10-NN shrinkage. |
| Dated geometry | [PCoA pilot](tasks/t04-pcoa-interpretation/evidence/interpretation.md) verifies dated states, roster, distance reconstruction and descriptive ratio alignment. The ratios are input measurements. |
| PDF and reported values | [Exhibit inventory](tasks/t07-submission-bundle/tasks/b-evidence-exhibits/evidence/exhibits.md) identifies the generated bindings and the evidence behind the interpretation. |

Use the updated [cover note](cover-note.md) for the author decision. Matched
calibration, residual-covariance contrasts, pricing restrictions, model-implied
portfolio risk, and multi-date uncertainty remain open. The spatial-error
pricing fixture is synthetic and stays outside the manuscript results.

## Earlier forecasting candidate

The following audit records an earlier candidate, its out-of-sample APT run
and the commands and source paths in use at that time.

## Verdict

The paper can be submitted as a theory-led workshop paper with a clearly labelled
application.

- **Theory:** checked by hand, and the core statements compile in Lean.
- **Empirics:** real but narrow: one roster and one train/test split. They are
  reported as found, including the negative out-of-sample result.
- **Main risk:** reviewers asking for more formations and as-filed data.

The paper states both risks as limitations.

## Strongest contribution

The paper makes one distinction and gives a usable test for it:

- predictive equivalence leaves nearest neighbours open;
- a neighbour-margin certificate says when an estimated network is the economic one.

The application then shows the two things the theory warns about:

- calibration improves agreement with estimated exposures, but not beyond the TFMs'
  own direct inputs;
- certificates fail by more than two orders of magnitude, and TFM spatial terms add
  nothing out of sample, while industry links do.

## Claim-to-evidence map

| Paper claim | Evidence | Kind |
| --- | --- | --- |
| Prop. 1(a): reparametrisation preserves predictions | `Geometry.optimal_equiv`, `Neighbours.stretch_predictions` | Lean |
| Prop. 1(b): some linear map reverses any non-collinear pair | Written proof, appendix A | Hand-checked |
| Prop. 1(c): the condition-number bound | `Neighbours.neighbourSet_linear`; sharpness by explicit map (appendix A) | Lean and hand |
| Table 1, raw flip | `Neighbours.anisotropic_flip`; test `test_anisotropic_map_flips_a_nearest_neighbour_but_not_predictions` | Lean and test |
| Table 1, unit-norm and standardisation flips | Tests `test_unit_normalisation_*`, `test_standardisation_*`; exact fractions in appendix A.2 | Test and exact arithmetic |
| Prop. 2: alignment | `Alignment.optimal_imp_sufficient_iff` | Lean |
| Thm. 3(a): margin certificate, uniqueness and sharpness | `Neighbours.neighbourSet_stable`, `_unique`, `_margin_sharp`; Hypothesis property test | Lean and test |
| Thm. 3(b): exposure and estimated-margin forms | `Neighbours.neighbourSet_of_exposures`, `_of_estimated_margin`; test `test_certified_rows_*` | Lean and test |
| Thm. 3(c) and the `√(2m/k)` count | Written proof, appendix A | Hand-checked; not in Lean |
| Covariance and score bounds (appendix A.1) | `Stability.matrix_covariance_target_sub_le`, `ScoreStability.loss_gap_le_of_norm_sub` | Lean, conditional on assumed M, V |
| Replication numbers (Table 2, Section 4) | `data/research/crsp-sec/replication` via the `workshop` stage | Saved output |
| APT numbers (Tables 3–5, 7, Section 5) | `data/research/crsp-sec/apt` via the `workshop` stage | Saved output |
| In-sample appendix (Table 6) | `comovement` and `alignment` outputs | Saved output |
| TFMs pretrained on synthetic data only | Model cards and the NVIDIA blog post; see the [gate](tasks/t06-uncertainty-robustness/evidence/historical-gate.md) | Documentation |

Every number in the PDF is a macro or table from
`src/latex/finfm/generated/`, which the `workshop` DVC stage writes from saved
outputs. None is typed by hand.

## Checks run, with their results

- **Lean.**
  - `just lean::check` exited 0.
    - Build passed, and API coverage is 312 of 312 tagged declarations.
    - The proof-integrity report is complete: 44 sources, 892 declaration records,
      no issues.
    - The axiom audit passed with 907 declarations and only `propext`,
      `Classical.choice` and `Quot.sound`.
    - The blueprint and manuscript `checkdecls`, `lake lint` and the proof-integrity
      self-tests all passed.
  - The report records a dirty tree at `4473b6e`, because the Lean changes were not yet
    committed.
- **Python.**
  - `tests/study/test_apt.py`: 11 tests pass.
  - Lint, strict types, layout, Tach and Vulture pass.
  - The full `just check` result is recorded in the hand-off message.
- **DVC.** `apt` and `workshop` were reproduced through DVC, and `dvc.lock` records
  them.
- **Manuscript.**
  - `just latex::finfm` (pdfLaTeX and BibTeX) gives no undefined citations or
    references and no overfull boxes.
  - The PDF has 7 pages in total, about 4.5 of them technical, and is US Letter.
  - Pages were rendered and inspected.
- **Anonymity.**
  - The extracted PDF text, the sources and the `.bbl` contain no names, emails, the
    repository name, GitHub, statadic or MathEconLib.
  - The PDF metadata holds only the pdfTeX producer and banner.

## Disclosed deviations

- **`params.yaml` timing.** In the base study, `params.yaml` and `design.md` entered Git
  together with the results. There is no timestamped pre-registration for the in-sample
  layers.
- **The `apt` stage.** It was committed (`173ab93`) before its first run.
  - A dry run on scratch output had shown the CompanyFacts direct readout exploding, so
    clipping was added before that commit.
  - The first recorded run exposed a centring bug in the clipped readout, which changed
    the XBRL readouts. It was diagnosed on training-window recovery only and fixed in
    `4473b6e` before the run that produced the reported numbers.
  - The out-of-sample test scores of the buggy run were seen. They affected only the
    calibrated XBRL networks, and no design choice was changed in response to them.

## Results needing repair or independent verification

- **Bootstrap shrinkage.** The replication bootstrap draws are shrunk relative to their
  point estimates in the 10-NN cross-sections. The matched table is not quoted in the
  paper; see the [gate](tasks/t06-uncertainty-robustness/evidence/historical-gate.md).
- **Mantel p-values.** They sit at the permutation floor (in-sample appendix only).
- **Theorem 3(c) count and Proposition 1(b).** These are hand-checked, not formalised.
- **Exponential-kernel bound.** The `√N` factor is not sharp. A dimension-free version
  is in the roadmap.

## Historical results not to use

- The withdrawn current-survivor study and its numbers (Git history only).
- The removed forecast, decoder, Gram and PCoA analyses.
- The working manuscript's appendix still describes ridge readouts, forecasts and daily
  loadings (`main.tex` around lines 344, 476–484, 555 and 945–948). Those passages are
  stale and are not used in the submission.
