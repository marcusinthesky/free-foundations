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
| 2023 | 429 | 756 | 249 |
| 2024 | 437 | 753 | 251 |
| 2025 | 459 | 753 | 249 |

## Held-out gains over the joint Fernández network

| Approach | Arm | exp/spherical | exp/diagonal | median/diagonal | matched/diagonal | exp/correlation |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | fernandez | +217.36 | -2,986.94 | -2,856.90 | -2,886.37 | -11,967.16 |
| `fernandez_market_to_book` | fernandez | -762.00 | -3,856.05 | -3,604.00 | -3,565.53 | +11,686.64 |
| `fernandez_dividend_yield` | fernandez | -932.90 | -129.97 | -524.74 | -546.22 | +24,164.25 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -1,036.82 | +0.00 | +0.00 |
| `histories__direct` | classical | +906.55 | +5,170.44 | +8,384.45 | +7,016.45 | +78.43 |
| `histories__mahalanobis_lw` | classical | -4,860.01 | +6,021.66 | +11,159.06 | +10,455.51 | +68,259.50 |
| `histories__pca16` | control | +1,283.58 | +5,125.62 | +9,054.85 | +6,859.29 | -9,724.27 |
| `histories__autoencoder` | control | +979.31 | -1,352.95 | +247.04 | -1,084.51 | -21,393.15 |
| `histories__random_autoencoder` | control | -614.45 | +3,644.36 | +11,665.20 | +9,128.32 | +25,935.40 |
| `histories__supervised_mlp16` | task | +247.17 | -5,469.23 | -7,047.09 | -4,794.02 | +3,496.02 |
| `histories__tabpfn_fast__late` | task | -1,173.09 | -2,754.54 | -1,049.14 | -1,832.29 | +25,222.23 |
| `histories__tabpfn_full__late` | task | -398.06 | -3,114.11 | -2,192.19 | -2,757.15 | +5,866.68 |
| `histories__tabfm__early_concat` | state | -630.20 | +3,566.10 | +8,733.11 | +9,584.94 | +34,767.84 |
| `histories__tabfm__early_mean` | state | -622.36 | +3,583.71 | +8,745.60 | +9,591.02 | +34,690.53 |
| `histories__tabfm__late` | task | -1,946.15 | -1,907.33 | +5,795.31 | +3,425.12 | +45,077.18 |
| `histories__tabfm__early_concat_labelnull` | state | -2,098.67 | -1,582.80 | +8,949.19 | +7,594.79 | +47,221.84 |
| `histories__exaone__late` | task | -926.85 | -2,265.13 | +2,800.22 | -1,016.12 | +29,706.30 |
| `histories__exaone__item_first_concat` | state | -2,820.55 | -3,072.22 | +8,667.80 | +7,735.18 | +53,704.63 |
| `histories__exaone__item_first_mean` | state | -2,818.27 | -3,047.21 | +8,972.81 | +7,935.65 | +53,719.41 |
| `histories__exaone__item_last_concat` | task | -1,353.98 | -832.55 | +5,850.74 | +4,493.37 | +33,154.87 |
| `broad__direct` | classical | -778.64 | -705.73 | -1,401.82 | +4,674.55 | +22,547.34 |
| `broad__mahalanobis_lw` | classical | -263.17 | +11,770.57 | +1,744.73 | +11,103.36 | +76,893.60 |
| `broad__pca16` | control | +2,987.13 | +4,768.58 | +2,779.54 | +6,276.23 | -73,583.53 |
| `broad__autoencoder` | control | +3,606.48 | +4,040.31 | +2,309.84 | +4,973.83 | -104,358.06 |
| `broad__random_autoencoder` | control | -1,770.05 | -1,988.67 | -2,147.46 | -1,671.25 | +36,933.48 |
| `broad__supervised_mlp16` | task | +55.86 | +3,694.89 | +2,856.87 | +2,781.73 | +41,556.94 |
| `broad__tabpfn_fast__late` | task | -1,037.08 | -2,544.17 | -238.31 | -1,184.54 | +22,890.70 |
| `broad__tabpfn_full__late` | task | -264.12 | -1,495.39 | +926.86 | -355.58 | +6,991.81 |
| `broad__tabfm__early_concat` | state | -709.52 | +1,751.17 | +5,490.04 | +7,129.04 | +32,243.98 |
| `broad__tabfm__early_mean` | state | -669.36 | +1,741.44 | +5,506.33 | +7,000.64 | +31,348.04 |
| `broad__tabfm__late` | task | -1,981.47 | -2,217.11 | +3,847.44 | +2,506.77 | +45,583.34 |
| `broad__tabfm__early_concat_labelnull` | state | -2,305.15 | -440.63 | +9,224.04 | +10,876.12 | +51,700.42 |
| `broad__exaone__late` | task | -884.20 | -4,072.12 | -4,220.17 | -4,610.84 | +24,616.49 |
| `broad__exaone__item_first_concat` | state | -2,820.76 | -3,100.03 | -3,071.03 | -2,707.55 | +53,665.62 |
| `broad__exaone__item_first_mean` | state | -2,818.77 | -3,099.78 | -3,630.90 | -2,977.32 | +53,645.30 |
| `broad__exaone__item_last_concat` | task | -1,283.66 | -3,129.30 | -1,763.40 | -2,097.87 | +27,822.31 |
| `metrics__direct` | classical | +216.69 | -549.14 | -1,344.41 | +4,820.57 | -2,238.40 |
| `metrics__mahalanobis_lw` | classical | +3,384.26 | +14,996.12 | +12,608.65 | +16,990.11 | +82,848.32 |
| `metrics__pca16` | control | +3,616.79 | +4,145.85 | +2,484.90 | +5,136.09 | -105,911.21 |
| `metrics__autoencoder` | control | +3,725.74 | +1,379.73 | +415.97 | +2,048.24 | -128,934.28 |
| `metrics__random_autoencoder` | control | -734.91 | +7,626.66 | +6,733.68 | +12,669.51 | +48,505.89 |
| `metrics__supervised_mlp16` | task | +1,267.49 | +4,735.49 | +4,581.03 | +4,323.16 | +44,871.36 |
| `metrics__tabpfn_fast__late` | task | -944.98 | -2,086.74 | +982.61 | -165.43 | +21,401.91 |
| `metrics__tabpfn_full__late` | task | -86.38 | +2,556.87 | +7,287.86 | +5,155.77 | +16,949.25 |
| `metrics__tabfm__early_concat` | state | -680.27 | +2,563.82 | +8,129.89 | +11,459.00 | +33,609.19 |
| `metrics__tabfm__early_mean` | state | -661.07 | +2,668.01 | +8,382.02 | +11,512.85 | +33,888.49 |
| `metrics__tabfm__late` | task | -1,904.33 | -1,214.93 | +8,638.96 | +6,711.40 | +46,375.44 |
| `metrics__tabfm__early_concat_labelnull` | state | -2,412.83 | -249.42 | +13,148.45 | +14,333.41 | +52,544.20 |
| `metrics__exaone__late` | task | -743.12 | -1,747.84 | +5,179.23 | -7.39 | +27,775.02 |
| `metrics__exaone__item_first_concat` | state | -2,820.99 | -3,087.39 | +9,475.11 | +8,793.97 | +53,677.98 |
| `metrics__exaone__item_first_mean` | state | -2,819.20 | -3,074.73 | +8,825.65 | +8,678.61 | +53,670.87 |
| `metrics__exaone__item_last_concat` | task | -1,041.76 | -537.02 | +6,635.03 | +5,272.14 | +28,937.53 |
| `histories@income_assets__direct` | classical | +519.69 | +4,212.67 | +8,479.92 | +6,929.21 | +7,738.05 |
| `histories@income_assets__mahalanobis_lw` | classical | -4,851.13 | +6,063.17 | +10,837.60 | +10,591.65 | +66,929.35 |
| `histories@income_assets__pca16` | control | +897.91 | +4,334.53 | +8,694.51 | +6,858.29 | -779.80 |
| `histories@income_assets__autoencoder` | control | +522.25 | -2,907.43 | -1,551.79 | -2,572.16 | -10,060.38 |
| `histories@income_assets__random_autoencoder` | control | -722.21 | +3,770.63 | +11,881.87 | +9,522.58 | +29,839.28 |
| `histories@income_assets__supervised_mlp16` | task | +1,000.84 | +371.58 | +562.99 | -783.25 | -3,701.76 |
| `histories@income_assets__tabpfn_fast__late` | task | -1,520.17 | -1,087.20 | +6,370.90 | +5,067.85 | +36,981.11 |
| `histories@income_assets__tabpfn_full__late` | task | -794.83 | -1,794.68 | +1,165.45 | +97.91 | +22,267.89 |
| `histories@income_assets__tabfm__early_concat` | state | -122.98 | +5,608.54 | +9,493.22 | +10,795.67 | +33,004.05 |
| `histories@income_assets__tabfm__early_mean` | state | -113.88 | +5,635.83 | +9,495.72 | +10,792.75 | +32,920.49 |
| `histories@income_assets__tabfm__late` | task | -2,042.74 | +269.20 | +12,268.45 | +13,062.97 | +49,842.93 |
| `histories@income_assets__tabfm__early_concat_labelnull` | state | -1,919.84 | -1,330.09 | +7,668.60 | +6,750.17 | +45,217.22 |
| `histories@income_assets__exaone__late` | task | -1,307.58 | +8,096.15 | +19,720.72 | +17,532.61 | +61,422.98 |
| `histories@income_assets__exaone__item_first_concat` | state | -2,819.84 | -3,071.58 | +7,898.59 | +6,847.29 | +53,696.57 |
| `histories@income_assets__exaone__item_first_mean` | state | -2,816.95 | -3,045.94 | +8,187.04 | +7,028.84 | +53,704.61 |
| `histories@income_assets__exaone__item_last_concat` | task | -1,858.62 | +1,887.06 | +13,898.10 | +15,570.79 | +48,321.99 |
| `h3__fernandez_market_cap_assets` | fernandez | -2,022.57 | -7,997.81 | -7,997.81 | -4,793.87 | +41,061.93 |
| `h3__fernandez_market_to_book` | fernandez | -2,177.48 | -8,243.57 | -8,191.42 | -5,086.72 | +43,771.64 |
| `h3__fernandez_dividend_yield` | fernandez | -2,237.96 | -1,691.84 | -1,701.95 | -1,188.60 | +59,643.85 |
| `h3__fernandez_joint` | fernandez | -1,062.37 | -256.08 | -1,176.48 | -1,233.80 | +31,282.75 |
| `h3__histories__direct` | classical | +855.68 | +5,042.19 | +9,397.61 | +6,953.40 | +13,428.14 |
| `h3__histories__mahalanobis_lw` | classical | -3,389.86 | +8,086.13 | +9,300.15 | +11,496.26 | +75,435.16 |
| `h3__histories__pca16` | control | +1,590.81 | +5,589.38 | +9,038.21 | +6,767.16 | -4,183.01 |
| `h3__histories__autoencoder` | control | +1,151.94 | -1,088.78 | -1,708.82 | -1,302.88 | -19,470.67 |
| `h3__histories__random_autoencoder` | control | -274.87 | +3,902.91 | +11,137.65 | +7,917.52 | +29,739.58 |
| `h3__histories__supervised_mlp16` | task | -85.34 | -4,619.03 | -5,756.22 | -4,733.52 | +24,448.15 |
| `h3__histories__tabpfn_fast__late` | task | -1,139.30 | -2,780.13 | -1,199.47 | -1,934.39 | +24,241.30 |
| `h3__histories__tabpfn_full__late` | task | -448.93 | -3,302.08 | -2,555.24 | -3,064.54 | +7,481.76 |
| `h3__histories__tabfm__early_concat` | state | -673.95 | +3,690.44 | +8,735.79 | +9,905.18 | +36,065.36 |
| `h3__histories__tabfm__early_mean` | state | -667.78 | +3,702.29 | +8,743.34 | +9,910.94 | +36,001.64 |
| `h3__histories__tabfm__late` | task | -1,960.20 | -1,405.63 | +8,050.82 | +5,351.11 | +46,228.47 |
| `h3__histories__tabfm__early_concat_labelnull` | state | -2,154.41 | -1,176.95 | +11,355.18 | +9,775.32 | +48,564.42 |
| `h3__histories__exaone__late` | task | -975.50 | -997.84 | +7,165.41 | +1,502.98 | +33,383.84 |
| `h3__histories__exaone__item_first_concat` | state | -2,820.65 | -3,081.48 | +6,872.34 | +6,218.91 | +53,688.49 |
| `h3__histories__exaone__item_first_mean` | state | -2,818.57 | -3,065.14 | +7,150.59 | +6,412.87 | +53,689.78 |
| `h3__histories__exaone__item_last_concat` | task | -1,425.29 | +867.60 | +10,608.91 | +8,696.69 | +38,086.90 |
| `uniform_network` | reference | -2,823.19 | -3,100.83 | -3,100.83 | -3,100.83 | +53,688.93 |
| `zero_network` | reference | -6,838.05 | +3,796.42 | +3,796.42 | +3,796.42 | +71,824.09 |
| `raw_sample_covariance` | control | — | — | — | — | — |
| `ff5_mom_diagonal` | control | — | — | — | — | — |
| `ff5_mom_sample_residual_covariance` | control | — | — | — | — | — |

