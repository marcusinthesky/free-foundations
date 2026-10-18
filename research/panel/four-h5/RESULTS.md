# Panel design `four-h5`

Characteristics: market_cap_assets, market_to_book, dividend_yield, debt_maturity. Network history: 5 annual snapshots; cohort requires complete, nonconstant 3- and 5-year histories. All rows score the same 66,337 held-out firm-days (2020-2025).
One spatial coefficient per network, kernel and innovation arm is fitted on
2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint
Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;
higher is better. Columns are kernel/innovation; `correlation` imposes prior raw
sample variances on every row so only implied correlations differ.

## Cohorts

| Return year | Firms | Prior complete days | Scored days | Reference firms |
| --- | ---: | ---: | ---: | ---: |
| 2016 | 32 | 756 | 251 | 706 |
| 2017 | 42 | 756 | 250 | 722 |
| 2018 | 48 | 755 | 250 | 735 |
| 2019 | 50 | 754 | 251 | 758 |
| 2020 | 47 | 754 | 252 | 778 |
| 2021 | 42 | 756 | 251 | 795 |
| 2022 | 41 | 757 | 250 | 820 |
| 2023 | 38 | 756 | 249 | 847 |
| 2024 | 43 | 753 | 251 | 866 |
| 2025 | 54 | 753 | 249 | 889 |

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | fernandez | -4.13 | +1.69 | -2.34 | -5.41 | -7.63 |
| `fernandez_market_to_book` | fernandez | -6.47 | -7.65 | -11.08 | -13.73 | -6.94 |
| `fernandez_dividend_yield` | fernandez | +7.02 | +18.46 | +6.18 | -2.82 | +2.15 |
| `fernandez_debt_maturity` | fernandez | -45.48 | -65.22 | -52.20 | -47.31 | -44.17 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -9.66 | -0.00 | +0.00 |
| `histories__direct` | classical | -25.57 | -53.42 | -64.14 | -58.98 | -8.82 |
| `histories__mahalanobis_lw` | classical | -115.66 | -203.64 | -75.98 | -56.75 | -131.58 |
| `histories__euclidean` | classical | -103.83 | -191.12 | -74.62 | -58.66 | -121.74 |
| `histories__direct_no_indicators` | classical | -13.70 | -61.37 | -50.64 | -51.95 | +1.50 |
| `histories__euclidean_no_indicators` | classical | -103.83 | -191.12 | -74.62 | -58.66 | -121.74 |
| `histories__pca16` | control | -24.39 | -54.62 | -69.24 | -59.89 | -9.15 |
| `histories__autoencoder` | control | -24.53 | -51.53 | -71.02 | -56.67 | -7.75 |
| `histories__random_autoencoder` | control | -28.93 | -56.91 | -76.27 | -66.71 | -13.09 |
| `histories__supervised_mlp16` | task | -12.70 | -8.09 | -27.52 | -15.58 | +39.81 |
| `histories__tabpfn_fast__late` | task | +1.02 | +5.30 | +65.30 | +33.55 | +34.64 |
| `histories__tabpfn_full__late` | task | +5.86 | +10.63 | +46.85 | +23.14 | +41.86 |
| `histories__tabfm__early_concat` | state | +16.78 | +12.57 | +75.30 | +62.59 | +45.96 |
| `histories__tabfm__early_mean` | state | +17.26 | +13.14 | +76.23 | +62.52 | +46.43 |
| `histories__tabfm__late` | task | -12.03 | -15.96 | +69.20 | +42.89 | +11.35 |
| `histories__tabfm__early_concat_labelnull` | state | -17.22 | -28.09 | +5.23 | -7.70 | +1.67 |
| `histories__exaone__late` | task | +2.37 | +9.60 | +70.65 | +35.28 | +37.26 |
| `histories__exaone__item_first_concat` | state | -24.56 | -35.08 | +20.03 | -6.42 | -9.42 |
| `histories__exaone__item_first_mean` | state | -24.52 | -35.03 | +22.59 | -5.22 | -9.38 |
| `histories__exaone__item_last_concat` | task | -5.01 | -5.59 | +77.46 | +51.54 | +21.86 |
| `h3__fernandez_market_cap_assets` | fernandez | -37.83 | -44.25 | -43.19 | -26.76 | -17.76 |
| `h3__fernandez_market_to_book` | fernandez | -53.44 | -95.36 | -96.56 | -47.03 | -56.22 |
| `h3__fernandez_dividend_yield` | fernandez | -7.94 | -32.75 | -53.85 | -19.31 | +3.75 |
| `h3__fernandez_debt_maturity` | fernandez | -46.77 | -69.91 | -52.06 | -37.22 | -34.96 |
| `h3__fernandez_joint` | fernandez | -23.77 | -40.53 | -35.93 | -32.21 | -15.24 |
| `h3__histories__direct` | classical | -18.17 | -37.46 | -42.33 | -37.18 | +2.54 |
| `h3__histories__mahalanobis_lw` | classical | -61.52 | -119.04 | -48.56 | -36.48 | -49.39 |
| `h3__histories__euclidean` | classical | -51.66 | -109.68 | -48.70 | -39.02 | -39.24 |
| `h3__histories__direct_no_indicators` | classical | -10.12 | -41.85 | -36.66 | -33.49 | +10.22 |
| `h3__histories__euclidean_no_indicators` | classical | -51.66 | -109.68 | -48.70 | -39.02 | -39.24 |
| `h3__histories__pca16` | control | -18.08 | -38.22 | -43.16 | -37.70 | +2.78 |
| `h3__histories__autoencoder` | control | -19.83 | -43.34 | -57.72 | -46.72 | -4.47 |
| `h3__histories__random_autoencoder` | control | -21.58 | -37.46 | -49.29 | -40.24 | -3.84 |
| `h3__histories__supervised_mlp16` | task | -2.94 | -7.86 | -41.75 | -10.25 | +44.20 |
| `h3__histories__tabpfn_fast__late` | task | +2.73 | +7.37 | +70.73 | +36.62 | +37.24 |
| `h3__histories__tabpfn_full__late` | task | +9.55 | +14.72 | +59.85 | +29.88 | +46.44 |
| `h3__histories__tabfm__early_concat` | state | +20.79 | +16.87 | +80.37 | +64.81 | +48.58 |
| `h3__histories__tabfm__early_mean` | state | +21.24 | +17.38 | +81.17 | +65.01 | +48.96 |
| `h3__histories__tabfm__late` | task | -10.13 | -12.58 | +91.66 | +56.69 | +14.50 |
| `h3__histories__tabfm__early_concat_labelnull` | state | -18.31 | -31.02 | -19.25 | -21.47 | -0.54 |
| `h3__histories__exaone__late` | task | +4.29 | +12.91 | +87.49 | +41.82 | +41.45 |
| `h3__histories__exaone__item_first_concat` | state | -24.56 | -35.08 | +13.98 | -7.74 | -9.42 |
| `h3__histories__exaone__item_first_mean` | state | -24.53 | -35.03 | +17.95 | -6.07 | -9.38 |
| `h3__histories__exaone__item_last_concat` | task | -4.13 | -3.19 | +90.79 | +56.96 | +23.77 |
| `uniform_network` | reference | -24.60 | -35.13 | -35.13 | -35.13 | -9.46 |
| `zero_network` | reference | -72.74 | -97.01 | -97.01 | -97.01 | -50.89 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `raw_sample_covariance` | 171,607.44 | 171,607.44 |
| `ff5_mom_diagonal` | 170,895.76 | 170,908.55 |
| `ff5_mom_sample_residual_covariance` | 171,607.44 | 171,607.44 |

## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)

Summed daily differences against the joint network; 95% percentile intervals
with 21- and 63-day expected blocks. Intervals are descriptive: the approaches
were not preregistered and these years were inspected during development.

| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | +1.69 | [-28.8, +26.1] | [-34.7, +31.5] | 27.3 |
| `fernandez_market_to_book` | -7.65 | [-43.8, +20.8] | [-48.4, +27.0] | 16.4 |
| `fernandez_dividend_yield` | +18.46 | [-7.6, +41.6] | [-13.5, +45.7] | 12.4 |
| `fernandez_debt_maturity` | -65.22 | [-103.0, -21.3] | [-111.2, -8.9] | 11.1 |
| `histories__direct` | -53.42 | [-82.9, -19.4] | [-90.0, -9.3] | 5.2 |
| `histories__mahalanobis_lw` | -203.64 | [-347.1, -110.0] | [-335.2, -116.0] | 21.0 |
| `histories__euclidean` | -191.12 | [-313.0, -108.2] | [-302.8, -114.9] | 14.9 |
| `histories__direct_no_indicators` | -61.37 | [-85.5, -34.8] | [-88.5, -29.4] | 23.1 |
| `histories__euclidean_no_indicators` | -191.12 | [-313.0, -108.2] | [-302.8, -114.9] | 14.9 |
| `histories__pca16` | -54.62 | [-84.3, -20.2] | [-92.0, -9.3] | 10.4 |
| `histories__autoencoder` | -51.53 | [-84.9, -11.9] | [-93.7, +0.2] | 14.0 |
| `histories__random_autoencoder` | -56.91 | [-87.4, -21.7] | [-94.6, -12.4] | 3.6 |
| `histories__supervised_mlp16` | -8.09 | [-60.1, +56.3] | [-76.1, +83.3] | 41.1 |
| `histories__tabpfn_fast__late` | +5.30 | [-41.1, +65.4] | [-53.5, +87.1] | 50.1 |
| `histories__tabpfn_full__late` | +10.63 | [-36.7, +72.5] | [-48.4, +93.5] | 49.5 |
| `histories__tabfm__early_concat` | +12.57 | [-30.1, +67.5] | [-42.8, +89.2] | 52.6 |
| `histories__tabfm__early_mean` | +13.14 | [-29.6, +68.5] | [-42.4, +90.1] | 52.5 |
| `histories__tabfm__late` | -15.96 | [-59.5, +40.7] | [-71.6, +60.8] | 43.2 |
| `histories__tabfm__early_concat_labelnull` | -28.09 | [-65.7, +19.7] | [-76.6, +36.1] | 28.8 |
| `histories__exaone__late` | +9.60 | [-40.4, +75.4] | [-54.3, +99.5] | 61.6 |
| `histories__exaone__item_first_concat` | -35.08 | [-75.0, +16.2] | [-86.3, +32.6] | 26.7 |
| `histories__exaone__item_first_mean` | -35.03 | [-74.9, +16.2] | [-86.3, +32.7] | 26.7 |
| `histories__exaone__item_last_concat` | -5.59 | [-47.2, +48.8] | [-59.3, +68.6] | 44.7 |
| `h3__fernandez_market_cap_assets` | -44.25 | [-92.7, -0.1] | [-94.7, +5.6] | 27.5 |
| `h3__fernandez_market_to_book` | -95.36 | [-169.7, -46.4] | [-174.4, -41.2] | 34.3 |
| `h3__fernandez_dividend_yield` | -32.75 | [-86.2, +17.0] | [-97.2, +31.8] | 10.1 |
| `h3__fernandez_debt_maturity` | -69.91 | [-126.7, -7.6] | [-136.5, +5.5] | 8.2 |
| `h3__fernandez_joint` | -40.53 | [-80.6, -10.4] | [-85.2, -4.5] | 32.9 |
| `h3__histories__direct` | -37.46 | [-75.1, +9.5] | [-85.9, +27.0] | 26.0 |
| `h3__histories__mahalanobis_lw` | -119.04 | [-189.3, -49.2] | [-186.5, -45.6] | 15.6 |
| `h3__histories__euclidean` | -109.68 | [-169.4, -44.9] | [-169.9, -37.7] | 6.0 |
| `h3__histories__direct_no_indicators` | -41.85 | [-78.6, +3.2] | [-86.1, +17.4] | 17.2 |
| `h3__histories__euclidean_no_indicators` | -109.68 | [-169.4, -44.9] | [-169.9, -37.7] | 6.0 |
| `h3__histories__pca16` | -38.22 | [-75.9, +8.7] | [-86.6, +26.0] | 25.6 |
| `h3__histories__autoencoder` | -43.34 | [-77.4, -2.3] | [-87.2, +12.8] | 25.2 |
| `h3__histories__random_autoencoder` | -37.46 | [-76.6, +13.1] | [-88.5, +30.9] | 19.8 |
| `h3__histories__supervised_mlp16` | -7.86 | [-57.1, +50.4] | [-71.9, +77.9] | 39.1 |
| `h3__histories__tabpfn_fast__late` | +7.37 | [-39.6, +68.8] | [-52.1, +90.1] | 50.0 |
| `h3__histories__tabpfn_full__late` | +14.72 | [-34.6, +79.8] | [-47.0, +101.9] | 59.9 |
| `h3__histories__tabfm__early_concat` | +16.87 | [-23.1, +68.3] | [-35.2, +88.9] | 48.2 |
| `h3__histories__tabfm__early_mean` | +17.38 | [-22.7, +69.0] | [-34.8, +89.8] | 48.2 |
| `h3__histories__tabfm__late` | -12.58 | [-57.4, +46.3] | [-69.8, +66.9] | 43.9 |
| `h3__histories__tabfm__early_concat_labelnull` | -31.02 | [-65.6, +12.9] | [-75.9, +27.9] | 28.7 |
| `h3__histories__exaone__late` | +12.91 | [-39.9, +82.6] | [-54.3, +108.1] | 61.5 |
| `h3__histories__exaone__item_first_concat` | -35.08 | [-74.9, +16.2] | [-86.3, +32.7] | 26.7 |
| `h3__histories__exaone__item_first_mean` | -35.03 | [-74.9, +16.2] | [-86.3, +32.7] | 26.8 |
| `h3__histories__exaone__item_last_concat` | -3.19 | [-47.3, +54.5] | [-59.6, +75.6] | 49.7 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +78.2 | [+59.6, +98.1] | +18 | +14 | +18 | +12 | +6 | +10 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +121.6 | [+84.5, +167.1] | +55 | +15 | +21 | +13 | +6 | +12 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/diagonal | +119.3 | [+80.2, +167.9] | +55 | +17 | +21 | +13 | +5 | +9 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/diagonal | +129.3 | [+89.9, +177.1] | +57 | +18 | +24 | +12 | +6 | +12 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +70.3 | [+48.2, +97.0] | +32 | +8 | +14 | +9 | +3 | +4 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | -23.9 | [-54.3, -3.2] | -22 | +1 | -0 | -0 | +1 | -5 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +81.4 | [+60.6, +107.1] | +25 | +14 | +19 | +11 | +4 | +9 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +116.5 | [+80.9, +159.1] | +53 | +15 | +22 | +11 | +4 | +11 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/correlation | +123.9 | [+81.1, +177.6] | +62 | +17 | +22 | +12 | +3 | +9 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/correlation | +122.7 | [+84.9, +166.7] | +54 | +18 | +25 | +11 | +4 | +11 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +66.3 | [+45.1, +91.1] | +30 | +8 | +15 | +8 | +2 | +3 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | -0.1 | [-8.6, +9.2] | +3 | +1 | -0 | -0 | +1 | -4 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +102.8 | [+69.2, +142.8] | +23 | +20 | +20 | +18 | +8 | +14 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | +139.4 | [+97.5, +193.9] | +62 | +19 | +23 | +15 | +7 | +14 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | median/diagonal | +151.3 | [+97.2, +226.0] | +75 | +21 | +23 | +16 | +6 | +11 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | median/diagonal | +151.6 | [+105.6, +211.2] | +67 | +22 | +26 | +15 | +7 | +15 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +70.1 | [+46.3, +101.0] | +32 | +8 | +15 | +10 | +2 | +4 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | -29.0 | [-64.2, -5.2] | -25 | +1 | -0 | -0 | +1 | -6 |

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
| `uniform_network` | 0.201 | -36 | +222,613 | -56,128 | +1,243 | -58 | -109 | +167,525 | 0.0235 |
| `fernandez_joint` | 0.242 | -21 | +167 | -214 | +508 | -33 | -66 | +342 | 0.0251 |
| `histories__direct` | 0.200 | -1 | +10 | -40 | -11 | -2 | +3 | -40 | 0.0247 |
| `histories__supervised_mlp16` | 0.198 | -2 | +14 | -79 | -2 | -9 | +3 | -75 | 0.0266 |
| `histories__tabfm__early_concat` | 0.221 | -9 | +72 | -123 | +213 | -12 | -23 | +118 | 0.0239 |
| `histories__tabfm__early_concat_labelnull` | 0.205 | -2 | +16 | -31 | +36 | -2 | -3 | +15 | 0.0236 |
| `histories__tabpfn_full__late` | 0.215 | -7 | +49 | -90 | +179 | -11 | -22 | +99 | 0.0244 |
| `histories__exaone__late` | 0.214 | -6 | +39 | -68 | +146 | -9 | -19 | +83 | 0.0240 |

