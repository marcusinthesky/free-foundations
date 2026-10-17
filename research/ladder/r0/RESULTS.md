# R0: practical replication of Fernández (2011) on US data

Stage one: robust MM CAPM betas (robustbase `lmrob`, MM) from 40 quarterly excess
returns, 2016-2025. Stage two: median quarterly excess return on beta, no intercept.
Networks: Spearman chord distances between 2015-2024 annual characteristic histories,
exp(-d), row-normalized, zero diagonal (primary). See
[the replication manifest](replication-manifest.md) for every substitution.

`common_four` is the faithful design (one sample, every network on it).
`coverage_*` tables use each characteristic's maximal cohort; their columns
are not comparable with each other. These are in-sample descriptive fits.

| Table | Firms |
| --- | ---: |
| common_four | 33 |
| common_three | 395 |
| coverage_market_cap_assets | 653 |
| coverage_market_to_book | 490 |
| coverage_dividend_yield | 571 |
| coverage_debt_maturity | 62 |

## common_four

Least squares: premium 0.0303 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.019, AIC -132.53.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| market_cap_assets | 0.016 (0.016) | spatial_lag_iv | 0.0065 (0.494) | 0.802 (0.005) | 0.020 | 0.000 | — | False |
| market_cap_assets | 0.016 (0.016) | spatial_error_ml | 0.0096 (0.281) | 0.805 (0.000) | 0.012 | 0.000 | -133.48 | False |
| market_cap_assets | 0.016 (0.016) | spatial_lag_ml | 0.0127 (0.065) | 0.591 (0.006) | 0.006 | 0.006 | -135.51 | False |
| market_to_book | 0.025 (0.006) | spatial_lag_iv | 0.0063 (0.507) | 0.807 (0.005) | 0.024 | 0.000 | — | False |
| market_to_book | 0.025 (0.006) | spatial_error_ml | 0.0094 (0.288) | 0.810 (0.000) | 0.012 | 0.002 | -133.87 | False |
| market_to_book | 0.025 (0.006) | spatial_lag_ml | 0.0123 (0.071) | 0.606 (0.005) | 0.008 | 0.008 | -135.78 | False |
| dividend_yield | -0.001 (0.214) | spatial_lag_iv | 0.0059 (0.537) | 0.833 (0.004) | 0.045 | 0.004 | — | False |
| dividend_yield | -0.001 (0.214) | spatial_error_ml | 0.0091 (0.300) | 0.810 (0.000) | 0.020 | 0.000 | -132.93 | False |
| dividend_yield | -0.001 (0.214) | spatial_lag_ml | 0.0132 (0.058) | 0.584 (0.007) | 0.008 | 0.005 | -135.24 | False |
| debt_maturity | 0.015 (0.005) | spatial_lag_iv | 0.0074 (0.424) | 0.799 (0.005) | 0.023 | 0.000 | — | False |
| debt_maturity | 0.015 (0.005) | spatial_error_ml | 0.0102 (0.236) | 0.817 (0.000) | 0.013 | 0.002 | -133.55 | False |
| debt_maturity | 0.015 (0.005) | spatial_lag_ml | 0.0129 (0.060) | 0.605 (0.004) | 0.008 | 0.007 | -135.68 | False |

## common_three

Least squares: premium 0.0309 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.071, AIC -1759.75.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| market_cap_assets | 0.070 (0.000) | spatial_lag_iv | 0.0138 (0.000) | 0.599 (0.000) | 0.000 | 0.123 | — | False |
| market_cap_assets | 0.070 (0.000) | spatial_error_ml | 0.0141 (0.000) | 0.957 (0.000) | 0.000 | 0.153 | -1836.12 | False |
| market_cap_assets | 0.070 (0.000) | spatial_lag_ml | 0.0114 (0.000) | 0.684 (0.000) | 0.000 | 0.142 | -1830.30 | False |
| market_to_book | 0.065 (0.000) | spatial_lag_iv | 0.0136 (0.000) | 0.603 (0.000) | 0.000 | 0.118 | — | False |
| market_to_book | 0.065 (0.000) | spatial_error_ml | 0.0138 (0.000) | 0.952 (0.000) | 0.000 | 0.142 | -1832.61 | False |
| market_to_book | 0.065 (0.000) | spatial_lag_ml | 0.0116 (0.000) | 0.673 (0.000) | 0.000 | 0.132 | -1828.08 | False |
| dividend_yield | 0.045 (0.000) | spatial_lag_iv | 0.0135 (0.000) | 0.616 (0.000) | 0.000 | 0.101 | — | False |
| dividend_yield | 0.045 (0.000) | spatial_error_ml | 0.0137 (0.000) | 0.953 (0.000) | 0.000 | 0.113 | -1821.13 | False |
| dividend_yield | 0.045 (0.000) | spatial_lag_ml | 0.0124 (0.000) | 0.653 (0.000) | 0.000 | 0.105 | -1820.73 | False |

