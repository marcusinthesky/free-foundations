# Panel design `four`

Characteristics: market_cap_assets, market_to_book, dividend_yield, debt_maturity. Network history: 3 annual snapshots; cohort requires complete, nonconstant 3-year histories. All rows score the same 87,351 held-out firm-days (2020-2025).
One spatial coefficient per network, kernel and innovation arm is fitted on
2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint
Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;
higher is better. Columns are kernel/innovation; `correlation` imposes prior raw
sample variances on every row so only implied correlations differ.

## Cohorts

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

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | fernandez | -46.83 | -71.47 | -74.96 | -24.82 | -63.45 |
| `fernandez_market_to_book` | fernandez | -99.11 | -148.82 | -144.51 | -70.14 | -135.33 |
| `fernandez_dividend_yield` | fernandez | +6.70 | -26.62 | -48.60 | -0.55 | -5.63 |
| `fernandez_debt_maturity` | fernandez | -92.44 | -78.34 | -58.47 | -33.85 | -36.69 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -6.00 | -0.00 | +0.00 |
| `histories__direct` | classical | -32.49 | -37.04 | -43.61 | -49.81 | -25.99 |
| `histories__mahalanobis_lw` | classical | -136.59 | -179.46 | -28.69 | -22.96 | -105.51 |
| `histories__euclidean` | classical | -125.69 | -190.40 | -49.06 | -43.77 | -131.81 |
| `histories__direct_no_indicators` | classical | -14.66 | -41.62 | -33.46 | -44.63 | -26.00 |
| `histories__euclidean_no_indicators` | classical | -125.69 | -190.40 | -49.06 | -43.77 | -131.81 |
| `histories__pca16` | control | -33.59 | -39.97 | -47.14 | -53.57 | -27.26 |
| `histories__autoencoder` | control | -40.89 | -51.42 | -79.51 | -77.24 | -38.23 |
| `histories__random_autoencoder` | control | -46.03 | -42.34 | -62.29 | -64.74 | -32.90 |
| `histories__supervised_mlp16` | task | -47.88 | -31.83 | -77.55 | -31.23 | +2.08 |
| `histories__tabpfn_fast__late` | task | -12.54 | +15.74 | +89.41 | +80.91 | +23.49 |
| `histories__tabpfn_full__late` | task | -7.99 | +21.35 | +70.06 | +64.67 | +27.84 |
| `histories__tabfm__early_concat` | state | +18.45 | +37.80 | +129.93 | +179.71 | +41.67 |
| `histories__tabfm__early_mean` | state | +19.02 | +38.35 | +131.06 | +179.50 | +42.01 |
| `histories__tabfm__late` | task | -30.14 | -9.36 | +129.10 | +135.48 | -0.91 |
| `histories__tabfm__early_concat_labelnull` | state | -37.29 | -28.10 | +8.06 | +10.30 | -17.36 |
| `histories__exaone__late` | task | -9.79 | +21.61 | +110.03 | +90.30 | +26.69 |
| `histories__exaone__item_first_concat` | state | -53.65 | -40.15 | +10.77 | +4.87 | -29.32 |
| `histories__exaone__item_first_mean` | state | -53.57 | -40.09 | +8.92 | +2.40 | -29.28 |
| `histories__exaone__item_last_concat` | task | -20.51 | +4.06 | +125.54 | +144.63 | +9.50 |
| `broad__direct` | classical | -14.40 | -0.01 | -10.43 | +166.05 | +7.36 |
| `broad__mahalanobis_lw` | classical | -107.40 | -183.66 | -20.69 | +24.05 | -51.86 |
| `broad__euclidean` | classical | +300.44 | +216.47 | +5.95 | +165.48 | +475.30 |
| `broad__direct_no_indicators` | classical | -9.37 | +3.00 | -8.36 | +77.14 | +8.18 |
| `broad__euclidean_no_indicators` | classical | +31.15 | -23.69 | +28.54 | +125.02 | +131.80 |
| `broad__direct_no_size` | classical | -14.40 | +0.28 | -10.09 | +158.24 | +7.17 |
| `broad__euclidean_no_size` | classical | +259.36 | +187.68 | +6.89 | +167.43 | +439.65 |
| `broad__pca16` | control | +40.41 | +58.78 | +43.22 | +110.57 | +56.07 |
| `broad__autoencoder` | control | +38.47 | +58.86 | +50.64 | +109.03 | +58.68 |
| `broad__random_autoencoder` | control | -32.37 | -28.99 | -29.57 | -34.22 | -22.56 |
| `broad__supervised_mlp16` | task | -10.57 | +57.80 | +59.75 | +72.41 | +57.33 |
| `broad__tabpfn_fast__late` | task | -11.82 | +12.13 | +79.37 | +72.73 | +18.47 |
| `broad__tabpfn_full__late` | task | -3.13 | +20.80 | +69.86 | +63.35 | +27.48 |
| `broad__tabfm__early_concat` | state | +10.97 | +36.47 | +130.91 | +228.84 | +41.80 |
| `broad__tabfm__early_mean` | state | +13.12 | +39.34 | +138.92 | +236.22 | +43.95 |
| `broad__tabfm__late` | task | -29.95 | -10.20 | +128.39 | +156.69 | -1.77 |
| `broad__tabfm__early_concat_labelnull` | state | -37.39 | -22.57 | +41.18 | +73.74 | -16.07 |
| `broad__exaone__late` | task | -8.47 | +20.85 | +95.16 | +80.05 | +25.00 |
| `broad__exaone__item_first_concat` | state | -53.67 | -40.11 | +41.18 | +44.75 | -29.26 |
| `broad__exaone__item_first_mean` | state | -53.60 | -40.02 | +41.13 | +43.94 | -29.16 |
| `broad__exaone__item_last_concat` | task | -15.47 | +6.37 | +118.47 | +146.74 | +11.64 |
| `metrics__direct` | classical | +2.79 | +23.91 | +7.48 | +287.60 | +22.20 |
| `metrics__mahalanobis_lw` | classical | +151.35 | +86.11 | +10.08 | +129.21 | +84.42 |
| `metrics__euclidean` | classical | +426.44 | +467.96 | +18.46 | +203.64 | +517.58 |
| `metrics__direct_no_indicators` | classical | +33.51 | +74.97 | +39.36 | +397.19 | +59.00 |
| `metrics__euclidean_no_indicators` | classical | +801.55 | +948.69 | +95.26 | +315.67 | +683.60 |
| `metrics__direct_no_size` | classical | +3.15 | +24.86 | +8.44 | +267.85 | +22.23 |
| `metrics__euclidean_no_size` | classical | +278.43 | +301.23 | +19.29 | +191.15 | +345.43 |
| `metrics__direct_no_changes` | classical | +13.12 | +33.49 | +15.38 | +291.91 | +29.54 |
| `metrics__euclidean_no_changes` | classical | +541.21 | +534.07 | +21.34 | +194.26 | +564.37 |
| `metrics__pca16` | control | +61.32 | +72.38 | +54.83 | +135.94 | +80.49 |
| `metrics__autoencoder` | control | +52.01 | +69.67 | +61.57 | +143.15 | +90.07 |
| `metrics__random_autoencoder` | control | -36.33 | -19.96 | -22.40 | -29.47 | -25.46 |
| `metrics__supervised_mlp16` | task | +7.23 | +15.77 | +23.52 | +31.73 | +21.42 |
| `metrics__tabpfn_fast__late` | task | -13.07 | +12.16 | +81.44 | +73.52 | +18.11 |
| `metrics__tabpfn_full__late` | task | -12.55 | +10.31 | +44.65 | +40.44 | +18.57 |
| `metrics__tabfm__early_concat` | state | +4.19 | +31.92 | +148.12 | +281.68 | +41.08 |
| `metrics__tabfm__early_mean` | state | +5.16 | +32.58 | +152.50 | +281.56 | +41.90 |
| `metrics__tabfm__late` | task | -30.88 | -11.25 | +127.59 | +150.86 | -2.36 |
| `metrics__tabfm__early_concat_labelnull` | state | -44.96 | -28.43 | +78.10 | +106.60 | -18.63 |
| `metrics__exaone__late` | task | -9.53 | +17.83 | +98.34 | +80.00 | +20.36 |
| `metrics__exaone__item_first_concat` | state | -53.70 | -40.18 | +0.24 | +3.12 | -29.34 |
| `metrics__exaone__item_first_mean` | state | -53.67 | -40.14 | -8.34 | +0.32 | -29.30 |
| `metrics__exaone__item_last_concat` | task | -14.91 | +7.38 | +137.47 | +174.05 | +9.81 |
| `histories@income_assets__direct` | classical | -33.53 | -36.68 | -44.89 | -49.80 | -25.53 |
| `histories@income_assets__mahalanobis_lw` | classical | -138.90 | -181.30 | -27.05 | -20.87 | -123.33 |
| `histories@income_assets__euclidean` | classical | -130.86 | -188.33 | -54.12 | -46.61 | -123.12 |
| `histories@income_assets__direct_no_indicators` | classical | -14.92 | -38.72 | -31.39 | -41.74 | -23.42 |
| `histories@income_assets__euclidean_no_indicators` | classical | -130.86 | -188.33 | -54.12 | -46.61 | -123.12 |
| `histories@income_assets__pca16` | control | -34.86 | -40.12 | -49.69 | -54.62 | -27.03 |
| `histories@income_assets__autoencoder` | control | -42.69 | -55.25 | -89.27 | -81.29 | -39.27 |
| `histories@income_assets__random_autoencoder` | control | -45.78 | -40.71 | -63.45 | -64.20 | -31.53 |
| `histories@income_assets__supervised_mlp16` | task | -2.17 | +9.65 | +3.34 | +9.56 | +17.64 |
| `histories@income_assets__tabpfn_fast__late` | task | -22.50 | -3.31 | +94.19 | +94.81 | +3.97 |
| `histories@income_assets__tabpfn_full__late` | task | +0.60 | +22.75 | +98.04 | +96.06 | +34.03 |
| `histories@income_assets__tabfm__early_concat` | state | +26.43 | +53.79 | +124.19 | +189.63 | +59.87 |
| `histories@income_assets__tabfm__early_mean` | state | +26.94 | +54.35 | +124.87 | +189.19 | +60.14 |
| `histories@income_assets__tabfm__late` | task | -32.15 | -13.59 | +119.37 | +164.74 | -4.63 |
| `histories@income_assets__tabfm__early_concat_labelnull` | state | -31.56 | -22.29 | +31.17 | +34.17 | -10.79 |
| `histories@income_assets__exaone__late` | task | -18.69 | +5.43 | +132.12 | +120.03 | +15.53 |
| `histories@income_assets__exaone__item_first_concat` | state | -53.64 | -40.14 | +0.60 | -1.75 | -29.33 |
| `histories@income_assets__exaone__item_first_mean` | state | -53.55 | -40.08 | -3.90 | -5.05 | -29.29 |
| `histories@income_assets__exaone__item_last_concat` | task | -32.00 | -14.27 | +91.69 | +154.88 | -4.42 |
| `histories@shared_market_cap_assets__direct` | classical | -34.53 | -39.27 | -47.34 | -53.69 | -27.98 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | classical | -148.86 | -186.71 | -27.93 | -23.21 | -130.19 |
| `histories@shared_market_cap_assets__euclidean` | classical | -134.33 | -189.78 | -53.94 | -47.45 | -128.38 |
| `histories@shared_market_cap_assets__direct_no_indicators` | classical | -17.46 | -44.77 | -35.85 | -48.28 | -28.85 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | classical | -134.33 | -189.78 | -53.94 | -47.45 | -128.38 |
| `histories@shared_market_cap_assets__pca16` | control | -36.94 | -43.28 | -52.56 | -58.98 | -29.86 |
| `histories@shared_market_cap_assets__autoencoder` | control | -44.48 | -58.34 | -92.84 | -85.85 | -44.10 |
| `histories@shared_market_cap_assets__random_autoencoder` | control | -47.10 | -43.32 | -64.74 | -67.01 | -33.98 |
| `histories@shared_market_cap_assets__supervised_mlp16` | task | -41.51 | -22.21 | -58.31 | -24.33 | +10.00 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | task | -12.70 | +15.26 | +88.73 | +79.76 | +22.30 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | task | -5.92 | +22.33 | +70.87 | +66.45 | +27.10 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | state | +16.88 | +35.99 | +132.04 | +179.86 | +40.78 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | state | +17.55 | +36.69 | +133.71 | +179.60 | +41.31 |
| `histories@shared_market_cap_assets__tabfm__late` | task | -29.46 | -7.99 | +142.91 | +152.20 | -0.12 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | state | -33.96 | -23.99 | +16.96 | +22.38 | -15.88 |
| `histories@shared_market_cap_assets__exaone__late` | task | -9.81 | +23.06 | +115.26 | +95.05 | +26.73 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | state | -53.64 | -40.14 | +9.27 | +5.12 | -29.32 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | state | -53.56 | -40.07 | +9.17 | +4.94 | -29.28 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | task | -19.08 | +6.62 | +136.53 | +153.58 | +10.21 |
| `histories@shared_income_assets__direct` | classical | -34.53 | -39.27 | -47.34 | -53.69 | -27.98 |
| `histories@shared_income_assets__mahalanobis_lw` | classical | -148.86 | -186.71 | -27.93 | -23.21 | -130.19 |
| `histories@shared_income_assets__euclidean` | classical | -134.33 | -189.78 | -53.94 | -47.45 | -128.38 |
| `histories@shared_income_assets__direct_no_indicators` | classical | -17.46 | -44.77 | -35.85 | -48.28 | -28.85 |
| `histories@shared_income_assets__euclidean_no_indicators` | classical | -134.33 | -189.78 | -53.94 | -47.45 | -128.38 |
| `histories@shared_income_assets__pca16` | control | -36.94 | -43.28 | -52.56 | -58.98 | -29.86 |
| `histories@shared_income_assets__autoencoder` | control | -44.48 | -58.34 | -92.84 | -85.85 | -44.10 |
| `histories@shared_income_assets__random_autoencoder` | control | -47.10 | -43.32 | -64.74 | -67.01 | -33.98 |
| `histories@shared_income_assets__supervised_mlp16` | task | -14.97 | -8.80 | -10.71 | -7.32 | +9.74 |
| `histories@shared_income_assets__tabpfn_fast__late` | task | -24.33 | -5.88 | +83.63 | +83.46 | +2.72 |
| `histories@shared_income_assets__tabpfn_full__late` | task | -0.68 | +20.62 | +88.01 | +84.02 | +31.22 |
| `histories@shared_income_assets__tabfm__early_concat` | state | +22.27 | +45.99 | +119.91 | +186.00 | +53.71 |
| `histories@shared_income_assets__tabfm__early_mean` | state | +22.76 | +46.47 | +120.40 | +185.21 | +53.96 |
| `histories@shared_income_assets__tabfm__late` | task | -33.70 | -15.81 | +110.15 | +155.79 | -7.13 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | state | -33.96 | -23.99 | +16.96 | +22.38 | -15.88 |
| `histories@shared_income_assets__exaone__late` | task | -22.35 | -0.41 | +101.87 | +91.54 | +7.13 |
| `histories@shared_income_assets__exaone__item_first_concat` | state | -53.64 | -40.14 | +9.27 | +5.12 | -29.32 |
| `histories@shared_income_assets__exaone__item_first_mean` | state | -53.56 | -40.07 | +9.17 | +4.94 | -29.28 |
| `histories@shared_income_assets__exaone__item_last_concat` | task | -31.50 | -14.48 | +85.95 | +143.65 | -5.68 |
| `uniform_network` | reference | -53.74 | -40.22 | -40.22 | -40.22 | -29.38 |
| `zero_network` | reference | -208.29 | -169.57 | -169.57 | -169.57 | -107.65 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `raw_sample_covariance` | 224,819.87 | 224,819.87 |
| `ff5_mom_diagonal` | 224,657.11 | 224,672.47 |
| `ff5_mom_sample_residual_covariance` | 224,819.87 | 224,819.87 |

## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)

Summed daily differences against the joint network; 95% percentile intervals
with 21- and 63-day expected blocks. Intervals are descriptive: the approaches
were not preregistered and these years were inspected during development.

| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | -71.47 | [-128.1, -21.6] | [-137.8, -16.4] | 22.6 |
| `fernandez_market_to_book` | -148.82 | [-256.0, -72.2] | [-279.5, -56.2] | 48.4 |
| `fernandez_dividend_yield` | -26.62 | [-78.4, +14.1] | [-80.5, +19.0] | 26.4 |
| `fernandez_debt_maturity` | -78.34 | [-151.3, +1.8] | [-168.5, +22.9] | 17.3 |
| `histories__direct` | -37.04 | [-84.1, +21.7] | [-101.2, +43.1] | 46.2 |
| `histories__mahalanobis_lw` | -179.46 | [-289.1, -79.6] | [-282.0, -83.6] | 15.1 |
| `histories__euclidean` | -190.40 | [-296.9, -103.0] | [-284.8, -109.0] | 17.6 |
| `histories__direct_no_indicators` | -41.62 | [-84.3, +14.0] | [-96.6, +32.4] | 28.9 |
| `histories__euclidean_no_indicators` | -190.40 | [-296.9, -103.0] | [-284.8, -109.0] | 17.6 |
| `histories__pca16` | -39.97 | [-85.7, +16.3] | [-102.9, +37.1] | 45.6 |
| `histories__autoencoder` | -51.42 | [-96.0, -0.5] | [-113.4, +18.8] | 42.2 |
| `histories__random_autoencoder` | -42.34 | [-91.9, +19.0] | [-111.1, +41.9] | 47.9 |
| `histories__supervised_mlp16` | -31.83 | [-81.8, +25.1] | [-98.5, +44.4] | 28.6 |
| `histories__tabpfn_fast__late` | +15.74 | [-39.5, +94.0] | [-53.8, +116.3] | 54.9 |
| `histories__tabpfn_full__late` | +21.35 | [-32.3, +97.9] | [-45.2, +118.6] | 55.0 |
| `histories__tabfm__early_concat` | +37.80 | [-17.1, +115.3] | [-32.1, +136.7] | 60.1 |
| `histories__tabfm__early_mean` | +38.35 | [-16.5, +116.0] | [-31.5, +137.4] | 60.1 |
| `histories__tabfm__late` | -9.36 | [-66.0, +66.1] | [-83.8, +90.9] | 49.7 |
| `histories__tabfm__early_concat_labelnull` | -28.10 | [-76.8, +32.0] | [-93.4, +53.7] | 46.1 |
| `histories__exaone__late` | +21.61 | [-40.3, +110.5] | [-56.5, +135.5] | 54.9 |
| `histories__exaone__item_first_concat` | -40.15 | [-93.1, +24.8] | [-111.8, +47.5] | 43.2 |
| `histories__exaone__item_first_mean` | -40.09 | [-93.0, +24.9] | [-111.8, +47.5] | 43.2 |
| `histories__exaone__item_last_concat` | +4.06 | [-50.7, +77.5] | [-67.3, +101.3] | 60.7 |
| `broad__direct` | -0.01 | [-50.0, +65.0] | [-66.6, +84.9] | 45.0 |
| `broad__mahalanobis_lw` | -183.66 | [-439.3, -11.8] | [-446.9, +1.7] | 32.8 |
| `broad__euclidean` | +216.47 | [-42.5, +410.6] | [-96.6, +455.9] | 40.3 |
| `broad__direct_no_indicators` | +3.00 | [-48.7, +70.8] | [-65.2, +90.8] | 46.4 |
| `broad__euclidean_no_indicators` | -23.69 | [-236.6, +140.5] | [-277.4, +175.5] | 41.5 |
| `broad__direct_no_size` | +0.28 | [-50.1, +66.2] | [-66.7, +86.3] | 45.2 |
| `broad__euclidean_no_size` | +187.68 | [-60.2, +374.6] | [-103.4, +412.1] | 35.8 |
| `broad__pca16` | +58.78 | [+11.3, +126.6] | [+2.4, +136.1] | 36.2 |
| `broad__autoencoder` | +58.86 | [+3.9, +137.4] | [-8.2, +150.8] | 38.8 |
| `broad__random_autoencoder` | -28.99 | [-73.1, +25.5] | [-87.7, +43.6] | 2.9 |
| `broad__supervised_mlp16` | +57.80 | [-35.0, +192.2] | [-58.7, +229.1] | 57.4 |
| `broad__tabpfn_fast__late` | +12.13 | [-42.3, +89.1] | [-57.0, +111.0] | 54.7 |
| `broad__tabpfn_full__late` | +20.80 | [-33.5, +96.8] | [-47.0, +117.8] | 54.8 |
| `broad__tabfm__early_concat` | +36.47 | [-19.7, +113.6] | [-36.2, +137.5] | 61.6 |
| `broad__tabfm__early_mean` | +39.34 | [-17.7, +118.4] | [-34.3, +142.6] | 61.5 |
| `broad__tabfm__late` | -10.20 | [-67.4, +65.2] | [-85.7, +90.4] | 50.0 |
| `broad__tabfm__early_concat_labelnull` | -22.57 | [-76.5, +46.4] | [-94.6, +69.4] | 45.6 |
| `broad__exaone__late` | +20.85 | [-44.6, +115.0] | [-61.2, +140.5] | 54.0 |
| `broad__exaone__item_first_concat` | -40.11 | [-93.1, +24.8] | [-111.8, +47.5] | 43.2 |
| `broad__exaone__item_first_mean` | -40.02 | [-93.0, +24.9] | [-111.7, +47.6] | 43.2 |
| `broad__exaone__item_last_concat` | +6.37 | [-51.9, +86.9] | [-68.8, +109.6] | 54.6 |
| `metrics__direct` | +23.91 | [-31.2, +100.4] | [-48.2, +122.7] | 46.2 |
| `metrics__mahalanobis_lw` | +86.11 | [+1.7, +178.4] | [+2.4, +170.5] | 71.2 |
| `metrics__euclidean` | +467.96 | [+330.2, +608.0] | [+341.5, +598.6] | 7.4 |
| `metrics__direct_no_indicators` | +74.97 | [+2.7, +185.9] | [-16.1, +208.3] | 53.7 |
| `metrics__euclidean_no_indicators` | +948.69 | [+615.6, +1,420.0] | [+580.5, +1,457.9] | 4.9 |
| `metrics__direct_no_size` | +24.86 | [-31.4, +103.5] | [-48.3, +126.0] | 46.5 |
| `metrics__euclidean_no_size` | +301.23 | [+163.9, +432.0] | [+166.2, +433.7] | 11.6 |
| `metrics__direct_no_changes` | +33.49 | [-24.7, +115.4] | [-42.2, +137.9] | 45.8 |
| `metrics__euclidean_no_changes` | +534.07 | [+413.0, +672.2] | [+415.6, +659.8] | 29.5 |
| `metrics__pca16` | +72.38 | [+23.4, +144.5] | [+12.2, +156.2] | 42.3 |
| `metrics__autoencoder` | +69.67 | [+18.8, +140.0] | [+5.1, +157.6] | 19.8 |
| `metrics__random_autoencoder` | -19.96 | [-65.0, +35.6] | [-80.8, +55.7] | 16.6 |
| `metrics__supervised_mlp16` | +15.77 | [-58.6, +131.6] | [-74.3, +154.7] | 34.0 |
| `metrics__tabpfn_fast__late` | +12.16 | [-40.7, +87.2] | [-54.8, +108.2] | 54.4 |
| `metrics__tabpfn_full__late` | +10.31 | [-36.6, +75.7] | [-48.1, +93.2] | 46.0 |
| `metrics__tabfm__early_concat` | +31.92 | [-29.2, +117.6] | [-47.6, +142.6] | 60.4 |
| `metrics__tabfm__early_mean` | +32.58 | [-28.3, +117.8] | [-46.4, +142.8] | 60.4 |
| `metrics__tabfm__late` | -11.25 | [-68.0, +63.7] | [-86.3, +88.1] | 49.4 |
| `metrics__tabfm__early_concat_labelnull` | -28.43 | [-83.8, +41.6] | [-103.9, +65.8] | 45.1 |
| `metrics__exaone__late` | +17.83 | [-43.9, +106.4] | [-59.7, +130.3] | 53.9 |
| `metrics__exaone__item_first_concat` | -40.18 | [-93.1, +24.7] | [-111.9, +47.4] | 43.2 |
| `metrics__exaone__item_first_mean` | -40.14 | [-93.1, +24.7] | [-111.8, +47.5] | 43.2 |
| `metrics__exaone__item_last_concat` | +7.38 | [-49.3, +86.0] | [-65.9, +108.0] | 54.7 |
| `histories@income_assets__direct` | -36.68 | [-85.0, +23.7] | [-102.7, +45.2] | 64.5 |
| `histories@income_assets__mahalanobis_lw` | -181.30 | [-307.1, -76.0] | [-293.7, -83.2] | 14.3 |
| `histories@income_assets__euclidean` | -188.33 | [-294.1, -101.5] | [-281.5, -107.4] | 16.7 |
| `histories@income_assets__direct_no_indicators` | -38.72 | [-83.6, +19.7] | [-96.3, +40.2] | 32.7 |
| `histories@income_assets__euclidean_no_indicators` | -188.33 | [-294.1, -101.5] | [-281.5, -107.4] | 16.7 |
| `histories@income_assets__pca16` | -40.12 | [-86.7, +17.4] | [-104.6, +38.7] | 45.6 |
| `histories@income_assets__autoencoder` | -55.25 | [-97.5, -8.2] | [-114.2, +9.9] | 40.3 |
| `histories@income_assets__random_autoencoder` | -40.71 | [-91.4, +22.4] | [-111.0, +46.0] | 47.8 |
| `histories@income_assets__supervised_mlp16` | +9.65 | [-46.9, +92.8] | [-58.4, +110.7] | 31.2 |
| `histories@income_assets__tabpfn_fast__late` | -3.31 | [-61.6, +75.1] | [-79.7, +99.9] | 60.1 |
| `histories@income_assets__tabpfn_full__late` | +22.75 | [-38.7, +110.2] | [-55.8, +134.4] | 54.9 |
| `histories@income_assets__tabfm__early_concat` | +53.79 | [-5.1, +138.8] | [-21.2, +162.0] | 60.0 |
| `histories@income_assets__tabfm__early_mean` | +54.35 | [-4.7, +139.5] | [-20.6, +162.8] | 60.0 |
| `histories@income_assets__tabfm__late` | -13.59 | [-69.5, +59.0] | [-88.0, +83.7] | 50.0 |
| `histories@income_assets__tabfm__early_concat_labelnull` | -22.29 | [-70.6, +36.9] | [-86.8, +58.1] | 46.2 |
| `histories@income_assets__exaone__late` | +5.43 | [-56.1, +90.3] | [-74.7, +116.2] | 48.4 |
| `histories@income_assets__exaone__item_first_concat` | -40.14 | [-93.1, +24.8] | [-111.8, +47.5] | 43.2 |
| `histories@income_assets__exaone__item_first_mean` | -40.08 | [-93.0, +24.9] | [-111.7, +47.5] | 43.2 |
| `histories@income_assets__exaone__item_last_concat` | -14.27 | [-67.3, +54.5] | [-85.1, +77.8] | 45.1 |
| `histories@shared_market_cap_assets__direct` | -39.27 | [-85.0, +17.6] | [-102.4, +38.7] | 45.9 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | -186.71 | [-306.2, -83.3] | [-294.8, -89.6] | 15.1 |
| `histories@shared_market_cap_assets__euclidean` | -189.78 | [-299.6, -100.0] | [-287.0, -106.2] | 16.8 |
| `histories@shared_market_cap_assets__direct_no_indicators` | -44.77 | [-85.7, +8.1] | [-97.5, +25.2] | 28.5 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | -189.78 | [-299.6, -100.0] | [-287.0, -106.2] | 16.8 |
| `histories@shared_market_cap_assets__pca16` | -43.28 | [-87.9, +11.3] | [-105.0, +30.9] | 45.0 |
| `histories@shared_market_cap_assets__autoencoder` | -58.34 | [-98.7, -14.4] | [-115.4, +2.2] | 39.9 |
| `histories@shared_market_cap_assets__random_autoencoder` | -43.32 | [-92.3, +17.0] | [-111.3, +39.5] | 47.7 |
| `histories@shared_market_cap_assets__supervised_mlp16` | -22.21 | [-78.2, +43.8] | [-96.4, +68.2] | 7.1 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | +15.26 | [-40.6, +94.1] | [-55.4, +117.2] | 55.0 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | +22.33 | [-31.9, +99.4] | [-45.1, +120.8] | 54.8 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | +35.99 | [-20.1, +115.2] | [-35.9, +138.1] | 61.0 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | +36.69 | [-19.2, +115.9] | [-35.0, +138.8] | 61.0 |
| `histories@shared_market_cap_assets__tabfm__late` | -7.99 | [-65.4, +68.8] | [-83.6, +94.2] | 60.9 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | -23.99 | [-74.2, +39.0] | [-90.8, +60.8] | 50.9 |
| `histories@shared_market_cap_assets__exaone__late` | +23.06 | [-40.7, +113.9] | [-57.5, +139.8] | 55.2 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | -40.14 | [-93.1, +24.8] | [-111.8, +47.5] | 43.2 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | -40.07 | [-93.0, +24.9] | [-111.7, +47.6] | 43.2 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | +6.62 | [-49.7, +82.5] | [-66.5, +107.1] | 60.5 |
| `histories@shared_income_assets__direct` | -39.27 | [-85.0, +17.6] | [-102.4, +38.7] | 45.9 |
| `histories@shared_income_assets__mahalanobis_lw` | -186.71 | [-306.2, -83.3] | [-294.8, -89.6] | 15.1 |
| `histories@shared_income_assets__euclidean` | -189.78 | [-299.6, -100.0] | [-287.0, -106.2] | 16.8 |
| `histories@shared_income_assets__direct_no_indicators` | -44.77 | [-85.7, +8.1] | [-97.5, +25.2] | 28.5 |
| `histories@shared_income_assets__euclidean_no_indicators` | -189.78 | [-299.6, -100.0] | [-287.0, -106.2] | 16.8 |
| `histories@shared_income_assets__pca16` | -43.28 | [-87.9, +11.3] | [-105.0, +30.9] | 45.0 |
| `histories@shared_income_assets__autoencoder` | -58.34 | [-98.7, -14.4] | [-115.4, +2.2] | 39.9 |
| `histories@shared_income_assets__random_autoencoder` | -43.32 | [-92.3, +17.0] | [-111.3, +39.5] | 47.7 |
| `histories@shared_income_assets__supervised_mlp16` | -8.80 | [-61.5, +65.8] | [-72.1, +79.5] | 53.2 |
| `histories@shared_income_assets__tabpfn_fast__late` | -5.88 | [-61.8, +69.1] | [-79.3, +92.2] | 56.0 |
| `histories@shared_income_assets__tabpfn_full__late` | +20.62 | [-37.7, +102.7] | [-53.8, +126.2] | 55.4 |
| `histories@shared_income_assets__tabfm__early_concat` | +45.99 | [-12.0, +128.2] | [-28.8, +151.9] | 60.7 |
| `histories@shared_income_assets__tabfm__early_mean` | +46.47 | [-11.4, +128.5] | [-28.1, +152.2] | 60.7 |
| `histories@shared_income_assets__tabfm__late` | -15.81 | [-71.2, +55.6] | [-89.7, +79.4] | 50.2 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | -23.99 | [-74.2, +39.0] | [-90.8, +60.8] | 50.9 |
| `histories@shared_income_assets__exaone__late` | -0.41 | [-59.6, +80.3] | [-77.8, +105.6] | 59.6 |
| `histories@shared_income_assets__exaone__item_first_concat` | -40.14 | [-93.1, +24.8] | [-111.8, +47.5] | 43.2 |
| `histories@shared_income_assets__exaone__item_first_mean` | -40.07 | [-93.0, +24.9] | [-111.7, +47.6] | 43.2 |
| `histories@shared_income_assets__exaone__item_last_concat` | -14.48 | [-68.3, +55.1] | [-86.8, +78.5] | 45.5 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +210.9 | [+152.0, +278.1] | +59 | +32 | +42 | +45 | +16 | +18 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +229.5 | [+171.0, +307.7] | +69 | +35 | +44 | +39 | +22 | +21 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/diagonal | +202.7 | [+145.8, +272.6] | +53 | +34 | +38 | +42 | +18 | +18 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/diagonal | +244.5 | [+180.4, +327.5] | +72 | +37 | +49 | +42 | +25 | +19 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +169.4 | [+117.1, +238.4] | +76 | +20 | +29 | +23 | +11 | +9 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | -9.6 | [-44.6, +17.6] | -7 | +1 | +8 | +1 | -4 | -8 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | matched/diagonal | +156.4 | [+100.2, +207.2] | +7 | +29 | +33 | +37 | +27 | +23 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | matched/diagonal | +62.8 | [-2.4, +147.8] | +74 | +4 | -5 | -3 | -2 | -5 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | matched/diagonal | +204.8 | [+131.6, +301.5] | +96 | +25 | +37 | +26 | +11 | +11 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | matched/diagonal | +263.1 | [+187.0, +366.9] | +102 | +33 | +36 | +43 | +28 | +21 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | matched/diagonal | +155.1 | [+111.1, +205.4] | +61 | +16 | +18 | +29 | +17 | +14 |
| topology | `broad__direct` | `uniform_network` | matched/diagonal | +206.3 | [+148.3, +260.5] | +9 | +36 | +59 | +47 | +29 | +27 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | matched/diagonal | +249.9 | [+191.5, +311.3] | +59 | +29 | +43 | +45 | +41 | +33 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | matched/diagonal | -5.9 | [-50.6, +45.7] | +28 | -7 | -16 | -3 | -1 | -7 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | matched/diagonal | +152.5 | [+101.4, +207.9] | +33 | +18 | +31 | +33 | +18 | +19 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | matched/diagonal | +311.1 | [+216.5, +453.8] | +125 | +39 | +41 | +48 | +28 | +30 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | matched/diagonal | +175.1 | [+124.7, +227.8] | +36 | +27 | +45 | +37 | +17 | +13 |
| topology | `metrics__direct` | `uniform_network` | matched/diagonal | +327.8 | [+256.4, +423.0] | +76 | +47 | +72 | +60 | +36 | +37 |
| inputs (direct) | `metrics__direct` | `histories__direct` | matched/diagonal | +337.4 | [+259.9, +451.8] | +83 | +46 | +64 | +59 | +40 | +45 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +102.0 | [+53.5, +171.1] | +42 | +4 | +4 | +18 | +17 | +17 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +173.1 | [+124.3, +220.3] | +20 | +35 | +44 | +39 | +15 | +21 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +207.9 | [+159.4, +263.8] | +49 | +37 | +47 | +34 | +21 | +20 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/correlation | +183.0 | [+128.0, +241.4] | +37 | +37 | +41 | +37 | +17 | +15 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/correlation | +224.5 | [+169.8, +288.5] | +55 | +39 | +51 | +36 | +23 | +20 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +144.7 | [+104.9, +191.1] | +56 | +22 | +31 | +20 | +10 | +6 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | -6.8 | [-43.0, +21.2] | -4 | +2 | +7 | +1 | -5 | -7 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | matched/correlation | +153.6 | [+92.0, +204.3] | +3 | +30 | +35 | +34 | +25 | +26 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | matched/correlation | +29.3 | [-9.9, +73.7] | +30 | +3 | -0 | -3 | +1 | -0 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | matched/correlation | +174.9 | [+118.8, +236.6] | +66 | +27 | +39 | +25 | +8 | +9 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | matched/correlation | +260.5 | [+193.4, +350.0] | +98 | +34 | +39 | +39 | +25 | +26 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | matched/correlation | +149.2 | [+107.0, +197.7] | +59 | +18 | +20 | +25 | +14 | +14 |
| topology | `broad__direct` | `uniform_network` | matched/correlation | +226.3 | [+168.2, +292.7] | +43 | +39 | +56 | +43 | +22 | +23 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | matched/correlation | +248.6 | [+198.7, +302.1] | +58 | +32 | +45 | +41 | +35 | +37 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | matched/correlation | +40.7 | [-30.0, +142.5] | +66 | -9 | -13 | -6 | +2 | +1 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | matched/correlation | +181.9 | [+121.9, +263.1] | +66 | +22 | +33 | +30 | +14 | +17 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | matched/correlation | +336.6 | [+218.9, +524.7] | +156 | +37 | +41 | +43 | +26 | +34 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | matched/correlation | +163.9 | [+118.4, +210.9] | +33 | +28 | +45 | +30 | +16 | +12 |
| topology | `metrics__direct` | `uniform_network` | matched/correlation | +276.8 | [+204.3, +353.5] | +39 | +53 | +71 | +58 | +27 | +29 |
| inputs (direct) | `metrics__direct` | `histories__direct` | matched/correlation | +283.6 | [+210.9, +366.2] | +42 | +51 | +64 | +57 | +32 | +37 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | +116.4 | [+47.5, +225.5] | +60 | +5 | +3 | +17 | +13 | +18 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +207.5 | [+129.8, +312.6] | +72 | +28 | +27 | +49 | +18 | +14 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | +173.5 | [+124.0, +244.0] | +56 | +25 | +32 | +29 | +16 | +14 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | median/diagonal | +158.6 | [+106.0, +232.7] | +48 | +25 | +26 | +33 | +15 | +13 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | median/diagonal | +192.2 | [+136.2, +270.5] | +62 | +27 | +37 | +33 | +20 | +13 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +121.9 | [+77.1, +186.1] | +62 | +13 | +20 | +15 | +7 | +5 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | -3.4 | [-30.8, +19.4] | -3 | +1 | +8 | +1 | -3 | -7 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | median/diagonal | +71.2 | [+25.6, +110.9] | -13 | +17 | +21 | +23 | +14 | +9 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | median/diagonal | +141.3 | [+99.7, +192.7] | +51 | +20 | +29 | +22 | +12 | +7 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | median/diagonal | +151.6 | [+108.1, +205.7] | +53 | +22 | +33 | +24 | +11 | +8 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | median/diagonal | +160.5 | [+112.7, +225.2] | +59 | +22 | +29 | +27 | +16 | +9 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | median/diagonal | +89.7 | [+62.5, +120.4] | +35 | +10 | +16 | +17 | +8 | +4 |
| topology | `broad__direct` | `uniform_network` | median/diagonal | +29.8 | [+21.1, +39.0] | +4 | +6 | +7 | +7 | +4 | +2 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | median/diagonal | +124.6 | [+88.9, +160.7] | +30 | +15 | +23 | +21 | +21 | +15 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | median/diagonal | +140.6 | [+93.7, +207.3] | +56 | +16 | +26 | +21 | +12 | +10 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | median/diagonal | +138.0 | [+98.3, +191.5] | +45 | +18 | +28 | +23 | +11 | +12 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | median/diagonal | +170.5 | [+113.2, +256.2] | +72 | +22 | +27 | +24 | +13 | +13 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | median/diagonal | +70.0 | [+39.4, +101.2] | +11 | +14 | +26 | +14 | +5 | +0 |
| topology | `metrics__direct` | `uniform_network` | median/diagonal | +47.7 | [+34.4, +65.0] | +12 | +8 | +9 | +10 | +4 | +4 |
| inputs (direct) | `metrics__direct` | `histories__direct` | median/diagonal | +51.1 | [+24.9, +88.1] | +15 | +7 | +2 | +9 | +8 | +10 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +18.2 | [-5.8, +50.2] | +15 | -2 | -5 | +1 | +4 | +6 |

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical|exp | 127 | `metrics__euclidean_no_indicators` |
| diagonal|exp | 130 | `fernandez_dividend_yield`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__mahalanobis_lw`, `broad__euclidean`, `broad__direct_no_indicators`, `broad__euclidean_no_indicators`, `broad__direct_no_size`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__supervised_mlp16`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| correlation|exp | 130 | `fernandez_debt_maturity`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__mahalanobis_lw`, `broad__euclidean`, `broad__direct_no_indicators`, `broad__euclidean_no_indicators`, `broad__direct_no_size`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__supervised_mlp16`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__exaone__late`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| spherical|median | 127 | `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__item_last_concat`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean` |
| diagonal|median | 130 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__euclidean_no_indicators`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__euclidean_no_size`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_first_concat`, `histories@shared_market_cap_assets__exaone__item_first_mean`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_first_concat`, `histories@shared_income_assets__exaone__item_first_mean`, `histories@shared_income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| correlation|median | 130 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__euclidean_no_indicators`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| spherical|matched | 127 | `metrics__direct`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__direct_no_changes` |
| diagonal|matched | 130 | `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__euclidean`, `broad__euclidean_no_indicators`, `broad__direct_no_size`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| correlation|matched | 130 | `histories__tabpfn_fast__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__euclidean`, `broad__euclidean_no_indicators`, `broad__direct_no_size`, `broad__euclidean_no_size`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |

## Label-permutation placebos (exp kernel, diagonal innovations)

Each prespecified network is compared with 19 permutations P W P' restricted
within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.

| Approach | Observed | Placebo mean | Placebo max | Rank p-value |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_joint` | 224,826.68 | 224,747.66 | 224,789.83 | 0.05 |
| `histories__direct` | 224,789.63 | 224,776.23 | 224,821.37 | 0.30 |
| `histories__pca16` | 224,786.71 | 224,775.83 | 224,820.71 | 0.35 |
| `histories__tabpfn_full__late` | 224,848.03 | 224,780.63 | 224,814.69 | 0.05 |
| `histories__tabfm__early_concat` | 224,864.47 | 224,789.78 | 224,809.92 | 0.05 |

