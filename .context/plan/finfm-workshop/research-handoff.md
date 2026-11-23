---
description: Reviewed research evidence and open dependencies from the FinFM swarm.
---

# FinFM research handoff

The five GPT-6.1 Terra workers used medium reasoning effort and the pinned
snapshot `b6fc9880fe3a9300d5fbe21eaed49b84eaf9fcda`. The cohort and
state manifests matched their recorded hashes. Results below use saved frozen
states and in-sample financial estimates.

| Task | Accepted evidence or remaining dependency |
| --- | --- |
| t01.1–t01.3 | The Lean source and frozen API contracts match the revision used for the theory receipt. The neighbour and covariance claims are conditional on the stated graph and measurement premises. [Theory receipt](tasks/t01-theory/evidence/theory.md) |
| t02.1–t02.3 | The coordinator replayed December 2015 membership and matched all 39,600 fixed-formation quarter rows. Of these, 32,547 are observed before the analytical filter. Unknown terminal outcomes remain unidentified. [Coverage and replay](tasks/t02-data-cohorts/evidence/coverage.md) |
| t03.1–t03.2 | The coordinator independently reproduced the available mean and median point fits with the profile estimator and verified the common 40-quarter, 878-issuer matrix. Lag without an intercept moves from 0.860 to 0.899. Median lag with an intercept is unavailable. The mean intercept fit is imprecise and becomes unavailable in the pooled clipping sensitivity. Paired intervals remain pending. [Point fits and influence sensitivity](tasks/t03-spatial-inference/evidence/mean_median.md) |
| t03.3–t03.4 | The full and contrast likelihood fixtures pass. The coordinator reconstructed all 60 ordered quarterly masks and reconciled counts to the saved ledger. Acceptance of the empirical contrast, residual covariance and any risk estimate requires the graph and estimator replay. The portfolio quantity also requires dated holdings and exit accounting. [Panel receipt and replay command](tasks/t03-spatial-inference/evidence/panel_jacobian.md) |
| t04.1–t04.2 | The PCoA replay passed. The coordinator independently reproduced the CAPM beta rank regression and the common-roster principal angles using direct Gram eigendecomposition. The top-three beta rank R² is 0.00248 on 878 issuers. Across the 850 common issuers in January 2016 and January 2017 the three angles are 18.77°, 25.00° and 38.61°. These are descriptive. A structured null and uncertainty are required for inferential claims. [Beta alignment](tasks/t04-pcoa-interpretation/evidence/beta-alignment-receipt.md) · [Two-date stability](tasks/t04-pcoa-interpretation/evidence/stability-receipt.md) |
| t04.3 | Dated normalized holdings, verified return accounting and spanning evidence are required for the mimicking portfolio. [Interpretation task](tasks/t04-pcoa-interpretation/tasks/t04-3-mimicking-portfolios/README.md) |
| t05.1–t05.2 | The restriction fixture passed. The coordinator independently reproduced the descriptive quarterly mean-on-beta slope of 2.059% and pricing-error RMS of 3.679% on 878 issuers. A full cross-sectional Wald test requires a valid procedure for singular restriction covariance, generated betas and time dependence. [Pricing receipt](tasks/t05-sapt-restrictions/evidence/pricing-pilot.md) |
| t05.3 | The additional-factor pricing comparison requires verified t04.3 factor returns and spanning, and t05.2 inference. [Pricing task](tasks/t05-sapt-restrictions/tasks/t05-3-mimicking-pricing/README.md) |
| t06.1–t06.3 | The shared draw-schedule fixture passed. The historical 10-NN shrinkage remains unresolved. The financial paired-refit runner and its interval assumptions are recorded. Panel uncertainty depends on verified per-quarter inputs. [Uncertainty receipt and commands](tasks/t06-uncertainty-robustness/evidence/swarm-t06/receipt.md) |

The host fell from 23 GiB free to roughly 4 GiB and recovered to 16 GiB at
handoff. The full panel replay and paired financial refits remain below
the agreed 20 GiB free-space threshold. The recorded commands resume those
jobs from the saved inputs.

`just check` passed in pinned devenv, including the Lean proof and axiom
audits. The Python suite reported 233 passed and two skipped.
