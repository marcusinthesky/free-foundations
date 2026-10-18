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
| `covariance_exposures` | control | -3,138.57 | -4,414.38 | +8,016.21 | +7,347.07 | -2,355.55 |
| `fernandez_market_cap_assets` | fernandez | +298.20 | -322.86 | -793.72 | -1,025.51 | -106.37 |
| `fernandez_market_to_book` | fernandez | -800.87 | -1,778.48 | -2,072.82 | -2,156.96 | -769.94 |
| `fernandez_dividend_yield` | fernandez | -983.78 | -834.81 | -1,337.76 | -1,505.93 | -424.59 |
| `fernandez_joint` | fernandez | +0.00 | +0.00 | -915.75 | -0.00 | +0.00 |
| `histories@decoded__direct` | calibrated | -3,234.71 | -4,579.72 | +105.16 | -496.21 | -2,477.23 |
| `histories@decoded__pca16` | calibrated | -3,236.78 | -4,579.06 | -2,614.50 | -1,379.37 | -2,477.48 |
| `histories@decoded__autoencoder` | calibrated | -3,234.56 | -4,574.23 | +822.12 | -211.61 | -2,474.11 |
| `histories@decoded__random_autoencoder` | calibrated | -3,234.34 | -4,574.35 | +390.40 | -246.45 | -2,474.13 |
| `histories@decoded__supervised_mlp16` | calibrated | -3,236.23 | -4,578.59 | -1,295.24 | -1,376.71 | -2,476.19 |
| `histories@decoded__tabpfn_fast__late` | calibrated | -3,215.74 | -4,540.59 | +4,474.15 | +3,442.75 | -2,452.13 |
| `histories@decoded__tabpfn_full__late` | calibrated | -3,215.60 | -4,541.27 | +4,473.72 | +3,390.77 | -2,451.70 |
| `histories@decoded__tabfm__early_concat` | calibrated | -3,220.78 | -4,551.63 | +3,527.37 | +2,700.97 | -2,458.38 |
| `histories@decoded__tabfm__early_mean` | calibrated | -3,220.74 | -4,551.46 | +3,532.56 | +2,741.46 | -2,458.25 |
| `histories@decoded__tabfm__late` | calibrated | -3,215.35 | -4,541.01 | +4,345.62 | +3,526.52 | -2,452.27 |
| `histories@decoded__tabfm__early_concat_labelnull` | calibrated | -3,224.71 | -4,559.69 | +2,723.55 | +1,928.29 | -2,463.70 |
| `histories@decoded__exaone__late` | calibrated | -3,216.64 | -4,541.87 | +4,378.81 | +3,451.42 | -2,452.20 |
| `histories@decoded__exaone__item_first_concat` | calibrated | -3,235.57 | -4,597.89 | -204.48 | -1,224.69 | -2,487.03 |
| `histories@decoded__exaone__item_first_mean` | calibrated | -3,235.67 | -4,582.92 | -196.64 | -1,197.50 | -2,479.38 |
| `histories@decoded__exaone__item_last_concat` | calibrated | -3,213.82 | -4,537.35 | +4,385.72 | +3,426.04 | -2,449.28 |
| `histories__direct` | classical | +818.94 | +1,216.98 | +3,206.89 | +2,187.09 | +1,045.94 |
| `histories__mahalanobis_lw` | classical | -5,315.24 | -10,613.60 | -2,514.62 | -1,429.82 | -14,963.39 |
| `histories__euclidean` | classical | +1,310.49 | +861.37 | +2,983.00 | +703.78 | +1,372.50 |
| `histories__direct_no_indicators` | classical | +2,237.61 | +3,155.91 | +3,166.02 | +2,561.45 | +1,100.56 |
| `histories__euclidean_no_indicators` | classical | +1,310.49 | +861.37 | +2,983.00 | +703.78 | +1,372.50 |
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
| `broad__euclidean` | classical | +8,272.45 | +1,330.91 | -2,067.43 | +3,847.11 | +4,324.14 |
| `broad__direct_no_indicators` | classical | -1,724.16 | -2,188.71 | -2,879.74 | +2,031.83 | -819.17 |
| `broad__euclidean_no_indicators` | classical | +4,692.80 | +1,331.50 | -2,645.92 | -582.38 | +3,689.22 |
| `broad__direct_no_size` | classical | -863.68 | -888.16 | -1,932.62 | +6,590.80 | +57.70 |
| `broad__euclidean_no_size` | classical | +9,231.74 | +1,260.60 | -1,928.53 | +4,123.32 | +5,362.05 |
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
| `metrics__euclidean` | classical | +7,566.78 | -1,958.41 | -865.22 | +4,825.95 | +588.75 |
| `metrics__direct_no_indicators` | classical | +411.03 | +1,232.41 | -429.55 | +7,026.07 | +838.05 |
| `metrics__euclidean_no_indicators` | classical | +13,792.09 | +12,445.64 | +152.88 | +2,784.30 | +7,003.32 |
| `metrics__direct_no_size` | classical | +243.53 | +675.40 | -765.05 | +6,957.66 | +742.85 |
| `metrics__euclidean_no_size` | classical | +7,595.65 | -2,101.43 | -706.34 | +4,766.08 | -398.60 |
| `metrics__direct_no_changes` | classical | +479.43 | +975.50 | -548.93 | +7,363.86 | +880.06 |
| `metrics__euclidean_no_changes` | classical | +10,444.96 | +2,233.88 | -597.03 | +5,008.80 | +3,119.76 |
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
| `histories@income_assets__euclidean` | classical | +1,446.89 | +1,050.89 | +2,923.93 | +618.20 | +1,175.51 |
| `histories@income_assets__direct_no_indicators` | classical | +2,149.50 | +3,001.23 | +3,112.47 | +2,501.46 | +1,140.85 |
| `histories@income_assets__euclidean_no_indicators` | classical | +1,446.89 | +1,050.89 | +2,923.93 | +618.20 | +1,175.51 |
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
| `histories@shared_market_cap_assets__direct` | classical | +784.04 | +1,167.64 | +3,234.28 | +2,194.56 | +1,042.64 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | classical | -5,185.74 | -10,132.19 | -2,519.73 | -1,384.25 | -15,043.01 |
| `histories@shared_market_cap_assets__euclidean` | classical | +1,290.95 | +924.25 | +2,987.79 | +724.12 | +1,309.83 |
| `histories@shared_market_cap_assets__direct_no_indicators` | classical | +2,212.62 | +3,123.76 | +3,190.34 | +2,579.99 | +1,100.08 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | classical | +1,290.95 | +924.25 | +2,987.79 | +724.12 | +1,309.83 |
| `histories@shared_market_cap_assets__pca16` | control | +1,120.93 | +1,541.37 | +3,311.19 | +2,108.23 | +1,244.47 |
| `histories@shared_market_cap_assets__autoencoder` | control | +806.45 | +935.68 | +2,979.46 | +1,333.15 | +1,323.35 |
| `histories@shared_market_cap_assets__random_autoencoder` | control | -882.96 | -853.28 | +2,230.22 | +760.52 | -258.67 |
| `histories@shared_market_cap_assets__supervised_mlp16` | task | +74.67 | -34.91 | -162.78 | -1,105.31 | +1,079.81 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | task | -1,429.56 | -1,519.35 | +1,851.23 | +563.64 | -447.14 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | task | -585.06 | -250.17 | +2,047.41 | +649.14 | +218.29 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | state | -787.69 | -896.41 | +2,532.62 | +2,382.91 | +243.96 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | state | -777.16 | -883.73 | +2,550.33 | +2,394.89 | +253.53 |
| `histories@shared_market_cap_assets__tabfm__late` | task | -2,293.09 | -3,076.33 | +2,030.05 | +264.88 | -1,324.23 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | state | -2,351.43 | -3,153.89 | +2,293.36 | +1,522.65 | -1,437.12 |
| `histories@shared_market_cap_assets__exaone__late` | task | -1,196.41 | -1,385.55 | +2,485.01 | -120.39 | -160.74 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | state | -3,239.80 | -4,585.73 | -635.54 | -1,686.53 | -2,480.86 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | state | -3,236.97 | -4,581.30 | -581.51 | -1,684.05 | -2,477.06 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | task | -1,604.21 | -1,891.20 | +3,378.71 | +1,885.42 | -680.49 |
| `histories@shared_income_assets__direct` | classical | +784.04 | +1,167.64 | +3,234.28 | +2,194.56 | +1,042.64 |
| `histories@shared_income_assets__mahalanobis_lw` | classical | -5,185.74 | -10,132.19 | -2,519.73 | -1,384.25 | -15,043.01 |
| `histories@shared_income_assets__euclidean` | classical | +1,290.95 | +924.25 | +2,987.79 | +724.12 | +1,309.83 |
| `histories@shared_income_assets__direct_no_indicators` | classical | +2,212.62 | +3,123.76 | +3,190.34 | +2,579.99 | +1,100.08 |
| `histories@shared_income_assets__euclidean_no_indicators` | classical | +1,290.95 | +924.25 | +2,987.79 | +724.12 | +1,309.83 |
| `histories@shared_income_assets__pca16` | control | +1,120.93 | +1,541.37 | +3,311.19 | +2,108.23 | +1,244.47 |
| `histories@shared_income_assets__autoencoder` | control | +806.45 | +935.68 | +2,979.46 | +1,333.15 | +1,323.35 |
| `histories@shared_income_assets__random_autoencoder` | control | -882.96 | -853.28 | +2,230.22 | +760.52 | -258.67 |
| `histories@shared_income_assets__supervised_mlp16` | task | +780.13 | +768.92 | +851.54 | -602.09 | +1,536.97 |
| `histories@shared_income_assets__tabpfn_fast__late` | task | -1,915.60 | -2,381.54 | +2,479.46 | +1,233.64 | -911.13 |
| `histories@shared_income_assets__tabpfn_full__late` | task | -1,074.25 | -1,192.32 | +2,137.11 | +657.88 | -38.73 |
| `histories@shared_income_assets__tabfm__early_concat` | state | -221.91 | -37.46 | +2,287.23 | +2,841.13 | +608.90 |
| `histories@shared_income_assets__tabfm__early_mean` | state | -211.68 | -24.36 | +2,294.20 | +2,845.07 | +617.19 |
| `histories@shared_income_assets__tabfm__late` | task | -2,477.95 | -3,358.60 | +1,562.47 | +1,268.25 | -1,547.79 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | state | -2,351.43 | -3,153.89 | +2,293.36 | +1,522.65 | -1,437.12 |
| `histories@shared_income_assets__exaone__late` | task | -1,772.02 | -2,223.43 | +2,667.40 | +701.80 | -756.43 |
| `histories@shared_income_assets__exaone__item_first_concat` | state | -3,239.80 | -4,585.73 | -635.54 | -1,686.53 | -2,480.86 |
| `histories@shared_income_assets__exaone__item_first_mean` | state | -3,236.97 | -4,581.30 | -581.51 | -1,684.05 | -2,477.06 |
| `histories@shared_income_assets__exaone__item_last_concat` | task | -2,224.40 | -2,899.75 | +1,961.40 | +2,365.32 | -1,309.83 |
| `histories@redraw1__mahalanobis_lw` | classical | -5,254.10 | -10,200.46 | -1,369.48 | -864.33 | -12,625.11 |
| `histories@redraw1__pca16` | control | +1,328.04 | +1,779.18 | +3,390.79 | +2,327.91 | +1,359.87 |
| `histories@redraw1__autoencoder` | control | +1,058.59 | +1,314.00 | +3,366.40 | +1,670.66 | +1,432.75 |
| `histories@redraw1__random_autoencoder` | control | -854.05 | -809.79 | +2,198.54 | +750.53 | -236.19 |
| `histories@redraw1__supervised_mlp16` | task | +59.91 | +67.14 | +205.69 | -1,061.81 | +1,119.95 |
| `histories@redraw1__tabpfn_fast__late` | task | -1,460.13 | -1,554.23 | +1,724.36 | +385.85 | -445.98 |
| `histories@redraw1__tabpfn_full__late` | task | -651.10 | -297.08 | +1,920.27 | +483.79 | +264.74 |
| `histories@redraw1__tabfm__early_concat` | state | -949.85 | -1,052.29 | +2,430.53 | +2,316.66 | +115.49 |
| `histories@redraw1__tabfm__early_mean` | state | -943.49 | -1,043.63 | +2,443.01 | +2,322.39 | +121.03 |
| `histories@redraw1__tabfm__late` | task | -2,311.94 | -3,088.22 | +1,980.59 | +278.40 | -1,323.21 |
| `histories@redraw1__tabfm__early_concat_labelnull` | state | -2,364.43 | -3,299.55 | +2,566.58 | +1,740.90 | -1,384.15 |
| `histories@redraw1__exaone__late` | task | -1,274.16 | -1,501.11 | +2,178.15 | -292.83 | -185.86 |
| `histories@redraw1__exaone__item_first_concat` | state | -3,239.85 | -4,585.54 | -255.22 | -1,397.93 | -2,481.00 |
| `histories@redraw1__exaone__item_first_mean` | state | -3,237.11 | -4,581.10 | -213.94 | -1,401.78 | -2,477.42 |
| `histories@redraw1__exaone__item_last_concat` | task | -1,668.63 | -1,942.59 | +3,228.58 | +1,454.69 | -704.20 |
| `histories@redraw2__mahalanobis_lw` | classical | -3,656.15 | -6,088.14 | +416.43 | -673.83 | -15,223.63 |
| `histories@redraw2__pca16` | control | +1,174.89 | +1,552.42 | +3,283.12 | +2,154.40 | +1,290.52 |
| `histories@redraw2__autoencoder` | control | +894.42 | +1,022.67 | +3,160.25 | +1,497.51 | +1,394.84 |
| `histories@redraw2__random_autoencoder` | control | -854.05 | -809.79 | +2,198.54 | +750.53 | -236.19 |
| `histories@redraw2__supervised_mlp16` | task | +46.02 | +79.78 | +402.38 | -1,010.03 | +1,182.05 |
| `histories@redraw2__tabpfn_fast__late` | task | -1,462.68 | -1,516.86 | +1,898.27 | +488.30 | -446.74 |
| `histories@redraw2__tabpfn_full__late` | task | -518.77 | -88.81 | +2,330.96 | +755.99 | +329.63 |
| `histories@redraw2__tabfm__early_concat` | state | -891.42 | -952.59 | +2,214.53 | +2,066.63 | +68.89 |
| `histories@redraw2__tabfm__early_mean` | state | -887.92 | -949.93 | +2,211.18 | +2,054.99 | +71.75 |
| `histories@redraw2__tabfm__late` | task | -2,369.32 | -3,123.47 | +1,783.14 | +114.75 | -1,408.69 |
| `histories@redraw2__tabfm__early_concat_labelnull` | state | -2,404.42 | -3,328.68 | +2,461.11 | +1,471.98 | -1,454.88 |
| `histories@redraw2__exaone__late` | task | -1,392.60 | -1,558.02 | +2,351.91 | -207.66 | -339.39 |
| `histories@redraw2__exaone__item_first_concat` | state | -3,240.60 | -4,586.36 | -459.43 | -1,507.59 | -2,481.99 |
| `histories@redraw2__exaone__item_first_mean` | state | -3,238.57 | -4,582.80 | -518.63 | -1,580.09 | -2,479.36 |
| `histories@redraw2__exaone__item_last_concat` | task | -1,658.94 | -1,957.09 | +3,274.14 | +1,422.54 | -751.28 |
| `histories@shared_both__supervised_mlp16` | task | +937.29 | +1,133.52 | +1,106.60 | -258.44 | +1,829.94 |
| `histories@shared_both__tabpfn_fast__late` | task | -1,647.82 | -1,900.18 | +2,102.71 | +938.10 | -644.72 |
| `histories@shared_both__tabpfn_full__late` | task | -792.27 | -665.13 | +2,146.20 | +852.10 | +128.08 |
| `histories@shared_both__tabfm__early_concat` | state | -494.38 | -444.90 | +2,372.77 | +2,708.52 | +443.24 |
| `histories@shared_both__tabfm__early_mean` | state | -483.98 | -431.82 | +2,385.09 | +2,716.51 | +452.17 |
| `histories@shared_both__tabfm__late` | task | -2,377.70 | -3,206.72 | +1,845.14 | +752.99 | -1,423.20 |
| `histories@shared_both__exaone__late` | task | -1,437.80 | -1,731.44 | +2,641.38 | +244.64 | -396.59 |
| `histories@shared_both__exaone__item_last_concat` | task | -1,884.09 | -2,346.17 | +2,854.38 | +2,187.40 | -954.27 |
| `h3__fernandez_market_cap_assets` | fernandez | -2,106.30 | -5,356.71 | -5,356.71 | -3,590.96 | -2,159.10 |
| `h3__fernandez_market_to_book` | fernandez | -2,294.23 | -5,334.64 | -5,282.49 | -3,708.46 | -2,472.82 |
| `h3__fernandez_dividend_yield` | fernandez | -2,411.17 | -4,449.07 | -4,503.31 | -3,286.53 | -2,006.15 |
| `h3__fernandez_joint` | fernandez | -1,136.54 | -2,535.10 | -2,590.42 | -2,663.92 | -654.53 |
| `h3__histories__direct` | classical | +686.62 | +987.29 | +2,987.03 | +1,540.46 | +1,162.35 |
| `h3__histories__mahalanobis_lw` | classical | -3,975.10 | -7,900.40 | -6,425.60 | -2,028.62 | -8,483.67 |
| `h3__histories__euclidean` | classical | +241.78 | -705.34 | -109.29 | +215.84 | +1,732.56 |
| `h3__histories__direct_no_indicators` | classical | +1,209.70 | +1,675.16 | +2,952.69 | +1,648.78 | +1,421.03 |
| `h3__histories__euclidean_no_indicators` | classical | +241.78 | -705.34 | -109.29 | +215.84 | +1,732.56 |
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
| `covariance_exposures` | -4,414.38 | [-7,984.2, -2,415.0] | [-8,347.4, -2,208.3] | 49.7 |
| `fernandez_market_cap_assets` | -322.86 | [-805.0, -4.4] | [-930.1, +48.7] | 50.2 |
| `fernandez_market_to_book` | -1,778.48 | [-3,625.9, -688.2] | [-3,926.0, -558.4] | 53.7 |
| `fernandez_dividend_yield` | -834.81 | [-1,837.7, -250.2] | [-1,973.8, -161.9] | 42.3 |
| `histories@decoded__direct` | -4,579.72 | [-8,284.0, -2,505.9] | [-8,660.3, -2,291.0] | 49.7 |
| `histories@decoded__pca16` | -4,579.06 | [-8,280.9, -2,506.9] | [-8,656.6, -2,292.0] | 49.7 |
| `histories@decoded__autoencoder` | -4,574.23 | [-8,271.0, -2,504.9] | [-8,647.5, -2,290.4] | 49.7 |
| `histories@decoded__random_autoencoder` | -4,574.35 | [-8,270.5, -2,505.3] | [-8,647.1, -2,290.6] | 49.7 |
| `histories@decoded__supervised_mlp16` | -4,578.59 | [-8,280.6, -2,506.5] | [-8,656.9, -2,291.4] | 49.7 |
| `histories@decoded__tabpfn_fast__late` | -4,540.59 | [-8,209.5, -2,486.5] | [-8,584.0, -2,274.0] | 49.7 |
| `histories@decoded__tabpfn_full__late` | -4,541.27 | [-8,211.3, -2,486.1] | [-8,586.8, -2,273.6] | 49.7 |
| `histories@decoded__tabfm__early_concat` | -4,551.63 | [-8,229.8, -2,492.3] | [-8,605.0, -2,278.8] | 49.7 |
| `histories@decoded__tabfm__early_mean` | -4,551.46 | [-8,229.6, -2,492.1] | [-8,604.8, -2,278.6] | 49.7 |
| `histories@decoded__tabfm__late` | -4,541.01 | [-8,209.9, -2,486.9] | [-8,584.2, -2,274.0] | 49.7 |
| `histories@decoded__tabfm__early_concat_labelnull` | -4,559.69 | [-8,244.4, -2,497.2] | [-8,619.5, -2,283.1] | 49.7 |
| `histories@decoded__exaone__late` | -4,541.87 | [-8,211.7, -2,487.4] | [-8,586.6, -2,274.5] | 49.7 |
| `histories@decoded__exaone__item_first_concat` | -4,597.89 | [-8,325.7, -2,511.8] | [-8,700.3, -2,295.9] | 49.7 |
| `histories@decoded__exaone__item_first_mean` | -4,582.92 | [-8,290.9, -2,507.7] | [-8,666.2, -2,292.1] | 49.7 |
| `histories@decoded__exaone__item_last_concat` | -4,537.35 | [-8,203.9, -2,484.5] | [-8,579.0, -2,271.9] | 49.7 |
| `histories__direct` | +1,216.98 | [+363.1, +2,412.5] | [+156.5, +2,802.8] | 63.3 |
| `histories__mahalanobis_lw` | -10,613.60 | [-21,995.4, -3,855.5] | [-24,070.8, -2,743.0] | 54.0 |
| `histories__euclidean` | +861.37 | [-496.7, +1,796.3] | [-497.8, +1,836.6] | 34.8 |
| `histories__direct_no_indicators` | +3,155.91 | [+1,406.6, +5,906.1] | [+1,082.1, +6,535.8] | 58.4 |
| `histories__euclidean_no_indicators` | +861.37 | [-496.7, +1,796.3] | [-497.8, +1,836.6] | 34.8 |
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
| `broad__euclidean` | +1,330.91 | [-15,169.4, +11,602.3] | [-18,061.4, +13,270.1] | 52.6 |
| `broad__direct_no_indicators` | -2,188.71 | [-3,999.8, -1,146.4] | [-4,142.2, -1,046.5] | 47.9 |
| `broad__euclidean_no_indicators` | +1,331.50 | [-7,333.4, +6,650.3] | [-8,925.9, +7,623.2] | 53.9 |
| `broad__direct_no_size` | -888.16 | [-1,534.7, -421.3] | [-1,528.7, -383.8] | 40.5 |
| `broad__euclidean_no_size` | +1,260.60 | [-15,506.5, +11,588.0] | [-18,211.6, +13,128.5] | 52.3 |
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
| `metrics__euclidean` | -1,958.41 | [-17,958.5, +7,534.3] | [-20,226.3, +9,059.5] | 48.6 |
| `metrics__direct_no_indicators` | +1,232.41 | [+393.3, +2,418.6] | [+145.0, +2,750.4] | 58.8 |
| `metrics__euclidean_no_indicators` | +12,445.64 | [+5,750.6, +17,402.3] | [+5,119.8, +18,249.4] | 8.1 |
| `metrics__direct_no_size` | +675.40 | [+20.0, +1,557.0] | [-189.9, +1,864.1] | 62.8 |
| `metrics__euclidean_no_size` | -2,101.43 | [-18,057.2, +7,211.7] | [-19,954.1, +8,631.5] | 39.6 |
| `metrics__direct_no_changes` | +975.50 | [+220.1, +2,038.4] | [+1.4, +2,357.3] | 61.2 |
| `metrics__euclidean_no_changes` | +2,233.88 | [-11,509.5, +10,686.3] | [-13,033.4, +11,988.5] | 37.1 |
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
| `histories@income_assets__euclidean` | +1,050.89 | [+72.0, +1,822.5] | [+138.3, +1,829.0] | 58.8 |
| `histories@income_assets__direct_no_indicators` | +3,001.23 | [+1,334.2, +5,611.1] | [+1,019.5, +6,227.1] | 58.8 |
| `histories@income_assets__euclidean_no_indicators` | +1,050.89 | [+72.0, +1,822.5] | [+138.3, +1,829.0] | 58.8 |
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
| `histories@shared_market_cap_assets__direct` | +1,167.64 | [+329.3, +2,331.7] | [+121.3, +2,732.6] | 63.8 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | -10,132.19 | [-20,845.2, -3,746.1] | [-22,836.7, -2,645.1] | 54.2 |
| `histories@shared_market_cap_assets__euclidean` | +924.25 | [-261.5, +1,778.6] | [-238.1, +1,816.0] | 39.9 |
| `histories@shared_market_cap_assets__direct_no_indicators` | +3,123.76 | [+1,366.2, +5,885.0] | [+1,035.4, +6,526.9] | 58.6 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | +924.25 | [-261.5, +1,778.6] | [-238.1, +1,816.0] | 39.9 |
| `histories@shared_market_cap_assets__pca16` | +1,541.37 | [+501.3, +3,036.7] | [+237.5, +3,511.9] | 63.3 |
| `histories@shared_market_cap_assets__autoencoder` | +935.68 | [+246.3, +1,838.2] | [+53.5, +2,200.5] | 14.1 |
| `histories@shared_market_cap_assets__random_autoencoder` | -853.28 | [-1,276.1, -419.8] | [-1,294.5, -330.2] | 37.1 |
| `histories@shared_market_cap_assets__supervised_mlp16` | -34.91 | [-940.6, +1,147.5] | [-1,119.0, +1,489.7] | 20.2 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | -1,519.35 | [-2,685.6, -745.1] | [-2,685.5, -688.5] | 37.9 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | -250.17 | [-805.9, +407.5] | [-860.7, +553.8] | 36.8 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | -896.41 | [-1,596.5, -329.9] | [-1,564.1, -283.9] | 34.3 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | -883.73 | [-1,576.6, -319.7] | [-1,543.3, -270.5] | 34.2 |
| `histories@shared_market_cap_assets__tabfm__late` | -3,076.33 | [-5,469.1, -1,727.5] | [-5,630.4, -1,607.6] | 44.8 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | -3,153.89 | [-5,531.2, -1,807.0] | [-5,710.7, -1,692.8] | 46.5 |
| `histories@shared_market_cap_assets__exaone__late` | -1,385.55 | [-2,492.8, -539.8] | [-2,456.9, -471.7] | 37.0 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | -4,585.73 | [-8,294.4, -2,509.7] | [-8,671.2, -2,294.5] | 49.7 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | -4,581.30 | [-8,284.4, -2,508.0] | [-8,662.1, -2,293.1] | 49.7 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | -1,891.20 | [-3,355.3, -985.3] | [-3,403.2, -913.1] | 42.0 |
| `histories@shared_income_assets__direct` | +1,167.64 | [+329.3, +2,331.7] | [+121.3, +2,732.6] | 63.8 |
| `histories@shared_income_assets__mahalanobis_lw` | -10,132.19 | [-20,845.2, -3,746.1] | [-22,836.7, -2,645.1] | 54.2 |
| `histories@shared_income_assets__euclidean` | +924.25 | [-261.5, +1,778.6] | [-238.1, +1,816.0] | 39.9 |
| `histories@shared_income_assets__direct_no_indicators` | +3,123.76 | [+1,366.2, +5,885.0] | [+1,035.4, +6,526.9] | 58.6 |
| `histories@shared_income_assets__euclidean_no_indicators` | +924.25 | [-261.5, +1,778.6] | [-238.1, +1,816.0] | 39.9 |
| `histories@shared_income_assets__pca16` | +1,541.37 | [+501.3, +3,036.7] | [+237.5, +3,511.9] | 63.3 |
| `histories@shared_income_assets__autoencoder` | +935.68 | [+246.3, +1,838.2] | [+53.5, +2,200.5] | 14.1 |
| `histories@shared_income_assets__random_autoencoder` | -853.28 | [-1,276.1, -419.8] | [-1,294.5, -330.2] | 37.1 |
| `histories@shared_income_assets__supervised_mlp16` | +768.92 | [+63.0, +1,657.6] | [-153.4, +2,022.7] | 12.0 |
| `histories@shared_income_assets__tabpfn_fast__late` | -2,381.54 | [-4,185.5, -1,322.2] | [-4,255.4, -1,234.5] | 43.7 |
| `histories@shared_income_assets__tabpfn_full__late` | -1,192.32 | [-2,188.0, -487.2] | [-2,158.6, -433.9] | 38.0 |
| `histories@shared_income_assets__tabfm__early_concat` | -37.46 | [-453.8, +483.8] | [-560.5, +663.5] | 5.2 |
| `histories@shared_income_assets__tabfm__early_mean` | -24.36 | [-442.5, +497.1] | [-552.3, +682.5] | 5.1 |
| `histories@shared_income_assets__tabfm__late` | -3,358.60 | [-5,985.3, -1,883.4] | [-6,180.5, -1,751.2] | 47.0 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | -3,153.89 | [-5,531.2, -1,807.0] | [-5,710.7, -1,692.8] | 46.5 |
| `histories@shared_income_assets__exaone__late` | -2,223.43 | [-3,910.9, -1,202.7] | [-3,942.1, -1,134.7] | 41.3 |
| `histories@shared_income_assets__exaone__item_first_concat` | -4,585.73 | [-8,294.4, -2,509.7] | [-8,671.2, -2,294.5] | 49.7 |
| `histories@shared_income_assets__exaone__item_first_mean` | -4,581.30 | [-8,284.4, -2,508.0] | [-8,662.1, -2,293.1] | 49.7 |
| `histories@shared_income_assets__exaone__item_last_concat` | -2,899.75 | [-5,177.7, -1,607.0] | [-5,336.2, -1,489.7] | 46.8 |
| `histories@redraw1__mahalanobis_lw` | -10,200.46 | [-21,431.0, -3,677.3] | [-23,155.9, -2,700.3] | 52.2 |
| `histories@redraw1__pca16` | +1,779.18 | [+767.7, +3,254.4] | [+538.5, +3,668.5] | 62.4 |
| `histories@redraw1__autoencoder` | +1,314.00 | [+429.7, +2,543.2] | [+206.4, +2,953.5] | 43.1 |
| `histories@redraw1__random_autoencoder` | -809.79 | [-1,210.4, -387.9] | [-1,237.1, -299.3] | 35.5 |
| `histories@redraw1__supervised_mlp16` | +67.14 | [-829.6, +1,274.4] | [-1,041.5, +1,639.0] | 22.2 |
| `histories@redraw1__tabpfn_fast__late` | -1,554.23 | [-2,777.3, -757.7] | [-2,780.2, -697.5] | 38.4 |
| `histories@redraw1__tabpfn_full__late` | -297.08 | [-896.8, +357.7] | [-909.1, +468.1] | 36.5 |
| `histories@redraw1__tabfm__early_concat` | -1,052.29 | [-1,853.7, -454.0] | [-1,818.3, -402.7] | 35.5 |
| `histories@redraw1__tabfm__early_mean` | -1,043.63 | [-1,840.7, -447.1] | [-1,803.2, -396.3] | 35.4 |
| `histories@redraw1__tabfm__late` | -3,088.22 | [-5,485.5, -1,731.1] | [-5,650.5, -1,610.7] | 44.7 |
| `histories@redraw1__tabfm__early_concat_labelnull` | -3,299.55 | [-5,875.0, -1,853.5] | [-6,061.2, -1,728.6] | 46.0 |
| `histories@redraw1__exaone__late` | -1,501.11 | [-2,748.5, -624.7] | [-2,709.8, -554.8] | 37.4 |
| `histories@redraw1__exaone__item_first_concat` | -4,585.54 | [-8,294.0, -2,509.7] | [-8,670.7, -2,294.5] | 49.7 |
| `histories@redraw1__exaone__item_first_mean` | -4,581.10 | [-8,284.0, -2,508.1] | [-8,661.6, -2,293.2] | 49.7 |
| `histories@redraw1__exaone__item_last_concat` | -1,942.59 | [-3,490.3, -1,007.8] | [-3,551.0, -931.1] | 42.2 |
| `histories@redraw2__mahalanobis_lw` | -6,088.14 | [-12,856.0, -2,098.8] | [-13,984.4, -1,345.8] | 51.0 |
| `histories@redraw2__pca16` | +1,552.42 | [+623.2, +2,882.9] | [+403.0, +3,288.6] | 62.7 |
| `histories@redraw2__autoencoder` | +1,022.67 | [+265.0, +2,021.7] | [+64.5, +2,403.0] | 3.2 |
| `histories@redraw2__random_autoencoder` | -809.79 | [-1,210.4, -387.9] | [-1,237.1, -299.3] | 35.5 |
| `histories@redraw2__supervised_mlp16` | +79.78 | [-815.5, +1,249.1] | [-1,020.9, +1,638.1] | 11.2 |
| `histories@redraw2__tabpfn_fast__late` | -1,516.86 | [-2,657.7, -753.9] | [-2,645.7, -693.8] | 38.8 |
| `histories@redraw2__tabpfn_full__late` | -88.81 | [-650.3, +612.6] | [-766.0, +830.4] | 43.5 |
| `histories@redraw2__tabfm__early_concat` | -952.59 | [-1,641.1, -411.4] | [-1,619.2, -360.0] | 36.1 |
| `histories@redraw2__tabfm__early_mean` | -949.93 | [-1,640.6, -408.4] | [-1,616.4, -357.0] | 36.0 |
| `histories@redraw2__tabfm__late` | -3,123.47 | [-5,502.2, -1,776.5] | [-5,678.6, -1,655.7] | 45.5 |
| `histories@redraw2__tabfm__early_concat_labelnull` | -3,328.68 | [-5,939.0, -1,861.6] | [-6,129.3, -1,733.4] | 46.5 |
| `histories@redraw2__exaone__late` | -1,558.02 | [-2,717.9, -745.4] | [-2,679.4, -679.4] | 37.7 |
| `histories@redraw2__exaone__item_first_concat` | -4,586.36 | [-8,296.1, -2,509.9] | [-8,672.4, -2,294.7] | 49.7 |
| `histories@redraw2__exaone__item_first_mean` | -4,582.80 | [-8,288.4, -2,508.4] | [-8,665.3, -2,293.5] | 49.7 |
| `histories@redraw2__exaone__item_last_concat` | -1,957.09 | [-3,440.6, -1,058.7] | [-3,493.9, -983.6] | 42.7 |
| `histories@shared_both__supervised_mlp16` | +1,133.52 | [+123.7, +2,443.4] | [-163.7, +2,992.1] | 6.3 |
| `histories@shared_both__tabpfn_fast__late` | -1,900.18 | [-3,341.3, -1,009.8] | [-3,365.1, -944.0] | 41.0 |
| `histories@shared_both__tabpfn_full__late` | -665.13 | [-1,341.6, -41.2] | [-1,312.4, +38.8] | 35.9 |
| `histories@shared_both__tabfm__early_concat` | -444.90 | [-907.0, +40.2] | [-906.7, +136.2] | 35.1 |
| `histories@shared_both__tabfm__early_mean` | -431.82 | [-889.1, +55.4] | [-894.0, +148.9] | 35.2 |
| `histories@shared_both__tabfm__late` | -3,206.72 | [-5,710.5, -1,797.8] | [-5,898.2, -1,673.6] | 45.9 |
| `histories@shared_both__exaone__late` | -1,731.44 | [-3,070.2, -842.5] | [-3,055.8, -781.5] | 38.2 |
| `histories@shared_both__exaone__item_last_concat` | -2,346.17 | [-4,171.4, -1,282.1] | [-4,256.9, -1,183.6] | 44.4 |
| `h3__fernandez_market_cap_assets` | -5,356.71 | [-11,510.4, -1,723.3] | [-12,489.1, -1,184.3] | 53.3 |
| `h3__fernandez_market_to_book` | -5,334.64 | [-11,441.1, -1,863.4] | [-12,267.9, -1,394.4] | 50.7 |
| `h3__fernandez_dividend_yield` | -4,449.07 | [-9,415.9, -1,493.6] | [-10,235.7, -962.8] | 53.8 |
| `h3__fernandez_joint` | -2,535.10 | [-5,800.5, -603.0] | [-6,317.1, -281.8] | 52.2 |
| `h3__histories__direct` | +987.29 | [+146.4, +2,091.7] | [-111.9, +2,540.1] | 45.0 |
| `h3__histories__mahalanobis_lw` | -7,900.40 | [-16,791.5, -2,771.0] | [-18,094.0, -2,084.1] | 52.8 |
| `h3__histories__euclidean` | -705.34 | [-2,359.5, +405.7] | [-2,320.8, +523.4] | 5.3 |
| `h3__histories__direct_no_indicators` | +1,675.16 | [+580.8, +3,225.2] | [+285.6, +3,717.4] | 63.7 |
| `h3__histories__euclidean_no_indicators` | -705.34 | [-2,359.5, +405.7] | [-2,320.8, +523.4] | 5.3 |
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
| support redraw | `histories@redraw1__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +23.0 | [-107.5, +205.0] | +125 | -26 | -21 | -6 | +8 | -58 |
| support redraw | `histories@redraw2__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | -227.0 | [-461.4, -77.1] | -164 | -21 | -43 | -11 | +21 | -10 |
| both targets vs one | `histories@shared_both__tabfm__early_concat` | `histories@shared_market_cap_assets__tabfm__early_concat` | matched/diagonal | +325.6 | [+146.4, +637.2] | +183 | +24 | +3 | +46 | +6 | +63 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +407.3 | [-416.8, +1,074.6] | -531 | +223 | +248 | +97 | +44 | +327 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +3,197.2 | [+2,033.6, +5,126.0] | +1,349 | +317 | +399 | +260 | +201 | +672 |
| support redraw | `histories@redraw1__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/diagonal | -232.9 | [-478.0, -74.1] | -181 | -22 | +32 | -0 | -23 | -39 |
| support redraw | `histories@redraw2__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/diagonal | +39.3 | [-50.7, +176.5] | +99 | -17 | -9 | -8 | +1 | -26 |
| both targets vs one | `histories@shared_both__tabpfn_full__late` | `histories@shared_market_cap_assets__tabpfn_full__late` | matched/diagonal | +203.0 | [+135.8, +280.9] | +32 | +46 | +16 | +32 | +23 | +54 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/diagonal | +2,674.0 | [+1,602.4, +4,002.6] | +375 | +443 | +564 | +381 | +219 | +692 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +3,887.0 | [+2,696.2, +5,865.3] | +1,457 | +364 | +544 | +378 | +351 | +793 |
| support redraw | `histories@redraw1__exaone__late` | `histories__exaone__late` | matched/diagonal | -143.7 | [-283.8, -47.1] | -118 | -7 | +11 | -13 | -7 | -10 |
| support redraw | `histories@redraw2__exaone__late` | `histories__exaone__late` | matched/diagonal | -58.6 | [-91.9, -26.8] | -16 | +4 | -6 | -23 | -3 | -14 |
| both targets vs one | `histories@shared_both__exaone__late` | `histories@shared_market_cap_assets__exaone__late` | matched/diagonal | +365.0 | [+227.2, +592.7] | +129 | +33 | +22 | +52 | +41 | +87 |
| decoded vs native | `histories@decoded__exaone__late` | `histories__exaone__late` | matched/diagonal | +3,600.5 | [+2,142.2, +5,696.3] | +855 | +546 | +632 | +384 | +280 | +904 |
| decoded vs decoded inputs | `histories@decoded__exaone__late` | `histories@decoded__direct` | matched/diagonal | +3,947.6 | [+2,595.5, +6,172.1] | +1,597 | +383 | +511 | +310 | +316 | +831 |
| support redraw | `histories@redraw1__supervised_mlp16` | `histories__supervised_mlp16` | matched/diagonal | +71.3 | [-29.8, +212.9] | +89 | +18 | -25 | -7 | +15 | -19 |
| support redraw | `histories@redraw2__supervised_mlp16` | `histories__supervised_mlp16` | matched/diagonal | +123.1 | [+13.1, +258.2] | +112 | +19 | -41 | +22 | +11 | +0 |
| both targets vs one | `histories@shared_both__supervised_mlp16` | `histories@shared_market_cap_assets__supervised_mlp16` | matched/diagonal | +846.9 | [+525.3, +1,387.2] | +358 | +63 | +69 | +70 | +82 | +204 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/diagonal | -243.6 | [-1,188.6, +454.2] | -775 | +249 | +85 | +75 | +13 | +111 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/diagonal | -880.5 | [-1,593.5, -447.6] | -439 | -16 | -130 | -108 | -67 | -121 |
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
| support redraw | `histories@redraw1__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | -131.7 | [-209.7, -71.8] | -30 | -28 | -21 | -13 | +5 | -45 |
| support redraw | `histories@redraw2__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | -255.4 | [-536.9, -76.1] | -207 | -14 | -39 | -5 | +14 | -5 |
| both targets vs one | `histories@shared_both__tabfm__early_concat` | `histories@shared_market_cap_assets__tabfm__early_concat` | matched/correlation | -130.3 | [-483.5, +116.8] | -277 | +41 | +2 | +53 | +6 | +44 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | -2,730.8 | [-7,349.4, +307.2] | -3,578 | +330 | +205 | +185 | -44 | +172 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -471.2 | [-3,959.7, +1,833.7] | -2,346 | +472 | +359 | +388 | +180 | +474 |
| support redraw | `histories@redraw1__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/correlation | -20.9 | [-85.5, +58.9] | +39 | -25 | +26 | -20 | -14 | -26 |
| support redraw | `histories@redraw2__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/correlation | +91.4 | [-24.8, +272.6] | +135 | -12 | -4 | -10 | +2 | -19 |
| both targets vs one | `histories@shared_both__tabpfn_full__late` | `histories@shared_market_cap_assets__tabpfn_full__late` | matched/correlation | +274.8 | [+156.2, +470.6] | +123 | +40 | +8 | +36 | +19 | +50 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/correlation | -1,652.0 | [-6,594.5, +1,724.8] | -3,727 | +612 | +472 | +484 | +65 | +443 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -627.9 | [-5,112.0, +2,295.3] | -3,023 | +558 | +480 | +527 | +278 | +553 |
| support redraw | `histories@redraw1__exaone__late` | `histories__exaone__late` | matched/correlation | -58.1 | [-92.2, -20.4] | -13 | -11 | +5 | -23 | -6 | -11 |
| support redraw | `histories@redraw2__exaone__late` | `histories__exaone__late` | matched/correlation | +3.9 | [-40.7, +66.0] | +28 | +2 | -1 | -13 | -1 | -12 |
| both targets vs one | `histories@shared_both__exaone__late` | `histories@shared_market_cap_assets__exaone__late` | matched/correlation | +176.6 | [+80.3, +266.2] | -25 | +36 | +17 | +45 | +33 | +71 |
| decoded vs native | `histories@decoded__exaone__late` | `histories__exaone__late` | matched/correlation | -1,255.7 | [-6,247.1, +2,208.1] | -3,770 | +723 | +543 | +529 | +114 | +606 |
| decoded vs decoded inputs | `histories@decoded__exaone__late` | `histories@decoded__direct` | matched/correlation | -303.4 | [-4,212.6, +2,278.3] | -2,621 | +556 | +455 | +447 | +266 | +594 |
| support redraw | `histories@redraw1__supervised_mlp16` | `histories__supervised_mlp16` | matched/correlation | +71.5 | [-42.8, +239.5] | +110 | +4 | -28 | -14 | +11 | -12 |
| support redraw | `histories@redraw2__supervised_mlp16` | `histories__supervised_mlp16` | matched/correlation | +133.6 | [+11.6, +297.3] | +131 | +15 | -42 | +17 | +10 | +2 |
| both targets vs one | `histories@shared_both__supervised_mlp16` | `histories@shared_market_cap_assets__supervised_mlp16` | matched/correlation | +635.6 | [+396.6, +1,002.1] | +196 | +85 | +56 | +85 | +51 | +163 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/correlation | -348.5 | [-1,218.2, +316.6] | -756 | +217 | +60 | +84 | -6 | +53 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/correlation | +89.3 | [-325.9, +613.9] | +408 | -57 | -114 | -106 | +49 | -92 |
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
| support redraw | `histories@redraw1__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +142.0 | [+28.6, +302.9] | +146 | +2 | -10 | +7 | +6 | -10 |
| support redraw | `histories@redraw2__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | -74.0 | [-199.8, +10.6] | -66 | -12 | -6 | -9 | +9 | +11 |
| both targets vs one | `histories@shared_both__tabfm__early_concat` | `histories@shared_market_cap_assets__tabfm__early_concat` | median/diagonal | -159.9 | [-227.9, -105.0] | -73 | -11 | -46 | -7 | -11 | -13 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +1,238.9 | [+324.9, +2,014.7] | -387 | +367 | +453 | +243 | +96 | +467 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +3,422.2 | [+1,879.1, +5,889.3] | +1,959 | +142 | +254 | +249 | +179 | +639 |
| support redraw | `histories@redraw1__tabpfn_full__late` | `histories__tabpfn_full__late` | median/diagonal | -191.5 | [-395.6, -55.6] | -159 | -6 | +20 | -12 | -30 | -5 |
| support redraw | `histories@redraw2__tabpfn_full__late` | `histories__tabpfn_full__late` | median/diagonal | +219.2 | [+49.9, +484.9] | +213 | -5 | +5 | +4 | +6 | -4 |
| both targets vs one | `histories@shared_both__tabpfn_full__late` | `histories@shared_market_cap_assets__tabpfn_full__late` | median/diagonal | +98.8 | [+8.2, +195.6] | +0 | +47 | -2 | +9 | -3 | +47 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | median/diagonal | +2,362.0 | [+1,225.9, +3,552.9] | -1 | +444 | +558 | +407 | +238 | +716 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +4,368.6 | [+2,618.2, +7,162.1] | +2,256 | +144 | +343 | +391 | +409 | +825 |
| support redraw | `histories@redraw1__exaone__late` | `histories__exaone__late` | median/diagonal | -227.2 | [-464.6, -61.8] | -199 | -11 | +26 | -27 | -15 | -1 |
| support redraw | `histories@redraw2__exaone__late` | `histories__exaone__late` | median/diagonal | -53.4 | [-115.8, +6.5] | -15 | +9 | +13 | -29 | -12 | -20 |
| both targets vs one | `histories@shared_both__exaone__late` | `histories@shared_market_cap_assets__exaone__late` | median/diagonal | +156.4 | [-25.4, +399.7] | +37 | +24 | -20 | +23 | +16 | +77 |
| decoded vs native | `histories@decoded__exaone__late` | `histories__exaone__late` | median/diagonal | +1,973.5 | [+511.6, +3,468.5] | -250 | +465 | +498 | +324 | +184 | +753 |
| decoded vs decoded inputs | `histories@decoded__exaone__late` | `histories@decoded__direct` | median/diagonal | +4,273.6 | [+2,506.4, +7,090.6] | +2,231 | +196 | +322 | +353 | +345 | +827 |
| support redraw | `histories@redraw1__supervised_mlp16` | `histories__supervised_mlp16` | median/diagonal | +265.3 | [+83.8, +479.6] | +93 | +67 | -45 | +1 | +129 | +20 |
| support redraw | `histories@redraw2__supervised_mlp16` | `histories__supervised_mlp16` | median/diagonal | +462.0 | [+208.0, +783.4] | +239 | +63 | -71 | +63 | +133 | +36 |
| both targets vs one | `histories@shared_both__supervised_mlp16` | `histories@shared_market_cap_assets__supervised_mlp16` | median/diagonal | +1,269.4 | [+554.4, +2,334.1] | +395 | +106 | +2 | +66 | +252 | +450 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | median/diagonal | -1,235.6 | [-3,449.0, +354.9] | -1,953 | +375 | +110 | +47 | +100 | +86 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | median/diagonal | -1,400.4 | [-2,529.5, -633.6] | -482 | -110 | -233 | -153 | -100 | -322 |

