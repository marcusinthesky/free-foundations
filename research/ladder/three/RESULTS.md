# Cross-sectional ladder: `three` arm (market_cap_assets, market_to_book, dividend_yield)

All rows use the same 395 firms, median quarterly excess returns 2016-2025 and
MM exposures. Each spatial row estimates one coefficient for one combined network.
Information criteria are conditional on generated exposures and W (n = firms).
Rows with equal parameter counts have identical AIC/BIC/HQIC rankings
(ΔIC = -2 ΔlogL), so the criteria add information only across nonspatial versus
spatial rows and CAPM versus FF5+Mom exposures. Not ranked against the other arm.

## CAPM exposures, SEM-ML

Nonspatial OLS: log-likelihood 881.876, AIC -1759.75, BIC -1751.79, HQIC -1756.60.

| Network | Rung | Kernel | λ (p) | Premium (p) | logL - OLS | logL - joint | BIC | Eff. nbrs | Placebo p | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `fernandez_market_cap_assets` | r0_single | exp | 0.957 (0.000) | 0.0141 (0.000) | +39.185 | +2.531 | -1824.19 | 0.888 | 0.010 | False |
| `fernandez_market_cap_assets` | r0_single | median | 0.953 (0.000) | 0.0141 (0.000) | +34.878 | -1.776 | -1815.57 | 0.940 | 0.010 | False |
| `fernandez_market_cap_assets` | r0_single | matched | 0.954 (0.000) | 0.0141 (0.000) | +35.097 | -1.557 | -1816.01 | 0.938 | 0.010 | False |
| `fernandez_market_to_book` | r0_single | exp | 0.952 (0.000) | 0.0138 (0.000) | +37.428 | +0.773 | -1820.67 | 0.884 | 0.010 | False |
| `fernandez_market_to_book` | r0_single | median | 0.950 (0.000) | 0.0139 (0.000) | +33.693 | -2.961 | -1813.20 | 0.936 | 0.010 | False |
| `fernandez_market_to_book` | r0_single | matched | 0.950 (0.000) | 0.0139 (0.000) | +33.581 | -3.074 | -1812.98 | 0.938 | 0.010 | False |
| `fernandez_dividend_yield` | r0_single | exp | 0.953 (0.000) | 0.0137 (0.000) | +31.690 | -4.964 | -1809.20 | 0.885 | 0.010 | False |
| `fernandez_dividend_yield` | r0_single | median | 0.951 (0.000) | 0.0138 (0.000) | +29.350 | -7.304 | -1804.51 | 0.937 | 0.010 | False |
| `fernandez_dividend_yield` | r0_single | matched | 0.951 (0.000) | 0.0138 (0.000) | +29.321 | -7.333 | -1804.46 | 0.938 | 0.010 | False |
| `fernandez_joint` | r1_joint | exp | 0.956 (0.000) | 0.0139 (0.000) | +36.654 | +0.000 | -1819.12 | 0.938 | 0.010 | False |
| `fernandez_joint` | r1_joint | median | 0.952 (0.000) | 0.0140 (0.000) | +32.804 | -3.850 | -1811.42 | 0.967 | 0.010 | False |
| `fernandez_joint` | r1_joint | matched | 0.956 (0.000) | 0.0139 (0.000) | +36.654 | +0.000 | -1819.12 | 0.938 | 0.010 | False |
| `r2_histories__direct` | r1_joint | exp | 0.951 (0.000) | 0.0133 (0.000) | +26.545 | -10.109 | -1798.91 | 0.934 | 0.010 | False |
| `r2_histories__direct` | r1_joint | median | 0.954 (0.000) | 0.0131 (0.000) | +27.667 | -8.987 | -1801.15 | 0.898 | 0.010 | False |
| `r2_histories__direct` | r1_joint | matched | 0.951 (0.000) | 0.0134 (0.000) | +26.427 | -10.227 | -1798.67 | 0.938 | 0.010 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | exp | 0.921 (0.000) | 0.0130 (0.000) | +31.244 | -5.410 | -1808.30 | 0.607 | 0.010 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | median | 0.943 (0.000) | 0.0137 (0.000) | +27.002 | -9.652 | -1799.82 | 0.859 | 0.010 | False |
| `r2_histories__mahalanobis_lw` | r1_joint | matched | 0.940 (0.000) | 0.0141 (0.000) | +24.760 | -11.895 | -1795.33 | 0.938 | 0.010 | False |
| `r2_histories__pca16` | r2_histories | exp | 0.954 (0.000) | 0.0133 (0.000) | +26.684 | -9.970 | -1799.18 | 0.919 | 0.010 | False |
| `r2_histories__pca16` | r2_histories | median | 0.956 (0.000) | 0.0131 (0.000) | +27.685 | -8.969 | -1801.18 | 0.881 | 0.010 | False |
| `r2_histories__pca16` | r2_histories | matched | 0.953 (0.000) | 0.0134 (0.000) | +26.137 | -10.517 | -1798.09 | 0.938 | 0.010 | False |
| `r2_histories__autoencoder` | r2_histories | exp | 0.953 (0.000) | 0.0134 (0.000) | +26.054 | -10.600 | -1797.92 | 0.914 | 0.010 | False |
| `r2_histories__autoencoder` | r2_histories | median | 0.956 (0.000) | 0.0131 (0.000) | +27.334 | -9.321 | -1800.48 | 0.842 | 0.010 | False |
| `r2_histories__autoencoder` | r2_histories | matched | 0.952 (0.000) | 0.0135 (0.000) | +25.534 | -11.121 | -1796.88 | 0.938 | 0.010 | False |
| `r2_histories__random_autoencoder` | r2_histories | exp | 0.942 (0.000) | 0.0135 (0.000) | +24.909 | -11.746 | -1795.63 | 0.945 | 0.010 | False |
| `r2_histories__random_autoencoder` | r2_histories | median | 0.945 (0.000) | 0.0130 (0.000) | +26.705 | -9.949 | -1799.23 | 0.862 | 0.010 | False |
| `r2_histories__random_autoencoder` | r2_histories | matched | 0.943 (0.000) | 0.0135 (0.000) | +25.085 | -11.570 | -1795.98 | 0.938 | 0.010 | False |
| `r2_histories__supervised_mlp16` | r2_histories | exp | 0.968 (0.000) | 0.0135 (0.000) | +31.702 | -4.952 | -1809.22 | 0.826 | 0.010 | False |
| `r2_histories__supervised_mlp16` | r2_histories | median | 0.961 (0.000) | 0.0133 (0.000) | +36.372 | -0.282 | -1818.56 | 0.647 | 0.010 | False |
| `r2_histories__supervised_mlp16` | r2_histories | matched | 0.963 (0.000) | 0.0138 (0.000) | +27.593 | -9.061 | -1801.00 | 0.938 | 0.010 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | exp | 0.955 (0.000) | 0.0139 (0.000) | +26.087 | -10.568 | -1797.99 | 0.971 | 0.010 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | median | 0.965 (0.000) | 0.0136 (0.000) | +30.538 | -6.116 | -1806.89 | 0.848 | 0.010 | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | matched | 0.959 (0.000) | 0.0138 (0.000) | +27.681 | -8.974 | -1801.18 | 0.938 | 0.010 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | exp | 0.958 (0.000) | 0.0139 (0.000) | +26.437 | -10.217 | -1798.69 | 0.945 | 0.010 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | median | 0.964 (0.000) | 0.0137 (0.000) | +29.128 | -7.527 | -1804.07 | 0.851 | 0.010 | False |
| `r2_histories__tabpfn_full__late` | r2_histories | matched | 0.958 (0.000) | 0.0139 (0.000) | +26.713 | -9.941 | -1799.24 | 0.938 | 0.010 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | exp | 0.953 (0.000) | 0.0139 (0.000) | +26.136 | -10.519 | -1798.09 | 0.975 | 0.010 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | median | 0.962 (0.000) | 0.0136 (0.000) | +30.105 | -6.549 | -1806.03 | 0.899 | 0.010 | False |
| `r2_histories__tabfm__early_concat` | r2_histories | matched | 0.959 (0.000) | 0.0137 (0.000) | +28.401 | -8.253 | -1802.62 | 0.938 | 0.010 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | exp | 0.953 (0.000) | 0.0139 (0.000) | +26.165 | -10.489 | -1798.15 | 0.975 | 0.010 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | median | 0.962 (0.000) | 0.0136 (0.000) | +30.143 | -6.511 | -1806.10 | 0.899 | 0.010 | False |
| `r2_histories__tabfm__early_mean` | r2_histories | matched | 0.959 (0.000) | 0.0137 (0.000) | +28.416 | -8.238 | -1802.65 | 0.938 | 0.010 | False |
| `r2_histories__tabfm__late` | r2_histories | exp | 0.951 (0.000) | 0.0140 (0.000) | +24.697 | -11.957 | -1795.21 | 0.992 | 0.010 | False |
| `r2_histories__tabfm__late` | r2_histories | median | 0.970 (0.000) | 0.0131 (0.000) | +33.967 | -2.687 | -1813.75 | 0.841 | 0.010 | False |
| `r2_histories__tabfm__late` | r2_histories | matched | 0.964 (0.000) | 0.0135 (0.000) | +29.183 | -7.471 | -1804.18 | 0.938 | 0.010 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | exp | 0.942 (0.000) | 0.0142 (0.000) | +23.247 | -13.407 | -1792.31 | 0.996 | 0.010 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | median | 0.952 (0.000) | 0.0136 (0.000) | +27.345 | -9.309 | -1800.51 | 0.889 | 0.010 | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | matched | 0.949 (0.000) | 0.0138 (0.000) | +25.960 | -10.694 | -1797.74 | 0.938 | 0.010 | False |
| `r2_histories__exaone__late` | r2_histories | exp | 0.962 (0.000) | 0.0139 (0.000) | +27.452 | -9.202 | -1800.72 | 0.958 | 0.010 | False |
| `r2_histories__exaone__late` | r2_histories | median | 0.972 (0.000) | 0.0134 (0.000) | +36.073 | -0.581 | -1817.96 | 0.744 | 0.010 | False |
| `r2_histories__exaone__late` | r2_histories | matched | 0.964 (0.000) | 0.0138 (0.000) | +28.604 | -8.051 | -1803.02 | 0.938 | 0.010 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.493 | -14.161 | -1790.80 | 1.000 | 0.010 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | median | 0.939 (0.000) | 0.0147 (0.000) | +25.428 | -11.227 | -1796.67 | 0.776 | 0.010 | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | matched | 0.939 (0.000) | 0.0145 (0.000) | +24.169 | -12.485 | -1794.15 | 0.938 | 0.010 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.497 | -14.158 | -1790.81 | 1.000 | 0.010 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | median | 0.938 (0.000) | 0.0148 (0.000) | +25.350 | -11.304 | -1796.52 | 0.766 | 0.010 | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | matched | 0.939 (0.000) | 0.0145 (0.000) | +24.129 | -12.525 | -1794.07 | 0.938 | 0.010 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | exp | 0.950 (0.000) | 0.0140 (0.000) | +25.970 | -10.684 | -1797.75 | 0.979 | 0.010 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | median | 0.963 (0.000) | 0.0136 (0.000) | +32.319 | -4.335 | -1810.45 | 0.845 | 0.010 | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | matched | 0.957 (0.000) | 0.0138 (0.000) | +28.563 | -8.092 | -1802.94 | 0.938 | 0.010 | False |
| `r3_broad__direct` | r3_broad | exp | 0.941 (0.000) | 0.0141 (0.000) | +23.433 | -13.221 | -1792.68 | 0.991 | 0.010 | False |
| `r3_broad__direct` | r3_broad | median | 0.940 (0.000) | 0.0141 (0.000) | +23.165 | -13.489 | -1792.15 | 0.995 | 0.010 | False |
| `r3_broad__direct` | r3_broad | matched | 0.944 (0.000) | 0.0138 (0.000) | +24.914 | -11.740 | -1795.64 | 0.938 | 0.010 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | exp | 0.902 (0.000) | 0.0140 (0.000) | +24.909 | -11.745 | -1795.63 | 0.063 | 0.030 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | median | 0.932 (0.000) | 0.0143 (0.000) | +22.956 | -13.698 | -1791.73 | 0.990 | 0.010 | False |
| `r3_broad__mahalanobis_lw` | r3_broad | matched | 0.921 (0.000) | 0.0142 (0.000) | +23.606 | -13.048 | -1793.03 | 0.938 | 0.010 | False |
| `r3_broad__pca16` | r3_broad | exp | 0.944 (0.000) | 0.0137 (0.000) | +24.519 | -12.136 | -1794.85 | 0.924 | 0.010 | False |
| `r3_broad__pca16` | r3_broad | median | 0.943 (0.000) | 0.0139 (0.000) | +23.971 | -12.683 | -1793.76 | 0.961 | 0.010 | False |
| `r3_broad__pca16` | r3_broad | matched | 0.944 (0.000) | 0.0138 (0.000) | +24.339 | -12.315 | -1794.49 | 0.938 | 0.010 | False |
| `r3_broad__autoencoder` | r3_broad | exp | 0.946 (0.000) | 0.0137 (0.000) | +24.186 | -12.468 | -1794.19 | 0.908 | 0.010 | False |
| `r3_broad__autoencoder` | r3_broad | median | 0.945 (0.000) | 0.0138 (0.000) | +23.782 | -12.872 | -1793.38 | 0.947 | 0.010 | False |
| `r3_broad__autoencoder` | r3_broad | matched | 0.945 (0.000) | 0.0138 (0.000) | +23.892 | -12.762 | -1793.60 | 0.938 | 0.010 | False |
| `r3_broad__random_autoencoder` | r3_broad | exp | 0.939 (0.000) | 0.0140 (0.000) | +23.108 | -13.547 | -1792.03 | 0.958 | 0.040 | False |
| `r3_broad__random_autoencoder` | r3_broad | median | 0.939 (0.000) | 0.0141 (0.000) | +22.992 | -13.662 | -1791.80 | 0.973 | 0.040 | False |
| `r3_broad__random_autoencoder` | r3_broad | matched | 0.939 (0.000) | 0.0140 (0.000) | +23.231 | -13.423 | -1792.28 | 0.938 | 0.040 | False |
| `r3_broad__supervised_mlp16` | r3_broad | exp | 0.958 (0.000) | 0.0133 (0.000) | +29.027 | -7.627 | -1803.87 | 0.881 | 0.010 | False |
| `r3_broad__supervised_mlp16` | r3_broad | median | 0.957 (0.000) | 0.0135 (0.000) | +28.085 | -8.569 | -1801.98 | 0.913 | 0.010 | False |
| `r3_broad__supervised_mlp16` | r3_broad | matched | 0.955 (0.000) | 0.0136 (0.000) | +27.251 | -9.404 | -1800.32 | 0.938 | 0.010 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | exp | 0.955 (0.000) | 0.0139 (0.000) | +26.313 | -10.341 | -1798.44 | 0.970 | 0.010 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | median | 0.966 (0.000) | 0.0135 (0.000) | +30.732 | -5.922 | -1807.28 | 0.859 | 0.010 | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | matched | 0.960 (0.000) | 0.0137 (0.000) | +28.004 | -8.650 | -1801.82 | 0.938 | 0.010 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | exp | 0.960 (0.000) | 0.0138 (0.000) | +27.290 | -9.364 | -1800.39 | 0.943 | 0.010 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | median | 0.967 (0.000) | 0.0135 (0.000) | +30.469 | -6.185 | -1806.75 | 0.846 | 0.010 | False |
| `r3_broad__tabpfn_full__late` | r3_broad | matched | 0.961 (0.000) | 0.0138 (0.000) | +27.506 | -9.148 | -1800.83 | 0.938 | 0.010 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | exp | 0.952 (0.000) | 0.0139 (0.000) | +25.679 | -10.976 | -1797.17 | 0.980 | 0.010 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | median | 0.961 (0.000) | 0.0136 (0.000) | +29.294 | -7.360 | -1804.40 | 0.916 | 0.010 | False |
| `r3_broad__tabfm__early_concat` | r3_broad | matched | 0.959 (0.000) | 0.0137 (0.000) | +28.295 | -8.360 | -1802.40 | 0.938 | 0.010 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | exp | 0.952 (0.000) | 0.0139 (0.000) | +25.765 | -10.890 | -1797.34 | 0.980 | 0.010 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | median | 0.962 (0.000) | 0.0136 (0.000) | +29.540 | -7.115 | -1804.89 | 0.912 | 0.010 | False |
| `r3_broad__tabfm__early_mean` | r3_broad | matched | 0.960 (0.000) | 0.0137 (0.000) | +28.347 | -8.307 | -1802.51 | 0.938 | 0.010 | False |
| `r3_broad__tabfm__late` | r3_broad | exp | 0.950 (0.000) | 0.0140 (0.000) | +24.658 | -11.996 | -1795.13 | 0.993 | 0.010 | False |
| `r3_broad__tabfm__late` | r3_broad | median | 0.969 (0.000) | 0.0132 (0.000) | +33.286 | -3.368 | -1812.39 | 0.856 | 0.010 | False |
| `r3_broad__tabfm__late` | r3_broad | matched | 0.964 (0.000) | 0.0135 (0.000) | +29.225 | -7.429 | -1804.27 | 0.938 | 0.010 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | exp | 0.939 (0.000) | 0.0142 (0.000) | +22.875 | -13.779 | -1791.57 | 0.998 | 0.010 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | median | 0.941 (0.000) | 0.0140 (0.000) | +24.827 | -11.827 | -1795.47 | 0.927 | 0.010 | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | matched | 0.941 (0.000) | 0.0140 (0.000) | +24.656 | -11.999 | -1795.13 | 0.938 | 0.010 | False |
| `r3_broad__exaone__late` | r3_broad | exp | 0.962 (0.000) | 0.0138 (0.000) | +27.639 | -9.015 | -1801.09 | 0.957 | 0.010 | False |
| `r3_broad__exaone__late` | r3_broad | median | 0.973 (0.000) | 0.0132 (0.000) | +36.557 | -0.097 | -1818.93 | 0.742 | 0.010 | False |
| `r3_broad__exaone__late` | r3_broad | matched | 0.965 (0.000) | 0.0137 (0.000) | +28.775 | -7.879 | -1803.37 | 0.938 | 0.010 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.489 | -14.166 | -1790.79 | 1.000 | 0.390 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | median | 0.949 (0.000) | 0.0143 (0.000) | +22.542 | -14.112 | -1790.90 | 0.800 | 0.130 | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | matched | 0.946 (0.000) | 0.0143 (0.000) | +22.449 | -14.205 | -1790.71 | 0.938 | 0.230 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.488 | -14.166 | -1790.79 | 1.000 | 0.470 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | median | 0.950 (0.000) | 0.0143 (0.000) | +22.332 | -14.322 | -1790.48 | 0.781 | 0.200 | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | matched | 0.946 (0.000) | 0.0143 (0.000) | +22.375 | -14.279 | -1790.57 | 0.938 | 0.310 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | exp | 0.952 (0.000) | 0.0139 (0.000) | +26.006 | -10.648 | -1797.83 | 0.979 | 0.010 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | median | 0.965 (0.000) | 0.0134 (0.000) | +32.039 | -4.616 | -1809.89 | 0.856 | 0.010 | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | matched | 0.959 (0.000) | 0.0137 (0.000) | +28.646 | -8.008 | -1803.11 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | exp | 0.950 (0.000) | 0.0134 (0.000) | +26.102 | -10.553 | -1798.02 | 0.942 | 0.010 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | median | 0.953 (0.000) | 0.0131 (0.000) | +27.610 | -9.044 | -1801.03 | 0.893 | 0.010 | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | matched | 0.950 (0.000) | 0.0134 (0.000) | +26.267 | -10.387 | -1798.35 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | exp | 0.921 (0.000) | 0.0133 (0.000) | +30.858 | -5.796 | -1807.53 | 0.591 | 0.010 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | median | 0.943 (0.000) | 0.0139 (0.000) | +26.414 | -10.241 | -1798.64 | 0.862 | 0.010 | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | matched | 0.940 (0.000) | 0.0141 (0.000) | +24.477 | -12.177 | -1794.77 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | exp | 0.952 (0.000) | 0.0134 (0.000) | +26.196 | -10.459 | -1798.21 | 0.934 | 0.010 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | median | 0.955 (0.000) | 0.0131 (0.000) | +27.744 | -8.910 | -1801.30 | 0.877 | 0.010 | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | matched | 0.952 (0.000) | 0.0134 (0.000) | +26.083 | -10.571 | -1797.98 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | exp | 0.951 (0.000) | 0.0135 (0.000) | +25.412 | -11.243 | -1796.64 | 0.935 | 0.010 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | median | 0.956 (0.000) | 0.0131 (0.000) | +27.209 | -9.445 | -1800.23 | 0.834 | 0.010 | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | matched | 0.951 (0.000) | 0.0135 (0.000) | +25.354 | -11.300 | -1796.52 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | exp | 0.943 (0.000) | 0.0136 (0.000) | +25.028 | -11.627 | -1795.87 | 0.945 | 0.010 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | median | 0.946 (0.000) | 0.0131 (0.000) | +26.854 | -9.800 | -1799.52 | 0.866 | 0.010 | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | matched | 0.943 (0.000) | 0.0135 (0.000) | +25.220 | -11.434 | -1796.26 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | exp | 0.943 (0.000) | 0.0128 (0.000) | +26.937 | -9.717 | -1799.69 | 0.827 | 0.010 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | median | 0.943 (0.000) | 0.0129 (0.000) | +26.644 | -10.010 | -1799.10 | 0.849 | 0.010 | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | matched | 0.942 (0.000) | 0.0133 (0.000) | +25.163 | -11.491 | -1796.14 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | exp | 0.948 (0.000) | 0.0141 (0.000) | +24.935 | -11.720 | -1795.68 | 0.988 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | median | 0.960 (0.000) | 0.0139 (0.000) | +30.893 | -5.761 | -1807.60 | 0.850 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | matched | 0.955 (0.000) | 0.0140 (0.000) | +27.919 | -8.736 | -1801.65 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | exp | 0.952 (0.000) | 0.0141 (0.000) | +26.694 | -9.960 | -1799.20 | 0.968 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | median | 0.961 (0.000) | 0.0140 (0.000) | +31.663 | -4.992 | -1809.14 | 0.847 | 0.010 | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | matched | 0.956 (0.000) | 0.0140 (0.000) | +28.326 | -8.328 | -1802.47 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | exp | 0.953 (0.000) | 0.0138 (0.000) | +27.702 | -8.952 | -1801.22 | 0.953 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | median | 0.955 (0.000) | 0.0137 (0.000) | +28.774 | -7.880 | -1803.36 | 0.932 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | matched | 0.955 (0.000) | 0.0138 (0.000) | +28.527 | -8.127 | -1802.87 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | exp | 0.953 (0.000) | 0.0138 (0.000) | +27.715 | -8.939 | -1801.25 | 0.953 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | median | 0.955 (0.000) | 0.0137 (0.000) | +28.773 | -7.881 | -1803.36 | 0.932 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | matched | 0.955 (0.000) | 0.0138 (0.000) | +28.522 | -8.132 | -1802.86 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | exp | 0.944 (0.000) | 0.0142 (0.000) | +24.072 | -12.582 | -1793.96 | 0.995 | 0.010 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | median | 0.957 (0.000) | 0.0141 (0.000) | +29.820 | -6.835 | -1805.45 | 0.904 | 0.010 | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | matched | 0.955 (0.000) | 0.0141 (0.000) | +28.380 | -8.274 | -1802.58 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | exp | 0.943 (0.000) | 0.0142 (0.000) | +23.398 | -13.257 | -1792.61 | 0.993 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | median | 0.952 (0.000) | 0.0138 (0.000) | +26.799 | -9.855 | -1799.41 | 0.885 | 0.010 | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | matched | 0.949 (0.000) | 0.0139 (0.000) | +25.502 | -11.152 | -1796.82 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | exp | 0.950 (0.000) | 0.0140 (0.000) | +25.474 | -11.181 | -1796.76 | 0.980 | 0.010 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | median | 0.962 (0.000) | 0.0138 (0.000) | +31.656 | -4.998 | -1809.13 | 0.816 | 0.010 | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | matched | 0.955 (0.000) | 0.0139 (0.000) | +27.731 | -8.923 | -1801.28 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.494 | -14.160 | -1790.80 | 1.000 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | median | 0.940 (0.000) | 0.0147 (0.000) | +25.721 | -10.933 | -1797.26 | 0.771 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | matched | 0.940 (0.000) | 0.0145 (0.000) | +24.334 | -12.320 | -1794.48 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | exp | 0.939 (0.000) | 0.0143 (0.000) | +22.499 | -14.156 | -1790.81 | 1.000 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | median | 0.939 (0.000) | 0.0147 (0.000) | +25.597 | -11.058 | -1797.01 | 0.761 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | matched | 0.939 (0.000) | 0.0145 (0.000) | +24.272 | -12.382 | -1794.36 | 0.938 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | exp | 0.943 (0.000) | 0.0142 (0.000) | +24.274 | -12.380 | -1794.36 | 0.992 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | median | 0.953 (0.000) | 0.0139 (0.000) | +29.017 | -7.638 | -1803.85 | 0.895 | 0.010 | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | matched | 0.950 (0.000) | 0.0140 (0.000) | +27.455 | -9.200 | -1800.72 | 0.938 | 0.010 | False |
| `uniform_network` | reference | none | 0.939 (0.000) | 0.0143 (0.000) | +22.489 | -14.165 | -1790.79 | 1.000 | — | False |

