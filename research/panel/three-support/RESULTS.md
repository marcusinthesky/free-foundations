# Panel design `three-support`

Characteristics: market_cap_assets, market_to_book, dividend_yield. Network history: 5 annual snapshots; cohort requires complete, nonconstant 3- and 5-year histories. All rows score the same 642,024 held-out firm-days (2020-2025).
One spatial coefficient per network, kernel and innovation arm is fitted on
2016-2019 and frozen. Cells are held-out log-likelihood gains over the joint
Fernández network (`fernandez_joint`, exp kernel) within the same innovation arm;
higher is better. Columns are kernel/innovation; `correlation` imposes prior raw
sample variances on every row so only implied correlations differ.

## Cohorts

| Return year | Firms | Prior complete days | Scored days | Reference firms |
| --- | ---: | ---: | ---: | ---: |
| 2016 | 329 | 756 | 251 | 409 |
| 2017 | 381 | 756 | 250 | 383 |
| 2018 | 386 | 755 | 250 | 397 |
| 2019 | 396 | 754 | 251 | 412 |
| 2020 | 406 | 754 | 252 | 419 |
| 2021 | 413 | 756 | 251 | 424 |
| 2022 | 421 | 757 | 250 | 440 |
| 2023 | 429 | 755 | 249 | 457 |
| 2024 | 437 | 753 | 251 | 472 |
| 2025 | 459 | 753 | 249 | 484 |

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `covariance_exposures` | control | -3,138.57 | -4,414.38 | +8,016.21 | +7,347.07 | -2,355.55 |
| `reference_exposures` | control | -3,146.30 | -4,430.15 | +7,454.72 | +7,298.10 | -2,373.93 |
| `fernandez_market_cap_assets` | fernandez | +298.20 | -322.86 | -793.72 | -1,025.51 | -106.37 |
| `fernandez_market_to_book` | fernandez | -800.87 | -1,778.48 | -2,072.82 | -2,156.96 | -769.94 |
| `fernandez_dividend_yield` | fernandez | -983.78 | -834.81 | -1,337.76 | -1,505.93 | -424.59 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -915.75 | -0.00 | +0.00 |
| `histories@decoded__direct` | calibrated | -3,234.93 | -4,576.87 | +1,852.54 | +295.90 | -2,475.76 |
| `histories@decoded__pca16` | calibrated | -3,236.51 | -4,578.80 | +508.00 | -236.61 | -2,477.38 |
| `histories@decoded__supervised_mlp16` | calibrated | -3,235.81 | -4,578.52 | -4,493.29 | -808.76 | -2,476.07 |
| `histories@decoded__tabpfn_full__late` | calibrated | -3,217.53 | -4,544.74 | +4,371.18 | +3,330.98 | -2,454.73 |
| `histories@decoded__tabpfn_full_random__late` | calibrated | -3,225.93 | -4,558.45 | +2,923.47 | +1,859.71 | -2,464.64 |
| `histories@decoded__tabfm__early_concat` | calibrated | -3,221.36 | -4,552.49 | +3,766.14 | +2,877.20 | -2,458.80 |
| `histories@decoded__tabfm__early_concat_labelnull` | calibrated | -3,224.71 | -4,559.92 | +3,063.70 | +2,209.99 | -2,463.37 |
| `histories__direct` | classical | +818.94 | +1,216.98 | +3,206.89 | +2,187.09 | +1,045.94 |
| `histories__pca16` | control | +1,189.16 | +1,613.80 | +3,423.74 | +2,208.47 | +1,239.14 |
| `histories__supervised_mlp16` | task | +68.42 | -51.73 | -59.62 | -1,133.11 | +1,027.66 |
| `histories__tabpfn_full__late` | task | -558.96 | -225.81 | +2,111.74 | +716.72 | +213.70 |
| `histories__tabpfn_full_random__late` | control | -3,041.08 | -4,237.09 | -347.83 | -32.08 | -2,215.48 |
| `histories__tabfm__early_concat` | state | -842.03 | -1,035.18 | +2,288.49 | +2,293.63 | +236.58 |
| `histories__tabfm__early_concat_labelnull` | state | -2,463.96 | -3,367.66 | +2,151.37 | +1,347.78 | -1,549.58 |
| `histories@support32@decoded__pca16` | calibrated | -3,236.45 | -4,579.10 | +1,098.44 | -43.56 | -2,477.48 |
| `histories@support32@decoded__supervised_mlp16` | calibrated | -3,233.75 | -4,573.16 | +1,892.64 | +320.70 | -2,473.28 |
| `histories@support32@decoded__tabpfn_full__late` | calibrated | -3,216.70 | -4,544.18 | +4,026.44 | +3,293.41 | -2,453.82 |
| `histories@support32@decoded__tabpfn_full_random__late` | calibrated | -3,228.17 | -4,562.18 | +2,617.84 | +1,633.64 | -2,466.95 |
| `histories@support32@decoded__tabfm__early_concat` | calibrated | -3,222.16 | -4,553.85 | +3,498.48 | +2,615.20 | -2,460.16 |
| `histories@support32@decoded__tabfm__early_concat_labelnull` | calibrated | -3,224.58 | -4,558.28 | +3,254.95 | +2,305.72 | -2,463.32 |
| `histories@support32__pca16` | control | +1,501.34 | +1,795.86 | +3,475.82 | +2,455.57 | +1,469.09 |
| `histories@support32__supervised_mlp16` | task | -327.08 | -551.17 | -957.10 | -1,314.47 | +567.78 |
| `histories@support32__tabpfn_full__late` | task | -505.80 | -5.06 | +1,951.94 | +363.06 | +302.95 |
| `histories@support32__tabpfn_full_random__late` | control | -3,007.56 | -4,172.42 | -1,045.38 | -1,045.81 | -2,157.35 |
| `histories@support32__tabfm__early_concat` | state | -1,630.45 | -2,050.46 | +2,131.90 | +1,506.57 | -609.35 |
| `histories@support32__tabfm__early_concat_labelnull` | state | -2,454.30 | -3,349.57 | +1,756.38 | +548.70 | -1,517.06 |
| `histories@support64@decoded__pca16` | calibrated | -3,236.45 | -4,578.63 | +355.66 | -63.47 | -2,476.70 |
| `histories@support64@decoded__supervised_mlp16` | calibrated | -3,235.45 | -4,576.95 | +1,120.18 | -345.72 | -2,475.72 |
| `histories@support64@decoded__tabpfn_full__late` | calibrated | -3,216.27 | -4,543.85 | +4,269.88 | +3,396.60 | -2,453.65 |
| `histories@support64@decoded__tabpfn_full_random__late` | calibrated | -3,227.38 | -4,561.56 | +2,831.47 | +1,702.62 | -2,466.15 |
| `histories@support64@decoded__tabfm__early_concat` | calibrated | -3,221.30 | -4,551.60 | +3,918.60 | +2,950.82 | -2,459.09 |
| `histories@support64@decoded__tabfm__early_concat_labelnull` | calibrated | -3,223.12 | -4,555.00 | +3,667.94 | +2,573.32 | -2,461.86 |
| `histories@support64__pca16` | control | +1,566.31 | +1,980.52 | +3,570.76 | +2,502.78 | +1,261.64 |
| `histories@support64__supervised_mlp16` | task | -234.66 | -175.06 | -583.72 | -1,077.88 | +580.56 |
| `histories@support64__tabpfn_full__late` | task | -508.14 | +80.83 | +2,133.18 | +641.58 | +287.28 |
| `histories@support64__tabpfn_full_random__late` | control | -3,048.75 | -4,244.10 | -1,089.65 | -1,101.63 | -2,218.66 |
| `histories@support64__tabfm__early_concat` | state | -1,490.77 | -1,938.03 | +2,235.59 | +1,615.77 | -467.40 |
| `histories@support64__tabfm__early_concat_labelnull` | state | -2,458.14 | -3,401.29 | +2,054.52 | +975.97 | -1,543.30 |
| `histories@support128@decoded__pca16` | calibrated | -3,236.37 | -4,578.84 | +896.64 | +45.57 | -2,476.77 |
| `histories@support128@decoded__supervised_mlp16` | calibrated | -3,235.10 | -4,575.95 | +1,325.91 | +24.77 | -2,475.21 |
| `histories@support128@decoded__tabpfn_full__late` | calibrated | -3,216.59 | -4,543.99 | +4,263.27 | +3,281.85 | -2,453.78 |
| `histories@support128@decoded__tabpfn_full_random__late` | calibrated | -3,226.37 | -4,559.71 | +3,036.72 | +1,993.66 | -2,464.93 |
| `histories@support128@decoded__tabfm__early_concat` | calibrated | -3,220.87 | -4,551.12 | +3,511.22 | +2,735.38 | -2,458.60 |
| `histories@support128@decoded__tabfm__early_concat_labelnull` | calibrated | -3,225.40 | -4,560.26 | +3,113.43 | +2,032.38 | -2,463.85 |
| `histories@support128__pca16` | control | +1,466.88 | +2,005.70 | +3,598.29 | +2,459.54 | +1,186.03 |
| `histories@support128__supervised_mlp16` | task | +113.24 | +5.38 | -193.08 | -1,056.27 | +1,158.00 |
| `histories@support128__tabpfn_full__late` | task | -694.83 | -423.59 | +1,920.23 | +540.09 | +132.59 |
| `histories@support128__tabpfn_full_random__late` | control | -3,044.18 | -4,242.80 | -882.03 | -829.19 | -2,218.02 |
| `histories@support128__tabfm__early_concat` | state | -1,028.36 | -1,365.83 | +2,256.29 | +1,950.31 | +36.03 |
| `histories@support128__tabfm__early_concat_labelnull` | state | -2,480.80 | -3,397.49 | +1,839.36 | +896.96 | -1,575.97 |
| `h3__fernandez_market_cap_assets` | fernandez | -2,106.30 | -5,356.71 | -5,356.71 | -3,590.96 | -2,159.10 |
| `h3__fernandez_market_to_book` | fernandez | -2,294.23 | -5,334.64 | -5,282.49 | -3,708.46 | -2,472.82 |
| `h3__fernandez_dividend_yield` | fernandez | -2,411.17 | -4,449.07 | -4,503.31 | -3,286.53 | -2,006.15 |
| `h3__fernandez_joint` | fernandez | -1,136.54 | -2,535.10 | -2,590.42 | -2,663.92 | -654.53 |
| `h3__histories__direct` | classical | +686.62 | +987.29 | +2,987.03 | +1,540.46 | +1,162.35 |
| `h3__histories__pca16` | control | +1,460.66 | +1,929.57 | +2,954.31 | +1,696.03 | +1,459.64 |
| `h3__histories__supervised_mlp16` | task | -348.15 | -746.26 | -2,721.48 | -1,513.78 | +731.34 |
| `h3__histories__tabpfn_full__late` | task | -617.99 | -340.69 | +1,989.66 | +582.99 | +207.69 |
| `h3__histories__tabpfn_full_random__late` | control | -3,049.42 | -4,253.61 | -651.35 | -168.50 | -2,217.01 |
| `h3__histories__tabfm__early_concat` | state | -894.66 | -1,091.37 | +1,824.62 | +1,944.36 | +194.04 |
| `h3__histories__tabfm__early_concat_labelnull` | state | -2,525.76 | -3,487.40 | +1,584.37 | +628.41 | -1,601.34 |
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
| `covariance_exposures` | -4,414.38 | [-7,984.2, -2,415.0] | [-8,347.4, -2,208.3] | 49.7 |
| `reference_exposures` | -4,430.15 | [-8,009.0, -2,426.0] | [-8,374.5, -2,218.1] | 49.7 |
| `fernandez_market_cap_assets` | -322.86 | [-805.0, -4.4] | [-930.1, +48.7] | 50.2 |
| `fernandez_market_to_book` | -1,778.48 | [-3,625.9, -688.2] | [-3,926.0, -558.4] | 53.7 |
| `fernandez_dividend_yield` | -834.81 | [-1,837.7, -250.2] | [-1,973.8, -161.9] | 42.3 |
| `histories@decoded__direct` | -4,576.87 | [-8,277.5, -2,505.1] | [-8,653.8, -2,290.5] | 49.7 |
| `histories@decoded__pca16` | -4,578.80 | [-8,280.4, -2,506.8] | [-8,656.2, -2,292.0] | 49.7 |
| `histories@decoded__supervised_mlp16` | -4,578.52 | [-8,280.9, -2,506.1] | [-8,657.3, -2,291.1] | 49.7 |
| `histories@decoded__tabpfn_full__late` | -4,544.74 | [-8,217.1, -2,488.7] | [-8,592.2, -2,276.0] | 49.7 |
| `histories@decoded__tabpfn_full_random__late` | -4,558.45 | [-8,241.2, -2,496.6] | [-8,617.0, -2,283.1] | 49.7 |
| `histories@decoded__tabfm__early_concat` | -4,552.49 | [-8,231.4, -2,492.9] | [-8,606.4, -2,279.4] | 49.7 |
| `histories@decoded__tabfm__early_concat_labelnull` | -4,559.92 | [-8,245.1, -2,496.9] | [-8,620.8, -2,282.9] | 49.7 |
| `histories__direct` | +1,216.98 | [+363.1, +2,412.5] | [+156.5, +2,802.8] | 63.3 |
| `histories__pca16` | +1,613.80 | [+538.1, +3,175.9] | [+271.5, +3,636.2] | 62.7 |
| `histories__supervised_mlp16` | -51.73 | [-884.1, +1,032.2] | [-1,044.6, +1,342.1] | 11.1 |
| `histories__tabpfn_full__late` | -225.81 | [-784.6, +440.5] | [-847.0, +593.5] | 37.6 |
| `histories__tabpfn_full_random__late` | -4,237.09 | [-7,621.7, -2,345.2] | [-7,945.0, -2,154.2] | 49.1 |
| `histories__tabfm__early_concat` | -1,035.18 | [-1,873.6, -440.3] | [-1,833.4, -386.0] | 35.1 |
| `histories__tabfm__early_concat_labelnull` | -3,367.66 | [-5,970.3, -1,904.0] | [-6,169.2, -1,778.3] | 46.9 |
| `histories@support32@decoded__pca16` | -4,579.10 | [-8,281.0, -2,506.7] | [-8,657.7, -2,291.8] | 49.7 |
| `histories@support32@decoded__supervised_mlp16` | -4,573.16 | [-8,268.5, -2,504.7] | [-8,644.8, -2,289.8] | 49.7 |
| `histories@support32@decoded__tabpfn_full__late` | -4,544.18 | [-8,217.3, -2,488.2] | [-8,590.4, -2,275.0] | 49.7 |
| `histories@support32@decoded__tabpfn_full_random__late` | -4,562.18 | [-8,248.2, -2,498.3] | [-8,624.8, -2,284.5] | 49.7 |
| `histories@support32@decoded__tabfm__early_concat` | -4,553.85 | [-8,232.2, -2,494.3] | [-8,607.7, -2,281.0] | 49.7 |
| `histories@support32@decoded__tabfm__early_concat_labelnull` | -4,558.28 | [-8,241.8, -2,496.8] | [-8,616.7, -2,282.8] | 49.7 |
| `histories@support32__pca16` | +1,795.86 | [+749.5, +3,302.1] | [+500.6, +3,730.1] | 35.0 |
| `histories@support32__supervised_mlp16` | -551.17 | [-1,379.0, +418.9] | [-1,398.9, +599.6] | 23.5 |
| `histories@support32__tabpfn_full__late` | -5.06 | [-637.3, +788.3] | [-827.6, +1,128.7] | 65.9 |
| `histories@support32__tabpfn_full_random__late` | -4,172.42 | [-7,510.8, -2,308.1] | [-7,808.5, -2,125.7] | 48.9 |
| `histories@support32__tabfm__early_concat` | -2,050.46 | [-3,490.3, -1,155.4] | [-3,524.3, -1,087.1] | 40.7 |
| `histories@support32__tabfm__early_concat_labelnull` | -3,349.57 | [-5,848.8, -1,934.6] | [-6,028.8, -1,811.5] | 45.8 |
| `histories@support64@decoded__pca16` | -4,578.63 | [-8,280.3, -2,506.4] | [-8,657.4, -2,291.8] | 49.7 |
| `histories@support64@decoded__supervised_mlp16` | -4,576.95 | [-8,276.7, -2,505.7] | [-8,653.5, -2,290.9] | 49.7 |
| `histories@support64@decoded__tabpfn_full__late` | -4,543.85 | [-8,215.9, -2,488.5] | [-8,589.2, -2,275.5] | 49.7 |
| `histories@support64@decoded__tabpfn_full_random__late` | -4,561.56 | [-8,248.2, -2,497.4] | [-8,624.7, -2,283.8] | 49.7 |
| `histories@support64@decoded__tabfm__early_concat` | -4,551.60 | [-8,228.8, -2,493.1] | [-8,603.4, -2,279.6] | 49.7 |
| `histories@support64@decoded__tabfm__early_concat_labelnull` | -4,555.00 | [-8,234.5, -2,495.4] | [-8,609.6, -2,281.7] | 49.7 |
| `histories@support64__pca16` | +1,980.52 | [+689.7, +3,873.5] | [+388.3, +4,417.8] | 61.6 |
| `histories@support64__supervised_mlp16` | -175.06 | [-979.5, +875.6] | [-1,138.3, +1,185.6] | 59.8 |
| `histories@support64__tabpfn_full__late` | +80.83 | [-558.1, +881.8] | [-749.4, +1,224.0] | 65.9 |
| `histories@support64__tabpfn_full_random__late` | -4,244.10 | [-7,647.4, -2,341.9] | [-7,970.8, -2,151.9] | 49.1 |
| `histories@support64__tabfm__early_concat` | -1,938.03 | [-3,434.9, -1,035.8] | [-3,469.1, -968.7] | 39.9 |
| `histories@support64__tabfm__early_concat_labelnull` | -3,401.29 | [-6,016.5, -1,928.3] | [-6,221.4, -1,796.8] | 46.6 |
| `histories@support128@decoded__pca16` | -4,578.84 | [-8,280.5, -2,506.4] | [-8,657.8, -2,291.7] | 49.7 |
| `histories@support128@decoded__supervised_mlp16` | -4,575.95 | [-8,273.9, -2,506.0] | [-8,650.8, -2,291.1] | 49.7 |
| `histories@support128@decoded__tabpfn_full__late` | -4,543.99 | [-8,217.2, -2,488.0] | [-8,590.5, -2,274.8] | 49.7 |
| `histories@support128@decoded__tabpfn_full_random__late` | -4,559.71 | [-8,244.4, -2,497.0] | [-8,620.6, -2,283.1] | 49.7 |
| `histories@support128@decoded__tabfm__early_concat` | -4,551.12 | [-8,227.0, -2,493.2] | [-8,602.2, -2,279.8] | 49.7 |
| `histories@support128@decoded__tabfm__early_concat_labelnull` | -4,560.26 | [-8,245.6, -2,497.2] | [-8,621.1, -2,283.4] | 49.7 |
| `histories@support128__pca16` | +2,005.70 | [+684.9, +3,964.2] | [+385.4, +4,526.5] | 61.6 |
| `histories@support128__supervised_mlp16` | +5.38 | [-963.2, +1,259.5] | [-1,136.6, +1,622.4] | 21.6 |
| `histories@support128__tabpfn_full__late` | -423.59 | [-1,002.9, +214.3] | [-1,028.3, +333.8] | 36.0 |
| `histories@support128__tabpfn_full_random__late` | -4,242.80 | [-7,637.0, -2,345.3] | [-7,960.4, -2,156.0] | 49.1 |
| `histories@support128__tabfm__early_concat` | -1,365.83 | [-2,472.5, -627.2] | [-2,455.0, -578.2] | 35.8 |
| `histories@support128__tabfm__early_concat_labelnull` | -3,397.49 | [-6,028.9, -1,918.3] | [-6,223.7, -1,787.0] | 47.2 |
| `h3__fernandez_market_cap_assets` | -5,356.71 | [-11,510.4, -1,723.3] | [-12,489.1, -1,184.3] | 53.3 |
| `h3__fernandez_market_to_book` | -5,334.64 | [-11,441.1, -1,863.4] | [-12,267.9, -1,394.4] | 50.7 |
| `h3__fernandez_dividend_yield` | -4,449.07 | [-9,415.9, -1,493.6] | [-10,235.7, -962.8] | 53.8 |
| `h3__fernandez_joint` | -2,535.10 | [-5,800.5, -603.0] | [-6,317.1, -281.8] | 52.2 |
| `h3__histories__direct` | +987.29 | [+146.4, +2,091.7] | [-111.9, +2,540.1] | 45.0 |
| `h3__histories__pca16` | +1,929.57 | [+681.8, +3,718.2] | [+346.4, +4,266.5] | 63.3 |
| `h3__histories__supervised_mlp16` | -746.26 | [-1,835.3, +409.2] | [-1,824.1, +606.5] | 40.0 |
| `h3__histories__tabpfn_full__late` | -340.69 | [-937.9, +326.8] | [-962.9, +455.0] | 37.2 |
| `h3__histories__tabpfn_full_random__late` | -4,253.61 | [-7,660.6, -2,351.1] | [-7,977.4, -2,162.4] | 49.0 |
| `h3__histories__tabfm__early_concat` | -1,091.37 | [-1,984.3, -469.2] | [-1,958.4, -418.9] | 36.2 |
| `h3__histories__tabfm__early_concat_labelnull` | -3,487.40 | [-6,241.3, -1,943.4] | [-6,467.1, -1,807.6] | 47.4 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +3,426.7 | [+2,190.8, +5,593.2] | +1,543 | +359 | +367 | +345 | +236 | +577 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +106.5 | [-208.9, +322.9] | -81 | -6 | +67 | +19 | +48 | +60 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +945.8 | [+661.9, +1,403.6] | +348 | +108 | +149 | +91 | +74 | +177 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | +6,777.8 | [+3,557.6, +12,273.4] | +4,137 | +534 | +585 | +523 | +269 | +730 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +583.6 | [-192.7, +1,222.0] | -432 | +216 | +242 | +105 | +89 | +365 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,581.3 | [+1,708.1, +3,995.2] | +932 | +283 | +324 | +217 | +241 | +583 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/diagonal | +2,614.3 | [+1,543.4, +3,961.2] | +375 | +419 | +519 | +379 | +195 | +726 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +3,035.1 | [+2,182.9, +4,366.9] | +942 | +314 | +431 | +325 | +323 | +700 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/diagonal | +324.4 | [-424.0, +892.9] | -532 | +276 | +113 | +128 | +80 | +260 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/diagonal | -1,104.7 | [-2,231.2, -465.5] | -711 | -15 | -171 | -105 | -4 | -98 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +1,821.8 | [+1,159.9, +2,497.9] | +68 | +417 | +328 | +393 | +169 | +447 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +778.7 | [+279.8, +1,523.6] | +616 | -26 | +75 | -18 | +65 | +67 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +488.4 | [+168.9, +744.9] | -93 | +137 | +130 | +121 | +58 | +135 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | +3,727.3 | [+2,449.8, +5,548.3] | +1,151 | +661 | +531 | +659 | +184 | +541 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | -3,270.4 | [-8,746.3, +304.3] | -4,220 | +350 | +200 | +223 | -18 | +193 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,278.9 | [-5,289.8, +1,325.4] | -2,819 | +424 | +289 | +329 | +110 | +389 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/correlation | -2,373.8 | [-8,234.4, +1,565.9] | -4,426 | +611 | +428 | +499 | +38 | +477 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -1,617.8 | [-6,716.3, +1,645.0] | -3,554 | +488 | +370 | +445 | +153 | +480 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/correlation | -164.5 | [-1,258.8, +647.8] | -896 | +259 | +90 | +166 | +35 | +182 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/correlation | +5.2 | [-442.3, +579.4] | +437 | -83 | -150 | -122 | -7 | -70 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +2,348.1 | [+1,244.1, +4,205.4] | +875 | +260 | +144 | +207 | +283 | +579 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | -918.4 | [-1,755.2, -443.7] | -544 | -73 | -58 | -89 | -38 | -116 |
| labels vs constant labels | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +137.1 | [+7.7, +268.5] | -14 | +37 | +39 | -12 | +20 | +67 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | +7,797.6 | [+4,080.6, +14,156.3] | +4,757 | +568 | +638 | +594 | +351 | +888 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +1,477.7 | [+550.0, +2,276.5] | -313 | +378 | +452 | +233 | +164 | +564 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,913.6 | [+1,082.3, +3,216.2] | +797 | +118 | +173 | +116 | +214 | +496 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | median/diagonal | +2,259.4 | [+1,094.7, +3,439.6] | -93 | +448 | +553 | +367 | +194 | +791 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,518.6 | [+1,598.2, +3,922.0] | +928 | +113 | +259 | +228 | +332 | +659 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | median/diagonal | -4,433.7 | [-10,691.9, -481.0] | -4,790 | +295 | -22 | -25 | +125 | -16 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | median/diagonal | -6,345.8 | [-12,960.3, -2,549.2] | -4,555 | -225 | -445 | -348 | -108 | -664 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | matched/diagonal | -680.5 | [-1,223.5, -333.4] | -251 | -118 | -108 | -91 | +6 | -117 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | matched/correlation | +175.9 | [-371.0, +924.7] | +551 | -147 | -79 | -125 | +40 | -64 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | median/diagonal | -1,075.0 | [-1,953.5, -562.2] | -492 | -118 | -98 | -140 | -24 | -203 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | matched/diagonal | -949.0 | [-1,705.8, -492.1] | -424 | -149 | -106 | -106 | -30 | -135 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | matched/correlation | +100.9 | [-519.4, +961.9] | +574 | -185 | -78 | -153 | +17 | -73 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | median/diagonal | -1,343.9 | [-2,502.5, -682.7] | -689 | -129 | -101 | -153 | -50 | -223 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | matched/diagonal | +2,821.0 | [+1,700.8, +4,787.0] | +1,463 | +262 | +230 | +235 | +222 | +409 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | matched/correlation | +1,430.0 | [+954.1, +1,944.2] | +127 | +313 | +216 | +289 | +167 | +317 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | median/diagonal | +3,089.0 | [+1,762.7, +5,514.6] | +1,543 | +294 | +280 | +152 | +276 | +544 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__tabfm__early_concat_labelnull` | matched/diagonal | +957.9 | [+500.2, +1,681.4] | +578 | +59 | +15 | +83 | +79 | +143 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__tabfm__early_concat_labelnull` | matched/correlation | +189.9 | [-433.2, +615.3] | -286 | +127 | +23 | +147 | +63 | +115 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__tabfm__early_concat_labelnull` | median/diagonal | +375.5 | [+189.5, +542.8] | +41 | +68 | +77 | +31 | +59 | +99 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories__direct` | matched/diagonal | -1,824.0 | [-3,430.4, -938.5] | -965 | -189 | -160 | -188 | -40 | -283 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories__direct` | matched/correlation | -398.0 | [-984.8, +281.2] | +359 | -240 | -120 | -226 | +11 | -183 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories__direct` | median/diagonal | -1,254.9 | [-2,598.2, -498.8] | -653 | -130 | -116 | -137 | -8 | -212 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__pca16` | matched/diagonal | -2,092.5 | [-3,918.8, -1,081.5] | -1,138 | -219 | -158 | -202 | -76 | -300 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__pca16` | matched/correlation | -473.0 | [-1,151.6, +306.4] | +382 | -278 | -119 | -254 | -12 | -192 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__pca16` | median/diagonal | -1,523.9 | [-3,154.8, -625.2] | -849 | -140 | -119 | -150 | -34 | -232 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__supervised_mlp16` | matched/diagonal | +1,677.5 | [+1,144.8, +2,541.9] | +749 | +192 | +179 | +138 | +176 | +244 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__supervised_mlp16` | matched/correlation | +856.0 | [+460.0, +1,160.9] | -65 | +221 | +175 | +188 | +139 | +198 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__supervised_mlp16` | median/diagonal | +2,909.0 | [+1,783.5, +4,875.8] | +1,382 | +283 | +262 | +155 | +292 | +535 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random__late` | matched/diagonal | +1,408.9 | [+640.4, +2,575.3] | +1,003 | +88 | +85 | +56 | +61 | +115 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random__late` | matched/correlation | +720.4 | [+396.1, +1,040.3] | +213 | +134 | +94 | +126 | +58 | +96 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random__late` | median/diagonal | +2,997.3 | [+1,609.3, +5,163.9] | +1,853 | +200 | +218 | +194 | +183 | +350 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,319.3 | [+1,392.7, +3,877.3] | +1,039 | +225 | +158 | +201 | +233 | +462 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,119.8 | [-4,515.6, +1,070.1] | -2,360 | +376 | +143 | +303 | +107 | +311 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,645.9 | [+707.3, +3,154.7] | +937 | +45 | -21 | +104 | +214 | +367 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | matched/diagonal | +2,658.8 | [+1,662.7, +4,333.7] | +1,088 | +235 | +281 | +260 | +220 | +574 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | matched/correlation | -953.3 | [-4,540.8, +1,379.9] | -2,493 | +404 | +259 | +358 | +109 | +410 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | median/diagonal | +2,400.0 | [+1,317.9, +4,145.2] | +1,179 | +77 | +140 | +224 | +193 | +588 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +2,294.5 | [+1,496.8, +3,617.5] | +859 | +263 | +290 | +251 | +211 | +419 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -1,035.9 | [-4,403.3, +1,178.5] | -2,389 | +400 | +256 | +314 | +107 | +276 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +1,605.8 | [+988.2, +2,552.6] | +571 | +167 | +161 | +176 | +181 | +350 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__tabfm__early_concat_labelnull` | matched/diagonal | +309.5 | [+90.3, +611.2] | +113 | +8 | +5 | +109 | +52 | +23 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__tabfm__early_concat_labelnull` | matched/correlation | -607.6 | [-1,813.9, +169.6] | -884 | +81 | +11 | +140 | +34 | +10 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__tabfm__early_concat_labelnull` | median/diagonal | +243.5 | [+29.9, +500.0] | +41 | +6 | +9 | +112 | +55 | +20 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +2,997.5 | [+2,141.0, +4,213.6] | +724 | +412 | +432 | +324 | +351 | +755 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -2,193.9 | [-8,294.1, +1,723.0] | -4,308 | +597 | +385 | +465 | +160 | +507 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,173.9 | [+1,466.2, +3,035.5] | +372 | +283 | +227 | +224 | +368 | +701 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__pca16` | matched/diagonal | +3,337.0 | [+2,381.3, +4,682.4] | +773 | +422 | +555 | +383 | +337 | +867 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__pca16` | matched/correlation | -2,027.4 | [-8,274.3, +2,036.0] | -4,441 | +625 | +502 | +520 | +162 | +606 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__pca16` | median/diagonal | +2,928.0 | [+2,091.4, +4,025.7] | +614 | +315 | +387 | +344 | +347 | +922 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +2,972.7 | [+2,169.4, +3,996.5] | +544 | +450 | +564 | +374 | +329 | +712 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -2,110.0 | [-8,177.4, +1,827.1] | -4,337 | +620 | +499 | +476 | +160 | +472 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +2,133.8 | [+1,441.8, +2,803.6] | +5 | +405 | +408 | +296 | +335 | +684 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random__late` | matched/diagonal | +1,659.8 | [+1,174.7, +2,146.1] | +119 | +350 | +337 | +200 | +164 | +489 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random__late` | matched/correlation | -1,261.7 | [-5,021.8, +1,182.2] | -2,674 | +423 | +308 | +282 | +73 | +327 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random__late` | median/diagonal | +1,408.6 | [+668.8, +2,049.9] | -321 | +425 | +324 | +220 | +221 | +540 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | matched/diagonal | -571.3 | [-1,175.0, -204.5] | -290 | -116 | -50 | -52 | +21 | -85 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | matched/correlation | +197.2 | [-284.7, +835.9] | +470 | -145 | -23 | -112 | +53 | -46 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | median/diagonal | -971.3 | [-1,819.8, -483.2] | -431 | -88 | -112 | -129 | -40 | -171 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | matched/diagonal | -887.0 | [-1,876.8, -325.0] | -592 | -120 | -34 | -44 | +11 | -108 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | matched/correlation | +246.0 | [-366.7, +1,088.3] | +568 | -174 | -11 | -130 | +50 | -57 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | median/diagonal | -1,335.2 | [-2,504.8, -686.9] | -703 | -99 | -140 | -146 | -52 | -196 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | matched/diagonal | +2,693.6 | [+1,703.5, +4,433.3] | +1,255 | +263 | +268 | +270 | +207 | +431 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | matched/correlation | +1,424.5 | [+936.9, +1,934.3] | +95 | +305 | +250 | +289 | +149 | +337 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | median/diagonal | +2,819.3 | [+1,589.4, +5,014.3] | +1,313 | +336 | +255 | +158 | +203 | +555 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__tabfm__early_concat_labelnull` | matched/diagonal | +639.8 | [+358.8, +1,066.9] | +350 | +38 | +50 | +43 | +60 | +99 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__tabfm__early_concat_labelnull` | matched/correlation | +22.9 | [-526.2, +366.8] | -305 | +77 | +53 | +70 | +54 | +73 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__tabfm__early_concat_labelnull` | median/diagonal | +181.1 | [+66.1, +299.2] | +79 | +53 | +17 | -27 | +10 | +49 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories__direct` | matched/diagonal | -1,545.5 | [-3,002.1, -727.6] | -866 | -185 | -140 | -168 | +15 | -203 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories__direct` | matched/correlation | -366.7 | [-916.7, +222.7] | +246 | -232 | -101 | -196 | +49 | -133 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories__direct` | median/diagonal | -1,073.7 | [-2,269.8, -375.3] | -574 | -130 | -96 | -153 | +59 | -180 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__pca16` | matched/diagonal | -1,861.2 | [-3,722.9, -827.4] | -1,168 | -189 | -124 | -160 | +5 | -226 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__pca16` | matched/correlation | -317.9 | [-976.1, +410.3] | +344 | -261 | -88 | -214 | +45 | -144 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__pca16` | median/diagonal | -1,437.6 | [-2,956.8, -581.6] | -846 | -141 | -123 | -170 | +47 | -205 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__supervised_mlp16` | matched/diagonal | +1,719.5 | [+1,204.5, +2,579.8] | +679 | +194 | +178 | +153 | +201 | +314 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__supervised_mlp16` | matched/correlation | +860.7 | [+444.3, +1,192.7] | -129 | +217 | +172 | +205 | +145 | +250 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__supervised_mlp16` | median/diagonal | +2,716.9 | [+1,658.5, +4,547.8] | +1,170 | +294 | +271 | +135 | +301 | +546 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random__late` | matched/diagonal | +1,743.2 | [+766.9, +3,240.8] | +1,255 | +61 | +107 | +30 | +96 | +193 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random__late` | matched/correlation | +756.6 | [+408.1, +1,068.9] | +163 | +121 | +114 | +123 | +88 | +148 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random__late` | median/diagonal | +3,222.8 | [+1,674.5, +5,661.6] | +2,043 | +174 | +234 | +141 | +237 | +394 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,654.9 | [+1,677.7, +4,296.5] | +1,058 | +286 | +263 | +227 | +277 | +544 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,474.1 | [-5,651.7, +1,226.0] | -2,967 | +428 | +240 | +335 | +132 | +358 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +2,066.1 | [+1,032.5, +3,769.7] | +1,016 | +121 | +80 | +129 | +258 | +462 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | matched/diagonal | +3,014.3 | [+1,951.2, +4,757.5] | +1,095 | +286 | +399 | +302 | +305 | +627 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | matched/correlation | -486.9 | [-3,480.4, +1,643.6] | -2,266 | +448 | +367 | +383 | +154 | +427 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | median/diagonal | +3,562.9 | [+2,088.3, +6,033.0] | +1,811 | +164 | +282 | +285 | +366 | +655 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +3,296.5 | [+2,111.5, +5,254.4] | +1,262 | +359 | +428 | +288 | +262 | +697 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -1,259.8 | [-5,738.6, +1,683.8] | -3,183 | +514 | +389 | +401 | +129 | +491 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +2,798.4 | [+1,747.5, +4,478.6] | +1,001 | +282 | +329 | +250 | +231 | +706 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__tabfm__early_concat_labelnull` | matched/diagonal | +377.5 | [+74.6, +677.9] | -63 | +118 | +80 | +84 | +66 | +91 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__tabfm__early_concat_labelnull` | matched/correlation | -954.6 | [-2,718.7, +223.5] | -1,388 | +158 | +86 | +115 | +27 | +47 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__tabfm__early_concat_labelnull` | median/diagonal | +250.7 | [-84.1, +544.7] | -159 | +118 | +58 | +73 | +72 | +88 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +3,100.7 | [+2,174.5, +4,505.2] | +889 | +380 | +391 | +300 | +362 | +779 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -2,038.4 | [-7,770.0, +1,676.6] | -4,093 | +577 | +335 | +453 | +166 | +523 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,417.3 | [+1,541.5, +3,651.1] | +702 | +223 | +179 | +177 | +394 | +742 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__pca16` | matched/diagonal | +3,460.1 | [+2,439.3, +4,989.1] | +926 | +380 | +527 | +374 | +391 | +862 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__pca16` | matched/correlation | -1,051.3 | [-5,571.8, +2,079.3] | -3,391 | +597 | +463 | +500 | +188 | +592 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__pca16` | median/diagonal | +3,914.2 | [+2,630.2, +5,917.6] | +1,497 | +266 | +381 | +333 | +502 | +935 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +3,742.3 | [+2,612.3, +5,468.9] | +1,093 | +454 | +557 | +360 | +347 | +932 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -1,824.2 | [-7,839.3, +2,131.1] | -4,308 | +663 | +484 | +519 | +162 | +656 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +3,149.7 | [+2,218.8, +4,412.3] | +687 | +384 | +428 | +298 | +367 | +986 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random__late` | matched/diagonal | +1,694.0 | [+1,143.4, +2,342.5] | +241 | +332 | +329 | +174 | +132 | +485 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random__late` | matched/correlation | -1,096.7 | [-4,373.3, +1,098.3] | -2,442 | +421 | +282 | +281 | +35 | +328 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random__late` | median/diagonal | +1,438.4 | [+889.3, +1,947.4] | -131 | +356 | +319 | +165 | +196 | +534 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | matched/diagonal | -236.8 | [-647.1, +40.6] | -116 | -66 | -10 | -42 | +23 | -27 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | matched/correlation | +441.3 | [-58.4, +1,131.0] | +558 | -97 | +14 | -88 | +51 | +4 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | median/diagonal | -950.6 | [-1,799.3, -470.5] | -431 | -86 | -93 | -123 | -65 | -154 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | matched/diagonal | -509.2 | [-1,285.4, -68.7] | -415 | -52 | -11 | -23 | +29 | -37 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | matched/correlation | +537.5 | [-53.8, +1,387.1] | +649 | -99 | +12 | -83 | +59 | -1 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | median/diagonal | -1,342.0 | [-2,603.8, -656.4] | -758 | -93 | -119 | -125 | -73 | -173 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | matched/diagonal | +3,006.6 | [+1,847.2, +5,071.1] | +1,377 | +314 | +297 | +289 | +223 | +506 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | matched/correlation | +1,366.2 | [+680.8, +1,987.3] | -166 | +363 | +275 | +333 | +163 | +397 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | median/diagonal | +2,449.4 | [+1,120.4, +4,711.5] | +1,043 | +297 | +140 | +176 | +223 | +571 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__tabfm__early_concat_labelnull` | matched/diagonal | +1,053.4 | [+495.8, +1,929.0] | +704 | +53 | +87 | +28 | +56 | +125 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__tabfm__early_concat_labelnull` | matched/correlation | +256.3 | [-133.9, +522.7] | -132 | +90 | +84 | +67 | +46 | +101 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__tabfm__early_concat_labelnull` | median/diagonal | +416.9 | [+78.7, +889.1] | +406 | +31 | +2 | -47 | -30 | +55 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories__direct` | matched/diagonal | -1,647.0 | [-3,315.0, -713.2] | -1,014 | -189 | -155 | -148 | +35 | -177 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories__direct` | matched/correlation | -458.9 | [-1,037.6, +100.1] | +126 | -239 | -112 | -186 | +62 | -111 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories__direct` | median/diagonal | -1,286.7 | [-2,798.0, -438.1] | -802 | -142 | -101 | -125 | +64 | -181 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__pca16` | matched/diagonal | -1,919.5 | [-4,003.4, -752.6] | -1,313 | -175 | -156 | -129 | +40 | -187 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__pca16` | matched/correlation | -362.7 | [-970.9, +273.0] | +217 | -240 | -114 | -180 | +71 | -116 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__pca16` | median/diagonal | -1,678.1 | [-3,598.7, -606.9] | -1,129 | -149 | -127 | -127 | +56 | -201 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__supervised_mlp16` | matched/diagonal | +1,596.4 | [+1,138.9, +2,341.8] | +479 | +191 | +152 | +183 | +234 | +357 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__supervised_mlp16` | matched/correlation | +466.0 | [-442.3, +1,121.3] | -597 | +222 | +149 | +236 | +175 | +282 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__supervised_mlp16` | median/diagonal | +2,113.3 | [+1,104.3, +3,698.1] | +672 | +240 | +132 | +174 | +352 | +544 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random__late` | matched/diagonal | +1,369.3 | [+725.4, +2,323.6] | +866 | +43 | +124 | +80 | +104 | +151 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random__late` | matched/correlation | +543.6 | [+68.3, +859.4] | -19 | +83 | +129 | +137 | +94 | +119 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random__late` | median/diagonal | +2,802.3 | [+1,613.0, +4,638.1] | +1,628 | +153 | +256 | +198 | +237 | +330 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,439.5 | [+1,573.0, +3,843.5] | +877 | +250 | +309 | +233 | +221 | +549 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,449.1 | [-5,592.4, +1,234.0] | -2,923 | +406 | +277 | +340 | +95 | +355 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,658.7 | [+879.9, +2,878.8] | +675 | +87 | +139 | +117 | +195 | +446 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | matched/diagonal | +2,689.8 | [+1,794.7, +4,026.7] | +787 | +292 | +425 | +326 | +231 | +629 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | matched/correlation | -1,096.6 | [-5,211.6, +1,633.6] | -2,898 | +465 | +393 | +411 | +118 | +414 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | median/diagonal | +2,614.6 | [+1,741.3, +3,830.7] | +1,010 | +187 | +341 | +276 | +186 | +614 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +2,710.6 | [+1,787.3, +4,056.0] | +705 | +263 | +445 | +463 | +235 | +599 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -1,382.2 | [-5,888.1, +1,599.5] | -3,263 | +437 | +399 | +508 | +114 | +422 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,185.3 | [+1,390.4, +3,047.4] | +184 | +180 | +368 | +470 | +237 | +746 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__tabfm__early_concat_labelnull` | matched/diagonal | +703.0 | [+305.1, +1,277.9] | +262 | +44 | +193 | +81 | +18 | +105 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__tabfm__early_concat_labelnull` | matched/correlation | -1,193.2 | [-3,446.0, +271.8] | -1,700 | +144 | +179 | +148 | -3 | +39 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__tabfm__early_concat_labelnull` | median/diagonal | +397.8 | [+89.9, +744.3] | +54 | +26 | +179 | +40 | +4 | +94 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +2,986.0 | [+2,137.2, +4,249.8] | +803 | +356 | +359 | +330 | +348 | +789 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -1,681.6 | [-6,920.0, +1,699.0] | -3,677 | +522 | +311 | +446 | +161 | +555 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,410.7 | [+1,532.5, +3,642.4] | +728 | +180 | +162 | +222 | +363 | +756 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__pca16` | matched/diagonal | +3,236.3 | [+2,341.4, +4,451.0] | +713 | +398 | +475 | +424 | +358 | +869 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__pca16` | matched/correlation | -1,329.1 | [-6,507.8, +2,092.1] | -3,652 | +581 | +427 | +518 | +184 | +614 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__pca16` | median/diagonal | +3,366.6 | [+2,405.1, +4,662.4] | +1,063 | +280 | +364 | +381 | +355 | +924 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +3,257.1 | [+2,349.3, +4,492.6] | +630 | +369 | +495 | +561 | +363 | +839 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -1,614.7 | [-7,204.4, +2,063.6] | -4,017 | +552 | +433 | +615 | +180 | +622 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,937.4 | [+2,046.5, +3,914.0] | +237 | +273 | +392 | +575 | +405 | +1,056 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random__late` | matched/diagonal | +1,288.2 | [+853.0, +1,703.8] | -35 | +236 | +260 | +231 | +141 | +455 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random__late` | matched/correlation | -562.2 | [-2,954.1, +1,040.2] | -1,740 | +281 | +229 | +256 | +59 | +353 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random__late` | median/diagonal | +1,226.5 | [+703.3, +1,704.0] | -223 | +246 | +265 | +253 | +184 | +502 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +106.5 | [-208.9, +322.9] | -81 | -6 | +67 | +19 | +48 | +60 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +778.7 | [+279.8, +1,523.6] | +616 | -26 | +75 | -18 | +65 | +67 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | -918.4 | [-1,755.2, -443.7] | -544 | -73 | -58 | -89 | -38 | -116 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | matched/diagonal | +85.2 | [-312.0, +343.5] | -158 | -4 | +77 | +49 | +53 | +68 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | matched/correlation | +747.4 | [+302.8, +1,426.9] | +539 | -25 | +84 | +2 | +71 | +77 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | median/diagonal | -1,135.3 | [-2,192.8, -535.2] | -713 | -77 | -78 | -92 | -46 | -130 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +3,426.7 | [+2,190.8, +5,593.2] | +1,543 | +359 | +367 | +345 | +236 | +577 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +1,821.8 | [+1,159.9, +2,497.9] | +68 | +417 | +328 | +393 | +169 | +447 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +2,348.1 | [+1,244.1, +4,205.4] | +875 | +260 | +144 | +207 | +283 | +579 |
| support 256 native | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/diagonal | +945.8 | [+661.9, +1,403.6] | +348 | +108 | +149 | +91 | +74 | +177 |
| support 256 native | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | matched/correlation | +488.4 | [+168.9, +744.9] | -93 | +137 | +130 | +121 | +58 | +135 |
| support 256 native | `histories__tabfm__early_concat` | `histories__tabfm__early_concat_labelnull` | median/diagonal | +137.1 | [+7.7, +268.5] | -14 | +37 | +39 | -12 | +20 | +67 |
| support 256 native | `histories__tabpfn_full__late` | `histories__direct` | matched/diagonal | -1,470.4 | [-2,965.0, -633.2] | -879 | -179 | -105 | -146 | +24 | -185 |
| support 256 native | `histories__tabpfn_full__late` | `histories__direct` | matched/correlation | -456.8 | [-1,023.0, +78.9] | +88 | -222 | -71 | -178 | +52 | -125 |
| support 256 native | `histories__tabpfn_full__late` | `histories__direct` | median/diagonal | -1,095.2 | [-2,413.5, -339.4] | -634 | -148 | -73 | -112 | +50 | -179 |
| support 256 native | `histories__tabpfn_full__late` | `histories__pca16` | matched/diagonal | -1,491.8 | [-3,076.3, -596.7] | -956 | -177 | -95 | -116 | +29 | -177 |
| support 256 native | `histories__tabpfn_full__late` | `histories__pca16` | matched/correlation | -488.1 | [-1,072.3, +43.6] | +10 | -222 | -62 | -157 | +59 | -116 |
| support 256 native | `histories__tabpfn_full__late` | `histories__pca16` | median/diagonal | -1,312.0 | [-2,831.0, -453.2] | -802 | -152 | -94 | -115 | +43 | -193 |
| support 256 native | `histories__tabpfn_full__late` | `histories__supervised_mlp16` | matched/diagonal | +1,849.8 | [+1,293.6, +2,783.9] | +746 | +186 | +195 | +180 | +211 | +332 |
| support 256 native | `histories__tabpfn_full__late` | `histories__supervised_mlp16` | matched/correlation | +586.3 | [-231.4, +1,151.5] | -461 | +220 | +182 | +233 | +157 | +255 |
| support 256 native | `histories__tabpfn_full__late` | `histories__supervised_mlp16` | median/diagonal | +2,171.4 | [+1,332.9, +3,548.2] | +786 | +185 | +129 | +184 | +371 | +516 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random__late` | matched/diagonal | +748.8 | [+484.4, +1,076.8] | +364 | +36 | +154 | +45 | +66 | +85 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random__late` | matched/correlation | +397.1 | [-70.3, +722.0] | -16 | +50 | +156 | +82 | +64 | +61 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random__late` | median/diagonal | +2,459.6 | [+1,487.3, +3,929.3] | +1,366 | +134 | +277 | +188 | +198 | +297 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,581.3 | [+1,708.1, +3,995.2] | +932 | +283 | +324 | +217 | +241 | +583 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,278.9 | [-5,289.8, +1,325.4] | -2,819 | +424 | +289 | +329 | +110 | +389 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,913.6 | [+1,082.3, +3,216.2] | +797 | +118 | +173 | +116 | +214 | +496 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | matched/diagonal | +3,113.8 | [+2,109.1, +4,739.3] | +1,128 | +311 | +430 | +310 | +259 | +676 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | matched/correlation | -1,233.7 | [-5,722.0, +1,653.4] | -3,086 | +474 | +393 | +392 | +132 | +460 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | median/diagonal | +3,258.1 | [+2,056.6, +5,148.2] | +1,396 | +249 | +341 | +331 | +229 | +712 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | matched/diagonal | +3,686.0 | [+2,217.2, +6,188.2] | +1,643 | +299 | +495 | +322 | +245 | +682 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | matched/correlation | -1,284.1 | [-5,824.7, +1,755.7] | -3,257 | +507 | +439 | +451 | +117 | +459 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | median/diagonal | +8,259.4 | [+3,723.2, +16,155.5] | +5,352 | +343 | +619 | +464 | +322 | +1,160 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__tabfm__early_concat_labelnull` | matched/diagonal | +667.2 | [+396.4, +1,069.0] | +223 | +50 | +156 | +59 | +39 | +140 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__tabfm__early_concat_labelnull` | matched/correlation | -946.7 | [-2,827.9, +268.9] | -1,400 | +110 | +141 | +112 | +15 | +75 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__tabfm__early_concat_labelnull` | median/diagonal | +702.4 | [+358.9, +1,242.5] | +301 | +35 | +167 | +31 | +29 | +140 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +3,035.1 | [+2,182.9, +4,366.9] | +942 | +314 | +431 | +325 | +323 | +700 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -1,617.8 | [-6,716.3, +1,645.0] | -3,554 | +488 | +370 | +445 | +153 | +480 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,518.6 | [+1,598.2, +3,922.0] | +928 | +113 | +259 | +228 | +332 | +659 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__pca16` | matched/diagonal | +3,567.6 | [+2,571.8, +5,120.4] | +1,137 | +342 | +536 | +418 | +341 | +793 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__pca16` | matched/correlation | -1,572.6 | [-7,157.2, +1,983.0] | -3,820 | +539 | +475 | +508 | +175 | +551 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__pca16` | median/diagonal | +3,863.2 | [+2,581.7, +5,839.8] | +1,527 | +244 | +427 | +442 | +347 | +875 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__supervised_mlp16` | matched/diagonal | +4,139.7 | [+2,704.1, +6,568.2] | +1,653 | +330 | +601 | +430 | +327 | +799 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__supervised_mlp16` | matched/correlation | -1,623.0 | [-7,272.6, +2,071.1] | -3,991 | +572 | +520 | +566 | +160 | +550 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__supervised_mlp16` | median/diagonal | +8,864.5 | [+4,250.0, +16,875.4] | +5,483 | +338 | +705 | +576 | +440 | +1,323 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random__late` | matched/diagonal | +1,471.3 | [+1,127.3, +1,860.8] | +200 | +206 | +377 | +227 | +116 | +345 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random__late` | matched/correlation | -448.7 | [-2,757.2, +1,052.5] | -1,582 | +253 | +331 | +273 | +52 | +224 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random__late` | median/diagonal | +1,447.7 | [+1,079.5, +1,804.8] | +50 | +182 | +414 | +256 | +154 | +392 |

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
| `uniform_network` | 0.707 | -782 | +2,145,743 | -549,849 | +42,398 | -815 | -13,101 | +1,623,593 | 0.0023 |
| `fernandez_joint` | 0.776 | -360 | +3,791 | -6,242 | +10,899 | -268 | -3,053 | +4,767 | 0.0026 |
| `covariance_exposures` | 0.710 | -12 | +154 | -254 | +426 | -5 | -145 | +164 | 0.0023 |
| `reference_exposures` | 0.710 | -11 | +131 | -224 | +381 | -6 | -127 | +145 | 0.0023 |
| `histories__direct` | 0.793 | -428 | +3,116 | -7,402 | +13,559 | -281 | -4,269 | +4,294 | 0.0026 |
| `histories__supervised_mlp16` | 0.752 | -343 | +1,689 | -4,521 | +8,617 | -403 | -2,885 | +2,154 | 0.0031 |
| `histories__tabfm__early_concat` | 0.757 | -217 | +1,978 | -4,440 | +8,343 | -144 | -2,779 | +2,740 | 0.0024 |
| `histories__tabfm__early_concat_labelnull` | 0.724 | -67 | +577 | -1,186 | +2,321 | -43 | -797 | +806 | 0.0024 |
| `histories__tabpfn_full__late` | 0.764 | -265 | +2,055 | -4,100 | +9,043 | -221 | -3,437 | +3,075 | 0.0025 |
| `histories@decoded__direct` | 0.707 | -1 | +9 | -17 | +28 | -0 | -8 | +11 | 0.0023 |
| `histories@decoded__tabfm__early_concat` | 0.708 | -3 | +27 | -52 | +94 | -1 | -29 | +36 | 0.0023 |

### matched kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.707 | -782 | +2,145,743 | -549,849 | +42,398 | -815 | -13,101 | +1,623,593 | 0.0023 |
| `fernandez_joint` | 0.776 | -360 | +3,791 | -6,242 | +10,899 | -268 | -3,053 | +4,767 | 0.0026 |
| `covariance_exposures` | 0.894 | -1,292 | +15,864 | -32,733 | +48,811 | -527 | -13,823 | +16,299 | 0.0026 |
| `reference_exposures` | 0.902 | -1,407 | +16,149 | -34,411 | +52,576 | -583 | -15,410 | +16,913 | 0.0026 |
| `histories__direct` | 0.804 | -514 | +3,669 | -8,500 | +15,628 | -341 | -4,977 | +4,965 | 0.0026 |
| `histories__supervised_mlp16` | 0.746 | -207 | +1,185 | -2,958 | +5,983 | -214 | -2,225 | +1,564 | 0.0026 |
| `histories__tabfm__early_concat` | 0.796 | -462 | +4,323 | -9,230 | +16,800 | -324 | -5,415 | +5,692 | 0.0026 |
| `histories__tabfm__early_concat_labelnull` | 0.781 | -374 | +3,432 | -7,111 | +13,022 | -281 | -4,131 | +4,557 | 0.0026 |
| `histories__tabpfn_full__late` | 0.772 | -329 | +2,930 | -5,446 | +11,435 | -295 | -4,104 | +4,190 | 0.0026 |
| `histories@decoded__direct` | 0.795 | -444 | +3,602 | -8,002 | +12,933 | -290 | -3,222 | +4,577 | 0.0027 |
| `histories@decoded__tabfm__early_concat` | 0.837 | -741 | +6,369 | -14,563 | +24,411 | -409 | -6,851 | +8,216 | 0.0026 |

The uniform row shows its own parts; every other row is its difference from it.

## Measurement variants

Held-out gains over the joint network (exp kernel) for the history rung: the native
readout, two re-encodings on differently salted 256-row supports, the two support
targets on shared rows and their combination (RMS of the two distances), and
networks built from reference-factor exposures decoded out of the same states
(see `decoding.py`).

### exp kernel, diagonal innovations

| Representation | native | redraw 1 | redraw 2 | shared cap/assets | shared income/assets | both shared | decoded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct` | +1,217.0 | — | — | — | — | — | -4,576.9 |
| `tabfm__early_concat` | -1,035.2 | — | — | — | — | — | -4,552.5 |
| `tabpfn_full__late` | -225.8 | — | — | — | — | — | -4,544.7 |
| `exaone__late` | — | — | — | — | — | — | — |
| `supervised_mlp16` | -51.7 | — | — | — | — | — | -4,578.5 |