## Covariance controls

| Control | Held-out log-likelihood | Correlation-only |
| --- | ---: | ---: |
| `histories__pca16` | 1,363,516.71 | 1,596,674.49 |
| `histories__pca16` | 1,679,433.57 | 1,596,674.49 |
| `histories__pca16` | 1,596,674.49 | 1,596,674.49 |
| `histories__pca16` | 1,364,594.10 | 1,596,674.49 |
| `histories__pca16` | 1,683,362.80 | 1,596,674.49 |
| `histories__pca16` | 1,573,487.37 | 1,596,674.49 |
| `histories__pca16` | 1,363,811.41 | 1,596,674.49 |
| `histories__pca16` | 1,681,167.24 | 1,596,674.49 |
| `histories__pca16` | 1,593,709.02 | 1,596,674.49 |
| `histories__autoencoder` | 1,363,212.44 | 1,585,005.60 |
| `histories__autoencoder` | 1,672,955.01 | 1,585,005.60 |
| `histories__autoencoder` | 1,585,005.60 | 1,585,005.60 |
| `histories__autoencoder` | 1,364,339.97 | 1,585,005.60 |
| `histories__autoencoder` | 1,674,554.99 | 1,585,005.60 |
| `histories__autoencoder` | 1,528,252.32 | 1,585,005.60 |
| `histories__autoencoder` | 1,363,216.38 | 1,585,005.60 |
| `histories__autoencoder` | 1,673,223.44 | 1,585,005.60 |
| `histories__autoencoder` | 1,576,096.40 | 1,585,005.60 |
| `histories__random_autoencoder` | 1,361,618.68 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,677,952.31 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,632,334.16 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,363,628.91 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,685,973.16 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,623,040.17 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,362,678.03 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,683,436.28 | 1,632,334.16 |
| `histories__random_autoencoder` | 1,634,275.50 | 1,632,334.16 |
| `broad__pca16` | 1,365,220.26 | 1,532,815.22 |
| `broad__pca16` | 1,679,076.53 | 1,532,815.22 |
| `broad__pca16` | 1,532,815.22 | 1,532,815.22 |
| `broad__pca16` | 1,363,637.52 | 1,532,815.22 |
| `broad__pca16` | 1,677,087.49 | 1,532,815.22 |
| `broad__pca16` | 1,582,960.80 | 1,532,815.22 |
| `broad__pca16` | 1,366,270.93 | 1,532,815.22 |
| `broad__pca16` | 1,680,584.18 | 1,532,815.22 |
| `broad__pca16` | 1,501,794.00 | 1,532,815.22 |
| `broad__autoencoder` | 1,365,839.61 | 1,502,040.70 |
| `broad__autoencoder` | 1,678,348.26 | 1,502,040.70 |
| `broad__autoencoder` | 1,502,040.70 | 1,502,040.70 |
| `broad__autoencoder` | 1,364,275.76 | 1,502,040.70 |
| `broad__autoencoder` | 1,676,617.79 | 1,502,040.70 |
| `broad__autoencoder` | 1,558,931.14 | 1,502,040.70 |
| `broad__autoencoder` | 1,366,471.95 | 1,502,040.70 |
| `broad__autoencoder` | 1,679,281.78 | 1,502,040.70 |
| `broad__autoencoder` | 1,480,011.11 | 1,502,040.70 |
| `broad__random_autoencoder` | 1,360,463.08 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,672,319.29 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,643,332.24 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,360,252.41 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,672,160.49 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,647,182.33 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,360,976.26 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,672,636.71 | 1,643,332.24 |
| `broad__random_autoencoder` | 1,633,413.91 | 1,643,332.24 |
| `metrics__pca16` | 1,365,849.92 | 1,500,487.54 |
| `metrics__pca16` | 1,678,453.80 | 1,500,487.54 |
| `metrics__pca16` | 1,500,487.54 | 1,500,487.54 |
| `metrics__pca16` | 1,364,134.10 | 1,500,487.54 |
| `metrics__pca16` | 1,676,792.86 | 1,500,487.54 |
| `metrics__pca16` | 1,563,390.42 | 1,500,487.54 |
| `metrics__pca16` | 1,366,424.18 | 1,500,487.54 |
| `metrics__pca16` | 1,679,444.04 | 1,500,487.54 |
| `metrics__pca16` | 1,482,451.64 | 1,500,487.54 |
| `metrics__autoencoder` | 1,365,958.87 | 1,477,464.47 |
| `metrics__autoencoder` | 1,675,687.68 | 1,477,464.47 |
| `metrics__autoencoder` | 1,477,464.47 | 1,477,464.47 |
| `metrics__autoencoder` | 1,364,474.53 | 1,477,464.47 |
| `metrics__autoencoder` | 1,674,723.92 | 1,477,464.47 |
| `metrics__autoencoder` | 1,541,124.77 | 1,477,464.47 |
| `metrics__autoencoder` | 1,366,278.52 | 1,477,464.47 |
| `metrics__autoencoder` | 1,676,356.19 | 1,477,464.47 |
| `metrics__autoencoder` | 1,471,436.29 | 1,477,464.47 |
| `metrics__random_autoencoder` | 1,361,498.22 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,681,934.61 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,654,904.64 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,361,292.30 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,681,041.63 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,654,782.09 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,362,805.90 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,686,977.47 | 1,654,904.64 |
| `metrics__random_autoencoder` | 1,659,667.89 | 1,654,904.64 |
| `histories@income_assets__pca16` | 1,363,131.04 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,678,642.48 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,605,618.95 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,364,597.43 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,683,002.46 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,574,783.85 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,363,701.88 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,681,166.24 | 1,605,618.95 |
| `histories@income_assets__pca16` | 1,598,965.04 | 1,605,618.95 |
| `histories@income_assets__autoencoder` | 1,362,755.38 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,671,400.52 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,596,338.37 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,364,485.83 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,672,756.16 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,518,747.07 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,363,230.51 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,671,735.79 | 1,596,338.37 |
| `histories@income_assets__autoencoder` | 1,573,861.49 | 1,596,338.37 |
| `histories@income_assets__random_autoencoder` | 1,361,510.92 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,678,078.58 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,636,238.04 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,363,607.59 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,686,189.83 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,627,560.75 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,362,617.40 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,683,830.53 | 1,636,238.04 |
| `histories@income_assets__random_autoencoder` | 1,639,491.27 | 1,636,238.04 |
| `h3__histories__pca16` | 1,363,823.94 | 1,602,215.74 |
| `h3__histories__pca16` | 1,679,897.33 | 1,602,215.74 |
| `h3__histories__pca16` | 1,602,215.74 | 1,602,215.74 |
| `h3__histories__pca16` | 1,364,187.90 | 1,602,215.74 |
| `h3__histories__pca16` | 1,683,346.16 | 1,602,215.74 |
| `h3__histories__pca16` | 1,634,426.11 | 1,602,215.74 |
| `h3__histories__pca16` | 1,363,464.23 | 1,602,215.74 |
| `h3__histories__pca16` | 1,681,075.11 | 1,602,215.74 |
| `h3__histories__pca16` | 1,624,476.20 | 1,602,215.74 |
| `h3__histories__autoencoder` | 1,363,385.07 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,673,219.17 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,586,928.08 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,363,992.71 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,672,599.13 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,567,078.80 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,363,020.67 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,673,005.08 | 1,586,928.08 |
| `h3__histories__autoencoder` | 1,594,368.42 | 1,586,928.08 |
| `h3__histories__random_autoencoder` | 1,361,958.26 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,678,210.86 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,636,138.33 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,363,927.42 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,685,445.60 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,662,004.81 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,362,932.48 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,682,225.47 | 1,636,138.33 |
| `h3__histories__random_autoencoder` | 1,644,811.74 | 1,636,138.33 |
| `raw_sample_covariance` | 1,070,558.51 | 1,070,558.51 |
| `raw_sample_covariance` | 1,070,558.51 | 1,070,558.51 |
| `ff5_mom_diagonal` | 1,678,104.37 | 1,678,222.84 |
| `ff5_mom_diagonal` | 1,678,222.84 | 1,678,222.84 |
| `ff5_mom_sample_residual_covariance` | 1,070,558.51 | 1,070,558.51 |
| `ff5_mom_sample_residual_covariance` | 1,070,558.51 | 1,070,558.51 |

