# Chronological matched-panel comparison

One constant spatial coefficient per approach is estimated by Gaussian residual ML
on 2016-2019 and frozen for 2020-2025. The principal score is summed held-out
Gaussian log-likelihood of daily excess returns; higher is better. It includes all
normalizing constants. Returns are decimals, not percentages.

All approaches use the identical annual firms and dates. Every annual spatial
network combines its input into one W. There is no coefficient per feature or year.
Annual nuisance variances and factor loadings are estimated using preceding returns.
No test-year factors or returns enter an annual covariance or expected-return forecast.

| Approach | Frozen lambda | Held-out log-likelihood | Gain vs joint four | Boundary |
| --- | ---: | ---: | ---: | --- |
| fernandez_market_cap_assets | 0.2088 | 219,946.41 | -46.83 | False |
| fernandez_market_to_book | 0.2086 | 219,894.13 | -99.11 | False |
| fernandez_dividend_yield | 0.1994 | 219,999.94 | +6.70 | False |
| fernandez_debt_maturity | 0.1331 | 219,900.80 | -92.44 | False |
| fernandez_joint_four | 0.2276 | 219,993.24 | +0.00 | False |
| four__direct | 0.2190 | 219,960.75 | -32.49 | False |
| four__pca16 | 0.2178 | 219,959.65 | -33.59 | False |
| four__autoencoder | 0.2156 | 219,952.35 | -40.89 | False |
| four__random_autoencoder | 0.2147 | 219,947.21 | -46.03 | False |
| four__tabpfn_fast | 0.2272 | 219,980.70 | -12.54 | False |
| four__tabpfn_full | 0.2300 | 219,985.25 | -7.99 | False |
| four__tabfm | 0.2158 | 219,963.10 | -30.14 | False |
| four__exaone | 0.2270 | 219,983.45 | -9.79 | False |
| broad__direct | 0.2269 | 219,978.84 | -14.40 | False |
| broad__pca16 | 0.2602 | 220,033.65 | +40.41 | False |
| broad__autoencoder | 0.2573 | 220,031.71 | +38.47 | False |
| broad__random_autoencoder | 0.2189 | 219,960.87 | -32.37 | False |
| broad__tabpfn_fast | 0.2288 | 219,981.42 | -11.82 | False |
| broad__tabpfn_full | 0.2320 | 219,990.10 | -3.13 | False |
| broad__tabfm | 0.2161 | 219,963.29 | -29.95 | False |
| broad__exaone | 0.2299 | 219,984.77 | -8.47 | False |
| metrics__direct | 0.2376 | 219,996.03 | +2.79 | False |
| metrics__pca16 | 0.2668 | 220,054.56 | +61.32 | False |
| metrics__autoencoder | 0.2641 | 220,045.25 | +52.01 | False |
| metrics__random_autoencoder | 0.2299 | 219,956.91 | -36.33 | False |
| metrics__tabpfn_fast | 0.2285 | 219,980.16 | -13.07 | False |
| metrics__tabpfn_full | 0.2305 | 219,980.69 | -12.55 | False |
| metrics__tabfm | 0.2157 | 219,962.36 | -30.88 | False |
| metrics__exaone | 0.2296 | 219,983.71 | -9.53 | False |
| ff5_mom_spherical | 0.0000 | 219,784.95 | -208.29 | False |
| uniform_network | 0.2043 | 219,939.50 | -53.74 | False |
| ff5_mom_diagonal | — | 224,657.11 | +4,663.87 | False |
| ff5_mom_sample_residual_covariance | — | 224,819.87 | +4,826.63 | False |
| raw_sample_covariance | — | 224,819.87 | +4,826.63 | False |

## Annual matched cohorts

| Return year | Firms | Prior complete days | Scored days |
| --- | ---: | ---: | ---: |
| 2016 | 58 | 756 | 251 |
| 2017 | 63 | 756 | 250 |
| 2018 | 64 | 554 | 250 |
| 2019 | 64 | 754 | 251 |
| 2020 | 60 | 754 | 252 |
| 2021 | 47 | 756 | 251 |
| 2022 | 48 | 757 | 250 |
| 2023 | 60 | 756 | 249 |
| 2024 | 64 | 753 | 251 |
| 2025 | 70 | 753 | 249 |

## Construction and chronology