## coverage_market_cap_assets

Least squares: premium 0.0314 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.084, AIC -2837.74.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| market_cap_assets | 0.057 (0.000) | spatial_lag_iv | 0.0150 (0.000) | 0.568 (0.000) | 0.000 | 0.129 | — | False |
| market_cap_assets | 0.057 (0.000) | spatial_error_ml | 0.0151 (0.000) | 0.965 (0.000) | 0.000 | 0.155 | -2949.43 | False |
| market_cap_assets | 0.057 (0.000) | spatial_lag_ml | 0.0128 (0.000) | 0.645 (0.000) | 0.000 | 0.143 | -2938.81 | False |

## coverage_market_to_book

Least squares: premium 0.0324 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.100, AIC -2130.22.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| market_to_book | 0.052 (0.000) | spatial_lag_iv | 0.0171 (0.000) | 0.520 (0.000) | 0.000 | 0.137 | — | False |
| market_to_book | 0.052 (0.000) | spatial_error_ml | 0.0172 (0.000) | 0.953 (0.000) | 0.000 | 0.162 | -2201.30 | False |
| market_to_book | 0.052 (0.000) | spatial_lag_ml | 0.0149 (0.000) | 0.592 (0.000) | 0.000 | 0.147 | -2193.62 | False |

## coverage_dividend_yield

Least squares: premium 0.0299 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.057, AIC -2545.58.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| dividend_yield | 0.039 (0.000) | spatial_lag_iv | 0.0122 (0.000) | 0.640 (0.000) | 0.000 | 0.079 | — | False |
| dividend_yield | 0.039 (0.000) | spatial_error_ml | 0.0124 (0.000) | 0.959 (0.000) | 0.000 | 0.088 | -2630.53 | False |
| dividend_yield | 0.039 (0.000) | spatial_lag_ml | 0.0114 (0.000) | 0.668 (0.000) | 0.000 | 0.082 | -2630.34 | False |

## coverage_debt_maturity

Least squares: premium 0.0296 (p 0.000), Shapiro-Wilk p 0.000, pseudo-R² 0.009, AIC -258.70.

| Network | Moran I (p) | Model | Premium (p) | Coefficient (p) | SW p | Pseudo-R² | AIC | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| debt_maturity | 0.050 (0.000) | spatial_lag_iv | 0.0043 (0.466) | 0.884 (0.000) | 0.039 | 0.001 | — | False |
| debt_maturity | 0.050 (0.000) | spatial_error_ml | 0.0053 (0.357) | 0.897 (0.000) | 0.029 | 0.000 | -271.68 | False |
| debt_maturity | 0.050 (0.000) | spatial_lag_ml | 0.0081 (0.065) | 0.751 (0.000) | 0.014 | 0.002 | -273.97 | False |

## Sensitivity: literal self-links and median-scaled kernel (SEM-ML)

