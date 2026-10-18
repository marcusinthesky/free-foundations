# Panel design `four-xqxo`

Characteristics: market_cap_assets, market_to_book, dividend_yield, debt_maturity. Network history: 3 annual snapshots; cohort requires complete, nonconstant 3-year histories. All rows score the same 86,851 held-out firm-days (2020-2025).
One spatial coefficient per network, kernel and innovation arm is fitted on
2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint
Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;
higher is better. Columns are kernel/innovation; `correlation` imposes prior raw
sample variances on every row so only implied correlations differ.

## Cohorts

| Return year | Firms | Prior complete days | Scored days | Reference firms |
| --- | ---: | ---: | ---: | ---: |
| 2016 | 58 | 756 | 251 | 679 |
| 2017 | 63 | 756 | 250 | 700 |
| 2018 | 64 | 554 | 250 | 740 |
| 2019 | 64 | 754 | 251 | 743 |
| 2020 | 60 | 754 | 252 | 764 |
| 2021 | 47 | 756 | 251 | 789 |
| 2022 | 48 | 757 | 250 | 812 |
| 2023 | 60 | 756 | 249 | 824 |
| 2024 | 63 | 753 | 251 | 845 |
| 2025 | 69 | 753 | 249 | 873 |

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | fernandez | -52.11 | -63.84 | -72.38 | -22.30 | -57.04 |
| `fernandez_market_to_book` | fernandez | -91.12 | -148.24 | -145.33 | -71.08 | -132.37 |
| `fernandez_dividend_yield` | fernandez | +10.70 | -23.57 | -45.25 | +0.36 | -3.13 |
| `fernandez_debt_maturity` | fernandez | -60.86 | -74.44 | -52.71 | -31.21 | -35.90 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -6.18 | +0.00 | +0.00 |
| `histories__direct` | classical | -31.10 | -38.09 | -45.23 | -51.86 | -26.83 |
| `histories__mahalanobis_lw` | classical | -111.01 | -181.00 | -31.05 | -25.92 | -109.55 |
| `histories__euclidean` | classical | -114.30 | -194.77 | -55.93 | -50.78 | -137.50 |
| `histories__direct_no_indicators` | classical | -18.09 | -39.81 | -32.32 | -43.39 | -21.94 |
| `histories__euclidean_no_indicators` | classical | -114.30 | -194.77 | -55.93 | -50.78 | -137.50 |
| `histories__pca16` | control | -31.99 | -41.07 | -48.79 | -55.73 | -27.91 |
| `histories__autoencoder` | control | -37.31 | -51.91 | -80.54 | -78.49 | -38.42 |
| `histories__random_autoencoder` | control | -41.12 | -42.89 | -62.57 | -65.25 | -33.65 |
| `histories__supervised_mlp16` | task | -40.00 | -33.56 | -86.17 | -38.06 | -0.60 |
| `histories__tabpfn_fast__late` | task | -6.90 | +14.92 | +88.59 | +80.18 | +22.22 |
| `histories__tabpfn_full__late` | task | -2.89 | +20.47 | +68.98 | +63.69 | +26.57 |
| `histories__tabfm__early_concat` | state | +17.74 | +37.43 | +130.16 | +180.59 | +39.64 |
| `histories__tabfm__early_mean` | state | +18.27 | +37.98 | +131.31 | +180.38 | +39.99 |
| `histories__tabfm__late` | task | -23.04 | -10.30 | +127.75 | +134.42 | -3.07 |
| `histories__tabfm__early_concat_labelnull` | state | -30.63 | -28.97 | +6.84 | +9.12 | -19.62 |
| `histories__exaone__late` | task | -4.46 | +20.94 | +109.35 | +89.71 | +25.40 |
| `histories__exaone__item_first_concat` | state | -42.04 | -41.15 | +10.49 | +4.60 | -30.86 |
| `histories__exaone__item_first_mean` | state | -41.99 | -41.09 | +8.93 | +2.35 | -30.82 |
| `histories__exaone__item_last_concat` | task | -14.33 | +3.28 | +125.05 | +144.06 | +7.95 |
| `uniform_network` | reference | -42.10 | -41.22 | -41.22 | -41.22 | -30.91 |
| `zero_network` | reference | -141.30 | -170.96 | -170.96 | -170.96 | -111.51 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `raw_sample_covariance` | 224,333.38 | 224,333.38 |
| `ff5_mom_diagonal` | 224,140.57 | 224,156.07 |
| `ff5_mom_sample_residual_covariance` | 224,333.38 | 224,333.38 |

## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)

Summed daily differences against the joint network; 95% percentile intervals
with 21- and 63-day expected blocks. Intervals are descriptive: the approaches
were not preregistered and these years were inspected during development.

| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | -63.84 | [-122.0, -13.7] | [-133.0, -8.1] | 22.9 |
| `fernandez_market_to_book` | -148.24 | [-255.4, -72.0] | [-279.6, -55.0] | 48.5 |
| `fernandez_dividend_yield` | -23.57 | [-75.2, +16.8] | [-78.0, +21.5] | 19.2 |
| `fernandez_debt_maturity` | -74.44 | [-148.2, +6.7] | [-165.9, +27.0] | 15.5 |
| `histories__direct` | -38.09 | [-85.3, +21.1] | [-102.8, +42.4] | 45.8 |
| `histories__mahalanobis_lw` | -181.00 | [-291.4, -79.8] | [-285.0, -84.3] | 15.4 |
| `histories__euclidean` | -194.77 | [-301.5, -107.6] | [-288.1, -113.0] | 17.7 |
| `histories__direct_no_indicators` | -39.81 | [-82.7, +15.8] | [-94.5, +34.0] | 29.5 |
| `histories__euclidean_no_indicators` | -194.77 | [-301.5, -107.6] | [-288.1, -113.0] | 17.7 |
| `histories__pca16` | -41.07 | [-87.1, +16.0] | [-104.3, +37.0] | 45.1 |
| `histories__autoencoder` | -51.91 | [-96.6, -0.8] | [-114.4, +18.9] | 41.7 |
| `histories__random_autoencoder` | -42.89 | [-92.7, +18.9] | [-111.9, +41.5] | 47.5 |
| `histories__supervised_mlp16` | -33.56 | [-83.8, +23.7] | [-100.7, +43.3] | 28.2 |
| `histories__tabpfn_fast__late` | +14.92 | [-40.4, +93.4] | [-55.1, +115.8] | 55.0 |
| `histories__tabpfn_full__late` | +20.47 | [-33.3, +96.8] | [-46.3, +118.3] | 55.1 |
| `histories__tabfm__early_concat` | +37.43 | [-17.3, +114.8] | [-32.7, +136.4] | 60.1 |
| `histories__tabfm__early_mean` | +37.98 | [-16.9, +115.6] | [-32.2, +137.0] | 60.1 |
| `histories__tabfm__late` | -10.30 | [-67.0, +65.8] | [-85.1, +90.7] | 49.7 |
| `histories__tabfm__early_concat_labelnull` | -28.97 | [-77.7, +31.6] | [-94.4, +53.7] | 46.1 |
| `histories__exaone__late` | +20.94 | [-40.9, +110.0] | [-57.3, +135.0] | 54.9 |
| `histories__exaone__item_first_concat` | -41.15 | [-94.0, +23.8] | [-112.7, +47.0] | 43.2 |
| `histories__exaone__item_first_mean` | -41.09 | [-94.0, +23.8] | [-112.6, +47.0] | 43.2 |
| `histories__exaone__item_last_concat` | +3.28 | [-51.4, +77.1] | [-68.0, +100.9] | 60.6 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +218.6 | [+160.1, +285.4] | +59 | +32 | +42 | +45 | +20 | +21 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +232.4 | [+174.3, +310.2] | +69 | +35 | +44 | +39 | +22 | +23 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/diagonal | +206.5 | [+150.2, +276.4] | +53 | +34 | +38 | +42 | +21 | +19 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/diagonal | +245.8 | [+183.2, +328.7] | +72 | +37 | +49 | +42 | +24 | +22 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +171.5 | [+119.6, +240.2] | +76 | +20 | +29 | +23 | +13 | +10 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | -10.6 | [-45.5, +16.5] | -7 | +1 | +8 | +1 | -5 | -8 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +177.8 | [+128.6, +225.2] | +20 | +35 | +44 | +39 | +17 | +24 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +206.9 | [+157.7, +262.9] | +49 | +37 | +47 | +34 | +20 | +20 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/correlation | +186.2 | [+131.7, +244.1] | +37 | +37 | +41 | +37 | +19 | +16 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/correlation | +222.1 | [+167.2, +286.9] | +55 | +39 | +51 | +36 | +21 | +20 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +146.4 | [+106.8, +192.6] | +56 | +22 | +31 | +20 | +11 | +6 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | -6.2 | [-42.6, +22.0] | -4 | +2 | +7 | +1 | -4 | -8 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +216.3 | [+138.8, +321.1] | +72 | +28 | +27 | +49 | +24 | +16 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | +175.4 | [+126.0, +245.8] | +56 | +25 | +32 | +29 | +17 | +16 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | median/diagonal | +161.2 | [+108.7, +235.3] | +48 | +25 | +26 | +33 | +17 | +13 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | median/diagonal | +192.7 | [+137.4, +271.2] | +62 | +27 | +37 | +33 | +19 | +15 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +123.3 | [+78.8, +187.2] | +62 | +13 | +20 | +15 | +9 | +5 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | -4.0 | [-31.3, +18.6] | -3 | +1 | +8 | +1 | -4 | -7 |