## Where the residual likelihood comes from

Exact split of the held-out spatial-error log-likelihood of factor residuals at the
frozen coefficient and prior-window variances (Lean `Likelihood.spatial_loss`),
summed over 2020-2025, minus the uniform network's parts. `alignment` is the term
linear in lambda (covariance between a firm and its neighbours); the two
`concentration` terms are quadratic, split into the neighbours' own variances
weighted by squared weights (the Herfindahl noise cost) and their cross products.
This is the residual model only; the reported held-out scores add the factor
covariance. `H` is the mean row Herfindahl index.

### exp kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.707 | -782 | +2,145,743 | -549,849 | +42,398 | -815 | -13,101 | +1,623,593 | 0.0023 |
| `fernandez_joint` | 0.776 | -360 | +3,791 | -6,242 | +10,899 | -268 | -3,053 | +4,767 | 0.0026 |
| `covariance_exposures` | 0.710 | -12 | +154 | -254 | +426 | -5 | -145 | +164 | 0.0023 |
| `histories__direct` | 0.793 | -428 | +3,116 | -7,402 | +13,559 | -281 | -4,269 | +4,294 | 0.0026 |
| `histories__supervised_mlp16` | 0.752 | -343 | +1,689 | -4,521 | +8,617 | -403 | -2,885 | +2,154 | 0.0031 |
| `histories__tabfm__early_concat` | 0.757 | -217 | +1,978 | -4,440 | +8,343 | -144 | -2,779 | +2,740 | 0.0024 |
| `histories__tabfm__early_concat_labelnull` | 0.724 | -67 | +577 | -1,186 | +2,321 | -43 | -797 | +806 | 0.0024 |
| `histories__tabpfn_full__late` | 0.764 | -265 | +2,055 | -4,100 | +9,043 | -221 | -3,437 | +3,075 | 0.0025 |
| `histories__exaone__late` | 0.744 | -164 | +1,331 | -2,715 | +6,240 | -150 | -2,549 | +1,992 | 0.0025 |
| `histories@decoded__direct` | 0.707 | -1 | +10 | -18 | +25 | -0 | -5 | +11 | 0.0023 |
| `histories@decoded__tabfm__early_concat` | 0.708 | -3 | +27 | -51 | +92 | -1 | -28 | +36 | 0.0023 |

