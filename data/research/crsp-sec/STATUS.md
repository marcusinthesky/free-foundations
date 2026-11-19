---
description: What the in-sample study has and has not established yet.
---

# Study status

The in-sample design (`crsp-sec-quarterly-v2`) is implemented and tested. Every
stage ran on the frozen sources on 2026-11-18 and 2026-11-19. The saved results have
not yet been reviewed or written into the manuscript, so none is a stated finding.

## Sources

The frozen `crsp_sec_sources` stage holds the staged CRSP CIZ extract (477,653
monthly security rows, 2,781 PERMNOs), official SEC CompanyFacts and submissions,
historical identifier evidence and French factors; byte hashes are in its manifest.
Original filing documents were partly recovered into staging and are not used.

## Pipeline

| Stage | State |
| --- | --- |
| `prepare` | Complete: 59,508 analytical of 67,344 population issuer-quarters |
| `representations` | Complete: 15 January quarters, 2 rungs, 4 models and direct |
| `replication`, `comovement`, `alignment` | Complete |
| `publication` | Complete; with an intercept, every exact-kernel fit is a boundary fit |

## Verification

The Python checks pass: lint, strict types, Tach, test layout, Vulture and the test
suite, including recovery of known spatial coefficients and parity of the bootstrap
refits with statadic. Statadic's observed spatial panel could not run at study scale
(it requested 286 GB), so the panels use the eigenvalue profile likelihood.