## Where the residual likelihood comes from

Exact split of the held-out spatial-error log-likelihood of factor residuals,
conditional on realized factors, at the frozen coefficient and prior-window
variances (Lean `Likelihood.spatial_loss`), summed over 2020-2025, minus the uniform
network's parts. `alignment` is the term linear in lambda (weighted cross products
of a firm's and its neighbours' residuals); the two `concentration` terms are
quadratic, split into the neighbours' own second moments weighted by squared
weights and their cross products. Those second moments hold common and
idiosyncratic variance together, so `concentration_own` is not a pure noise cost,
and a larger `alignment` is not by itself evidence of recovered exposures. This
split does not decompose the headline unconditional scores, which add factor
uncertainty around the prior mean. `H` is the mean row Herfindahl index.

### exp kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.260 | -63 | +290,043 | -72,286 | +2,191 | -97 | -252 | +219,537 | 0.0180 |
| `fernandez_joint` | 0.281 | -23 | +190 | -270 | +618 | -38 | -67 | +412 | 0.0211 |
| `histories__direct` | 0.271 | -9 | +34 | -60 | +96 | -14 | -18 | +27 | 0.0192 |
| `histories__supervised_mlp16` | 0.249 | +2 | -14 | -42 | -72 | -6 | +24 | -108 | 0.0200 |
| `histories__tabfm__early_concat` | 0.295 | -22 | +125 | -190 | +391 | -28 | -68 | +208 | 0.0183 |
| `histories__tabfm__early_concat_labelnull` | 0.270 | -6 | +34 | -53 | +89 | -8 | -15 | +41 | 0.0181 |
| `histories__tabpfn_full__late` | 0.284 | -15 | +84 | -135 | +334 | -23 | -63 | +182 | 0.0186 |
| `histories__exaone__late` | 0.281 | -13 | +68 | -106 | +279 | -19 | -52 | +156 | 0.0184 |

### matched kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.260 | -63 | +290,043 | -72,286 | +2,191 | -97 | -252 | +219,537 | 0.0180 |
| `fernandez_joint` | 0.281 | -23 | +190 | -270 | +618 | -38 | -67 | +412 | 0.0211 |
| `histories__direct` | 0.272 | -15 | +41 | -84 | +105 | -25 | -17 | +4 | 0.0210 |
| `histories__supervised_mlp16` | 0.249 | -8 | -17 | -32 | -47 | -21 | +22 | -103 | 0.0235 |
| `histories__tabfm__early_concat` | 0.338 | -63 | +331 | -528 | +1,039 | -88 | -176 | +515 | 0.0210 |
| `histories__tabfm__early_concat_labelnull` | 0.304 | -35 | +183 | -313 | +481 | -53 | -71 | +193 | 0.0210 |
| `histories__tabpfn_full__late` | 0.292 | -28 | +147 | -241 | +551 | -45 | -94 | +290 | 0.0210 |
| `histories__exaone__late` | 0.292 | -28 | +147 | -238 | +553 | -45 | -94 | +294 | 0.0211 |

The uniform row shows its own parts; every other row is its difference from it.

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical/exp | 26 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct_no_indicators`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat` |
| diagonal/exp | 29 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__direct_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| correlation/exp | 29 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| spherical/median | 26 | `histories__tabfm__early_mean` |
| diagonal/median | 29 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| correlation/median | 29 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| spherical/matched | 26 | `histories__tabfm__early_mean` |
| diagonal/matched | 29 | `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| correlation/matched | 29 | `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |

## Label-permutation placebos (exp kernel, diagonal innovations)

Each prespecified network is compared with 19 permutations P W P' restricted
within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.

