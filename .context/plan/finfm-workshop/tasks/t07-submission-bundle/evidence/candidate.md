# FinFM candidate handoff

The anonymous author-review bundle lives under
`src/latex/projects/free-foundations/build/finfm-candidate/`. The main
text ends on page 4 of the ten-page US Letter PDF. The title and abstract
in the bundle agree with the rendered first page.

| File | SHA-256 |
| --- | --- |
| `finfm.pdf` | `31c44246093adcb882c9edd19a0acf8d574e79be16cd0905acb3a0541ffbbe55` |
| `title.txt` | `00f589fefbfdc25a3f5784e6df414b2e9be4ee7fa120a3688a79f952f1003e6b` |
| `abstract.txt` | `c7fae2f7f13d622bec9a1de938bf9ca82af7f29d1196b1b946bd8af3cfb653fd` |

The working copy builds on `6d43351`. The bundle's `sources.sha256`
identifies the manuscript, template, bibliography and numerical exhibits
used by this PDF. Verify it from the repository root and verify
`SHA256SUMS` from inside the bundle.

The primary-cohort exhibits were rendered with `just latex-assets`. The
matched exhibits use the indexed run at `/tmp/finfm-locked.rmyDtK`.
A fresh `research collect-matched` reproduced its evidence index byte for
byte (SHA-256 `f89349c8b3de8ee0df87f52756753db3b7f732caeacc3661a7b8d68fd90a1227`).
Its input panel manifest matches the canonical panel
(`a56bd4ea963bcfd6556b75da3f769fffd875c1ce7593e776e21b1b642be594ff`).
Both layouts built in pinned devenv with `SOURCE_DATE_EPOCH=1795046400`.

Before submission, compare the canonical matched evidence index under
`data/research/crsp-sec/experiments/matched-comparisons/evidence/` with
the hash above. If it differs, compare the stage artifacts, regenerate the
matched exhibits from the canonical outputs, review any changed claims
and refresh the bundle and its hashes.

The submission deadline is **21 November 2026 at 13:59 SAST**. The
[official call](https://finfm.finhorizons.org/) gives the paper-length and
anonymity requirements. The [public venue page](https://openreview.net/group?id=AAAI.org/2027/Workshop/FinFM)
does not expose the live submission fields used here. Confirm title, abstract,
author order, OpenReview readiness, presenter, track, disclosures, optional
supplement and the submission decision from an author account. See the
[cover note](../../../cover-note.md).