### matched kernel, diagonal innovations

| Representation | native | redraw 1 | redraw 2 | shared cap/assets | shared income/assets | both shared | decoded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct` | +2,187.1 | — | — | — | — | — | +295.9 |
| `tabfm__early_concat` | +2,293.6 | — | — | — | — | — | +2,877.2 |
| `tabpfn_full__late` | +716.7 | — | — | — | — | — | +3,331.0 |
| `exaone__late` | — | — | — | — | — | — | — |
| `supervised_mlp16` | -1,133.1 | — | — | — | — | — | -808.8 |

Decoders: out-of-fold R^2 of the rank-5 reference exposures (mean over
years, median in brackets), and the Spearman correlation between decoded and
target distances. The target's reliability bounds R^2 near 0.90
and distance Spearman near 0.77; see Calibration targets.

| Representation | Out-of-fold R^2 | Distance Spearman |
| --- | ---: | ---: |
| `direct` | 0.092 [0.086] | 0.220 |
| `pca16` | 0.059 [0.071] | 0.175 |
| `supervised_mlp16` | 0.059 [0.059] | 0.160 |
| `tabpfn_full__late` | 0.282 [0.307] | 0.371 |
| `tabpfn_full_random__late` | 0.189 [0.218] | 0.276 |
| `tabfm__early_concat` | 0.224 [0.245] | 0.349 |
| `tabfm__early_concat_labelnull` | 0.175 [0.192] | 0.319 |

## Calibration targets

`reference` is each cohort firm's OLS loadings on the leading principal components
of standardized prior factor residuals of firms outside the cohort
(383-484 a year); a held-out firm's returns never reach another
firm's target. `covariance` is the earlier in-panel construction, the rank-k
coordinates of the cohort's own residual covariance, kept as a control. Means over
years. Halves split the prior window; the reference halves share the full-window
factor series, so the Spearman-Brown value estimates the reliability of the
full-window target and bounds any decoder's R^2 against it. In-panel coordinates
rotate between halves, so only their distances are compared. Commonality is the
share of each firm's residual variance the target explains; the effective firm
fraction is (1 / sum p_i^2) / N for p_i a firm's share of the target's squared
mass, low when a few firms hold it, as for a diagonal covariance.

| Target | Rank | Half-window correlation | Spearman-Brown | Distance reliability | Commonality | Effective firm fraction |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reference | 3 | 0.844 | 0.915 | 0.762 | 0.126 | 0.362 |
| covariance | 3 | — | — | 0.670 | 0.136 | 0.120 |
| reference | 5 | 0.820 | 0.901 | 0.774 | 0.158 | 0.390 |
| covariance | 5 | — | — | 0.701 | 0.178 | 0.118 |
| reference | 8 | 0.794 | 0.884 | 0.793 | 0.193 | 0.432 |
| covariance | 8 | — | — | 0.715 | 0.223 | 0.133 |

Mean out-of-fold decoder R^2 against the reference target at each rank (history
rung); networks use rank 5 only.

| Representation | Rank 3 | Rank 5 | Rank 8 |
| --- | ---: | ---: | ---: |
| `direct` | 0.105 | 0.092 | 0.080 |
| `pca16` | 0.063 | 0.059 | 0.052 |
| `supervised_mlp16` | 0.075 | 0.059 | 0.053 |
| `tabpfn_full__late` | 0.313 | 0.282 | 0.254 |
| `tabpfn_full_random__late` | 0.216 | 0.189 | 0.165 |
| `tabfm__early_concat` | 0.252 | 0.224 | 0.201 |
| `tabfm__early_concat_labelnull` | 0.195 | 0.175 | 0.158 |

## Support size

Every row re-encodes the same query firms on a nested prefix of the 256-row support.
Query-only rows (`direct`) do not depend on the support and appear once. Gains are
over the joint network (exp kernel), matched kernel with diagonal innovations, the
arm declared before this design ran.

### Native distance

| Representation | 32 rows | 64 rows | 128 rows | 256 rows |
| --- | ---: | ---: | ---: | ---: |
| `direct` | +2,187.1 | +2,187.1 | +2,187.1 | +2,187.1 |
| `pca16` | +2,455.6 | +2,502.8 | +2,459.5 | +2,208.5 |
| `supervised_mlp16` | -1,314.5 | -1,077.9 | -1,056.3 | -1,133.1 |
| `tabfm__early_concat` | +1,506.6 | +1,615.8 | +1,950.3 | +2,293.6 |
| `tabfm__early_concat_labelnull` | +548.7 | +976.0 | +897.0 | +1,347.8 |
| `tabpfn_full__late` | +363.1 | +641.6 | +540.1 | +716.7 |
| `tabpfn_full_random__late` | -1,045.8 | -1,101.6 | -829.2 | -32.1 |

### Decoded distance

| Representation | 32 rows | 64 rows | 128 rows | 256 rows |
| --- | ---: | ---: | ---: | ---: |
| `direct` | +295.9 | +295.9 | +295.9 | +295.9 |
| `pca16` | -43.6 | -63.5 | +45.6 | -236.6 |
| `supervised_mlp16` | +320.7 | -345.7 | +24.8 | -808.8 |
| `tabfm__early_concat` | +2,615.2 | +2,950.8 | +2,735.4 | +2,877.2 |
| `tabfm__early_concat_labelnull` | +2,305.7 | +2,573.3 | +2,032.4 | +2,210.0 |
| `tabpfn_full__late` | +3,293.4 | +3,396.6 | +3,281.8 | +3,331.0 |
| `tabpfn_full_random__late` | +1,633.6 | +1,702.6 | +1,993.7 | +1,859.7 |

### Decoder quality

Mean out-of-fold R^2 (median in brackets) against the rank-5 reference
target. The target's own reliability bounds R^2 near 0.90 and distance
Spearman near 0.77.

| Representation | 32 rows | 64 rows | 128 rows | 256 rows |
| --- | ---: | ---: | ---: | ---: |
| `direct` | 0.092 [0.086] | 0.092 [0.086] | 0.092 [0.086] | 0.092 [0.086] |
| `pca16` | 0.070 [0.079] | 0.062 [0.053] | 0.055 [0.048] | 0.059 [0.071] |
| `supervised_mlp16` | 0.076 [0.071] | 0.054 [0.056] | 0.065 [0.070] | 0.059 [0.059] |
| `tabfm__early_concat` | 0.204 [0.218] | 0.218 [0.231] | 0.225 [0.250] | 0.224 [0.245] |
| `tabfm__early_concat_labelnull` | 0.185 [0.198] | 0.181 [0.194] | 0.174 [0.177] | 0.175 [0.192] |
| `tabpfn_full__late` | 0.280 [0.304] | 0.283 [0.302] | 0.285 [0.297] | 0.282 [0.307] |
| `tabpfn_full_random__late` | 0.168 [0.165] | 0.179 [0.186] | 0.189 [0.196] | 0.189 [0.218] |

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical/exp | 69 | `fernandez_market_cap_assets`, `histories__pca16`, `histories@support32__pca16`, `histories@support64__pca16`, `histories@support128__pca16`, `h3__histories__pca16` |
| diagonal/exp | 72 | `fernandez_market_cap_assets`, `fernandez_dividend_yield`, `fernandez_joint`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__tabpfn_full__late`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__tabpfn_full__late`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__tabpfn_full__late`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__tabpfn_full__late`, `h3__fernandez_market_cap_assets`, `h3__fernandez_market_to_book`, `h3__fernandez_joint`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_full__late` |
| correlation/exp | 72 | `fernandez_market_cap_assets`, `fernandez_joint`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__supervised_mlp16` |
| spherical/median | 69 | `covariance_exposures` |
| diagonal/median | 72 | `covariance_exposures` |
| correlation/median | 72 | `covariance_exposures`, `reference_exposures`, `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories@decoded__direct`, `histories@decoded__pca16`, `histories@decoded__supervised_mlp16`, `histories@decoded__tabpfn_full__late`, `histories@decoded__tabpfn_full_random__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__early_concat_labelnull`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__tabpfn_full__late`, `histories__tabpfn_full_random__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_concat_labelnull`, `histories@support32@decoded__pca16`, `histories@support32@decoded__supervised_mlp16`, `histories@support32@decoded__tabpfn_full__late`, `histories@support32@decoded__tabpfn_full_random__late`, `histories@support32@decoded__tabfm__early_concat`, `histories@support32@decoded__tabfm__early_concat_labelnull`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__tabpfn_full__late`, `histories@support32__tabpfn_full_random__late`, `histories@support32__tabfm__early_concat`, `histories@support32__tabfm__early_concat_labelnull`, `histories@support64@decoded__pca16`, `histories@support64@decoded__supervised_mlp16`, `histories@support64@decoded__tabpfn_full__late`, `histories@support64@decoded__tabpfn_full_random__late`, `histories@support64@decoded__tabfm__early_concat`, `histories@support64@decoded__tabfm__early_concat_labelnull`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__tabpfn_full__late`, `histories@support64__tabpfn_full_random__late`, `histories@support64__tabfm__early_concat`, `histories@support64__tabfm__early_concat_labelnull`, `histories@support128@decoded__pca16`, `histories@support128@decoded__supervised_mlp16`, `histories@support128@decoded__tabpfn_full__late`, `histories@support128@decoded__tabpfn_full_random__late`, `histories@support128@decoded__tabfm__early_concat`, `histories@support128@decoded__tabfm__early_concat_labelnull`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__tabpfn_full__late`, `histories@support128__tabpfn_full_random__late`, `histories@support128__tabfm__early_concat`, `histories@support128__tabfm__early_concat_labelnull`, `h3__fernandez_market_cap_assets`, `h3__fernandez_market_to_book`, `h3__fernandez_dividend_yield`, `h3__fernandez_joint`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_full__late`, `h3__histories__tabpfn_full_random__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_concat_labelnull`, `uniform_network` |
| spherical/matched | 69 | `reference_exposures` |
| diagonal/matched | 72 | `covariance_exposures`, `reference_exposures` |
| correlation/matched | 72 | `covariance_exposures`, `reference_exposures`, `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories@decoded__direct`, `histories@decoded__pca16`, `histories@decoded__supervised_mlp16`, `histories@decoded__tabpfn_full__late`, `histories@decoded__tabpfn_full_random__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__early_concat_labelnull`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__tabpfn_full__late`, `histories__tabpfn_full_random__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_concat_labelnull`, `histories@support32@decoded__pca16`, `histories@support32@decoded__supervised_mlp16`, `histories@support32@decoded__tabpfn_full__late`, `histories@support32@decoded__tabpfn_full_random__late`, `histories@support32@decoded__tabfm__early_concat`, `histories@support32@decoded__tabfm__early_concat_labelnull`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__tabpfn_full__late`, `histories@support32__tabpfn_full_random__late`, `histories@support32__tabfm__early_concat`, `histories@support32__tabfm__early_concat_labelnull`, `histories@support64@decoded__supervised_mlp16`, `histories@support64@decoded__tabpfn_full__late`, `histories@support64@decoded__tabpfn_full_random__late`, `histories@support64@decoded__tabfm__early_concat`, `histories@support64@decoded__tabfm__early_concat_labelnull`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__tabpfn_full__late`, `histories@support64__tabpfn_full_random__late`, `histories@support64__tabfm__early_concat`, `histories@support64__tabfm__early_concat_labelnull`, `histories@support128@decoded__pca16`, `histories@support128@decoded__supervised_mlp16`, `histories@support128@decoded__tabpfn_full__late`, `histories@support128@decoded__tabpfn_full_random__late`, `histories@support128@decoded__tabfm__early_concat`, `histories@support128@decoded__tabfm__early_concat_labelnull`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__tabpfn_full__late`, `histories@support128__tabpfn_full_random__late`, `histories@support128__tabfm__early_concat`, `histories@support128__tabfm__early_concat_labelnull`, `h3__fernandez_joint`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_full__late`, `h3__histories__tabpfn_full_random__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_concat_labelnull` |

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
`Matched miss` is the largest achieved miss, in neighbours, over all years. Matching
the mean of 1/H_i does not match the mean row Herfindahl H, which the last two
columns compare (held-out years), nor spectral structure.

| Approach | exp | median | matched | Matched miss | Matched H | Joint exp H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `covariance_exposures` | 1.000 | 0.841 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `fernandez_dividend_yield` | 0.795 | 0.885 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `fernandez_joint` | 0.898 | 0.942 | 0.898 | 9.5e-11 | 0.0026 | 0.0026 |
| `fernandez_market_cap_assets` | 0.801 | 0.885 | 0.898 | 1.9e-12 | 0.0026 | 0.0026 |
| `fernandez_market_to_book` | 0.804 | 0.883 | 0.898 | 1.9e-10 | 0.0026 | 0.0026 |
| `h3__fernandez_dividend_yield` | 0.640 | 0.655 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `h3__fernandez_joint` | 0.785 | 0.875 | 0.898 | 1.6e-10 | 0.0026 | 0.0026 |
| `h3__fernandez_market_cap_assets` | 0.636 | 0.636 | 0.898 | 1.7e-09 | 0.0026 | 0.0026 |
| `h3__fernandez_market_to_book` | 0.638 | 0.654 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `h3__histories__direct` | 0.918 | 0.831 | 0.898 | 6.5e-10 | 0.0026 | 0.0026 |
| `h3__histories__pca16` | 0.891 | 0.838 | 0.898 | 2.4e-10 | 0.0026 | 0.0026 |
| `h3__histories__supervised_mlp16` | 0.817 | 0.614 | 0.898 | 3.8e-10 | 0.0026 | 0.0026 |
| `h3__histories__tabfm__early_concat` | 0.971 | 0.906 | 0.898 | 4.1e-10 | 0.0026 | 0.0026 |
| `h3__histories__tabfm__early_concat_labelnull` | 0.995 | 0.864 | 0.898 | 9.2e-10 | 0.0026 | 0.0026 |
| `h3__histories__tabpfn_full__late` | 0.939 | 0.836 | 0.898 | 5.8e-11 | 0.0026 | 0.0026 |
| `h3__histories__tabpfn_full_random__late` | 0.999 | 0.920 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories@decoded__direct` | 1.000 | 0.803 | 0.898 | 1.1e-09 | 0.0027 | 0.0026 |
| `histories@decoded__pca16` | 1.000 | 0.790 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@decoded__supervised_mlp16` | 1.000 | 0.784 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabfm__early_concat` | 1.000 | 0.859 | 0.898 | 4.4e-10 | 0.0026 | 0.0026 |
| `histories@decoded__tabfm__early_concat_labelnull` | 1.000 | 0.852 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full__late` | 1.000 | 0.860 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.2e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__pca16` | 1.000 | 0.788 | 0.898 | 1.3e-09 | 0.0027 | 0.0026 |
| `histories@support128@decoded__supervised_mlp16` | 1.000 | 0.795 | 0.898 | 1.2e-09 | 0.0027 | 0.0026 |
| `histories@support128@decoded__tabfm__early_concat` | 1.000 | 0.862 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabfm__early_concat_labelnull` | 1.000 | 0.854 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full__late` | 1.000 | 0.861 | 0.898 | 1.8e-09 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.3e-10 | 0.0026 | 0.0026 |
| `histories@support128__pca16` | 0.909 | 0.855 | 0.898 | 7.3e-12 | 0.0026 | 0.0026 |
| `histories@support128__supervised_mlp16` | 0.788 | 0.644 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support128__tabfm__early_concat` | 0.973 | 0.893 | 0.898 | 4.4e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabfm__early_concat_labelnull` | 0.995 | 0.869 | 0.898 | 4.3e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full__late` | 0.942 | 0.840 | 0.898 | 9.9e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full_random__late` | 0.999 | 0.909 | 0.898 | 2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__pca16` | 1.000 | 0.791 | 0.898 | 3.3e-10 | 0.0027 | 0.0026 |
| `histories@support32@decoded__supervised_mlp16` | 1.000 | 0.799 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabfm__early_concat` | 1.000 | 0.859 | 0.898 | 5.7e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabfm__early_concat_labelnull` | 1.000 | 0.856 | 0.898 | 7.5e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full__late` | 1.000 | 0.859 | 0.898 | 2.1e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full_random__late` | 1.000 | 0.861 | 0.898 | 9.9e-10 | 0.0026 | 0.0026 |
| `histories@support32__pca16` | 0.909 | 0.866 | 0.898 | 1.9e-09 | 0.0026 | 0.0026 |
| `histories@support32__supervised_mlp16` | 0.764 | 0.660 | 0.898 | 4.2e-10 | 0.0026 | 0.0026 |
| `histories@support32__tabfm__early_concat` | 0.982 | 0.879 | 0.898 | 2.3e-10 | 0.0026 | 0.0026 |
| `histories@support32__tabfm__early_concat_labelnull` | 0.994 | 0.857 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full__late` | 0.927 | 0.817 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full_random__late` | 0.999 | 0.904 | 0.898 | 5.4e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__pca16` | 1.000 | 0.789 | 0.898 | 6e-10 | 0.0028 | 0.0026 |
| `histories@support64@decoded__supervised_mlp16` | 1.000 | 0.791 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabfm__early_concat` | 1.000 | 0.860 | 0.898 | 7.3e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabfm__early_concat_labelnull` | 1.000 | 0.853 | 0.898 | 3.4e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full__late` | 1.000 | 0.861 | 0.898 | 2e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@support64__pca16` | 0.911 | 0.858 | 0.898 | 2.1e-09 | 0.0026 | 0.0026 |
| `histories@support64__supervised_mlp16` | 0.786 | 0.662 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support64__tabfm__early_concat` | 0.979 | 0.882 | 0.898 | 8.3e-11 | 0.0026 | 0.0026 |
| `histories@support64__tabfm__early_concat_labelnull` | 0.995 | 0.865 | 0.898 | 4.7e-10 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full__late` | 0.934 | 0.833 | 0.898 | 2.3e-11 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full_random__late` | 0.999 | 0.906 | 0.898 | 1.7e-09 | 0.0026 | 0.0026 |
| `histories__direct` | 0.925 | 0.864 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories__pca16` | 0.913 | 0.853 | 0.898 | 3.3e-10 | 0.0026 | 0.0026 |
| `histories__supervised_mlp16` | 0.784 | 0.655 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories__tabfm__early_concat` | 0.972 | 0.905 | 0.898 | 6.5e-12 | 0.0026 | 0.0026 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.874 | 0.898 | 3.5e-10 | 0.0026 | 0.0026 |
| `histories__tabpfn_full__late` | 0.938 | 0.841 | 0.898 | 4e-11 | 0.0026 | 0.0026 |
| `histories__tabpfn_full_random__late` | 0.999 | 0.914 | 0.898 | 3.4e-10 | 0.0026 | 0.0026 |
| `reference_exposures` | 1.000 | 0.860 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `uniform_network` | nan | nan | nan | nan | nan | 0.0026 |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