### matched kernel, diagonal innovations

| Approach | lambda | spectrum | variance | baseline | alignment | concentration_own | concentration_cross | Total | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `uniform_network` | 0.707 | -782 | +2,145,743 | -549,849 | +42,398 | -815 | -13,101 | +1,623,593 | 0.0023 |
| `fernandez_joint` | 0.776 | -360 | +3,791 | -6,242 | +10,899 | -268 | -3,053 | +4,767 | 0.0026 |
| `covariance_exposures` | 0.894 | -1,292 | +15,864 | -32,733 | +48,811 | -527 | -13,823 | +16,299 | 0.0026 |
| `histories__direct` | 0.804 | -514 | +3,669 | -8,500 | +15,628 | -341 | -4,977 | +4,965 | 0.0026 |
| `histories__supervised_mlp16` | 0.746 | -207 | +1,185 | -2,958 | +5,983 | -214 | -2,225 | +1,564 | 0.0026 |
| `histories__tabfm__early_concat` | 0.796 | -462 | +4,323 | -9,230 | +16,800 | -324 | -5,415 | +5,692 | 0.0026 |
| `histories__tabfm__early_concat_labelnull` | 0.781 | -374 | +3,432 | -7,111 | +13,022 | -281 | -4,131 | +4,557 | 0.0026 |
| `histories__tabpfn_full__late` | 0.772 | -329 | +2,930 | -5,446 | +11,435 | -295 | -4,104 | +4,190 | 0.0026 |
| `histories__exaone__late` | 0.755 | -242 | +2,216 | -4,204 | +9,070 | -243 | -3,484 | +3,114 | 0.0026 |
| `histories@decoded__direct` | 0.783 | -377 | +3,196 | -6,948 | +11,133 | -344 | -2,576 | +4,084 | 0.0029 |
| `histories@decoded__tabfm__early_concat` | 0.834 | -715 | +6,383 | -14,385 | +23,470 | -390 | -6,385 | +7,979 | 0.0026 |