## Paired stationary-bootstrap intervals (exp kernel, diagonal innovations)

Summed daily differences against the joint network; 95% percentile intervals
with 21- and 63-day expected blocks. Intervals are descriptive: the approaches
were not preregistered and these years were inspected during development.

| Approach | Difference | 21-day interval | 63-day interval | Politis-White block |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | -2,986.94 | [-5,070.9, -1,328.5] | [-6,154.0, -654.2] | 73.4 |
| `fernandez_market_to_book` | -3,856.05 | [-6,012.6, -2,103.7] | [-6,652.9, -1,547.2] | 62.0 |
| `fernandez_dividend_yield` | -129.97 | [-1,323.7, +856.4] | [-1,545.7, +1,190.9] | 36.8 |
| `histories__direct` | +5,170.44 | [+2,653.8, +8,179.3] | [+1,661.6, +9,753.8] | 72.4 |
| `histories__mahalanobis_lw` | +6,021.66 | [-10,284.7, +22,358.2] | [-15,973.9, +30,381.7] | 67.2 |
| `histories__pca16` | +5,125.62 | [+2,781.2, +7,828.4] | [+1,897.7, +9,143.1] | 70.8 |
| `histories__autoencoder` | -1,352.95 | [-3,511.7, +549.9] | [-4,702.5, +1,350.6] | 72.2 |
| `histories__random_autoencoder` | +3,644.36 | [+919.7, +7,111.0] | [-206.1, +8,984.7] | 73.7 |
| `histories__supervised_mlp16` | -5,469.23 | [-9,953.6, -1,819.5] | [-12,409.0, -359.5] | 72.8 |
| `histories__tabpfn_fast__late` | -2,754.54 | [-4,203.8, -1,550.2] | [-4,520.6, -1,278.5] | 53.0 |
| `histories__tabpfn_full__late` | -3,114.11 | [-5,570.6, -1,109.6] | [-6,889.5, -337.0] | 71.8 |
| `histories__tabfm__early_concat` | +3,566.10 | [+587.8, +7,261.1] | [-600.1, +9,252.4] | 72.6 |
| `histories__tabfm__early_mean` | +3,583.71 | [+602.3, +7,284.0] | [-585.5, +9,273.8] | 72.6 |
| `histories__tabfm__late` | -1,907.33 | [-4,520.9, -97.1] | [-4,914.2, +428.6] | 51.8 |
| `histories__tabfm__early_concat_labelnull` | -1,582.80 | [-4,523.7, +672.7] | [-5,055.8, +1,486.5] | 57.0 |
| `histories__exaone__late` | -2,265.13 | [-3,526.9, -1,170.3] | [-3,707.5, -958.5] | 42.9 |
| `histories__exaone__item_first_concat` | -3,072.22 | [-6,986.9, -425.6] | [-7,650.6, +372.2] | 54.6 |
| `histories__exaone__item_first_mean` | -3,047.21 | [-6,966.5, -390.2] | [-7,631.9, +414.4] | 54.7 |
| `histories__exaone__item_last_concat` | -832.55 | [-2,565.5, +503.3] | [-2,780.6, +927.7] | 53.3 |
| `broad__direct` | -705.73 | [-1,554.0, -73.2] | [-1,597.0, +7.3] | 43.0 |
| `broad__mahalanobis_lw` | +11,770.57 | [-6,338.9, +29,494.5] | [-12,069.9, +37,744.3] | 64.9 |
| `broad__pca16` | +4,768.58 | [+2,841.8, +7,868.2] | [+2,512.9, +8,342.2] | 55.2 |
| `broad__autoencoder` | +4,040.31 | [+1,615.1, +7,669.1] | [+962.8, +8,459.4] | 57.5 |
| `broad__random_autoencoder` | -1,988.67 | [-4,150.6, -599.2] | [-4,412.9, -298.2] | 51.7 |
| `broad__supervised_mlp16` | +3,694.89 | [+1,306.1, +6,635.6] | [+364.2, +8,128.5] | 72.7 |
| `broad__tabpfn_fast__late` | -2,544.17 | [-3,858.9, -1,395.0] | [-4,294.5, -1,122.1] | 57.4 |
| `broad__tabpfn_full__late` | -1,495.39 | [-2,907.5, -213.1] | [-3,668.9, +298.2] | 69.9 |
| `broad__tabfm__early_concat` | +1,751.17 | [-249.3, +4,128.3] | [-940.1, +5,338.0] | 70.1 |
| `broad__tabfm__early_mean` | +1,741.44 | [-182.5, +4,044.5] | [-854.1, +5,222.8] | 70.2 |
| `broad__tabfm__late` | -2,217.11 | [-4,852.6, -482.9] | [-5,185.6, -39.5] | 50.2 |
| `broad__tabfm__early_concat_labelnull` | -440.63 | [-4,171.0, +2,956.6] | [-5,155.3, +4,428.1] | 63.4 |
| `broad__exaone__late` | -4,072.12 | [-6,438.9, -2,058.0] | [-7,621.6, -1,402.5] | 68.1 |
| `broad__exaone__item_first_concat` | -3,100.03 | [-7,010.2, -467.9] | [-7,665.5, +319.6] | 54.5 |
| `broad__exaone__item_first_mean` | -3,099.78 | [-7,006.6, -470.9] | [-7,660.6, +315.2] | 54.5 |
| `broad__exaone__item_last_concat` | -3,129.30 | [-4,715.4, -1,838.2] | [-5,056.5, -1,527.7] | 53.6 |
| `metrics__direct` | -549.14 | [-1,664.6, +508.1] | [-2,240.0, +961.1] | 69.4 |
| `metrics__mahalanobis_lw` | +14,996.12 | [-787.0, +31,514.8] | [-5,990.4, +39,629.6] | 67.0 |
| `metrics__pca16` | +4,145.85 | [+1,660.0, +7,857.6] | [+938.8, +8,663.5] | 57.6 |
| `metrics__autoencoder` | +1,379.73 | [-2,940.0, +6,074.9] | [-4,906.8, +7,619.3] | 65.7 |
| `metrics__random_autoencoder` | +7,626.66 | [+2,297.1, +14,381.8] | [+82.2, +18,141.1] | 73.7 |
| `metrics__supervised_mlp16` | +4,735.49 | [+2,305.2, +7,604.0] | [+1,450.0, +8,760.5] | 66.6 |
| `metrics__tabpfn_fast__late` | -2,086.74 | [-3,183.6, -1,117.3] | [-3,515.5, -899.2] | 54.8 |
| `metrics__tabpfn_full__late` | +2,556.87 | [+1,083.6, +4,322.6] | [+481.2, +5,173.9] | 72.4 |
| `metrics__tabfm__early_concat` | +2,563.82 | [+141.8, +5,503.0] | [-771.0, +7,097.2] | 71.9 |
| `metrics__tabfm__early_mean` | +2,668.01 | [+187.9, +5,677.9] | [-752.9, +7,313.3] | 71.9 |
| `metrics__tabfm__late` | -1,214.93 | [-3,969.0, +958.6] | [-4,437.6, +1,770.8] | 56.9 |
| `metrics__tabfm__early_concat_labelnull` | -249.42 | [-4,114.2, +3,357.1] | [-5,177.0, +4,971.1] | 64.4 |
| `metrics__exaone__late` | -1,747.84 | [-2,739.7, -809.4] | [-2,939.0, -606.2] | 43.4 |
| `metrics__exaone__item_first_concat` | -3,087.39 | [-6,998.7, -447.3] | [-7,659.1, +343.7] | 54.5 |
| `metrics__exaone__item_first_mean` | -3,074.73 | [-6,986.2, -432.0] | [-7,647.9, +362.9] | 54.6 |
| `metrics__exaone__item_last_concat` | -537.02 | [-1,777.4, +466.6] | [-1,890.9, +795.1] | 53.2 |
| `histories@income_assets__direct` | +4,212.67 | [+1,995.4, +6,933.3] | [+1,077.3, +8,390.5] | 73.2 |
| `histories@income_assets__mahalanobis_lw` | +6,063.17 | [-10,073.1, +22,266.7] | [-15,732.0, +30,343.3] | 67.4 |
| `histories@income_assets__pca16` | +4,334.53 | [+2,227.1, +6,819.7] | [+1,398.3, +8,050.3] | 71.9 |
| `histories@income_assets__autoencoder` | -2,907.43 | [-5,719.6, -620.0] | [-7,244.8, +325.7] | 73.1 |
| `histories@income_assets__random_autoencoder` | +3,770.63 | [+799.2, +7,533.2] | [-432.9, +9,569.4] | 73.5 |
| `histories@income_assets__supervised_mlp16` | +371.58 | [-1,187.4, +2,147.8] | [-1,791.8, +2,853.4] | 67.0 |
| `histories@income_assets__tabpfn_fast__late` | -1,087.20 | [-3,027.5, +406.7] | [-3,283.0, +889.1] | 54.0 |
| `histories@income_assets__tabpfn_full__late` | -1,794.68 | [-2,778.6, -919.0] | [-2,954.4, -759.6] | 43.9 |
| `histories@income_assets__tabfm__early_concat` | +5,608.54 | [+2,064.2, +10,040.6] | [+643.8, +12,524.2] | 73.6 |
| `histories@income_assets__tabfm__early_mean` | +5,635.83 | [+2,079.0, +10,072.7] | [+668.9, +12,566.9] | 73.6 |
| `histories@income_assets__tabfm__late` | +269.20 | [-3,244.7, +3,693.8] | [-4,257.7, +5,249.7] | 65.2 |
| `histories@income_assets__tabfm__early_concat_labelnull` | -1,330.09 | [-4,022.8, +785.2] | [-4,500.2, +1,558.0] | 57.3 |
| `histories@income_assets__exaone__late` | +8,096.15 | [+1,623.9, +16,219.1] | [-1,067.9, +20,648.6] | 73.0 |
| `histories@income_assets__exaone__item_first_concat` | -3,071.58 | [-6,985.1, -426.1] | [-7,648.1, +371.6] | 54.6 |
| `histories@income_assets__exaone__item_first_mean` | -3,045.94 | [-6,962.8, -391.2] | [-7,627.3, +413.6] | 54.7 |
| `histories@income_assets__exaone__item_last_concat` | +1,887.06 | [-1,906.4, +6,049.8] | [-3,134.5, +8,122.1] | 69.3 |
| `h3__fernandez_market_cap_assets` | -7,997.81 | [-14,063.7, -3,916.6] | [-15,000.2, -2,889.7] | 53.7 |
| `h3__fernandez_market_to_book` | -8,243.57 | [-14,267.2, -4,170.7] | [-15,141.0, -3,178.5] | 51.8 |
| `h3__fernandez_dividend_yield` | -1,691.84 | [-7,186.7, +2,492.2] | [-8,536.0, +3,989.2] | 59.2 |
| `h3__fernandez_joint` | -256.08 | [-3,997.2, +2,722.6] | [-4,908.4, +3,852.6] | 60.2 |
| `h3__histories__direct` | +5,042.19 | [+2,510.0, +8,105.7] | [+1,518.1, +9,666.3] | 71.7 |
| `h3__histories__mahalanobis_lw` | +8,086.13 | [-5,811.0, +22,893.7] | [-10,641.6, +30,157.7] | 68.2 |
| `h3__histories__pca16` | +5,589.38 | [+3,088.0, +8,446.1] | [+2,189.2, +9,813.0] | 69.1 |
| `h3__histories__autoencoder` | -1,088.78 | [-3,450.1, +1,076.0] | [-4,718.1, +2,031.0] | 70.8 |
| `h3__histories__random_autoencoder` | +3,902.91 | [+1,125.5, +7,414.3] | [+5.4, +9,322.2] | 73.0 |
| `h3__histories__supervised_mlp16` | -4,619.03 | [-7,912.0, -1,872.3] | [-9,636.4, -820.1] | 69.9 |
| `h3__histories__tabpfn_fast__late` | -2,780.13 | [-4,226.9, -1,554.8] | [-4,605.3, -1,266.9] | 54.7 |
| `h3__histories__tabpfn_full__late` | -3,302.08 | [-5,807.6, -1,256.4] | [-7,138.2, -488.7] | 71.5 |
| `h3__histories__tabfm__early_concat` | +3,690.44 | [+585.3, +7,527.9] | [-630.4, +9,591.7] | 72.6 |
| `h3__histories__tabfm__early_mean` | +3,702.29 | [+595.9, +7,540.6] | [-622.7, +9,606.0] | 72.6 |
| `h3__histories__tabfm__late` | -1,405.63 | [-4,153.0, +696.7] | [-4,602.6, +1,456.8] | 55.8 |
| `h3__histories__tabfm__early_concat_labelnull` | -1,176.95 | [-4,418.1, +1,473.6] | [-5,069.4, +2,507.1] | 59.7 |
| `h3__histories__exaone__late` | -997.84 | [-2,266.6, -66.4] | [-2,239.5, +27.8] | 39.2 |
| `h3__histories__exaone__item_first_concat` | -3,081.48 | [-6,994.6, -439.2] | [-7,655.6, +354.8] | 54.6 |
| `h3__histories__exaone__item_first_mean` | -3,065.14 | [-6,979.1, -418.9] | [-7,642.0, +380.8] | 54.6 |
| `h3__histories__exaone__item_last_concat` | +867.60 | [-1,631.9, +3,479.3] | [-2,372.2, +4,700.5] | 66.7 |

