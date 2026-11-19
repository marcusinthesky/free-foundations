# FinFM candidate handoff

The local anonymous long paper is under
`src/latex/projects/free-foundations/build/finfm-candidate/`.

| File | Contents |
| --- | --- |
| `finfm.pdf` | Four-page US Letter candidate, including references and appendix |
| `title.txt` | Matching plain-text title |
| `abstract.txt` | Matching plain-text abstract |

PDF SHA-256:
`e33bb20f5d5deef56ad240e7c4fd08258351eb645b50b0764a703927ee13d4d7`.

The checkout is based on `793ae468309e02b5f46fc73a2ab00080464e973d` with
working changes. The scientific receipts bind the saved inputs independently.
The final layout was rebuilt from an empty FinFM build directory with
`just latex::paper finfm` in pinned devenv. The build used
`SOURCE_DATE_EPOCH=1795046400` for repeatable PDF dates. The named arXiv
layout also built. The reviewed files were copied to the candidate directory.
A source-only copy built both layouts and showed a visible
notice where the private numerical assets were absent.

The submission deadline is **21 November 2026 at 13:59 SAST**. The
[official call](https://finfm.finhorizons.org/) gives the paper-length and
anonymity requirements. The [public venue page](https://openreview.net/group?id=AAAI.org/2027/Workshop/FinFM)
does not expose the live submission fields used here. Confirm title, abstract,
author order, OpenReview readiness, presenter, track, disclosures, optional
supplement and the submission decision from an author account. See the
[cover note](../../../cover-note.md).

The candidate uses the fixed 2015 observed-quarter reimplementation, two
formal results and the dated input-alignment PCoA. The exhibits and audit
document the inference and terminal-outcome limits. Pricing, matched
supervised calibration, model-implied risk and full sensitivity remain
with their research tasks.
