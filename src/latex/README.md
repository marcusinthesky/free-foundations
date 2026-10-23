# Paper and supplement

The manuscript is *Pretrained Tabular Features and the Measurement of Financial
Proximity*. Its five main sections are Introduction, Framework, Empirical design,
Results, and Conclusion. The argument connects economic proximity, information
retained by prediction tasks, exposure estimation, and covariance forecasting.
One retrospective frozen-feature application examines these connections. The
appendices contain the exact mathematical statements and proofs, empirical
construction and decisive diagnostics, then the Fernández core replication and
VaR audit.

Run the publication commands from the repository root in the development environment:

```sh
just latex-assets  # tables, scalar bindings, PGF figure, and claims audit
just latex-build   # assets, then Tectonic compilation
just latex-count   # assets, then TeXcount; writes build/word-count.txt
```

The combined paper and supplement are written to `src/latex/build/main.pdf`.
Publication reads recorded artifacts: it does not fit models, acquire financial
observations, or alter numerical DVC outputs. Restore missing artifacts through
DVC first; the root README documents the retained empirical workflow.

TeXcount, Tectonic, and the `pdflatex` packages used to measure PGF labels are
provided by `devenv.nix`. Reload the development environment after updating it.
Python dependencies are locked in `src/python/uv.lock`; generated assets and the
Matplotlib cache stay in the ignored `build/` directory.

## Publication assets and evidence

The main text has three tables and one figure:

- `measurement.tex` compares direct inputs, PCA, the valuation-task network and
  all four pretrained models, with exposure-prediction R² preceding native and
  calibrated forecast gains. A separate panel reports the reference-exposure and
  in-panel-exposure return-based benchmarks on the same forecast outcomes and
  score reference. Main scores use five-year histories, 256 encoder examples where
  applicable, rank-five exposures, matched-neighbor bandwidths and fitted
  firm-specific innovation variances.
- `variance-contrasts.tex` and `variance-contrasts-marginal.tex` report
  calibrated-minus-native differences in two panels: fitted innovation variances
  and common marginal variances. Each panel
  gives point estimates and paired confidence intervals for expected bootstrap
  blocks of 21 and 63 scored dates. The full paired contrasts, including direct
  benchmarks, remain in the empirical appendix.
- `support.pgf` distinguishes encoder context size from financial training firms
  per readout fold. The context experiment uses all available calibration firms,
  whereas the calibration-size experiment limits their number, so the endpoints
  need not coincide.
- `geometry-main.tex` compares direct Gram and spatial covariance on identical
  unit-chord geometries with common marginal variances. Both native and decoded
  principal geometries and the joint characteristic control are shown. The
  displayed differences are Gram minus spatial scores; adverse results are
  retained and the count of negative contrasts is bound to saved estimates.

Decoder means are unweighted annual averages over **2016–2025**; forecast scores
cover **2020–2025**. The appendix also reports decoder means over forecast years.
Score gains use the joint characteristic exponential-kernel reference within
the relevant variance specification. Neither score differences nor their
firm-day normalization are portfolio returns or welfare measures.

Decisive supplementary evidence includes target reliability, normalization and
fold sensitivity, learned-weight controls, common-marginal results and historical
return-based benchmarks. Kumo's three fresh initializations reproduce one
intercept-only cross-fitted null, displayed once; the null diagnostic checks all
three draws in every year.
The direct-geometry appendix retains all 31 geometries in both covariance
models and variance treatments, including six resets and the decoded
intercept-only control. It reports both bootstrap block lengths, full spectra,
rank-five descriptive projection summaries, and a PGF scree plot for the fixed
latest year, 2025. Signed Gram similarities retain their diagonal and are never
row-normalized. Empirical Gram residual scales and profiled spatial innovation
scales differ; common-marginal results lead the comparison. Component portfolios
and their projection shares are descriptive, with all weights and component
returns retained in the saved geometry artifacts. The original raw statistic is
an uncentered return-energy share; centered coordinates exclude the uniform
cross-sectional direction while that statistic's denominator retains it. The
companion relative-return share uses cross-sectionally centered energy in its
denominator and is compared with rank-matched random centered subspaces. These
statistics are neither standard regression R² nor time-series variance shares.
The direct Gram covariance uses the full uncentered similarity matrix. It does
not test an estimated component-factor covariance, and low raw energy shares
do not rule out characteristic-mimicking factors. Annual PCoA coordinates do not
provide a reusable transform for new firms.
`pcoa-energy.tex` gives relative-return energy shares and rank-matched random
centered-subspace references. Reference bands summarize random directions, not
confidence intervals; undefined denominators remain missing and valid annual
counts are shown. `pcoa-cutoff.tex` separates numerical ties at the retained
boundary from relative gaps at most 0.001. The prescribed rank remains fixed;
numerical boundary ties flag a nonunique subspace rather than prompting a rank
chosen using returns.

