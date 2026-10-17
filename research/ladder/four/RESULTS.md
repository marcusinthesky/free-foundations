# Cross-sectional ladder: `four` arm (market_cap_assets, market_to_book, dividend_yield, debt_maturity)

All rows use the same 33 firms, median quarterly excess returns 2016-2025 and
MM exposures. Each spatial row estimates one coefficient for one combined network.
Information criteria are conditional on generated exposures and W (n = firms).
Rows with equal parameter counts have identical AIC/BIC/HQIC rankings
(ΔIC = -2 ΔlogL), so the criteria add information only across nonspatial versus
spatial rows and CAPM versus FF5+Mom exposures. Not ranked against the other arm.

## CAPM exposures, SEM-ML

Nonspatial OLS: log-likelihood 68.264, AIC -132.53, BIC -129.54, HQIC -131.52.

| Network | Rung | Kernel | λ (p) | Premium (p) | logL - OLS | logL - joint | BIC | Eff. nbrs | Placebo p | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `fernandez_market_cap_assets` | r0_single | exp | 0.805 (0.000) | 0.0096 (0.281) | +1.476 | +0.031 | -128.99 | 0.897 | 0.180 | False |
| `fernandez_market_cap_assets` | r0_single | median | 0.807 (0.000) | 0.0098 (0.268) | +1.450 | +0.005 | -128.94 | 0.942 | 0.180 | False |
| `fernandez_market_cap_assets` | r0_single | matched | 0.808 (0.000) | 0.0100 (0.257) | +1.423 | -0.022 | -128.89 | 0.968 | 0.180 | False |
| `fernandez_market_to_book` | r0_single | exp | 0.810 (0.000) | 0.0094 (0.288) | +1.671 | +0.226 | -129.38 | 0.892 | 0.160 | False |
| `fernandez_market_to_book` | r0_single | median | 0.811 (0.000) | 0.0098 (0.270) | +1.587 | +0.142 | -129.21 | 0.942 | 0.160 | False |
| `fernandez_market_to_book` | r0_single | matched | 0.811 (0.000) | 0.0100 (0.258) | +1.523 | +0.078 | -129.08 | 0.968 | 0.160 | False |
| `fernandez_dividend_yield` | r0_single | exp | 0.810 (0.000) | 0.0091 (0.300) | +1.202 | -0.243 | -128.44 | 0.876 | 0.470 | False |
| `fernandez_dividend_yield` | r0_single | median | 0.809 (0.000) | 0.0097 (0.269) | +1.231 | -0.214 | -128.50 | 0.933 | 0.490 | False |
| `fernandez_dividend_yield` | r0_single | matched | 0.809 (0.000) | 0.0101 (0.250) | +1.260 | -0.185 | -128.56 | 0.968 | 0.480 | False |
| `fernandez_debt_maturity` | r0_single | exp | 0.817 (0.000) | 0.0102 (0.236) | +1.509 | +0.064 | -129.06 | 0.937 | 0.110 | False |
| `fernandez_debt_maturity` | r0_single | median | 0.815 (0.000) | 0.0104 (0.232) | +1.464 | +0.019 | -128.97 | 0.969 | 0.090 | False |
| `fernandez_debt_maturity` | r0_single | matched | 0.815 (0.000) | 0.0104 (0.232) | +1.464 | +0.019 | -128.97 | 0.968 | 0.090 | False |
| `fernandez_joint` | r1_joint | exp | 0.810 (0.000) | 0.0099 (0.261) | +1.445 | +0.000 | -128.93 | 0.968 | 0.190 | False |
| `fernandez_joint` | r1_joint | median | 0.810 (0.000) | 0.0101 (0.251) | +1.418 | -0.028 | -128.87 | 0.984 | 0.180 | False |
| `fernandez_joint` | r1_joint | matched | 0.810 (0.000) | 0.0099 (0.261) | +1.445 | +0.000 | -128.93 | 0.968 | 0.190 | False |
| `r2_histories__direct` | r1_joint | exp | 0.807 (0.000) | 0.0101 (0.249) | +1.384 | -0.061 | -128.81 | 0.964 | 0.250 | False |
| `r2_histories__direct` | r1_joint | median | 0.805 (0.000) | 0.0100 (0.255) | +1.393 | -0.052 | -128.82 | 0.942 | 0.260 | False |
| `r2_histories__direct` | r1_joint | matched | 0.807 (0.000) | 0.0102 (0.248) | +1.381 | -0.064 | -128.80 | 0.968 | 0.250 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | exp | 0.562 (0.005) | 0.0198 (0.007) | +0.396 | -1.049 | -126.83 | 0.215 | 0.520 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | median | 0.806 (0.000) | 0.0103 (0.243) | +1.439 | -0.007 | -128.92 | 0.927 | 0.320 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | matched | 0.808 (0.000) | 0.0104 (0.238) | +1.390 | -0.055 | -128.82 | 0.968 | 0.330 | False |
| `r2_histories__pca16` | r2_histories | exp | 0.810 (0.000) | 0.0100 (0.264) | +1.194 | -0.251 | -128.43 | 0.955 | 0.500 | False |
| `r2_histories__pca16` | r2_histories | median | 0.810 (0.000) | 0.0096 (0.286) | +1.093 | -0.352 | -128.22 | 0.891 | 0.520 | False |
| `r2_histories__pca16` | r2_histories | matched | 0.810 (0.000) | 0.0101 (0.257) | +1.220 | -0.225 | -128.48 | 0.968 | 0.500 | False |
| `r2_histories__autoencoder` | r2_histories | exp | 0.809 (0.000) | 0.0098 (0.268) | +1.241 | -0.204 | -128.52 | 0.953 | 0.370 | False |
| `r2_histories__autoencoder` | r2_histories | median | 0.808 (0.000) | 0.0093 (0.301) | +1.111 | -0.334 | -128.26 | 0.855 | 0.390 | False |
| `r2_histories__autoencoder` | r2_histories | matched | 0.809 (0.000) | 0.0100 (0.260) | +1.261 | -0.184 | -128.56 | 0.968 | 0.360 | False |
| `r2_histories__random_autoencoder` | r2_histories | exp | 0.804 (0.000) | 0.0102 (0.244) | +1.406 | -0.039 | -128.85 | 0.957 | 0.200 | False |
| `r2_histories__random_autoencoder` | r2_histories | median | 0.799 (0.000) | 0.0101 (0.249) | +1.416 | -0.029 | -128.87 | 0.894 | 0.200 | False |
| `r2_histories__random_autoencoder` | r2_histories | matched | 0.805 (0.000) | 0.0102 (0.242) | +1.398 | -0.047 | -128.84 | 0.968 | 0.190 | False |
| `r2_histories__supervised_mlp16` | r2_histories | exp | 0.806 (0.000) | 0.0106 (0.242) | +1.037 | -0.408 | -128.11 | 0.922 | 0.890 | False |
| `r2_histories__supervised_mlp16` | r2_histories | median | 0.796 (0.000) | 0.0108 (0.238) | +0.823 | -0.622 | -127.68 | 0.818 | 0.900 | False |
| `r2_histories__supervised_mlp16` | r2_histories | matched | 0.808 (0.000) | 0.0106 (0.237) | +1.150 | -0.295 | -128.34 | 0.968 | 0.930 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | exp | 0.810 (0.000) | 0.0111 (0.207) | +1.333 | -0.112 | -128.71 | 0.983 | 0.250 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | median | 0.803 (0.000) | 0.0122 (0.163) | +1.374 | -0.071 | -128.79 | 0.848 | 0.240 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | matched | 0.810 (0.000) | 0.0112 (0.200) | +1.340 | -0.105 | -128.72 | 0.968 | 0.240 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | exp | 0.807 (0.000) | 0.0112 (0.202) | +1.299 | -0.146 | -128.64 | 0.962 | 0.290 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | median | 0.794 (0.000) | 0.0122 (0.162) | +1.272 | -0.173 | -128.58 | 0.840 | 0.270 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | matched | 0.807 (0.000) | 0.0111 (0.205) | +1.300 | -0.145 | -128.64 | 0.968 | 0.290 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.414 | -0.031 | -128.87 | 0.984 | 0.140 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | median | 0.806 (0.000) | 0.0107 (0.223) | +1.523 | +0.078 | -129.09 | 0.921 | 0.140 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | matched | 0.808 (0.000) | 0.0107 (0.223) | +1.452 | +0.007 | -128.94 | 0.968 | 0.140 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.415 | -0.030 | -128.87 | 0.984 | 0.150 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | median | 0.806 (0.000) | 0.0107 (0.223) | +1.526 | +0.081 | -129.09 | 0.919 | 0.140 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | matched | 0.808 (0.000) | 0.0107 (0.223) | +1.452 | +0.007 | -128.94 | 0.968 | 0.140 | False |
| `r2_histories__tabfm__late` | r2_histories | exp | 0.810 (0.000) | 0.0108 (0.218) | +1.362 | -0.083 | -128.76 | 0.995 | 0.170 | False |
| `r2_histories__tabfm__late` | r2_histories | median | 0.800 (0.000) | 0.0117 (0.175) | +1.608 | +0.162 | -129.25 | 0.872 | 0.120 | False |
| `r2_histories__tabfm__late` | r2_histories | matched | 0.810 (0.000) | 0.0110 (0.206) | +1.444 | -0.001 | -128.93 | 0.968 | 0.150 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | exp | 0.808 (0.000) | 0.0104 (0.233) | +1.423 | -0.022 | -128.88 | 0.997 | 0.020 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | median | 0.803 (0.000) | 0.0094 (0.281) | +1.766 | +0.321 | -129.57 | 0.915 | 0.020 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | matched | 0.806 (0.000) | 0.0099 (0.256) | +1.614 | +0.169 | -129.27 | 0.968 | 0.020 | False |
| `r2_histories__exaone__late` | r2_histories | exp | 0.811 (0.000) | 0.0113 (0.201) | +1.335 | -0.110 | -128.71 | 0.972 | 0.280 | False |
| `r2_histories__exaone__late` | r2_histories | median | 0.748 (0.000) | 0.0149 (0.083) | +1.059 | -0.387 | -128.16 | 0.756 | 0.400 | False |
| `r2_histories__exaone__late` | r2_histories | matched | 0.811 (0.000) | 0.0113 (0.199) | +1.336 | -0.109 | -128.71 | 0.968 | 0.280 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.321 | -0.124 | -128.68 | 1.000 | 0.840 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | median | 0.778 (0.000) | 0.0108 (0.250) | +0.707 | -0.738 | -127.45 | 0.783 | 0.980 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | matched | 0.800 (0.000) | 0.0107 (0.235) | +1.163 | -0.282 | -128.36 | 0.968 | 0.900 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.321 | -0.124 | -128.68 | 1.000 | 0.800 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | median | 0.776 (0.000) | 0.0108 (0.249) | +0.693 | -0.752 | -127.43 | 0.769 | 0.950 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | matched | 0.800 (0.000) | 0.0107 (0.235) | +1.170 | -0.276 | -128.38 | 0.968 | 0.860 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | exp | 0.808 (0.000) | 0.0111 (0.206) | +1.423 | -0.023 | -128.88 | 0.990 | 0.130 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | median | 0.797 (0.000) | 0.0122 (0.162) | +1.565 | +0.120 | -129.17 | 0.888 | 0.160 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | matched | 0.805 (0.000) | 0.0114 (0.192) | +1.490 | +0.045 | -129.02 | 0.968 | 0.130 | False |
| `r3_broad__direct` | r3_broad | exp | 0.810 (0.000) | 0.0104 (0.232) | +1.398 | -0.047 | -128.84 | 0.994 | 0.080 | False |
| `r3_broad__direct` | r3_broad | median | 0.810 (0.000) | 0.0105 (0.231) | +1.385 | -0.060 | -128.81 | 0.996 | 0.080 | False |
| `r3_broad__direct` | r3_broad | matched | 0.812 (0.000) | 0.0101 (0.245) | +1.475 | +0.030 | -128.99 | 0.968 | 0.080 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | exp | 0.757 (0.000) | 0.0098 (0.258) | +1.311 | -0.135 | -128.66 | 0.133 | 0.420 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | median | 0.806 (0.000) | 0.0105 (0.229) | +1.404 | -0.042 | -128.85 | 0.993 | 0.210 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | matched | 0.802 (0.000) | 0.0104 (0.234) | +1.481 | +0.036 | -129.00 | 0.968 | 0.220 | False |
| `r3_broad__pca16` | r3_broad | exp | 0.811 (0.000) | 0.0102 (0.235) | +1.614 | +0.169 | -129.27 | 0.962 | 0.030 | False |
| `r3_broad__pca16` | r3_broad | median | 0.811 (0.000) | 0.0102 (0.236) | +1.634 | +0.188 | -129.31 | 0.956 | 0.030 | False |
| `r3_broad__pca16` | r3_broad | matched | 0.811 (0.000) | 0.0103 (0.234) | +1.591 | +0.146 | -129.22 | 0.968 | 0.030 | False |
| `r3_broad__autoencoder` | r3_broad | exp | 0.803 (0.000) | 0.0105 (0.224) | +1.561 | +0.116 | -129.16 | 0.958 | 0.080 | False |
| `r3_broad__autoencoder` | r3_broad | median | 0.802 (0.000) | 0.0105 (0.224) | +1.600 | +0.155 | -129.24 | 0.934 | 0.090 | False |
| `r3_broad__autoencoder` | r3_broad | matched | 0.804 (0.000) | 0.0105 (0.224) | +1.538 | +0.092 | -129.11 | 0.968 | 0.080 | False |
| `r3_broad__random_autoencoder` | r3_broad | exp | 0.811 (0.000) | 0.0098 (0.258) | +1.457 | +0.012 | -128.95 | 0.967 | 0.220 | False |
| `r3_broad__random_autoencoder` | r3_broad | median | 0.811 (0.000) | 0.0098 (0.257) | +1.454 | +0.008 | -128.95 | 0.970 | 0.220 | False |
| `r3_broad__random_autoencoder` | r3_broad | matched | 0.811 (0.000) | 0.0098 (0.257) | +1.456 | +0.010 | -128.95 | 0.968 | 0.220 | False |
| `r3_broad__supervised_mlp16` | r3_broad | exp | 0.807 (0.000) | 0.0111 (0.200) | +1.563 | +0.118 | -129.16 | 0.940 | 0.160 | False |
| `r3_broad__supervised_mlp16` | r3_broad | median | 0.807 (0.000) | 0.0111 (0.201) | +1.549 | +0.104 | -129.14 | 0.948 | 0.160 | False |
| `r3_broad__supervised_mlp16` | r3_broad | matched | 0.808 (0.000) | 0.0110 (0.207) | +1.504 | +0.059 | -129.05 | 0.968 | 0.170 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | exp | 0.810 (0.000) | 0.0112 (0.202) | +1.374 | -0.071 | -128.79 | 0.980 | 0.240 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | median | 0.802 (0.000) | 0.0125 (0.152) | +1.473 | +0.028 | -128.99 | 0.834 | 0.220 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | matched | 0.810 (0.000) | 0.0113 (0.196) | +1.390 | -0.056 | -128.82 | 0.968 | 0.240 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | exp | 0.809 (0.000) | 0.0113 (0.198) | +1.303 | -0.142 | -128.64 | 0.959 | 0.280 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | median | 0.795 (0.000) | 0.0126 (0.150) | +1.272 | -0.173 | -128.58 | 0.816 | 0.290 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | matched | 0.809 (0.000) | 0.0112 (0.202) | +1.304 | -0.141 | -128.65 | 0.968 | 0.290 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | exp | 0.804 (0.000) | 0.0110 (0.213) | +1.334 | -0.111 | -128.71 | 0.986 | 0.310 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | median | 0.795 (0.000) | 0.0114 (0.197) | +1.325 | -0.120 | -128.69 | 0.931 | 0.300 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | matched | 0.801 (0.000) | 0.0111 (0.207) | +1.335 | -0.111 | -128.71 | 0.968 | 0.290 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | exp | 0.804 (0.000) | 0.0110 (0.213) | +1.337 | -0.108 | -128.71 | 0.986 | 0.300 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | median | 0.795 (0.000) | 0.0114 (0.197) | +1.333 | -0.112 | -128.70 | 0.928 | 0.300 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | matched | 0.801 (0.000) | 0.0111 (0.207) | +1.339 | -0.106 | -128.72 | 0.968 | 0.290 | False |
| `r3_broad__tabfm__late` | r3_broad | exp | 0.809 (0.000) | 0.0108 (0.217) | +1.352 | -0.094 | -128.74 | 0.996 | 0.180 | False |
| `r3_broad__tabfm__late` | r3_broad | median | 0.793 (0.000) | 0.0119 (0.170) | +1.497 | +0.052 | -129.03 | 0.891 | 0.180 | False |
| `r3_broad__tabfm__late` | r3_broad | matched | 0.806 (0.000) | 0.0111 (0.202) | +1.418 | -0.027 | -128.88 | 0.968 | 0.160 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | exp | 0.807 (0.000) | 0.0106 (0.223) | +1.387 | -0.058 | -128.81 | 0.998 | 0.040 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | median | 0.797 (0.000) | 0.0104 (0.227) | +1.652 | +0.207 | -129.34 | 0.933 | 0.050 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | matched | 0.801 (0.000) | 0.0105 (0.225) | +1.573 | +0.128 | -129.19 | 0.968 | 0.040 | False |
| `r3_broad__exaone__late` | r3_broad | exp | 0.812 (0.000) | 0.0113 (0.199) | +1.355 | -0.090 | -128.75 | 0.970 | 0.250 | False |
| `r3_broad__exaone__late` | r3_broad | median | 0.712 (0.000) | 0.0162 (0.052) | +0.882 | -0.563 | -127.80 | 0.757 | 0.410 | False |
| `r3_broad__exaone__late` | r3_broad | matched | 0.812 (0.000) | 0.0113 (0.198) | +1.356 | -0.089 | -128.75 | 0.968 | 0.240 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | exp | 0.809 (0.000) | 0.0106 (0.223) | +1.322 | -0.124 | -128.68 | 1.000 | 0.440 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | median | 0.796 (0.000) | 0.0113 (0.206) | +1.083 | -0.362 | -128.20 | 0.803 | 0.340 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | matched | 0.806 (0.000) | 0.0107 (0.224) | +1.247 | -0.198 | -128.53 | 0.968 | 0.390 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | exp | 0.809 (0.000) | 0.0106 (0.223) | +1.322 | -0.124 | -128.68 | 1.000 | 0.440 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | median | 0.796 (0.000) | 0.0113 (0.202) | +1.093 | -0.352 | -128.23 | 0.793 | 0.330 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | matched | 0.806 (0.000) | 0.0107 (0.223) | +1.253 | -0.192 | -128.55 | 0.968 | 0.390 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | exp | 0.808 (0.000) | 0.0111 (0.203) | +1.413 | -0.032 | -128.86 | 0.990 | 0.130 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | median | 0.796 (0.000) | 0.0125 (0.151) | +1.515 | +0.070 | -129.07 | 0.890 | 0.190 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | matched | 0.806 (0.000) | 0.0115 (0.187) | +1.468 | +0.023 | -128.98 | 0.968 | 0.130 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | exp | 0.806 (0.000) | 0.0101 (0.250) | +1.399 | -0.046 | -128.84 | 0.965 | 0.210 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | median | 0.805 (0.000) | 0.0100 (0.257) | +1.415 | -0.031 | -128.87 | 0.940 | 0.210 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | matched | 0.807 (0.000) | 0.0102 (0.249) | +1.396 | -0.049 | -128.83 | 0.968 | 0.210 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | exp | 0.526 (0.011) | 0.0211 (0.003) | +0.409 | -1.036 | -126.86 | 0.202 | 0.460 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | median | 0.807 (0.000) | 0.0102 (0.246) | +1.455 | +0.010 | -128.95 | 0.925 | 0.310 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | matched | 0.809 (0.000) | 0.0103 (0.239) | +1.399 | -0.046 | -128.84 | 0.968 | 0.320 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | exp | 0.807 (0.000) | 0.0101 (0.257) | +1.296 | -0.149 | -128.63 | 0.957 | 0.300 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | median | 0.805 (0.000) | 0.0098 (0.275) | +1.257 | -0.189 | -128.55 | 0.890 | 0.310 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | matched | 0.807 (0.000) | 0.0101 (0.252) | +1.303 | -0.143 | -128.64 | 0.968 | 0.300 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | exp | 0.810 (0.000) | 0.0099 (0.266) | +1.264 | -0.181 | -128.57 | 0.962 | 0.340 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | median | 0.810 (0.000) | 0.0093 (0.301) | +1.157 | -0.289 | -128.35 | 0.869 | 0.380 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | matched | 0.810 (0.000) | 0.0099 (0.262) | +1.272 | -0.173 | -128.58 | 0.968 | 0.340 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | exp | 0.805 (0.000) | 0.0102 (0.245) | +1.397 | -0.048 | -128.83 | 0.961 | 0.200 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | median | 0.800 (0.000) | 0.0100 (0.252) | +1.407 | -0.038 | -128.85 | 0.897 | 0.230 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | matched | 0.805 (0.000) | 0.0102 (0.244) | +1.392 | -0.053 | -128.82 | 0.968 | 0.180 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | exp | 0.792 (0.000) | 0.0103 (0.248) | +1.193 | -0.252 | -128.42 | 0.869 | 0.430 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | median | 0.792 (0.000) | 0.0103 (0.247) | +1.199 | -0.246 | -128.44 | 0.874 | 0.430 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | matched | 0.801 (0.000) | 0.0106 (0.232) | +1.301 | -0.144 | -128.64 | 0.968 | 0.360 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | exp | 0.805 (0.000) | 0.0110 (0.207) | +1.399 | -0.046 | -128.84 | 0.995 | 0.090 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | median | 0.783 (0.000) | 0.0126 (0.147) | +1.590 | +0.145 | -129.22 | 0.879 | 0.120 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | matched | 0.798 (0.000) | 0.0116 (0.184) | +1.498 | +0.052 | -129.03 | 0.968 | 0.100 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | exp | 0.803 (0.000) | 0.0114 (0.192) | +1.478 | +0.032 | -128.99 | 0.984 | 0.100 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | median | 0.784 (0.000) | 0.0129 (0.135) | +1.660 | +0.215 | -129.36 | 0.860 | 0.130 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0117 (0.180) | +1.531 | +0.086 | -129.10 | 0.968 | 0.100 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | exp | 0.800 (0.000) | 0.0112 (0.206) | +1.355 | -0.091 | -128.75 | 0.971 | 0.310 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | median | 0.796 (0.000) | 0.0114 (0.198) | +1.350 | -0.095 | -128.74 | 0.942 | 0.320 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0112 (0.205) | +1.355 | -0.091 | -128.75 | 0.968 | 0.320 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | exp | 0.800 (0.000) | 0.0112 (0.206) | +1.352 | -0.093 | -128.74 | 0.971 | 0.320 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | median | 0.796 (0.000) | 0.0114 (0.198) | +1.346 | -0.099 | -128.73 | 0.942 | 0.340 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0112 (0.205) | +1.352 | -0.093 | -128.74 | 0.968 | 0.320 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | exp | 0.803 (0.000) | 0.0109 (0.209) | +1.476 | +0.031 | -128.99 | 0.998 | 0.050 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | median | 0.781 (0.000) | 0.0119 (0.162) | +1.926 | +0.481 | -129.89 | 0.934 | 0.050 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | matched | 0.789 (0.000) | 0.0115 (0.178) | +1.793 | +0.347 | -129.62 | 0.968 | 0.040 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | exp | 0.807 (0.000) | 0.0104 (0.233) | +1.462 | +0.017 | -128.96 | 0.995 | 0.020 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | median | 0.803 (0.000) | 0.0095 (0.275) | +1.831 | +0.386 | -129.70 | 0.914 | 0.020 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | matched | 0.805 (0.000) | 0.0100 (0.252) | +1.653 | +0.208 | -129.35 | 0.968 | 0.020 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | exp | 0.805 (0.000) | 0.0114 (0.194) | +1.456 | +0.011 | -128.95 | 0.991 | 0.060 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | median | 0.782 (0.000) | 0.0137 (0.117) | +1.736 | +0.291 | -129.51 | 0.861 | 0.070 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0120 (0.169) | +1.563 | +0.118 | -129.16 | 0.968 | 0.060 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.321 | -0.124 | -128.68 | 1.000 | 0.830 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | median | 0.773 (0.000) | 0.0112 (0.229) | +0.661 | -0.784 | -127.36 | 0.768 | 0.980 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0108 (0.231) | +1.160 | -0.285 | -128.36 | 0.968 | 0.890 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | exp | 0.809 (0.000) | 0.0107 (0.223) | +1.321 | -0.124 | -128.68 | 1.000 | 0.800 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | median | 0.772 (0.000) | 0.0112 (0.228) | +0.656 | -0.789 | -127.35 | 0.757 | 0.980 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | matched | 0.800 (0.000) | 0.0107 (0.231) | +1.166 | -0.279 | -128.37 | 0.968 | 0.880 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | exp | 0.806 (0.000) | 0.0110 (0.208) | +1.398 | -0.047 | -128.84 | 0.997 | 0.100 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | median | 0.791 (0.000) | 0.0122 (0.160) | +1.573 | +0.128 | -129.18 | 0.952 | 0.110 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | matched | 0.795 (0.000) | 0.0119 (0.171) | +1.543 | +0.097 | -129.12 | 0.968 | 0.110 | False |
| `uniform_network` | reference | none | 0.809 (0.000) | 0.0106 (0.223) | +1.322 | -0.123 | -128.68 | 1.000 | — | False |