| Table | Network | Kernel | Self-links | Premium | λ | Boundary |
| --- | --- | --- | --- | ---: | ---: | --- |
| common_four | market_cap_assets | exp | True | 0.0098 | 0.820 | False |
| common_four | market_cap_assets | median | False | 0.0098 | 0.807 | False |
| common_four | market_cap_assets | median | True | 0.0099 | 0.819 | False |
| common_four | market_to_book | exp | True | 0.0098 | 0.824 | False |
| common_four | market_to_book | median | False | 0.0098 | 0.811 | False |
| common_four | market_to_book | median | True | 0.0099 | 0.821 | False |
| common_four | dividend_yield | exp | True | 0.0093 | 0.826 | False |
| common_four | dividend_yield | median | False | 0.0097 | 0.809 | False |
| common_four | dividend_yield | median | True | 0.0098 | 0.821 | False |
| common_four | debt_maturity | exp | True | 0.0104 | 0.833 | False |
| common_four | debt_maturity | median | False | 0.0104 | 0.815 | False |
| common_four | debt_maturity | median | True | 0.0104 | 0.827 | False |
| common_three | market_cap_assets | exp | True | 0.0141 | 0.957 | False |
| common_three | market_cap_assets | median | False | 0.0141 | 0.953 | False |
| common_three | market_cap_assets | median | True | 0.0141 | 0.954 | False |
| common_three | market_to_book | exp | True | 0.0138 | 0.952 | False |
| common_three | market_to_book | median | False | 0.0139 | 0.950 | False |
| common_three | market_to_book | median | True | 0.0139 | 0.950 | False |
| common_three | dividend_yield | exp | True | 0.0137 | 0.954 | False |
| common_three | dividend_yield | median | False | 0.0138 | 0.951 | False |
| common_three | dividend_yield | median | True | 0.0138 | 0.951 | False |
| coverage_market_cap_assets | market_cap_assets | exp | True | 0.0151 | 0.965 | False |
| coverage_market_cap_assets | market_cap_assets | median | False | 0.0152 | 0.962 | False |
| coverage_market_cap_assets | market_cap_assets | median | True | 0.0152 | 0.962 | False |
| coverage_market_to_book | market_to_book | exp | True | 0.0172 | 0.954 | False |
| coverage_market_to_book | market_to_book | median | False | 0.0173 | 0.950 | False |
| coverage_market_to_book | market_to_book | median | True | 0.0173 | 0.951 | False |
| coverage_dividend_yield | dividend_yield | exp | True | 0.0124 | 0.959 | False |
| coverage_dividend_yield | dividend_yield | median | False | 0.0125 | 0.958 | False |
| coverage_dividend_yield | dividend_yield | median | True | 0.0125 | 0.958 | False |
| coverage_debt_maturity | debt_maturity | exp | True | 0.0053 | 0.903 | False |
| coverage_debt_maturity | debt_maturity | median | False | 0.0054 | 0.897 | False |
| coverage_debt_maturity | debt_maturity | median | True | 0.0054 | 0.901 | False |

## Generated-beta bootstrap (W fixed)

Quarters resampled jointly for returns and factors (stationary bootstrap,
expected block four quarters), MM betas and medians recomputed, 199 valid replicates.

