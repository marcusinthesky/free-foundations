# Paper and supplement

The single paper lives in `projects/free-foundations`. Its `src/sections/`
contains the shared article and appendix; `src/targets/arxiv.tex` and
`src/targets/finfm.tex` supply the two layouts. Both targets use the same body
and appendix. A source build works without the private numerical inputs and
shows a visible data-availability notice. Use the paper command for a
candidate with results.

Run from the repository root, inside the pinned devenv environment:

```sh
just latex::build arxiv  # cached Tectonic build of the shared manuscript
just latex::build finfm  # anonymous AAAI-27 pdfLaTeX/BibTeX build
just latex::assets       # render saved research outputs only
just latex::paper arxiv  # render saved results, then build
just latex::paper finfm
just latex::count arxiv
just latex::check         # format/lint and both target builds
just latex::prose-lint     # optional editorial suggestions for all sections
```

After `just latex::setup`, the prose check runs offline. Pass individual
authored `.tex` paths to review selected sections. Matches identify the rule
and original source location; read the surrounding paragraph before editing.

`just latex::assets` writes `projects/free-foundations/src/generated/` from saved
CRSP–SEC results. It does not acquire data or fit models. Individual numbers
are declared in `generated/numbers.tex` and read with `\ffvalue{key}`;
`\ffnum[precision]{key}` and `\ffnume[precision]{key}` format numeric values.
The canonical keys have `quarterly-` or `apt-` prefixes. Generated tables are
separate `tabular` fragments under `generated/tables/`; authored sections own
their table captions, labels and placement and can include the bodies with
`\input{generated/tables/<name>}`. The corresponding claims and metrics audit
is saved in `data/publication/crsp-sec/free-foundations`.

The reference exporter writes the project-local `src/refs.bib` from authored
CSL records. Run `just sync` after editing references. The AAAI author-kit files
under `src/vendor/` are kept byte-identical to their source. Generated TeX and
PDFs are never hand-edited; `build/` is ignored. The arXiv target uses the pinned
Tectonic bundle, while FinFM uses the pinned TeX Live pdfLaTeX environment required
by the AAAI kit.