## FF6 exposures, SEM-ML

Nonspatial OLS: log-likelihood 79.857, AIC -145.71, BIC -135.24, HQIC -142.19.

| Network | Rung | Kernel | λ (p) | Premium (p) | logL - OLS | logL - joint | BIC | Eff. nbrs | Placebo p | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `fernandez_market_cap_assets` | r0_single | exp | -0.990 (0.390) | 0.0481 (0.000) | +0.939 | +0.097 | -133.62 | 0.897 | — | True |
| `fernandez_market_cap_assets` | r0_single | median | -0.990 (0.418) | 0.0483 (0.000) | +0.875 | +0.033 | -133.49 | 0.942 | — | True |
| `fernandez_market_cap_assets` | r0_single | matched | -0.990 (0.437) | 0.0484 (0.000) | +0.824 | -0.018 | -133.39 | 0.968 | — | True |
| `fernandez_market_to_book` | r0_single | exp | -0.990 (0.387) | 0.0491 (0.000) | +0.698 | -0.143 | -133.14 | 0.892 | — | True |
| `fernandez_market_to_book` | r0_single | median | -0.990 (0.419) | 0.0490 (0.000) | +0.695 | -0.146 | -133.13 | 0.942 | — | True |
| `fernandez_market_to_book` | r0_single | matched | -0.990 (0.437) | 0.0489 (0.000) | +0.693 | -0.149 | -133.13 | 0.968 | — | True |
| `fernandez_dividend_yield` | r0_single | exp | -0.990 (0.373) | 0.0484 (0.000) | +1.183 | +0.342 | -134.11 | 0.876 | — | True |
| `fernandez_dividend_yield` | r0_single | median | -0.990 (0.411) | 0.0485 (0.000) | +1.053 | +0.212 | -133.85 | 0.933 | — | True |
| `fernandez_dividend_yield` | r0_single | matched | -0.990 (0.436) | 0.0486 (0.000) | +0.938 | +0.096 | -133.62 | 0.968 | — | True |
| `fernandez_debt_maturity` | r0_single | exp | -0.990 (0.410) | 0.0481 (0.000) | +0.389 | -0.452 | -132.52 | 0.937 | — | True |
| `fernandez_debt_maturity` | r0_single | median | -0.990 (0.434) | 0.0483 (0.000) | +0.488 | -0.353 | -132.72 | 0.969 | — | True |
| `fernandez_debt_maturity` | r0_single | matched | -0.990 (0.434) | 0.0483 (0.000) | +0.487 | -0.355 | -132.72 | 0.968 | — | True |
| `fernandez_joint` | r1_joint | exp | -0.990 (0.435) | 0.0484 (0.000) | +0.842 | +0.000 | -133.43 | 0.968 | — | True |
| `fernandez_joint` | r1_joint | median | -0.990 (0.447) | 0.0485 (0.000) | +0.792 | -0.050 | -133.33 | 0.984 | — | True |
| `fernandez_joint` | r1_joint | matched | -0.990 (0.435) | 0.0484 (0.000) | +0.842 | +0.000 | -133.43 | 0.968 | — | True |
| `r2_histories__direct` | r1_joint | exp | -0.990 (0.439) | 0.0489 (0.000) | +0.870 | +0.029 | -133.48 | 0.964 | — | True |
| `r2_histories__direct` | r1_joint | median | -0.990 (0.427) | 0.0489 (0.000) | +0.921 | +0.079 | -133.58 | 0.942 | — | True |
| `r2_histories__direct` | r1_joint | matched | -0.990 (0.442) | 0.0489 (0.000) | +0.857 | +0.015 | -133.46 | 0.968 | — | True |
| `r2_histories__mahalanobis_lw` | r1_joint | exp | -0.887 (0.003) | 0.0475 (0.000) | +1.949 | +1.107 | -135.64 | 0.215 | — | False |
| `r2_histories__mahalanobis_lw` | r1_joint | median | -0.990 (0.437) | 0.0486 (0.000) | +0.834 | -0.008 | -133.41 | 0.927 | — | True |
| `r2_histories__mahalanobis_lw` | r1_joint | matched | -0.990 (0.451) | 0.0486 (0.000) | +0.778 | -0.064 | -133.30 | 0.968 | — | True |
| `r2_histories__pca16` | r2_histories | exp | -0.990 (0.432) | 0.0489 (0.000) | +0.980 | +0.138 | -133.70 | 0.955 | — | True |
| `r2_histories__pca16` | r2_histories | median | -0.990 (0.396) | 0.0489 (0.000) | +1.153 | +0.312 | -134.05 | 0.891 | — | True |
| `r2_histories__pca16` | r2_histories | matched | -0.990 (0.441) | 0.0489 (0.000) | +0.929 | +0.087 | -133.60 | 0.968 | — | True |
| `r2_histories__autoencoder` | r2_histories | exp | -0.990 (0.430) | 0.0489 (0.000) | +0.867 | +0.025 | -133.48 | 0.953 | — | True |
| `r2_histories__autoencoder` | r2_histories | median | -0.990 (0.375) | 0.0488 (0.000) | +0.991 | +0.150 | -133.72 | 0.855 | — | True |
| `r2_histories__autoencoder` | r2_histories | matched | -0.990 (0.440) | 0.0489 (0.000) | +0.836 | -0.006 | -133.41 | 0.968 | — | True |
| `r2_histories__random_autoencoder` | r2_histories | exp | -0.990 (0.433) | 0.0490 (0.000) | +0.776 | -0.066 | -133.29 | 0.957 | — | True |
| `r2_histories__random_autoencoder` | r2_histories | median | -0.990 (0.397) | 0.0490 (0.000) | +0.806 | -0.036 | -133.35 | 0.894 | — | True |
| `r2_histories__random_autoencoder` | r2_histories | matched | -0.990 (0.440) | 0.0489 (0.000) | +0.766 | -0.076 | -133.27 | 0.968 | — | True |
| `r2_histories__supervised_mlp16` | r2_histories | exp | -0.990 (0.423) | 0.0488 (0.000) | +0.998 | +0.157 | -133.74 | 0.922 | — | True |
| `r2_histories__supervised_mlp16` | r2_histories | median | -0.990 (0.370) | 0.0489 (0.000) | +1.247 | +0.405 | -134.24 | 0.818 | — | True |
| `r2_histories__supervised_mlp16` | r2_histories | matched | -0.990 (0.445) | 0.0487 (0.000) | +0.868 | +0.027 | -133.48 | 0.968 | — | True |
| `r2_histories__tabpfn_fast__late` | r2_histories | exp | -0.990 (0.451) | 0.0487 (0.000) | +0.838 | -0.004 | -133.42 | 0.983 | — | True |
| `r2_histories__tabpfn_fast__late` | r2_histories | median | -0.990 (0.370) | 0.0485 (0.000) | +1.179 | +0.337 | -134.10 | 0.848 | — | True |
| `r2_histories__tabpfn_fast__late` | r2_histories | matched | -0.990 (0.443) | 0.0486 (0.000) | +0.894 | +0.053 | -133.53 | 0.968 | — | True |
| `r2_histories__tabpfn_full__late` | r2_histories | exp | -0.990 (0.442) | 0.0487 (0.000) | +0.915 | +0.073 | -133.57 | 0.962 | — | True |
| `r2_histories__tabpfn_full__late` | r2_histories | median | -0.990 (0.358) | 0.0489 (0.000) | +1.247 | +0.405 | -134.23 | 0.840 | — | True |
| `r2_histories__tabpfn_full__late` | r2_histories | matched | -0.990 (0.445) | 0.0487 (0.000) | +0.891 | +0.050 | -133.52 | 0.968 | — | True |
| `r2_histories__tabfm__early_concat` | r2_histories | exp | -0.990 (0.453) | 0.0489 (0.000) | +0.829 | -0.013 | -133.40 | 0.984 | — | True |
| `r2_histories__tabfm__early_concat` | r2_histories | median | -0.990 (0.418) | 0.0489 (0.000) | +1.035 | +0.193 | -133.81 | 0.921 | — | True |
| `r2_histories__tabfm__early_concat` | r2_histories | matched | -0.990 (0.444) | 0.0489 (0.000) | +0.892 | +0.051 | -133.53 | 0.968 | — | True |
| `r2_histories__tabfm__early_mean` | r2_histories | exp | -0.990 (0.452) | 0.0489 (0.000) | +0.830 | -0.011 | -133.40 | 0.984 | — | True |
| `r2_histories__tabfm__early_mean` | r2_histories | median | -0.990 (0.417) | 0.0490 (0.000) | +1.039 | +0.197 | -133.82 | 0.919 | — | True |
| `r2_histories__tabfm__early_mean` | r2_histories | matched | -0.990 (0.444) | 0.0489 (0.000) | +0.893 | +0.051 | -133.53 | 0.968 | — | True |
| `r2_histories__tabfm__late` | r2_histories | exp | -0.990 (0.459) | 0.0488 (0.000) | +0.726 | -0.116 | -133.19 | 0.995 | — | True |
| `r2_histories__tabfm__late` | r2_histories | median | -0.990 (0.379) | 0.0491 (0.000) | +0.940 | +0.098 | -133.62 | 0.872 | — | True |
| `r2_histories__tabfm__late` | r2_histories | matched | -0.990 (0.448) | 0.0489 (0.000) | +0.786 | -0.055 | -133.31 | 0.968 | — | True |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | exp | -0.990 (0.459) | 0.0490 (0.000) | +0.727 | -0.115 | -133.20 | 0.997 | — | True |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | median | -0.990 (0.412) | 0.0496 (0.000) | +0.918 | +0.077 | -133.58 | 0.915 | — | True |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | matched | -0.990 (0.443) | 0.0494 (0.000) | +0.821 | -0.021 | -133.38 | 0.968 | — | True |
| `r2_histories__exaone__late` | r2_histories | exp | -0.990 (0.448) | 0.0488 (0.000) | +0.894 | +0.053 | -133.53 | 0.972 | — | True |
| `r2_histories__exaone__late` | r2_histories | median | -0.990 (0.101) | 0.0499 (0.000) | +1.638 | +0.797 | -135.02 | 0.756 | — | True |
| `r2_histories__exaone__late` | r2_histories | matched | -0.990 (0.447) | 0.0488 (0.000) | +0.911 | +0.069 | -133.56 | 0.968 | — | True |
| `r2_histories__exaone__item_first_concat` | r2_histories | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.686 | -0.156 | -133.11 | 1.000 | — | True |
| `r2_histories__exaone__item_first_concat` | r2_histories | median | -0.990 (0.346) | 0.0481 (0.000) | +1.492 | +0.650 | -134.73 | 0.783 | — | True |
| `r2_histories__exaone__item_first_concat` | r2_histories | matched | -0.990 (0.440) | 0.0486 (0.000) | +0.937 | +0.095 | -133.62 | 0.968 | — | True |
| `r2_histories__exaone__item_first_mean` | r2_histories | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.687 | -0.155 | -133.11 | 1.000 | — | True |
| `r2_histories__exaone__item_first_mean` | r2_histories | median | -0.990 (0.339) | 0.0480 (0.000) | +1.532 | +0.691 | -134.81 | 0.769 | — | True |
| `r2_histories__exaone__item_first_mean` | r2_histories | matched | -0.990 (0.440) | 0.0486 (0.000) | +0.937 | +0.095 | -133.62 | 0.968 | — | True |
| `r2_histories__exaone__item_last_concat` | r2_histories | exp | -0.990 (0.456) | 0.0489 (0.000) | +0.815 | -0.027 | -133.37 | 0.990 | — | True |
| `r2_histories__exaone__item_last_concat` | r2_histories | median | -0.990 (0.399) | 0.0493 (0.000) | +1.251 | +0.410 | -134.24 | 0.888 | — | True |
| `r2_histories__exaone__item_last_concat` | r2_histories | matched | -0.990 (0.445) | 0.0490 (0.000) | +0.938 | +0.097 | -133.62 | 0.968 | — | True |
| `r3_broad__direct` | r3_broad | exp | -0.990 (0.457) | 0.0487 (0.000) | +0.693 | -0.149 | -133.13 | 0.994 | — | True |
| `r3_broad__direct` | r3_broad | median | -0.990 (0.458) | 0.0487 (0.000) | +0.691 | -0.151 | -133.12 | 0.996 | — | True |
| `r3_broad__direct` | r3_broad | matched | -0.990 (0.439) | 0.0485 (0.000) | +0.715 | -0.126 | -133.17 | 0.968 | — | True |
| `r3_broad__mahalanobis_lw` | r3_broad | exp | -0.707 (0.008) | 0.0476 (0.000) | +0.978 | +0.136 | -133.70 | 0.133 | — | False |
| `r3_broad__mahalanobis_lw` | r3_broad | median | -0.990 (0.459) | 0.0488 (0.000) | +0.700 | -0.142 | -133.14 | 0.993 | — | True |
| `r3_broad__mahalanobis_lw` | r3_broad | matched | -0.990 (0.452) | 0.0488 (0.000) | +0.718 | -0.124 | -133.18 | 0.968 | — | True |
| `r3_broad__pca16` | r3_broad | exp | -0.990 (0.438) | 0.0488 (0.000) | +0.680 | -0.162 | -133.10 | 0.962 | — | True |
| `r3_broad__pca16` | r3_broad | median | -0.990 (0.435) | 0.0488 (0.000) | +0.683 | -0.159 | -133.11 | 0.956 | — | True |
| `r3_broad__pca16` | r3_broad | matched | -0.990 (0.442) | 0.0488 (0.000) | +0.677 | -0.165 | -133.10 | 0.968 | — | True |
| `r3_broad__autoencoder` | r3_broad | exp | -0.990 (0.441) | 0.0491 (0.000) | +0.714 | -0.128 | -133.17 | 0.958 | — | True |
| `r3_broad__autoencoder` | r3_broad | median | -0.990 (0.428) | 0.0491 (0.000) | +0.733 | -0.109 | -133.21 | 0.934 | — | True |
| `r3_broad__autoencoder` | r3_broad | matched | -0.990 (0.446) | 0.0491 (0.000) | +0.706 | -0.136 | -133.15 | 0.968 | — | True |
| `r3_broad__random_autoencoder` | r3_broad | exp | -0.990 (0.437) | 0.0488 (0.000) | +0.689 | -0.153 | -133.12 | 0.967 | — | True |
| `r3_broad__random_autoencoder` | r3_broad | median | -0.990 (0.438) | 0.0488 (0.000) | +0.690 | -0.151 | -133.12 | 0.970 | — | True |
| `r3_broad__random_autoencoder` | r3_broad | matched | -0.990 (0.437) | 0.0488 (0.000) | +0.690 | -0.152 | -133.12 | 0.968 | — | True |
| `r3_broad__supervised_mlp16` | r3_broad | exp | -0.990 (0.421) | 0.0489 (0.000) | +0.703 | -0.138 | -133.15 | 0.940 | — | True |
| `r3_broad__supervised_mlp16` | r3_broad | median | -0.990 (0.426) | 0.0489 (0.000) | +0.702 | -0.139 | -133.15 | 0.948 | — | True |
| `r3_broad__supervised_mlp16` | r3_broad | matched | -0.990 (0.439) | 0.0489 (0.000) | +0.699 | -0.143 | -133.14 | 0.968 | — | True |
| `r3_broad__tabpfn_fast__late` | r3_broad | exp | -0.990 (0.450) | 0.0487 (0.000) | +0.861 | +0.019 | -133.46 | 0.980 | — | True |
| `r3_broad__tabpfn_fast__late` | r3_broad | median | -0.990 (0.363) | 0.0487 (0.000) | +1.284 | +0.442 | -134.31 | 0.834 | — | True |
| `r3_broad__tabpfn_fast__late` | r3_broad | matched | -0.990 (0.444) | 0.0487 (0.000) | +0.911 | +0.069 | -133.56 | 0.968 | — | True |
| `r3_broad__tabpfn_full__late` | r3_broad | exp | -0.990 (0.440) | 0.0487 (0.000) | +0.939 | +0.097 | -133.62 | 0.959 | — | True |
| `r3_broad__tabpfn_full__late` | r3_broad | median | -0.990 (0.343) | 0.0488 (0.000) | +1.354 | +0.512 | -134.45 | 0.816 | — | True |
| `r3_broad__tabpfn_full__late` | r3_broad | matched | -0.990 (0.445) | 0.0487 (0.000) | +0.904 | +0.062 | -133.55 | 0.968 | — | True |
| `r3_broad__tabfm__early_concat` | r3_broad | exp | -0.990 (0.453) | 0.0488 (0.000) | +0.859 | +0.018 | -133.46 | 0.986 | — | True |
| `r3_broad__tabfm__early_concat` | r3_broad | median | -0.990 (0.421) | 0.0489 (0.000) | +1.124 | +0.283 | -133.99 | 0.931 | — | True |
| `r3_broad__tabfm__early_concat` | r3_broad | matched | -0.990 (0.443) | 0.0488 (0.000) | +0.961 | +0.119 | -133.66 | 0.968 | — | True |
| `r3_broad__tabfm__early_mean` | r3_broad | exp | -0.990 (0.453) | 0.0488 (0.000) | +0.856 | +0.015 | -133.45 | 0.986 | — | True |
| `r3_broad__tabfm__early_mean` | r3_broad | median | -0.990 (0.420) | 0.0489 (0.000) | +1.118 | +0.276 | -133.98 | 0.928 | — | True |
| `r3_broad__tabfm__early_mean` | r3_broad | matched | -0.990 (0.443) | 0.0488 (0.000) | +0.951 | +0.110 | -133.64 | 0.968 | — | True |
| `r3_broad__tabfm__late` | r3_broad | exp | -0.990 (0.459) | 0.0488 (0.000) | +0.731 | -0.110 | -133.20 | 0.996 | — | True |
| `r3_broad__tabfm__late` | r3_broad | median | -0.990 (0.393) | 0.0492 (0.000) | +0.994 | +0.152 | -133.73 | 0.891 | — | True |
| `r3_broad__tabfm__late` | r3_broad | matched | -0.990 (0.447) | 0.0489 (0.000) | +0.821 | -0.021 | -133.38 | 0.968 | — | True |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | exp | -0.990 (0.460) | 0.0489 (0.000) | +0.708 | -0.134 | -133.16 | 0.998 | — | True |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | median | -0.990 (0.424) | 0.0492 (0.000) | +0.854 | +0.013 | -133.45 | 0.933 | — | True |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | matched | -0.990 (0.444) | 0.0491 (0.000) | +0.796 | -0.046 | -133.33 | 0.968 | — | True |
| `r3_broad__exaone__late` | r3_broad | exp | -0.990 (0.447) | 0.0489 (0.000) | +0.914 | +0.073 | -133.57 | 0.970 | — | True |
| `r3_broad__exaone__late` | r3_broad | median | -0.990 (0.011) | 0.0502 (0.000) | +1.502 | +0.661 | -134.75 | 0.757 | — | True |
| `r3_broad__exaone__late` | r3_broad | matched | -0.990 (0.446) | 0.0489 (0.000) | +0.923 | +0.081 | -133.59 | 0.968 | — | True |
| `r3_broad__exaone__item_first_concat` | r3_broad | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.685 | -0.157 | -133.11 | 1.000 | — | True |
| `r3_broad__exaone__item_first_concat` | r3_broad | median | -0.990 (0.354) | 0.0493 (0.000) | +1.190 | +0.348 | -134.12 | 0.803 | — | True |
| `r3_broad__exaone__item_first_concat` | r3_broad | matched | -0.990 (0.440) | 0.0490 (0.000) | +0.875 | +0.033 | -133.49 | 0.968 | — | True |
| `r3_broad__exaone__item_first_mean` | r3_broad | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.686 | -0.156 | -133.11 | 1.000 | — | True |
| `r3_broad__exaone__item_first_mean` | r3_broad | median | -0.990 (0.349) | 0.0494 (0.000) | +1.172 | +0.330 | -134.09 | 0.793 | — | True |
| `r3_broad__exaone__item_first_mean` | r3_broad | matched | -0.990 (0.440) | 0.0490 (0.000) | +0.867 | +0.026 | -133.48 | 0.968 | — | True |
| `r3_broad__exaone__item_last_concat` | r3_broad | exp | -0.990 (0.456) | 0.0489 (0.000) | +0.827 | -0.014 | -133.40 | 0.990 | — | True |
| `r3_broad__exaone__item_last_concat` | r3_broad | median | -0.990 (0.393) | 0.0494 (0.000) | +1.282 | +0.441 | -134.31 | 0.890 | — | True |
| `r3_broad__exaone__item_last_concat` | r3_broad | matched | -0.990 (0.444) | 0.0491 (0.000) | +0.955 | +0.114 | -133.65 | 0.968 | — | True |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | exp | -0.990 (0.440) | 0.0489 (0.000) | +0.859 | +0.017 | -133.46 | 0.965 | — | True |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | median | -0.990 (0.427) | 0.0489 (0.000) | +0.915 | +0.073 | -133.57 | 0.940 | — | True |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | matched | -0.990 (0.442) | 0.0489 (0.000) | +0.850 | +0.008 | -133.44 | 0.968 | — | True |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | exp | -0.864 (0.002) | 0.0473 (0.000) | +2.127 | +1.285 | -136.00 | 0.202 | — | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | median | -0.990 (0.436) | 0.0486 (0.000) | +0.827 | -0.015 | -133.40 | 0.925 | — | True |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | matched | -0.990 (0.451) | 0.0486 (0.000) | +0.771 | -0.071 | -133.28 | 0.968 | — | True |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | exp | -0.990 (0.434) | 0.0490 (0.000) | +0.972 | +0.131 | -133.69 | 0.957 | — | True |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | median | -0.990 (0.396) | 0.0491 (0.000) | +1.159 | +0.317 | -134.06 | 0.890 | — | True |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | matched | -0.990 (0.441) | 0.0489 (0.000) | +0.930 | +0.089 | -133.60 | 0.968 | — | True |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | exp | -0.990 (0.436) | 0.0489 (0.000) | +0.902 | +0.060 | -133.54 | 0.962 | — | True |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | median | -0.990 (0.383) | 0.0489 (0.000) | +1.091 | +0.249 | -133.92 | 0.869 | — | True |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0489 (0.000) | +0.881 | +0.039 | -133.50 | 0.968 | — | True |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | exp | -0.990 (0.436) | 0.0489 (0.000) | +0.775 | -0.066 | -133.29 | 0.961 | — | True |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | median | -0.990 (0.400) | 0.0490 (0.000) | +0.808 | -0.034 | -133.36 | 0.897 | — | True |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0489 (0.000) | +0.768 | -0.074 | -133.28 | 0.968 | — | True |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | exp | -0.990 (0.378) | 0.0482 (0.000) | +1.384 | +0.542 | -134.51 | 0.869 | — | True |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | median | -0.990 (0.381) | 0.0482 (0.000) | +1.368 | +0.526 | -134.48 | 0.874 | — | True |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | matched | -0.990 (0.438) | 0.0486 (0.000) | +0.999 | +0.158 | -133.74 | 0.968 | — | True |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | exp | -0.990 (0.458) | 0.0489 (0.000) | +0.773 | -0.068 | -133.29 | 0.995 | — | True |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | median | -0.990 (0.393) | 0.0493 (0.000) | +1.232 | +0.391 | -134.21 | 0.879 | — | True |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | matched | -0.990 (0.444) | 0.0490 (0.000) | +0.925 | +0.083 | -133.59 | 0.968 | — | True |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | exp | -0.990 (0.453) | 0.0490 (0.000) | +0.844 | +0.002 | -133.43 | 0.984 | — | True |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | median | -0.990 (0.381) | 0.0494 (0.000) | +1.282 | +0.441 | -134.31 | 0.860 | — | True |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | matched | -0.990 (0.444) | 0.0491 (0.000) | +0.919 | +0.077 | -133.58 | 0.968 | — | True |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | exp | -0.990 (0.442) | 0.0489 (0.000) | +1.033 | +0.191 | -133.81 | 0.971 | — | True |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | median | -0.990 (0.424) | 0.0489 (0.000) | +1.204 | +0.362 | -134.15 | 0.942 | — | True |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0489 (0.000) | +1.051 | +0.209 | -133.84 | 0.968 | — | True |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | exp | -0.990 (0.442) | 0.0489 (0.000) | +1.037 | +0.195 | -133.82 | 0.971 | — | True |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | median | -0.990 (0.424) | 0.0489 (0.000) | +1.208 | +0.366 | -134.16 | 0.942 | — | True |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0489 (0.000) | +1.052 | +0.210 | -133.85 | 0.968 | — | True |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | exp | -0.990 (0.460) | 0.0490 (0.000) | +0.689 | -0.153 | -133.12 | 0.998 | — | True |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | median | -0.990 (0.428) | 0.0497 (0.000) | +0.757 | -0.085 | -133.26 | 0.934 | — | True |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | matched | -0.990 (0.446) | 0.0495 (0.000) | +0.719 | -0.123 | -133.18 | 0.968 | — | True |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | exp | -0.990 (0.458) | 0.0490 (0.000) | +0.721 | -0.121 | -133.18 | 0.995 | — | True |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | median | -0.990 (0.410) | 0.0495 (0.000) | +0.822 | -0.020 | -133.39 | 0.914 | — | True |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | matched | -0.990 (0.442) | 0.0493 (0.000) | +0.772 | -0.070 | -133.29 | 0.968 | — | True |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | exp | -0.990 (0.456) | 0.0489 (0.000) | +0.802 | -0.040 | -133.35 | 0.991 | — | True |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | median | -0.990 (0.384) | 0.0493 (0.000) | +1.296 | +0.454 | -134.33 | 0.861 | — | True |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | matched | -0.990 (0.443) | 0.0490 (0.000) | +0.924 | +0.082 | -133.59 | 0.968 | — | True |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.686 | -0.156 | -133.11 | 1.000 | — | True |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | median | -0.990 (0.337) | 0.0481 (0.000) | +1.541 | +0.699 | -134.82 | 0.768 | — | True |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0486 (0.000) | +0.936 | +0.094 | -133.61 | 0.968 | — | True |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | exp | -0.990 (0.461) | 0.0488 (0.000) | +0.687 | -0.155 | -133.12 | 1.000 | — | True |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | median | -0.990 (0.331) | 0.0481 (0.000) | +1.578 | +0.736 | -134.90 | 0.757 | — | True |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | matched | -0.990 (0.440) | 0.0486 (0.000) | +0.938 | +0.096 | -133.62 | 0.968 | — | True |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | exp | -0.990 (0.459) | 0.0488 (0.000) | +0.762 | -0.079 | -133.27 | 0.997 | — | True |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | median | -0.990 (0.433) | 0.0490 (0.000) | +1.073 | +0.231 | -133.89 | 0.952 | — | True |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | matched | -0.990 (0.442) | 0.0489 (0.000) | +0.988 | +0.147 | -133.72 | 0.968 | — | True |
| `uniform_network` | reference | none | -0.990 (0.461) | 0.0488 (0.000) | +0.685 | -0.157 | -133.11 | 1.000 | — | True |