| Table | Network | Parameter | Bootstrap SE | 95% interval |
| --- | --- | --- | ---: | --- |
| common_four | market_cap_assets | iv_intensity | 0.6503 | [0.1234, 1.7640] |
| common_four | market_cap_assets | iv_premium | 0.0174 | [-0.0171, 0.0454] |
| common_four | market_cap_assets | ols_premium | 0.0112 | [0.0119, 0.0537] |
| common_four | market_cap_assets | sem_intensity | 0.7784 | [-0.9900, 0.8706] |
| common_four | market_cap_assets | sem_premium | 0.0191 | [-0.0140, 0.0556] |
| common_four | market_to_book | iv_intensity | 0.6171 | [0.1270, 1.6852] |
| common_four | market_to_book | iv_premium | 0.0174 | [-0.0185, 0.0435] |
| common_four | market_to_book | ols_premium | 0.0112 | [0.0119, 0.0537] |
| common_four | market_to_book | sem_intensity | 0.7451 | [-0.9900, 0.8712] |
| common_four | market_to_book | sem_premium | 0.0193 | [-0.0150, 0.0551] |
| common_four | dividend_yield | iv_intensity | 0.7504 | [0.1239, 1.9226] |
| common_four | dividend_yield | iv_premium | 0.0184 | [-0.0192, 0.0450] |
| common_four | dividend_yield | ols_premium | 0.0112 | [0.0119, 0.0537] |
| common_four | dividend_yield | sem_intensity | 0.8414 | [-0.9900, 0.8766] |
| common_four | dividend_yield | sem_premium | 0.0203 | [-0.0158, 0.0568] |
| common_four | debt_maturity | iv_intensity | 0.7725 | [0.1091, 1.8524] |
| common_four | debt_maturity | iv_premium | 0.0182 | [-0.0175, 0.0456] |
| common_four | debt_maturity | ols_premium | 0.0112 | [0.0119, 0.0537] |
| common_four | debt_maturity | sem_intensity | 0.8227 | [-0.9900, 0.8785] |
| common_four | debt_maturity | sem_premium | 0.0194 | [-0.0144, 0.0559] |
| common_three | market_cap_assets | iv_intensity | 0.3281 | [0.1400, 1.0498] |
| common_three | market_cap_assets | iv_premium | 0.0093 | [-0.0017, 0.0309] |
| common_three | market_cap_assets | ols_premium | 0.0077 | [0.0144, 0.0443] |
| common_three | market_cap_assets | sem_intensity | 0.0185 | [0.9001, 0.9634] |
| common_three | market_cap_assets | sem_premium | 0.0094 | [-0.0016, 0.0310] |
| common_three | market_to_book | iv_intensity | 0.3401 | [0.1476, 1.0669] |
| common_three | market_to_book | iv_premium | 0.0093 | [-0.0020, 0.0307] |
| common_three | market_to_book | ols_premium | 0.0077 | [0.0144, 0.0443] |
| common_three | market_to_book | sem_intensity | 0.0200 | [0.8852, 0.9593] |
| common_three | market_to_book | sem_premium | 0.0093 | [-0.0019, 0.0307] |
| common_three | dividend_yield | iv_intensity | 0.4410 | [0.1549, 1.0912] |
| common_three | dividend_yield | iv_premium | 0.0094 | [-0.0026, 0.0308] |
| common_three | dividend_yield | ols_premium | 0.0077 | [0.0144, 0.0443] |
| common_three | dividend_yield | sem_intensity | 0.0431 | [0.8068, 0.9626] |
| common_three | dividend_yield | sem_premium | 0.0094 | [-0.0024, 0.0311] |
| coverage_market_cap_assets | market_cap_assets | iv_intensity | 0.2458 | [0.1056, 1.0617] |
| coverage_market_cap_assets | market_cap_assets | iv_premium | 0.0084 | [-0.0016, 0.0309] |
| coverage_market_cap_assets | market_cap_assets | ols_premium | 0.0075 | [0.0138, 0.0437] |
| coverage_market_cap_assets | market_cap_assets | sem_intensity | 0.0164 | [0.9111, 0.9702] |
| coverage_market_cap_assets | market_cap_assets | sem_premium | 0.0084 | [-0.0015, 0.0306] |
| coverage_market_to_book | market_to_book | iv_intensity | 0.2461 | [0.1491, 0.9734] |
| coverage_market_to_book | market_to_book | iv_premium | 0.0087 | [0.0002, 0.0319] |
| coverage_market_to_book | market_to_book | ols_premium | 0.0075 | [0.0152, 0.0442] |
| coverage_market_to_book | market_to_book | sem_intensity | 0.0207 | [0.8936, 0.9600] |
| coverage_market_to_book | market_to_book | sem_premium | 0.0087 | [0.0004, 0.0316] |
| coverage_dividend_yield | dividend_yield | iv_intensity | 0.3553 | [0.1950, 1.1636] |
| coverage_dividend_yield | dividend_yield | iv_premium | 0.0085 | [-0.0035, 0.0276] |
| coverage_dividend_yield | dividend_yield | ols_premium | 0.0077 | [0.0138, 0.0439] |
| coverage_dividend_yield | dividend_yield | sem_intensity | 0.0271 | [0.8793, 0.9665] |
| coverage_dividend_yield | dividend_yield | sem_premium | 0.0086 | [-0.0035, 0.0276] |
| coverage_debt_maturity | debt_maturity | iv_intensity | 0.4485 | [0.2532, 1.6706] |
| coverage_debt_maturity | debt_maturity | iv_premium | 0.0131 | [-0.0147, 0.0317] |
| coverage_debt_maturity | debt_maturity | ols_premium | 0.0092 | [0.0114, 0.0462] |
| coverage_debt_maturity | debt_maturity | sem_intensity | 0.5988 | [-0.9900, 0.9193] |
| coverage_debt_maturity | debt_maturity | sem_premium | 0.0145 | [-0.0123, 0.0405] |
