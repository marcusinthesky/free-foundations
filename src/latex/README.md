# Paper and supplement

Run `just latex-build` from the repository root in the development environment.
The combined paper and supplement are written to `src/latex/build/main.pdf`.
The build reads recorded results; it does not run models, refit estimates, or
change DVC outputs. Restore missing empirical artifacts with `dvc pull` first.

```sh
just latex-assets  # regenerate tables, scalar bindings, PGF figure, and audit
just latex-build   # assets, then Tectonic compilation
just latex-count   # assets, then TeXcount; saves build/word-count.txt
```

The Python environment uses `src/python/uv.lock`. TeXcount, Tectonic, and the
`pdflatex` packages used for PGF text metrics are
provided by `devenv.nix`; reload the development environment after updating it.
Generated files and the Matplotlib cache stay in the ignored `build/` directory.

## Standard rendering tools

- [pandas `DataFrame.to_latex`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_latex.html)
  produces the `booktabs` tables and multipage `longtable` grid. LaTeX typesets
  their text and numbers; the tables are not images.
- [Matplotlib's PGF backend](https://matplotlib.org/stable/users/explain/text/pgf.html)
  exports `support.pgf`, included directly with LaTeX `\input` at its authored
  6.5-inch width. Tectonic typesets its text and mathematics with the manuscript
  fonts. `pgf.rcfonts=False` prevents Matplotlib from overriding those fonts;
  `pdflatex` and `lmodern` measure labels during layout. The build produces no
  separate PDF/SVG/PNG plot. Inspect the figure in the compiled manuscript.
- [Jinja2](https://jinja.palletsprojects.com/en/stable/)
  renders `numbers.tex.j2` into numerical macros consumed by the abstract and
  results. Strict undefined variables stop the build instead of silently
  producing empty claims.
- Tectonic compiles the existing LaTeX source. TeXcount measures the text; there
  is no custom compiler wrapper, table-markup renderer, or word-count parser.

PyLaTeX would add a second document-construction interface to an existing LaTeX
paper. `tabulate` is useful for simple exports, but pandas already provides the
required multipage LaTeX output. `pgfplotstable` is a reasonable CSV-to-TeX option;
here, pandas keeps filtering, aggregation, and output in the same Python step.
The workflow therefore uses these established interfaces without introducing
another rendering framework or copying the custom tooling in
`pricing-perspective`.

## Binding and audit

`render_results.py` contains the paper-specific selectors and validation, not
empirical estimation. Main-table scores select five-year `histories`, 256
support rows where applicable, matched kernels, and diagonal innovations, with
the joint exponential-kernel reference. Decoder fits select rank five and use
unweighted annual means over **2016–2025**; forecast scores cover **2020–2025**.
The supplement also reports decoder means restricted to forecast years.

The replication table uses the current 33-firm common-four CAPM ladder with
zero self-links. Beta slopes and their conditional standard errors are rendered
in percentage units from the saved estimates. The main text also binds the
replication slopes, their uncertainty, and the support-size ranges to these
artifacts.

`build/claims-audit.json` records source SHA-256 hashes, selectors, aggregation
periods, headline values, and support-series values. The renderer checks:

- Unique selected rows, complete annual records, and common firm-day counts.
- All saved score totals against the saved annual scores, and reported
  gains against the appropriate joint reference.
- Decoder periods, paired contrasts, confidence intervals, replication AIC
  arithmetic, and the actual principal model confidence set.
- Every unchanged overlapping forecast against the earlier three-support
  experiment, with an absolute score tolerance of 0.00001.

Missing inputs, ambiguous selections, or inconsistent claims fail the build.
This checks agreement among recorded artifacts, not independent correctness of
the empirical pipeline or original data. The audit identifies the four-model protocol and hashes its run manifest and
actual inputs. It retains `162a7fd6f32fa1a02f8caa6262968687a285b417` as the
reviewed legacy reference, distinct from the new experiment.

## Counts and formal checks

TeXcount directives exclude the supplement and bibliography and count bound
numerical macros as words. `just latex-count` reports prose, headings, and
captions separately, with section subtotals. The initial subtotal contains the
abstract and title; subtract it when reporting main-text counts. Displayed
mathematics and table cells are not prose words under this convention.

The target is approximately 2,300 main-text words and a 180–220-word abstract,
with main text, headings, and captions together below 2,500 words under the
stated counting convention.

The combined PDF contains a paper-focused mathematical appendix: economic
motivation, assumptions, statements, substantive proof steps, and financial
interpretation. It covers exposure geometry, task alignment, calibration,
second-moment scoring, spatial filtering, and stability through portfolio risk.
The complete declaration-level blueprint remains available separately in
`src/lean/blueprint/src/content.tex` and through `just blueprint-pdf`.

`just blueprint-check` builds Lean and checks declarations named in both the
blueprint and manuscript. Declaration tags remain in the manuscript source but
are hidden in its typeset output. Mathematical review additionally checks the
assumptions and correspondence between those declarations and the paper's
statements. Each result's economic interpretation follows its stated hypotheses.

## Implementation details accompanying the supplement

Package names, artifact paths, and commands belong in this documentation rather
than the typeset manuscript. Stage-one robust MM estimation uses
`robustbase::lmrob`; the exposure decoder selects its ridge penalty with
`RidgeCV`. The replication source mapping and diagnostics are recorded in
`research/ladder/r0/replication-manifest.md` and
`research/ladder/r0/estimates.csv`. Additional ladder comparisons are described
in `research/ladder/four/RESULTS.md` and `research/ladder/three/RESULTS.md`.

For the principal panel, `research/panel/three-foundations/checkpoints.json` records
model versions and weight hashes; `target-audit.csv` and `decoding.csv` in the
same directory report target diagnostics and decoder results. Context records
identify support observations, query firms, features, labels, and cutoffs.
The measurement sensitivity audit is in `research/panel/audit/summary.csv`.
Companion designs under `research/panel/` are `four` (three-year histories),
`four-h5` (history-length comparison), `four-xqxo` (QXO exclusion), and `three`
(broader inputs and measurement variants).

Nested encoder supports use hash-ordered prefixes of a common support table,
with shared feature preprocessing held fixed across sizes. Outcome normalization
and model-internal preprocessing follow each prediction interface at its supplied
context size. The decoder's five folds are
assigned from ticker hashes. The replication records repeated MM fitting
attempts when convergence fails; the checkpoint record retains model versions
and weight fingerprints. These implementation details accompany the statistical
descriptions in the supplement.

The publication renderer checks the saved results without rerunning estimation.
For empirical reproduction, use `just python-ladder` and
`dvc repro panel_validate_measurement panel_report_three_foundations`.
The latter command includes the principal experiment and its measurement
diagnostics; `dvc.yaml` and `dvc.lock` specify the workflow.

## Representative model comparison

The main table uses prediction-head features from TabPFN 3.5, Google TabFM 1.1,
Kumo-Tabular Large and LimiX-2 alongside direct, PCA and supervised controls.
Earlier TabFM/Kumo features and three random initializations of TabPFN/Kumo
appear in supplementary tables. The PGF figure separates encoder support size
from financial calibration sample size; neither axis substitutes for the other.
The declared model landscape and execution protocol are in
`research/panel/three-foundations/`.

Raw SEC, Yahoo and corporate-action inputs are frozen DVC sources. Numerical
stages fail with a restoration instruction if a required snapshot is missing;
they do not fetch replacements. See the root README for restoration commands.

## Measurement construction and headline uncertainty

The renderer additionally reads `three-foundations-validation`: paired principal
contrasts, normalization comparisons, fold sensitivity, and null-control checks.
It binds the date count, target commonality and normalized joint-score example
from recorded results. The headline calibration contrasts retain both 21- and
63-day intervals, including the common-marginal reversals and the block-length
sensitivity of TabPFN versus native direct distance.

The new tables use the existing pandas LaTeX interface, and the support figure
remains native PGF. Numerical evaluation belongs to the DVC diagnostic stage;
the publication renderer only verifies and formats its saved artifacts.