### matched kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.201 | -36 | +222,613 | -56,128 | +1,243 | -58 | -109 | +167,525 | 0.0235 |
| `fernandez_joint` | 0.242 | -21 | +167 | -214 | +508 | -33 | -66 | +342 | 0.0251 |
| `histories__direct` | 0.200 | -1 | +11 | -50 | -12 | -3 | +4 | -51 | 0.0251 |
| `histories__supervised_mlp16` | 0.200 | -1 | +10 | -48 | +6 | -4 | +0 | -37 | 0.0251 |
| `histories__tabfm__early_concat` | 0.237 | -18 | +143 | -251 | +419 | -25 | -44 | +224 | 0.0251 |
| `histories__tabfm__early_concat_labelnull` | 0.215 | -7 | +65 | -136 | +158 | -12 | -11 | +58 | 0.0251 |
| `histories__tabpfn_full__late` | 0.215 | -8 | +60 | -114 | +212 | -13 | -24 | +113 | 0.0251 |
| `histories__exaone__late` | 0.215 | -8 | +58 | -107 | +203 | -13 | -23 | +109 | 0.0251 |

The uniform row shows its own parts; every other row is its difference from it.

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical/exp | 50 | `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories__direct_no_indicators`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `h3__fernandez_market_cap_assets`, `h3__fernandez_market_to_book`, `h3__fernandez_dividend_yield`, `h3__fernandez_joint`, `h3__histories__direct`, `h3__histories__euclidean`, `h3__histories__direct_no_indicators`, `h3__histories__euclidean_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat`, `zero_network` |
| diagonal/exp | 53 | `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `h3__fernandez_market_cap_assets`, `h3__fernandez_dividend_yield`, `h3__fernandez_debt_maturity`, `h3__histories__direct`, `h3__histories__direct_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| correlation/exp | 53 | `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories__direct`, `histories__direct_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `h3__fernandez_market_cap_assets`, `h3__fernandez_dividend_yield`, `h3__fernandez_debt_maturity`, `h3__histories__direct`, `h3__histories__mahalanobis_lw`, `h3__histories__euclidean`, `h3__histories__direct_no_indicators`, `h3__histories__euclidean_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| spherical/median | 50 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `histories__tabpfn_fast__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| diagonal/median | 53 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| correlation/median | 53 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| spherical/matched | 50 | `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean` |
| diagonal/matched | 53 | `fernandez_dividend_yield`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| correlation/matched | 53 | `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `h3__histories__direct_no_indicators`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |

## Label-permutation placebos (exp kernel, diagonal innovations)

Each prespecified network is compared with 19 permutations P W P' restricted
within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.

| Approach | Observed | Placebo mean | Placebo max | Rank p-value |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_joint` | 170,992.77 | 170,948.17 | 170,977.92 | 0.05 |
| `histories__direct` | 170,939.36 | 170,954.63 | 170,975.91 | 1.00 |
| `histories__pca16` | 170,938.15 | 170,955.63 | 170,976.11 | 1.00 |
| `histories__tabpfn_full__late` | 171,003.40 | 170,956.92 | 170,978.85 | 0.05 |
| `histories__tabfm__early_concat` | 171,005.34 | 170,965.19 | 170,985.54 | 0.05 |

## Network concentration

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform. The matched
kernel targets the joint network's mean effective neighbours under exp each year;
`Matched miss` is the largest achieved miss, in neighbours, over all years. Matching
the mean of 1/H_i does not match the mean row Herfindahl H, which the last two
columns compare (held-out years), nor spectral structure.

| Approach | exp | median | matched | Matched miss | Matched H | Joint exp H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `fernandez_debt_maturity` | 0.819 | 0.910 | 0.938 | 1.4e-10 | 0.0251 | 0.0251 |
| `fernandez_dividend_yield` | 0.803 | 0.888 | 0.938 | 7.2e-11 | 0.0251 | 0.0251 |
| `fernandez_joint` | 0.938 | 0.966 | 0.938 | 8.3e-11 | 0.0251 | 0.0251 |
| `fernandez_market_cap_assets` | 0.804 | 0.878 | 0.938 | 9e-11 | 0.0251 | 0.0251 |
| `fernandez_market_to_book` | 0.808 | 0.880 | 0.938 | 7.4e-11 | 0.0251 | 0.0251 |
| `h3__fernandez_debt_maturity` | 0.626 | 0.799 | 0.938 | 1.4e-10 | 0.0251 | 0.0251 |
| `h3__fernandez_dividend_yield` | 0.656 | 0.739 | 0.938 | 1.1e-11 | 0.0251 | 0.0251 |
| `h3__fernandez_joint` | 0.868 | 0.926 | 0.938 | 1.1e-10 | 0.0251 | 0.0251 |
| `h3__fernandez_market_cap_assets` | 0.650 | 0.694 | 0.938 | 1e-10 | 0.0251 | 0.0251 |
| `h3__fernandez_market_to_book` | 0.644 | 0.733 | 0.938 | 7.8e-11 | 0.0251 | 0.0251 |
| `h3__histories__autoencoder` | 0.951 | 0.837 | 0.938 | 1.9e-11 | 0.0251 | 0.0251 |
| `h3__histories__direct` | 0.942 | 0.886 | 0.938 | 1e-10 | 0.0251 | 0.0251 |
| `h3__histories__direct_no_indicators` | 0.865 | 0.909 | 0.938 | 7.6e-11 | 0.0251 | 0.0251 |
| `h3__histories__euclidean` | 0.433 | 0.835 | 0.938 | 4.3e-14 | 0.0251 | 0.0251 |
| `h3__histories__euclidean_no_indicators` | 0.433 | 0.835 | 0.938 | 4.3e-14 | 0.0251 | 0.0251 |
| `h3__histories__exaone__item_first_concat` | 1.000 | 0.819 | 0.938 | 7.7e-13 | 0.0251 | 0.0251 |
| `h3__histories__exaone__item_first_mean` | 1.000 | 0.797 | 0.938 | 1.3e-12 | 0.0251 | 0.0251 |
| `h3__histories__exaone__item_last_concat` | 0.990 | 0.884 | 0.938 | 9.1e-11 | 0.0251 | 0.0251 |
| `h3__histories__exaone__late` | 0.972 | 0.771 | 0.938 | 9.9e-14 | 0.0251 | 0.0251 |
| `h3__histories__mahalanobis_lw` | 0.335 | 0.841 | 0.938 | 2e-11 | 0.0251 | 0.0251 |
| `h3__histories__pca16` | 0.940 | 0.885 | 0.938 | 8.5e-11 | 0.0251 | 0.0251 |
| `h3__histories__random_autoencoder` | 0.967 | 0.869 | 0.938 | 7.6e-11 | 0.0251 | 0.0251 |
| `h3__histories__supervised_mlp16` | 0.895 | 0.767 | 0.938 | 5e-11 | 0.0251 | 0.0251 |
| `h3__histories__tabfm__early_concat` | 0.980 | 0.919 | 0.938 | 1.9e-12 | 0.0251 | 0.0251 |
| `h3__histories__tabfm__early_concat_labelnull` | 0.995 | 0.894 | 0.938 | 1e-11 | 0.0251 | 0.0251 |
| `h3__histories__tabfm__early_mean` | 0.980 | 0.918 | 0.938 | 1.8e-12 | 0.0251 | 0.0251 |
| `h3__histories__tabfm__late` | 0.994 | 0.865 | 0.938 | 1.2e-10 | 0.0251 | 0.0251 |
| `h3__histories__tabpfn_fast__late` | 0.977 | 0.839 | 0.938 | 3.5e-11 | 0.0251 | 0.0251 |
| `h3__histories__tabpfn_full__late` | 0.959 | 0.836 | 0.938 | 1.4e-14 | 0.0251 | 0.0251 |
| `histories__autoencoder` | 0.953 | 0.845 | 0.938 | 3.8e-11 | 0.0251 | 0.0251 |
| `histories__direct` | 0.949 | 0.907 | 0.938 | 1.3e-10 | 0.0251 | 0.0251 |
| `histories__direct_no_indicators` | 0.883 | 0.929 | 0.938 | 2.2e-11 | 0.0251 | 0.0251 |
| `histories__euclidean` | 0.345 | 0.867 | 0.938 | 9.8e-11 | 0.0251 | 0.0251 |
| `histories__euclidean_no_indicators` | 0.345 | 0.867 | 0.938 | 9.8e-11 | 0.0251 | 0.0251 |
| `histories__exaone__item_first_concat` | 1.000 | 0.812 | 0.938 | 1.2e-12 | 0.0251 | 0.0251 |
| `histories__exaone__item_first_mean` | 1.000 | 0.790 | 0.938 | 1.8e-12 | 0.0251 | 0.0251 |
| `histories__exaone__item_last_concat` | 0.990 | 0.894 | 0.938 | 8.9e-11 | 0.0251 | 0.0251 |
| `histories__exaone__late` | 0.971 | 0.774 | 0.938 | 1.3e-12 | 0.0251 | 0.0251 |
| `histories__mahalanobis_lw` | 0.237 | 0.877 | 0.938 | 6.7e-11 | 0.0251 | 0.0251 |
| `histories__pca16` | 0.948 | 0.880 | 0.938 | 1e-10 | 0.0251 | 0.0251 |
| `histories__random_autoencoder` | 0.959 | 0.890 | 0.938 | 7.9e-11 | 0.0251 | 0.0251 |
| `histories__supervised_mlp16` | 0.893 | 0.809 | 0.938 | 5.2e-11 | 0.0251 | 0.0251 |
| `histories__tabfm__early_concat` | 0.982 | 0.923 | 0.938 | 6.3e-12 | 0.0251 | 0.0251 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.899 | 0.938 | 4.1e-11 | 0.0251 | 0.0251 |
| `histories__tabfm__early_mean` | 0.982 | 0.921 | 0.938 | 6.6e-12 | 0.0251 | 0.0251 |
| `histories__tabfm__late` | 0.994 | 0.869 | 0.938 | 3.6e-11 | 0.0251 | 0.0251 |
| `histories__tabpfn_fast__late` | 0.977 | 0.841 | 0.938 | 1.4e-10 | 0.0251 | 0.0251 |
| `histories__tabpfn_full__late` | 0.957 | 0.834 | 0.938 | 5e-12 | 0.0251 | 0.0251 |
| `uniform_network` | nan | nan | nan | nan | nan | 0.0251 |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