- The four characteristics are capitalization/assets, market/book, dividend yield,
  and the strict lease-inclusive noncurrent-debt/total-debt ratio. Missing debt is
  never interpreted as zero. Known unresolved multiple share classes are excluded.
- Each annual snapshot uses only 10-K/10-K-A facts filed by December 31, with period
  ends no more than 550 days old. Original dates and accessions are retained in cache.
  Capitalization uses shares and split-reversed prices at the share observation date;
  assets and equity share a balance-sheet date. These dates can differ and are audited.
  Dividend yield uses trailing cash dividends on the same split basis as price.
- The strict cohort requires three complete, nonconstant annual histories for all
  four characteristics and at least 500 prior returns. The three-year history is
  a coverage compromise and yields relatively coarse Spearman distances.
  This is a US chronological adaptation, not an exact replication of Fernández's
  original sample, robust cross-sectional S-APT estimation, or history length.
- Fernández rows use Spearman chord distances, exp(-distance), zero diagonal,
  and row normalization. The joint-four RMS row is our extension; the original
  single-characteristic networks remain explicit references.
  A uniform network provides a geometry-free reference for the added value of topology.
- `four` encodes all four three-year histories jointly. `broad` adds up to 200
  unit- and period-specific SEC concepts in signed-log levels. `metrics` adds
  up to 100 concepts, asset-normalized dollar measures, their annual changes, and
  log assets. Schema selection uses past support-period coverage only.
- Model inputs use support-only median imputation, missingness indicators,
  standardization and clipping. PCA, autoencoder and random-encoder controls share
  a deterministic, outcome-independent 256-row historical support cap with the
  pretrained models. Preprocessing is fit before this cap on eligible past support.
  Support membership is matched across encoders within a rung. Cross-rung eligibility
  can differ slightly; common support counts are recorded in context-overlap.csv.
- Frozen foundation-model readouts use native late row states, not return predictions.
  The supervised context target is next-snapshot capitalization/assets, available
  by the network cutoff. Context years, rows, schemas and checkpoint hashes are saved.
  All learned vectors use unit-sphere chord distance and the same exponential kernel.
  The direct baseline adds a constant coordinate to avoid zero-vector distances.
- Factor means, loadings and covariances use the preceding three calendar years.
  The spatial coefficient is fitted once on calibration-year factor residuals,
  profiling an innovation variance per calibration year. Each evaluation year's
  variance is estimated from prior residuals at that fixed coefficient.
  Covariance forecasts are B Cov(F) B' plus the spatial residual covariance.
  Mean forecasts are prior mean excess returns. Raw covariance uses the same window.
- The full sample-residual FF covariance reconstructs raw sample covariance under
  OLS orthogonality; their equal scores are a useful independent consistency check.
- The first daily return of each year is excluded: its interval can start before
  a December 31 after-close filing. Filing dates have no intraday timestamp.
- Missing future observations remove dates identically for every approach, never
  firms when forming the network; removed dates are recorded in sample JSON files.
  Thus scores condition on common observed dates and omit missing outcomes.

## Interpretation and limitations

This is a retrospective public-data experiment on current survivors. Checkpoints
were released after some evaluated dates; their pretraining provenance is not a
verified historical information set. The research pipeline prevents panel look-ahead,
but does not establish absence of checkpoint pretraining contamination.

The raw SEC snapshot schema is broad, not a complete universe of economically
harmonized accounting ratios. Company-specific extension tags and segment facts
are outside companyfacts. Dividend nonpayers and firms missing strict debt histories
are excluded from this matched comparison; the larger acquired universe is not
the estimation sample. Yahoo share-class alignment remains a limitation.

Daily Gaussian densities are working models; serial dependence, changing volatility,
and selecting among many encoders prevent treating likelihood differences as
conventional significance tests. No chi-square p-values are attached to nonnested
network comparisons. A boundary flag means |lambda| >= 0.985 within (-0.99, 0.99).

See `comparison.csv` for the separate calibration ML likelihood and normalized score,
`annual-scores.csv` for diagnostics, `panel-coverage.csv` for sample sizes, and
`distances/<year>/` and `weights/<year>/` for labeled matrices. The geometry audit
checks those matrices and reports effective neighbor counts. Reproduce with
`just python-panel`; model readouts and characteristics are cached.