The uniform row shows its own parts; every other row is its difference from it.

## Measurement variants

Held-out gains over the joint network (exp kernel) for the history rung: the native
readout, two re-encodings on differently salted 256-row supports, the two support
targets on shared rows and their combination (RMS of the two distances), and
networks built from exposures decoded out of the same states (see `decoding.py`).

### exp kernel, diagonal innovations

| Representation | native | redraw 1 | redraw 2 | shared cap/assets | shared income/assets | both shared | decoded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct` | +1,217.0 | — | — | +1,167.6 | +1,167.6 | — | -4,579.7 |
| `tabfm__early_concat` | -1,035.2 | -1,052.3 | -952.6 | -896.4 | -37.5 | -444.9 | -4,551.6 |
| `tabpfn_full__late` | -225.8 | -297.1 | -88.8 | -250.2 | -1,192.3 | -665.1 | -4,541.3 |
| `exaone__late` | -1,390.2 | -1,501.1 | -1,558.0 | -1,385.6 | -2,223.4 | -1,731.4 | -4,541.9 |
| `supervised_mlp16` | -51.7 | +67.1 | +79.8 | -34.9 | +768.9 | +1,133.5 | -4,578.6 |

### matched kernel, diagonal innovations

| Representation | native | redraw 1 | redraw 2 | shared cap/assets | shared income/assets | both shared | decoded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct` | +2,187.1 | — | — | +2,194.6 | +2,194.6 | — | -496.2 |
| `tabfm__early_concat` | +2,293.6 | +2,316.7 | +2,066.6 | +2,382.9 | +2,841.1 | +2,708.5 | +2,701.0 |
| `tabpfn_full__late` | +716.7 | +483.8 | +756.0 | +649.1 | +657.9 | +852.1 | +3,390.8 |
| `exaone__late` | -149.1 | -292.8 | -207.7 | -120.4 | +701.8 | +244.6 | +3,451.4 |
| `supervised_mlp16` | -1,133.1 | -1,061.8 | -1,010.0 | -1,105.3 | -602.1 | -258.4 | -1,376.7 |