## Generated-beta bootstrap (exp kernel, W fixed)

| Factors | Network | Parameter | Bootstrap SE | 95% interval |
| --- | --- | --- | ---: | --- |
| capm | `fernandez_market_cap_assets` | sem_intensity | 0.7784 | [-0.9900, 0.8706] |
| capm | `fernandez_market_cap_assets` | sem_premium | 0.0191 | [-0.0140, 0.0556] |
| capm | `fernandez_market_to_book` | sem_intensity | 0.7451 | [-0.9900, 0.8712] |
| capm | `fernandez_market_to_book` | sem_premium | 0.0193 | [-0.0150, 0.0551] |
| capm | `fernandez_dividend_yield` | sem_intensity | 0.8414 | [-0.9900, 0.8766] |
| capm | `fernandez_dividend_yield` | sem_premium | 0.0203 | [-0.0158, 0.0568] |
| capm | `fernandez_debt_maturity` | sem_intensity | 0.8227 | [-0.9900, 0.8785] |
| capm | `fernandez_debt_maturity` | sem_premium | 0.0194 | [-0.0144, 0.0559] |
| capm | `fernandez_joint` | sem_intensity | 0.8496 | [-0.9900, 0.8758] |
| capm | `fernandez_joint` | sem_premium | 0.0196 | [-0.0152, 0.0558] |
| capm | `r2_histories__direct` | sem_intensity | 0.8722 | [-0.9900, 0.8729] |
| capm | `r2_histories__direct` | sem_premium | 0.0199 | [-0.0151, 0.0557] |
| capm | `r2_histories__mahalanobis_lw` | sem_intensity | 0.4231 | [-0.5508, 0.8361] |
| capm | `r2_histories__mahalanobis_lw` | sem_premium | 0.0162 | [-0.0058, 0.0551] |
| capm | `r2_histories__pca16` | sem_intensity | 0.8921 | [-0.9900, 0.8761] |
| capm | `r2_histories__pca16` | sem_premium | 0.0200 | [-0.0153, 0.0572] |
| capm | `r2_histories__autoencoder` | sem_intensity | 0.8898 | [-0.9900, 0.8758] |
| capm | `r2_histories__autoencoder` | sem_premium | 0.0202 | [-0.0151, 0.0575] |
| capm | `r2_histories__random_autoencoder` | sem_intensity | 0.8783 | [-0.9900, 0.8711] |
| capm | `r2_histories__random_autoencoder` | sem_premium | 0.0198 | [-0.0148, 0.0558] |
| capm | `r2_histories__supervised_mlp16` | sem_intensity | 0.8931 | [-0.9900, 0.8773] |
| capm | `r2_histories__supervised_mlp16` | sem_premium | 0.0198 | [-0.0138, 0.0571] |
| capm | `r2_histories__tabpfn_fast__late` | sem_intensity | 0.8684 | [-0.9900, 0.8749] |
| capm | `r2_histories__tabpfn_fast__late` | sem_premium | 0.0193 | [-0.0139, 0.0557] |
| capm | `r2_histories__tabpfn_full__late` | sem_intensity | 0.8709 | [-0.9900, 0.8730] |
| capm | `r2_histories__tabpfn_full__late` | sem_premium | 0.0191 | [-0.0137, 0.0556] |
| capm | `r2_histories__tabfm__early_concat` | sem_intensity | 0.8659 | [-0.9900, 0.8730] |
| capm | `r2_histories__tabfm__early_concat` | sem_premium | 0.0196 | [-0.0142, 0.0559] |
| capm | `r2_histories__tabfm__early_mean` | sem_intensity | 0.8655 | [-0.9900, 0.8731] |
| capm | `r2_histories__tabfm__early_mean` | sem_premium | 0.0196 | [-0.0142, 0.0559] |
| capm | `r2_histories__tabfm__late` | sem_intensity | 0.8788 | [-0.9900, 0.8749] |
| capm | `r2_histories__tabfm__late` | sem_premium | 0.0196 | [-0.0145, 0.0558] |
| capm | `r2_histories__tabfm__early_concat_labelnull` | sem_intensity | 0.8756 | [-0.9900, 0.8721] |
| capm | `r2_histories__tabfm__early_concat_labelnull` | sem_premium | 0.0198 | [-0.0148, 0.0559] |
| capm | `r2_histories__exaone__late` | sem_intensity | 0.8584 | [-0.9900, 0.8769] |
| capm | `r2_histories__exaone__late` | sem_premium | 0.0193 | [-0.0136, 0.0557] |
| capm | `r2_histories__exaone__item_first_concat` | sem_intensity | 0.8894 | [-0.9900, 0.8749] |
| capm | `r2_histories__exaone__item_first_concat` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r2_histories__exaone__item_first_mean` | sem_intensity | 0.8894 | [-0.9900, 0.8748] |
| capm | `r2_histories__exaone__item_first_mean` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r2_histories__exaone__item_last_concat` | sem_intensity | 0.8655 | [-0.9900, 0.8729] |
| capm | `r2_histories__exaone__item_last_concat` | sem_premium | 0.0194 | [-0.0139, 0.0558] |
| capm | `r3_broad__direct` | sem_intensity | 0.8792 | [-0.9900, 0.8760] |
| capm | `r3_broad__direct` | sem_premium | 0.0199 | [-0.0143, 0.0560] |
| capm | `r3_broad__mahalanobis_lw` | sem_intensity | 0.4851 | [-0.8598, 0.8793] |
| capm | `r3_broad__mahalanobis_lw` | sem_premium | 0.0181 | [-0.0136, 0.0516] |
| capm | `r3_broad__pca16` | sem_intensity | 0.8339 | [-0.9900, 0.8770] |
| capm | `r3_broad__pca16` | sem_premium | 0.0193 | [-0.0142, 0.0558] |
| capm | `r3_broad__autoencoder` | sem_intensity | 0.8565 | [-0.9900, 0.8721] |
| capm | `r3_broad__autoencoder` | sem_premium | 0.0197 | [-0.0145, 0.0565] |
| capm | `r3_broad__random_autoencoder` | sem_intensity | 0.8685 | [-0.9900, 0.8757] |
| capm | `r3_broad__random_autoencoder` | sem_premium | 0.0200 | [-0.0149, 0.0561] |
| capm | `r3_broad__supervised_mlp16` | sem_intensity | 0.7168 | [-0.9900, 0.8761] |
| capm | `r3_broad__supervised_mlp16` | sem_premium | 0.0186 | [-0.0130, 0.0543] |
| capm | `r3_broad__tabpfn_fast__late` | sem_intensity | 0.8565 | [-0.9900, 0.8748] |
| capm | `r3_broad__tabpfn_fast__late` | sem_premium | 0.0192 | [-0.0138, 0.0556] |
| capm | `r3_broad__tabpfn_full__late` | sem_intensity | 0.8566 | [-0.9900, 0.8746] |
| capm | `r3_broad__tabpfn_full__late` | sem_premium | 0.0189 | [-0.0135, 0.0550] |
| capm | `r3_broad__tabfm__early_concat` | sem_intensity | 0.8645 | [-0.9900, 0.8723] |
| capm | `r3_broad__tabfm__early_concat` | sem_premium | 0.0195 | [-0.0140, 0.0559] |
| capm | `r3_broad__tabfm__early_mean` | sem_intensity | 0.8636 | [-0.9900, 0.8722] |
| capm | `r3_broad__tabfm__early_mean` | sem_premium | 0.0194 | [-0.0140, 0.0559] |
| capm | `r3_broad__tabfm__late` | sem_intensity | 0.8783 | [-0.9900, 0.8739] |
| capm | `r3_broad__tabfm__late` | sem_premium | 0.0197 | [-0.0144, 0.0559] |
| capm | `r3_broad__tabfm__early_concat_labelnull` | sem_intensity | 0.8728 | [-0.9900, 0.8738] |
| capm | `r3_broad__tabfm__early_concat_labelnull` | sem_premium | 0.0197 | [-0.0147, 0.0560] |
| capm | `r3_broad__exaone__late` | sem_intensity | 0.8575 | [-0.9900, 0.8773] |
| capm | `r3_broad__exaone__late` | sem_premium | 0.0194 | [-0.0137, 0.0556] |
| capm | `r3_broad__exaone__item_first_concat` | sem_intensity | 0.8895 | [-0.9900, 0.8749] |
| capm | `r3_broad__exaone__item_first_concat` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r3_broad__exaone__item_first_mean` | sem_intensity | 0.8895 | [-0.9900, 0.8749] |
| capm | `r3_broad__exaone__item_first_mean` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r3_broad__exaone__item_last_concat` | sem_intensity | 0.8632 | [-0.9900, 0.8732] |
| capm | `r3_broad__exaone__item_last_concat` | sem_premium | 0.0194 | [-0.0139, 0.0558] |
| capm | `r2_histories@income_assets__direct` | sem_intensity | 0.8724 | [-0.9900, 0.8725] |
| capm | `r2_histories@income_assets__direct` | sem_premium | 0.0199 | [-0.0151, 0.0557] |
| capm | `r2_histories@income_assets__mahalanobis_lw` | sem_intensity | 0.3992 | [-0.4621, 0.8344] |
| capm | `r2_histories@income_assets__mahalanobis_lw` | sem_premium | 0.0159 | [-0.0052, 0.0538] |
| capm | `r2_histories@income_assets__pca16` | sem_intensity | 0.8862 | [-0.9900, 0.8732] |
| capm | `r2_histories@income_assets__pca16` | sem_premium | 0.0199 | [-0.0152, 0.0557] |
| capm | `r2_histories@income_assets__autoencoder` | sem_intensity | 0.8910 | [-0.9900, 0.8754] |
| capm | `r2_histories@income_assets__autoencoder` | sem_premium | 0.0202 | [-0.0153, 0.0575] |
| capm | `r2_histories@income_assets__random_autoencoder` | sem_intensity | 0.8762 | [-0.9900, 0.8715] |
| capm | `r2_histories@income_assets__random_autoencoder` | sem_premium | 0.0197 | [-0.0148, 0.0558] |
| capm | `r2_histories@income_assets__supervised_mlp16` | sem_intensity | 0.8539 | [-0.9900, 0.8710] |
| capm | `r2_histories@income_assets__supervised_mlp16` | sem_premium | 0.0198 | [-0.0151, 0.0560] |
| capm | `r2_histories@income_assets__tabpfn_fast__late` | sem_intensity | 0.8683 | [-0.9900, 0.8717] |
| capm | `r2_histories@income_assets__tabpfn_fast__late` | sem_premium | 0.0196 | [-0.0142, 0.0559] |
| capm | `r2_histories@income_assets__tabpfn_full__late` | sem_intensity | 0.8445 | [-0.9900, 0.8705] |
| capm | `r2_histories@income_assets__tabpfn_full__late` | sem_premium | 0.0193 | [-0.0137, 0.0560] |
| capm | `r2_histories@income_assets__tabfm__early_concat` | sem_intensity | 0.8380 | [-0.9900, 0.8723] |
| capm | `r2_histories@income_assets__tabfm__early_concat` | sem_premium | 0.0193 | [-0.0138, 0.0560] |
| capm | `r2_histories@income_assets__tabfm__early_mean` | sem_intensity | 0.8378 | [-0.9900, 0.8725] |
| capm | `r2_histories@income_assets__tabfm__early_mean` | sem_premium | 0.0193 | [-0.0138, 0.0560] |
| capm | `r2_histories@income_assets__tabfm__late` | sem_intensity | 0.8626 | [-0.9900, 0.8728] |
| capm | `r2_histories@income_assets__tabfm__late` | sem_premium | 0.0197 | [-0.0144, 0.0561] |
| capm | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_intensity | 0.8659 | [-0.9900, 0.8721] |
| capm | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_premium | 0.0197 | [-0.0146, 0.0560] |
| capm | `r2_histories@income_assets__exaone__late` | sem_intensity | 0.8544 | [-0.9900, 0.8713] |
| capm | `r2_histories@income_assets__exaone__late` | sem_premium | 0.0193 | [-0.0139, 0.0559] |
| capm | `r2_histories@income_assets__exaone__item_first_concat` | sem_intensity | 0.8894 | [-0.9900, 0.8749] |
| capm | `r2_histories@income_assets__exaone__item_first_concat` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r2_histories@income_assets__exaone__item_first_mean` | sem_intensity | 0.8894 | [-0.9900, 0.8748] |
| capm | `r2_histories@income_assets__exaone__item_first_mean` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| capm | `r2_histories@income_assets__exaone__item_last_concat` | sem_intensity | 0.8708 | [-0.9900, 0.8728] |
| capm | `r2_histories@income_assets__exaone__item_last_concat` | sem_premium | 0.0197 | [-0.0143, 0.0559] |
| capm | `uniform_network` | sem_intensity | 0.8895 | [-0.9900, 0.8749] |
| capm | `uniform_network` | sem_premium | 0.0197 | [-0.0145, 0.0559] |
| ff6 | `fernandez_market_cap_assets` | sem_intensity | 0.7589 | [-0.9900, 0.8993] |
| ff6 | `fernandez_market_cap_assets` | sem_premium | 0.0168 | [-0.0123, 0.0487] |
| ff6 | `fernandez_market_to_book` | sem_intensity | 0.7229 | [-0.9900, 0.8977] |
| ff6 | `fernandez_market_to_book` | sem_premium | 0.0168 | [-0.0119, 0.0468] |
| ff6 | `fernandez_dividend_yield` | sem_intensity | 0.7912 | [-0.9900, 0.9039] |
| ff6 | `fernandez_dividend_yield` | sem_premium | 0.0177 | [-0.0143, 0.0497] |
| ff6 | `fernandez_debt_maturity` | sem_intensity | 0.7473 | [-0.9900, 0.9058] |
| ff6 | `fernandez_debt_maturity` | sem_premium | 0.0165 | [-0.0115, 0.0472] |
| ff6 | `fernandez_joint` | sem_intensity | 0.7662 | [-0.9900, 0.9011] |
| ff6 | `fernandez_joint` | sem_premium | 0.0167 | [-0.0115, 0.0468] |
| ff6 | `r2_histories__direct` | sem_intensity | 0.7843 | [-0.9900, 0.9039] |
| ff6 | `r2_histories__direct` | sem_premium | 0.0170 | [-0.0115, 0.0489] |
| ff6 | `r2_histories__mahalanobis_lw` | sem_intensity | 0.5422 | [-0.8450, 0.9028] |
| ff6 | `r2_histories__mahalanobis_lw` | sem_premium | 0.0174 | [-0.0114, 0.0483] |
| ff6 | `r2_histories__pca16` | sem_intensity | 0.7952 | [-0.9900, 0.9044] |
| ff6 | `r2_histories__pca16` | sem_premium | 0.0172 | [-0.0121, 0.0486] |
| ff6 | `r2_histories__autoencoder` | sem_intensity | 0.7838 | [-0.9900, 0.9024] |
| ff6 | `r2_histories__autoencoder` | sem_premium | 0.0170 | [-0.0118, 0.0485] |
| ff6 | `r2_histories__random_autoencoder` | sem_intensity | 0.7772 | [-0.9900, 0.9023] |
| ff6 | `r2_histories__random_autoencoder` | sem_premium | 0.0169 | [-0.0115, 0.0488] |
| ff6 | `r2_histories__supervised_mlp16` | sem_intensity | 0.8109 | [-0.9900, 0.9042] |
| ff6 | `r2_histories__supervised_mlp16` | sem_premium | 0.0172 | [-0.0116, 0.0485] |
| ff6 | `r2_histories__tabpfn_fast__late` | sem_intensity | 0.7675 | [-0.9900, 0.9078] |
| ff6 | `r2_histories__tabpfn_fast__late` | sem_premium | 0.0166 | [-0.0109, 0.0470] |
| ff6 | `r2_histories__tabpfn_full__late` | sem_intensity | 0.7781 | [-0.9900, 0.9055] |
| ff6 | `r2_histories__tabpfn_full__late` | sem_premium | 0.0168 | [-0.0108, 0.0486] |
| ff6 | `r2_histories__tabfm__early_concat` | sem_intensity | 0.7740 | [-0.9900, 0.9065] |
| ff6 | `r2_histories__tabfm__early_concat` | sem_premium | 0.0167 | [-0.0114, 0.0473] |
| ff6 | `r2_histories__tabfm__early_mean` | sem_intensity | 0.7740 | [-0.9900, 0.9067] |
| ff6 | `r2_histories__tabfm__early_mean` | sem_premium | 0.0167 | [-0.0114, 0.0473] |
| ff6 | `r2_histories__tabfm__late` | sem_intensity | 0.7801 | [-0.9900, 0.9058] |
| ff6 | `r2_histories__tabfm__late` | sem_premium | 0.0167 | [-0.0110, 0.0473] |
| ff6 | `r2_histories__tabfm__early_concat_labelnull` | sem_intensity | 0.7792 | [-0.9900, 0.9045] |
| ff6 | `r2_histories__tabfm__early_concat_labelnull` | sem_premium | 0.0168 | [-0.0112, 0.0475] |
| ff6 | `r2_histories__exaone__late` | sem_intensity | 0.7632 | [-0.9900, 0.9076] |
| ff6 | `r2_histories__exaone__late` | sem_premium | 0.0166 | [-0.0109, 0.0472] |
| ff6 | `r2_histories__exaone__item_first_concat` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r2_histories__exaone__item_first_concat` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r2_histories__exaone__item_first_mean` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r2_histories__exaone__item_first_mean` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r2_histories__exaone__item_last_concat` | sem_intensity | 0.7735 | [-0.9900, 0.9063] |
| ff6 | `r2_histories__exaone__item_last_concat` | sem_premium | 0.0167 | [-0.0110, 0.0473] |
| ff6 | `r3_broad__direct` | sem_intensity | 0.7739 | [-0.9900, 0.9039] |
| ff6 | `r3_broad__direct` | sem_premium | 0.0167 | [-0.0112, 0.0474] |
| ff6 | `r3_broad__mahalanobis_lw` | sem_intensity | 0.5587 | [-0.9517, 0.8988] |
| ff6 | `r3_broad__mahalanobis_lw` | sem_premium | 0.0170 | [-0.0116, 0.0471] |
| ff6 | `r3_broad__pca16` | sem_intensity | 0.7682 | [-0.9900, 0.9044] |
| ff6 | `r3_broad__pca16` | sem_premium | 0.0166 | [-0.0114, 0.0478] |
| ff6 | `r3_broad__autoencoder` | sem_intensity | 0.7735 | [-0.9900, 0.9029] |
| ff6 | `r3_broad__autoencoder` | sem_premium | 0.0167 | [-0.0118, 0.0476] |
| ff6 | `r3_broad__random_autoencoder` | sem_intensity | 0.7622 | [-0.9900, 0.9012] |
| ff6 | `r3_broad__random_autoencoder` | sem_premium | 0.0166 | [-0.0113, 0.0446] |
| ff6 | `r3_broad__supervised_mlp16` | sem_intensity | 0.7058 | [-0.9900, 0.9086] |
| ff6 | `r3_broad__supervised_mlp16` | sem_premium | 0.0165 | [-0.0114, 0.0482] |
| ff6 | `r3_broad__tabpfn_fast__late` | sem_intensity | 0.7734 | [-0.9900, 0.9080] |
| ff6 | `r3_broad__tabpfn_fast__late` | sem_premium | 0.0168 | [-0.0109, 0.0486] |
| ff6 | `r3_broad__tabpfn_full__late` | sem_intensity | 0.7768 | [-0.9900, 0.9062] |
| ff6 | `r3_broad__tabpfn_full__late` | sem_premium | 0.0168 | [-0.0108, 0.0487] |
| ff6 | `r3_broad__tabfm__early_concat` | sem_intensity | 0.7736 | [-0.9900, 0.9057] |
| ff6 | `r3_broad__tabfm__early_concat` | sem_premium | 0.0167 | [-0.0114, 0.0474] |
| ff6 | `r3_broad__tabfm__early_mean` | sem_intensity | 0.7736 | [-0.9900, 0.9057] |
| ff6 | `r3_broad__tabfm__early_mean` | sem_premium | 0.0167 | [-0.0115, 0.0474] |
| ff6 | `r3_broad__tabfm__late` | sem_intensity | 0.7798 | [-0.9900, 0.9053] |
| ff6 | `r3_broad__tabfm__late` | sem_premium | 0.0167 | [-0.0111, 0.0474] |
| ff6 | `r3_broad__tabfm__early_concat_labelnull` | sem_intensity | 0.7733 | [-0.9900, 0.9034] |
| ff6 | `r3_broad__tabfm__early_concat_labelnull` | sem_premium | 0.0167 | [-0.0112, 0.0474] |
| ff6 | `r3_broad__exaone__late` | sem_intensity | 0.7630 | [-0.9900, 0.9081] |
| ff6 | `r3_broad__exaone__late` | sem_premium | 0.0167 | [-0.0108, 0.0472] |
| ff6 | `r3_broad__exaone__item_first_concat` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r3_broad__exaone__item_first_concat` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r3_broad__exaone__item_first_mean` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r3_broad__exaone__item_first_mean` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r3_broad__exaone__item_last_concat` | sem_intensity | 0.7735 | [-0.9900, 0.9064] |
| ff6 | `r3_broad__exaone__item_last_concat` | sem_premium | 0.0167 | [-0.0109, 0.0473] |
| ff6 | `r2_histories@income_assets__direct` | sem_intensity | 0.7843 | [-0.9900, 0.9034] |
| ff6 | `r2_histories@income_assets__direct` | sem_premium | 0.0170 | [-0.0116, 0.0489] |
| ff6 | `r2_histories@income_assets__mahalanobis_lw` | sem_intensity | 0.5130 | [-0.7738, 0.9037] |
| ff6 | `r2_histories@income_assets__mahalanobis_lw` | sem_premium | 0.0174 | [-0.0121, 0.0490] |
| ff6 | `r2_histories@income_assets__pca16` | sem_intensity | 0.7893 | [-0.9900, 0.9028] |
| ff6 | `r2_histories@income_assets__pca16` | sem_premium | 0.0171 | [-0.0119, 0.0488] |
| ff6 | `r2_histories@income_assets__autoencoder` | sem_intensity | 0.7841 | [-0.9900, 0.9032] |
| ff6 | `r2_histories@income_assets__autoencoder` | sem_premium | 0.0170 | [-0.0120, 0.0486] |
| ff6 | `r2_histories@income_assets__random_autoencoder` | sem_intensity | 0.7773 | [-0.9900, 0.9027] |
| ff6 | `r2_histories@income_assets__random_autoencoder` | sem_premium | 0.0169 | [-0.0115, 0.0487] |
| ff6 | `r2_histories@income_assets__supervised_mlp16` | sem_intensity | 0.8099 | [-0.9900, 0.8999] |
| ff6 | `r2_histories@income_assets__supervised_mlp16` | sem_premium | 0.0178 | [-0.0146, 0.0492] |
| ff6 | `r2_histories@income_assets__tabpfn_fast__late` | sem_intensity | 0.7732 | [-0.9900, 0.9059] |
| ff6 | `r2_histories@income_assets__tabpfn_fast__late` | sem_premium | 0.0167 | [-0.0111, 0.0474] |
| ff6 | `r2_histories@income_assets__tabpfn_full__late` | sem_intensity | 0.7633 | [-0.9900, 0.9069] |
| ff6 | `r2_histories@income_assets__tabpfn_full__late` | sem_premium | 0.0167 | [-0.0109, 0.0474] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat` | sem_intensity | 0.7833 | [-0.9900, 0.9077] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat` | sem_premium | 0.0170 | [-0.0123, 0.0487] |
| ff6 | `r2_histories@income_assets__tabfm__early_mean` | sem_intensity | 0.7831 | [-0.9900, 0.9077] |
| ff6 | `r2_histories@income_assets__tabfm__early_mean` | sem_premium | 0.0170 | [-0.0124, 0.0487] |
| ff6 | `r2_histories@income_assets__tabfm__late` | sem_intensity | 0.7788 | [-0.9900, 0.9041] |
| ff6 | `r2_histories@income_assets__tabfm__late` | sem_premium | 0.0168 | [-0.0111, 0.0475] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_intensity | 0.7730 | [-0.9900, 0.9044] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_premium | 0.0168 | [-0.0112, 0.0475] |
| ff6 | `r2_histories@income_assets__exaone__late` | sem_intensity | 0.7732 | [-0.9900, 0.9062] |
| ff6 | `r2_histories@income_assets__exaone__late` | sem_premium | 0.0167 | [-0.0110, 0.0474] |
| ff6 | `r2_histories@income_assets__exaone__item_first_concat` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r2_histories@income_assets__exaone__item_first_concat` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r2_histories@income_assets__exaone__item_first_mean` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `r2_histories@income_assets__exaone__item_first_mean` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
| ff6 | `r2_histories@income_assets__exaone__item_last_concat` | sem_intensity | 0.7794 | [-0.9900, 0.9052] |
| ff6 | `r2_histories@income_assets__exaone__item_last_concat` | sem_premium | 0.0167 | [-0.0111, 0.0473] |
| ff6 | `uniform_network` | sem_intensity | 0.7795 | [-0.9900, 0.9041] |
| ff6 | `uniform_network` | sem_premium | 0.0167 | [-0.0112, 0.0473] |