| Approach | Observed | Placebo mean | Placebo max | Rank p-value |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_joint` | 224,311.53 | 224,234.26 | 224,279.77 | 0.05 |
| `histories__direct` | 224,273.44 | 224,262.77 | 224,315.61 | 0.30 |
| `histories__pca16` | 224,270.46 | 224,262.48 | 224,315.24 | 0.35 |
| `histories__tabpfn_full__late` | 224,332.00 | 224,264.48 | 224,297.91 | 0.05 |
| `histories__tabfm__early_concat` | 224,348.96 | 224,274.93 | 224,294.76 | 0.05 |

## Network concentration

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform. The matched
kernel targets the joint network's mean effective neighbours under exp each year;
`Matched miss` is the largest achieved miss, in neighbours, over all years. Matching
the mean of 1/H_i does not match the mean row Herfindahl H, which the last two
columns compare (held-out years), nor spectral structure.

| Approach | exp | median | matched | Matched miss | Matched H | Joint exp H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `fernandez_debt_maturity` | 0.623 | 0.765 | 0.870 | 1.6e-10 | 0.0209 | 0.0211 |
| `fernandez_dividend_yield` | 0.647 | 0.708 | 0.870 | 1.8e-10 | 0.0209 | 0.0211 |
| `fernandez_joint` | 0.870 | 0.928 | 0.870 | 3.6e-10 | 0.0211 | 0.0211 |
| `fernandez_market_cap_assets` | 0.647 | 0.714 | 0.870 | 1.7e-10 | 0.0209 | 0.0211 |
| `fernandez_market_to_book` | 0.643 | 0.754 | 0.870 | 1.7e-12 | 0.0209 | 0.0211 |
| `histories__autoencoder` | 0.950 | 0.835 | 0.870 | 9.7e-11 | 0.0210 | 0.0211 |
| `histories__direct` | 0.941 | 0.886 | 0.870 | 2.6e-10 | 0.0210 | 0.0211 |
| `histories__direct_no_indicators` | 0.862 | 0.907 | 0.870 | 2.6e-10 | 0.0210 | 0.0211 |
| `histories__euclidean` | 0.429 | 0.842 | 0.870 | 1.9e-10 | 0.0210 | 0.0211 |
| `histories__euclidean_no_indicators` | 0.429 | 0.842 | 0.870 | 1.9e-10 | 0.0210 | 0.0211 |
| `histories__exaone__item_first_concat` | 1.000 | 0.818 | 0.870 | 2.2e-10 | 0.0210 | 0.0211 |
| `histories__exaone__item_first_mean` | 1.000 | 0.795 | 0.870 | 9e-11 | 0.0210 | 0.0211 |
| `histories__exaone__item_last_concat` | 0.991 | 0.889 | 0.870 | 7.4e-12 | 0.0210 | 0.0211 |
| `histories__exaone__late` | 0.973 | 0.776 | 0.870 | 1.3e-10 | 0.0211 | 0.0211 |
| `histories__mahalanobis_lw` | 0.329 | 0.846 | 0.870 | 5.8e-11 | 0.0210 | 0.0211 |
| `histories__pca16` | 0.940 | 0.885 | 0.870 | 2.9e-10 | 0.0210 | 0.0211 |
| `histories__random_autoencoder` | 0.967 | 0.871 | 0.870 | 3.3e-10 | 0.0210 | 0.0211 |
| `histories__supervised_mlp16` | 0.898 | 0.772 | 0.870 | 2.4e-10 | 0.0235 | 0.0211 |
| `histories__tabfm__early_concat` | 0.980 | 0.920 | 0.870 | 1.3e-10 | 0.0210 | 0.0211 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.896 | 0.870 | 1.5e-12 | 0.0210 | 0.0211 |
| `histories__tabfm__early_mean` | 0.980 | 0.919 | 0.870 | 1.6e-10 | 0.0210 | 0.0211 |
| `histories__tabfm__late` | 0.995 | 0.872 | 0.870 | 7e-12 | 0.0211 | 0.0211 |
| `histories__tabpfn_fast__late` | 0.977 | 0.838 | 0.870 | 8.3e-11 | 0.0210 | 0.0211 |
| `histories__tabpfn_full__late` | 0.960 | 0.840 | 0.870 | 2.3e-10 | 0.0210 | 0.0211 |
| `uniform_network` | nan | nan | nan | nan | nan | 0.0211 |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
