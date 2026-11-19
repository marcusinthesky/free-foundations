# Paper and supplement

The manuscript is *Pretrained Tabular Features and the Measurement of Financial
Proximity*. The retained framework and mathematical appendix distinguish
predictive sufficiency, economic alignment, exposure estimation, geometry and
financial loss. The [Lean guide](../lean/README.md) records proof assumptions,
compiled declarations and integrity checks.

The empirical section now consumes the
[quarterly CRSP–SEC study](../../data/research/crsp-sec/README.md). The previous
current-survivor manuscript and publication guide remain in the Git history. Their
numerical findings are not conclusions of the new dataset.

```sh
just latex::assets # saved-result tables, source coverage and claims audit
just latex::paper  # render, then Tectonic compilation
just latex::count  # render, then TeXcount to build/word-count.txt
```

The combined manuscript is written to `src/latex/build/main.pdf`. Rendering reads
saved panel, representation, measurement and replication artifacts. It never
acquires financial data or refits a model. The generated
`build/crsp-study.tex` reports coverage, estimator availability and recorded
estimates; pending or failed stages remain explicit. The corresponding claims
audit is saved under `research/crsp-study/publication`.

All empirical artifacts must agree on the study specification, master-panel,
issuer-roster and observed-return-mask hashes. Consistency checks do not certify
historical source completeness. Current ticker candidates, verified historical
SEC links, missing XBRL and unresolved linkage remain distinct. Terminal-return
coverage and whole-issuer capitalization are not certified by the staged CRSP
fields. Retrospective model weights and revised SEC data remain limitations.

TeXcount, Tectonic and TeX packages are supplied by `devenv.nix`; generated files
stay under ignored `build/`. `just lean::blueprint-check` checks every retained
manuscript declaration against compiled Lean names. Declaration existence is
separate from checking that a theorem's hypotheses justify an economic claim.
Publication does not claim that conditional theory establishes an empirical
model ranking.