The replication tables report the primary common-four CAPM exercise with zero
self-links, supported explicitly by the 2007 working paper. Timing windows are
crossed with both MM packages on natural and intersection cohorts. The appendix
displays the intersection contrasts and cohort sizes and separates raw Moran
I from its standardized z statistic, conditional SEM fit from its reduced-form
mean, and information-matrix inference from the original score covariance.
The generated-beta bootstrap remains on the primary result. The complete model
landscape and earlier extraction stages are not publication dependencies.

## Rendering and claims audit

`render_results.py` selects and verifies saved estimates. pandas `to_latex`
generates ordinary `booktabs` tables; Jinja2 with strict undefined variables
binds numerical claims; Matplotlib exports the native PGF figure at its authored
6.5-inch width. Tectonic typesets labels using the manuscript fonts. There is no
separate raster or vector plot replacing the PGF source.

`build/claims-audit.json` records input hashes, selectors, reporting windows,
headline values and figure series. Validation requires unambiguous selections,
complete years and common observations; it reconciles totals to annual scores,
paired contrasts to their inputs, and numerical claims to the reported
confidence sets and replication estimates. Exposure-prediction extrema are
computed from the selected current results rather than assigned to a named
model in prose.

Geometry validation requires the full 124-procedure grid, all 744 annual scores,
310 PCoA summaries and complete spectra. Every recorded contrast is reconciled
to annual differences, and every geometry artifact is checked against its source
manifest, including the binary coordinate, weight and return files. Annual
projection ratios are reconciled to total, relative and projected energy;
cutoff flags are checked against the saved eigenvalues. Replication sensitivity
validation requires all 160 conditional estimates, both software
runtime records in both windows, and unchanged intersection firm identities.
Publication generation atomically replaces restored output files so it does
not write through DVC cache hard links.

The audit checks consistency among recorded artifacts. It does not independently
certify the source data or regenerate financial estimates. Historical overlap
checks belong to the recorded migration audit, rather than requiring retired
experiments for every publication build. Restored outputs, numerical
regeneration and manuscript compilation remain separate reproducibility claims.

## Length and mathematical review

The main-text target is approximately **3,800 words**, with a **4,000-word
ceiling** including headings and captions, and a **180–220-word abstract**. This
replaces the earlier 3,500-word target to support progressive explanation of the
economic argument and empirical design. TeXcount excludes the appendices and
bibliography and treats bound numerical macros as words. Report prose,
headings and captions separately; subtract the initial title/abstract subtotal
when quoting the main-text count. Displayed mathematics and table cells are not
prose under this convention.

The main text explains task–target alignment and calibrated measurement risk.
Their exact proposition statements, declaration tags and proofs appear with the
supporting identities in the mathematical appendix. The conditional
covariance-stability result keeps bandwidth, spatial coefficient and innovation
covariance fixed; it is not a performance guarantee for re-estimated procedures.
The portfolio-regret result remains in the complete Lean blueprint rather than
the manuscript.

`just blueprint-check` checks the declarations named in the manuscript and the
blueprint against the compiled Lean library. Retained declaration tags are
hidden in the typeset manuscript. Mathematical review also checks the actual
hypotheses and correspondence with the financial statements; declaration
existence alone does not establish that correspondence. The full blueprint is
`src/lean/blueprint/src/content.tex`, built separately with `just blueprint-pdf`.

## Interpretation and provenance

The application predicts a historical statistical exposure proxy, not directly
observed structural exposure. Conditional on fixed pretrained weights and
context, its deterministic features add no information to the supplied history;
the potential gain is accessibility to the restricted fitted readout. The
auxiliary valuation task is not assumed sufficient for exposures, and the
conditional risk bound supplies no pretraining-specific convergence rate.

Current-survivor sampling, retrospective checkpoints, evaluation-year
configuration examination and conditional inference remain explicit in the
manuscript. Removing retired execution branches does not create a new holdout.
Frozen SEC, Yahoo and corporate-action sources and their reviewed price
decisions remain identifiable. Public checkpoints retain immutable revision
identities and verified hashes; reviewer access to the private financial archive
is available from the author on request.
