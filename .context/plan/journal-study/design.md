# Journal-ready CRSP–SEC study: in-sample spatial tests of foundation-model geometry

## Context

The design discussion in `.context/chat/Free Foundations CRSP (2026-11-17).md` moved
the study from a current-survivor Yahoo panel to a point-in-time CRSP universe, with
quarterly returns faithful to Fernández (2011) and survivorship handled through
historical membership. The quarterly CRSP–SEC migration (`a9542ce`) implements most of
that. It cannot yet produce a paper, for three reasons:

- **The Fernández characteristics are unavailable.**
  - `market_cap_assets`, `market_to_book` and `dividend_yield` are unavailable in all
    67,344 issuer-quarters; `debt_maturity` is available in only 9,174.
  - The cause: preparation accepts only SEC-verified market values, of which there are
    none, and requires lease-inclusive debt.
  - Encoders are blocked as well, because their context label is the next-quarter
    `market_cap_assets` (`study/encoding.py:211`).
- **The design is forecast-oriented.**
  - `study/analysis.py` scores past-only covariance forecasts.
  - It cross-fits ridge decoders, tunes bandwidths and fits a Gram θ.
  - The user wants a descriptive, inferential study with in-sample confidence
    intervals, not backtests or out-of-sample estimates.
- **The full-XBRL rung is blocked.** Original-filing recovery stopped at 661 of 3,357
  CIKs, with 113,441 filings pending.

Decisions made with the user:

- **Market value:** CRSP market equity combined with SEC book values.
- **Full-XBRL rung:** dropped; the standard XBRL rung uses CompanyFacts.
- **Sample:** the full point-in-time population, with no complete-case cohort.
- **Foundation models:** no fitted parameters on top of them. Each model's internal
  representation defines the network directly, so the only network parameter is the
  spatial coefficient ρ (or λ).

Intended outcome: a manuscript whose every number comes from saved in-sample
estimates with CIs, plus a faithful Fernández replication and parameter-free
comparisons of model geometry.

## Decisions after API probes (2026-11-17)

- **Kernel scale:** her exact `exp(−d)` on chord distances in [0, 2] gives nearly
  uniform W. In simulation with true ρ = 0.4, the pooled panel estimate was 0.91 and the
  period-effects estimates were 0.12–0.22. Every comparison network therefore uses
  `exp(−d / median_{i≠j} d)`: a deterministic, outcome-free scale from each network's own
  distances. ρ remains the only fitted network parameter. The exact kernel is reported as
  the faithful replication and as a sensitivity, together with each W's distance from
  uniform.
- **Intercept:** Layer A reports her no-intercept models (replication) and the same
  models with an intercept (the identified specification). Moran and LM diagnostics
  come from the intercept models.
- **Network construction (supersedes median scaling):** a further probe showed that the
  median-scaled kernel also fails. With an intercept, ML hits the boundary and returns
  NaN for N = 200–900, because embedding chord distances concentrate near √2 and
  row weights vary by only about 1.7×. Comparison networks are therefore k-nearest
  neighbours, with k = 10 declared in advance (5 and 20 as sensitivities),
  symmetrized and row-normalized. These graphs use only the ordering of distances.
  Fernández's exact `exp(−d)` remains the faithful replication. ρ is still the only
  fitted network parameter.
- **Configuration and layout:** the study settings move to DVC `params.yaml`. Stages and
  the CLI follow the CCFinance and pricing-perspective pattern: `stages <layer> <command>`
  with explicit inputs and outputs, `desc` and `params` on every stage.
- **Tractable standard rung and annual networks (2026-11-18):** the as-of CompanyFacts
  feature identifiers expand every concept by lag and offset, giving about 14 million
  columns by 2025. At about 80 s per model per 500-column block on the RTX 5060 Ti,
  that is infeasible. The standard rung is therefore the latest as-of value of each
  standard concept (by unit and period kind) with a 10% disclosure-coverage floor.
  States are encoded each January and networks held for the year. Peak VRAM per model
  is 2.3–3.7 GiB; encoding runs with `FF_CUDA_MEMORY_FRACTION=0.45` beside another
  GPU job.

## Scientific design

### Parameter-free networks (core principle)

Every network uses Fernández's kernel (eq. 10): `W = rownorm(exp(−d))`, with a zero
diagonal.

- **Distance:** `d` is always a chord distance, `d_ij = sqrt(2(1 − cos(z_i, z_j)))`.
- **Fernández histories:** `z` is the vector of centred ranks, so the chord distance is
  exactly her `sqrt(2(1 − ρ_Spearman))` (eq. 9).
