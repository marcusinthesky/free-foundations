---
description: Anonymous FinFM AAAI-27 workshop submission and how to rebuild it.
---

# FinFM AAAI-27 submission

`submission.tex` is the anonymous long-paper version (at most 7 technical pages)
for the FinFM workshop. It uses the unmodified AAAI-27 author kit (`aaai2027.sty`
and `aaai2027.bst`, both from AuthorKit27, October 2026), which requires pdfLaTeX;
the pinned devenv TeX Live provides it. The identifiable working
manuscript stays in [`../main.tex`](../main.tex).

Every number in the paper is a macro or table generated from saved stage outputs
by the `workshop` DVC stage, written to the DVC-tracked `generated/` directory.
The references come from the shared `../refs.bib`. `anonymous.bib` holds only the
anonymised self-citation of the statistical library.

```sh
just dvc repro -s apt          # out-of-sample spatial APT (about 20 minutes, CPU)
just dvc repro -s workshop     # macros and table bodies from saved results
just latex::finfm              # pdfLaTeX + BibTeX; fails on undefined references
```

`abstract.txt` is the plain-text abstract for OpenReview. Before uploading, check
the anonymity list in the plan record
([finfm-workshop](../../../.context/plan/finfm-workshop/README.md)).