Decoders: mean over years of the out-of-fold R^2 of the five prior-covariance
exposures, and the Spearman correlation between decoded and covariance-exposure
distances.

| Representation | Out-of-fold R^2 | Distance Spearman |
| --- | ---: | ---: |
| `autoencoder` | 0.035 | 0.184 |
| `direct` | -0.384 | 0.231 |
| `exaone__item_first_concat` | -301.567 | 0.132 |
| `exaone__item_first_mean` | -3.127 | 0.126 |
| `exaone__item_last_concat` | 0.229 | 0.420 |
| `exaone__late` | 0.204 | 0.377 |
| `pca16` | 0.025 | 0.194 |
| `random_autoencoder` | 0.036 | 0.191 |
| `supervised_mlp16` | 0.007 | 0.164 |
| `tabfm__early_concat` | 0.165 | 0.358 |
| `tabfm__early_concat_labelnull` | 0.111 | 0.327 |
| `tabfm__early_mean` | 0.165 | 0.359 |
| `tabfm__late` | 0.222 | 0.409 |
| `tabpfn_fast__late` | 0.216 | 0.402 |
| `tabpfn_full__late` | 0.217 | 0.395 |

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical|exp | 203 | `metrics__euclidean_no_indicators` |
| diagonal|exp | 206 | `histories__direct`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__supervised_mlp16`, `broad__mahalanobis_lw`, `broad__euclidean`, `broad__euclidean_no_indicators`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_full__late`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_full__late`, `histories@income_assets__direct`, `histories@income_assets__euclidean`, `histories@income_assets__direct_no_indicators`, `histories@income_assets__euclidean_no_indicators`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@shared_market_cap_assets__direct`, `histories@shared_market_cap_assets__euclidean`, `histories@shared_market_cap_assets__direct_no_indicators`, `histories@shared_market_cap_assets__euclidean_no_indicators`, `histories@shared_market_cap_assets__pca16`, `histories@shared_market_cap_assets__autoencoder`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_income_assets__direct`, `histories@shared_income_assets__euclidean`, `histories@shared_income_assets__direct_no_indicators`, `histories@shared_income_assets__euclidean_no_indicators`, `histories@shared_income_assets__pca16`, `histories@shared_income_assets__autoencoder`, `histories@shared_income_assets__supervised_mlp16`, `histories@redraw1__pca16`, `histories@redraw1__autoencoder`, `histories@redraw1__supervised_mlp16`, `histories@redraw2__pca16`, `histories@redraw2__autoencoder`, `histories@redraw2__supervised_mlp16`, `histories@shared_both__supervised_mlp16`, `h3__histories__direct`, `h3__histories__direct_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder` |
| correlation|exp | 206 | `histories__direct`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__supervised_mlp16`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `broad__mahalanobis_lw`, `broad__euclidean`, `broad__euclidean_no_indicators`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__exaone__late`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__exaone__late`, `histories@income_assets__direct`, `histories@income_assets__euclidean`, `histories@income_assets__direct_no_indicators`, `histories@income_assets__euclidean_no_indicators`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__direct`, `histories@shared_market_cap_assets__euclidean`, `histories@shared_market_cap_assets__direct_no_indicators`, `histories@shared_market_cap_assets__euclidean_no_indicators`, `histories@shared_market_cap_assets__pca16`, `histories@shared_market_cap_assets__autoencoder`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_income_assets__direct`, `histories@shared_income_assets__euclidean`, `histories@shared_income_assets__direct_no_indicators`, `histories@shared_income_assets__euclidean_no_indicators`, `histories@shared_income_assets__pca16`, `histories@shared_income_assets__autoencoder`, `histories@shared_income_assets__supervised_mlp16`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@redraw1__pca16`, `histories@redraw1__autoencoder`, `histories@redraw1__supervised_mlp16`, `histories@redraw1__tabpfn_full__late`, `histories@redraw1__tabfm__early_concat`, `histories@redraw1__tabfm__early_mean`, `histories@redraw2__pca16`, `histories@redraw2__autoencoder`, `histories@redraw2__supervised_mlp16`, `histories@redraw2__tabpfn_full__late`, `histories@redraw2__tabfm__early_concat`, `histories@redraw2__tabfm__early_mean`, `histories@shared_both__supervised_mlp16`, `histories@shared_both__tabfm__early_concat`, `histories@shared_both__tabfm__early_mean`, `h3__histories__direct`, `h3__histories__euclidean`, `h3__histories__direct_no_indicators`, `h3__histories__euclidean_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean` |
| spherical|median | 203 | `covariance_exposures` |
| diagonal|median | 206 | `covariance_exposures`, `histories@decoded__tabpfn_fast__late`, `histories@decoded__tabpfn_full__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__early_mean`, `histories@decoded__tabfm__late`, `histories@decoded__tabfm__early_concat_labelnull`, `histories@decoded__exaone__late`, `histories@decoded__exaone__item_last_concat`, `histories__direct`, `histories__direct_no_indicators`, `histories__pca16`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__exaone__late`, `metrics__autoencoder`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__direct_no_indicators`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__exaone__late`, `histories@shared_market_cap_assets__direct`, `histories@shared_market_cap_assets__direct_no_indicators`, `histories@shared_market_cap_assets__pca16`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__direct`, `histories@shared_income_assets__direct_no_indicators`, `histories@shared_income_assets__pca16`, `histories@redraw1__pca16`, `histories@redraw1__autoencoder`, `histories@redraw1__exaone__item_last_concat`, `histories@redraw2__pca16`, `histories@redraw2__autoencoder`, `histories@redraw2__exaone__late`, `histories@redraw2__exaone__item_last_concat`, `histories@shared_both__exaone__late`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |
| correlation|median | 206 | `covariance_exposures`, `histories@decoded__direct`, `histories@decoded__autoencoder`, `histories@decoded__supervised_mlp16`, `histories@decoded__tabpfn_fast__late`, `histories@decoded__tabpfn_full__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__early_mean`, `histories@decoded__tabfm__late`, `histories@decoded__tabfm__early_concat_labelnull`, `histories@decoded__exaone__late`, `histories@decoded__exaone__item_last_concat`, `histories__direct`, `histories__euclidean`, `histories__direct_no_indicators`, `histories__euclidean_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_first_concat`, `histories__exaone__item_first_mean`, `histories__exaone__item_last_concat`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_first_concat`, `broad__exaone__item_first_mean`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_first_concat`, `metrics__exaone__item_first_mean`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__euclidean`, `histories@income_assets__direct_no_indicators`, `histories@income_assets__euclidean_no_indicators`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__direct`, `histories@shared_market_cap_assets__euclidean`, `histories@shared_market_cap_assets__direct_no_indicators`, `histories@shared_market_cap_assets__euclidean_no_indicators`, `histories@shared_market_cap_assets__pca16`, `histories@shared_market_cap_assets__autoencoder`, `histories@shared_market_cap_assets__random_autoencoder`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__tabfm__early_concat_labelnull`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_first_concat`, `histories@shared_market_cap_assets__exaone__item_first_mean`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__direct`, `histories@shared_income_assets__euclidean`, `histories@shared_income_assets__direct_no_indicators`, `histories@shared_income_assets__euclidean_no_indicators`, `histories@shared_income_assets__pca16`, `histories@shared_income_assets__autoencoder`, `histories@shared_income_assets__random_autoencoder`, `histories@shared_income_assets__supervised_mlp16`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__tabfm__early_concat_labelnull`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_first_concat`, `histories@shared_income_assets__exaone__item_first_mean`, `histories@shared_income_assets__exaone__item_last_concat`, `histories@redraw1__pca16`, `histories@redraw1__autoencoder`, `histories@redraw1__random_autoencoder`, `histories@redraw1__supervised_mlp16`, `histories@redraw1__tabpfn_fast__late`, `histories@redraw1__tabpfn_full__late`, `histories@redraw1__tabfm__early_concat`, `histories@redraw1__tabfm__early_mean`, `histories@redraw1__tabfm__late`, `histories@redraw1__tabfm__early_concat_labelnull`, `histories@redraw1__exaone__late`, `histories@redraw1__exaone__item_first_concat`, `histories@redraw1__exaone__item_first_mean`, `histories@redraw1__exaone__item_last_concat`, `histories@redraw2__pca16`, `histories@redraw2__autoencoder`, `histories@redraw2__random_autoencoder`, `histories@redraw2__supervised_mlp16`, `histories@redraw2__tabpfn_fast__late`, `histories@redraw2__tabpfn_full__late`, `histories@redraw2__tabfm__early_concat`, `histories@redraw2__tabfm__early_mean`, `histories@redraw2__tabfm__late`, `histories@redraw2__tabfm__early_concat_labelnull`, `histories@redraw2__exaone__late`, `histories@redraw2__exaone__item_first_concat`, `histories@redraw2__exaone__item_first_mean`, `histories@redraw2__exaone__item_last_concat`, `histories@shared_both__supervised_mlp16`, `histories@shared_both__tabpfn_fast__late`, `histories@shared_both__tabpfn_full__late`, `histories@shared_both__tabfm__early_concat`, `histories@shared_both__tabfm__early_mean`, `histories@shared_both__tabfm__late`, `histories@shared_both__exaone__late`, `histories@shared_both__exaone__item_last_concat`, `h3__histories__direct`, `h3__histories__euclidean`, `h3__histories__direct_no_indicators`, `h3__histories__euclidean_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_first_concat`, `h3__histories__exaone__item_first_mean`, `h3__histories__exaone__item_last_concat` |
| spherical|matched | 203 | `covariance_exposures` |
| diagonal|matched | 206 | `covariance_exposures`, `metrics__direct`, `metrics__direct_no_indicators`, `metrics__direct_no_size`, `metrics__direct_no_changes` |
| correlation|matched | 206 | `covariance_exposures`, `histories@decoded__tabpfn_fast__late`, `histories@decoded__tabpfn_full__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__early_mean`, `histories@decoded__tabfm__late`, `histories@decoded__tabfm__early_concat_labelnull`, `histories@decoded__exaone__late`, `histories@decoded__exaone__item_last_concat`, `histories__direct`, `histories__direct_no_indicators`, `histories__pca16`, `histories__autoencoder`, `histories__random_autoencoder`, `histories__supervised_mlp16`, `histories__tabpfn_fast__late`, `histories__tabpfn_full__late`, `histories__tabfm__early_concat`, `histories__tabfm__early_mean`, `histories__tabfm__late`, `histories__tabfm__early_concat_labelnull`, `histories__exaone__late`, `histories__exaone__item_last_concat`, `broad__direct`, `broad__euclidean`, `broad__direct_no_indicators`, `broad__euclidean_no_indicators`, `broad__direct_no_size`, `broad__euclidean_no_size`, `broad__pca16`, `broad__autoencoder`, `broad__supervised_mlp16`, `broad__tabpfn_fast__late`, `broad__tabpfn_full__late`, `broad__tabfm__early_concat`, `broad__tabfm__early_mean`, `broad__tabfm__late`, `broad__tabfm__early_concat_labelnull`, `broad__exaone__late`, `broad__exaone__item_last_concat`, `metrics__direct`, `metrics__mahalanobis_lw`, `metrics__euclidean`, `metrics__direct_no_indicators`, `metrics__euclidean_no_indicators`, `metrics__direct_no_size`, `metrics__euclidean_no_size`, `metrics__direct_no_changes`, `metrics__euclidean_no_changes`, `metrics__pca16`, `metrics__autoencoder`, `metrics__random_autoencoder`, `metrics__supervised_mlp16`, `metrics__tabpfn_fast__late`, `metrics__tabpfn_full__late`, `metrics__tabfm__early_concat`, `metrics__tabfm__early_mean`, `metrics__tabfm__late`, `metrics__tabfm__early_concat_labelnull`, `metrics__exaone__late`, `metrics__exaone__item_last_concat`, `histories@income_assets__direct`, `histories@income_assets__direct_no_indicators`, `histories@income_assets__pca16`, `histories@income_assets__autoencoder`, `histories@income_assets__random_autoencoder`, `histories@income_assets__supervised_mlp16`, `histories@income_assets__tabpfn_fast__late`, `histories@income_assets__tabpfn_full__late`, `histories@income_assets__tabfm__early_concat`, `histories@income_assets__tabfm__early_mean`, `histories@income_assets__tabfm__late`, `histories@income_assets__tabfm__early_concat_labelnull`, `histories@income_assets__exaone__late`, `histories@income_assets__exaone__item_first_concat`, `histories@income_assets__exaone__item_first_mean`, `histories@income_assets__exaone__item_last_concat`, `histories@shared_market_cap_assets__direct`, `histories@shared_market_cap_assets__direct_no_indicators`, `histories@shared_market_cap_assets__pca16`, `histories@shared_market_cap_assets__autoencoder`, `histories@shared_market_cap_assets__random_autoencoder`, `histories@shared_market_cap_assets__supervised_mlp16`, `histories@shared_market_cap_assets__tabpfn_fast__late`, `histories@shared_market_cap_assets__tabpfn_full__late`, `histories@shared_market_cap_assets__tabfm__early_concat`, `histories@shared_market_cap_assets__tabfm__early_mean`, `histories@shared_market_cap_assets__tabfm__late`, `histories@shared_market_cap_assets__tabfm__early_concat_labelnull`, `histories@shared_market_cap_assets__exaone__late`, `histories@shared_market_cap_assets__exaone__item_first_concat`, `histories@shared_market_cap_assets__exaone__item_first_mean`, `histories@shared_market_cap_assets__exaone__item_last_concat`, `histories@shared_income_assets__direct`, `histories@shared_income_assets__direct_no_indicators`, `histories@shared_income_assets__pca16`, `histories@shared_income_assets__autoencoder`, `histories@shared_income_assets__random_autoencoder`, `histories@shared_income_assets__supervised_mlp16`, `histories@shared_income_assets__tabpfn_fast__late`, `histories@shared_income_assets__tabpfn_full__late`, `histories@shared_income_assets__tabfm__early_concat`, `histories@shared_income_assets__tabfm__early_mean`, `histories@shared_income_assets__tabfm__late`, `histories@shared_income_assets__tabfm__early_concat_labelnull`, `histories@shared_income_assets__exaone__late`, `histories@shared_income_assets__exaone__item_first_concat`, `histories@shared_income_assets__exaone__item_first_mean`, `histories@shared_income_assets__exaone__item_last_concat`, `histories@redraw1__pca16`, `histories@redraw1__autoencoder`, `histories@redraw1__random_autoencoder`, `histories@redraw1__supervised_mlp16`, `histories@redraw1__tabpfn_fast__late`, `histories@redraw1__tabpfn_full__late`, `histories@redraw1__tabfm__early_concat`, `histories@redraw1__tabfm__early_mean`, `histories@redraw1__tabfm__late`, `histories@redraw1__tabfm__early_concat_labelnull`, `histories@redraw1__exaone__late`, `histories@redraw1__exaone__item_last_concat`, `histories@redraw2__pca16`, `histories@redraw2__autoencoder`, `histories@redraw2__random_autoencoder`, `histories@redraw2__supervised_mlp16`, `histories@redraw2__tabpfn_fast__late`, `histories@redraw2__tabpfn_full__late`, `histories@redraw2__tabfm__early_concat`, `histories@redraw2__tabfm__early_mean`, `histories@redraw2__tabfm__late`, `histories@redraw2__tabfm__early_concat_labelnull`, `histories@redraw2__exaone__late`, `histories@redraw2__exaone__item_last_concat`, `histories@shared_both__supervised_mlp16`, `histories@shared_both__tabpfn_fast__late`, `histories@shared_both__tabpfn_full__late`, `histories@shared_both__tabfm__early_concat`, `histories@shared_both__tabfm__early_mean`, `histories@shared_both__tabfm__late`, `histories@shared_both__exaone__late`, `histories@shared_both__exaone__item_last_concat`, `h3__histories__direct`, `h3__histories__euclidean`, `h3__histories__direct_no_indicators`, `h3__histories__euclidean_no_indicators`, `h3__histories__pca16`, `h3__histories__autoencoder`, `h3__histories__random_autoencoder`, `h3__histories__supervised_mlp16`, `h3__histories__tabpfn_fast__late`, `h3__histories__tabpfn_full__late`, `h3__histories__tabfm__early_concat`, `h3__histories__tabfm__early_mean`, `h3__histories__tabfm__late`, `h3__histories__tabfm__early_concat_labelnull`, `h3__histories__exaone__late`, `h3__histories__exaone__item_last_concat` |

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
| `broad__direct_no_indicators` | 0.987 | 0.993 | 0.898 | 1.4e-09 |
| `broad__direct_no_size` | 0.991 | 0.995 | 0.898 | 1.7e-09 |
| `broad__euclidean` | 0.076 | 0.991 | 0.898 | 1.5e-09 |
| `broad__euclidean_no_indicators` | 0.128 | 0.977 | 0.898 | 1.2e-09 |
| `broad__euclidean_no_size` | 0.080 | 0.991 | 0.898 | 1.5e-09 |
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
| `covariance_exposures` | 1.000 | 0.841 | 0.898 | 1.2e-09 |
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
| `h3__histories__direct_no_indicators` | 0.898 | 0.838 | 0.898 | 3.3e-10 |
| `h3__histories__euclidean` | 0.759 | 0.781 | 0.898 | 8.1e-10 |
| `h3__histories__euclidean_no_indicators` | 0.759 | 0.781 | 0.898 | 8.1e-10 |
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
| `histories@decoded__autoencoder` | 1.000 | 0.783 | 0.898 | 5.4e-10 |
| `histories@decoded__direct` | 1.000 | 0.800 | 0.898 | 7.3e-10 |
| `histories@decoded__exaone__item_first_concat` | 1.000 | 0.831 | 0.898 | 1.2e-09 |
| `histories@decoded__exaone__item_first_mean` | 1.000 | 0.828 | 0.898 | 1.6e-09 |
| `histories@decoded__exaone__item_last_concat` | 1.000 | 0.865 | 0.898 | 9.9e-10 |
| `histories@decoded__exaone__late` | 1.000 | 0.865 | 0.898 | 1.5e-09 |
| `histories@decoded__pca16` | 1.000 | 0.791 | 0.898 | 4.1e-10 |
| `histories@decoded__random_autoencoder` | 1.000 | 0.789 | 0.898 | 1.1e-09 |
| `histories@decoded__supervised_mlp16` | 1.000 | 0.793 | 0.898 | 7.7e-10 |
| `histories@decoded__tabfm__early_concat` | 1.000 | 0.868 | 0.898 | 4.1e-10 |
| `histories@decoded__tabfm__early_concat_labelnull` | 1.000 | 0.857 | 0.898 | 9.3e-10 |
| `histories@decoded__tabfm__early_mean` | 1.000 | 0.869 | 0.898 | 4.5e-10 |
| `histories@decoded__tabfm__late` | 1.000 | 0.869 | 0.898 | 1.4e-09 |
| `histories@decoded__tabpfn_fast__late` | 1.000 | 0.867 | 0.898 | 1.4e-09 |
| `histories@decoded__tabpfn_full__late` | 1.000 | 0.866 | 0.898 | 1.3e-09 |
| `histories@income_assets__autoencoder` | 0.923 | 0.806 | 0.898 | 8.9e-10 |
| `histories@income_assets__direct` | 0.936 | 0.860 | 0.898 | 1.7e-09 |
| `histories@income_assets__direct_no_indicators` | 0.886 | 0.878 | 0.898 | 9.5e-10 |
| `histories@income_assets__euclidean` | 0.666 | 0.809 | 0.898 | 3e-10 |
| `histories@income_assets__euclidean_no_indicators` | 0.666 | 0.809 | 0.898 | 3e-10 |
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
| `histories@redraw1__autoencoder` | 0.898 | 0.818 | 0.898 | 2.1e-09 |
| `histories@redraw1__exaone__item_first_concat` | 1.000 | 0.794 | 0.898 | 9.6e-10 |
| `histories@redraw1__exaone__item_first_mean` | 1.000 | 0.781 | 0.898 | 5.9e-10 |
| `histories@redraw1__exaone__item_last_concat` | 0.979 | 0.843 | 0.898 | 1.1e-09 |
| `histories@redraw1__exaone__late` | 0.950 | 0.742 | 0.898 | 2.1e-10 |
| `histories@redraw1__mahalanobis_lw` | 0.636 | 0.832 | 0.898 | 1.2e-09 |
| `histories@redraw1__pca16` | 0.905 | 0.861 | 0.898 | 2.4e-12 |
| `histories@redraw1__random_autoencoder` | 0.955 | 0.839 | 0.898 | 1.2e-09 |
| `histories@redraw1__supervised_mlp16` | 0.787 | 0.660 | 0.898 | 1.2e-09 |
| `histories@redraw1__tabfm__early_concat` | 0.972 | 0.898 | 0.898 | 1e-09 |
| `histories@redraw1__tabfm__early_concat_labelnull` | 0.995 | 0.875 | 0.898 | 6.7e-10 |
| `histories@redraw1__tabfm__early_mean` | 0.972 | 0.898 | 0.898 | 1.1e-09 |
| `histories@redraw1__tabfm__late` | 0.990 | 0.828 | 0.898 | 3.1e-10 |
| `histories@redraw1__tabpfn_fast__late` | 0.966 | 0.837 | 0.898 | 5.2e-11 |
| `histories@redraw1__tabpfn_full__late` | 0.933 | 0.835 | 0.898 | 1.2e-10 |
| `histories@redraw2__autoencoder` | 0.902 | 0.815 | 0.898 | 1.3e-09 |
| `histories@redraw2__exaone__item_first_concat` | 1.000 | 0.797 | 0.898 | 1.6e-09 |
| `histories@redraw2__exaone__item_first_mean` | 1.000 | 0.783 | 0.898 | 1.1e-09 |
| `histories@redraw2__exaone__item_last_concat` | 0.980 | 0.838 | 0.898 | 1.1e-09 |
| `histories@redraw2__exaone__late` | 0.955 | 0.742 | 0.898 | 1.4e-09 |
| `histories@redraw2__mahalanobis_lw` | 0.643 | 0.830 | 0.898 | 6e-11 |
| `histories@redraw2__pca16` | 0.910 | 0.857 | 0.898 | 2.3e-12 |
| `histories@redraw2__random_autoencoder` | 0.955 | 0.839 | 0.898 | 1.2e-09 |
| `histories@redraw2__supervised_mlp16` | 0.795 | 0.679 | 0.898 | 9.9e-10 |
| `histories@redraw2__tabfm__early_concat` | 0.971 | 0.901 | 0.898 | 1.6e-09 |
| `histories@redraw2__tabfm__early_concat_labelnull` | 0.995 | 0.867 | 0.898 | 1.3e-09 |
| `histories@redraw2__tabfm__early_mean` | 0.971 | 0.901 | 0.898 | 1.7e-09 |
| `histories@redraw2__tabfm__late` | 0.990 | 0.832 | 0.898 | 3.3e-10 |
| `histories@redraw2__tabpfn_fast__late` | 0.967 | 0.832 | 0.898 | 5e-11 |
| `histories@redraw2__tabpfn_full__late` | 0.935 | 0.831 | 0.898 | 4.4e-11 |
| `histories@shared_both__exaone__item_last_concat` | 0.988 | 0.881 | 0.898 | 7.7e-11 |
| `histories@shared_both__exaone__late` | 0.967 | 0.785 | 0.898 | 1.3e-09 |
| `histories@shared_both__supervised_mlp16` | 0.812 | 0.807 | 0.898 | 1.2e-09 |
| `histories@shared_both__tabfm__early_concat` | 0.966 | 0.910 | 0.898 | 1e-09 |
| `histories@shared_both__tabfm__early_mean` | 0.966 | 0.910 | 0.898 | 7.7e-10 |
| `histories@shared_both__tabfm__late` | 0.993 | 0.867 | 0.898 | 2.3e-10 |
| `histories@shared_both__tabpfn_fast__late` | 0.978 | 0.857 | 0.898 | 4.3e-12 |
| `histories@shared_both__tabpfn_full__late` | 0.952 | 0.852 | 0.898 | 2.3e-11 |
| `histories@shared_income_assets__autoencoder` | 0.900 | 0.813 | 0.898 | 2.1e-09 |
| `histories@shared_income_assets__direct` | 0.926 | 0.864 | 0.898 | 1.4e-09 |
| `histories@shared_income_assets__direct_no_indicators` | 0.885 | 0.877 | 0.898 | 1.1e-09 |
| `histories@shared_income_assets__euclidean` | 0.665 | 0.809 | 0.898 | 2.7e-10 |
| `histories@shared_income_assets__euclidean_no_indicators` | 0.665 | 0.809 | 0.898 | 2.7e-10 |
| `histories@shared_income_assets__exaone__item_first_concat` | 1.000 | 0.792 | 0.898 | 1e-09 |
| `histories@shared_income_assets__exaone__item_first_mean` | 1.000 | 0.779 | 0.898 | 1.1e-09 |
| `histories@shared_income_assets__exaone__item_last_concat` | 0.993 | 0.911 | 0.898 | 1.1e-10 |
| `histories@shared_income_assets__exaone__late` | 0.979 | 0.819 | 0.898 | 1.3e-09 |
| `histories@shared_income_assets__mahalanobis_lw` | 0.645 | 0.833 | 0.898 | 9.2e-10 |
| `histories@shared_income_assets__pca16` | 0.913 | 0.851 | 0.898 | 1.6e-10 |
| `histories@shared_income_assets__random_autoencoder` | 0.956 | 0.839 | 0.898 | 1.1e-09 |
| `histories@shared_income_assets__supervised_mlp16` | 0.812 | 0.808 | 0.898 | 5.4e-10 |
| `histories@shared_income_assets__tabfm__early_concat` | 0.960 | 0.914 | 0.898 | 8e-10 |
| `histories@shared_income_assets__tabfm__early_concat_labelnull` | 0.994 | 0.876 | 0.898 | 4.4e-10 |
| `histories@shared_income_assets__tabfm__early_mean` | 0.960 | 0.914 | 0.898 | 9.1e-10 |
| `histories@shared_income_assets__tabfm__late` | 0.995 | 0.895 | 0.898 | 2.8e-11 |
| `histories@shared_income_assets__tabpfn_fast__late` | 0.986 | 0.859 | 0.898 | 1.9e-09 |
| `histories@shared_income_assets__tabpfn_full__late` | 0.960 | 0.844 | 0.898 | 1.9e-09 |
| `histories@shared_market_cap_assets__autoencoder` | 0.900 | 0.813 | 0.898 | 2.1e-09 |
| `histories@shared_market_cap_assets__direct` | 0.926 | 0.864 | 0.898 | 1.4e-09 |
| `histories@shared_market_cap_assets__direct_no_indicators` | 0.885 | 0.877 | 0.898 | 1.1e-09 |
| `histories@shared_market_cap_assets__euclidean` | 0.665 | 0.809 | 0.898 | 2.7e-10 |
| `histories@shared_market_cap_assets__euclidean_no_indicators` | 0.665 | 0.809 | 0.898 | 2.7e-10 |
| `histories@shared_market_cap_assets__exaone__item_first_concat` | 1.000 | 0.792 | 0.898 | 1e-09 |
| `histories@shared_market_cap_assets__exaone__item_first_mean` | 1.000 | 0.779 | 0.898 | 1.1e-09 |
| `histories@shared_market_cap_assets__exaone__item_last_concat` | 0.981 | 0.853 | 0.898 | 8.6e-10 |
| `histories@shared_market_cap_assets__exaone__late` | 0.952 | 0.747 | 0.898 | 7.6e-10 |
| `histories@shared_market_cap_assets__mahalanobis_lw` | 0.645 | 0.833 | 0.898 | 9.2e-10 |
| `histories@shared_market_cap_assets__pca16` | 0.913 | 0.851 | 0.898 | 1.6e-10 |
| `histories@shared_market_cap_assets__random_autoencoder` | 0.956 | 0.839 | 0.898 | 1.1e-09 |
| `histories@shared_market_cap_assets__supervised_mlp16` | 0.782 | 0.645 | 0.898 | 1.4e-09 |
| `histories@shared_market_cap_assets__tabfm__early_concat` | 0.971 | 0.899 | 0.898 | 4.5e-10 |
| `histories@shared_market_cap_assets__tabfm__early_concat_labelnull` | 0.994 | 0.876 | 0.898 | 4.4e-10 |
| `histories@shared_market_cap_assets__tabfm__early_mean` | 0.971 | 0.899 | 0.898 | 4.7e-10 |
| `histories@shared_market_cap_assets__tabfm__late` | 0.990 | 0.830 | 0.898 | 2.5e-10 |
| `histories@shared_market_cap_assets__tabpfn_fast__late` | 0.968 | 0.842 | 0.898 | 2.7e-11 |
| `histories@shared_market_cap_assets__tabpfn_full__late` | 0.938 | 0.840 | 0.898 | 6.3e-11 |
| `histories__autoencoder` | 0.899 | 0.813 | 0.898 | 1.5e-09 |
| `histories__direct` | 0.925 | 0.864 | 0.898 | 1.1e-09 |
| `histories__direct_no_indicators` | 0.883 | 0.877 | 0.898 | 8.5e-10 |
| `histories__euclidean` | 0.658 | 0.808 | 0.898 | 3.7e-10 |
| `histories__euclidean_no_indicators` | 0.658 | 0.808 | 0.898 | 3.7e-10 |
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
| `metrics__direct_no_changes` | 0.983 | 0.991 | 0.898 | 2.4e-09 |
| `metrics__direct_no_indicators` | 0.979 | 0.990 | 0.898 | 8.1e-10 |
| `metrics__direct_no_size` | 0.984 | 0.992 | 0.898 | 2.1e-09 |
| `metrics__euclidean` | 0.060 | 0.985 | 0.898 | 8.6e-10 |
| `metrics__euclidean_no_changes` | 0.101 | 0.984 | 0.898 | 1.8e-09 |
| `metrics__euclidean_no_indicators` | 0.180 | 0.956 | 0.898 | 1e-09 |
| `metrics__euclidean_no_size` | 0.060 | 0.984 | 0.898 | 9.1e-10 |
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

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
