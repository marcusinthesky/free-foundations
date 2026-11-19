---
description: FinFM task dependencies, proposed module boundaries and evidence handoffs.
---

# FinFM work allocation

The numbers follow the final research priorities in the 19 November Paper Overview.
Agents can develop against small fixtures before upstream estimates are ready.
Follow the task link for source files, acceptance criteria and the evidence to return.

| Task | Can start now | Inputs needed for final results |
| --- | --- | --- |
| [01 Theory](tasks/t01-theory/README.md) | Verify proofs and specify premises | Existing Lean declarations and empirical graph definition |
| [02 Cohorts](tasks/t02-data-cohorts/README.md) | Audit formation membership, rank changes and exits | Frozen CRSP–SEC data and verified panel manifest |
| [03 Spatial inference](tasks/t03-spatial-inference/README.md) | Specify estimands and test fits | 02 panel, matching representation states and 01 assumptions |
| [04 Interpretation](tasks/t04-pcoa-interpretation/README.md) | Test decompositions and attribution on known distances | 02 panel and states for maps and portfolios, 03 loadings for exposure alignment |
| [05 Pricing](tasks/t05-sapt-restrictions/README.md) | Test a synthetic economy with known restrictions | 01 assumptions and 03 fits for primary pricing tests, 04 returns for the optional mimicking-factor contrast |
| [06 Uncertainty](tasks/t06-uncertainty-robustness/README.md) | Design resampling fixtures and the estimation inventory | 02 panel and actual estimation units, then each of 03–05 for its own contrast |
| [07 Manuscript and submission](tasks/t07-submission-bundle/README.md) | Plan the argument, register asset interfaces and verify sources | 01 proofs, accepted 02–06 outputs, complete section drafts and independent review of the candidate |

## Manuscript dependencies

07a supplies the section brief, page budget and evidence required for each
workshop claim. 07b integrates stage and exhibit interfaces while 07c checks
primary sources. With the brief in hand, 07c writes related work, 07d owns
methods, data and appendices, and 07e writes results as exhibits arrive.
07f owns the introduction, abstract, conclusion and assembly. It finalizes
the abstract against 07e's supported claims. 07g reviews the compiled candidate
and routes corrections back to the responsible writer. The parent packages
the reviewed revision after the corrections have been checked.

## Proposed module changes and write ownership

Each research agent owns the modules and matching tests named in its task, plus
its task-local evidence. Start with these [study modules](../../../src/python/apps/free_foundations/src/free_foundations/study)
and the [current study contract](../../../data/research/crsp-sec/README.md).

1. **Cohort access.** Today `alignment.py` imports `cohort_outcomes` from
   `replication.py`. 02 places the shared accessor in `rosters.py` beside
   `StudyInputs`, and exposes the verified formation-month ledger via
   `run.inputs`. 03 updates the replication caller. 07b switches the alignment
   import during integration. Keep the old import working through that migration.
2. **Financial fits.** Today `apt.run` estimates exposures, builds graphs, fits
   covariance and scores the historical split. 03 extracts the reusable factor
   and spatial fitting operations into `study/spatial_fit.py`. Check numerical
   parity on identical inputs before changing cohorts or estimands. Keep the
   existing `research apt` command and saved schema readable. Give 04 and 05
   saved, dated fit inputs for their own `study/pcoa.py` and `study/pricing.py`.
3. **Uncertainty.** 06 owns reusable block orders and intervals in
   `study/inference.py` and sensitivity analysis in `study/robustness.py`. Each estimator
   owner supplies per-period contributions and callable refits where resampling
   requires re-estimation. Changes to a fit go to that owner.
4. **Pipeline integration.** 07b edits `stages/research.py`,
   `study/spec.py`, shared CLI tests, `params.yaml`, DVC, Tach, Semflow and locks.
   Each producer supplies its proposed options, parameter dependencies and
   output directory. Register producers as their interfaces arrive. PCoA,
   pricing and robustness should have individually reproducible research
   outputs. Declare dependencies on the particular saved inputs each consumes.
5. **Rendering.** 07b owns `study/publication.py`, `study/publication_apt.py`
   and their tests. 07c owns CSL and the section writers own their captions.
   Today the orchestrator imports
   the APT renderer inside `render`, and the latter imports formatting helpers
   from the orchestrator. Move the shared helpers into `publication_format.py`
   as new exhibit writers join. Preserve macro keys and fragment names, and
   check panel, roster and mask identities before emitting any exhibits.

## Artifact handoffs

Each producer first records the planned relative path, key columns, units, timing
and a small worked example in its task's evidence note. Consumers can use that
contract while full data are pending. Discuss a changed key or estimand with
the affected consumers before rerunning.

02 produces the ledger and manifest under `data/processed/crsp-sec/panel/`.
03–06 place proposed research bundles under `data/research/crsp-sec/`, each
in its own output directory. Keep numerical data in the pipeline. In the task
note record the producing revision, command, artifact path and digest, formation
dates, issuer order and outcome mask, model identity, checks and limitations.
Consumers verify these identities before joining results. A missing or
unidentified estimate carries its reason through publication.

Use isolated worktrees or private output directories for concurrent numerical
runs. 07b applies stage and lock updates and coordinates `just sync`. 07f
builds the candidate and 07 runs the final repository checks.
