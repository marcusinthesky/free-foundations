# Workshop exhibit inventory

The workshop claim map selects the following accepted assets. The 2015 design
covers observed complete issuer-quarters during 2016–2025. The joint lag fit
uses the 878 available issuer betas and medians. Representation geometry uses
the separately verified 967-row formation roster.

Paths below are relative to the repository root. The pipeline layout was verified at revision `1192f9c`.

| Manuscript use | Inputs, producer and sample |
| --- | --- |
| Data coverage | `processed_prepare_panel` supplies `data/processed/crsp-sec/panel/membership.parquet`. Filter December 2015 and count unique formation PERMCOs. The saved `roster.parquet` in the replication summary distinguishes the analytical roster from issuers with available estimates. See the [cohort receipt](../../../../t02-data-cohorts/evidence/coverage.md). |
| Table 1 | `research_replicate@2015` supplies the original-ratio formation. `research_collect_replication` assembles `data/research/crsp-sec/experiments/replication/summary/`. Use its `networks.parquet`, `estimates.parquet` and `intervals.parquet` for the joint kernel, intercept contrast and refit percentiles on the observed-quarter design. See the [baseline receipt](../../../../t03-spatial-inference/evidence/baseline.md). |
| Dated geometry | `research_matched_historical_geometry` reproduces the January 2016 TabPFN description on the full analytical roster. Check the DVC manifest against the archived state and the [prior interpretation receipt](../../../../t04-pcoa-interpretation/evidence/interpretation.md) before citing the saved association and spectrum tables. |

With the saved data present, run `just latex::assets` to replay the
`publication_render` command. Check the quarterly keys in
`data/publication/crsp-sec/free-foundations/claims.csv` and
`src/latex/projects/free-foundations/src/generated/numbers.tex`. Reproduce the
dated PCoA exhibit with `just dvc repro research_matched_historical_geometry`.
The broader T08 exhibits are reviewed from `publication_render_matched` after
its independent comparison targets qualify.

The table labels the saved 95% percentiles as refit variation. The formation
graph is fixed before draw-specific restriction and normalization. The
analysis does not establish interval coverage or complete terminal-outcome
coverage. The 10-NN bootstrap result remains open and is absent from the
exhibit. Pricing restrictions, portfolio risk and a matched supervised
readout comparison require their own evidence.