- **Foundation models:** `z` is the frozen model embedding, so the scale ([0, 2]) and
  the kernel match hers exactly.
- **What is not used:** no bandwidth, no neighbour-count matching, no readout, no
  decoder, no shrinkage and no Gram θ.
- **What is estimated:** ρ/λ, σ², the CAPM premium in the Fernández cross-section, and
  the period effects in the panel.

All networks for a cross-section share one roster.

| Family | Networks |
| --- | --- |
| Fernández replication | One per characteristic (4) and the joint RMS network (her joint extension) |
| Direct control | Chord distance on the standardized raw rung features (NaN-aware pairwise) |
| Foundation models | TabPFN 3.5, TabFM 1.1, Kumo-Tabular, LimiX-2, for each rung |
| Classical comparators | Size (\|Δ log ME\| through the same kernel), SIC-2 industry (current SIC from SEC submissions, row-normalized), and a permutation null (relabelled W) |

There are two rungs:

- `fernandez`: ten annual history slots of the four characteristics.
- `standard_xbrl`: all CompanyFacts scalar facts as of each cutoff.

The `full_xbrl` rung, the PCA control and the supervised MLP control are removed.

### Data (existing only)

- **Returns:** CRSP CIZ monthly `mthret` for 2001–2025 (including delisting returns),
  compounded to quarterly returns at the issuer (PERMCO) level, as now.
- **Factors:** Mkt-RF and RF from the frozen French archive.
- **Characteristics (new definitions):**
  - ME is the CRSP issuer market equity at the month of the fiscal period end, summed
    over the issuer's classes in the extract.
  - `market_cap_assets` = ME / `Assets`.
  - `market_to_book` = ME / parent `StockholdersEquity`, which must be positive.
  - `dividend_yield` = `PaymentsOfDividendsCommonStock` (annual; fallback
    `PaymentsOfDividends`) / ME.
  - `debt_maturity` = noncurrent debt / total debt, excluding leases. Leases were off
    balance sheet in Fernández's 1997–2006 sample.
  - A missing tag stays missing; it is never treated as zero.
  - Each value records its CRSP and SEC component provenance in `components`.
- **Coverage audit first:** after re-preparation, print availability by characteristic
  and year before any encoding.

### Layer A — Fernández cross-section replication (faithful)

- **Formation:** December of year *y* (top 1,000, as in the contract).
- **Window:** the next 40 quarters.
- **Cohort:** the full formation roster, followed through exits, including delisting
  returns.
- **Stage 1:**
  - MM CAPM β per issuer from the quarters it is observed, with the existing R
    `robustbase` path (`fernandez/betas.R` via `fernandez/evaluation.robust_betas`).
  - The outcome is each issuer's median quarterly excess return.
  - Firms unable to fit stay as rows with an unavailable status.