## FF6 exposures, SEM-ML

Nonspatial OLS: log-likelihood 917.642, AIC -1821.28, BIC -1793.43, HQIC -1810.25.

| Network | Rung | Kernel | λ (p) | Premium (p) | logL - OLS | logL - joint | BIC | Eff. nbrs | Placebo p | Boundary |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `fernandez_market_cap_assets` | r0_single | exp | 0.956 (0.000) | 0.0216 (0.000) | +30.660 | +2.954 | -1848.77 | 0.888 | — | False |
| `fernandez_market_cap_assets` | r0_single | median | 0.953 (0.000) | 0.0220 (0.000) | +26.804 | -0.902 | -1841.06 | 0.940 | — | False |
| `fernandez_market_cap_assets` | r0_single | matched | 0.953 (0.000) | 0.0219 (0.000) | +26.999 | -0.707 | -1841.45 | 0.938 | — | False |
| `fernandez_market_to_book` | r0_single | exp | 0.949 (0.000) | 0.0214 (0.000) | +27.622 | -0.084 | -1842.70 | 0.884 | — | False |
| `fernandez_market_to_book` | r0_single | median | 0.948 (0.000) | 0.0218 (0.000) | +24.676 | -3.030 | -1836.81 | 0.936 | — | False |
| `fernandez_market_to_book` | r0_single | matched | 0.947 (0.000) | 0.0218 (0.000) | +24.587 | -3.118 | -1836.63 | 0.938 | — | False |
| `fernandez_dividend_yield` | r0_single | exp | 0.952 (0.000) | 0.0217 (0.000) | +23.525 | -4.181 | -1834.50 | 0.885 | — | False |
| `fernandez_dividend_yield` | r0_single | median | 0.950 (0.000) | 0.0220 (0.000) | +21.550 | -6.155 | -1830.55 | 0.937 | — | False |
| `fernandez_dividend_yield` | r0_single | matched | 0.950 (0.000) | 0.0220 (0.000) | +21.526 | -6.179 | -1830.51 | 0.938 | — | False |
| `fernandez_joint` | r1_joint | exp | 0.954 (0.000) | 0.0216 (0.000) | +27.705 | +0.000 | -1842.86 | 0.938 | — | False |
| `fernandez_joint` | r1_joint | median | 0.951 (0.000) | 0.0219 (0.000) | +24.469 | -3.237 | -1836.39 | 0.967 | — | False |
| `fernandez_joint` | r1_joint | matched | 0.954 (0.000) | 0.0216 (0.000) | +27.705 | +0.000 | -1842.86 | 0.938 | — | False |
| `r2_histories__direct` | r1_joint | exp | 0.947 (0.000) | 0.0221 (0.000) | +18.209 | -9.497 | -1823.87 | 0.934 | — | False |
| `r2_histories__direct` | r1_joint | median | 0.949 (0.000) | 0.0219 (0.000) | +18.886 | -8.819 | -1825.23 | 0.898 | — | False |
| `r2_histories__direct` | r1_joint | matched | 0.947 (0.000) | 0.0221 (0.000) | +18.139 | -9.566 | -1823.73 | 0.938 | — | False |
| `r2_histories__mahalanobis_lw` | r1_joint | exp | 0.916 (0.000) | 0.0212 (0.000) | +19.784 | -7.921 | -1827.02 | 0.607 | — | False |
| `r2_histories__mahalanobis_lw` | r1_joint | median | 0.944 (0.000) | 0.0222 (0.000) | +18.953 | -8.753 | -1825.36 | 0.859 | — | False |
| `r2_histories__mahalanobis_lw` | r1_joint | matched | 0.941 (0.000) | 0.0226 (0.000) | +17.677 | -10.028 | -1822.81 | 0.938 | — | False |
| `r2_histories__pca16` | r2_histories | exp | 0.949 (0.000) | 0.0220 (0.000) | +18.136 | -9.570 | -1823.73 | 0.919 | — | False |
| `r2_histories__pca16` | r2_histories | median | 0.951 (0.000) | 0.0218 (0.000) | +18.716 | -8.989 | -1824.89 | 0.881 | — | False |
| `r2_histories__pca16` | r2_histories | matched | 0.948 (0.000) | 0.0221 (0.000) | +17.828 | -9.877 | -1823.11 | 0.938 | — | False |
| `r2_histories__autoencoder` | r2_histories | exp | 0.946 (0.000) | 0.0222 (0.000) | +17.253 | -10.452 | -1821.96 | 0.914 | — | False |
| `r2_histories__autoencoder` | r2_histories | median | 0.948 (0.000) | 0.0219 (0.000) | +17.817 | -9.889 | -1823.09 | 0.842 | — | False |
| `r2_histories__autoencoder` | r2_histories | matched | 0.945 (0.000) | 0.0223 (0.000) | +17.041 | -10.665 | -1821.54 | 0.938 | — | False |
| `r2_histories__random_autoencoder` | r2_histories | exp | 0.940 (0.000) | 0.0223 (0.000) | +17.219 | -10.486 | -1821.89 | 0.945 | — | False |
| `r2_histories__random_autoencoder` | r2_histories | median | 0.942 (0.000) | 0.0218 (0.000) | +18.222 | -9.483 | -1823.90 | 0.862 | — | False |
| `r2_histories__random_autoencoder` | r2_histories | matched | 0.941 (0.000) | 0.0222 (0.000) | +17.315 | -10.390 | -1822.08 | 0.938 | — | False |
| `r2_histories__supervised_mlp16` | r2_histories | exp | 0.962 (0.000) | 0.0218 (0.000) | +20.724 | -6.981 | -1828.90 | 0.826 | — | False |
| `r2_histories__supervised_mlp16` | r2_histories | median | 0.956 (0.000) | 0.0212 (0.000) | +23.923 | -3.783 | -1835.30 | 0.647 | — | False |
| `r2_histories__supervised_mlp16` | r2_histories | matched | 0.956 (0.000) | 0.0223 (0.000) | +18.351 | -9.355 | -1824.16 | 0.938 | — | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | exp | 0.948 (0.000) | 0.0225 (0.000) | +17.805 | -9.901 | -1823.06 | 0.971 | — | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | median | 0.957 (0.000) | 0.0219 (0.000) | +20.532 | -7.173 | -1828.52 | 0.848 | — | False |
| `r2_histories__tabpfn_fast__late` | r2_histories | matched | 0.952 (0.000) | 0.0223 (0.000) | +18.717 | -8.988 | -1824.89 | 0.938 | — | False |
| `r2_histories__tabpfn_full__late` | r2_histories | exp | 0.950 (0.000) | 0.0224 (0.000) | +17.822 | -9.883 | -1823.10 | 0.945 | — | False |
| `r2_histories__tabpfn_full__late` | r2_histories | median | 0.956 (0.000) | 0.0221 (0.000) | +19.369 | -8.337 | -1826.19 | 0.851 | — | False |
| `r2_histories__tabpfn_full__late` | r2_histories | matched | 0.951 (0.000) | 0.0224 (0.000) | +17.969 | -9.736 | -1823.39 | 0.938 | — | False |
| `r2_histories__tabfm__early_concat` | r2_histories | exp | 0.949 (0.000) | 0.0225 (0.000) | +17.995 | -9.710 | -1823.44 | 0.975 | — | False |
| `r2_histories__tabfm__early_concat` | r2_histories | median | 0.957 (0.000) | 0.0220 (0.000) | +20.505 | -7.200 | -1828.46 | 0.899 | — | False |
| `r2_histories__tabfm__early_concat` | r2_histories | matched | 0.953 (0.000) | 0.0222 (0.000) | +19.388 | -8.317 | -1826.23 | 0.938 | — | False |
| `r2_histories__tabfm__early_mean` | r2_histories | exp | 0.949 (0.000) | 0.0225 (0.000) | +18.010 | -9.695 | -1823.47 | 0.975 | — | False |
| `r2_histories__tabfm__early_mean` | r2_histories | median | 0.957 (0.000) | 0.0220 (0.000) | +20.525 | -7.181 | -1828.50 | 0.899 | — | False |
| `r2_histories__tabfm__early_mean` | r2_histories | matched | 0.953 (0.000) | 0.0222 (0.000) | +19.394 | -8.312 | -1826.24 | 0.938 | — | False |
| `r2_histories__tabfm__late` | r2_histories | exp | 0.946 (0.000) | 0.0226 (0.000) | +17.077 | -10.628 | -1821.61 | 0.992 | — | False |
| `r2_histories__tabfm__late` | r2_histories | median | 0.964 (0.000) | 0.0213 (0.000) | +22.817 | -4.888 | -1833.09 | 0.841 | — | False |
| `r2_histories__tabfm__late` | r2_histories | matched | 0.957 (0.000) | 0.0219 (0.000) | +19.628 | -8.077 | -1826.71 | 0.938 | — | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | exp | 0.940 (0.000) | 0.0228 (0.000) | +16.295 | -11.411 | -1820.04 | 0.996 | — | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | median | 0.947 (0.000) | 0.0223 (0.000) | +18.365 | -9.340 | -1824.18 | 0.889 | — | False |
| `r2_histories__tabfm__early_concat_labelnull` | r2_histories | matched | 0.945 (0.000) | 0.0225 (0.000) | +17.610 | -10.095 | -1822.67 | 0.938 | — | False |
| `r2_histories__exaone__late` | r2_histories | exp | 0.954 (0.000) | 0.0223 (0.000) | +18.430 | -9.275 | -1824.31 | 0.958 | — | False |
| `r2_histories__exaone__late` | r2_histories | median | 0.966 (0.000) | 0.0212 (0.000) | +24.052 | -3.654 | -1835.56 | 0.744 | — | False |
| `r2_histories__exaone__late` | r2_histories | matched | 0.957 (0.000) | 0.0222 (0.000) | +19.083 | -8.623 | -1825.62 | 0.938 | — | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.970 | -11.736 | -1819.39 | 1.000 | — | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | median | 0.938 (0.000) | 0.0229 (0.000) | +16.948 | -10.758 | -1821.35 | 0.776 | — | False |
| `r2_histories__exaone__item_first_concat` | r2_histories | matched | 0.939 (0.000) | 0.0229 (0.000) | +16.524 | -11.181 | -1820.50 | 0.938 | — | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.971 | -11.735 | -1819.40 | 1.000 | — | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | median | 0.937 (0.000) | 0.0229 (0.000) | +16.855 | -10.850 | -1821.16 | 0.766 | — | False |
| `r2_histories__exaone__item_first_mean` | r2_histories | matched | 0.938 (0.000) | 0.0229 (0.000) | +16.491 | -11.214 | -1820.44 | 0.938 | — | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | exp | 0.945 (0.000) | 0.0225 (0.000) | +17.908 | -9.797 | -1823.27 | 0.979 | — | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | median | 0.955 (0.000) | 0.0217 (0.000) | +22.106 | -5.599 | -1831.67 | 0.845 | — | False |
| `r2_histories__exaone__item_last_concat` | r2_histories | matched | 0.950 (0.000) | 0.0222 (0.000) | +19.519 | -8.187 | -1826.49 | 0.938 | — | False |
| `r3_broad__direct` | r3_broad | exp | 0.940 (0.000) | 0.0227 (0.000) | +16.540 | -11.166 | -1820.53 | 0.991 | — | False |
| `r3_broad__direct` | r3_broad | median | 0.940 (0.000) | 0.0228 (0.000) | +16.378 | -11.327 | -1820.21 | 0.995 | — | False |
| `r3_broad__direct` | r3_broad | matched | 0.943 (0.000) | 0.0225 (0.000) | +17.429 | -10.277 | -1822.31 | 0.938 | — | False |
| `r3_broad__mahalanobis_lw` | r3_broad | exp | 0.923 (0.000) | 0.0227 (0.000) | +18.336 | -9.370 | -1824.13 | 0.063 | — | False |
| `r3_broad__mahalanobis_lw` | r3_broad | median | 0.933 (0.000) | 0.0229 (0.000) | +16.377 | -11.329 | -1820.21 | 0.990 | — | False |
| `r3_broad__mahalanobis_lw` | r3_broad | matched | 0.923 (0.000) | 0.0228 (0.000) | +16.951 | -10.754 | -1821.36 | 0.938 | — | False |
| `r3_broad__pca16` | r3_broad | exp | 0.942 (0.000) | 0.0224 (0.000) | +17.078 | -10.628 | -1821.61 | 0.924 | — | False |
| `r3_broad__pca16` | r3_broad | median | 0.941 (0.000) | 0.0226 (0.000) | +16.785 | -10.921 | -1821.02 | 0.961 | — | False |
| `r3_broad__pca16` | r3_broad | matched | 0.941 (0.000) | 0.0225 (0.000) | +16.982 | -10.723 | -1821.42 | 0.938 | — | False |
| `r3_broad__autoencoder` | r3_broad | exp | 0.945 (0.000) | 0.0225 (0.000) | +16.956 | -10.749 | -1821.37 | 0.908 | — | False |
| `r3_broad__autoencoder` | r3_broad | median | 0.943 (0.000) | 0.0226 (0.000) | +16.721 | -10.984 | -1820.90 | 0.947 | — | False |
| `r3_broad__autoencoder` | r3_broad | matched | 0.944 (0.000) | 0.0226 (0.000) | +16.785 | -10.920 | -1821.02 | 0.938 | — | False |
| `r3_broad__random_autoencoder` | r3_broad | exp | 0.937 (0.000) | 0.0227 (0.000) | +16.486 | -11.219 | -1820.43 | 0.958 | — | False |
| `r3_broad__random_autoencoder` | r3_broad | median | 0.938 (0.000) | 0.0228 (0.000) | +16.390 | -11.316 | -1820.23 | 0.973 | — | False |
| `r3_broad__random_autoencoder` | r3_broad | matched | 0.937 (0.000) | 0.0227 (0.000) | +16.589 | -11.117 | -1820.63 | 0.938 | — | False |
| `r3_broad__supervised_mlp16` | r3_broad | exp | 0.953 (0.000) | 0.0219 (0.000) | +19.600 | -8.106 | -1826.65 | 0.881 | — | False |
| `r3_broad__supervised_mlp16` | r3_broad | median | 0.951 (0.000) | 0.0220 (0.000) | +19.035 | -8.670 | -1825.52 | 0.913 | — | False |
| `r3_broad__supervised_mlp16` | r3_broad | matched | 0.950 (0.000) | 0.0222 (0.000) | +18.548 | -9.157 | -1824.55 | 0.938 | — | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | exp | 0.949 (0.000) | 0.0224 (0.000) | +17.929 | -9.776 | -1823.31 | 0.970 | — | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | median | 0.958 (0.000) | 0.0219 (0.000) | +20.592 | -7.114 | -1828.64 | 0.859 | — | False |
| `r3_broad__tabpfn_fast__late` | r3_broad | matched | 0.953 (0.000) | 0.0222 (0.000) | +18.893 | -8.812 | -1825.24 | 0.938 | — | False |
| `r3_broad__tabpfn_full__late` | r3_broad | exp | 0.953 (0.000) | 0.0223 (0.000) | +18.378 | -9.327 | -1824.21 | 0.943 | — | False |
| `r3_broad__tabpfn_full__late` | r3_broad | median | 0.959 (0.000) | 0.0219 (0.000) | +20.304 | -7.401 | -1828.06 | 0.846 | — | False |
| `r3_broad__tabpfn_full__late` | r3_broad | matched | 0.953 (0.000) | 0.0223 (0.000) | +18.500 | -9.205 | -1824.45 | 0.938 | — | False |
| `r3_broad__tabfm__early_concat` | r3_broad | exp | 0.948 (0.000) | 0.0225 (0.000) | +17.767 | -9.939 | -1822.99 | 0.980 | — | False |
| `r3_broad__tabfm__early_concat` | r3_broad | median | 0.955 (0.000) | 0.0220 (0.000) | +20.046 | -7.659 | -1827.55 | 0.916 | — | False |
| `r3_broad__tabfm__early_concat` | r3_broad | matched | 0.953 (0.000) | 0.0222 (0.000) | +19.391 | -8.315 | -1826.23 | 0.938 | — | False |
| `r3_broad__tabfm__early_mean` | r3_broad | exp | 0.948 (0.000) | 0.0225 (0.000) | +17.818 | -9.887 | -1823.09 | 0.980 | — | False |
| `r3_broad__tabfm__early_mean` | r3_broad | median | 0.956 (0.000) | 0.0220 (0.000) | +20.214 | -7.492 | -1827.88 | 0.912 | — | False |
| `r3_broad__tabfm__early_mean` | r3_broad | matched | 0.954 (0.000) | 0.0222 (0.000) | +19.427 | -8.278 | -1826.31 | 0.938 | — | False |
| `r3_broad__tabfm__late` | r3_broad | exp | 0.946 (0.000) | 0.0226 (0.000) | +17.125 | -10.581 | -1821.70 | 0.993 | — | False |
| `r3_broad__tabfm__late` | r3_broad | median | 0.963 (0.000) | 0.0214 (0.000) | +22.696 | -5.009 | -1832.85 | 0.856 | — | False |
| `r3_broad__tabfm__late` | r3_broad | matched | 0.957 (0.000) | 0.0220 (0.000) | +19.874 | -7.832 | -1827.20 | 0.938 | — | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | exp | 0.939 (0.000) | 0.0229 (0.000) | +16.206 | -11.499 | -1819.87 | 0.998 | — | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | median | 0.940 (0.000) | 0.0227 (0.000) | +17.435 | -10.271 | -1822.32 | 0.927 | — | False |
| `r3_broad__tabfm__early_concat_labelnull` | r3_broad | matched | 0.939 (0.000) | 0.0227 (0.000) | +17.326 | -10.380 | -1822.10 | 0.938 | — | False |
| `r3_broad__exaone__late` | r3_broad | exp | 0.955 (0.000) | 0.0223 (0.000) | +18.723 | -8.982 | -1824.90 | 0.957 | — | False |
| `r3_broad__exaone__late` | r3_broad | median | 0.967 (0.000) | 0.0211 (0.000) | +24.823 | -2.883 | -1837.10 | 0.742 | — | False |
| `r3_broad__exaone__late` | r3_broad | matched | 0.958 (0.000) | 0.0222 (0.000) | +19.410 | -8.295 | -1826.27 | 0.938 | — | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.968 | -11.737 | -1819.39 | 1.000 | — | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | median | 0.945 (0.000) | 0.0228 (0.000) | +15.848 | -11.857 | -1819.15 | 0.800 | — | False |
| `r3_broad__exaone__item_first_concat` | r3_broad | matched | 0.943 (0.000) | 0.0228 (0.000) | +15.871 | -11.834 | -1819.20 | 0.938 | — | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.968 | -11.737 | -1819.39 | 1.000 | — | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | median | 0.947 (0.000) | 0.0228 (0.000) | +15.661 | -12.044 | -1818.78 | 0.781 | — | False |
| `r3_broad__exaone__item_first_mean` | r3_broad | matched | 0.944 (0.000) | 0.0229 (0.000) | +15.803 | -11.902 | -1819.06 | 0.938 | — | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | exp | 0.947 (0.000) | 0.0224 (0.000) | +17.991 | -9.714 | -1823.44 | 0.979 | — | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | median | 0.957 (0.000) | 0.0216 (0.000) | +22.056 | -5.649 | -1831.57 | 0.856 | — | False |
| `r3_broad__exaone__item_last_concat` | r3_broad | matched | 0.952 (0.000) | 0.0221 (0.000) | +19.680 | -8.026 | -1826.81 | 0.938 | — | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | exp | 0.946 (0.000) | 0.0222 (0.000) | +17.915 | -9.790 | -1823.28 | 0.942 | — | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | median | 0.949 (0.000) | 0.0219 (0.000) | +18.810 | -8.895 | -1825.07 | 0.893 | — | False |
| `r2_histories@income_assets__direct` | r2_histories@income_assets | matched | 0.946 (0.000) | 0.0222 (0.000) | +18.011 | -9.694 | -1823.48 | 0.938 | — | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | exp | 0.914 (0.000) | 0.0215 (0.000) | +18.985 | -8.720 | -1825.42 | 0.591 | — | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | median | 0.943 (0.000) | 0.0224 (0.000) | +18.266 | -9.440 | -1823.99 | 0.862 | — | False |
| `r2_histories@income_assets__mahalanobis_lw` | r2_histories@income_assets | matched | 0.941 (0.000) | 0.0227 (0.000) | +17.358 | -10.347 | -1822.17 | 0.938 | — | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | exp | 0.947 (0.000) | 0.0222 (0.000) | +17.879 | -9.826 | -1823.21 | 0.934 | — | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | median | 0.950 (0.000) | 0.0218 (0.000) | +18.790 | -8.915 | -1825.03 | 0.877 | — | False |
| `r2_histories@income_assets__pca16` | r2_histories@income_assets | matched | 0.947 (0.000) | 0.0222 (0.000) | +17.815 | -9.890 | -1823.08 | 0.938 | — | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | exp | 0.945 (0.000) | 0.0223 (0.000) | +16.903 | -10.802 | -1821.26 | 0.935 | — | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | median | 0.947 (0.000) | 0.0220 (0.000) | +17.636 | -10.069 | -1822.73 | 0.834 | — | False |
| `r2_histories@income_assets__autoencoder` | r2_histories@income_assets | matched | 0.944 (0.000) | 0.0224 (0.000) | +16.882 | -10.824 | -1821.22 | 0.938 | — | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | exp | 0.941 (0.000) | 0.0223 (0.000) | +17.298 | -10.408 | -1822.05 | 0.945 | — | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | median | 0.943 (0.000) | 0.0218 (0.000) | +18.328 | -9.377 | -1824.11 | 0.866 | — | False |
| `r2_histories@income_assets__random_autoencoder` | r2_histories@income_assets | matched | 0.941 (0.000) | 0.0222 (0.000) | +17.404 | -10.302 | -1822.26 | 0.938 | — | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | exp | 0.939 (0.000) | 0.0217 (0.000) | +17.333 | -10.372 | -1822.12 | 0.827 | — | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | median | 0.939 (0.000) | 0.0218 (0.000) | +17.235 | -10.470 | -1821.92 | 0.849 | — | False |
| `r2_histories@income_assets__supervised_mlp16` | r2_histories@income_assets | matched | 0.939 (0.000) | 0.0222 (0.000) | +16.754 | -10.951 | -1820.96 | 0.938 | — | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | exp | 0.943 (0.000) | 0.0226 (0.000) | +17.236 | -10.470 | -1821.93 | 0.988 | — | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | median | 0.953 (0.000) | 0.0220 (0.000) | +20.883 | -6.822 | -1829.22 | 0.850 | — | False |
| `r2_histories@income_assets__tabpfn_fast__late` | r2_histories@income_assets | matched | 0.949 (0.000) | 0.0223 (0.000) | +18.957 | -8.748 | -1825.37 | 0.938 | — | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | exp | 0.946 (0.000) | 0.0225 (0.000) | +18.239 | -9.466 | -1823.93 | 0.968 | — | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | median | 0.953 (0.000) | 0.0219 (0.000) | +21.414 | -6.292 | -1830.28 | 0.847 | — | False |
| `r2_histories@income_assets__tabpfn_full__late` | r2_histories@income_assets | matched | 0.949 (0.000) | 0.0223 (0.000) | +19.221 | -8.484 | -1825.90 | 0.938 | — | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | exp | 0.948 (0.000) | 0.0223 (0.000) | +19.002 | -8.703 | -1825.46 | 0.953 | — | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | median | 0.950 (0.000) | 0.0222 (0.000) | +19.686 | -8.019 | -1826.83 | 0.932 | — | False |
| `r2_histories@income_assets__tabfm__early_concat` | r2_histories@income_assets | matched | 0.950 (0.000) | 0.0222 (0.000) | +19.527 | -8.179 | -1826.51 | 0.938 | — | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | exp | 0.948 (0.000) | 0.0223 (0.000) | +19.011 | -8.694 | -1825.48 | 0.953 | — | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | median | 0.950 (0.000) | 0.0222 (0.000) | +19.688 | -8.018 | -1826.83 | 0.932 | — | False |
| `r2_histories@income_assets__tabfm__early_mean` | r2_histories@income_assets | matched | 0.950 (0.000) | 0.0222 (0.000) | +19.525 | -8.180 | -1826.50 | 0.938 | — | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | exp | 0.942 (0.000) | 0.0228 (0.000) | +16.871 | -10.835 | -1821.19 | 0.995 | — | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | median | 0.951 (0.000) | 0.0222 (0.000) | +20.562 | -7.143 | -1828.58 | 0.904 | — | False |
| `r2_histories@income_assets__tabfm__late` | r2_histories@income_assets | matched | 0.949 (0.000) | 0.0224 (0.000) | +19.576 | -8.129 | -1826.61 | 0.938 | — | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | exp | 0.940 (0.000) | 0.0228 (0.000) | +16.368 | -11.338 | -1820.19 | 0.993 | — | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | median | 0.945 (0.000) | 0.0225 (0.000) | +18.125 | -9.581 | -1823.70 | 0.885 | — | False |
| `r2_histories@income_assets__tabfm__early_concat_labelnull` | r2_histories@income_assets | matched | 0.943 (0.000) | 0.0226 (0.000) | +17.408 | -10.297 | -1822.27 | 0.938 | — | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | exp | 0.945 (0.000) | 0.0225 (0.000) | +17.507 | -10.198 | -1822.47 | 0.980 | — | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | median | 0.955 (0.000) | 0.0218 (0.000) | +21.243 | -6.462 | -1829.94 | 0.816 | — | False |
| `r2_histories@income_assets__exaone__late` | r2_histories@income_assets | matched | 0.949 (0.000) | 0.0222 (0.000) | +18.788 | -8.918 | -1825.03 | 0.938 | — | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.970 | -11.735 | -1819.39 | 1.000 | — | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | median | 0.939 (0.000) | 0.0228 (0.000) | +17.179 | -10.527 | -1821.81 | 0.771 | — | False |
| `r2_histories@income_assets__exaone__item_first_concat` | r2_histories@income_assets | matched | 0.939 (0.000) | 0.0229 (0.000) | +16.649 | -11.056 | -1820.75 | 0.938 | — | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | exp | 0.939 (0.000) | 0.0229 (0.000) | +15.972 | -11.734 | -1819.40 | 1.000 | — | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | median | 0.938 (0.000) | 0.0228 (0.000) | +17.048 | -10.658 | -1821.55 | 0.761 | — | False |
| `r2_histories@income_assets__exaone__item_first_mean` | r2_histories@income_assets | matched | 0.939 (0.000) | 0.0229 (0.000) | +16.599 | -11.106 | -1820.65 | 0.938 | — | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | exp | 0.941 (0.000) | 0.0227 (0.000) | +17.012 | -10.693 | -1821.48 | 0.992 | — | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | median | 0.948 (0.000) | 0.0221 (0.000) | +20.033 | -7.672 | -1827.52 | 0.895 | — | False |
| `r2_histories@income_assets__exaone__item_last_concat` | r2_histories@income_assets | matched | 0.946 (0.000) | 0.0223 (0.000) | +18.999 | -8.706 | -1825.45 | 0.938 | — | False |
| `uniform_network` | reference | none | 0.939 (0.000) | 0.0229 (0.000) | +15.968 | -11.737 | -1819.39 | 1.000 | — | False |