## Model confidence sets (size 0.10)

| Family | Networks | Included |
| --- | ---: | --- |
| spherical|exp | 90 | `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder` |
| diagonal|exp | 90 | `histories__direct`, `histories__mahalanobis_lw`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_full__late`, `histories@income_assets__direct`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__pca16`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late`, `h3__histories__direct`, `h3__histories__mahalanobis_lw`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `zero_network` |
| correlation|exp | 93 | `histories__mahalanobis_lw`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `broad__mahalanobis_lw`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `metrics__mahalanobis_lw`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `h3__fernandez_dividend_yield`, `h3__histories__mahalanobis_lw`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `uniform_network`, `zero_network`, `ff5_mom_diagonal` |
| spherical|median | 90 | `histories__direct`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__pca16`, `broad__autoencoder`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_mean`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__pca16`, `metrics__autoencoder`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `h3__fernandez_dividend_yield`, `h3__histories__direct`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| diagonal|median | 90 | `histories__direct`, `histories__mahalanobis_lw`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__autoencoder`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__early_concat_labelnull`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__pca16`, `histories@income_assets__random_autoencoder`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `h3__histories__direct`, `h3__histories__mahalanobis_lw`, `h3__histories__pca16`, `h3__histories__random_autoencoder`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat`, `zero_network` |
| correlation|median | 93 | `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `metrics__mahalanobis_lw`, `metrics__exaone__item_first_mean`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `h3__histories__mahalanobis_lw`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `zero_network`, `ff5_mom_diagonal` |
| spherical|matched | 90 | `metrics__direct` |
| diagonal|matched | 90 | `histories__direct`, `histories__mahalanobis_lw`, `histories__pca16`, `histories__random_autoencoder`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `broad__direct`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__early_concat_labelnull`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__pca16`, `histories@income_assets__random_autoencoder`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_last_concat`, `h3__histories__mahalanobis_lw`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__item_last_concat`, `zero_network` |
| correlation|matched | 93 | `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `broad__mahalanobis_lw`, `broad__tabfm__early_concat_labelnull`, `metrics__mahalanobis_lw`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `h3__histories__mahalanobis_lw`, `zero_network`, `ff5_mom_diagonal` |
| controls|diagonal-exp | 91 | `histories__direct`, `histories__mahalanobis_lw`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `broad__mahalanobis_lw`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_full__late`, `histories@income_assets__direct`, `histories@income_assets__mahalanobis_lw`, `histories@income_assets__pca16`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__exaone__late`, `h3__histories__direct`, `h3__histories__mahalanobis_lw`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `ff5_mom_diagonal` |