- **Networks:**
  - Primary: predetermined W, built from information as of formation (the formation
    quarter's existing per-quarter encodings and characteristic histories). This keeps
    W exogenous to the outcome window.
  - Fidelity sensitivity (characteristic networks only): Fernández's contemporaneous
    timing, with histories ending at the window end.
  - Pairwise Spearman correlations are computed on intersecting years
    (`study/moments.pairwise_spearman`). Fewer than two common years gives the neutral
    distance √2; the count of neutral pairs is reported.
- **Models** (her specifications), each with W:
  - OLS without intercept.
  - Spatial lag by IV, as she estimated it; ML lag is added as a modern check.
  - Spatial error by ML.
  - Residual Moran's I, LM, robust LM and AK tests, AIC, and LR tests against OLS.
- **Windows:**
  - Primary: formation Dec 2015 → 2016Q1–2025Q4.
  - Rolling: formations Dec 2010 to Dec 2015 (six windows), shown as a descriptive
    stability figure. These are in-sample, not out-of-sample.
- **VaR comparative:** her eq. 8a/8b equal-weight portfolio VaR, evaluated at the fitted
  in-sample parameters for OLS versus each spatial model, with CIs. No exceedance
  backtest.

### Layer B — quarterly spatial panel of co-movement

- **Outcome:** quarterly excess returns `y_t`, for 2011Q1–2025Q4. XBRL coverage is
  complete from 2011.
- **Model:** SAR and SEM with period fixed effects. W_t comes from each quarter's
  as-of encodings, using the active roster per period. The panel is unbalanced:
  missing returns are marginalized, never imputed.
- **Estimated parameters:** ρ (or λ) and σ² only.
- **Purpose:** this replaces the dropped forecast comparisons. It is the in-sample
  counterpart of the paper's covariance `(I − ρW)⁻¹D(I − ρW)⁻ᵀ`.
- **Network comparison:** within a model class every network has the same parameter
  count, so the comparison is the in-sample log-likelihood difference. This is a
  Vuong-type comparison on per-quarter likelihood contributions.
- **Sensitivity:** the outcome net of `β̂_MM × Mkt-RF`, using the Layer A betas.

### Layer C — descriptive alignment (parameter-free)

- **Statistic:** the Spearman Mantel correlation between each network's distance and
  the realized return-correlation distance over the window. It is also computed against
  the Fernández joint distance.
- **Paired comparisons:** foundation model minus direct control, and foundation model
  minus Fernández joint, each against the same target.

### In-sample inference

| Quantity | Interval |
| --- | --- |
| Layer A ρ/λ and premium, conditional on β | Information-matrix CIs (`statadic.inference.spatial.spatial_covariance`) |
| Layer A, generated-regressor robust (primary) | Stationary quarter bootstrap: refit MM β and medians, then refit the spatial model with fixed W. 999 draws. Expected block length chosen by `statadic.inference.resampling.block_length.optimal_block_length_numpy` instead of the fixed 4 |
| Layer B ρ/λ | statadic observed-information CIs |
| Layer B network differences | `stationary_bootstrap_ci` on per-quarter log-likelihood-contribution differences |
| Layer C | `statadic.inference.independence.paired_mantel_bootstrap` (node bootstrap) and `mantel_permutation_kernel` p-values |
| Families of network contrasts | Holm adjustment, reported next to the raw intervals |

The seed stays at 42. Every estimate also records its failures and unavailability rows.

## Implementation steps

0. **Records.**
   - `just plan-new` for this plan, with child tasks for steps 1–8.
   - `just reference-new` for:
     - Fernández (2011, 2007 working paper)
     - Kou, Peng & Zhong (2018), *Asset Pricing with Spatial Interaction* (verify the
       citation)
     - Anselin (1988), and LeSage & Pace (2009)
     - Vuong (1989)
     - Politis & Romano (1994), and Politis & White (2004)
     - Yohai (1987, MM)
     - Mantel (1967)
1. **Dependency.**
   - Add `statadic==0.5.0a2` (PyPI; the tag contains `estimation/spatial/observed_panel`,
     `inference/spatial`, `inference/independence` and `inference/resampling`) to
     `src/python/apps/free_foundations/pyproject.toml`.
   - Run `uv lock`.
   - Add a comment in `semflow.toml` noting that statadic is an external pinned
     dependency, as pricing-perspective does.
   - Enable JAX float64 at the statadic boundary.
2. **Spec v2** (`study/spec.py`, `research/crsp-study/study.json`, version
   `crsp-sec-quarterly-v2`).
   - Set `RUNGS = ("fernandez", "standard_xbrl")`.
   - Add the window settings: 40 quarters, the formation-year list, and the panel range
     2011Q1–2025Q4.
   - Add the network list and the kernel declaration.
   - Bootstrap: draws 999, Mantel draws 9,999, block length `"politis_white"`.
   - Remove `return_lookback_quarters`, the fixed `bootstrap_blocks` and
     `min_eigenvalue`.
   - Update the `research/crsp-study/README.md` contract and replace `STATUS.md`.
3. **Characteristics** (`study/features.py:_characteristics`).
   - Use the CRSP ME definitions above, passing the issuer's monthly CRSP ME, which
     already exists in `prepared/issuer_monthly.parquet`.
   - Replace the lease-inclusive debt path with a lease-exclusive selector in
     `fernandez/characteristics.py`, keeping its component audit.
   - Update `CHARACTERISTIC_REASONS`.
   - Remove the empty component-semantics catalogue gate for market cap, and the gate
     on `original_xbrl_filings_incomplete` in `study/run._source_recovery` and
     publication. Unresolved linkage (2,361 issuer-quarters) stays as a ledger entry,
     not a gate.
4. **Encoding** (`study/encoding.py`).
   - Two rungs.
   - Remove `pca16` and `supervised_mlp16` from `conventional_states` and
     `representations/baselines.supervised_states` (along with its tests). Keep
     `direct`.
   - The context label (next-quarter `market_cap_assets`) becomes available with CRSP
     ME, so the encoder needs no other change.
5. **Analysis rewrite.** Each module is small and owns one layer;
   `study/analysis.py` becomes orchestration only.
   - `study/networks.py`: distances and W for every family. It reuses
     `fernandez/models.rank_distance` and `paper_weights` (moved here),
     `representations/distance.pairwise_distance("chord")` and
     `study/moments.pairwise_spearman`. It also builds SIC and size networks, and
     statadic graph objects.
   - `study/cross_section.py` (Layer A): statadic `SpatialProblem`, `ML(SAR())`,
     `ML(SEM())`, `SpatialIV`, `spatial_covariance`, `spatial_diagnostics` and
     `spatial_likelihood_ratio`; OLS without intercept. It reuses `_mm_estimates` and
     `generated_beta_indices` for stage 1 and the bootstrap.
   - `study/panel_model.py` (Layer B): statadic `ObservedSpatialPanelProblem`,
     `ObservedPanelML` with `effects="time"`, and per-period `ObservedSpatialPeriod`
     graphs.
   - `study/alignment.py` (Layer C): `statadic.association.mantel` and the
     `inference.independence` bootstrap and permutation.
   - `study/var.py`: eq. 8a/8b at the fitted parameters.
   - `study/inference.py`: rewritten around the statadic block-length, stationary
     bootstrap and Holm summaries.
6. **Delete superseded code** in the same change, with no backups; Git keeps history.
   - In `study/analysis.py`: `_forecast_covariances`, `gaussian_observed`, `fit_spatial`,
     `fit_gram`, `estimate_exposures`, `_decoded_states`, `match_gram_geometry`,
     `_geometry_tables`/PCoA and the forecast tables.
   - In `study/inference.py`: `paired_intervals` and `scientific_contrasts`.
   - In `fernandez/models.py`: `ols`, `lag_iv`, `error_ml` and the profile helpers.
     Before deleting them, add one parity test asserting that statadic SEM ML matches
     `error_ml` on a fixture.
   - `fernandez/kernels.py` and `fernandez/diagnostics.py`.
   - `panel/geometry.py` and `panel/decoding.py`, if no longer imported.
   - Their tests, `tach.toml` modules and Vulture entries.
7. **Publication and manuscript.**
   - `study/publication.py` renders `src/latex/build/crsp-study.tex` and tables:
     - sample and coverage
     - Fernández descriptive statistics and estimates per W (her table structure)
     - diagnostics
     - rolling-window figure
     - Layer B ρ and the likelihood-difference table
     - Mantel table
     - VaR table
     - claims audit
   - Rewrite `src/latex/main.tex`:
     - abstract, introduction and contribution: a few-parameter, in-sample test of
       whether foundation-model geometry organizes return co-movement and premia
     - empirical design and results
     - limitations: retrospective weights, revised CompanyFacts vintages,
       extract-limited share classes, current SIC, and the CRSP extract's missing
       terminal flags
     - conclusion
   - Remove the decoded-geometry and forecast framing and all "migration/archived"
     language. Theorem statements and Lean stay unchanged.
8. **Pipeline and docs.**
   - In `dvc.yaml`, `replication` → Layer A and `measurement` → Layers B and C.
     `prepare` and `representations` rerun.
   - Run `just semflow-patch`, then `just semflow-apply`.
   - Update `tach.toml`.
   - Update `README.md`, `research/README.md`, `src/python/README.md` and `CHANGELOG.md`.

## Verification

- **Unit and property tests (python-testing skill, mirrored layout):**
  - Networks are row-stochastic with a zero diagonal and permutation-equivariant.
  - The chord distance on centred ranks equals Fernández eq. 9.
  - The CRSP-ME characteristics are correct on fixtures, and missing values never
    become zero.
  - Synthetic SAR/SEM data: statadic recovers ρ inside its CI.
  - Generated-β bootstrap coverage is sane in a small Monte Carlo test marked `slow`.
- **Coverage gate:** after `just dvc repro prepare`, inspect the characteristic
  availability table, and confirm it before `just dvc repro representations` (GPU).
- **End to end:** `just build` (semflow-check, then DVC repro through `publication`),
  then `just latex::paper`. Every manuscript number must trace to a saved table through
  the claims audit.
- **Gates:**
  - `just python::check` (lint, pyrefly strict, Tach, layout, Vulture, tests)
  - `just latex::check`
  - `just lean::blueprint-check`
  - `just check`

## Compute and risks

- **Compute:** re-preparation takes hours. Encoding runs four models × two rungs × about
  60 quarters on the local GPU. The MM bootstrap is 999 refits of about 1,000 firms per
  window: run it for the primary window, and use information-matrix CIs for the rolling
  windows.
- **Risk:** sparse dividend tags for non-payers produce undefined dividend histories,
  which become neutral distances. The neutral-pair counts are reported, and the joint
  network is unaffected by any single characteristic.
