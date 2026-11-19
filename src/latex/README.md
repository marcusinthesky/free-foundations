# Paper and supplement

The single paper lives in `projects/free-foundations`. Its `src/sections/`
contains the shared article and appendix; `src/targets/arxiv.tex` and
`src/targets/finfm.tex` supply the two layouts. The current manuscript is an
outline scaffold: the introduction has reviewed structural comments and the
remaining sections await drafting. Both targets use the same body and appendix.

Run from the repository root, inside the pinned devenv environment:

```sh
just latex::build arxiv  # cached Tectonic build of the shared outline
just latex::build finfm  # anonymous AAAI-27 pdfLaTeX/BibTeX build
just latex::assets       # render saved research outputs only
just latex::paper arxiv  # render saved results, then build
just latex::paper finfm
just latex::count arxiv
just latex::check         # format/lint and both target builds
```

`just latex::assets` writes `projects/free-foundations/src/generated/` from saved
CRSP–SEC results. It does not acquire data or fit models. Individual numbers
are declared in `generated/numbers.tex` and read with `\ffvalue{key}`;
`\ffnum[precision]{key}` and `\ffnume[precision]{key}` format numeric values.
The canonical keys have `quarterly-` or `apt-` prefixes. Generated tables are
separate `tabular` fragments under `generated/tables/`; authored sections own
their table captions, labels and placement and can include the bodies with
`\input{generated/tables/<name>}`. The corresponding claims and metrics audit
is saved in `data/research/crsp-sec/publication`.

The reference exporter writes the project-local `src/refs.bib` from authored
CSL records. Run `just sync` after editing references. The AAAI author-kit files
under `src/vendor/` are kept byte-identical to their source. Generated TeX and
PDFs are never hand-edited; `build/` is ignored. The arXiv target uses the pinned
Tectonic bundle, while FinFM uses the pinned TeX Live pdfLaTeX environment required
by the AAAI kit.
