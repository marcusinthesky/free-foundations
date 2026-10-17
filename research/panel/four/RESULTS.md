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
| `uniform_network` | reference | -53.74 | -40.22 | -40.22 | -40.22 | -29.38 |
| `zero_network` | reference | -208.29 | -169.57 | -169.57 | -169.57 | -107.65 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `histories__pca16` | 219,959.65 | 224,752.87 |
| `histories__pca16` | 224,786.71 | 224,752.87 |
| `histories__pca16` | 224,752.87 | 224,752.87 |
| `histories__pca16` | 219,962.74 | 224,752.87 |
| `histories__pca16` | 224,779.54 | 224,752.87 |
| `histories__pca16` | 224,747.74 | 224,752.87 |
| `histories__pca16` | 219,961.26 | 224,752.87 |
| `histories__pca16` | 224,773.10 | 224,752.87 |
| `histories__pca16` | 224,742.42 | 224,752.87 |
| `histories__autoencoder` | 219,952.35 | 224,741.89 |
| `histories__autoencoder` | 224,775.26 | 224,741.89 |
| `histories__autoencoder` | 224,741.89 | 224,741.89 |
| `histories__autoencoder` | 219,951.49 | 224,741.89 |
| `histories__autoencoder` | 224,747.16 | 224,741.89 |
| `histories__autoencoder` | 224,720.55 | 224,741.89 |
| `histories__autoencoder` | 219,950.90 | 224,741.89 |
| `histories__autoencoder` | 224,749.44 | 224,741.89 |
| `histories__autoencoder` | 224,720.75 | 224,741.89 |
| `histories__random_autoencoder` | 219,947.21 | 224,747.22 |
| `histories__random_autoencoder` | 224,784.34 | 224,747.22 |
| `histories__random_autoencoder` | 224,747.22 | 224,747.22 |
| `histories__random_autoencoder` | 219,944.77 | 224,747.22 |
| `histories__random_autoencoder` | 224,764.39 | 224,747.22 |
| `histories__random_autoencoder` | 224,729.91 | 224,747.22 |
| `histories__random_autoencoder` | 219,943.93 | 224,747.22 |
| `histories__random_autoencoder` | 224,761.94 | 224,747.22 |
| `histories__random_autoencoder` | 224,727.31 | 224,747.22 |
| `broad__pca16` | 220,033.65 | 224,836.19 |
| `broad__pca16` | 224,885.46 | 224,836.19 |
| `broad__pca16` | 224,836.19 | 224,836.19 |
| `broad__pca16` | 220,018.49 | 224,836.19 |
| `broad__pca16` | 224,869.90 | 224,836.19 |
| `broad__pca16` | 224,823.61 | 224,836.19 |
| `broad__pca16` | 220,083.76 | 224,836.19 |
| `broad__pca16` | 224,937.25 | 224,836.19 |
| `broad__pca16` | 224,890.42 | 224,836.19 |
| `broad__autoencoder` | 220,031.71 | 224,838.80 |
| `broad__autoencoder` | 224,885.54 | 224,838.80 |
| `broad__autoencoder` | 224,838.80 | 224,838.80 |
| `broad__autoencoder` | 220,023.64 | 224,838.80 |
| `broad__autoencoder` | 224,877.32 | 224,838.80 |
| `broad__autoencoder` | 224,831.27 | 224,838.80 |
| `broad__autoencoder` | 220,078.99 | 224,838.80 |
| `broad__autoencoder` | 224,935.71 | 224,838.80 |
| `broad__autoencoder` | 224,897.31 | 224,838.80 |
| `broad__random_autoencoder` | 219,960.87 | 224,757.57 |
| `broad__random_autoencoder` | 224,797.69 | 224,757.57 |
| `broad__random_autoencoder` | 224,757.57 | 224,757.57 |
| `broad__random_autoencoder` | 219,959.79 | 224,757.57 |
| `broad__random_autoencoder` | 224,797.10 | 224,757.57 |
| `broad__random_autoencoder` | 224,757.33 | 224,757.57 |
| `broad__random_autoencoder` | 219,968.43 | 224,757.57 |
| `broad__random_autoencoder` | 224,792.46 | 224,757.57 |
| `broad__random_autoencoder` | 224,745.89 | 224,757.57 |
| `metrics__pca16` | 220,054.56 | 224,860.61 |
| `metrics__pca16` | 224,899.06 | 224,860.61 |
| `metrics__pca16` | 224,860.61 | 224,860.61 |
| `metrics__pca16` | 220,035.71 | 224,860.61 |
| `metrics__pca16` | 224,881.50 | 224,860.61 |
| `metrics__pca16` | 224,842.57 | 224,860.61 |
| `metrics__pca16` | 220,122.20 | 224,860.61 |
| `metrics__pca16` | 224,962.62 | 224,860.61 |
| `metrics__pca16` | 224,937.74 | 224,860.61 |
| `metrics__autoencoder` | 220,045.25 | 224,870.20 |
| `metrics__autoencoder` | 224,896.35 | 224,870.20 |
| `metrics__autoencoder` | 224,870.20 | 224,870.20 |
| `metrics__autoencoder` | 220,035.44 | 224,870.20 |
| `metrics__autoencoder` | 224,888.25 | 224,870.20 |
| `metrics__autoencoder` | 224,853.68 | 224,870.20 |
| `metrics__autoencoder` | 220,115.99 | 224,870.20 |
| `metrics__autoencoder` | 224,969.83 | 224,870.20 |
| `metrics__autoencoder` | 224,960.61 | 224,870.20 |
| `metrics__random_autoencoder` | 219,956.91 | 224,754.67 |
| `metrics__random_autoencoder` | 224,806.72 | 224,754.67 |
| `metrics__random_autoencoder` | 224,754.67 | 224,754.67 |
| `metrics__random_autoencoder` | 219,954.74 | 224,754.67 |
| `metrics__random_autoencoder` | 224,804.27 | 224,754.67 |
| `metrics__random_autoencoder` | 224,754.28 | 224,754.67 |
| `metrics__random_autoencoder` | 219,951.12 | 224,754.67 |
| `metrics__random_autoencoder` | 224,797.21 | 224,754.67 |
| `metrics__random_autoencoder` | 224,731.58 | 224,754.67 |
| `histories@income_assets__pca16` | 219,958.38 | 224,753.09 |
| `histories@income_assets__pca16` | 224,786.56 | 224,753.09 |
| `histories@income_assets__pca16` | 224,753.09 | 224,753.09 |
| `histories@income_assets__pca16` | 219,960.84 | 224,753.09 |
| `histories@income_assets__pca16` | 224,776.99 | 224,753.09 |
| `histories@income_assets__pca16` | 224,746.72 | 224,753.09 |
| `histories@income_assets__pca16` | 219,959.77 | 224,753.09 |
| `histories@income_assets__pca16` | 224,772.06 | 224,753.09 |
| `histories@income_assets__pca16` | 224,742.25 | 224,753.09 |
| `histories@income_assets__autoencoder` | 219,950.55 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,771.43 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,740.85 | 224,740.85 |
| `histories@income_assets__autoencoder` | 219,947.25 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,737.40 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,715.63 | 224,740.85 |
| `histories@income_assets__autoencoder` | 219,948.85 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,745.39 | 224,740.85 |
| `histories@income_assets__autoencoder` | 224,719.36 | 224,740.85 |
| `histories@income_assets__random_autoencoder` | 219,947.45 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,785.97 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,748.60 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 219,944.53 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,763.22 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,728.46 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 219,944.35 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,762.48 | 224,748.60 |
| `histories@income_assets__random_autoencoder` | 224,727.10 | 224,748.60 |
| `raw_sample_covariance` | 224,819.87 | 224,819.87 |
| `raw_sample_covariance` | 224,819.87 | 224,819.87 |
| `ff5_mom_diagonal` | 224,657.11 | 224,672.47 |
| `ff5_mom_diagonal` | 224,672.47 | 224,672.47 |
| `ff5_mom_sample_residual_covariance` | 224,819.87 | 224,819.87 |
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