## Generated-beta bootstrap (exp kernel, W fixed)

| Factors | Network | Parameter | Bootstrap SE | 95% interval |
| --- | --- | --- | ---: | --- |
| capm | `fernandez_market_cap_assets` | sem_intensity | 0.0185 | [0.9001, 0.9634] |
| capm | `fernandez_market_cap_assets` | sem_premium | 0.0094 | [-0.0016, 0.0310] |
| capm | `fernandez_market_to_book` | sem_intensity | 0.0200 | [0.8852, 0.9593] |
| capm | `fernandez_market_to_book` | sem_premium | 0.0093 | [-0.0019, 0.0307] |
| capm | `fernandez_dividend_yield` | sem_intensity | 0.0431 | [0.8068, 0.9626] |
| capm | `fernandez_dividend_yield` | sem_premium | 0.0094 | [-0.0024, 0.0311] |
| capm | `fernandez_joint` | sem_intensity | 0.0214 | [0.8848, 0.9627] |
| capm | `fernandez_joint` | sem_premium | 0.0094 | [-0.0020, 0.0309] |
| capm | `r2_histories__direct` | sem_intensity | 0.0768 | [0.6987, 0.9668] |
| capm | `r2_histories__direct` | sem_premium | 0.0096 | [-0.0033, 0.0309] |
| capm | `r2_histories__mahalanobis_lw` | sem_intensity | 0.0713 | [0.6805, 0.9520] |
| capm | `r2_histories__mahalanobis_lw` | sem_premium | 0.0096 | [-0.0035, 0.0315] |
| capm | `r2_histories__pca16` | sem_intensity | 0.0921 | [0.6913, 0.9699] |
| capm | `r2_histories__pca16` | sem_premium | 0.0096 | [-0.0035, 0.0308] |
| capm | `r2_histories__autoencoder` | sem_intensity | 0.2135 | [0.4640, 0.9707] |
| capm | `r2_histories__autoencoder` | sem_premium | 0.0096 | [-0.0033, 0.0308] |
| capm | `r2_histories__random_autoencoder` | sem_intensity | 0.1702 | [0.6173, 0.9609] |
| capm | `r2_histories__random_autoencoder` | sem_premium | 0.0096 | [-0.0031, 0.0311] |
| capm | `r2_histories__supervised_mlp16` | sem_intensity | 0.1065 | [0.5751, 0.9803] |
| capm | `r2_histories__supervised_mlp16` | sem_premium | 0.0096 | [-0.0038, 0.0305] |
| capm | `r2_histories__tabpfn_fast__late` | sem_intensity | 0.1082 | [0.6021, 0.9664] |
| capm | `r2_histories__tabpfn_fast__late` | sem_premium | 0.0096 | [-0.0026, 0.0316] |
| capm | `r2_histories__tabpfn_full__late` | sem_intensity | 0.1220 | [0.6138, 0.9699] |
| capm | `r2_histories__tabpfn_full__late` | sem_premium | 0.0096 | [-0.0027, 0.0316] |
| capm | `r2_histories__tabfm__early_concat` | sem_intensity | 0.0843 | [0.6051, 0.9678] |
| capm | `r2_histories__tabfm__early_concat` | sem_premium | 0.0096 | [-0.0026, 0.0315] |
| capm | `r2_histories__tabfm__early_mean` | sem_intensity | 0.0834 | [0.6096, 0.9678] |
| capm | `r2_histories__tabfm__early_mean` | sem_premium | 0.0096 | [-0.0026, 0.0315] |
| capm | `r2_histories__tabfm__late` | sem_intensity | 0.1561 | [0.4765, 0.9640] |
| capm | `r2_histories__tabfm__late` | sem_premium | 0.0096 | [-0.0026, 0.0318] |
| capm | `r2_histories__tabfm__early_concat_labelnull` | sem_intensity | 0.3440 | [-0.9900, 0.9588] |
| capm | `r2_histories__tabfm__early_concat_labelnull` | sem_premium | 0.0097 | [-0.0025, 0.0332] |
| capm | `r2_histories__exaone__late` | sem_intensity | 0.1683 | [0.5937, 0.9724] |
| capm | `r2_histories__exaone__late` | sem_premium | 0.0097 | [-0.0028, 0.0314] |
| capm | `r2_histories__exaone__item_first_concat` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r2_histories__exaone__item_first_concat` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r2_histories__exaone__item_first_mean` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r2_histories__exaone__item_first_mean` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r2_histories__exaone__item_last_concat` | sem_intensity | 0.0928 | [0.6069, 0.9634] |
| capm | `r2_histories__exaone__item_last_concat` | sem_premium | 0.0096 | [-0.0024, 0.0317] |
| capm | `r3_broad__direct` | sem_intensity | 0.2430 | [0.0442, 0.9589] |
| capm | `r3_broad__direct` | sem_premium | 0.0097 | [-0.0026, 0.0327] |
| capm | `r3_broad__mahalanobis_lw` | sem_intensity | 0.1732 | [0.3525, 0.9706] |
| capm | `r3_broad__mahalanobis_lw` | sem_premium | 0.0098 | [-0.0023, 0.0350] |
| capm | `r3_broad__pca16` | sem_intensity | 0.1124 | [0.5589, 0.9593] |
| capm | `r3_broad__pca16` | sem_premium | 0.0096 | [-0.0028, 0.0316] |
| capm | `r3_broad__autoencoder` | sem_intensity | 0.1176 | [0.5611, 0.9617] |
| capm | `r3_broad__autoencoder` | sem_premium | 0.0096 | [-0.0028, 0.0317] |
| capm | `r3_broad__random_autoencoder` | sem_intensity | 0.3744 | [-0.9900, 0.9585] |
| capm | `r3_broad__random_autoencoder` | sem_premium | 0.0098 | [-0.0027, 0.0352] |
| capm | `r3_broad__supervised_mlp16` | sem_intensity | 0.1447 | [0.7702, 0.9683] |
| capm | `r3_broad__supervised_mlp16` | sem_premium | 0.0097 | [-0.0037, 0.0307] |
| capm | `r3_broad__tabpfn_fast__late` | sem_intensity | 0.0865 | [0.6320, 0.9668] |
| capm | `r3_broad__tabpfn_fast__late` | sem_premium | 0.0096 | [-0.0027, 0.0315] |
| capm | `r3_broad__tabpfn_full__late` | sem_intensity | 0.0867 | [0.6296, 0.9718] |
| capm | `r3_broad__tabpfn_full__late` | sem_premium | 0.0096 | [-0.0029, 0.0314] |
| capm | `r3_broad__tabfm__early_concat` | sem_intensity | 0.0961 | [0.5615, 0.9662] |
| capm | `r3_broad__tabfm__early_concat` | sem_premium | 0.0096 | [-0.0025, 0.0316] |
| capm | `r3_broad__tabfm__early_mean` | sem_intensity | 0.0929 | [0.5724, 0.9667] |
| capm | `r3_broad__tabfm__early_mean` | sem_premium | 0.0096 | [-0.0025, 0.0316] |
| capm | `r3_broad__tabfm__late` | sem_intensity | 0.1471 | [0.4936, 0.9635] |
| capm | `r3_broad__tabfm__late` | sem_premium | 0.0096 | [-0.0026, 0.0318] |
| capm | `r3_broad__tabfm__early_concat_labelnull` | sem_intensity | 0.3783 | [-0.9900, 0.9581] |
| capm | `r3_broad__tabfm__early_concat_labelnull` | sem_premium | 0.0098 | [-0.0025, 0.0353] |
| capm | `r3_broad__exaone__late` | sem_intensity | 0.1565 | [0.6630, 0.9723] |
| capm | `r3_broad__exaone__late` | sem_premium | 0.0097 | [-0.0029, 0.0314] |
| capm | `r3_broad__exaone__item_first_concat` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r3_broad__exaone__item_first_concat` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r3_broad__exaone__item_first_mean` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r3_broad__exaone__item_first_mean` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r3_broad__exaone__item_last_concat` | sem_intensity | 0.0925 | [0.6234, 0.9643] |
| capm | `r3_broad__exaone__item_last_concat` | sem_premium | 0.0096 | [-0.0025, 0.0316] |
| capm | `r2_histories@income_assets__direct` | sem_intensity | 0.0867 | [0.6584, 0.9664] |
| capm | `r2_histories@income_assets__direct` | sem_premium | 0.0096 | [-0.0032, 0.0310] |
| capm | `r2_histories@income_assets__mahalanobis_lw` | sem_intensity | 0.0753 | [0.6554, 0.9547] |
| capm | `r2_histories@income_assets__mahalanobis_lw` | sem_premium | 0.0095 | [-0.0032, 0.0316] |
| capm | `r2_histories@income_assets__pca16` | sem_intensity | 0.0958 | [0.6620, 0.9687] |
| capm | `r2_histories@income_assets__pca16` | sem_premium | 0.0096 | [-0.0033, 0.0310] |
| capm | `r2_histories@income_assets__autoencoder` | sem_intensity | 0.2201 | [0.4225, 0.9696] |
| capm | `r2_histories@income_assets__autoencoder` | sem_premium | 0.0096 | [-0.0031, 0.0310] |
| capm | `r2_histories@income_assets__random_autoencoder` | sem_intensity | 0.1635 | [0.6161, 0.9614] |
| capm | `r2_histories@income_assets__random_autoencoder` | sem_premium | 0.0096 | [-0.0031, 0.0311] |
| capm | `r2_histories@income_assets__supervised_mlp16` | sem_intensity | 0.0639 | [0.7039, 0.9600] |
| capm | `r2_histories@income_assets__supervised_mlp16` | sem_premium | 0.0095 | [-0.0037, 0.0309] |
| capm | `r2_histories@income_assets__tabpfn_fast__late` | sem_intensity | 0.1680 | [0.4500, 0.9617] |
| capm | `r2_histories@income_assets__tabpfn_fast__late` | sem_premium | 0.0096 | [-0.0023, 0.0318] |
| capm | `r2_histories@income_assets__tabpfn_full__late` | sem_intensity | 0.0847 | [0.6552, 0.9643] |
| capm | `r2_histories@income_assets__tabpfn_full__late` | sem_premium | 0.0096 | [-0.0023, 0.0316] |
| capm | `r2_histories@income_assets__tabfm__early_concat` | sem_intensity | 0.0666 | [0.6915, 0.9674] |
| capm | `r2_histories@income_assets__tabfm__early_concat` | sem_premium | 0.0095 | [-0.0027, 0.0313] |
| capm | `r2_histories@income_assets__tabfm__early_mean` | sem_intensity | 0.0665 | [0.6923, 0.9674] |
| capm | `r2_histories@income_assets__tabfm__early_mean` | sem_premium | 0.0095 | [-0.0027, 0.0313] |
| capm | `r2_histories@income_assets__tabfm__late` | sem_intensity | 0.1894 | [0.1438, 0.9599] |
| capm | `r2_histories@income_assets__tabfm__late` | sem_premium | 0.0096 | [-0.0024, 0.0322] |
| capm | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_intensity | 0.3395 | [-0.9900, 0.9599] |
| capm | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_premium | 0.0097 | [-0.0025, 0.0329] |
| capm | `r2_histories@income_assets__exaone__late` | sem_intensity | 0.0988 | [0.6036, 0.9622] |
| capm | `r2_histories@income_assets__exaone__late` | sem_premium | 0.0096 | [-0.0024, 0.0318] |
| capm | `r2_histories@income_assets__exaone__item_first_concat` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r2_histories@income_assets__exaone__item_first_concat` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r2_histories@income_assets__exaone__item_first_mean` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `r2_histories@income_assets__exaone__item_first_mean` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| capm | `r2_histories@income_assets__exaone__item_last_concat` | sem_intensity | 0.1209 | [0.4775, 0.9592] |
| capm | `r2_histories@income_assets__exaone__item_last_concat` | sem_premium | 0.0096 | [-0.0024, 0.0319] |
| capm | `uniform_network` | sem_intensity | 0.4735 | [-0.9900, 0.9586] |
| capm | `uniform_network` | sem_premium | 0.0099 | [-0.0025, 0.0353] |
| ff6 | `fernandez_market_cap_assets` | sem_intensity | 0.0120 | [0.9236, 0.9673] |
| ff6 | `fernandez_market_cap_assets` | sem_premium | 0.0066 | [-0.0023, 0.0207] |
| ff6 | `fernandez_market_to_book` | sem_intensity | 0.0134 | [0.9163, 0.9642] |
| ff6 | `fernandez_market_to_book` | sem_premium | 0.0066 | [-0.0025, 0.0208] |
| ff6 | `fernandez_dividend_yield` | sem_intensity | 0.0186 | [0.9098, 0.9672] |
| ff6 | `fernandez_dividend_yield` | sem_premium | 0.0066 | [-0.0025, 0.0209] |
| ff6 | `fernandez_joint` | sem_intensity | 0.0135 | [0.9197, 0.9669] |
| ff6 | `fernandez_joint` | sem_premium | 0.0066 | [-0.0024, 0.0209] |
| ff6 | `r2_histories__direct` | sem_intensity | 0.0257 | [0.8885, 0.9711] |
| ff6 | `r2_histories__direct` | sem_premium | 0.0066 | [-0.0026, 0.0209] |
| ff6 | `r2_histories__mahalanobis_lw` | sem_intensity | 0.0486 | [0.8218, 0.9615] |
| ff6 | `r2_histories__mahalanobis_lw` | sem_premium | 0.0066 | [-0.0031, 0.0207] |
| ff6 | `r2_histories__pca16` | sem_intensity | 0.0247 | [0.8857, 0.9725] |
| ff6 | `r2_histories__pca16` | sem_premium | 0.0066 | [-0.0026, 0.0208] |
| ff6 | `r2_histories__autoencoder` | sem_intensity | 0.0274 | [0.8780, 0.9731] |
| ff6 | `r2_histories__autoencoder` | sem_premium | 0.0066 | [-0.0025, 0.0209] |
| ff6 | `r2_histories__random_autoencoder` | sem_intensity | 0.0295 | [0.8742, 0.9685] |
| ff6 | `r2_histories__random_autoencoder` | sem_premium | 0.0067 | [-0.0025, 0.0210] |
| ff6 | `r2_histories__supervised_mlp16` | sem_intensity | 0.0204 | [0.8994, 0.9824] |
| ff6 | `r2_histories__supervised_mlp16` | sem_premium | 0.0066 | [-0.0026, 0.0211] |
| ff6 | `r2_histories__tabpfn_fast__late` | sem_intensity | 0.0251 | [0.8965, 0.9709] |
| ff6 | `r2_histories__tabpfn_fast__late` | sem_premium | 0.0067 | [-0.0025, 0.0213] |
| ff6 | `r2_histories__tabpfn_full__late` | sem_intensity | 0.0234 | [0.8970, 0.9735] |
| ff6 | `r2_histories__tabpfn_full__late` | sem_premium | 0.0067 | [-0.0024, 0.0213] |
| ff6 | `r2_histories__tabfm__early_concat` | sem_intensity | 0.0257 | [0.8957, 0.9711] |
| ff6 | `r2_histories__tabfm__early_concat` | sem_premium | 0.0067 | [-0.0024, 0.0213] |
| ff6 | `r2_histories__tabfm__early_mean` | sem_intensity | 0.0255 | [0.8959, 0.9712] |
| ff6 | `r2_histories__tabfm__early_mean` | sem_premium | 0.0067 | [-0.0024, 0.0213] |
| ff6 | `r2_histories__tabfm__late` | sem_intensity | 0.0292 | [0.8931, 0.9697] |
| ff6 | `r2_histories__tabfm__late` | sem_premium | 0.0067 | [-0.0024, 0.0214] |
| ff6 | `r2_histories__tabfm__early_concat_labelnull` | sem_intensity | 0.0361 | [0.8804, 0.9660] |
| ff6 | `r2_histories__tabfm__early_concat_labelnull` | sem_premium | 0.0068 | [-0.0023, 0.0215] |
| ff6 | `r2_histories__exaone__late` | sem_intensity | 0.0229 | [0.9016, 0.9757] |
| ff6 | `r2_histories__exaone__late` | sem_premium | 0.0067 | [-0.0025, 0.0212] |
| ff6 | `r2_histories__exaone__item_first_concat` | sem_intensity | 0.1388 | [0.8804, 0.9643] |
| ff6 | `r2_histories__exaone__item_first_concat` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r2_histories__exaone__item_first_mean` | sem_intensity | 0.1388 | [0.8804, 0.9643] |
| ff6 | `r2_histories__exaone__item_first_mean` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r2_histories__exaone__item_last_concat` | sem_intensity | 0.0258 | [0.8969, 0.9683] |
| ff6 | `r2_histories__exaone__item_last_concat` | sem_premium | 0.0067 | [-0.0025, 0.0213] |
| ff6 | `r3_broad__direct` | sem_intensity | 0.0308 | [0.8848, 0.9649] |
| ff6 | `r3_broad__direct` | sem_premium | 0.0068 | [-0.0023, 0.0214] |
| ff6 | `r3_broad__mahalanobis_lw` | sem_intensity | 0.0779 | [0.7190, 0.9841] |
| ff6 | `r3_broad__mahalanobis_lw` | sem_premium | 0.0066 | [-0.0021, 0.0212] |
| ff6 | `r3_broad__pca16` | sem_intensity | 0.0280 | [0.8898, 0.9671] |
| ff6 | `r3_broad__pca16` | sem_premium | 0.0067 | [-0.0024, 0.0212] |
| ff6 | `r3_broad__autoencoder` | sem_intensity | 0.0281 | [0.8902, 0.9681] |
| ff6 | `r3_broad__autoencoder` | sem_premium | 0.0067 | [-0.0024, 0.0212] |
| ff6 | `r3_broad__random_autoencoder` | sem_intensity | 0.0405 | [0.8819, 0.9639] |
| ff6 | `r3_broad__random_autoencoder` | sem_premium | 0.0068 | [-0.0023, 0.0215] |
| ff6 | `r3_broad__supervised_mlp16` | sem_intensity | 0.0182 | [0.9047, 0.9706] |
| ff6 | `r3_broad__supervised_mlp16` | sem_premium | 0.0067 | [-0.0028, 0.0207] |
| ff6 | `r3_broad__tabpfn_fast__late` | sem_intensity | 0.0246 | [0.9009, 0.9708] |
| ff6 | `r3_broad__tabpfn_fast__late` | sem_premium | 0.0067 | [-0.0025, 0.0213] |
| ff6 | `r3_broad__tabpfn_full__late` | sem_intensity | 0.0228 | [0.9028, 0.9750] |
| ff6 | `r3_broad__tabpfn_full__late` | sem_premium | 0.0067 | [-0.0025, 0.0212] |
| ff6 | `r3_broad__tabfm__early_concat` | sem_intensity | 0.0263 | [0.8944, 0.9700] |
| ff6 | `r3_broad__tabfm__early_concat` | sem_premium | 0.0067 | [-0.0024, 0.0213] |
| ff6 | `r3_broad__tabfm__early_mean` | sem_intensity | 0.0261 | [0.8948, 0.9703] |
| ff6 | `r3_broad__tabfm__early_mean` | sem_premium | 0.0067 | [-0.0024, 0.0213] |
| ff6 | `r3_broad__tabfm__late` | sem_intensity | 0.0294 | [0.8934, 0.9695] |
| ff6 | `r3_broad__tabfm__late` | sem_premium | 0.0067 | [-0.0024, 0.0214] |
| ff6 | `r3_broad__tabfm__early_concat_labelnull` | sem_intensity | 0.0379 | [0.8806, 0.9643] |
| ff6 | `r3_broad__tabfm__early_concat_labelnull` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r3_broad__exaone__late` | sem_intensity | 0.0223 | [0.9055, 0.9757] |
| ff6 | `r3_broad__exaone__late` | sem_premium | 0.0067 | [-0.0025, 0.0212] |
| ff6 | `r3_broad__exaone__item_first_concat` | sem_intensity | 0.1388 | [0.8805, 0.9643] |
| ff6 | `r3_broad__exaone__item_first_concat` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r3_broad__exaone__item_first_mean` | sem_intensity | 0.1388 | [0.8805, 0.9643] |
| ff6 | `r3_broad__exaone__item_first_mean` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r3_broad__exaone__item_last_concat` | sem_intensity | 0.0259 | [0.8979, 0.9685] |
| ff6 | `r3_broad__exaone__item_last_concat` | sem_premium | 0.0067 | [-0.0025, 0.0212] |
| ff6 | `r2_histories@income_assets__direct` | sem_intensity | 0.0267 | [0.8865, 0.9709] |
| ff6 | `r2_histories@income_assets__direct` | sem_premium | 0.0067 | [-0.0026, 0.0210] |
| ff6 | `r2_histories@income_assets__mahalanobis_lw` | sem_intensity | 0.0470 | [0.8218, 0.9631] |
| ff6 | `r2_histories@income_assets__mahalanobis_lw` | sem_premium | 0.0066 | [-0.0029, 0.0208] |
| ff6 | `r2_histories@income_assets__pca16` | sem_intensity | 0.0258 | [0.8846, 0.9718] |
| ff6 | `r2_histories@income_assets__pca16` | sem_premium | 0.0066 | [-0.0026, 0.0209] |
| ff6 | `r2_histories@income_assets__autoencoder` | sem_intensity | 0.0287 | [0.8781, 0.9718] |
| ff6 | `r2_histories@income_assets__autoencoder` | sem_premium | 0.0067 | [-0.0024, 0.0210] |
| ff6 | `r2_histories@income_assets__random_autoencoder` | sem_intensity | 0.0294 | [0.8742, 0.9687] |
| ff6 | `r2_histories@income_assets__random_autoencoder` | sem_premium | 0.0067 | [-0.0025, 0.0210] |
| ff6 | `r2_histories@income_assets__supervised_mlp16` | sem_intensity | 0.0340 | [0.8833, 0.9672] |
| ff6 | `r2_histories@income_assets__supervised_mlp16` | sem_premium | 0.0066 | [-0.0029, 0.0207] |
| ff6 | `r2_histories@income_assets__tabpfn_fast__late` | sem_intensity | 0.0291 | [0.8886, 0.9681] |
| ff6 | `r2_histories@income_assets__tabpfn_fast__late` | sem_premium | 0.0068 | [-0.0023, 0.0214] |
| ff6 | `r2_histories@income_assets__tabpfn_full__late` | sem_intensity | 0.0247 | [0.8950, 0.9687] |
| ff6 | `r2_histories@income_assets__tabpfn_full__late` | sem_premium | 0.0067 | [-0.0023, 0.0213] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat` | sem_intensity | 0.0241 | [0.8966, 0.9709] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat` | sem_premium | 0.0067 | [-0.0025, 0.0211] |
| ff6 | `r2_histories@income_assets__tabfm__early_mean` | sem_intensity | 0.0240 | [0.8967, 0.9709] |
| ff6 | `r2_histories@income_assets__tabfm__early_mean` | sem_premium | 0.0067 | [-0.0025, 0.0211] |
| ff6 | `r2_histories@income_assets__tabfm__late` | sem_intensity | 0.0320 | [0.8875, 0.9663] |
| ff6 | `r2_histories@income_assets__tabfm__late` | sem_premium | 0.0068 | [-0.0022, 0.0215] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_intensity | 0.0354 | [0.8801, 0.9676] |
| ff6 | `r2_histories@income_assets__tabfm__early_concat_labelnull` | sem_premium | 0.0068 | [-0.0023, 0.0216] |
| ff6 | `r2_histories@income_assets__exaone__late` | sem_intensity | 0.0264 | [0.8976, 0.9679] |
| ff6 | `r2_histories@income_assets__exaone__late` | sem_premium | 0.0067 | [-0.0023, 0.0214] |
| ff6 | `r2_histories@income_assets__exaone__item_first_concat` | sem_intensity | 0.1388 | [0.8804, 0.9643] |
| ff6 | `r2_histories@income_assets__exaone__item_first_concat` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r2_histories@income_assets__exaone__item_first_mean` | sem_intensity | 0.1388 | [0.8804, 0.9643] |
| ff6 | `r2_histories@income_assets__exaone__item_first_mean` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
| ff6 | `r2_histories@income_assets__exaone__item_last_concat` | sem_intensity | 0.0297 | [0.8908, 0.9652] |
| ff6 | `r2_histories@income_assets__exaone__item_last_concat` | sem_premium | 0.0068 | [-0.0022, 0.0214] |
| ff6 | `uniform_network` | sem_intensity | 0.1388 | [0.8804, 0.9643] |
| ff6 | `uniform_network` | sem_premium | 0.0068 | [-0.0022, 0.0216] |