## Network concentration

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform. The matched
kernel targets the joint network's mean effective neighbours under exp each year;
the last column is the largest achieved miss, in neighbours, over all years. Matching
the mean leaves row-wise concentration and spectral structure free to differ.

| Approach | exp | median | matched | Matched miss |
| --- | ---: | ---: | ---: | ---: |
| `broad__autoencoder` | 0.941 | 0.950 | 0.870 | 5.1e-11 |
| `broad__direct` | 0.993 | 0.996 | 0.870 | 1.7e-10 |
| `broad__direct_no_indicators` | 0.985 | 0.992 | 0.870 | 9.7e-11 |
| `broad__direct_no_size` | 0.993 | 0.996 | 0.870 | 1.1e-10 |
| `broad__euclidean` | 0.167 | 0.992 | 0.870 | 2e-10 |
| `broad__euclidean_no_indicators` | 0.184 | 0.977 | 0.870 | 3.3e-10 |
| `broad__euclidean_no_size` | 0.171 | 0.992 | 0.870 | 2.8e-10 |
| `broad__exaone__item_first_concat` | 1.000 | 0.791 | 0.870 | 6.1e-11 |
| `broad__exaone__item_first_mean` | 1.000 | 0.778 | 0.870 | 1.4e-10 |
| `broad__exaone__item_last_concat` | 0.990 | 0.905 | 0.870 | 1.8e-10 |
| `broad__exaone__late` | 0.972 | 0.783 | 0.870 | 8.2e-13 |
| `broad__mahalanobis_lw` | 0.130 | 0.991 | 0.870 | 2.7e-10 |
| `broad__pca16` | 0.943 | 0.958 | 0.870 | 6.4e-11 |
| `broad__random_autoencoder` | 0.967 | 0.971 | 0.870 | 2e-11 |
| `broad__supervised_mlp16` | 0.918 | 0.907 | 0.870 | 8.1e-11 |
| `broad__tabfm__early_concat` | 0.983 | 0.937 | 0.870 | 5.7e-13 |
| `broad__tabfm__early_concat_labelnull` | 0.997 | 0.929 | 0.870 | 1.3e-10 |
| `broad__tabfm__early_mean` | 0.983 | 0.935 | 0.870 | 1.2e-10 |
| `broad__tabfm__late` | 0.995 | 0.896 | 0.870 | 2.4e-10 |
| `broad__tabpfn_fast__late` | 0.977 | 0.844 | 0.870 | 9.7e-11 |
| `broad__tabpfn_full__late` | 0.960 | 0.838 | 0.870 | 1.7e-10 |
| `fernandez_debt_maturity` | 0.623 | 0.765 | 0.870 | 1.6e-10 |
| `fernandez_dividend_yield` | 0.647 | 0.707 | 0.870 | 1.8e-10 |
| `fernandez_joint` | 0.870 | 0.928 | 0.870 | 3.8e-10 |
| `fernandez_market_cap_assets` | 0.647 | 0.714 | 0.870 | 1.7e-10 |
| `fernandez_market_to_book` | 0.643 | 0.754 | 0.870 | 9e-13 |
| `histories@income_assets__autoencoder` | 0.950 | 0.834 | 0.870 | 2.8e-10 |
| `histories@income_assets__direct` | 0.945 | 0.882 | 0.870 | 2.6e-10 |
| `histories@income_assets__direct_no_indicators` | 0.864 | 0.907 | 0.870 | 2.8e-10 |
| `histories@income_assets__euclidean` | 0.454 | 0.838 | 0.870 | 1.7e-10 |
| `histories@income_assets__euclidean_no_indicators` | 0.454 | 0.838 | 0.870 | 1.7e-10 |
| `histories@income_assets__exaone__item_first_concat` | 1.000 | 0.816 | 0.870 | 2.1e-10 |
| `histories@income_assets__exaone__item_first_mean` | 1.000 | 0.793 | 0.870 | 6.7e-11 |
| `histories@income_assets__exaone__item_last_concat` | 0.997 | 0.938 | 0.870 | 4.2e-11 |
| `histories@income_assets__exaone__late` | 0.989 | 0.851 | 0.870 | 4.8e-11 |
| `histories@income_assets__mahalanobis_lw` | 0.329 | 0.843 | 0.870 | 2.6e-12 |
| `histories@income_assets__pca16` | 0.944 | 0.880 | 0.870 | 2.1e-10 |
| `histories@income_assets__random_autoencoder` | 0.973 | 0.869 | 0.870 | 4.9e-11 |
| `histories@income_assets__supervised_mlp16` | 0.861 | 0.838 | 0.870 | 1.6e-10 |
| `histories@income_assets__tabfm__early_concat` | 0.973 | 0.930 | 0.870 | 2.1e-11 |
| `histories@income_assets__tabfm__early_concat_labelnull` | 0.993 | 0.900 | 0.870 | 2e-11 |
| `histories@income_assets__tabfm__early_mean` | 0.973 | 0.930 | 0.870 | 2.1e-11 |
| `histories@income_assets__tabfm__late` | 0.997 | 0.920 | 0.870 | 9.6e-11 |
| `histories@income_assets__tabpfn_fast__late` | 0.992 | 0.876 | 0.870 | 2.1e-10 |
| `histories@income_assets__tabpfn_full__late` | 0.976 | 0.863 | 0.870 | 2.7e-10 |
| `histories@shared_income_assets__autoencoder` | 0.950 | 0.834 | 0.870 | 2.5e-10 |
| `histories@shared_income_assets__direct` | 0.941 | 0.885 | 0.870 | 2.5e-10 |
| `histories@shared_income_assets__direct_no_indicators` | 0.861 | 0.906 | 0.870 | 2.6e-10 |
| `histories@shared_income_assets__euclidean` | 0.422 | 0.840 | 0.870 | 2.1e-10 |
| `histories@shared_income_assets__euclidean_no_indicators` | 0.422 | 0.840 | 0.870 | 2.1e-10 |
| `histories@shared_income_assets__exaone__item_first_concat` | 1.000 | 0.819 | 0.870 | 2.7e-10 |
| `histories@shared_income_assets__exaone__item_first_mean` | 1.000 | 0.796 | 0.870 | 1.4e-10 |
| `histories@shared_income_assets__exaone__item_last_concat` | 0.997 | 0.937 | 0.870 | 3.2e-10 |
| `histories@shared_income_assets__exaone__late` | 0.989 | 0.853 | 0.870 | 4.5e-11 |
| `histories@shared_income_assets__mahalanobis_lw` | 0.319 | 0.847 | 0.870 | 4.9e-11 |
| `histories@shared_income_assets__pca16` | 0.939 | 0.884 | 0.870 | 2.2e-10 |
| `histories@shared_income_assets__random_autoencoder` | 0.967 | 0.872 | 0.870 | 6.4e-11 |
| `histories@shared_income_assets__supervised_mlp16` | 0.860 | 0.840 | 0.870 | 2.5e-10 |
| `histories@shared_income_assets__tabfm__early_concat` | 0.976 | 0.929 | 0.870 | 2.6e-11 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | 0.994 | 0.893 | 0.870 | 1.8e-10 |
| `histories@shared_income_assets__tabfm__early_mean` | 0.976 | 0.928 | 0.870 | 2.7e-11 |
| `histories@shared_income_assets__tabfm__late` | 0.997 | 0.918 | 0.870 | 9.6e-11 |
| `histories@shared_income_assets__tabpfn_fast__late` | 0.991 | 0.871 | 0.870 | 1.9e-10 |
| `histories@shared_income_assets__tabpfn_full__late` | 0.974 | 0.859 | 0.870 | 1.4e-10 |
| `histories@shared_market_cap_assets__autoencoder` | 0.950 | 0.834 | 0.870 | 2.5e-10 |
| `histories@shared_market_cap_assets__direct` | 0.941 | 0.885 | 0.870 | 2.5e-10 |
| `histories@shared_market_cap_assets__direct_no_indicators` | 0.861 | 0.906 | 0.870 | 2.6e-10 |
| `histories@shared_market_cap_assets__euclidean` | 0.422 | 0.840 | 0.870 | 2.1e-10 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | 0.422 | 0.840 | 0.870 | 2.1e-10 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | 1.000 | 0.819 | 0.870 | 2.7e-10 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | 1.000 | 0.796 | 0.870 | 1.4e-10 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | 0.991 | 0.888 | 0.870 | 2.2e-10 |
| `histories@shared_market_cap_assets__exaone__late` | 0.973 | 0.776 | 0.870 | 8.7e-11 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | 0.319 | 0.847 | 0.870 | 4.9e-11 |
| `histories@shared_market_cap_assets__pca16` | 0.939 | 0.884 | 0.870 | 2.2e-10 |
| `histories@shared_market_cap_assets__random_autoencoder` | 0.967 | 0.872 | 0.870 | 6.4e-11 |
| `histories@shared_market_cap_assets__supervised_mlp16` | 0.898 | 0.765 | 0.870 | 9.8e-11 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | 0.980 | 0.917 | 0.870 | 3.4e-11 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | 0.994 | 0.893 | 0.870 | 1.8e-10 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | 0.980 | 0.916 | 0.870 | 4.7e-11 |
| `histories@shared_market_cap_assets__tabfm__late` | 0.995 | 0.871 | 0.870 | 9.5e-11 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | 0.977 | 0.835 | 0.870 | 6.1e-11 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | 0.960 | 0.838 | 0.870 | 2.3e-10 |
| `histories__autoencoder` | 0.949 | 0.834 | 0.870 | 9.7e-11 |
| `histories__direct` | 0.941 | 0.886 | 0.870 | 2.6e-10 |
| `histories__direct_no_indicators` | 0.862 | 0.907 | 0.870 | 2.6e-10 |
| `histories__euclidean` | 0.427 | 0.839 | 0.870 | 1.9e-10 |
| `histories__euclidean_no_indicators` | 0.427 | 0.839 | 0.870 | 1.9e-10 |
| `histories__exaone__item_first_concat` | 1.000 | 0.818 | 0.870 | 3.7e-10 |
| `histories__exaone__item_first_mean` | 1.000 | 0.795 | 0.870 | 9e-11 |
| `histories__exaone__item_last_concat` | 0.991 | 0.889 | 0.870 | 7.4e-12 |
| `histories__exaone__late` | 0.973 | 0.776 | 0.870 | 1.6e-10 |
| `histories__mahalanobis_lw` | 0.327 | 0.844 | 0.870 | 1.2e-10 |
| `histories__pca16` | 0.939 | 0.885 | 0.870 | 2.9e-10 |
| `histories__random_autoencoder` | 0.967 | 0.871 | 0.870 | 6.6e-11 |
| `histories__supervised_mlp16` | 0.898 | 0.771 | 0.870 | 2.4e-10 |
| `histories__tabfm__early_concat` | 0.980 | 0.920 | 0.870 | 1.3e-10 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.895 | 0.870 | 4.6e-11 |
| `histories__tabfm__early_mean` | 0.979 | 0.919 | 0.870 | 1.6e-10 |
| `histories__tabfm__late` | 0.995 | 0.871 | 0.870 | 2.1e-12 |
| `histories__tabpfn_fast__late` | 0.977 | 0.839 | 0.870 | 8.3e-11 |
| `histories__tabpfn_full__late` | 0.960 | 0.841 | 0.870 | 2.3e-10 |
| `metrics__autoencoder` | 0.946 | 0.954 | 0.870 | 2.4e-10 |
| `metrics__direct` | 0.992 | 0.995 | 0.870 | 9.6e-11 |
| `metrics__direct_no_changes` | 0.990 | 0.994 | 0.870 | 5.2e-11 |
| `metrics__direct_no_indicators` | 0.986 | 0.992 | 0.870 | 9.3e-11 |
| `metrics__direct_no_size` | 0.991 | 0.995 | 0.870 | 1.9e-11 |
| `metrics__euclidean` | 0.160 | 0.987 | 0.870 | 2.3e-10 |
| `metrics__euclidean_no_changes` | 0.214 | 0.985 | 0.870 | 6.5e-11 |
| `metrics__euclidean_no_indicators` | 0.225 | 0.967 | 0.870 | 5.3e-11 |
| `metrics__euclidean_no_size` | 0.162 | 0.986 | 0.870 | 2.9e-10 |
| `metrics__exaone__item_first_concat` | 1.000 | 0.809 | 0.870 | 2.5e-10 |
| `metrics__exaone__item_first_mean` | 1.000 | 0.780 | 0.870 | 2.4e-10 |
| `metrics__exaone__item_last_concat` | 0.991 | 0.904 | 0.870 | 1.9e-10 |
| `metrics__exaone__late` | 0.972 | 0.781 | 0.870 | 1.1e-10 |
| `metrics__mahalanobis_lw` | 0.164 | 0.985 | 0.870 | 2.1e-10 |
| `metrics__pca16` | 0.945 | 0.959 | 0.870 | 4.2e-12 |
| `metrics__random_autoencoder` | 0.960 | 0.968 | 0.870 | 2.9e-11 |
| `metrics__supervised_mlp16` | 0.923 | 0.912 | 0.870 | 2.6e-10 |
| `metrics__tabfm__early_concat` | 0.989 | 0.944 | 0.870 | 1.3e-10 |
| `metrics__tabfm__early_concat_labelnull` | 0.999 | 0.916 | 0.870 | 9.8e-11 |
| `metrics__tabfm__early_mean` | 0.988 | 0.942 | 0.870 | 3.1e-10 |
| `metrics__tabfm__late` | 0.996 | 0.891 | 0.870 | 1.4e-10 |
| `metrics__tabpfn_fast__late` | 0.977 | 0.843 | 0.870 | 2.2e-10 |
| `metrics__tabpfn_full__late` | 0.958 | 0.838 | 0.870 | 2.6e-10 |
| `uniform_network` | nan | nan | nan | nan |
| `zero_network` | nan | nan | nan | nan |

## Regression check against the original panel

31 unchanged approaches were rescored under the exp kernel and spherical
innovations; the largest absolute held-out difference is 2.87e-08.

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