## Model confidence sets (size 0.10)

| Family | Networks | Included |
| --- | ---: | --- |
| spherical|exp | 71 | `metrics__mahalanobis_lw` |
| diagonal|exp | 71 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_joint`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__exaone__late`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late` |
| correlation|exp | 74 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__mahalanobis_lw`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__random_autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `uniform_network`, `zero_network`, `raw_sample_covariance`, `ff5_mom_diagonal`, `ff5_mom_sample_residual_covariance` |
| spherical|median | 71 | `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__item_last_concat`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__item_last_concat`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late` |
| diagonal|median | 71 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__autoencoder`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat` |
| correlation|median | 74 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_last_concat`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| spherical|matched | 71 | `metrics__direct` |
| diagonal|matched | 71 | `metrics__direct`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean` |
| correlation|matched | 74 | `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |
| controls|diagonal-exp | 72 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_debt_maturity`, `fernandez_joint`, `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__random_autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `raw_sample_covariance`, `ff5_mom_sample_residual_covariance` |

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

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform.

| Approach | exp | median | matched |
| --- | ---: | ---: | ---: |
| `broad__autoencoder` | 0.941 | 0.950 | 0.870 |
| `broad__direct` | 0.993 | 0.996 | 0.870 |
| `broad__exaone__item_first_concat` | 1.000 | 0.791 | 0.870 |
| `broad__exaone__item_first_mean` | 1.000 | 0.778 | 0.870 |
| `broad__exaone__item_last_concat` | 0.990 | 0.905 | 0.870 |
| `broad__exaone__late` | 0.972 | 0.783 | 0.870 |
| `broad__mahalanobis_lw` | 0.130 | 0.991 | 0.870 |
| `broad__pca16` | 0.943 | 0.958 | 0.870 |
| `broad__random_autoencoder` | 0.967 | 0.971 | 0.870 |
| `broad__supervised_mlp16` | 0.918 | 0.907 | 0.870 |
| `broad__tabfm__early_concat` | 0.983 | 0.937 | 0.870 |
| `broad__tabfm__early_concat_labelnull` | 0.997 | 0.929 | 0.870 |
| `broad__tabfm__early_mean` | 0.983 | 0.935 | 0.870 |
| `broad__tabfm__late` | 0.995 | 0.896 | 0.870 |
| `broad__tabpfn_fast__late` | 0.977 | 0.844 | 0.870 |
| `broad__tabpfn_full__late` | 0.960 | 0.838 | 0.870 |
| `fernandez_debt_maturity` | 0.623 | 0.765 | 0.870 |
| `fernandez_dividend_yield` | 0.647 | 0.707 | 0.870 |
| `fernandez_joint` | 0.870 | 0.928 | 0.870 |
| `fernandez_market_cap_assets` | 0.647 | 0.714 | 0.870 |
| `fernandez_market_to_book` | 0.643 | 0.754 | 0.870 |
| `histories@income_assets__autoencoder` | 0.950 | 0.834 | 0.870 |
| `histories@income_assets__direct` | 0.945 | 0.882 | 0.870 |
| `histories@income_assets__exaone__item_first_concat` | 1.000 | 0.816 | 0.870 |
| `histories@income_assets__exaone__item_first_mean` | 1.000 | 0.793 | 0.870 |
| `histories@income_assets__exaone__item_last_concat` | 0.997 | 0.938 | 0.870 |
| `histories@income_assets__exaone__late` | 0.989 | 0.851 | 0.870 |
| `histories@income_assets__mahalanobis_lw` | 0.329 | 0.843 | 0.870 |
| `histories@income_assets__pca16` | 0.944 | 0.880 | 0.870 |
| `histories@income_assets__random_autoencoder` | 0.973 | 0.869 | 0.870 |
| `histories@income_assets__supervised_mlp16` | 0.861 | 0.838 | 0.870 |
| `histories@income_assets__tabfm__early_concat` | 0.973 | 0.930 | 0.870 |
| `histories@income_assets__tabfm__early_concat_labelnull` | 0.993 | 0.900 | 0.870 |
| `histories@income_assets__tabfm__early_mean` | 0.973 | 0.930 | 0.870 |
| `histories@income_assets__tabfm__late` | 0.997 | 0.920 | 0.870 |
| `histories@income_assets__tabpfn_fast__late` | 0.992 | 0.876 | 0.870 |
| `histories@income_assets__tabpfn_full__late` | 0.976 | 0.863 | 0.870 |
| `histories__autoencoder` | 0.949 | 0.834 | 0.870 |
| `histories__direct` | 0.941 | 0.886 | 0.870 |
| `histories__exaone__item_first_concat` | 1.000 | 0.818 | 0.870 |
| `histories__exaone__item_first_mean` | 1.000 | 0.795 | 0.870 |
| `histories__exaone__item_last_concat` | 0.991 | 0.889 | 0.870 |
| `histories__exaone__late` | 0.973 | 0.776 | 0.870 |
| `histories__mahalanobis_lw` | 0.327 | 0.844 | 0.870 |
| `histories__pca16` | 0.939 | 0.885 | 0.870 |
| `histories__random_autoencoder` | 0.967 | 0.871 | 0.870 |
| `histories__supervised_mlp16` | 0.898 | 0.771 | 0.870 |
| `histories__tabfm__early_concat` | 0.980 | 0.920 | 0.870 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.895 | 0.870 |
| `histories__tabfm__early_mean` | 0.979 | 0.919 | 0.870 |
| `histories__tabfm__late` | 0.995 | 0.871 | 0.870 |
| `histories__tabpfn_fast__late` | 0.977 | 0.839 | 0.870 |
| `histories__tabpfn_full__late` | 0.960 | 0.841 | 0.870 |
| `metrics__autoencoder` | 0.946 | 0.954 | 0.870 |
| `metrics__direct` | 0.992 | 0.995 | 0.870 |
| `metrics__exaone__item_first_concat` | 1.000 | 0.809 | 0.870 |
| `metrics__exaone__item_first_mean` | 1.000 | 0.780 | 0.870 |
| `metrics__exaone__item_last_concat` | 0.991 | 0.904 | 0.870 |
| `metrics__exaone__late` | 0.972 | 0.781 | 0.870 |
| `metrics__mahalanobis_lw` | 0.164 | 0.985 | 0.870 |
| `metrics__pca16` | 0.945 | 0.959 | 0.870 |
| `metrics__random_autoencoder` | 0.960 | 0.968 | 0.870 |
| `metrics__supervised_mlp16` | 0.923 | 0.912 | 0.870 |
| `metrics__tabfm__early_concat` | 0.989 | 0.944 | 0.870 |
| `metrics__tabfm__early_concat_labelnull` | 0.999 | 0.916 | 0.870 |
| `metrics__tabfm__early_mean` | 0.988 | 0.942 | 0.870 |
| `metrics__tabfm__late` | 0.996 | 0.891 | 0.870 |
| `metrics__tabpfn_fast__late` | 0.977 | 0.843 | 0.870 |
| `metrics__tabpfn_full__late` | 0.958 | 0.838 | 0.870 |
| `uniform_network` | nan | nan | nan |
| `zero_network` | nan | nan | nan |

## Regression check against the original panel

31 unchanged approaches were rescored under the exp kernel and spherical
innovations; the largest absolute held-out difference is 2.87e-08.

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
