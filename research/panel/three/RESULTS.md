# Panel design `three`

Characteristics: market_cap_assets, market_to_book, dividend_yield. Network history: 5 annual snapshots; cohort requires complete, nonconstant 3- and 5-year histories. All rows score the same 642,024 held-out firm-days (2020-2025).
One spatial coefficient per network, kernel and innovation arm is fitted on
2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint
Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;
higher is better. Columns are kernel/innovation; `correlation` imposes prior raw
sample variances on every row so only implied correlations differ.

## Cohorts

| Return year | Firms | Prior complete days | Scored days |
| --- | ---: | ---: | ---: |
| 2016 | 329 | 756 | 251 |
| 2017 | 381 | 756 | 250 |
| 2018 | 386 | 755 | 250 |
| 2019 | 396 | 754 | 251 |
| 2020 | 406 | 754 | 252 |
| 2021 | 413 | 756 | 251 |
| 2022 | 421 | 757 | 250 |
| 2023 | 429 | 755 | 249 |
| 2024 | 437 | 753 | 251 |
| 2025 | 459 | 753 | 249 |

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | fernandez | +298.20 | -322.86 | -793.72 | -1,025.51 | -106.37 |
| `fernandez_market_to_book` | fernandez | -800.87 | -1,778.48 | -2,072.82 | -2,156.96 | -769.94 |
| `fernandez_dividend_yield` | fernandez | -983.78 | -834.81 | -1,337.76 | -1,505.93 | -424.59 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -915.75 | -0.00 | +0.00 |
| `histories__direct` | classical | +818.94 | +1,216.98 | +3,206.89 | +2,187.09 | +1,045.94 |
| `histories__mahalanobis_lw` | classical | -5,315.24 | -10,613.60 | -2,514.62 | -1,429.82 | -14,963.39 |
| `histories__pca16` | control | +1,189.16 | +1,613.80 | +3,423.74 | +2,208.47 | +1,239.14 |
| `histories__autoencoder` | control | +880.80 | +984.92 | +2,999.16 | +1,333.49 | +1,350.88 |
| `histories__random_autoencoder` | control | -854.05 | -809.79 | +2,198.54 | +750.53 | -236.19 |
| `histories__supervised_mlp16` | task | +68.42 | -51.73 | -59.62 | -1,133.11 | +1,027.66 |
| `histories__tabpfn_fast__late` | task | -1,424.66 | -1,525.39 | +1,770.99 | +539.22 | -443.26 |
| `histories__tabpfn_full__late` | task | -558.96 | -225.81 | +2,111.74 | +716.72 | +213.70 |
| `histories__tabfm__early_concat` | state | -842.03 | -1,035.18 | +2,288.49 | +2,293.63 | +236.58 |
| `histories__tabfm__early_mean` | state | -833.43 | -1,024.18 | +2,303.85 | +2,304.33 | +243.67 |
| `histories__tabfm__late` | task | -2,294.57 | -3,091.74 | +1,959.38 | +189.38 | -1,328.64 |
| `histories__tabfm__early_concat_labelnull` | state | -2,463.96 | -3,367.66 | +2,151.37 | +1,347.78 | -1,549.58 |
| `histories__exaone__late` | task | -1,188.93 | -1,390.21 | +2,405.31 | -149.09 | -156.99 |
| `histories__exaone__item_first_concat` | state | -3,240.34 | -4,586.69 | -1,202.19 | -2,058.61 | -2,481.65 |
| `histories__exaone__item_first_mean` | state | -3,237.94 | -4,583.02 | -1,108.07 | -2,018.99 | -2,478.45 |
| `histories__exaone__item_last_concat` | task | -1,613.61 | -1,918.15 | +3,206.32 | +1,796.85 | -695.43 |
| `broad__direct` | classical | -993.22 | -1,065.76 | -2,063.86 | +6,455.28 | -48.95 |
| `broad__mahalanobis_lw` | classical | +88.26 | -5,814.91 | -3,909.00 | -2,572.81 | -5,893.00 |
| `broad__pca16` | control | +3,136.20 | +4,180.70 | +2,114.18 | +5,501.26 | +1,725.77 |
| `broad__autoencoder` | control | +3,785.45 | +4,765.87 | +2,846.64 | +5,618.11 | +1,779.26 |
| `broad__random_autoencoder` | control | -2,039.90 | -2,579.27 | -2,959.04 | -1,670.30 | -1,087.29 |
| `broad__supervised_mlp16` | task | -138.24 | -96.77 | -488.64 | -782.10 | +1,110.29 |
| `broad__tabpfn_fast__late` | task | -1,277.65 | -1,274.28 | +2,314.65 | +1,034.16 | -308.92 |
| `broad__tabpfn_full__late` | task | -416.50 | +4.11 | +2,339.68 | +926.84 | +326.15 |
| `broad__tabfm__early_concat` | state | -926.85 | -1,114.61 | +1,975.27 | +2,743.53 | +102.59 |
| `broad__tabfm__early_mean` | state | -882.40 | -1,048.35 | +2,118.64 | +2,784.56 | +137.45 |
| `broad__tabfm__late` | task | -2,334.88 | -3,187.80 | +1,494.14 | +205.99 | -1,381.89 |
| `broad__tabfm__early_concat_labelnull` | state | -2,688.17 | -3,718.64 | -369.72 | +774.39 | -1,834.73 |
| `broad__exaone__late` | task | -1,138.81 | -1,262.46 | +2,737.53 | +50.41 | -91.41 |
| `broad__exaone__item_first_concat` | state | -3,240.49 | -4,586.56 | -616.79 | -1,484.58 | -2,481.75 |
| `broad__exaone__item_first_mean` | state | -3,238.32 | -4,583.09 | -734.05 | -1,557.85 | -2,478.92 |
| `broad__exaone__item_last_concat` | task | -1,542.78 | -1,819.43 | +3,105.11 | +2,016.98 | -656.73 |
| `metrics__direct` | classical | +94.76 | +466.29 | -927.63 | +7,079.82 | +685.39 |
| `metrics__mahalanobis_lw` | classical | +4,081.29 | -2,827.52 | -3,075.73 | -813.35 | +72.08 |
| `metrics__pca16` | control | +3,839.89 | +4,935.14 | +2,854.43 | +5,692.62 | +1,619.34 |
| `metrics__autoencoder` | control | +3,949.14 | +5,163.27 | +3,380.08 | +5,628.01 | +1,533.87 |
| `metrics__random_autoencoder` | control | -988.44 | -988.83 | -1,324.93 | +979.40 | -169.96 |
| `metrics__supervised_mlp16` | task | +1,136.70 | +1,379.05 | +867.89 | +395.52 | +2,020.73 |
| `metrics__tabpfn_fast__late` | task | -1,175.81 | -1,107.82 | +2,624.43 | +1,292.73 | -279.47 |
| `metrics__tabpfn_full__late` | task | -233.89 | +282.12 | +2,747.53 | +1,230.28 | +394.68 |
| `metrics__tabfm__early_concat` | state | -881.01 | -1,076.36 | +2,600.85 | +3,422.16 | +115.77 |
| `metrics__tabfm__early_mean` | state | -858.99 | -1,062.89 | +2,693.50 | +3,378.50 | +134.71 |
| `metrics__tabfm__late` | task | -2,251.28 | -3,056.77 | +2,084.40 | +526.95 | -1,292.62 |
| `metrics__tabfm__early_concat_labelnull` | state | -2,794.60 | -3,798.92 | +1,536.20 | +1,996.69 | -1,932.83 |
| `metrics__exaone__late` | task | -991.24 | -1,062.29 | +3,241.65 | +299.75 | +20.15 |
| `metrics__exaone__item_first_concat` | state | -3,240.74 | -4,586.97 | +885.82 | -282.17 | -2,482.51 |
| `metrics__exaone__item_first_mean` | state | -3,238.79 | -4,583.86 | +428.84 | -606.22 | -2,480.36 |
| `metrics__exaone__item_last_concat` | task | -1,283.70 | -1,447.23 | +4,025.68 | +2,722.16 | -457.75 |
| `histories@income_assets__direct` | classical | +392.66 | +622.94 | +3,122.75 | +1,973.09 | +815.78 |
| `histories@income_assets__mahalanobis_lw` | classical | -5,381.73 | -10,516.47 | -2,790.35 | -1,458.65 | -16,159.62 |
| `histories@income_assets__pca16` | control | +778.48 | +1,073.91 | +3,305.47 | +2,032.79 | +1,041.47 |
| `histories@income_assets__autoencoder` | control | +384.83 | +368.77 | +3,143.16 | +1,341.72 | +1,054.75 |
| `histories@income_assets__random_autoencoder` | control | -969.21 | -1,017.79 | +2,102.65 | +614.71 | -295.94 |
| `histories@income_assets__supervised_mlp16` | task | +889.31 | +1,304.88 | +1,438.20 | -174.68 | +1,381.61 |
| `histories@income_assets__tabpfn_fast__late` | task | -1,837.16 | -2,313.03 | +2,583.05 | +1,306.00 | -840.60 |
| `histories@income_assets__tabpfn_full__late` | task | -1,039.67 | -1,130.18 | +2,333.39 | +777.15 | -13.97 |
| `histories@income_assets__tabfm__early_concat` | state | -290.23 | -154.92 | +2,011.27 | +2,469.30 | +636.01 |
| `histories@income_assets__tabfm__early_mean` | state | -280.04 | -139.85 | +2,016.68 | +2,472.55 | +644.35 |
| `histories@income_assets__tabfm__late` | task | -2,402.07 | -3,282.22 | +1,802.04 | +1,422.85 | -1,461.85 |
| `histories@income_assets__tabfm__early_concat_labelnull` | state | -2,270.79 | -3,074.36 | +2,240.37 | +1,388.46 | -1,330.26 |
| `histories@income_assets__exaone__late` | task | -1,646.13 | -2,072.85 | +3,029.04 | +895.96 | -634.51 |
| `histories@income_assets__exaone__item_first_concat` | state | -3,239.57 | -4,585.38 | -817.71 | -1,802.26 | -2,480.56 |
| `histories@income_assets__exaone__item_first_mean` | state | -3,236.53 | -4,580.62 | -799.47 | -1,809.00 | -2,476.47 |
| `histories@income_assets__exaone__item_last_concat` | task | -2,187.48 | -2,848.90 | +2,262.63 | +2,421.60 | -1,271.94 |
| `h3__fernandez_market_cap_assets` | fernandez | -2,106.30 | -5,356.71 | -5,356.71 | -3,590.96 | -2,159.10 |
| `h3__fernandez_market_to_book` | fernandez | -2,294.23 | -5,334.64 | -5,282.49 | -3,708.46 | -2,472.82 |
| `h3__fernandez_dividend_yield` | fernandez | -2,411.17 | -4,449.07 | -4,503.31 | -3,286.53 | -2,006.15 |
| `h3__fernandez_joint` | fernandez | -1,136.54 | -2,535.10 | -2,590.42 | -2,663.92 | -654.53 |
| `h3__histories__direct` | classical | +686.62 | +987.29 | +2,987.03 | +1,540.46 | +1,162.35 |
| `h3__histories__mahalanobis_lw` | classical | -3,975.10 | -7,900.40 | -6,425.60 | -2,028.62 | -8,483.67 |
| `h3__histories__pca16` | control | +1,460.66 | +1,929.57 | +2,954.31 | +1,696.03 | +1,459.64 |
| `h3__histories__autoencoder` | control | +1,013.32 | +1,308.21 | +2,773.76 | +1,126.02 | +1,515.78 |
| `h3__histories__random_autoencoder` | control | -524.76 | -626.21 | +2,485.02 | +802.91 | +377.42 |
| `h3__histories__supervised_mlp16` | task | -348.15 | -746.26 | -2,721.48 | -1,513.78 | +731.34 |
| `h3__histories__tabpfn_fast__late` | task | -1,392.59 | -1,483.25 | +1,847.36 | +610.06 | -430.99 |
| `h3__histories__tabpfn_full__late` | task | -617.99 | -340.69 | +1,989.66 | +582.99 | +207.69 |
| `h3__histories__tabfm__early_concat` | state | -894.66 | -1,091.37 | +1,824.62 | +1,944.36 | +194.04 |
| `h3__histories__tabfm__early_mean` | state | -888.07 | -1,083.20 | +1,832.73 | +1,952.29 | +199.75 |
| `h3__histories__tabfm__late` | task | -2,311.32 | -3,096.41 | +1,984.65 | +178.85 | -1,333.51 |
| `h3__histories__tabfm__early_concat_labelnull` | state | -2,525.76 | -3,487.40 | +1,584.37 | +628.41 | -1,601.34 |
| `h3__histories__exaone__late` | task | -1,248.70 | -1,474.80 | +2,265.60 | -239.87 | -207.65 |
| `h3__histories__exaone__item_first_concat` | state | -3,240.42 | -4,586.72 | -1,077.61 | -1,940.19 | -2,481.71 |
| `h3__histories__exaone__item_first_mean` | state | -3,238.23 | -4,583.36 | -998.62 | -1,912.96 | -2,478.84 |
| `h3__histories__exaone__item_last_concat` | task | -1,699.05 | -2,040.01 | +2,958.58 | +1,528.69 | -767.05 |
| `uniform_network` | reference | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `zero_network` | reference | -7,789.43 | -14,038.84 | -14,038.84 | -14,038.84 | -10,957.69 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `raw_sample_covariance` | 1,071,535.66 | 1,071,535.66 |
| `ff5_mom_diagonal` | 1,679,203.95 | 1,679,322.43 |
| `ff5_mom_sample_residual_covariance` | 1,071,535.66 | 1,071,535.66 |

## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)

Summed daily differences against the joint network; 95% percentile intervals
with 21- and 63-day expected blocks. Intervals are descriptive: the approaches
were not preregistered and these years were inspected during development.

| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | -322.86 | [-805.0, -4.4] | [-930.1, +48.7] | 50.2 |
| `fernandez_market_to_book` | -1,778.48 | [-3,625.9, -688.2] | [-3,926.0, -558.4] | 53.7 |
| `fernandez_dividend_yield` | -834.81 | [-1,837.7, -250.2] | [-1,973.8, -161.9] | 42.3 |
| `histories__direct` | +1,216.98 | [+363.1, +2,412.5] | [+156.5, +2,802.8] | 63.3 |
| `histories__mahalanobis_lw` | -10,613.60 | [-21,995.4, -3,855.5] | [-24,070.8, -2,743.0] | 54.0 |
| `histories__pca16` | +1,613.80 | [+538.1, +3,175.9] | [+271.5, +3,636.2] | 62.7 |
| `histories__autoencoder` | +984.92 | [+262.0, +1,929.8] | [+60.3, +2,305.8] | 13.5 |
| `histories__random_autoencoder` | -809.79 | [-1,210.4, -387.9] | [-1,237.1, -299.3] | 35.5 |
| `histories__supervised_mlp16` | -51.73 | [-884.1, +1,032.2] | [-1,044.6, +1,342.1] | 11.1 |
| `histories__tabpfn_fast__late` | -1,525.39 | [-2,714.9, -744.1] | [-2,713.0, -684.5] | 38.3 |
| `histories__tabpfn_full__late` | -225.81 | [-784.6, +440.5] | [-847.0, +593.5] | 37.6 |
| `histories__tabfm__early_concat` | -1,035.18 | [-1,873.6, -440.3] | [-1,833.4, -386.0] | 35.1 |
| `histories__tabfm__early_mean` | -1,024.18 | [-1,853.1, -430.3] | [-1,815.1, -378.0] | 35.0 |
| `histories__tabfm__late` | -3,091.74 | [-5,500.2, -1,733.9] | [-5,666.5, -1,614.7] | 44.6 |
| `histories__tabfm__early_concat_labelnull` | -3,367.66 | [-5,970.3, -1,904.0] | [-6,169.2, -1,778.3] | 46.9 |
| `histories__exaone__late` | -1,390.21 | [-2,518.5, -543.4] | [-2,475.2, -476.7] | 36.4 |
| `histories__exaone__item_first_concat` | -4,586.69 | [-8,296.6, -2,510.0] | [-8,673.2, -2,294.7] | 49.7 |
| `histories__exaone__item_first_mean` | -4,583.02 | [-8,288.4, -2,508.6] | [-8,666.0, -2,293.5] | 49.7 |
| `histories__exaone__item_last_concat` | -1,918.15 | [-3,428.5, -992.8] | [-3,479.9, -922.0] | 42.1 |
| `broad__direct` | -1,065.76 | [-1,852.6, -535.8] | [-1,854.9, -490.6] | 41.7 |
| `broad__mahalanobis_lw` | -5,814.91 | [-19,076.3, +1,739.0] | [-20,905.4, +2,640.6] | 49.5 |
| `broad__pca16` | +4,180.70 | [+2,255.1, +7,265.9] | [+1,894.3, +7,879.4] | 56.2 |
| `broad__autoencoder` | +4,765.87 | [+2,597.5, +8,277.3] | [+2,198.3, +8,946.4] | 56.0 |
| `broad__random_autoencoder` | -2,579.27 | [-4,643.3, -1,399.2] | [-4,822.9, -1,260.7] | 48.5 |
| `broad__supervised_mlp16` | -96.77 | [-737.9, +733.9] | [-923.1, +1,052.1] | 8.8 |
| `broad__tabpfn_fast__late` | -1,274.28 | [-2,206.3, -587.7] | [-2,174.7, -526.3] | 38.1 |
| `broad__tabpfn_full__late` | +4.11 | [-547.3, +701.0] | [-689.8, +936.0] | 10.9 |
| `broad__tabfm__early_concat` | -1,114.61 | [-1,990.6, -460.5] | [-1,955.4, -405.6] | 34.3 |
| `broad__tabfm__early_mean` | -1,048.35 | [-1,879.8, -407.5] | [-1,844.7, -351.5] | 34.0 |
| `broad__tabfm__late` | -3,187.80 | [-5,661.7, -1,790.9] | [-5,840.7, -1,673.0] | 44.9 |
| `broad__tabfm__early_concat_labelnull` | -3,718.64 | [-6,666.3, -2,068.0] | [-6,916.0, -1,908.9] | 48.0 |
| `broad__exaone__late` | -1,262.46 | [-2,235.4, -480.4] | [-2,197.8, -405.6] | 36.7 |
| `broad__exaone__item_first_concat` | -4,586.56 | [-8,297.4, -2,509.6] | [-8,672.6, -2,294.3] | 49.7 |
| `broad__exaone__item_first_mean` | -4,583.09 | [-8,290.8, -2,507.9] | [-8,665.6, -2,292.9] | 49.7 |
| `broad__exaone__item_last_concat` | -1,819.43 | [-3,196.9, -962.1] | [-3,238.8, -894.0] | 41.6 |
| `metrics__direct` | +466.29 | [-82.9, +1,175.0] | [-273.8, +1,444.1] | 64.3 |
| `metrics__mahalanobis_lw` | -2,827.52 | [-13,140.5, +3,443.7] | [-14,310.8, +4,149.2] | 49.0 |
| `metrics__pca16` | +4,935.14 | [+2,708.5, +8,503.7] | [+2,260.0, +9,223.4] | 55.9 |
| `metrics__autoencoder` | +5,163.27 | [+2,836.8, +8,874.6] | [+2,384.6, +9,625.3] | 55.7 |
| `metrics__random_autoencoder` | -988.83 | [-1,659.5, -526.7] | [-1,685.2, -467.7] | 45.5 |
| `metrics__supervised_mlp16` | +1,379.05 | [+107.2, +3,141.1] | [-238.7, +3,793.7] | 9.8 |
| `metrics__tabpfn_fast__late` | -1,107.82 | [-1,916.2, -476.8] | [-1,889.7, -427.6] | 37.8 |
| `metrics__tabpfn_full__late` | +282.12 | [-345.3, +1,066.1] | [-526.5, +1,407.8] | 11.5 |
| `metrics__tabfm__early_concat` | -1,076.36 | [-1,924.1, -453.3] | [-1,880.0, -407.1] | 35.5 |
| `metrics__tabfm__early_mean` | -1,062.89 | [-1,916.9, -435.5] | [-1,873.4, -389.4] | 35.2 |
| `metrics__tabfm__late` | -3,056.77 | [-5,422.5, -1,721.7] | [-5,572.5, -1,603.9] | 44.6 |
| `metrics__tabfm__early_concat_labelnull` | -3,798.92 | [-6,777.6, -2,129.7] | [-7,041.9, -1,969.1] | 49.0 |
| `metrics__exaone__late` | -1,062.29 | [-1,912.4, -313.8] | [-1,867.5, -224.0] | 37.0 |
| `metrics__exaone__item_first_concat` | -4,586.97 | [-8,297.6, -2,510.1] | [-8,673.3, -2,294.8] | 49.7 |
| `metrics__exaone__item_first_mean` | -4,583.86 | [-8,291.2, -2,508.8] | [-8,666.8, -2,293.9] | 49.7 |
| `metrics__exaone__item_last_concat` | -1,447.23 | [-2,492.0, -742.5] | [-2,489.7, -689.6] | 40.0 |
| `histories@income_assets__direct` | +622.94 | [+2.8, +1,425.0] | [-174.4, +1,763.5] | 44.1 |
| `histories@income_assets__mahalanobis_lw` | -10,516.47 | [-21,693.5, -3,825.7] | [-23,861.6, -2,667.7] | 54.7 |
| `histories@income_assets__pca16` | +1,073.91 | [+214.0, +2,254.5] | [-19.7, +2,691.5] | 64.8 |
| `histories@income_assets__autoencoder` | +368.77 | [-188.4, +1,061.3] | [-348.7, +1,365.2] | 3.0 |
| `histories@income_assets__random_autoencoder` | -1,017.79 | [-1,562.4, -540.2] | [-1,559.4, -476.1] | 38.6 |
| `histories@income_assets__supervised_mlp16` | +1,304.88 | [+178.1, +2,834.7] | [-151.5, +3,435.5] | 65.8 |
| `histories@income_assets__tabpfn_fast__late` | -2,313.03 | [-4,006.1, -1,299.4] | [-4,066.7, -1,219.0] | 43.0 |
| `histories@income_assets__tabpfn_full__late` | -1,130.18 | [-1,977.5, -468.3] | [-1,945.0, -405.1] | 38.1 |
| `histories@income_assets__tabfm__early_concat` | -154.92 | [-586.0, +337.3] | [-628.2, +449.4] | 9.1 |
| `histories@income_assets__tabfm__early_mean` | -139.85 | [-569.7, +356.4] | [-614.7, +468.9] | 8.8 |
| `histories@income_assets__tabfm__late` | -3,282.22 | [-5,825.9, -1,850.4] | [-6,016.3, -1,720.6] | 46.4 |
| `histories@income_assets__tabfm__early_concat_labelnull` | -3,074.36 | [-5,415.1, -1,747.1] | [-5,593.6, -1,632.7] | 46.0 |
| `histories@income_assets__exaone__late` | -2,072.85 | [-3,612.8, -1,104.7] | [-3,613.0, -1,042.1] | 39.8 |
| `histories@income_assets__exaone__item_first_concat` | -4,585.38 | [-8,293.6, -2,509.6] | [-8,670.5, -2,294.4] | 49.7 |
| `histories@income_assets__exaone__item_first_mean` | -4,580.62 | [-8,282.9, -2,507.7] | [-8,660.6, -2,292.9] | 49.7 |
| `histories@income_assets__exaone__item_last_concat` | -2,848.90 | [-5,040.5, -1,590.6] | [-5,195.8, -1,478.7] | 46.4 |
| `h3__fernandez_market_cap_assets` | -5,356.71 | [-11,510.4, -1,723.3] | [-12,489.1, -1,184.3] | 53.3 |
| `h3__fernandez_market_to_book` | -5,334.64 | [-11,441.1, -1,863.4] | [-12,267.9, -1,394.4] | 50.7 |
| `h3__fernandez_dividend_yield` | -4,449.07 | [-9,415.9, -1,493.6] | [-10,235.7, -962.8] | 53.8 |
| `h3__fernandez_joint` | -2,535.10 | [-5,800.5, -603.0] | [-6,317.1, -281.8] | 52.2 |
| `h3__histories__direct` | +987.29 | [+146.4, +2,091.7] | [-111.9, +2,540.1] | 45.0 |
| `h3__histories__mahalanobis_lw` | -7,900.40 | [-16,791.5, -2,771.0] | [-18,094.0, -2,084.1] | 52.8 |
| `h3__histories__pca16` | +1,929.57 | [+681.8, +3,718.2] | [+346.4, +4,266.5] | 63.3 |
| `h3__histories__autoencoder` | +1,308.21 | [+353.7, +2,583.7] | [+68.4, +3,070.6] | 5.6 |
| `h3__histories__random_autoencoder` | -626.21 | [-1,098.1, -153.6] | [-1,128.9, -49.4] | 24.7 |
| `h3__histories__supervised_mlp16` | -746.26 | [-1,835.3, +409.2] | [-1,824.1, +606.5] | 40.0 |
| `h3__histories__tabpfn_fast__late` | -1,483.25 | [-2,630.3, -718.9] | [-2,615.8, -662.6] | 38.6 |
| `h3__histories__tabpfn_full__late` | -340.69 | [-937.9, +326.8] | [-962.9, +455.0] | 37.2 |
| `h3__histories__tabfm__early_concat` | -1,091.37 | [-1,984.3, -469.2] | [-1,958.4, -418.9] | 36.2 |
| `h3__histories__tabfm__early_mean` | -1,083.20 | [-1,971.1, -462.9] | [-1,944.5, -413.3] | 36.1 |
| `h3__histories__tabfm__late` | -3,096.41 | [-5,506.7, -1,737.1] | [-5,668.0, -1,617.4] | 44.8 |
| `h3__histories__tabfm__early_concat_labelnull` | -3,487.40 | [-6,241.3, -1,943.4] | [-6,467.1, -1,807.6] | 47.4 |
| `h3__histories__exaone__late` | -1,474.80 | [-2,669.0, -610.0] | [-2,618.4, -541.1] | 37.0 |
| `h3__histories__exaone__item_first_concat` | -4,586.72 | [-8,296.8, -2,510.1] | [-8,673.2, -2,294.8] | 49.7 |
| `h3__histories__exaone__item_first_mean` | -4,583.36 | [-8,289.3, -2,508.8] | [-8,666.5, -2,293.8] | 49.7 |
| `h3__histories__exaone__item_last_concat` | -2,040.01 | [-3,653.2, -1,069.0] | [-3,714.5, -993.5] | 42.5 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +3,426.7 | [+2,190.8, +5,593.2] | +1,543 | +359 | +367 | +345 | +236 | +577 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +106.5 | [-208.9, +322.9] | -81 | -6 | +67 | +19 | +48 | +60 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/diagonal | +3,723.4 | [+2,111.2, +6,287.8] | +2,122 | +158 | +362 | +206 | +187 | +687 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/diagonal | +1,543.1 | [+980.5, +2,398.4] | +753 | +91 | +247 | +133 | +112 | +207 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +945.8 | [+661.9, +1,403.6] | +348 | +108 | +149 | +91 | +74 | +177 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | +6,777.8 | [+3,557.6, +12,273.4] | +4,137 | +534 | +585 | +523 | +269 | +730 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | matched/diagonal | +3,525.6 | [+2,135.2, +5,845.4] | +1,840 | +289 | +375 | +281 | +262 | +479 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | matched/diagonal | -3,711.8 | [-5,589.9, -2,464.3] | -1,092 | -535 | -507 | -421 | -302 | -855 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | matched/diagonal | +5,316.3 | [+2,494.8, +9,999.2] | +3,623 | +219 | +410 | +321 | +294 | +451 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | matched/diagonal | +4,413.8 | [+2,247.0, +7,931.2] | +2,850 | +262 | +360 | +231 | +224 | +487 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | matched/diagonal | +1,969.1 | [+844.4, +3,755.2] | +1,429 | -5 | +75 | +148 | +147 | +175 |
| topology | `broad__direct` | `uniform_network` | matched/diagonal | +11,046.0 | [+6,682.4, +18,586.3] | +5,550 | +1,030 | +1,124 | +948 | +720 | +1,673 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | matched/diagonal | +3,026.6 | [+2,054.2, +4,636.0] | +1,215 | +242 | +326 | +494 | +250 | +499 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | matched/diagonal | -3,657.7 | [-5,972.6, -2,154.2] | -1,361 | -452 | -506 | -217 | -270 | -852 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | matched/diagonal | +4,235.5 | [+2,410.9, +7,288.7] | +2,439 | +235 | +336 | +489 | +329 | +408 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | matched/diagonal | +2,442.8 | [+1,376.7, +4,007.9] | +1,477 | +108 | +172 | +401 | +149 | +135 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | matched/diagonal | +1,425.5 | [+956.4, +2,024.7] | +619 | +79 | +199 | +311 | +136 | +81 |
| topology | `metrics__direct` | `uniform_network` | matched/diagonal | +11,670.6 | [+6,936.9, +19,824.1] | +5,941 | +994 | +1,182 | +980 | +742 | +1,831 |
| inputs (direct) | `metrics__direct` | `histories__direct` | matched/diagonal | +4,892.7 | [+3,166.6, +7,589.9] | +1,804 | +460 | +597 | +457 | +473 | +1,102 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +1,128.5 | [+668.4, +1,793.0] | +524 | +14 | +24 | +221 | +155 | +191 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +1,821.8 | [+1,159.9, +2,497.9] | +68 | +417 | +328 | +393 | +169 | +447 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +778.7 | [+279.8, +1,523.6] | +616 | -26 | +75 | -18 | +65 | +67 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | matched/correlation | +3,887.2 | [+2,531.0, +5,604.2] | +1,226 | +237 | +374 | +271 | +144 | +1,634 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | matched/correlation | +1,476.5 | [+971.0, +2,242.1] | +682 | +115 | +245 | +149 | +108 | +177 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +488.4 | [+168.9, +744.9] | -93 | +137 | +130 | +121 | +58 | +135 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | +3,727.3 | [+2,449.8, +5,548.3] | +1,151 | +661 | +531 | +659 | +184 | +541 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | matched/correlation | +1,451.0 | [+637.5, +2,095.9] | -231 | +366 | +356 | +367 | +214 | +378 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | matched/correlation | +206.6 | [-2,637.8, +4,423.4] | +2,889 | -706 | -470 | -644 | -197 | -666 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | matched/correlation | +2,810.8 | [+1,849.9, +4,257.7] | +1,053 | +358 | +389 | +435 | +235 | +340 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | matched/correlation | +2,510.1 | [+1,698.6, +3,679.6] | +932 | +360 | +340 | +322 | +177 | +379 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | matched/correlation | +675.8 | [+303.1, +1,021.8] | +78 | +92 | +68 | +210 | +120 | +108 |
| topology | `broad__direct` | `uniform_network` | matched/correlation | +4,316.4 | [+1,110.7, +6,872.0] | -1,243 | +1,334 | +1,059 | +1,293 | +548 | +1,326 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | matched/correlation | +843.9 | [-765.7, +2,000.5] | -973 | +352 | +305 | +556 | +207 | +397 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | matched/correlation | +1,238.0 | [-2,223.9, +6,487.8] | +3,672 | -690 | -459 | -516 | -136 | -633 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | matched/correlation | +1,767.0 | [+849.3, +2,540.2] | -41 | +363 | +329 | +581 | +248 | +288 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | matched/correlation | +1,410.0 | [+867.0, +1,994.3] | +412 | +202 | +169 | +424 | +126 | +76 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | matched/correlation | +1,008.4 | [+604.9, +1,414.2] | +270 | +110 | +196 | +276 | +119 | +38 |
| topology | `metrics__direct` | `uniform_network` | matched/correlation | +3,534.5 | [-1,062.4, +6,907.2] | -2,306 | +1,394 | +1,101 | +1,395 | +537 | +1,414 |
| inputs (direct) | `metrics__direct` | `histories__direct` | matched/correlation | -192.8 | [-5,439.9, +3,272.1] | -3,457 | +734 | +569 | +736 | +353 | +873 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | +266.5 | [-468.1, +768.0] | -401 | +70 | +35 | +238 | +152 | +172 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +2,348.1 | [+1,244.1, +4,205.4] | +875 | +260 | +144 | +207 | +283 | +579 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | -918.4 | [-1,755.2, -443.7] | -544 | -73 | -58 | -89 | -38 | -116 |
| pretrained vs Mahalanobis | `histories__tabfm__early_concat` | `histories__mahalanobis_lw` | median/diagonal | +4,803.1 | [+2,223.1, +8,892.7] | +3,307 | +77 | +336 | +129 | +164 | +790 |
| pretrained vs random autoencoder | `histories__tabfm__early_concat` | `histories__random_autoencoder` | median/diagonal | +89.9 | [-178.6, +337.0] | +66 | -30 | +81 | -7 | -2 | -19 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +137.1 | [+7.7, +268.5] | -14 | +37 | +39 | -12 | +20 | +67 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | +7,797.6 | [+4,080.6, +14,156.3] | +4,757 | +568 | +638 | +594 | +351 | +888 |
| pretrained vs supervised | `broad__tabfm__early_concat` | `broad__supervised_mlp16` | median/diagonal | +2,463.9 | [+1,500.7, +4,055.6] | +1,269 | +202 | +280 | +191 | +170 | +352 |
| pretrained vs direct | `broad__tabfm__early_concat` | `broad__direct` | median/diagonal | +4,039.1 | [+2,072.5, +7,213.1] | +2,588 | +263 | +328 | +267 | +203 | +389 |
| pretrained vs Mahalanobis | `broad__tabfm__early_concat` | `broad__mahalanobis_lw` | median/diagonal | +5,884.3 | [+2,966.3, +10,718.8] | +3,783 | +363 | +469 | +382 | +299 | +590 |
| pretrained vs random autoencoder | `broad__tabfm__early_concat` | `broad__random_autoencoder` | median/diagonal | +4,934.3 | [+2,503.2, +8,924.3] | +3,179 | +316 | +402 | +285 | +234 | +518 |
| labels vs constant labels | `broad__tabfm__early_concat` | `broad__tabfm__early_concat_labelnull` | median/diagonal | +2,345.0 | [+1,081.0, +4,393.7] | +1,643 | +90 | +176 | +134 | +110 | +192 |
| topology | `broad__direct` | `uniform_network` | median/diagonal | +2,526.9 | [+1,293.9, +4,666.5] | +1,549 | +167 | +199 | +170 | +133 | +309 |
| pretrained vs supervised | `metrics__tabfm__early_concat` | `metrics__supervised_mlp16` | median/diagonal | +1,733.0 | [+1,154.2, +2,634.9] | +616 | +130 | +205 | +271 | +130 | +381 |
| pretrained vs direct | `metrics__tabfm__early_concat` | `metrics__direct` | median/diagonal | +3,528.5 | [+2,010.7, +5,965.5] | +2,044 | +240 | +296 | +323 | +190 | +435 |
| pretrained vs Mahalanobis | `metrics__tabfm__early_concat` | `metrics__mahalanobis_lw` | median/diagonal | +5,676.6 | [+3,079.7, +10,022.4] | +3,394 | +368 | +447 | +454 | +322 | +691 |
| pretrained vs random autoencoder | `metrics__tabfm__early_concat` | `metrics__random_autoencoder` | median/diagonal | +3,925.8 | [+2,165.1, +6,755.4] | +2,373 | +262 | +300 | +358 | +193 | +439 |
| labels vs constant labels | `metrics__tabfm__early_concat` | `metrics__tabfm__early_concat_labelnull` | median/diagonal | +1,064.6 | [+665.3, +1,582.8] | +520 | +117 | +164 | +142 | +66 | +55 |
| topology | `metrics__direct` | `uniform_network` | median/diagonal | +3,663.1 | [+1,819.4, +6,859.2] | +2,298 | +234 | +261 | +233 | +181 | +456 |
| inputs (direct) | `metrics__direct` | `histories__direct` | median/diagonal | -4,134.5 | [-7,284.4, -2,259.7] | -2,460 | -334 | -377 | -361 | -170 | -433 |
| inputs (tabfm__early_concat) | `metrics__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +312.4 | [+149.9, +496.5] | +129 | -20 | -23 | +51 | +58 | +118 |

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical|exp | 90 | `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder` |
| diagonal|exp | 93 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `histories@income_assets__pca16`, `histories@income_assets__supervised_mlp16`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder` |
| correlation|exp | 93 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__supervised_mlp16`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__exaone__late`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean` |
| spherical|median | 90 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__autoencoder`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__pca16`, `metrics__autoencoder`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__exaone__late`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__tabpfn_full__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| diagonal|median | 93 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__pca16`, `broad__autoencoder`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__pca16`, `metrics__autoencoder`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `h3__fernandez_market_cap_assets`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| correlation|median | 93 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| spherical|matched | 90 | `metrics__direct` |
| diagonal|matched | 93 | `metrics__direct` |
| correlation|matched | 93 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |

## Label-permutation placebos (exp kernel, diagonal innovations)

Each prespecified network is compared with 19 permutations P W P' restricted
within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.

| Approach | Observed | Placebo mean | Placebo max | Rank p-value |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_joint` | 1,693,242.79 | 1,688,202.50 | 1,688,374.38 | 0.05 |
| `histories__direct` | 1,694,459.78 | 1,688,444.96 | 1,688,732.76 | 0.05 |
| `histories__pca16` | 1,694,856.59 | 1,688,352.45 | 1,688,626.56 | 0.05 |
| `histories__tabpfn_full__late` | 1,693,016.98 | 1,688,490.37 | 1,688,768.04 | 0.05 |
| `histories__tabfm__early_concat` | 1,692,207.61 | 1,688,694.46 | 1,688,958.78 | 0.05 |

## Network concentration

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform. The matched
kernel targets the joint network's mean effective neighbours under exp each year;
the last column is the largest achieved miss, in neighbours, over all years. Matching
the mean leaves row-wise concentration and spectral structure free to differ.

| Approach | exp | median | matched | Matched miss |
| --- | ---: | ---: | ---: | ---: |
| `broad__autoencoder` | 0.917 | 0.951 | 0.898 | 2.2e-09 |
| `broad__direct` | 0.992 | 0.996 | 0.898 | 1.3e-09 |
| `broad__exaone__item_first_concat` | 1.000 | 0.786 | 0.898 | 1.2e-09 |
| `broad__exaone__item_first_mean` | 1.000 | 0.771 | 0.898 | 1.4e-09 |
| `broad__exaone__item_last_concat` | 0.981 | 0.868 | 0.898 | 2.7e-10 |
| `broad__exaone__late` | 0.952 | 0.752 | 0.898 | 4.5e-10 |
| `broad__mahalanobis_lw` | 0.076 | 0.991 | 0.898 | 1.2e-09 |
| `broad__pca16` | 0.928 | 0.961 | 0.898 | 1.7e-09 |
| `broad__random_autoencoder` | 0.957 | 0.973 | 0.898 | 7.6e-10 |
| `broad__supervised_mlp16` | 0.857 | 0.885 | 0.898 | 6.7e-12 |
| `broad__tabfm__early_concat` | 0.975 | 0.918 | 0.898 | 8.9e-10 |
| `broad__tabfm__early_concat_labelnull` | 0.997 | 0.936 | 0.898 | 7.6e-10 |
| `broad__tabfm__early_mean` | 0.975 | 0.916 | 0.898 | 1.2e-09 |
| `broad__tabfm__late` | 0.991 | 0.850 | 0.898 | 6.9e-11 |
| `broad__tabpfn_fast__late` | 0.969 | 0.848 | 0.898 | 2.8e-11 |
| `broad__tabpfn_full__late` | 0.938 | 0.841 | 0.898 | 4.8e-11 |
| `fernandez_dividend_yield` | 0.795 | 0.885 | 0.898 | 1e-09 |
| `fernandez_joint` | 0.898 | 0.942 | 0.898 | 9.5e-11 |
| `fernandez_market_cap_assets` | 0.801 | 0.885 | 0.898 | 1.9e-12 |
| `fernandez_market_to_book` | 0.804 | 0.883 | 0.898 | 1.9e-10 |
| `h3__fernandez_dividend_yield` | 0.640 | 0.655 | 0.898 | 1.6e-09 |
| `h3__fernandez_joint` | 0.785 | 0.875 | 0.898 | 1.6e-10 |
| `h3__fernandez_market_cap_assets` | 0.636 | 0.636 | 0.898 | 1.7e-09 |
| `h3__fernandez_market_to_book` | 0.638 | 0.654 | 0.898 | 1.4e-09 |
| `h3__histories__autoencoder` | 0.886 | 0.800 | 0.898 | 1.2e-09 |
| `h3__histories__direct` | 0.918 | 0.831 | 0.898 | 6.5e-10 |
| `h3__histories__exaone__item_first_concat` | 1.000 | 0.800 | 0.898 | 6.9e-10 |
| `h3__histories__exaone__item_first_mean` | 1.000 | 0.787 | 0.898 | 1.5e-09 |
| `h3__histories__exaone__item_last_concat` | 0.981 | 0.849 | 0.898 | 1.3e-09 |
| `h3__histories__exaone__late` | 0.952 | 0.745 | 0.898 | 7.5e-10 |
| `h3__histories__mahalanobis_lw` | 0.741 | 0.811 | 0.898 | 6.7e-10 |
| `h3__histories__pca16` | 0.891 | 0.838 | 0.898 | 2.4e-10 |
| `h3__histories__random_autoencoder` | 0.949 | 0.816 | 0.898 | 2e-09 |
| `h3__histories__supervised_mlp16` | 0.817 | 0.614 | 0.898 | 3.8e-10 |
| `h3__histories__tabfm__early_concat` | 0.971 | 0.906 | 0.898 | 4.1e-10 |
| `h3__histories__tabfm__early_concat_labelnull` | 0.995 | 0.864 | 0.898 | 9.2e-10 |
| `h3__histories__tabfm__early_mean` | 0.970 | 0.906 | 0.898 | 4.1e-10 |
| `h3__histories__tabfm__late` | 0.990 | 0.826 | 0.898 | 4.1e-10 |
| `h3__histories__tabpfn_fast__late` | 0.967 | 0.842 | 0.898 | 7.8e-11 |
| `h3__histories__tabpfn_full__late` | 0.939 | 0.836 | 0.898 | 5.8e-11 |
| `histories@income_assets__autoencoder` | 0.923 | 0.806 | 0.898 | 8.9e-10 |
| `histories@income_assets__direct` | 0.936 | 0.860 | 0.898 | 1.7e-09 |
| `histories@income_assets__exaone__item_first_concat` | 1.000 | 0.789 | 0.898 | 1e-09 |
| `histories@income_assets__exaone__item_first_mean` | 1.000 | 0.776 | 0.898 | 1.4e-09 |
| `histories@income_assets__exaone__item_last_concat` | 0.993 | 0.907 | 0.898 | 1.6e-09 |
| `histories@income_assets__exaone__late` | 0.979 | 0.815 | 0.898 | 1.2e-09 |
| `histories@income_assets__mahalanobis_lw` | 0.625 | 0.834 | 0.898 | 1.1e-10 |
| `histories@income_assets__pca16` | 0.926 | 0.850 | 0.898 | 1.7e-09 |
| `histories@income_assets__random_autoencoder` | 0.957 | 0.839 | 0.898 | 1.1e-09 |
| `histories@income_assets__supervised_mlp16` | 0.816 | 0.803 | 0.898 | 1.8e-09 |
| `histories@income_assets__tabfm__early_concat` | 0.957 | 0.913 | 0.898 | 1e-09 |
| `histories@income_assets__tabfm__early_concat_labelnull` | 0.993 | 0.874 | 0.898 | 4e-10 |
| `histories@income_assets__tabfm__early_mean` | 0.957 | 0.913 | 0.898 | 1e-09 |
| `histories@income_assets__tabfm__late` | 0.995 | 0.892 | 0.898 | 3.3e-10 |
| `histories@income_assets__tabpfn_fast__late` | 0.986 | 0.858 | 0.898 | 1.9e-09 |
| `histories@income_assets__tabpfn_full__late` | 0.961 | 0.843 | 0.898 | 2e-09 |
| `histories__autoencoder` | 0.899 | 0.813 | 0.898 | 1.5e-09 |
| `histories__direct` | 0.925 | 0.864 | 0.898 | 1.1e-09 |
| `histories__exaone__item_first_concat` | 1.000 | 0.795 | 0.898 | 1.4e-09 |
| `histories__exaone__item_first_mean` | 1.000 | 0.781 | 0.898 | 1.1e-09 |
| `histories__exaone__item_last_concat` | 0.981 | 0.856 | 0.898 | 1e-09 |
| `histories__exaone__late` | 0.951 | 0.747 | 0.898 | 8e-10 |
| `histories__mahalanobis_lw` | 0.633 | 0.831 | 0.898 | 6.5e-10 |
| `histories__pca16` | 0.913 | 0.853 | 0.898 | 3.3e-10 |
| `histories__random_autoencoder` | 0.955 | 0.839 | 0.898 | 1.2e-09 |
| `histories__supervised_mlp16` | 0.784 | 0.655 | 0.898 | 1.4e-09 |
| `histories__tabfm__early_concat` | 0.972 | 0.905 | 0.898 | 6.5e-12 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.874 | 0.898 | 3.5e-10 |
| `histories__tabfm__early_mean` | 0.972 | 0.905 | 0.898 | 4.4e-10 |
| `histories__tabfm__late` | 0.990 | 0.829 | 0.898 | 3.1e-10 |
| `histories__tabpfn_fast__late` | 0.967 | 0.844 | 0.898 | 2.8e-11 |
| `histories__tabpfn_full__late` | 0.938 | 0.841 | 0.898 | 4e-11 |
| `metrics__autoencoder` | 0.911 | 0.944 | 0.898 | 4.9e-11 |
| `metrics__direct` | 0.985 | 0.993 | 0.898 | 1.2e-09 |
| `metrics__exaone__item_first_concat` | 1.000 | 0.807 | 0.898 | 1.4e-09 |
| `metrics__exaone__item_first_mean` | 1.000 | 0.778 | 0.898 | 1.3e-09 |
| `metrics__exaone__item_last_concat` | 0.980 | 0.864 | 0.898 | 6.5e-10 |
| `metrics__exaone__late` | 0.951 | 0.749 | 0.898 | 3.7e-10 |
| `metrics__mahalanobis_lw` | 0.106 | 0.983 | 0.898 | 1.1e-09 |
| `metrics__pca16` | 0.915 | 0.952 | 0.898 | 2e-10 |
| `metrics__random_autoencoder` | 0.961 | 0.968 | 0.898 | 3.9e-10 |
| `metrics__supervised_mlp16` | 0.851 | 0.879 | 0.898 | 7.6e-10 |
| `metrics__tabfm__early_concat` | 0.980 | 0.919 | 0.898 | 8.1e-11 |
| `metrics__tabfm__early_concat_labelnull` | 0.998 | 0.916 | 0.898 | 7.5e-10 |
| `metrics__tabfm__early_mean` | 0.979 | 0.916 | 0.898 | 1.7e-09 |
| `metrics__tabfm__late` | 0.991 | 0.842 | 0.898 | 8.8e-11 |
| `metrics__tabpfn_fast__late` | 0.968 | 0.849 | 0.898 | 1.6e-11 |
| `metrics__tabpfn_full__late` | 0.937 | 0.842 | 0.898 | 2.3e-11 |
| `uniform_network` | nan | nan | nan | nan |
| `zero_network` | nan | nan | nan | nan |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