## Label-permutation placebos (exp kernel, diagonal innovations)

Each prespecified network is compared with 19 permutations P W P' restricted
within prior-year log-assets terciles; the spectrum, and so the Jacobian, is unchanged.

| Approach | Observed | Placebo mean | Placebo max | Rank p-value |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_joint` | 1,674,307.95 | 1,670,260.20 | 1,673,278.56 | 0.05 |
| `histories__direct` | 1,679,478.39 | 1,671,587.05 | 1,678,301.28 | 0.05 |
| `histories__pca16` | 1,679,433.57 | 1,671,569.98 | 1,678,009.04 | 0.05 |
| `histories__tabpfn_full__late` | 1,671,193.84 | 1,671,697.25 | 1,678,375.30 | 0.40 |
| `histories__tabfm__early_concat` | 1,677,874.05 | 1,671,973.95 | 1,675,912.77 | 0.05 |

## Network concentration

Mean effective-neighbour fraction (1/sum w^2)/(N-1); one is uniform.

| Approach | exp | median | matched |
| --- | ---: | ---: | ---: |
| `broad__autoencoder` | 0.917 | 0.951 | 0.898 |
| `broad__direct` | 0.992 | 0.996 | 0.898 |
| `broad__exaone__item_first_concat` | 1.000 | 0.786 | 0.898 |
| `broad__exaone__item_first_mean` | 1.000 | 0.771 | 0.898 |
| `broad__exaone__item_last_concat` | 0.981 | 0.868 | 0.898 |
| `broad__exaone__late` | 0.952 | 0.752 | 0.898 |
| `broad__mahalanobis_lw` | 0.076 | 0.991 | 0.898 |
| `broad__pca16` | 0.928 | 0.961 | 0.898 |
| `broad__random_autoencoder` | 0.957 | 0.973 | 0.898 |
| `broad__supervised_mlp16` | 0.857 | 0.885 | 0.898 |
| `broad__tabfm__early_concat` | 0.975 | 0.918 | 0.898 |
| `broad__tabfm__early_concat_labelnull` | 0.997 | 0.936 | 0.898 |
| `broad__tabfm__early_mean` | 0.975 | 0.916 | 0.898 |
| `broad__tabfm__late` | 0.991 | 0.850 | 0.898 |
| `broad__tabpfn_fast__late` | 0.969 | 0.848 | 0.898 |
| `broad__tabpfn_full__late` | 0.938 | 0.841 | 0.898 |
| `fernandez_dividend_yield` | 0.795 | 0.885 | 0.898 |
| `fernandez_joint` | 0.898 | 0.942 | 0.898 |
| `fernandez_market_cap_assets` | 0.801 | 0.885 | 0.898 |
| `fernandez_market_to_book` | 0.804 | 0.883 | 0.898 |
| `h3__fernandez_dividend_yield` | 0.640 | 0.655 | 0.898 |
| `h3__fernandez_joint` | 0.785 | 0.875 | 0.898 |
| `h3__fernandez_market_cap_assets` | 0.636 | 0.636 | 0.898 |
| `h3__fernandez_market_to_book` | 0.638 | 0.654 | 0.898 |
| `h3__histories__autoencoder` | 0.886 | 0.800 | 0.898 |
| `h3__histories__direct` | 0.918 | 0.831 | 0.898 |
| `h3__histories__exaone__item_first_concat` | 1.000 | 0.800 | 0.898 |
| `h3__histories__exaone__item_first_mean` | 1.000 | 0.787 | 0.898 |
| `h3__histories__exaone__item_last_concat` | 0.981 | 0.849 | 0.898 |
| `h3__histories__exaone__late` | 0.952 | 0.745 | 0.898 |
| `h3__histories__mahalanobis_lw` | 0.741 | 0.811 | 0.898 |
| `h3__histories__pca16` | 0.891 | 0.838 | 0.898 |
| `h3__histories__random_autoencoder` | 0.949 | 0.816 | 0.898 |
| `h3__histories__supervised_mlp16` | 0.817 | 0.614 | 0.898 |
| `h3__histories__tabfm__early_concat` | 0.971 | 0.906 | 0.898 |
| `h3__histories__tabfm__early_concat_labelnull` | 0.995 | 0.864 | 0.898 |
| `h3__histories__tabfm__early_mean` | 0.970 | 0.906 | 0.898 |
| `h3__histories__tabfm__late` | 0.990 | 0.826 | 0.898 |
| `h3__histories__tabpfn_fast__late` | 0.967 | 0.842 | 0.898 |
| `h3__histories__tabpfn_full__late` | 0.939 | 0.836 | 0.898 |
| `histories@income_assets__autoencoder` | 0.923 | 0.806 | 0.898 |
| `histories@income_assets__direct` | 0.936 | 0.860 | 0.898 |
| `histories@income_assets__exaone__item_first_concat` | 1.000 | 0.789 | 0.898 |
| `histories@income_assets__exaone__item_first_mean` | 1.000 | 0.776 | 0.898 |
| `histories@income_assets__exaone__item_last_concat` | 0.993 | 0.907 | 0.898 |
| `histories@income_assets__exaone__late` | 0.979 | 0.815 | 0.898 |
| `histories@income_assets__mahalanobis_lw` | 0.625 | 0.834 | 0.898 |
| `histories@income_assets__pca16` | 0.926 | 0.850 | 0.898 |
| `histories@income_assets__random_autoencoder` | 0.957 | 0.839 | 0.898 |
| `histories@income_assets__supervised_mlp16` | 0.816 | 0.803 | 0.898 |
| `histories@income_assets__tabfm__early_concat` | 0.957 | 0.913 | 0.898 |
| `histories@income_assets__tabfm__early_concat_labelnull` | 0.993 | 0.874 | 0.898 |
| `histories@income_assets__tabfm__early_mean` | 0.957 | 0.913 | 0.898 |
| `histories@income_assets__tabfm__late` | 0.995 | 0.892 | 0.898 |
| `histories@income_assets__tabpfn_fast__late` | 0.986 | 0.858 | 0.898 |
| `histories@income_assets__tabpfn_full__late` | 0.961 | 0.843 | 0.898 |
| `histories__autoencoder` | 0.899 | 0.813 | 0.898 |
| `histories__direct` | 0.925 | 0.864 | 0.898 |
| `histories__exaone__item_first_concat` | 1.000 | 0.795 | 0.898 |
| `histories__exaone__item_first_mean` | 1.000 | 0.781 | 0.898 |
| `histories__exaone__item_last_concat` | 0.981 | 0.856 | 0.898 |
| `histories__exaone__late` | 0.951 | 0.747 | 0.898 |
| `histories__mahalanobis_lw` | 0.633 | 0.831 | 0.898 |
| `histories__pca16` | 0.913 | 0.853 | 0.898 |
| `histories__random_autoencoder` | 0.955 | 0.839 | 0.898 |
| `histories__supervised_mlp16` | 0.784 | 0.655 | 0.898 |
| `histories__tabfm__early_concat` | 0.972 | 0.905 | 0.898 |
| `histories__tabfm__early_concat_labelnull` | 0.995 | 0.874 | 0.898 |
| `histories__tabfm__early_mean` | 0.972 | 0.905 | 0.898 |
| `histories__tabfm__late` | 0.990 | 0.829 | 0.898 |
| `histories__tabpfn_fast__late` | 0.967 | 0.844 | 0.898 |
| `histories__tabpfn_full__late` | 0.938 | 0.841 | 0.898 |
| `metrics__autoencoder` | 0.911 | 0.944 | 0.898 |
| `metrics__direct` | 0.985 | 0.993 | 0.898 |
| `metrics__exaone__item_first_concat` | 1.000 | 0.807 | 0.898 |
| `metrics__exaone__item_first_mean` | 1.000 | 0.778 | 0.898 |
| `metrics__exaone__item_last_concat` | 0.980 | 0.864 | 0.898 |
| `metrics__exaone__late` | 0.951 | 0.749 | 0.898 |
| `metrics__mahalanobis_lw` | 0.106 | 0.983 | 0.898 |
| `metrics__pca16` | 0.915 | 0.952 | 0.898 |
| `metrics__random_autoencoder` | 0.961 | 0.968 | 0.898 |
| `metrics__supervised_mlp16` | 0.851 | 0.879 | 0.898 |
| `metrics__tabfm__early_concat` | 0.980 | 0.919 | 0.898 |
| `metrics__tabfm__early_concat_labelnull` | 0.998 | 0.916 | 0.898 |
| `metrics__tabfm__early_mean` | 0.979 | 0.916 | 0.898 |
| `metrics__tabfm__late` | 0.991 | 0.842 | 0.898 |
| `metrics__tabpfn_fast__late` | 0.968 | 0.849 | 0.898 |
| `metrics__tabpfn_full__late` | 0.937 | 0.842 | 0.898 |
| `uniform_network` | nan | nan | nan |
| `zero_network` | nan | nan | nan |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
