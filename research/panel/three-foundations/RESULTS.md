# Panel design `three-foundations`

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
| `histories@calibration32@decoded__direct` | calibrated | -3,227.07 | -4,564.00 | +2,565.22 | +1,256.97 | -2,466.07 |
| `histories@calibration64@decoded__direct` | calibrated | -3,227.77 | -4,565.43 | +1,590.64 | +379.82 | -2,466.90 |
| `histories@calibration128@decoded__direct` | calibrated | -3,230.01 | -4,567.80 | +2,162.75 | +721.32 | -2,469.79 |
| `histories@calibration256@decoded__direct` | calibrated | -3,229.99 | -4,567.35 | +2,408.33 | +979.00 | -2,469.81 |
| `histories@decoded__pca16` | calibrated | -3,236.51 | -4,578.80 | +508.00 | -236.61 | -2,477.38 |
| `histories@calibration32@decoded__pca16` | calibrated | -3,233.34 | -4,572.90 | +468.41 | -638.67 | -2,473.07 |
| `histories@calibration64@decoded__pca16` | calibrated | -3,232.40 | -4,571.49 | +927.68 | -329.63 | -2,472.56 |
| `histories@calibration128@decoded__pca16` | calibrated | -3,231.17 | -4,568.97 | +1,511.72 | +132.90 | -2,470.99 |
| `histories@calibration256@decoded__pca16` | calibrated | -3,232.42 | -4,570.59 | +1,783.68 | +255.15 | -2,472.56 |
| `histories@decoded__supervised_mlp16` | calibrated | -3,235.81 | -4,578.52 | -4,493.29 | -808.76 | -2,476.07 |
| `histories@calibration32@decoded__supervised_mlp16` | calibrated | -3,228.26 | -4,563.48 | +2,321.93 | +1,064.90 | -2,467.13 |
| `histories@calibration64@decoded__supervised_mlp16` | calibrated | -3,233.49 | -4,575.28 | -2,389.81 | -2,170.62 | -2,474.20 |
| `histories@calibration128@decoded__supervised_mlp16` | calibrated | -3,233.17 | -4,575.37 | -3,921.44 | -1,419.53 | -2,473.12 |
| `histories@calibration256@decoded__supervised_mlp16` | calibrated | -3,233.33 | -4,575.01 | +845.35 | -552.98 | -2,473.41 |
| `histories@decoded__tabpfn_full__late` | calibrated | -3,217.53 | -4,544.74 | +4,371.18 | +3,330.98 | -2,454.73 |
| `histories@calibration32@decoded__tabpfn_full__late` | calibrated | -3,232.33 | -4,569.74 | +2,606.13 | +1,240.84 | -2,472.41 |
| `histories@calibration64@decoded__tabpfn_full__late` | calibrated | -3,227.43 | -4,561.37 | +3,445.73 | +1,699.02 | -2,466.06 |
| `histories@calibration128@decoded__tabpfn_full__late` | calibrated | -3,222.51 | -4,553.12 | +4,010.94 | +2,588.56 | -2,460.07 |
| `histories@calibration256@decoded__tabpfn_full__late` | calibrated | -3,217.39 | -4,544.88 | +4,189.47 | +3,101.61 | -2,454.09 |
| `histories@decoded__tabpfn_full_random__late` | calibrated | -3,225.93 | -4,558.45 | +2,923.47 | +1,859.71 | -2,464.64 |
| `histories@decoded__tabpfn_full_random43__late` | calibrated | -3,225.57 | -4,557.72 | +3,040.88 | +1,951.27 | -2,464.24 |
| `histories@decoded__tabpfn_full_random44__late` | calibrated | -3,226.33 | -4,558.88 | +2,969.79 | +1,887.22 | -2,465.39 |
| `histories@decoded__tabfm__early_concat` | calibrated | -3,221.36 | -4,552.49 | +3,766.14 | +2,877.20 | -2,458.80 |
| `histories@decoded__tabfm__late` | calibrated | -3,216.37 | -4,542.96 | +4,405.87 | +3,612.89 | -2,453.49 |
| `histories@calibration32@decoded__tabfm__late` | calibrated | -3,225.87 | -4,557.73 | +3,887.20 | +3,158.54 | -2,464.16 |
| `histories@calibration64@decoded__tabfm__late` | calibrated | -3,224.08 | -4,556.74 | +3,336.01 | +2,521.47 | -2,461.84 |
| `histories@calibration128@decoded__tabfm__late` | calibrated | -3,220.90 | -4,551.42 | +3,651.46 | +2,864.01 | -2,457.80 |
| `histories@calibration256@decoded__tabfm__late` | calibrated | -3,216.07 | -4,542.78 | +4,257.88 | +3,535.19 | -2,452.97 |
| `histories@decoded__kumo__late` | calibrated | -3,217.45 | -4,544.19 | +4,723.67 | +3,608.60 | -2,454.29 |
| `histories@calibration32@decoded__kumo__late` | calibrated | -3,226.56 | -4,558.51 | +4,060.99 | +3,150.72 | -2,464.92 |
| `histories@calibration64@decoded__kumo__late` | calibrated | -3,225.49 | -4,557.88 | +3,628.33 | +2,384.80 | -2,463.03 |
| `histories@calibration128@decoded__kumo__late` | calibrated | -3,222.00 | -4,551.76 | +4,469.94 | +3,148.00 | -2,458.81 |
| `histories@calibration256@decoded__kumo__late` | calibrated | -3,216.67 | -4,542.74 | +4,737.82 | +3,575.97 | -2,453.40 |
| `histories@decoded__kumo__early_concat` | calibrated | -3,213.17 | -4,537.72 | +4,772.76 | +3,936.79 | -2,450.05 |
| `histories@decoded__kumo_random__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@decoded__kumo_random43__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@decoded__kumo_random44__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@decoded__limix__late` | calibrated | -3,226.09 | -4,558.81 | +3,188.65 | +1,992.89 | -2,464.39 |
| `histories@calibration32@decoded__limix__late` | calibrated | -3,237.69 | -4,579.96 | +572.76 | -818.77 | -2,478.88 |
| `histories@calibration64@decoded__limix__late` | calibrated | -3,233.85 | -4,572.06 | +3,459.44 | +1,042.30 | -2,474.29 |
| `histories@calibration128@decoded__limix__late` | calibrated | -3,230.92 | -4,567.40 | +3,276.11 | +1,415.66 | -2,470.40 |
| `histories@calibration256@decoded__limix__late` | calibrated | -3,226.14 | -4,558.75 | +3,176.99 | +1,869.86 | -2,464.30 |
| `histories__direct` | classical | +818.94 | +1,216.98 | +3,206.89 | +2,187.09 | +1,045.94 |
| `histories__pca16` | control | +1,189.16 | +1,613.80 | +3,423.74 | +2,208.47 | +1,239.14 |
| `histories__supervised_mlp16` | task | +68.42 | -51.73 | -59.62 | -1,133.11 | +1,027.66 |
| `histories__tabpfn_full__late` | task | -558.96 | -225.81 | +2,111.74 | +716.72 | +213.70 |
| `histories__tabpfn_full_random__late` | control | -3,041.08 | -4,237.09 | -347.83 | -32.08 | -2,215.48 |
| `histories__tabpfn_full_random43__late` | control | -3,020.62 | -4,198.77 | -389.26 | +79.58 | -2,190.17 |
| `histories__tabpfn_full_random44__late` | control | -3,006.66 | -4,177.12 | -442.02 | -237.57 | -2,167.86 |
| `histories__tabfm__early_concat` | state | -842.03 | -1,035.18 | +2,288.49 | +2,293.63 | +236.58 |
| `histories__tabfm__late` | task | -2,294.57 | -3,091.74 | +1,959.38 | +189.38 | -1,328.64 |
| `histories__kumo__late` | task | -1,919.86 | -2,431.60 | +2,391.69 | +367.96 | -901.69 |
| `histories__kumo__early_concat` | state | -2,383.39 | -3,213.59 | +2,480.87 | +1,890.36 | -1,447.69 |
| `histories__kumo_random__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories__kumo_random43__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories__kumo_random44__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories__limix__late` | task | +816.41 | +1,827.13 | +1,373.49 | +707.13 | +825.48 |
| `histories@support32@decoded__pca16` | calibrated | -3,236.45 | -4,579.10 | +1,098.44 | -43.56 | -2,477.48 |
| `histories@support32@decoded__supervised_mlp16` | calibrated | -3,233.75 | -4,573.16 | +1,892.64 | +320.70 | -2,473.28 |
| `histories@support32@decoded__tabpfn_full__late` | calibrated | -3,216.70 | -4,544.18 | +4,026.44 | +3,293.41 | -2,453.82 |
| `histories@support32@decoded__tabpfn_full_random__late` | calibrated | -3,228.17 | -4,562.18 | +2,617.84 | +1,633.64 | -2,466.95 |
| `histories@support32@decoded__tabpfn_full_random43__late` | calibrated | -3,227.40 | -4,561.05 | +2,901.85 | +1,898.20 | -2,466.03 |
| `histories@support32@decoded__tabpfn_full_random44__late` | calibrated | -3,227.61 | -4,561.43 | +2,881.14 | +1,795.44 | -2,466.77 |
| `histories@support32@decoded__tabfm__early_concat` | calibrated | -3,222.16 | -4,553.85 | +3,498.48 | +2,615.20 | -2,460.16 |
| `histories@support32@decoded__tabfm__late` | calibrated | -3,217.42 | -4,544.82 | +4,364.19 | +3,500.39 | -2,454.91 |
| `histories@support32@decoded__kumo__late` | calibrated | -3,219.51 | -4,549.33 | +3,606.59 | +2,893.30 | -2,456.66 |
| `histories@support32@decoded__kumo__early_concat` | calibrated | -3,215.73 | -4,542.29 | +4,380.60 | +3,548.32 | -2,452.92 |
| `histories@support32@decoded__kumo_random__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support32@decoded__kumo_random43__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support32@decoded__kumo_random44__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support32@decoded__limix__late` | calibrated | -3,227.41 | -4,560.75 | +3,286.87 | +1,758.65 | -2,465.93 |
| `histories@support32__pca16` | control | +1,501.34 | +1,795.86 | +3,475.82 | +2,455.57 | +1,469.09 |
| `histories@support32__supervised_mlp16` | task | -327.08 | -551.17 | -957.10 | -1,314.47 | +567.78 |
| `histories@support32__tabpfn_full__late` | task | -505.80 | -5.06 | +1,951.94 | +363.06 | +302.95 |
| `histories@support32__tabpfn_full_random__late` | control | -3,007.56 | -4,172.42 | -1,045.38 | -1,045.81 | -2,157.35 |
| `histories@support32__tabpfn_full_random43__late` | control | -2,940.00 | -4,057.83 | -934.30 | -934.02 | -2,072.00 |
| `histories@support32__tabpfn_full_random44__late` | control | -2,929.12 | -4,039.01 | -843.32 | -991.39 | -2,050.11 |
| `histories@support32__tabfm__early_concat` | state | -1,630.45 | -2,050.46 | +2,131.90 | +1,506.57 | -609.35 |
| `histories@support32__tabfm__late` | task | -2,197.65 | -2,775.26 | +1,882.27 | -19.64 | -1,217.58 |
| `histories@support32__kumo__late` | task | -1,748.90 | -2,017.22 | +1,792.94 | +115.51 | -706.26 |
| `histories@support32__kumo__early_concat` | state | -2,363.08 | -3,179.38 | +2,271.37 | +1,022.58 | -1,397.52 |
| `histories@support32__kumo_random__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support32__kumo_random43__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support32__kumo_random44__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support32__limix__late` | task | +1,000.02 | +2,346.58 | +1,701.09 | +922.32 | +868.86 |
| `histories@support64@decoded__pca16` | calibrated | -3,236.45 | -4,578.63 | +355.66 | -63.47 | -2,476.70 |
| `histories@support64@decoded__supervised_mlp16` | calibrated | -3,235.45 | -4,576.95 | +1,120.18 | -345.72 | -2,475.72 |
| `histories@support64@decoded__tabpfn_full__late` | calibrated | -3,216.27 | -4,543.85 | +4,269.88 | +3,396.60 | -2,453.65 |
| `histories@support64@decoded__tabpfn_full_random__late` | calibrated | -3,227.38 | -4,561.56 | +2,831.47 | +1,702.62 | -2,466.15 |
| `histories@support64@decoded__tabpfn_full_random43__late` | calibrated | -3,226.78 | -4,559.91 | +3,019.41 | +1,856.64 | -2,464.89 |
| `histories@support64@decoded__tabpfn_full_random44__late` | calibrated | -3,226.97 | -4,559.90 | +3,616.79 | +2,330.05 | -2,465.83 |
| `histories@support64@decoded__tabfm__early_concat` | calibrated | -3,221.30 | -4,551.60 | +3,918.60 | +2,950.82 | -2,459.09 |
| `histories@support64@decoded__tabfm__late` | calibrated | -3,217.07 | -4,544.37 | +4,228.42 | +3,419.11 | -2,454.15 |
| `histories@support64@decoded__kumo__late` | calibrated | -3,217.34 | -4,544.47 | +4,649.51 | +3,638.08 | -2,453.74 |
| `histories@support64@decoded__kumo__early_concat` | calibrated | -3,214.05 | -4,539.32 | +4,697.66 | +3,843.32 | -2,450.88 |
| `histories@support64@decoded__kumo_random__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support64@decoded__kumo_random43__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support64@decoded__kumo_random44__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support64@decoded__limix__late` | calibrated | -3,226.58 | -4,559.63 | +2,901.46 | +1,784.07 | -2,464.50 |
| `histories@support64__pca16` | control | +1,566.31 | +1,980.52 | +3,570.76 | +2,502.78 | +1,261.64 |
| `histories@support64__supervised_mlp16` | task | -234.66 | -175.06 | -583.72 | -1,077.88 | +580.56 |
| `histories@support64__tabpfn_full__late` | task | -508.14 | +80.83 | +2,133.18 | +641.58 | +287.28 |
| `histories@support64__tabpfn_full_random__late` | control | -3,048.75 | -4,244.10 | -1,089.65 | -1,101.63 | -2,218.66 |
| `histories@support64__tabpfn_full_random43__late` | control | -2,987.55 | -4,129.25 | -811.42 | -785.45 | -2,140.39 |
| `histories@support64__tabpfn_full_random44__late` | control | -2,978.11 | -4,106.72 | -770.48 | -907.00 | -2,115.09 |
| `histories@support64__tabfm__early_concat` | state | -1,490.77 | -1,938.03 | +2,235.59 | +1,615.77 | -467.40 |
| `histories@support64__tabfm__late` | task | -2,267.03 | -2,945.10 | +1,928.52 | +51.96 | -1,300.22 |
| `histories@support64__kumo__late` | task | -1,921.88 | -2,351.55 | +2,096.42 | +299.21 | -903.43 |
| `histories@support64__kumo__early_concat` | state | -2,363.65 | -3,191.33 | +2,754.48 | +1,839.05 | -1,411.11 |
| `histories@support64__kumo_random__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support64__kumo_random43__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support64__kumo_random44__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support64__limix__late` | task | +663.87 | +1,839.90 | +1,318.68 | +646.09 | +684.13 |
| `histories@support128@decoded__pca16` | calibrated | -3,236.37 | -4,578.84 | +896.64 | +45.57 | -2,476.77 |
| `histories@support128@decoded__supervised_mlp16` | calibrated | -3,235.10 | -4,575.95 | +1,325.91 | +24.77 | -2,475.21 |
| `histories@support128@decoded__tabpfn_full__late` | calibrated | -3,216.59 | -4,543.99 | +4,263.27 | +3,281.85 | -2,453.78 |
| `histories@support128@decoded__tabpfn_full_random__late` | calibrated | -3,226.37 | -4,559.71 | +3,036.72 | +1,993.66 | -2,464.93 |
| `histories@support128@decoded__tabpfn_full_random43__late` | calibrated | -3,226.54 | -4,559.77 | +3,031.00 | +1,927.75 | -2,464.96 |
| `histories@support128@decoded__tabpfn_full_random44__late` | calibrated | -3,225.91 | -4,558.49 | +3,375.56 | +2,145.58 | -2,464.45 |
| `histories@support128@decoded__tabfm__early_concat` | calibrated | -3,220.87 | -4,551.12 | +3,511.22 | +2,735.38 | -2,458.60 |
| `histories@support128@decoded__tabfm__late` | calibrated | -3,217.12 | -4,544.07 | +4,130.09 | +3,327.68 | -2,453.56 |
| `histories@support128@decoded__kumo__late` | calibrated | -3,217.77 | -4,545.40 | +4,265.01 | +3,218.72 | -2,454.72 |
| `histories@support128@decoded__kumo__early_concat` | calibrated | -3,213.79 | -4,539.33 | +4,571.05 | +3,750.72 | -2,450.65 |
| `histories@support128@decoded__kumo_random__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support128@decoded__kumo_random43__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support128@decoded__kumo_random44__late` | calibrated | -3,243.10 | -4,590.68 | -6,141.56 | -5,039.19 | -2,485.15 |
| `histories@support128@decoded__limix__late` | calibrated | -3,225.95 | -4,558.24 | +3,767.44 | +2,355.39 | -2,464.88 |
| `histories@support128__pca16` | control | +1,466.88 | +2,005.70 | +3,598.29 | +2,459.54 | +1,186.03 |
| `histories@support128__supervised_mlp16` | task | +113.24 | +5.38 | -193.08 | -1,056.27 | +1,158.00 |
| `histories@support128__tabpfn_full__late` | task | -694.83 | -423.59 | +1,920.23 | +540.09 | +132.59 |
| `histories@support128__tabpfn_full_random__late` | control | -3,044.18 | -4,242.80 | -882.03 | -829.19 | -2,218.02 |
| `histories@support128__tabpfn_full_random43__late` | control | -3,009.51 | -4,185.57 | -748.42 | -559.66 | -2,178.07 |
| `histories@support128__tabpfn_full_random44__late` | control | -3,001.38 | -4,169.82 | -812.55 | -821.07 | -2,159.01 |
| `histories@support128__tabfm__early_concat` | state | -1,028.36 | -1,365.83 | +2,256.29 | +1,950.31 | +36.03 |
| `histories@support128__tabfm__late` | task | -2,338.06 | -3,139.89 | +1,717.54 | +36.33 | -1,373.99 |
| `histories@support128__kumo__late` | task | -1,955.36 | -2,489.43 | +2,181.01 | +323.27 | -934.75 |
| `histories@support128__kumo__early_concat` | state | -2,399.03 | -3,238.72 | +2,457.14 | +1,870.72 | -1,467.18 |
| `histories@support128__kumo_random__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support128__kumo_random43__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support128__kumo_random44__late` | control | -3,243.13 | -4,590.76 | -4,590.76 | -4,590.76 | -2,485.19 |
| `histories@support128__limix__late` | task | +685.45 | +1,657.59 | +1,253.33 | +582.49 | +847.91 |
| `h3__fernandez_market_cap_assets` | fernandez | -2,106.30 | -5,356.71 | -5,356.71 | -3,590.96 | -2,159.10 |
| `h3__fernandez_market_to_book` | fernandez | -2,294.23 | -5,334.64 | -5,282.49 | -3,708.46 | -2,472.82 |
| `h3__fernandez_dividend_yield` | fernandez | -2,411.17 | -4,449.07 | -4,503.31 | -3,286.53 | -2,006.15 |
| `h3__fernandez_joint` | fernandez | -1,136.54 | -2,535.10 | -2,590.42 | -2,663.92 | -654.53 |
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
| `histories@calibration32@decoded__direct` | -4,564.00 | [-8,250.0, -2,500.8] | [-8,625.2, -2,287.0] | 49.7 |
| `histories@calibration64@decoded__direct` | -4,565.43 | [-8,254.8, -2,500.0] | [-8,631.4, -2,285.9] | 49.7 |
| `histories@calibration128@decoded__direct` | -4,567.80 | [-8,258.8, -2,501.6] | [-8,635.1, -2,287.3] | 49.7 |
| `histories@calibration256@decoded__direct` | -4,567.35 | [-8,257.7, -2,501.6] | [-8,634.1, -2,287.3] | 49.7 |
| `histories@decoded__pca16` | -4,578.80 | [-8,280.4, -2,506.8] | [-8,656.2, -2,292.0] | 49.7 |
| `histories@calibration32@decoded__pca16` | -4,572.90 | [-8,267.3, -2,505.1] | [-8,643.6, -2,290.3] | 49.7 |
| `histories@calibration64@decoded__pca16` | -4,571.49 | [-8,266.3, -2,503.5] | [-8,642.1, -2,288.8] | 49.7 |
| `histories@calibration128@decoded__pca16` | -4,568.97 | [-8,260.3, -2,502.6] | [-8,636.3, -2,288.2] | 49.7 |
| `histories@calibration256@decoded__pca16` | -4,570.59 | [-8,262.7, -2,503.8] | [-8,638.9, -2,289.4] | 49.7 |
| `histories@decoded__supervised_mlp16` | -4,578.52 | [-8,280.9, -2,506.1] | [-8,657.3, -2,291.1] | 49.7 |
| `histories@calibration32@decoded__supervised_mlp16` | -4,563.48 | [-8,246.0, -2,501.9] | [-8,620.3, -2,288.0] | 49.7 |
| `histories@calibration64@decoded__supervised_mlp16` | -4,575.28 | [-8,273.1, -2,505.6] | [-8,649.7, -2,290.6] | 49.7 |
| `histories@calibration128@decoded__supervised_mlp16` | -4,575.37 | [-8,275.5, -2,504.2] | [-8,651.3, -2,289.3] | 49.7 |
| `histories@calibration256@decoded__supervised_mlp16` | -4,575.01 | [-8,273.3, -2,504.9] | [-8,649.7, -2,290.0] | 49.7 |
| `histories@decoded__tabpfn_full__late` | -4,544.74 | [-8,217.1, -2,488.7] | [-8,592.2, -2,276.0] | 49.7 |
| `histories@calibration32@decoded__tabpfn_full__late` | -4,569.74 | [-8,260.5, -2,503.7] | [-8,635.6, -2,289.4] | 49.7 |
| `histories@calibration64@decoded__tabpfn_full__late` | -4,561.37 | [-8,248.0, -2,497.0] | [-8,623.9, -2,283.5] | 49.7 |
| `histories@calibration128@decoded__tabpfn_full__late` | -4,553.12 | [-8,233.9, -2,492.1] | [-8,609.7, -2,278.9] | 49.7 |
| `histories@calibration256@decoded__tabpfn_full__late` | -4,544.88 | [-8,218.3, -2,488.1] | [-8,593.8, -2,275.4] | 49.7 |
| `histories@decoded__tabpfn_full_random__late` | -4,558.45 | [-8,241.2, -2,496.6] | [-8,617.0, -2,283.1] | 49.7 |
| `histories@decoded__tabpfn_full_random43__late` | -4,557.72 | [-8,239.3, -2,496.4] | [-8,615.1, -2,283.0] | 49.7 |
| `histories@decoded__tabpfn_full_random44__late` | -4,558.88 | [-8,242.0, -2,497.0] | [-8,617.7, -2,283.2] | 49.7 |
| `histories@decoded__tabfm__early_concat` | -4,552.49 | [-8,231.4, -2,492.9] | [-8,606.4, -2,279.4] | 49.7 |
| `histories@decoded__tabfm__late` | -4,542.96 | [-8,213.7, -2,487.8] | [-8,587.9, -2,275.2] | 49.7 |
| `histories@calibration32@decoded__tabfm__late` | -4,557.73 | [-8,237.3, -2,497.7] | [-8,612.6, -2,283.9] | 49.7 |
| `histories@calibration64@decoded__tabfm__late` | -4,556.74 | [-8,239.7, -2,494.8] | [-8,615.8, -2,281.2] | 49.7 |
| `histories@calibration128@decoded__tabfm__late` | -4,551.42 | [-8,231.7, -2,491.4] | [-8,605.9, -2,278.0] | 49.7 |
| `histories@calibration256@decoded__tabfm__late` | -4,542.78 | [-8,213.9, -2,487.5] | [-8,587.9, -2,275.0] | 49.7 |
| `histories@decoded__kumo__late` | -4,544.19 | [-8,215.9, -2,488.4] | [-8,590.8, -2,275.7] | 49.7 |
| `histories@calibration32@decoded__kumo__late` | -4,558.51 | [-8,237.7, -2,498.7] | [-8,611.5, -2,284.9] | 49.7 |
| `histories@calibration64@decoded__kumo__late` | -4,557.88 | [-8,240.9, -2,495.5] | [-8,616.6, -2,282.5] | 49.7 |
| `histories@calibration128@decoded__kumo__late` | -4,551.76 | [-8,230.6, -2,492.0] | [-8,606.5, -2,279.0] | 49.7 |
| `histories@calibration256@decoded__kumo__late` | -4,542.74 | [-8,214.0, -2,487.2] | [-8,588.8, -2,274.7] | 49.7 |
| `histories@decoded__kumo__early_concat` | -4,537.72 | [-8,203.9, -2,485.1] | [-8,578.4, -2,272.6] | 49.7 |
| `histories@decoded__kumo_random__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@decoded__kumo_random43__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@decoded__kumo_random44__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@decoded__limix__late` | -4,558.81 | [-8,244.0, -2,495.4] | [-8,619.5, -2,282.3] | 49.7 |
| `histories@calibration32@decoded__limix__late` | -4,579.96 | [-8,282.3, -2,507.5] | [-8,658.8, -2,293.0] | 49.7 |
| `histories@calibration64@decoded__limix__late` | -4,572.06 | [-8,267.1, -2,503.5] | [-8,643.3, -2,289.5] | 49.7 |
| `histories@calibration128@decoded__limix__late` | -4,567.40 | [-8,260.5, -2,500.0] | [-8,636.4, -2,286.3] | 49.7 |
| `histories@calibration256@decoded__limix__late` | -4,558.75 | [-8,244.0, -2,495.5] | [-8,619.6, -2,282.3] | 49.7 |
| `histories__direct` | +1,216.98 | [+363.1, +2,412.5] | [+156.5, +2,802.8] | 63.3 |
| `histories__pca16` | +1,613.80 | [+538.1, +3,175.9] | [+271.5, +3,636.2] | 62.7 |
| `histories__supervised_mlp16` | -51.73 | [-884.1, +1,032.2] | [-1,044.6, +1,342.1] | 11.1 |
| `histories__tabpfn_full__late` | -225.81 | [-784.6, +440.5] | [-847.0, +593.5] | 37.6 |
| `histories__tabpfn_full_random__late` | -4,237.09 | [-7,621.7, -2,345.2] | [-7,945.0, -2,154.2] | 49.1 |
| `histories__tabpfn_full_random43__late` | -4,198.77 | [-7,544.5, -2,328.1] | [-7,854.1, -2,143.0] | 49.1 |
| `histories__tabpfn_full_random44__late` | -4,177.12 | [-7,506.9, -2,314.6] | [-7,819.8, -2,128.8] | 49.0 |
| `histories__tabfm__early_concat` | -1,035.18 | [-1,873.6, -440.3] | [-1,833.4, -386.0] | 35.1 |
| `histories__tabfm__late` | -3,091.74 | [-5,500.2, -1,733.9] | [-5,666.5, -1,614.7] | 44.6 |
| `histories__kumo__late` | -2,431.60 | [-4,337.6, -1,300.6] | [-4,403.2, -1,220.2] | 42.2 |
| `histories__kumo__early_concat` | -3,213.59 | [-5,733.1, -1,800.1] | [-5,928.2, -1,670.2] | 46.5 |
| `histories__kumo_random__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories__kumo_random43__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories__kumo_random44__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories__limix__late` | +1,827.13 | [+678.9, +3,448.7] | [+396.3, +3,983.5] | 64.4 |
| `histories@support32@decoded__pca16` | -4,579.10 | [-8,281.0, -2,506.7] | [-8,657.7, -2,291.8] | 49.7 |
| `histories@support32@decoded__supervised_mlp16` | -4,573.16 | [-8,268.5, -2,504.7] | [-8,644.8, -2,289.8] | 49.7 |
| `histories@support32@decoded__tabpfn_full__late` | -4,544.18 | [-8,217.3, -2,488.2] | [-8,590.4, -2,275.0] | 49.7 |
| `histories@support32@decoded__tabpfn_full_random__late` | -4,562.18 | [-8,248.2, -2,498.3] | [-8,624.8, -2,284.5] | 49.7 |
| `histories@support32@decoded__tabpfn_full_random43__late` | -4,561.05 | [-8,246.5, -2,497.5] | [-8,623.0, -2,284.0] | 49.7 |
| `histories@support32@decoded__tabpfn_full_random44__late` | -4,561.43 | [-8,247.1, -2,497.7] | [-8,623.5, -2,284.3] | 49.7 |
| `histories@support32@decoded__tabfm__early_concat` | -4,553.85 | [-8,232.2, -2,494.3] | [-8,607.7, -2,281.0] | 49.7 |
| `histories@support32@decoded__tabfm__late` | -4,544.82 | [-8,216.4, -2,489.0] | [-8,590.8, -2,276.1] | 49.7 |
| `histories@support32@decoded__kumo__late` | -4,549.33 | [-8,228.5, -2,489.8] | [-8,601.8, -2,276.5] | 49.7 |
| `histories@support32@decoded__kumo__early_concat` | -4,542.29 | [-8,212.4, -2,487.4] | [-8,587.0, -2,274.7] | 49.7 |
| `histories@support32@decoded__kumo_random__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support32@decoded__kumo_random43__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support32@decoded__kumo_random44__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support32@decoded__limix__late` | -4,560.75 | [-8,248.6, -2,496.6] | [-8,623.4, -2,283.1] | 49.7 |
| `histories@support32__pca16` | +1,795.86 | [+749.5, +3,302.1] | [+500.6, +3,730.1] | 35.0 |
| `histories@support32__supervised_mlp16` | -551.17 | [-1,379.0, +418.9] | [-1,398.9, +599.6] | 23.5 |
| `histories@support32__tabpfn_full__late` | -5.06 | [-637.3, +788.3] | [-827.6, +1,128.7] | 65.9 |
| `histories@support32__tabpfn_full_random__late` | -4,172.42 | [-7,510.8, -2,308.1] | [-7,808.5, -2,125.7] | 48.9 |
| `histories@support32__tabpfn_full_random43__late` | -4,057.83 | [-7,278.0, -2,259.0] | [-7,570.4, -2,084.2] | 48.7 |
| `histories@support32__tabpfn_full_random44__late` | -4,039.01 | [-7,245.5, -2,249.6] | [-7,530.4, -2,075.0] | 48.6 |
| `histories@support32__tabfm__early_concat` | -2,050.46 | [-3,490.3, -1,155.4] | [-3,524.3, -1,087.1] | 40.7 |
| `histories@support32__tabfm__late` | -2,775.26 | [-4,753.4, -1,624.4] | [-4,842.6, -1,518.1] | 44.0 |
| `histories@support32__kumo__late` | -2,017.22 | [-3,431.6, -1,117.5] | [-3,442.5, -1,055.2] | 40.3 |
| `histories@support32__kumo__early_concat` | -3,179.38 | [-5,629.1, -1,797.4] | [-5,801.0, -1,674.1] | 45.5 |
| `histories@support32__kumo_random__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support32__kumo_random43__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support32__kumo_random44__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support32__limix__late` | +2,346.58 | [+824.2, +4,568.7] | [+470.9, +5,225.1] | 62.4 |
| `histories@support64@decoded__pca16` | -4,578.63 | [-8,280.3, -2,506.4] | [-8,657.4, -2,291.8] | 49.7 |
| `histories@support64@decoded__supervised_mlp16` | -4,576.95 | [-8,276.7, -2,505.7] | [-8,653.5, -2,290.9] | 49.7 |
| `histories@support64@decoded__tabpfn_full__late` | -4,543.85 | [-8,215.9, -2,488.5] | [-8,589.2, -2,275.5] | 49.7 |
| `histories@support64@decoded__tabpfn_full_random__late` | -4,561.56 | [-8,248.2, -2,497.4] | [-8,624.7, -2,283.8] | 49.7 |
| `histories@support64@decoded__tabpfn_full_random43__late` | -4,559.91 | [-8,244.5, -2,497.1] | [-8,620.3, -2,283.5] | 49.7 |
| `histories@support64@decoded__tabpfn_full_random44__late` | -4,559.90 | [-8,243.7, -2,497.5] | [-8,619.6, -2,283.5] | 49.7 |
| `histories@support64@decoded__tabfm__early_concat` | -4,551.60 | [-8,228.8, -2,493.1] | [-8,603.4, -2,279.6] | 49.7 |
| `histories@support64@decoded__tabfm__late` | -4,544.37 | [-8,216.2, -2,488.5] | [-8,589.7, -2,275.8] | 49.7 |
| `histories@support64@decoded__kumo__late` | -4,544.47 | [-8,218.7, -2,487.6] | [-8,592.9, -2,275.0] | 49.7 |
| `histories@support64@decoded__kumo__early_concat` | -4,539.32 | [-8,207.5, -2,485.4] | [-8,582.4, -2,273.0] | 49.7 |
| `histories@support64@decoded__kumo_random__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support64@decoded__kumo_random43__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support64@decoded__kumo_random44__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support64@decoded__limix__late` | -4,559.63 | [-8,246.7, -2,495.9] | [-8,621.2, -2,282.4] | 49.7 |
| `histories@support64__pca16` | +1,980.52 | [+689.7, +3,873.5] | [+388.3, +4,417.8] | 61.6 |
| `histories@support64__supervised_mlp16` | -175.06 | [-979.5, +875.6] | [-1,138.3, +1,185.6] | 59.8 |
| `histories@support64__tabpfn_full__late` | +80.83 | [-558.1, +881.8] | [-749.4, +1,224.0] | 65.9 |
| `histories@support64__tabpfn_full_random__late` | -4,244.10 | [-7,647.4, -2,341.9] | [-7,970.8, -2,151.9] | 49.1 |
| `histories@support64__tabpfn_full_random43__late` | -4,129.25 | [-7,416.1, -2,291.0] | [-7,718.4, -2,112.2] | 48.9 |
| `histories@support64__tabpfn_full_random44__late` | -4,106.72 | [-7,381.4, -2,276.3] | [-7,676.6, -2,100.4] | 48.8 |
| `histories@support64__tabfm__early_concat` | -1,938.03 | [-3,434.9, -1,035.8] | [-3,469.1, -968.7] | 39.9 |
| `histories@support64__tabfm__late` | -2,945.10 | [-5,119.8, -1,695.4] | [-5,252.6, -1,578.7] | 44.3 |
| `histories@support64__kumo__late` | -2,351.55 | [-4,129.2, -1,279.8] | [-4,190.4, -1,198.5] | 42.4 |
| `histories@support64__kumo__early_concat` | -3,191.33 | [-5,621.7, -1,814.7] | [-5,808.5, -1,688.1] | 45.7 |
| `histories@support64__kumo_random__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support64__kumo_random43__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support64__kumo_random44__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support64__limix__late` | +1,839.90 | [+679.3, +3,479.0] | [+389.4, +4,026.8] | 64.3 |
| `histories@support128@decoded__pca16` | -4,578.84 | [-8,280.5, -2,506.4] | [-8,657.8, -2,291.7] | 49.7 |
| `histories@support128@decoded__supervised_mlp16` | -4,575.95 | [-8,273.9, -2,506.0] | [-8,650.8, -2,291.1] | 49.7 |
| `histories@support128@decoded__tabpfn_full__late` | -4,543.99 | [-8,217.2, -2,488.0] | [-8,590.5, -2,274.8] | 49.7 |
| `histories@support128@decoded__tabpfn_full_random__late` | -4,559.71 | [-8,244.4, -2,497.0] | [-8,620.6, -2,283.1] | 49.7 |
| `histories@support128@decoded__tabpfn_full_random43__late` | -4,559.77 | [-8,244.1, -2,497.3] | [-8,619.6, -2,283.4] | 49.7 |
| `histories@support128@decoded__tabpfn_full_random44__late` | -4,558.49 | [-8,241.5, -2,496.6] | [-8,617.2, -2,283.0] | 49.7 |
| `histories@support128@decoded__tabfm__early_concat` | -4,551.12 | [-8,227.0, -2,493.2] | [-8,602.2, -2,279.8] | 49.7 |
| `histories@support128@decoded__tabfm__late` | -4,544.07 | [-8,215.8, -2,488.4] | [-8,589.4, -2,275.6] | 49.7 |
| `histories@support128@decoded__kumo__late` | -4,545.40 | [-8,219.5, -2,488.6] | [-8,593.7, -2,275.7] | 49.7 |
| `histories@support128@decoded__kumo__early_concat` | -4,539.33 | [-8,207.9, -2,485.3] | [-8,582.4, -2,272.9] | 49.7 |
| `histories@support128@decoded__kumo_random__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support128@decoded__kumo_random43__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support128@decoded__kumo_random44__late` | -4,590.68 | [-8,305.2, -2,511.7] | [-8,680.9, -2,296.1] | 49.7 |
| `histories@support128@decoded__limix__late` | -4,558.24 | [-8,243.3, -2,495.3] | [-8,618.8, -2,281.9] | 49.7 |
| `histories@support128__pca16` | +2,005.70 | [+684.9, +3,964.2] | [+385.4, +4,526.5] | 61.6 |
| `histories@support128__supervised_mlp16` | +5.38 | [-963.2, +1,259.5] | [-1,136.6, +1,622.4] | 21.6 |
| `histories@support128__tabpfn_full__late` | -423.59 | [-1,002.9, +214.3] | [-1,028.3, +333.8] | 36.0 |
| `histories@support128__tabpfn_full_random__late` | -4,242.80 | [-7,637.0, -2,345.3] | [-7,960.4, -2,156.0] | 49.1 |
| `histories@support128__tabpfn_full_random43__late` | -4,185.57 | [-7,513.7, -2,323.5] | [-7,822.4, -2,139.8] | 49.1 |
| `histories@support128__tabpfn_full_random44__late` | -4,169.82 | [-7,489.3, -2,312.8] | [-7,799.8, -2,129.2] | 49.0 |
| `histories@support128__tabfm__early_concat` | -1,365.83 | [-2,472.5, -627.2] | [-2,455.0, -578.2] | 35.8 |
| `histories@support128__tabfm__late` | -3,139.89 | [-5,572.6, -1,766.0] | [-5,743.8, -1,645.1] | 44.8 |
| `histories@support128__kumo__late` | -2,489.43 | [-4,441.8, -1,338.8] | [-4,516.0, -1,254.6] | 42.5 |
| `histories@support128__kumo__early_concat` | -3,238.72 | [-5,763.1, -1,819.8] | [-5,957.4, -1,691.5] | 46.5 |
| `histories@support128__kumo_random__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support128__kumo_random43__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support128__kumo_random44__late` | -4,590.76 | [-8,305.3, -2,511.7] | [-8,681.0, -2,296.1] | 49.7 |
| `histories@support128__limix__late` | +1,657.59 | [+597.3, +3,124.9] | [+325.1, +3,644.2] | 65.2 |
| `h3__fernandez_market_cap_assets` | -5,356.71 | [-11,510.4, -1,723.3] | [-12,489.1, -1,184.3] | 53.3 |
| `h3__fernandez_market_to_book` | -5,334.64 | [-11,441.1, -1,863.4] | [-12,267.9, -1,394.4] | 50.7 |
| `h3__fernandez_dividend_yield` | -4,449.07 | [-9,415.9, -1,493.6] | [-10,235.7, -962.8] | 53.8 |
| `h3__fernandez_joint` | -2,535.10 | [-5,800.5, -603.0] | [-6,317.1, -281.8] | 52.2 |

## Declared paired contrasts

Left minus right, summed over held-out days, with 95% stationary-bootstrap intervals
(21-day expected blocks). The intervals resample realized daily differences and hold
the fitted coefficients, networks and searched specifications fixed.

| Contrast | Left | Right | Arm | Difference | 21-day interval | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +3,426.7 | [+2,190.8, +5,593.2] | +1,543 | +359 | +367 | +345 | +236 | +577 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +106.5 | [-208.9, +322.9] | -81 | -6 | +67 | +19 | +48 | +60 |
| topology | `histories__direct` | `uniform_network` | matched/diagonal | +6,777.8 | [+3,557.6, +12,273.4] | +4,137 | +534 | +585 | +523 | +269 | +730 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/diagonal | +583.6 | [-192.7, +1,222.0] | -432 | +216 | +242 | +105 | +89 | +365 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,581.3 | [+1,708.1, +3,995.2] | +932 | +283 | +324 | +217 | +241 | +583 |
| decoded vs native | `histories@decoded__tabfm__late` | `histories__tabfm__late` | matched/diagonal | +3,423.5 | [+2,078.2, +5,287.1] | +708 | +542 | +550 | +456 | +269 | +898 |
| decoded vs decoded inputs | `histories@decoded__tabfm__late` | `histories@decoded__direct` | matched/diagonal | +3,317.0 | [+2,383.4, +4,772.5] | +989 | +420 | +422 | +376 | +323 | +788 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/diagonal | +2,614.3 | [+1,543.4, +3,961.2] | +375 | +419 | +519 | +379 | +195 | +726 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/diagonal | +3,035.1 | [+2,182.9, +4,366.9] | +942 | +314 | +431 | +325 | +323 | +700 |
| decoded vs native | `histories@decoded__kumo__late` | `histories__kumo__late` | matched/diagonal | +3,240.6 | [+1,903.4, +5,086.3] | +655 | +549 | +554 | +385 | +265 | +832 |
| decoded vs decoded inputs | `histories@decoded__kumo__late` | `histories@decoded__direct` | matched/diagonal | +3,312.7 | [+2,300.8, +4,941.2] | +1,099 | +406 | +429 | +308 | +337 | +734 |
| decoded vs native | `histories@decoded__limix__late` | `histories__limix__late` | matched/diagonal | +1,285.8 | [+633.5, +2,049.9] | +98 | +172 | +214 | +208 | +117 | +477 |
| decoded vs decoded inputs | `histories@decoded__limix__late` | `histories@decoded__direct` | matched/diagonal | +1,697.0 | [+1,031.1, +2,694.6] | +712 | +39 | +110 | +134 | +238 | +464 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/diagonal | +324.4 | [-424.0, +892.9] | -532 | +276 | +113 | +128 | +80 | +260 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/diagonal | -1,104.7 | [-2,231.2, -465.5] | -711 | -15 | -171 | -105 | -4 | -98 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +1,821.8 | [+1,159.9, +2,497.9] | +68 | +417 | +328 | +393 | +169 | +447 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +778.7 | [+279.8, +1,523.6] | +616 | -26 | +75 | -18 | +65 | +67 |
| topology | `histories__direct` | `uniform_network` | matched/correlation | +3,727.3 | [+2,449.8, +5,548.3] | +1,151 | +661 | +531 | +659 | +184 | +541 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | matched/correlation | -3,270.4 | [-8,746.3, +304.3] | -4,220 | +350 | +200 | +223 | -18 | +193 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,278.9 | [-5,289.8, +1,325.4] | -2,819 | +424 | +289 | +329 | +110 | +389 |
| decoded vs native | `histories@decoded__tabfm__late` | `histories__tabfm__late` | matched/correlation | -3,349.0 | [-11,226.1, +1,869.6] | -5,900 | +800 | +464 | +660 | +63 | +564 |
| decoded vs decoded inputs | `histories@decoded__tabfm__late` | `histories@decoded__direct` | matched/correlation | -2,374.7 | [-8,763.3, +1,739.5] | -4,538 | +626 | +363 | +526 | +134 | +515 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | matched/correlation | -2,373.8 | [-8,234.4, +1,565.9] | -4,426 | +611 | +428 | +499 | +38 | +477 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | matched/correlation | -1,617.8 | [-6,716.3, +1,645.0] | -3,554 | +488 | +370 | +445 | +153 | +480 |
| decoded vs native | `histories@decoded__kumo__late` | `histories__kumo__late` | matched/correlation | -2,857.7 | [-9,783.1, +1,803.2] | -5,262 | +759 | +477 | +576 | +85 | +507 |
| decoded vs decoded inputs | `histories@decoded__kumo__late` | `histories@decoded__direct` | matched/correlation | -2,028.1 | [-7,773.4, +1,657.9] | -4,055 | +578 | +377 | +443 | +165 | +465 |
| decoded vs native | `histories@decoded__limix__late` | `histories__limix__late` | matched/correlation | -999.8 | [-3,655.1, +816.9] | -2,031 | +276 | +171 | +229 | +16 | +341 |
| decoded vs decoded inputs | `histories@decoded__limix__late` | `histories@decoded__direct` | matched/correlation | -437.5 | [-2,433.9, +855.7] | -1,333 | +142 | +106 | +165 | +127 | +356 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | matched/correlation | -164.5 | [-1,258.8, +647.8] | -896 | +259 | +90 | +166 | +35 | +182 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | matched/correlation | +5.2 | [-442.3, +579.4] | +437 | -83 | -150 | -122 | -7 | -70 |
| pretrained vs supervised | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +2,348.1 | [+1,244.1, +4,205.4] | +875 | +260 | +144 | +207 | +283 | +579 |
| pretrained vs direct | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | -918.4 | [-1,755.2, -443.7] | -544 | -73 | -58 | -89 | -38 | -116 |
| topology | `histories__direct` | `uniform_network` | median/diagonal | +7,797.6 | [+4,080.6, +14,156.3] | +4,757 | +568 | +638 | +594 | +351 | +888 |
| decoded vs native | `histories@decoded__tabfm__early_concat` | `histories__tabfm__early_concat` | median/diagonal | +1,477.7 | [+550.0, +2,276.5] | -313 | +378 | +452 | +233 | +164 | +564 |
| decoded vs decoded inputs | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,913.6 | [+1,082.3, +3,216.2] | +797 | +118 | +173 | +116 | +214 | +496 |
| decoded vs native | `histories@decoded__tabfm__late` | `histories__tabfm__late` | median/diagonal | +2,446.5 | [+1,126.8, +3,739.8] | -241 | +573 | +550 | +442 | +243 | +879 |
| decoded vs decoded inputs | `histories@decoded__tabfm__late` | `histories@decoded__direct` | median/diagonal | +2,553.3 | [+1,753.6, +3,718.8] | +730 | +292 | +241 | +284 | +302 | +705 |
| decoded vs native | `histories@decoded__tabpfn_full__late` | `histories__tabpfn_full__late` | median/diagonal | +2,259.4 | [+1,094.7, +3,439.6] | -93 | +448 | +553 | +367 | +194 | +791 |
| decoded vs decoded inputs | `histories@decoded__tabpfn_full__late` | `histories@decoded__direct` | median/diagonal | +2,518.6 | [+1,598.2, +3,922.0] | +928 | +113 | +259 | +228 | +332 | +659 |
| decoded vs native | `histories@decoded__kumo__late` | `histories__kumo__late` | median/diagonal | +2,332.0 | [+956.0, +3,750.0] | -162 | +542 | +544 | +362 | +241 | +805 |
| decoded vs decoded inputs | `histories@decoded__kumo__late` | `histories@decoded__direct` | median/diagonal | +2,871.1 | [+1,808.0, +4,556.7] | +1,084 | +248 | +261 | +241 | +358 | +680 |
| decoded vs native | `histories@decoded__limix__late` | `histories__limix__late` | median/diagonal | +1,815.2 | [+982.1, +2,928.3] | +303 | +222 | +248 | +248 | +171 | +624 |
| decoded vs decoded inputs | `histories@decoded__limix__late` | `histories@decoded__direct` | median/diagonal | +1,336.1 | [+352.5, +2,761.2] | +928 | -179 | -115 | +32 | +249 | +421 |
| decoded vs native | `histories@decoded__supervised_mlp16` | `histories__supervised_mlp16` | median/diagonal | -4,433.7 | [-10,691.9, -481.0] | -4,790 | +295 | -22 | -25 | +125 | -16 |
| decoded vs decoded inputs | `histories@decoded__supervised_mlp16` | `histories@decoded__direct` | median/diagonal | -6,345.8 | [-12,960.3, -2,549.2] | -4,555 | -225 | -445 | -348 | -108 | -664 |
| support 32 native | `histories@support32__kumo__late` | `histories__direct` | matched/diagonal | -2,071.6 | [-4,051.6, -986.4] | -1,214 | -180 | -180 | -186 | -31 | -280 |
| support 32 native | `histories@support32__kumo__late` | `histories__direct` | matched/correlation | -338.4 | [-1,018.4, +468.9] | +477 | -246 | -144 | -257 | +19 | -188 |
| support 32 native | `histories@support32__kumo__late` | `histories__direct` | median/diagonal | -1,413.9 | [-3,068.2, -513.6] | -858 | -133 | -123 | -112 | +12 | -199 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__pca16` | matched/diagonal | -2,340.1 | [-4,535.7, -1,122.3] | -1,387 | -210 | -178 | -201 | -67 | -297 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__pca16` | matched/correlation | -413.4 | [-1,180.7, +492.9] | +499 | -284 | -143 | -285 | -4 | -197 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__pca16` | median/diagonal | -1,682.9 | [-3,612.2, -633.7] | -1,054 | -144 | -126 | -124 | -15 | -219 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__supervised_mlp16` | matched/diagonal | +1,430.0 | [+1,105.8, +1,937.7] | +500 | +200 | +159 | +140 | +185 | +247 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__supervised_mlp16` | matched/correlation | +915.7 | [+641.3, +1,141.4] | +53 | +215 | +151 | +158 | +147 | +194 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__supervised_mlp16` | median/diagonal | +2,750.0 | [+1,794.0, +4,415.1] | +1,177 | +280 | +255 | +180 | +311 | +548 |
| support 32 native | `histories@support32__limix__late` | `histories__direct` | matched/diagonal | -1,264.8 | [-2,258.4, -693.1] | -606 | -177 | -163 | -171 | +20 | -167 |
| support 32 native | `histories@support32__limix__late` | `histories__direct` | matched/correlation | -513.6 | [-958.4, -112.5] | +19 | -192 | -120 | -171 | +52 | -101 |
| support 32 native | `histories@support32__limix__late` | `histories__direct` | median/diagonal | -1,505.8 | [-2,803.7, -777.1] | -792 | -180 | -175 | -171 | +5 | -192 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__pca16` | matched/diagonal | -1,533.3 | [-2,752.7, -843.8] | -779 | -208 | -161 | -185 | -16 | -184 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__pca16` | matched/correlation | -588.5 | [-1,099.8, -104.3] | +41 | -230 | -119 | -200 | +29 | -109 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__pca16` | median/diagonal | -1,774.7 | [-3,346.6, -895.7] | -988 | -190 | -178 | -184 | -22 | -212 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__supervised_mlp16` | matched/diagonal | +2,236.8 | [+1,377.2, +3,713.5] | +1,108 | +203 | +175 | +155 | +236 | +359 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__supervised_mlp16` | matched/correlation | +740.5 | [-63.6, +1,322.3] | -405 | +268 | +175 | +243 | +180 | +281 |
| support 32 native | `histories@support32__limix__late` | `histories@support32__supervised_mlp16` | median/diagonal | +2,658.2 | [+1,512.6, +4,663.3] | +1,243 | +233 | +203 | +120 | +304 | +555 |
| support 32 native | `histories@support32__tabfm__late` | `histories__direct` | matched/diagonal | -2,206.7 | [-4,071.9, -1,181.2] | -1,170 | -180 | -227 | -230 | -68 | -332 |
| support 32 native | `histories@support32__tabfm__late` | `histories__direct` | matched/correlation | -399.1 | [-1,186.4, +558.3] | +589 | -270 | -188 | -303 | -5 | -221 |
| support 32 native | `histories@support32__tabfm__late` | `histories__direct` | median/diagonal | -1,324.6 | [-2,662.1, -565.8] | -647 | -106 | -141 | -158 | -20 | -251 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__pca16` | matched/diagonal | -2,475.2 | [-4,563.4, -1,322.8] | -1,342 | -210 | -225 | -245 | -104 | -350 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__pca16` | matched/correlation | -474.1 | [-1,342.3, +601.1] | +611 | -308 | -187 | -332 | -28 | -230 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__pca16` | median/diagonal | -1,593.5 | [-3,211.5, -697.4] | -844 | -117 | -144 | -171 | -47 | -271 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__supervised_mlp16` | matched/diagonal | +1,294.8 | [+913.6, +1,895.9] | +545 | +200 | +112 | +96 | +148 | +194 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__supervised_mlp16` | matched/correlation | +855.0 | [+701.0, +1,036.9] | +165 | +190 | +107 | +111 | +122 | +160 |
| support 32 native | `histories@support32__tabfm__late` | `histories@support32__supervised_mlp16` | median/diagonal | +2,839.4 | [+1,715.3, +4,813.6] | +1,387 | +307 | +236 | +134 | +279 | +496 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random__late` | matched/diagonal | +4,706.3 | [+2,511.0, +8,260.9] | +2,923 | +354 | +405 | +336 | +238 | +450 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random__late` | matched/correlation | +3,388.9 | [+2,188.0, +5,291.5] | +1,628 | +415 | +387 | +403 | +203 | +354 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random__late` | median/diagonal | +6,383.7 | [+3,463.7, +11,169.4] | +3,899 | +435 | +515 | +482 | +363 | +689 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random43__late` | matched/diagonal | +4,706.3 | [+2,511.0, +8,260.9] | +2,923 | +354 | +405 | +336 | +238 | +450 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random43__late` | matched/correlation | +3,388.9 | [+2,188.0, +5,291.5] | +1,628 | +415 | +387 | +403 | +203 | +354 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random43__late` | median/diagonal | +6,383.7 | [+3,463.7, +11,169.4] | +3,899 | +435 | +515 | +482 | +363 | +689 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random44__late` | matched/diagonal | +4,706.3 | [+2,511.0, +8,260.9] | +2,923 | +354 | +405 | +336 | +238 | +450 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random44__late` | matched/correlation | +3,388.9 | [+2,188.0, +5,291.5] | +1,628 | +415 | +387 | +403 | +203 | +354 |
| support 32 native | `histories@support32__kumo__late` | `histories@support32__kumo_random44__late` | median/diagonal | +6,383.7 | [+3,463.7, +11,169.4] | +3,899 | +435 | +515 | +482 | +363 | +689 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random43__late` | matched/diagonal | +1,297.1 | [+614.6, +2,308.0] | +911 | +70 | +93 | +56 | +68 | +99 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random43__late` | matched/correlation | +619.4 | [+215.7, +937.8] | +119 | +121 | +103 | +126 | +63 | +86 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random43__late` | median/diagonal | +2,886.2 | [+1,598.7, +4,887.9] | +1,750 | +186 | +225 | +194 | +193 | +339 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random44__late` | matched/diagonal | +1,354.5 | [+675.2, +2,361.9] | +912 | +83 | +108 | +72 | +68 | +111 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random44__late` | matched/correlation | +662.5 | [+259.0, +985.0] | +111 | +135 | +117 | +142 | +63 | +95 |
| support 32 native | `histories@support32__tabpfn_full__late` | `histories@support32__tabpfn_full_random44__late` | median/diagonal | +2,795.3 | [+1,563.5, +4,714.4] | +1,677 | +181 | +222 | +195 | +185 | +336 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | matched/diagonal | -680.5 | [-1,223.5, -333.4] | -251 | -118 | -108 | -91 | +6 | -117 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | matched/correlation | +175.9 | [-371.0, +924.7] | +551 | -147 | -79 | -125 | +40 | -64 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories__direct` | median/diagonal | -1,075.0 | [-1,953.5, -562.2] | -492 | -118 | -98 | -140 | -24 | -203 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | matched/diagonal | -949.0 | [-1,705.8, -492.1] | -424 | -149 | -106 | -106 | -30 | -135 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | matched/correlation | +100.9 | [-519.4, +961.9] | +574 | -185 | -78 | -153 | +17 | -73 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__pca16` | median/diagonal | -1,343.9 | [-2,502.5, -682.7] | -689 | -129 | -101 | -153 | -50 | -223 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | matched/diagonal | +2,821.0 | [+1,700.8, +4,787.0] | +1,463 | +262 | +230 | +235 | +222 | +409 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | matched/correlation | +1,430.0 | [+954.1, +1,944.2] | +127 | +313 | +216 | +289 | +167 | +317 |
| support 32 native | `histories@support32__tabfm__early_concat` | `histories@support32__supervised_mlp16` | median/diagonal | +3,089.0 | [+1,762.7, +5,514.6] | +1,543 | +294 | +280 | +152 | +276 | +544 |
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
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@decoded__direct` | matched/diagonal | +2,597.4 | [+1,928.8, +3,558.9] | +587 | +391 | +303 | +318 | +322 | +677 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@decoded__direct` | matched/correlation | -1,248.3 | [-5,686.3, +1,606.3] | -3,088 | +518 | +267 | +404 | +169 | +482 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@decoded__direct` | median/diagonal | +1,754.0 | [+1,209.3, +2,371.4] | +197 | +226 | +85 | +252 | +365 | +628 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__pca16` | matched/diagonal | +2,936.9 | [+2,167.8, +4,027.9] | +636 | +401 | +426 | +377 | +309 | +789 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__pca16` | matched/correlation | -1,081.8 | [-5,713.7, +1,929.5] | -3,222 | +546 | +383 | +459 | +171 | +581 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__pca16` | median/diagonal | +2,508.2 | [+1,846.8, +3,335.8] | +440 | +258 | +246 | +372 | +344 | +849 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +2,572.6 | [+1,954.2, +3,344.9] | +407 | +429 | +435 | +368 | +300 | +634 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -1,164.4 | [-5,588.8, +1,718.9] | -3,117 | +542 | +380 | +415 | +169 | +446 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +1,713.9 | [+1,073.5, +2,288.6] | -169 | +349 | +267 | +323 | +332 | +612 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@decoded__direct` | matched/diagonal | +1,462.8 | [+1,030.8, +2,029.8] | +433 | +151 | +73 | +118 | +238 | +450 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@decoded__direct` | matched/correlation | -624.7 | [-2,941.4, +831.2] | -1,549 | +226 | +75 | +156 | +134 | +333 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@decoded__direct` | median/diagonal | +1,434.3 | [+534.2, +2,700.9] | +880 | -22 | -153 | +23 | +247 | +459 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__pca16` | matched/diagonal | +1,802.2 | [+1,306.0, +2,481.4] | +482 | +161 | +196 | +177 | +225 | +562 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__pca16` | matched/correlation | -458.2 | [-2,958.9, +1,153.0] | -1,682 | +254 | +192 | +211 | +136 | +432 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__pca16` | median/diagonal | +2,188.4 | [+1,164.2, +3,705.3] | +1,122 | +10 | +8 | +143 | +226 | +680 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +1,438.0 | [+1,124.9, +1,808.1] | +253 | +189 | +205 | +167 | +216 | +407 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -540.8 | [-2,840.3, +923.9] | -1,578 | +249 | +189 | +167 | +135 | +298 |
| support 32 decoded | `histories@support32@decoded__limix__late` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +1,394.2 | [+869.8, +2,092.3] | +514 | +101 | +29 | +95 | +214 | +442 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@decoded__direct` | matched/diagonal | +3,204.5 | [+2,179.2, +4,908.0] | +1,155 | +372 | +332 | +352 | +334 | +659 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@decoded__direct` | matched/correlation | -2,091.1 | [-7,775.5, +1,546.3] | -4,007 | +564 | +289 | +480 | +158 | +425 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@decoded__direct` | median/diagonal | +2,511.6 | [+1,567.0, +4,019.0] | +956 | +238 | +148 | +265 | +335 | +570 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__pca16` | matched/diagonal | +3,543.9 | [+2,427.5, +5,380.5] | +1,205 | +382 | +455 | +410 | +321 | +771 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__pca16` | matched/correlation | -1,924.6 | [-7,777.7, +1,854.8] | -4,140 | +592 | +406 | +534 | +160 | +524 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__pca16` | median/diagonal | +3,265.8 | [+2,174.7, +5,018.6] | +1,198 | +270 | +309 | +385 | +313 | +791 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +3,179.7 | [+2,254.5, +4,659.0] | +976 | +410 | +464 | +401 | +312 | +616 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -2,007.2 | [-7,683.6, +1,656.7] | -4,036 | +588 | +403 | +490 | +158 | +390 |
| support 32 decoded | `histories@support32@decoded__tabfm__late` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +2,471.6 | [+1,795.4, +3,440.5] | +589 | +360 | +330 | +337 | +302 | +553 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random__late` | matched/diagonal | +7,932.5 | [+4,987.6, +13,023.5] | +3,597 | +864 | +903 | +776 | +498 | +1,295 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random__late` | matched/correlation | +1,641.2 | [-2,491.4, +4,636.6] | -2,483 | +1,095 | +815 | +971 | +305 | +938 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random__late` | median/diagonal | +9,748.2 | [+6,149.6, +15,956.5] | +4,425 | +1,047 | +1,023 | +946 | +695 | +1,613 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random43__late` | matched/diagonal | +7,932.5 | [+4,987.6, +13,023.5] | +3,597 | +864 | +903 | +776 | +498 | +1,295 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random43__late` | matched/correlation | +1,641.2 | [-2,491.4, +4,636.6] | -2,483 | +1,095 | +815 | +971 | +305 | +938 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random43__late` | median/diagonal | +9,748.2 | [+6,149.6, +15,956.5] | +4,425 | +1,047 | +1,023 | +946 | +695 | +1,613 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random44__late` | matched/diagonal | +7,932.5 | [+4,987.6, +13,023.5] | +3,597 | +864 | +903 | +776 | +498 | +1,295 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random44__late` | matched/correlation | +1,641.2 | [-2,491.4, +4,636.6] | -2,483 | +1,095 | +815 | +971 | +305 | +938 |
| support 32 decoded | `histories@support32@decoded__kumo__late` | `histories@support32@decoded__kumo_random44__late` | median/diagonal | +9,748.2 | [+6,149.6, +15,956.5] | +4,425 | +1,047 | +1,023 | +946 | +695 | +1,613 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random43__late` | matched/diagonal | +1,395.2 | [+872.2, +1,880.8] | -66 | +339 | +333 | +206 | +122 | +462 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random43__late` | matched/correlation | -1,322.6 | [-5,080.2, +1,100.7] | -2,670 | +395 | +309 | +277 | +45 | +322 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random43__late` | median/diagonal | +1,124.6 | [+148.4, +1,912.8] | -552 | +412 | +336 | +241 | +169 | +519 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random44__late` | matched/diagonal | +1,498.0 | [+891.1, +2,034.0] | -133 | +379 | +384 | +217 | +146 | +506 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random44__late` | matched/correlation | -1,267.5 | [-5,164.1, +1,292.5] | -2,818 | +447 | +358 | +319 | +62 | +365 |
| support 32 decoded | `histories@support32@decoded__tabpfn_full__late` | `histories@support32@decoded__tabpfn_full_random44__late` | median/diagonal | +1,145.3 | [-17.6, +2,073.1] | -716 | +465 | +384 | +253 | +197 | +563 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,319.3 | [+1,392.7, +3,877.3] | +1,039 | +225 | +158 | +201 | +233 | +462 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,119.8 | [-4,515.6, +1,070.1] | -2,360 | +376 | +143 | +303 | +107 | +311 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,645.9 | [+707.3, +3,154.7] | +937 | +45 | -21 | +104 | +214 | +367 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | matched/diagonal | +2,658.8 | [+1,662.7, +4,333.7] | +1,088 | +235 | +281 | +260 | +220 | +574 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | matched/correlation | -953.3 | [-4,540.8, +1,379.9] | -2,493 | +404 | +259 | +358 | +109 | +410 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__pca16` | median/diagonal | +2,400.0 | [+1,317.9, +4,145.2] | +1,179 | +77 | +140 | +224 | +193 | +588 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | matched/diagonal | +2,294.5 | [+1,496.8, +3,617.5] | +859 | +263 | +290 | +251 | +211 | +419 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | matched/correlation | -1,035.9 | [-4,403.3, +1,178.5] | -2,389 | +400 | +256 | +314 | +107 | +276 |
| support 32 decoded | `histories@support32@decoded__tabfm__early_concat` | `histories@support32@decoded__supervised_mlp16` | median/diagonal | +1,605.8 | [+988.2, +2,552.6] | +571 | +167 | +161 | +176 | +181 | +350 |
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
| support 64 native | `histories@support64__kumo__late` | `histories__direct` | matched/diagonal | -1,887.9 | [-3,778.5, -836.3] | -1,161 | -212 | -167 | -149 | -3 | -196 |
| support 64 native | `histories@support64__kumo__late` | `histories__direct` | matched/correlation | -385.9 | [-1,020.9, +317.6] | +329 | -272 | -131 | -235 | +37 | -113 |
| support 64 native | `histories@support64__kumo__late` | `histories__direct` | median/diagonal | -1,110.5 | [-2,669.8, -246.4] | -770 | -110 | -57 | -88 | +62 | -147 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__pca16` | matched/diagonal | -2,203.6 | [-4,507.2, -923.2] | -1,463 | -216 | -151 | -141 | -13 | -220 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__pca16` | matched/correlation | -337.2 | [-1,088.7, +519.2] | +426 | -301 | -119 | -253 | +34 | -125 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__pca16` | median/diagonal | -1,474.3 | [-3,364.7, -438.2] | -1,042 | -120 | -84 | -106 | +50 | -172 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__supervised_mlp16` | matched/diagonal | +1,377.1 | [+1,093.2, +1,804.1] | +384 | +168 | +151 | +172 | +182 | +320 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__supervised_mlp16` | matched/correlation | +841.4 | [+545.1, +1,086.7] | -46 | +177 | +142 | +166 | +133 | +270 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__supervised_mlp16` | median/diagonal | +2,680.1 | [+1,807.1, +4,151.3] | +974 | +315 | +310 | +199 | +304 | +579 |
| support 64 native | `histories@support64__limix__late` | `histories__direct` | matched/diagonal | -1,541.0 | [-2,864.0, -785.2] | -886 | -200 | -141 | -167 | +14 | -162 |
| support 64 native | `histories@support64__limix__late` | `histories__direct` | matched/correlation | -712.5 | [-1,290.1, -275.9] | -157 | -218 | -102 | -183 | +48 | -101 |
| support 64 native | `histories@support64__limix__late` | `histories__direct` | median/diagonal | -1,888.2 | [-3,586.7, -929.6] | -1,127 | -192 | -163 | -205 | -1 | -200 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__pca16` | matched/diagonal | -1,856.7 | [-3,584.2, -871.2] | -1,188 | -204 | -125 | -159 | +4 | -186 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__pca16` | matched/correlation | -663.7 | [-1,254.2, -143.5] | -59 | -247 | -89 | -201 | +45 | -113 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__pca16` | median/diagonal | -2,252.1 | [-4,289.2, -1,094.9] | -1,399 | -203 | -191 | -222 | -13 | -225 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__supervised_mlp16` | matched/diagonal | +1,724.0 | [+1,146.7, +2,702.5] | +659 | +179 | +177 | +154 | +200 | +354 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__supervised_mlp16` | matched/correlation | +514.9 | [-339.8, +1,138.1] | -532 | +232 | +171 | +218 | +144 | +282 |
| support 64 native | `histories@support64__limix__late` | `histories@support64__supervised_mlp16` | median/diagonal | +1,902.4 | [+1,050.7, +3,252.0] | +617 | +232 | +204 | +83 | +241 | +526 |
| support 64 native | `histories@support64__tabfm__late` | `histories__direct` | matched/diagonal | -2,135.1 | [-4,055.7, -1,078.0] | -1,202 | -211 | -196 | -194 | -38 | -294 |
| support 64 native | `histories@support64__tabfm__late` | `histories__direct` | matched/correlation | -438.5 | [-1,152.1, +394.8] | +461 | -286 | -159 | -275 | +15 | -195 |
| support 64 native | `histories@support64__tabfm__late` | `histories__direct` | median/diagonal | -1,278.4 | [-2,714.7, -463.4] | -686 | -100 | -125 | -143 | +7 | -231 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__pca16` | matched/diagonal | -2,450.8 | [-4,774.6, -1,161.8] | -1,504 | -216 | -180 | -185 | -48 | -318 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__pca16` | matched/correlation | -389.7 | [-1,232.1, +620.4] | +559 | -315 | -147 | -293 | +12 | -206 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__pca16` | median/diagonal | -1,642.2 | [-3,412.2, -669.8] | -958 | -111 | -152 | -161 | -5 | -256 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__supervised_mlp16` | matched/diagonal | +1,129.8 | [+875.6, +1,521.4] | +343 | +168 | +122 | +128 | +148 | +222 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__supervised_mlp16` | matched/correlation | +788.9 | [+622.8, +958.1] | +87 | +164 | +114 | +125 | +111 | +188 |
| support 64 native | `histories@support64__tabfm__late` | `histories@support64__supervised_mlp16` | median/diagonal | +2,512.2 | [+1,589.2, +4,095.6] | +1,058 | +324 | +242 | +144 | +250 | +495 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random__late` | matched/diagonal | +4,890.0 | [+2,663.9, +8,512.4] | +2,976 | +323 | +418 | +374 | +266 | +533 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random__late` | matched/correlation | +3,341.4 | [+2,254.3, +5,061.7] | +1,480 | +389 | +401 | +424 | +220 | +428 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random__late` | median/diagonal | +6,687.2 | [+3,707.6, +11,545.7] | +3,988 | +459 | +581 | +506 | +413 | +741 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random43__late` | matched/diagonal | +4,890.0 | [+2,663.9, +8,512.4] | +2,976 | +323 | +418 | +374 | +266 | +533 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random43__late` | matched/correlation | +3,341.4 | [+2,254.3, +5,061.7] | +1,480 | +389 | +401 | +424 | +220 | +428 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random43__late` | median/diagonal | +6,687.2 | [+3,707.6, +11,545.7] | +3,988 | +459 | +581 | +506 | +413 | +741 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random44__late` | matched/diagonal | +4,890.0 | [+2,663.9, +8,512.4] | +2,976 | +323 | +418 | +374 | +266 | +533 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random44__late` | matched/correlation | +3,341.4 | [+2,254.3, +5,061.7] | +1,480 | +389 | +401 | +424 | +220 | +428 |
| support 64 native | `histories@support64__kumo__late` | `histories@support64__kumo_random44__late` | median/diagonal | +6,687.2 | [+3,707.6, +11,545.7] | +3,988 | +459 | +581 | +506 | +413 | +741 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random43__late` | matched/diagonal | +1,427.0 | [+698.9, +2,521.6] | +970 | +46 | +100 | +38 | +109 | +163 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random43__late` | matched/correlation | +590.1 | [+129.5, +915.4] | +33 | +104 | +109 | +126 | +95 | +122 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random43__late` | median/diagonal | +2,944.6 | [+1,629.6, +5,005.0] | +1,778 | +165 | +234 | +147 | +250 | +370 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random44__late` | matched/diagonal | +1,548.6 | [+756.6, +2,749.4] | +1,047 | +60 | +120 | +37 | +115 | +170 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random44__late` | matched/correlation | +645.2 | [+208.5, +968.8] | +49 | +117 | +128 | +126 | +97 | +128 |
| support 64 native | `histories@support64__tabpfn_full__late` | `histories@support64__tabpfn_full_random44__late` | median/diagonal | +2,903.7 | [+1,588.8, +4,971.3] | +1,770 | +160 | +232 | +133 | +246 | +363 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | matched/diagonal | -571.3 | [-1,175.0, -204.5] | -290 | -116 | -50 | -52 | +21 | -85 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | matched/correlation | +197.2 | [-284.7, +835.9] | +470 | -145 | -23 | -112 | +53 | -46 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories__direct` | median/diagonal | -971.3 | [-1,819.8, -483.2] | -431 | -88 | -112 | -129 | -40 | -171 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | matched/diagonal | -887.0 | [-1,876.8, -325.0] | -592 | -120 | -34 | -44 | +11 | -108 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | matched/correlation | +246.0 | [-366.7, +1,088.3] | +568 | -174 | -11 | -130 | +50 | -57 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__pca16` | median/diagonal | -1,335.2 | [-2,504.8, -686.9] | -703 | -99 | -140 | -146 | -52 | -196 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | matched/diagonal | +2,693.6 | [+1,703.5, +4,433.3] | +1,255 | +263 | +268 | +270 | +207 | +431 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | matched/correlation | +1,424.5 | [+936.9, +1,934.3] | +95 | +305 | +250 | +289 | +149 | +337 |
| support 64 native | `histories@support64__tabfm__early_concat` | `histories@support64__supervised_mlp16` | median/diagonal | +2,819.3 | [+1,589.4, +5,014.3] | +1,313 | +336 | +255 | +158 | +203 | +555 |
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
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@decoded__direct` | matched/diagonal | +3,342.2 | [+2,357.2, +4,907.8] | +1,047 | +374 | +430 | +369 | +343 | +779 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@decoded__direct` | matched/correlation | -1,499.2 | [-6,613.2, +1,826.2] | -3,622 | +561 | +373 | +476 | +170 | +542 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@decoded__direct` | median/diagonal | +2,797.0 | [+1,806.3, +4,297.6] | +935 | +218 | +227 | +279 | +402 | +737 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__pca16` | matched/diagonal | +3,701.5 | [+2,625.4, +5,391.1] | +1,084 | +374 | +566 | +444 | +372 | +862 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__pca16` | matched/correlation | -512.1 | [-4,434.1, +2,234.6] | -2,921 | +580 | +501 | +524 | +193 | +611 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__pca16` | median/diagonal | +4,293.8 | [+2,891.4, +6,558.8] | +1,729 | +260 | +429 | +435 | +510 | +930 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +3,983.8 | [+2,788.5, +5,881.7] | +1,251 | +448 | +596 | +430 | +328 | +932 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -1,285.0 | [-6,673.6, +2,288.7] | -3,838 | +647 | +522 | +542 | +167 | +675 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +3,529.3 | [+2,506.2, +5,032.9] | +919 | +378 | +476 | +400 | +375 | +980 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@decoded__direct` | matched/diagonal | +1,488.2 | [+1,002.8, +2,116.6] | +466 | +149 | +15 | +139 | +225 | +493 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@decoded__direct` | matched/correlation | -259.4 | [-2,116.0, +924.1] | -1,161 | +215 | +15 | +170 | +124 | +377 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@decoded__direct` | median/diagonal | +1,048.9 | [+339.9, +1,930.2] | +575 | -39 | -218 | +23 | +230 | +477 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__pca16` | matched/diagonal | +1,847.5 | [+1,320.9, +2,554.8] | +503 | +149 | +152 | +214 | +254 | +576 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__pca16` | matched/correlation | +727.7 | [-111.4, +1,443.3] | -459 | +235 | +142 | +218 | +147 | +446 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__pca16` | median/diagonal | +2,545.8 | [+1,431.1, +4,143.4] | +1,370 | +4 | -16 | +180 | +338 | +670 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +2,129.8 | [+1,487.8, +3,037.8] | +670 | +223 | +181 | +200 | +210 | +646 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -45.2 | [-2,173.5, +1,363.1] | -1,377 | +301 | +163 | +236 | +121 | +510 |
| support 64 decoded | `histories@support64@decoded__limix__late` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +1,781.3 | [+1,127.1, +2,617.0] | +560 | +122 | +31 | +144 | +203 | +721 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@decoded__direct` | matched/diagonal | +3,123.2 | [+2,144.1, +4,656.1] | +943 | +358 | +366 | +389 | +323 | +743 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@decoded__direct` | matched/correlation | -2,154.9 | [-7,993.2, +1,634.3] | -4,179 | +551 | +312 | +522 | +144 | +495 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@decoded__direct` | median/diagonal | +2,375.9 | [+1,483.6, +3,689.4] | +707 | +196 | +184 | +296 | +322 | +670 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__pca16` | matched/diagonal | +3,482.6 | [+2,398.9, +5,127.0] | +980 | +358 | +503 | +464 | +352 | +825 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__pca16` | matched/correlation | -1,167.8 | [-5,828.2, +2,017.1] | -3,478 | +570 | +440 | +569 | +166 | +564 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__pca16` | median/diagonal | +3,872.8 | [+2,576.8, +5,953.7] | +1,501 | +239 | +385 | +453 | +431 | +863 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +3,764.8 | [+2,574.0, +5,616.4] | +1,147 | +432 | +532 | +450 | +308 | +896 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -1,940.6 | [-8,055.0, +2,081.3] | -4,395 | +637 | +461 | +588 | +141 | +628 |
| support 64 decoded | `histories@support64@decoded__tabfm__late` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +3,108.2 | [+2,138.9, +4,447.8] | +692 | +357 | +433 | +418 | +296 | +914 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random__late` | matched/diagonal | +8,677.3 | [+5,348.1, +14,430.9] | +4,057 | +847 | +1,030 | +826 | +520 | +1,397 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random__late` | matched/correlation | +1,390.3 | [-3,370.3, +4,816.5] | -3,017 | +1,138 | +922 | +1,043 | +306 | +998 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random__late` | median/diagonal | +10,791.1 | [+6,598.3, +18,083.0] | +5,162 | +1,038 | +1,165 | +973 | +732 | +1,721 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random43__late` | matched/diagonal | +8,677.3 | [+5,348.1, +14,430.9] | +4,057 | +847 | +1,030 | +826 | +520 | +1,397 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random43__late` | matched/correlation | +1,390.3 | [-3,370.3, +4,816.5] | -3,017 | +1,138 | +922 | +1,043 | +306 | +998 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random43__late` | median/diagonal | +10,791.1 | [+6,598.3, +18,083.0] | +5,162 | +1,038 | +1,165 | +973 | +732 | +1,721 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random44__late` | matched/diagonal | +8,677.3 | [+5,348.1, +14,430.9] | +4,057 | +847 | +1,030 | +826 | +520 | +1,397 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random44__late` | matched/correlation | +1,390.3 | [-3,370.3, +4,816.5] | -3,017 | +1,138 | +922 | +1,043 | +306 | +998 |
| support 64 decoded | `histories@support64@decoded__kumo__late` | `histories@support64@decoded__kumo_random44__late` | median/diagonal | +10,791.1 | [+6,598.3, +18,083.0] | +5,162 | +1,038 | +1,165 | +973 | +732 | +1,721 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random43__late` | matched/diagonal | +1,540.0 | [+1,137.8, +1,992.4] | +210 | +316 | +307 | +155 | +153 | +400 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random43__late` | matched/correlation | -946.0 | [-3,882.7, +987.1] | -2,129 | +372 | +258 | +232 | +56 | +266 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random43__late` | median/diagonal | +1,250.5 | [+755.9, +1,701.2] | -177 | +333 | +290 | +142 | +218 | +444 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random44__late` | matched/diagonal | +1,066.6 | [+382.8, +1,646.9] | -349 | +318 | +363 | +147 | +128 | +460 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random44__late` | matched/correlation | -1,065.1 | [-4,302.4, +1,089.0] | -2,381 | +400 | +315 | +247 | +44 | +310 |
| support 64 decoded | `histories@support64@decoded__tabpfn_full__late` | `histories@support64@decoded__tabpfn_full_random44__late` | median/diagonal | +653.1 | [-659.5, +1,614.1] | -867 | +348 | +355 | +130 | +187 | +501 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,654.9 | [+1,677.7, +4,296.5] | +1,058 | +286 | +263 | +227 | +277 | +544 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,474.1 | [-5,651.7, +1,226.0] | -2,967 | +428 | +240 | +335 | +132 | +358 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +2,066.1 | [+1,032.5, +3,769.7] | +1,016 | +121 | +80 | +129 | +258 | +462 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | matched/diagonal | +3,014.3 | [+1,951.2, +4,757.5] | +1,095 | +286 | +399 | +302 | +305 | +627 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | matched/correlation | -486.9 | [-3,480.4, +1,643.6] | -2,266 | +448 | +367 | +383 | +154 | +427 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__pca16` | median/diagonal | +3,562.9 | [+2,088.3, +6,033.0] | +1,811 | +164 | +282 | +285 | +366 | +655 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | matched/diagonal | +3,296.5 | [+2,111.5, +5,254.4] | +1,262 | +359 | +428 | +288 | +262 | +697 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | matched/correlation | -1,259.8 | [-5,738.6, +1,683.8] | -3,183 | +514 | +389 | +401 | +129 | +491 |
| support 64 decoded | `histories@support64@decoded__tabfm__early_concat` | `histories@support64@decoded__supervised_mlp16` | median/diagonal | +2,798.4 | [+1,747.5, +4,478.6] | +1,001 | +282 | +329 | +250 | +231 | +706 |
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
| support 128 native | `histories@support128__kumo__late` | `histories__direct` | matched/diagonal | -1,863.8 | [-3,734.7, -835.9] | -1,081 | -210 | -175 | -149 | -21 | -229 |
| support 128 native | `histories@support128__kumo__late` | `histories__direct` | matched/correlation | -332.9 | [-1,006.7, +458.5] | +446 | -277 | -141 | -242 | +26 | -144 |
| support 128 native | `histories@support128__kumo__late` | `histories__direct` | median/diagonal | -1,025.9 | [-2,520.3, -166.9] | -608 | -99 | -77 | -79 | +10 | -173 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__pca16` | matched/diagonal | -2,136.3 | [-4,408.7, -883.3] | -1,380 | -196 | -176 | -130 | -15 | -239 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__pca16` | matched/correlation | -236.7 | [-994.9, +663.4] | +536 | -279 | -142 | -237 | +35 | -149 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__pca16` | median/diagonal | -1,417.3 | [-3,333.0, -371.2] | -936 | -106 | -103 | -82 | +2 | -192 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__supervised_mlp16` | matched/diagonal | +1,379.5 | [+1,033.1, +1,930.1] | +412 | +170 | +132 | +182 | +179 | +304 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__supervised_mlp16` | matched/correlation | +592.1 | [+73.9, +978.7] | -278 | +183 | +120 | +179 | +139 | +249 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__supervised_mlp16` | median/diagonal | +2,374.1 | [+1,410.3, +3,991.5] | +865 | +283 | +156 | +219 | +298 | +552 |
| support 128 native | `histories@support128__limix__late` | `histories__direct` | matched/diagonal | -1,604.6 | [-3,000.6, -807.6] | -922 | -211 | -139 | -166 | +19 | -185 |
| support 128 native | `histories@support128__limix__late` | `histories__direct` | matched/correlation | -632.2 | [-1,174.9, -163.7] | -41 | -241 | -97 | -185 | +51 | -119 |
| support 128 native | `histories@support128__limix__late` | `histories__direct` | median/diagonal | -1,953.6 | [-3,643.4, -999.7] | -1,107 | -212 | -164 | -200 | -9 | -262 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__pca16` | matched/diagonal | -1,877.1 | [-3,694.1, -844.7] | -1,222 | -197 | -140 | -148 | +24 | -195 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__pca16` | matched/correlation | -536.0 | [-1,097.9, +3.1] | +49 | -243 | -98 | -180 | +60 | -124 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__pca16` | median/diagonal | -2,345.0 | [-4,456.8, -1,151.1] | -1,434 | -219 | -191 | -203 | -17 | -281 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__supervised_mlp16` | matched/diagonal | +1,638.8 | [+1,032.2, +2,660.2] | +571 | +169 | +167 | +164 | +218 | +348 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__supervised_mlp16` | matched/correlation | +292.7 | [-764.1, +1,071.9] | -765 | +219 | +165 | +236 | +164 | +274 |
| support 128 native | `histories@support128__limix__late` | `histories@support128__supervised_mlp16` | median/diagonal | +1,446.4 | [+441.9, +2,901.4] | +367 | +171 | +69 | +98 | +279 | +463 |
| support 128 native | `histories@support128__tabfm__late` | `histories__direct` | matched/diagonal | -2,150.8 | [-4,197.2, -1,038.3] | -1,243 | -193 | -201 | -182 | -55 | -276 |
| support 128 native | `histories@support128__tabfm__late` | `histories__direct` | matched/correlation | -363.1 | [-1,098.7, +515.0] | +518 | -273 | -162 | -265 | +3 | -183 |
| support 128 native | `histories@support128__tabfm__late` | `histories__direct` | median/diagonal | -1,489.3 | [-3,222.3, -534.5] | -855 | -94 | -125 | -146 | -34 | -236 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__pca16` | matched/diagonal | -2,423.2 | [-4,889.0, -1,073.4] | -1,543 | -180 | -202 | -164 | -49 | -286 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__pca16` | matched/correlation | -266.9 | [-1,088.5, +727.2] | +608 | -275 | -164 | -260 | +12 | -189 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__pca16` | median/diagonal | -1,880.7 | [-4,020.0, -716.2] | -1,182 | -102 | -151 | -148 | -42 | -255 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__supervised_mlp16` | matched/diagonal | +1,092.6 | [+820.5, +1,480.3] | +250 | +187 | +106 | +148 | +145 | +257 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__supervised_mlp16` | matched/correlation | +561.9 | [+173.7, +869.2] | -206 | +187 | +99 | +156 | +116 | +209 |
| support 128 native | `histories@support128__tabfm__late` | `histories@support128__supervised_mlp16` | median/diagonal | +1,910.6 | [+1,035.2, +3,291.0] | +619 | +288 | +108 | +153 | +254 | +489 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random__late` | matched/diagonal | +4,914.0 | [+2,632.2, +8,570.9] | +3,056 | +325 | +410 | +374 | +249 | +500 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random__late` | matched/correlation | +3,394.5 | [+2,236.6, +5,213.4] | +1,597 | +383 | +390 | +417 | +210 | +397 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random__late` | median/diagonal | +6,771.8 | [+3,687.4, +11,725.2] | +4,149 | +470 | +561 | +515 | +361 | +715 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random43__late` | matched/diagonal | +4,914.0 | [+2,632.2, +8,570.9] | +3,056 | +325 | +410 | +374 | +249 | +500 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random43__late` | matched/correlation | +3,394.5 | [+2,236.6, +5,213.4] | +1,597 | +383 | +390 | +417 | +210 | +397 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random43__late` | median/diagonal | +6,771.8 | [+3,687.4, +11,725.2] | +4,149 | +470 | +561 | +515 | +361 | +715 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random44__late` | matched/diagonal | +4,914.0 | [+2,632.2, +8,570.9] | +3,056 | +325 | +410 | +374 | +249 | +500 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random44__late` | matched/correlation | +3,394.5 | [+2,236.6, +5,213.4] | +1,597 | +383 | +390 | +417 | +210 | +397 |
| support 128 native | `histories@support128__kumo__late` | `histories@support128__kumo_random44__late` | median/diagonal | +6,771.8 | [+3,687.4, +11,725.2] | +4,149 | +470 | +561 | +515 | +361 | +715 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random43__late` | matched/diagonal | +1,099.7 | [+674.5, +1,685.0] | +608 | +36 | +122 | +74 | +118 | +141 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random43__late` | matched/correlation | +354.1 | [-377.4, +777.5] | -192 | +75 | +130 | +134 | +100 | +108 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random43__late` | median/diagonal | +2,668.7 | [+1,640.4, +4,240.4] | +1,450 | +156 | +266 | +202 | +257 | +337 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random44__late` | matched/diagonal | +1,361.2 | [+763.9, +2,216.8] | +822 | +48 | +136 | +82 | +127 | +146 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random44__late` | matched/correlation | +480.8 | [-154.9, +867.9] | -118 | +91 | +145 | +143 | +106 | +114 |
| support 128 native | `histories@support128__tabpfn_full__late` | `histories@support128__tabpfn_full_random44__late` | median/diagonal | +2,732.8 | [+1,618.1, +4,438.6] | +1,544 | +155 | +264 | +194 | +255 | +321 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | matched/diagonal | -236.8 | [-647.1, +40.6] | -116 | -66 | -10 | -42 | +23 | -27 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | matched/correlation | +441.3 | [-58.4, +1,131.0] | +558 | -97 | +14 | -88 | +51 | +4 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories__direct` | median/diagonal | -950.6 | [-1,799.3, -470.5] | -431 | -86 | -93 | -123 | -65 | -154 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | matched/diagonal | -509.2 | [-1,285.4, -68.7] | -415 | -52 | -11 | -23 | +29 | -37 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | matched/correlation | +537.5 | [-53.8, +1,387.1] | +649 | -99 | +12 | -83 | +59 | -1 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__pca16` | median/diagonal | -1,342.0 | [-2,603.8, -656.4] | -758 | -93 | -119 | -125 | -73 | -173 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | matched/diagonal | +3,006.6 | [+1,847.2, +5,071.1] | +1,377 | +314 | +297 | +289 | +223 | +506 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | matched/correlation | +1,366.2 | [+680.8, +1,987.3] | -166 | +363 | +275 | +333 | +163 | +397 |
| support 128 native | `histories@support128__tabfm__early_concat` | `histories@support128__supervised_mlp16` | median/diagonal | +2,449.4 | [+1,120.4, +4,711.5] | +1,043 | +297 | +140 | +176 | +223 | +571 |
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
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@decoded__direct` | matched/diagonal | +2,922.8 | [+2,140.2, +4,109.8] | +792 | +362 | +395 | +318 | +332 | +724 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@decoded__direct` | matched/correlation | -1,607.6 | [-6,651.8, +1,642.6] | -3,540 | +521 | +334 | +423 | +165 | +489 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@decoded__direct` | median/diagonal | +2,412.5 | [+1,632.2, +3,537.3] | +703 | +204 | +204 | +266 | +360 | +675 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__pca16` | matched/diagonal | +3,173.1 | [+2,347.2, +4,317.9] | +702 | +404 | +511 | +412 | +342 | +803 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__pca16` | matched/correlation | -1,255.1 | [-6,271.6, +2,031.3] | -3,515 | +580 | +449 | +494 | +188 | +548 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__pca16` | median/diagonal | +3,368.4 | [+2,507.8, +4,525.2] | +1,039 | +304 | +406 | +425 | +351 | +843 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +3,194.0 | [+2,346.1, +4,342.5] | +620 | +375 | +531 | +549 | +346 | +773 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -1,540.8 | [-6,934.2, +2,014.0] | -3,879 | +552 | +455 | +591 | +184 | +556 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,939.1 | [+2,129.9, +3,808.4] | +213 | +297 | +434 | +620 | +402 | +975 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@decoded__direct` | matched/diagonal | +2,059.5 | [+1,188.3, +3,431.5] | +1,061 | +141 | +81 | +165 | +184 | +427 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@decoded__direct` | matched/correlation | -169.9 | [-1,833.5, +867.9] | -1,021 | +190 | +69 | +156 | +106 | +330 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@decoded__direct` | median/diagonal | +1,914.9 | [+614.1, +3,925.4] | +1,421 | -44 | -133 | +79 | +183 | +408 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__pca16` | matched/diagonal | +2,309.8 | [+1,522.1, +3,547.8] | +970 | +182 | +197 | +259 | +194 | +507 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__pca16` | matched/correlation | +182.6 | [-1,447.9, +1,253.5] | -996 | +250 | +185 | +227 | +129 | +389 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__pca16` | median/diagonal | +2,870.8 | [+1,550.8, +4,797.1] | +1,757 | +56 | +69 | +238 | +174 | +576 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +2,330.6 | [+1,545.9, +3,620.3] | +888 | +154 | +217 | +396 | +199 | +477 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -103.0 | [-2,103.1, +1,226.6] | -1,361 | +221 | +191 | +324 | +125 | +398 |
| support 128 decoded | `histories@support128@decoded__limix__late` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,441.5 | [+1,475.3, +3,913.5] | +930 | +49 | +97 | +433 | +225 | +708 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@decoded__direct` | matched/diagonal | +3,031.8 | [+2,121.0, +4,398.7] | +846 | +369 | +374 | +362 | +315 | +766 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@decoded__direct` | matched/correlation | -2,013.8 | [-7,720.8, +1,676.2] | -4,033 | +565 | +323 | +491 | +135 | +506 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@decoded__direct` | median/diagonal | +2,277.5 | [+1,477.5, +3,392.0] | +592 | +239 | +181 | +263 | +302 | +701 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__pca16` | matched/diagonal | +3,282.1 | [+2,322.9, +4,603.8] | +755 | +410 | +490 | +456 | +325 | +846 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__pca16` | matched/correlation | -1,661.3 | [-7,307.2, +2,065.4] | -4,008 | +624 | +439 | +562 | +157 | +565 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__pca16` | median/diagonal | +3,233.4 | [+2,328.5, +4,412.9] | +928 | +339 | +383 | +422 | +293 | +869 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +3,302.9 | [+2,322.1, +4,630.6] | +673 | +382 | +510 | +593 | +329 | +816 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -1,946.9 | [-7,988.2, +2,045.9] | -4,373 | +595 | +444 | +659 | +154 | +573 |
| support 128 decoded | `histories@support128@decoded__tabfm__late` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,804.2 | [+1,902.4, +3,731.4] | +102 | +331 | +410 | +616 | +344 | +1,001 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random__late` | matched/diagonal | +8,257.9 | [+5,156.1, +13,618.9] | +3,803 | +835 | +995 | +776 | +508 | +1,341 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random__late` | matched/correlation | +1,281.9 | [-3,421.2, +4,638.3] | -2,934 | +1,098 | +882 | +990 | +301 | +945 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random__late` | median/diagonal | +10,406.6 | [+6,421.4, +17,308.3] | +4,931 | +1,025 | +1,141 | +961 | +689 | +1,659 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random43__late` | matched/diagonal | +8,257.9 | [+5,156.1, +13,618.9] | +3,803 | +835 | +995 | +776 | +508 | +1,341 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random43__late` | matched/correlation | +1,281.9 | [-3,421.2, +4,638.3] | -2,934 | +1,098 | +882 | +990 | +301 | +945 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random43__late` | median/diagonal | +10,406.6 | [+6,421.4, +17,308.3] | +4,931 | +1,025 | +1,141 | +961 | +689 | +1,659 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random44__late` | matched/diagonal | +8,257.9 | [+5,156.1, +13,618.9] | +3,803 | +835 | +995 | +776 | +508 | +1,341 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random44__late` | matched/correlation | +1,281.9 | [-3,421.2, +4,638.3] | -2,934 | +1,098 | +882 | +990 | +301 | +945 |
| support 128 decoded | `histories@support128@decoded__kumo__late` | `histories@support128@decoded__kumo_random44__late` | median/diagonal | +10,406.6 | [+6,421.4, +17,308.3] | +4,931 | +1,025 | +1,141 | +961 | +689 | +1,659 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random43__late` | matched/diagonal | +1,354.1 | [+959.2, +1,733.8] | +7 | +252 | +290 | +206 | +149 | +450 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random43__late` | matched/correlation | -534.8 | [-2,959.3, +1,055.3] | -1,699 | +298 | +255 | +235 | +57 | +319 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random43__late` | median/diagonal | +1,232.3 | [+663.8, +1,727.6] | -236 | +251 | +300 | +221 | +195 | +502 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random44__late` | matched/diagonal | +1,136.3 | [+630.1, +1,597.2] | -228 | +244 | +320 | +194 | +161 | +445 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random44__late` | matched/correlation | -528.9 | [-2,946.6, +1,066.4] | -1,716 | +282 | +285 | +238 | +62 | +320 |
| support 128 decoded | `histories@support128@decoded__tabpfn_full__late` | `histories@support128@decoded__tabpfn_full_random44__late` | median/diagonal | +887.7 | [-12.9, +1,595.3] | -580 | +234 | +324 | +212 | +208 | +491 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,439.5 | [+1,573.0, +3,843.5] | +877 | +250 | +309 | +233 | +221 | +549 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,449.1 | [-5,592.4, +1,234.0] | -2,923 | +406 | +277 | +340 | +95 | +355 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,658.7 | [+879.9, +2,878.8] | +675 | +87 | +139 | +117 | +195 | +446 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | matched/diagonal | +2,689.8 | [+1,794.7, +4,026.7] | +787 | +292 | +425 | +326 | +231 | +629 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | matched/correlation | -1,096.6 | [-5,211.6, +1,633.6] | -2,898 | +465 | +393 | +411 | +118 | +414 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__pca16` | median/diagonal | +2,614.6 | [+1,741.3, +3,830.7] | +1,010 | +187 | +341 | +276 | +186 | +614 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | matched/diagonal | +2,710.6 | [+1,787.3, +4,056.0] | +705 | +263 | +445 | +463 | +235 | +599 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | matched/correlation | -1,382.2 | [-5,888.1, +1,599.5] | -3,263 | +437 | +399 | +508 | +114 | +422 |
| support 128 decoded | `histories@support128@decoded__tabfm__early_concat` | `histories@support128@decoded__supervised_mlp16` | median/diagonal | +2,185.3 | [+1,390.4, +3,047.4] | +184 | +180 | +368 | +470 | +237 | +746 |
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
| support 256 native | `histories__kumo__late` | `histories__direct` | matched/diagonal | -1,819.1 | [-3,570.4, -851.9] | -1,002 | -217 | -141 | -170 | -32 | -258 |
| support 256 native | `histories__kumo__late` | `histories__direct` | matched/correlation | -383.2 | [-1,051.6, +393.1] | +422 | -281 | -113 | -258 | +17 | -171 |
| support 256 native | `histories__kumo__late` | `histories__direct` | median/diagonal | -815.2 | [-2,096.3, -13.2] | -409 | -107 | -61 | -94 | +29 | -173 |
| support 256 native | `histories__kumo__late` | `histories__pca16` | matched/diagonal | -1,840.5 | [-3,684.5, -821.6] | -1,079 | -215 | -131 | -140 | -27 | -249 |
| support 256 native | `histories__kumo__late` | `histories__pca16` | matched/correlation | -414.5 | [-1,080.3, +326.3] | +345 | -281 | -104 | -237 | +23 | -161 |
| support 256 native | `histories__kumo__late` | `histories__pca16` | median/diagonal | -1,032.1 | [-2,517.0, -158.5] | -577 | -111 | -82 | -97 | +21 | -187 |
| support 256 native | `histories__kumo__late` | `histories__supervised_mlp16` | matched/diagonal | +1,501.1 | [+1,057.4, +2,198.1] | +623 | +148 | +159 | +156 | +156 | +260 |
| support 256 native | `histories__kumo__late` | `histories__supervised_mlp16` | matched/correlation | +659.9 | [+262.3, +936.9] | -127 | +162 | +140 | +153 | +122 | +210 |
| support 256 native | `histories__kumo__late` | `histories__supervised_mlp16` | median/diagonal | +2,451.3 | [+1,587.1, +3,911.4] | +1,011 | +226 | +141 | +202 | +350 | +522 |
| support 256 native | `histories__limix__late` | `histories__direct` | matched/diagonal | -1,480.0 | [-2,733.0, -758.6] | -832 | -207 | -119 | -167 | +17 | -172 |
| support 256 native | `histories__limix__late` | `histories__direct` | matched/correlation | -650.6 | [-1,180.0, -209.2] | -86 | -234 | -78 | -187 | +48 | -113 |
| support 256 native | `histories__limix__late` | `histories__direct` | median/diagonal | -1,833.4 | [-3,388.8, -946.9] | -1,029 | -214 | -141 | -189 | -10 | -251 |
| support 256 native | `histories__limix__late` | `histories__pca16` | matched/diagonal | -1,501.3 | [-2,850.9, -721.9] | -909 | -205 | -109 | -137 | +22 | -164 |
| support 256 native | `histories__limix__late` | `histories__pca16` | matched/correlation | -681.8 | [-1,253.3, -229.0] | -163 | -233 | -70 | -167 | +54 | -104 |
| support 256 native | `histories__limix__late` | `histories__pca16` | median/diagonal | -2,050.3 | [-3,819.0, -1,042.7] | -1,197 | -218 | -162 | -191 | -18 | -264 |
| support 256 native | `histories__limix__late` | `histories__supervised_mlp16` | matched/diagonal | +1,840.2 | [+1,171.4, +3,015.7] | +793 | +158 | +181 | +159 | +204 | +345 |
| support 256 native | `histories__limix__late` | `histories__supervised_mlp16` | matched/correlation | +392.6 | [-567.8, +1,081.8] | -635 | +209 | +174 | +224 | +153 | +267 |
| support 256 native | `histories__limix__late` | `histories__supervised_mlp16` | median/diagonal | +1,433.1 | [+656.6, +2,599.7] | +391 | +119 | +60 | +108 | +311 | +444 |
| support 256 native | `histories__tabfm__late` | `histories__direct` | matched/diagonal | -1,997.7 | [-3,946.0, -932.8] | -1,165 | -196 | -144 | -172 | -50 | -270 |
| support 256 native | `histories__tabfm__late` | `histories__direct` | matched/correlation | -238.6 | [-998.9, +682.8] | +578 | -275 | -115 | -257 | +7 | -178 |
| support 256 native | `histories__tabfm__late` | `histories__direct` | median/diagonal | -1,247.5 | [-2,767.2, -379.1] | -684 | -94 | -87 | -132 | -29 | -222 |
| support 256 native | `histories__tabfm__late` | `histories__pca16` | matched/diagonal | -2,019.1 | [-4,065.5, -894.1] | -1,242 | -194 | -134 | -142 | -45 | -261 |
| support 256 native | `histories__tabfm__late` | `histories__pca16` | matched/correlation | -269.9 | [-1,008.1, +600.0] | +501 | -274 | -106 | -237 | +14 | -168 |
| support 256 native | `histories__tabfm__late` | `histories__pca16` | median/diagonal | -1,464.4 | [-3,197.0, -500.4] | -852 | -98 | -108 | -134 | -37 | -236 |
| support 256 native | `histories__tabfm__late` | `histories__supervised_mlp16` | matched/diagonal | +1,322.5 | [+1,002.2, +1,812.8] | +460 | +169 | +156 | +153 | +138 | +248 |
| support 256 native | `histories__tabfm__late` | `histories__supervised_mlp16` | matched/correlation | +804.5 | [+607.3, +975.2] | +30 | +168 | +138 | +154 | +112 | +203 |
| support 256 native | `histories__tabfm__late` | `histories__supervised_mlp16` | median/diagonal | +2,019.0 | [+1,305.9, +3,195.4] | +736 | +239 | +114 | +164 | +292 | +473 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random__late` | matched/diagonal | +4,958.7 | [+2,604.0, +8,745.2] | +3,135 | +317 | +443 | +353 | +237 | +472 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random__late` | matched/correlation | +3,344.1 | [+2,197.1, +5,147.7] | +1,573 | +379 | +419 | +402 | +200 | +371 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random__late` | median/diagonal | +6,982.4 | [+3,737.0, +12,191.2] | +4,349 | +461 | +577 | +500 | +380 | +715 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random43__late` | matched/diagonal | +4,958.7 | [+2,604.0, +8,745.2] | +3,135 | +317 | +443 | +353 | +237 | +472 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random43__late` | matched/correlation | +3,344.1 | [+2,197.1, +5,147.7] | +1,573 | +379 | +419 | +402 | +200 | +371 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random43__late` | median/diagonal | +6,982.4 | [+3,737.0, +12,191.2] | +4,349 | +461 | +577 | +500 | +380 | +715 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random44__late` | matched/diagonal | +4,958.7 | [+2,604.0, +8,745.2] | +3,135 | +317 | +443 | +353 | +237 | +472 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random44__late` | matched/correlation | +3,344.1 | [+2,197.1, +5,147.7] | +1,573 | +379 | +419 | +402 | +200 | +371 |
| support 256 native | `histories__kumo__late` | `histories__kumo_random44__late` | median/diagonal | +6,982.4 | [+3,737.0, +12,191.2] | +4,349 | +461 | +577 | +500 | +380 | +715 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random43__late` | matched/diagonal | +637.1 | [+407.7, +903.9] | +233 | +42 | +152 | +44 | +80 | +86 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random43__late` | matched/correlation | +275.6 | [-396.9, +680.6] | -156 | +59 | +155 | +90 | +72 | +56 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random43__late` | median/diagonal | +2,501.0 | [+1,571.7, +3,895.3] | +1,329 | +149 | +288 | +198 | +221 | +315 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random44__late` | matched/diagonal | +954.3 | [+588.3, +1,431.2] | +517 | +42 | +168 | +48 | +89 | +90 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random44__late` | matched/correlation | +423.4 | [-118.1, +783.1] | -54 | +68 | +173 | +97 | +77 | +63 |
| support 256 native | `histories__tabpfn_full__late` | `histories__tabpfn_full_random44__late` | median/diagonal | +2,553.8 | [+1,528.7, +4,106.6] | +1,442 | +135 | +285 | +184 | +217 | +292 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | matched/diagonal | +106.5 | [-208.9, +322.9] | -81 | -6 | +67 | +19 | +48 | +60 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | matched/correlation | +778.7 | [+279.8, +1,523.6] | +616 | -26 | +75 | -18 | +65 | +67 |
| support 256 native | `histories__tabfm__early_concat` | `histories__direct` | median/diagonal | -918.4 | [-1,755.2, -443.7] | -544 | -73 | -58 | -89 | -38 | -116 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | matched/diagonal | +85.2 | [-312.0, +343.5] | -158 | -4 | +77 | +49 | +53 | +68 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | matched/correlation | +747.4 | [+302.8, +1,426.9] | +539 | -25 | +84 | +2 | +71 | +77 |
| support 256 native | `histories__tabfm__early_concat` | `histories__pca16` | median/diagonal | -1,135.3 | [-2,192.8, -535.2] | -713 | -77 | -78 | -92 | -46 | -130 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/diagonal | +3,426.7 | [+2,190.8, +5,593.2] | +1,543 | +359 | +367 | +345 | +236 | +577 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | matched/correlation | +1,821.8 | [+1,159.9, +2,497.9] | +68 | +417 | +328 | +393 | +169 | +447 |
| support 256 native | `histories__tabfm__early_concat` | `histories__supervised_mlp16` | median/diagonal | +2,348.1 | [+1,244.1, +4,205.4] | +875 | +260 | +144 | +207 | +283 | +579 |
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
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__direct` | matched/diagonal | +3,312.7 | [+2,300.8, +4,941.2] | +1,099 | +406 | +429 | +308 | +337 | +734 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__direct` | matched/correlation | -2,028.1 | [-7,773.4, +1,657.9] | -4,055 | +578 | +377 | +443 | +165 | +465 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__direct` | median/diagonal | +2,871.1 | [+1,808.0, +4,556.7] | +1,084 | +248 | +261 | +241 | +358 | +680 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__pca16` | matched/diagonal | +3,845.2 | [+2,698.4, +5,676.3] | +1,295 | +434 | +534 | +401 | +355 | +827 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__pca16` | matched/correlation | -1,982.9 | [-8,211.1, +1,990.2] | -4,322 | +628 | +482 | +506 | +187 | +536 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__pca16` | median/diagonal | +4,215.7 | [+2,791.5, +6,492.0] | +1,683 | +379 | +429 | +455 | +373 | +895 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__supervised_mlp16` | matched/diagonal | +4,417.4 | [+2,826.5, +7,133.4] | +1,810 | +421 | +600 | +413 | +341 | +832 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__supervised_mlp16` | matched/correlation | -2,033.3 | [-8,297.4, +2,066.7] | -4,493 | +661 | +527 | +564 | +171 | +535 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__supervised_mlp16` | median/diagonal | +9,217.0 | [+4,461.1, +17,493.2] | +5,639 | +473 | +707 | +589 | +466 | +1,344 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__direct` | matched/diagonal | +1,697.0 | [+1,031.1, +2,694.6] | +712 | +39 | +110 | +134 | +238 | +464 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__direct` | matched/correlation | -437.5 | [-2,433.9, +855.7] | -1,333 | +142 | +106 | +165 | +127 | +356 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__direct` | median/diagonal | +1,336.1 | [+352.5, +2,761.2] | +928 | -179 | -115 | +32 | +249 | +421 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__pca16` | matched/diagonal | +2,229.5 | [+1,435.6, +3,418.0] | +907 | +67 | +216 | +227 | +256 | +556 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__pca16` | matched/correlation | -392.3 | [-2,882.4, +1,184.9] | -1,599 | +192 | +210 | +229 | +149 | +427 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__pca16` | median/diagonal | +2,680.6 | [+1,351.4, +4,656.9] | +1,528 | -47 | +53 | +247 | +264 | +636 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__supervised_mlp16` | matched/diagonal | +2,801.6 | [+1,561.0, +4,899.3] | +1,423 | +55 | +281 | +239 | +241 | +562 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__supervised_mlp16` | matched/correlation | -442.7 | [-2,991.6, +1,271.2] | -1,770 | +225 | +256 | +287 | +133 | +426 |
| support 256 decoded | `histories@decoded__limix__late` | `histories@decoded__supervised_mlp16` | median/diagonal | +7,681.9 | [+3,017.1, +15,690.3] | +5,484 | +46 | +330 | +380 | +356 | +1,085 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__direct` | matched/diagonal | +3,317.0 | [+2,383.4, +4,772.5] | +989 | +420 | +422 | +376 | +323 | +788 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__direct` | matched/correlation | -2,374.7 | [-8,763.3, +1,739.5] | -4,538 | +626 | +363 | +526 | +134 | +515 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__direct` | median/diagonal | +2,553.3 | [+1,753.6, +3,718.8] | +730 | +292 | +241 | +284 | +302 | +705 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__pca16` | matched/diagonal | +3,849.5 | [+2,785.1, +5,507.2] | +1,184 | +448 | +528 | +469 | +341 | +880 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__pca16` | matched/correlation | -2,329.5 | [-9,200.2, +2,069.1] | -4,804 | +676 | +467 | +590 | +156 | +586 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__pca16` | median/diagonal | +3,897.9 | [+2,739.4, +5,643.6] | +1,329 | +423 | +409 | +498 | +317 | +920 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__supervised_mlp16` | matched/diagonal | +4,421.7 | [+2,918.8, +6,967.7] | +1,700 | +435 | +593 | +481 | +326 | +886 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__supervised_mlp16` | matched/correlation | -2,380.0 | [-9,306.9, +2,158.5] | -4,975 | +709 | +513 | +648 | +140 | +585 |
| support 256 decoded | `histories@decoded__tabfm__late` | `histories@decoded__supervised_mlp16` | median/diagonal | +8,899.2 | [+4,454.2, +16,585.8] | +5,285 | +517 | +687 | +632 | +410 | +1,369 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random__late` | matched/diagonal | +8,647.8 | [+5,285.1, +14,461.6] | +4,110 | +879 | +1,029 | +765 | +514 | +1,351 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random__late` | matched/correlation | +861.4 | [-4,529.3, +4,617.0] | -3,450 | +1,155 | +925 | +1,010 | +300 | +921 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random__late` | median/diagonal | +10,865.2 | [+6,560.9, +18,357.7] | +5,311 | +1,069 | +1,199 | +935 | +688 | +1,664 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random43__late` | matched/diagonal | +8,647.8 | [+5,285.1, +14,461.6] | +4,110 | +879 | +1,029 | +765 | +514 | +1,351 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random43__late` | matched/correlation | +861.4 | [-4,529.3, +4,617.0] | -3,450 | +1,155 | +925 | +1,010 | +300 | +921 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random43__late` | median/diagonal | +10,865.2 | [+6,560.9, +18,357.7] | +5,311 | +1,069 | +1,199 | +935 | +688 | +1,664 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random44__late` | matched/diagonal | +8,647.8 | [+5,285.1, +14,461.6] | +4,110 | +879 | +1,029 | +765 | +514 | +1,351 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random44__late` | matched/correlation | +861.4 | [-4,529.3, +4,617.0] | -3,450 | +1,155 | +925 | +1,010 | +300 | +921 |
| support 256 decoded | `histories@decoded__kumo__late` | `histories@decoded__kumo_random44__late` | median/diagonal | +10,865.2 | [+6,560.9, +18,357.7] | +5,311 | +1,069 | +1,199 | +935 | +688 | +1,664 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random43__late` | matched/diagonal | +1,379.7 | [+1,072.8, +1,702.4] | +129 | +212 | +396 | +199 | +109 | +335 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random43__late` | matched/correlation | -140.4 | [-1,944.9, +1,050.3] | -1,216 | +235 | +351 | +219 | +41 | +229 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random43__late` | median/diagonal | +1,330.3 | [+959.0, +1,691.5] | -45 | +185 | +445 | +219 | +146 | +380 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random44__late` | matched/diagonal | +1,443.8 | [+1,115.2, +1,787.7] | +153 | +194 | +397 | +223 | +124 | +352 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random44__late` | matched/correlation | -168.5 | [-2,139.3, +1,125.4] | -1,319 | +245 | +355 | +252 | +55 | +244 |
| support 256 decoded | `histories@decoded__tabpfn_full__late` | `histories@decoded__tabpfn_full_random44__late` | median/diagonal | +1,401.4 | [+1,014.2, +1,768.9] | -20 | +163 | +433 | +259 | +165 | +400 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/diagonal | +2,581.3 | [+1,708.1, +3,995.2] | +932 | +283 | +324 | +217 | +241 | +583 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | matched/correlation | -1,278.9 | [-5,289.8, +1,325.4] | -2,819 | +424 | +289 | +329 | +110 | +389 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__direct` | median/diagonal | +1,913.6 | [+1,082.3, +3,216.2] | +797 | +118 | +173 | +116 | +214 | +496 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | matched/diagonal | +3,113.8 | [+2,109.1, +4,739.3] | +1,128 | +311 | +430 | +310 | +259 | +676 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | matched/correlation | -1,233.7 | [-5,722.0, +1,653.4] | -3,086 | +474 | +393 | +392 | +132 | +460 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__pca16` | median/diagonal | +3,258.1 | [+2,056.6, +5,148.2] | +1,396 | +249 | +341 | +331 | +229 | +712 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | matched/diagonal | +3,686.0 | [+2,217.2, +6,188.2] | +1,643 | +299 | +495 | +322 | +245 | +682 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | matched/correlation | -1,284.1 | [-5,824.7, +1,755.7] | -3,257 | +507 | +439 | +451 | +117 | +459 |
| support 256 decoded | `histories@decoded__tabfm__early_concat` | `histories@decoded__supervised_mlp16` | median/diagonal | +8,259.4 | [+3,723.2, +16,155.5] | +5,352 | +343 | +619 | +464 | +322 | +1,160 |
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
| `tabfm__late` | -3,091.7 | — | — | — | — | — | -4,543.0 |
| `tabpfn_full__late` | -225.8 | — | — | — | — | — | -4,544.7 |
| `exaone__late` | — | — | — | — | — | — | — |
| `kumo__late` | -2,431.6 | — | — | — | — | — | -4,544.2 |
| `limix__late` | +1,827.1 | — | — | — | — | — | -4,558.8 |
| `supervised_mlp16` | -51.7 | — | — | — | — | — | -4,578.5 |

### matched kernel, diagonal innovations

| Representation | native | redraw 1 | redraw 2 | shared cap/assets | shared income/assets | both shared | decoded |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `direct` | +2,187.1 | — | — | — | — | — | +295.9 |
| `tabfm__early_concat` | +2,293.6 | — | — | — | — | — | +2,877.2 |
| `tabfm__late` | +189.4 | — | — | — | — | — | +3,612.9 |
| `tabpfn_full__late` | +716.7 | — | — | — | — | — | +3,331.0 |
| `exaone__late` | — | — | — | — | — | — | — |
| `kumo__late` | +368.0 | — | — | — | — | — | +3,608.6 |
| `limix__late` | +707.1 | — | — | — | — | — | +1,992.9 |
| `supervised_mlp16` | -1,133.1 | — | — | — | — | — | -808.8 |

Decoders: out-of-fold R^2 of the rank-5 reference exposures (mean over
years, median in brackets), and the Spearman correlation between decoded and
target distances. Exposure and distance reliability diagnostics are 0.90
and 0.77; a ceiling interpretation needs a noise model.

| Representation | Out-of-fold R^2 | Distance Spearman |
| --- | ---: | ---: |
| `direct` | 0.092 [0.086] | 0.220 |
| `pca16` | 0.059 [0.071] | 0.175 |
| `supervised_mlp16` | 0.059 [0.059] | 0.160 |
| `tabpfn_full__late` | 0.282 [0.307] | 0.371 |
| `tabpfn_full_random__late` | 0.189 [0.218] | 0.276 |
| `tabpfn_full_random43__late` | 0.194 [0.213] | 0.278 |
| `tabpfn_full_random44__late` | 0.188 [0.199] | 0.279 |
| `tabfm__early_concat` | 0.224 [0.245] | 0.349 |
| `tabfm__late` | 0.292 [0.315] | 0.388 |
| `kumo__late` | 0.291 [0.320] | 0.389 |
| `kumo__early_concat` | 0.295 [0.313] | 0.404 |
| `kumo_random__late` | -0.005 [-0.005] | 0.009 |
| `kumo_random43__late` | -0.005 [-0.005] | 0.009 |
| `kumo_random44__late` | -0.005 [-0.005] | 0.009 |
| `limix__late` | 0.195 [0.220] | 0.262 |

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
| `tabpfn_full_random43__late` | 0.221 | 0.194 | 0.172 |
| `tabpfn_full_random44__late` | 0.215 | 0.188 | 0.166 |
| `tabfm__early_concat` | 0.252 | 0.224 | 0.201 |
| `tabfm__late` | 0.326 | 0.292 | 0.262 |
| `kumo__late` | 0.326 | 0.291 | 0.261 |
| `kumo__early_concat` | 0.330 | 0.295 | 0.264 |
| `kumo_random__late` | -0.006 | -0.005 | -0.005 |
| `kumo_random43__late` | -0.006 | -0.005 | -0.005 |
| `kumo_random44__late` | -0.006 | -0.005 | -0.005 |
| `limix__late` | 0.223 | 0.195 | 0.172 |

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
| `tabpfn_full__late` | +363.1 | +641.6 | +540.1 | +716.7 |
| `tabpfn_full_random__late` | -1,045.8 | -1,101.6 | -829.2 | -32.1 |
| `tabpfn_full_random43__late` | -934.0 | -785.5 | -559.7 | +79.6 |
| `tabpfn_full_random44__late` | -991.4 | -907.0 | -821.1 | -237.6 |
| `tabfm__early_concat` | +1,506.6 | +1,615.8 | +1,950.3 | +2,293.6 |
| `tabfm__late` | -19.6 | +52.0 | +36.3 | +189.4 |
| `kumo__late` | +115.5 | +299.2 | +323.3 | +368.0 |
| `kumo__early_concat` | +1,022.6 | +1,839.1 | +1,870.7 | +1,890.4 |
| `kumo_random__late` | -4,590.8 | -4,590.8 | -4,590.8 | -4,590.8 |
| `kumo_random43__late` | -4,590.8 | -4,590.8 | -4,590.8 | -4,590.8 |
| `kumo_random44__late` | -4,590.8 | -4,590.8 | -4,590.8 | -4,590.8 |
| `limix__late` | +922.3 | +646.1 | +582.5 | +707.1 |

### Decoded distance

| Representation | 32 rows | 64 rows | 128 rows | 256 rows |
| --- | ---: | ---: | ---: | ---: |
| `direct` | +295.9 | +295.9 | +295.9 | +295.9 |
| `pca16` | -43.6 | -63.5 | +45.6 | -236.6 |
| `supervised_mlp16` | +320.7 | -345.7 | +24.8 | -808.8 |
| `tabpfn_full__late` | +3,293.4 | +3,396.6 | +3,281.8 | +3,331.0 |
| `tabpfn_full_random__late` | +1,633.6 | +1,702.6 | +1,993.7 | +1,859.7 |
| `tabpfn_full_random43__late` | +1,898.2 | +1,856.6 | +1,927.7 | +1,951.3 |
| `tabpfn_full_random44__late` | +1,795.4 | +2,330.1 | +2,145.6 | +1,887.2 |
| `tabfm__early_concat` | +2,615.2 | +2,950.8 | +2,735.4 | +2,877.2 |
| `tabfm__late` | +3,500.4 | +3,419.1 | +3,327.7 | +3,612.9 |
| `kumo__late` | +2,893.3 | +3,638.1 | +3,218.7 | +3,608.6 |
| `kumo__early_concat` | +3,548.3 | +3,843.3 | +3,750.7 | +3,936.8 |
| `kumo_random__late` | -5,039.2 | -5,039.2 | -5,039.2 | -5,039.2 |
| `kumo_random43__late` | -5,039.2 | -5,039.2 | -5,039.2 | -5,039.2 |
| `kumo_random44__late` | -5,039.2 | -5,039.2 | -5,039.2 | -5,039.2 |
| `limix__late` | +1,758.7 | +1,784.1 | +2,355.4 | +1,992.9 |

### Decoder quality

Mean out-of-fold R^2 (median in brackets) against the rank-5 reference
target. Reliability diagnostics are 0.90 for exposure agreement and
0.77 for distance agreement. A ceiling interpretation needs a noise model.

| Representation | 32 rows | 64 rows | 128 rows | 256 rows |
| --- | ---: | ---: | ---: | ---: |
| `direct` | 0.092 [0.086] | 0.092 [0.086] | 0.092 [0.086] | 0.092 [0.086] |
| `pca16` | 0.070 [0.079] | 0.062 [0.053] | 0.055 [0.048] | 0.059 [0.071] |
| `supervised_mlp16` | 0.076 [0.071] | 0.054 [0.056] | 0.065 [0.070] | 0.059 [0.059] |
| `tabpfn_full__late` | 0.280 [0.304] | 0.283 [0.302] | 0.285 [0.297] | 0.282 [0.307] |
| `tabpfn_full_random__late` | 0.168 [0.165] | 0.179 [0.186] | 0.189 [0.196] | 0.189 [0.218] |
| `tabpfn_full_random43__late` | 0.183 [0.190] | 0.189 [0.205] | 0.188 [0.204] | 0.194 [0.213] |
| `tabpfn_full_random44__late` | 0.173 [0.167] | 0.179 [0.181] | 0.192 [0.205] | 0.188 [0.199] |
| `tabfm__early_concat` | 0.204 [0.218] | 0.218 [0.231] | 0.225 [0.250] | 0.224 [0.245] |
| `tabfm__late` | 0.265 [0.302] | 0.279 [0.304] | 0.291 [0.319] | 0.292 [0.315] |
| `kumo__late` | 0.273 [0.290] | 0.287 [0.310] | 0.284 [0.313] | 0.291 [0.320] |
| `kumo__early_concat` | 0.281 [0.305] | 0.293 [0.312] | 0.295 [0.310] | 0.295 [0.313] |
| `kumo_random__late` | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] |
| `kumo_random43__late` | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] |
| `kumo_random44__late` | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] | -0.005 [-0.005] |
| `limix__late` | 0.193 [0.189] | 0.196 [0.199] | 0.192 [0.178] | 0.195 [0.220] |

## Financial calibration sample size

Encoder support stays at 256 examples. Each fold uses a nested subset of
training firms; its held-out firms remain fixed. Annual decoder R^2 means:

| representation    |   32.0 |   64.0 |   128.0 |   256.0 |
|:------------------|-------:|-------:|--------:|--------:|
| direct            |  0.029 |  0.061 |   0.088 |   0.109 |
| kumo__late        |  0.050 |  0.145 |   0.216 |   0.278 |
| limix__late       | -0.005 |  0.077 |   0.122 |   0.176 |
| pca16             |  0.011 |  0.040 |   0.055 |   0.069 |
| supervised_mlp16  | -0.046 | -0.000 |   0.017 |   0.062 |
| tabfm__late       |  0.084 |  0.172 |   0.225 |   0.278 |
| tabpfn_full__late |  0.008 |  0.112 |   0.201 |   0.265 |

## Model confidence sets (size 0.10)

Families are networks within one kernel and innovation arm; covariance controls and
the uniform and zero networks enter every family of their arm. A set ranks within
its family only; choosing a family after seeing the results is not accounted for.

| Family | Members | Included |
| --- | ---: | --- |
| spherical/exp | 154 | `fernandez_market_cap_assets`, `fernandez_joint`, `histories__pca16`, `histories__limix__late`, `histories@support32__pca16`, `histories@support32__limix__late`, `histories@support64__pca16`, `histories@support64__limix__late`, `histories@support128__pca16`, `histories@support128__limix__late` |
| diagonal/exp | 157 | `histories__limix__late`, `histories@support32__pca16`, `histories@support32__limix__late`, `histories@support64__pca16`, `histories@support64__limix__late`, `histories@support128__pca16`, `histories@support128__limix__late` |
| correlation/exp | 157 | `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__limix__late`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__limix__late`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__limix__late`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__limix__late` |
| spherical/median | 154 | `covariance_exposures` |
| diagonal/median | 157 | `covariance_exposures`, `reference_exposures`, `histories@calibration32@decoded__supervised_mlp16`, `histories@decoded__tabpfn_full__late`, `histories@calibration64@decoded__tabpfn_full__late`, `histories@calibration128@decoded__tabpfn_full__late`, `histories@calibration256@decoded__tabpfn_full__late`, `histories@decoded__tabfm__late`, `histories@calibration32@decoded__tabfm__late`, `histories@calibration128@decoded__tabfm__late`, `histories@calibration256@decoded__tabfm__late`, `histories@decoded__kumo__late`, `histories@calibration32@decoded__kumo__late`, `histories@calibration64@decoded__kumo__late`, `histories@calibration128@decoded__kumo__late`, `histories@calibration256@decoded__kumo__late`, `histories@decoded__kumo__early_concat`, `histories@calibration64@decoded__limix__late`, `histories__pca16`, `histories@support32@decoded__tabpfn_full__late`, `histories@support32@decoded__tabfm__late`, `histories@support32@decoded__kumo__late`, `histories@support32@decoded__kumo__early_concat`, `histories@support32__pca16`, `histories@support64@decoded__tabpfn_full__late`, `histories@support64@decoded__tabpfn_full_random44__late`, `histories@support64@decoded__tabfm__late`, `histories@support64@decoded__kumo__late`, `histories@support64@decoded__kumo__early_concat`, `histories@support64__pca16`, `histories@support128@decoded__tabpfn_full__late`, `histories@support128@decoded__tabfm__late`, `histories@support128@decoded__kumo__late`, `histories@support128@decoded__kumo__early_concat`, `histories@support128@decoded__limix__late`, `histories@support128__pca16` |
| correlation/median | 157 | `covariance_exposures`, `reference_exposures`, `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories@decoded__direct`, `histories@calibration32@decoded__direct`, `histories@calibration64@decoded__direct`, `histories@calibration128@decoded__direct`, `histories@calibration256@decoded__direct`, `histories@decoded__pca16`, `histories@calibration32@decoded__pca16`, `histories@calibration64@decoded__pca16`, `histories@calibration128@decoded__pca16`, `histories@calibration256@decoded__pca16`, `histories@decoded__supervised_mlp16`, `histories@calibration32@decoded__supervised_mlp16`, `histories@calibration64@decoded__supervised_mlp16`, `histories@calibration128@decoded__supervised_mlp16`, `histories@calibration256@decoded__supervised_mlp16`, `histories@decoded__tabpfn_full__late`, `histories@calibration32@decoded__tabpfn_full__late`, `histories@calibration64@decoded__tabpfn_full__late`, `histories@calibration128@decoded__tabpfn_full__late`, `histories@calibration256@decoded__tabpfn_full__late`, `histories@decoded__tabpfn_full_random__late`, `histories@decoded__tabpfn_full_random43__late`, `histories@decoded__tabpfn_full_random44__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__late`, `histories@calibration32@decoded__tabfm__late`, `histories@calibration64@decoded__tabfm__late`, `histories@calibration128@decoded__tabfm__late`, `histories@calibration256@decoded__tabfm__late`, `histories@decoded__kumo__late`, `histories@calibration32@decoded__kumo__late`, `histories@calibration64@decoded__kumo__late`, `histories@calibration128@decoded__kumo__late`, `histories@calibration256@decoded__kumo__late`, `histories@decoded__kumo__early_concat`, `histories@decoded__kumo_random__late`, `histories@decoded__kumo_random43__late`, `histories@decoded__kumo_random44__late`, `histories@decoded__limix__late`, `histories@calibration32@decoded__limix__late`, `histories@calibration64@decoded__limix__late`, `histories@calibration128@decoded__limix__late`, `histories@calibration256@decoded__limix__late`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__tabpfn_full__late`, `histories__tabpfn_full_random__late`, `histories__tabpfn_full_random43__late`, `histories__tabpfn_full_random44__late`, `histories__tabfm__early_concat`, `histories__tabfm__late`, `histories__kumo__late`, `histories__kumo__early_concat`, `histories__kumo_random__late`, `histories__kumo_random43__late`, `histories__kumo_random44__late`, `histories__limix__late`, `histories@support32@decoded__pca16`, `histories@support32@decoded__supervised_mlp16`, `histories@support32@decoded__tabpfn_full__late`, `histories@support32@decoded__tabpfn_full_random__late`, `histories@support32@decoded__tabpfn_full_random43__late`, `histories@support32@decoded__tabpfn_full_random44__late`, `histories@support32@decoded__tabfm__early_concat`, `histories@support32@decoded__tabfm__late`, `histories@support32@decoded__kumo__late`, `histories@support32@decoded__kumo__early_concat`, `histories@support32@decoded__kumo_random__late`, `histories@support32@decoded__kumo_random43__late`, `histories@support32@decoded__kumo_random44__late`, `histories@support32@decoded__limix__late`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__tabpfn_full__late`, `histories@support32__tabpfn_full_random__late`, `histories@support32__tabpfn_full_random43__late`, `histories@support32__tabpfn_full_random44__late`, `histories@support32__tabfm__early_concat`, `histories@support32__tabfm__late`, `histories@support32__kumo__late`, `histories@support32__kumo__early_concat`, `histories@support32__kumo_random__late`, `histories@support32__kumo_random43__late`, `histories@support32__kumo_random44__late`, `histories@support32__limix__late`, `histories@support64@decoded__pca16`, `histories@support64@decoded__supervised_mlp16`, `histories@support64@decoded__tabpfn_full__late`, `histories@support64@decoded__tabpfn_full_random__late`, `histories@support64@decoded__tabpfn_full_random43__late`, `histories@support64@decoded__tabpfn_full_random44__late`, `histories@support64@decoded__tabfm__early_concat`, `histories@support64@decoded__tabfm__late`, `histories@support64@decoded__kumo__late`, `histories@support64@decoded__kumo__early_concat`, `histories@support64@decoded__kumo_random__late`, `histories@support64@decoded__kumo_random43__late`, `histories@support64@decoded__kumo_random44__late`, `histories@support64@decoded__limix__late`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__tabpfn_full__late`, `histories@support64__tabpfn_full_random__late`, `histories@support64__tabpfn_full_random43__late`, `histories@support64__tabpfn_full_random44__late`, `histories@support64__tabfm__early_concat`, `histories@support64__tabfm__late`, `histories@support64__kumo__late`, `histories@support64__kumo__early_concat`, `histories@support64__kumo_random__late`, `histories@support64__kumo_random43__late`, `histories@support64__kumo_random44__late`, `histories@support64__limix__late`, `histories@support128@decoded__pca16`, `histories@support128@decoded__supervised_mlp16`, `histories@support128@decoded__tabpfn_full__late`, `histories@support128@decoded__tabpfn_full_random__late`, `histories@support128@decoded__tabpfn_full_random43__late`, `histories@support128@decoded__tabpfn_full_random44__late`, `histories@support128@decoded__tabfm__early_concat`, `histories@support128@decoded__tabfm__late`, `histories@support128@decoded__kumo__late`, `histories@support128@decoded__kumo__early_concat`, `histories@support128@decoded__kumo_random__late`, `histories@support128@decoded__kumo_random43__late`, `histories@support128@decoded__kumo_random44__late`, `histories@support128@decoded__limix__late`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__tabpfn_full__late`, `histories@support128__tabpfn_full_random__late`, `histories@support128__tabpfn_full_random43__late`, `histories@support128__tabpfn_full_random44__late`, `histories@support128__tabfm__early_concat`, `histories@support128__tabfm__late`, `histories@support128__kumo__late`, `histories@support128__kumo__early_concat`, `histories@support128__kumo_random__late`, `histories@support128__kumo_random43__late`, `histories@support128__kumo_random44__late`, `histories@support128__limix__late`, `h3__fernandez_market_cap_assets`, `h3__fernandez_market_to_book`, `h3__fernandez_dividend_yield`, `h3__fernandez_joint`, `uniform_network` |
| spherical/matched | 154 | `reference_exposures` |
| diagonal/matched | 157 | `covariance_exposures`, `reference_exposures` |
| correlation/matched | 157 | `covariance_exposures`, `reference_exposures`, `fernandez_market_cap_assets`, `fernandez_market_to_book`, `fernandez_dividend_yield`, `fernandez_joint`, `histories@decoded__direct`, `histories@calibration32@decoded__direct`, `histories@calibration64@decoded__direct`, `histories@calibration128@decoded__direct`, `histories@calibration256@decoded__direct`, `histories@decoded__pca16`, `histories@calibration32@decoded__pca16`, `histories@calibration64@decoded__pca16`, `histories@calibration128@decoded__pca16`, `histories@calibration256@decoded__pca16`, `histories@decoded__supervised_mlp16`, `histories@calibration32@decoded__supervised_mlp16`, `histories@calibration64@decoded__supervised_mlp16`, `histories@calibration128@decoded__supervised_mlp16`, `histories@calibration256@decoded__supervised_mlp16`, `histories@decoded__tabpfn_full__late`, `histories@calibration32@decoded__tabpfn_full__late`, `histories@calibration64@decoded__tabpfn_full__late`, `histories@calibration128@decoded__tabpfn_full__late`, `histories@calibration256@decoded__tabpfn_full__late`, `histories@decoded__tabpfn_full_random__late`, `histories@decoded__tabpfn_full_random43__late`, `histories@decoded__tabpfn_full_random44__late`, `histories@decoded__tabfm__early_concat`, `histories@decoded__tabfm__late`, `histories@calibration32@decoded__tabfm__late`, `histories@calibration64@decoded__tabfm__late`, `histories@calibration128@decoded__tabfm__late`, `histories@calibration256@decoded__tabfm__late`, `histories@decoded__kumo__late`, `histories@calibration32@decoded__kumo__late`, `histories@calibration64@decoded__kumo__late`, `histories@calibration128@decoded__kumo__late`, `histories@calibration256@decoded__kumo__late`, `histories@decoded__kumo__early_concat`, `histories@decoded__limix__late`, `histories@calibration32@decoded__limix__late`, `histories@calibration64@decoded__limix__late`, `histories@calibration128@decoded__limix__late`, `histories@calibration256@decoded__limix__late`, `histories__direct`, `histories__pca16`, `histories__supervised_mlp16`, `histories__tabpfn_full__late`, `histories__tabpfn_full_random__late`, `histories__tabpfn_full_random43__late`, `histories__tabpfn_full_random44__late`, `histories__tabfm__early_concat`, `histories__tabfm__late`, `histories__kumo__late`, `histories__kumo__early_concat`, `histories__limix__late`, `histories@support32@decoded__pca16`, `histories@support32@decoded__supervised_mlp16`, `histories@support32@decoded__tabpfn_full__late`, `histories@support32@decoded__tabpfn_full_random__late`, `histories@support32@decoded__tabpfn_full_random43__late`, `histories@support32@decoded__tabpfn_full_random44__late`, `histories@support32@decoded__tabfm__early_concat`, `histories@support32@decoded__tabfm__late`, `histories@support32@decoded__kumo__late`, `histories@support32@decoded__kumo__early_concat`, `histories@support32@decoded__limix__late`, `histories@support32__pca16`, `histories@support32__supervised_mlp16`, `histories@support32__tabpfn_full__late`, `histories@support32__tabpfn_full_random__late`, `histories@support32__tabpfn_full_random43__late`, `histories@support32__tabpfn_full_random44__late`, `histories@support32__tabfm__early_concat`, `histories@support32__tabfm__late`, `histories@support32__kumo__late`, `histories@support32__kumo__early_concat`, `histories@support32__limix__late`, `histories@support64@decoded__pca16`, `histories@support64@decoded__supervised_mlp16`, `histories@support64@decoded__tabpfn_full__late`, `histories@support64@decoded__tabpfn_full_random__late`, `histories@support64@decoded__tabpfn_full_random43__late`, `histories@support64@decoded__tabpfn_full_random44__late`, `histories@support64@decoded__tabfm__early_concat`, `histories@support64@decoded__tabfm__late`, `histories@support64@decoded__kumo__late`, `histories@support64@decoded__kumo__early_concat`, `histories@support64@decoded__limix__late`, `histories@support64__pca16`, `histories@support64__supervised_mlp16`, `histories@support64__tabpfn_full__late`, `histories@support64__tabpfn_full_random__late`, `histories@support64__tabpfn_full_random43__late`, `histories@support64__tabpfn_full_random44__late`, `histories@support64__tabfm__early_concat`, `histories@support64__tabfm__late`, `histories@support64__kumo__late`, `histories@support64__kumo__early_concat`, `histories@support64__limix__late`, `histories@support128@decoded__pca16`, `histories@support128@decoded__supervised_mlp16`, `histories@support128@decoded__tabpfn_full__late`, `histories@support128@decoded__tabpfn_full_random__late`, `histories@support128@decoded__tabpfn_full_random43__late`, `histories@support128@decoded__tabpfn_full_random44__late`, `histories@support128@decoded__tabfm__early_concat`, `histories@support128@decoded__tabfm__late`, `histories@support128@decoded__kumo__late`, `histories@support128@decoded__kumo__early_concat`, `histories@support128@decoded__limix__late`, `histories@support128__pca16`, `histories@support128__supervised_mlp16`, `histories@support128__tabpfn_full__late`, `histories@support128__tabpfn_full_random__late`, `histories@support128__tabpfn_full_random43__late`, `histories@support128__tabpfn_full_random44__late`, `histories@support128__tabfm__early_concat`, `histories@support128__tabfm__late`, `histories@support128__kumo__late`, `histories@support128__kumo__early_concat`, `histories@support128__limix__late`, `h3__fernandez_market_cap_assets`, `h3__fernandez_market_to_book`, `h3__fernandez_dividend_yield`, `h3__fernandez_joint` |

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
| `histories@calibration128@decoded__direct` | 1.000 | 0.807 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration128@decoded__kumo__late` | 1.000 | 0.858 | 0.898 | 6.6e-10 | 0.0026 | 0.0026 |
| `histories@calibration128@decoded__limix__late` | 1.000 | 0.845 | 0.898 | 5.8e-10 | 0.0026 | 0.0026 |
| `histories@calibration128@decoded__pca16` | 1.000 | 0.793 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@calibration128@decoded__supervised_mlp16` | 1.000 | 0.772 | 0.898 | 1.5e-09 | 0.0027 | 0.0026 |
| `histories@calibration128@decoded__tabfm__late` | 1.000 | 0.866 | 0.898 | 8.3e-10 | 0.0026 | 0.0026 |
| `histories@calibration128@decoded__tabpfn_full__late` | 1.000 | 0.859 | 0.898 | 1.7e-09 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__direct` | 1.000 | 0.808 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__kumo__late` | 1.000 | 0.859 | 0.898 | 8.3e-10 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__limix__late` | 1.000 | 0.855 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__pca16` | 1.000 | 0.789 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__supervised_mlp16` | 1.000 | 0.792 | 0.898 | 1.2e-09 | 0.0027 | 0.0026 |
| `histories@calibration256@decoded__tabfm__late` | 1.000 | 0.864 | 0.898 | 9.9e-10 | 0.0026 | 0.0026 |
| `histories@calibration256@decoded__tabpfn_full__late` | 1.000 | 0.859 | 0.898 | 1.8e-09 | 0.0026 | 0.0026 |
| `histories@calibration32@decoded__direct` | 1.000 | 0.823 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@calibration32@decoded__kumo__late` | 1.000 | 0.851 | 0.898 | 7.2e-10 | 0.0026 | 0.0026 |
| `histories@calibration32@decoded__limix__late` | 1.000 | 0.825 | 0.898 | 9.4e-10 | 0.0027 | 0.0026 |
| `histories@calibration32@decoded__pca16` | 1.000 | 0.816 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration32@decoded__supervised_mlp16` | 1.000 | 0.791 | 0.898 | 6.9e-10 | 0.0027 | 0.0026 |
| `histories@calibration32@decoded__tabfm__late` | 1.000 | 0.871 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories@calibration32@decoded__tabpfn_full__late` | 1.000 | 0.836 | 0.898 | 5.1e-10 | 0.0027 | 0.0026 |
| `histories@calibration64@decoded__direct` | 1.000 | 0.819 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__kumo__late` | 1.000 | 0.860 | 0.898 | 3.7e-10 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__limix__late` | 1.000 | 0.825 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__pca16` | 1.000 | 0.809 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__supervised_mlp16` | 1.000 | 0.768 | 0.898 | 8.8e-10 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__tabfm__late` | 1.000 | 0.871 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@calibration64@decoded__tabpfn_full__late` | 1.000 | 0.855 | 0.898 | 9.3e-10 | 0.0026 | 0.0026 |
| `histories@decoded__direct` | 1.000 | 0.803 | 0.898 | 1.1e-09 | 0.0027 | 0.0026 |
| `histories@decoded__kumo__early_concat` | 1.000 | 0.862 | 0.898 | 8.2e-10 | 0.0026 | 0.0026 |
| `histories@decoded__kumo__late` | 1.000 | 0.859 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories@decoded__kumo_random43__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@decoded__kumo_random44__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@decoded__kumo_random__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@decoded__limix__late` | 1.000 | 0.858 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@decoded__pca16` | 1.000 | 0.790 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@decoded__supervised_mlp16` | 1.000 | 0.784 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabfm__early_concat` | 1.000 | 0.859 | 0.898 | 4.4e-10 | 0.0026 | 0.0026 |
| `histories@decoded__tabfm__late` | 1.000 | 0.863 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full__late` | 1.000 | 0.860 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full_random43__late` | 1.000 | 0.859 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full_random44__late` | 1.000 | 0.860 | 0.898 | 6.7e-10 | 0.0026 | 0.0026 |
| `histories@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.2e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__kumo__early_concat` | 1.000 | 0.863 | 0.898 | 8.7e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__kumo__late` | 1.000 | 0.858 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories@support128@decoded__kumo_random43__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__kumo_random44__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__kumo_random__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__limix__late` | 1.000 | 0.855 | 0.898 | 1.9e-09 | 0.0026 | 0.0026 |
| `histories@support128@decoded__pca16` | 1.000 | 0.788 | 0.898 | 1.3e-09 | 0.0027 | 0.0026 |
| `histories@support128@decoded__supervised_mlp16` | 1.000 | 0.795 | 0.898 | 1.2e-09 | 0.0027 | 0.0026 |
| `histories@support128@decoded__tabfm__early_concat` | 1.000 | 0.862 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabfm__late` | 1.000 | 0.861 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full__late` | 1.000 | 0.861 | 0.898 | 1.8e-09 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full_random43__late` | 1.000 | 0.859 | 0.898 | 7.7e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full_random44__late` | 1.000 | 0.858 | 0.898 | 5.8e-10 | 0.0026 | 0.0026 |
| `histories@support128@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.3e-10 | 0.0026 | 0.0026 |
| `histories@support128__kumo__early_concat` | 0.995 | 0.885 | 0.898 | 1.1e-10 | 0.0026 | 0.0026 |
| `histories@support128__kumo__late` | 0.982 | 0.817 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support128__kumo_random43__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support128__kumo_random44__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support128__kumo_random__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support128__limix__late` | 0.854 | 0.870 | 0.898 | 1.5e-11 | 0.0026 | 0.0026 |
| `histories@support128__pca16` | 0.909 | 0.855 | 0.898 | 7.3e-12 | 0.0026 | 0.0026 |
| `histories@support128__supervised_mlp16` | 0.788 | 0.644 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support128__tabfm__early_concat` | 0.973 | 0.893 | 0.898 | 4.4e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabfm__late` | 0.990 | 0.828 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full__late` | 0.942 | 0.840 | 0.898 | 9.9e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full_random43__late` | 0.999 | 0.915 | 0.898 | 1.2e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full_random44__late` | 0.999 | 0.907 | 0.898 | 5e-10 | 0.0026 | 0.0026 |
| `histories@support128__tabpfn_full_random__late` | 0.999 | 0.909 | 0.898 | 2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__kumo__early_concat` | 1.000 | 0.863 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__kumo__late` | 1.000 | 0.857 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__kumo_random43__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__kumo_random44__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__kumo_random__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__limix__late` | 1.000 | 0.853 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__pca16` | 1.000 | 0.791 | 0.898 | 3.3e-10 | 0.0027 | 0.0026 |
| `histories@support32@decoded__supervised_mlp16` | 1.000 | 0.799 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabfm__early_concat` | 1.000 | 0.859 | 0.898 | 5.7e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabfm__late` | 1.000 | 0.860 | 0.898 | 8.3e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full__late` | 1.000 | 0.859 | 0.898 | 2.1e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full_random43__late` | 1.000 | 0.864 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full_random44__late` | 1.000 | 0.863 | 0.898 | 8.5e-10 | 0.0026 | 0.0026 |
| `histories@support32@decoded__tabpfn_full_random__late` | 1.000 | 0.861 | 0.898 | 9.9e-10 | 0.0026 | 0.0026 |
| `histories@support32__kumo__early_concat` | 0.994 | 0.853 | 0.898 | 6.3e-10 | 0.0026 | 0.0026 |
| `histories@support32__kumo__late` | 0.974 | 0.819 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support32__kumo_random43__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support32__kumo_random44__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support32__kumo_random__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support32__limix__late` | 0.843 | 0.862 | 0.898 | 9.7e-13 | 0.0026 | 0.0026 |
| `histories@support32__pca16` | 0.909 | 0.866 | 0.898 | 1.9e-09 | 0.0026 | 0.0026 |
| `histories@support32__supervised_mlp16` | 0.764 | 0.660 | 0.898 | 4.2e-10 | 0.0026 | 0.0026 |
| `histories@support32__tabfm__early_concat` | 0.982 | 0.879 | 0.898 | 2.3e-10 | 0.0026 | 0.0026 |
| `histories@support32__tabfm__late` | 0.986 | 0.808 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full__late` | 0.927 | 0.817 | 0.898 | 1.3e-09 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full_random43__late` | 0.998 | 0.904 | 0.898 | 9.4e-10 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full_random44__late` | 0.998 | 0.896 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories@support32__tabpfn_full_random__late` | 0.999 | 0.904 | 0.898 | 5.4e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__kumo__early_concat` | 1.000 | 0.863 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__kumo__late` | 1.000 | 0.860 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__kumo_random43__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__kumo_random44__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__kumo_random__late` | 1.000 | 0.768 | 0.898 | 4.8e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__limix__late` | 1.000 | 0.857 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__pca16` | 1.000 | 0.789 | 0.898 | 6e-10 | 0.0028 | 0.0026 |
| `histories@support64@decoded__supervised_mlp16` | 1.000 | 0.791 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabfm__early_concat` | 1.000 | 0.860 | 0.898 | 7.3e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabfm__late` | 1.000 | 0.861 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full__late` | 1.000 | 0.861 | 0.898 | 2e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full_random43__late` | 1.000 | 0.858 | 0.898 | 9e-10 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full_random44__late` | 1.000 | 0.858 | 0.898 | 1.2e-09 | 0.0026 | 0.0026 |
| `histories@support64@decoded__tabpfn_full_random__late` | 1.000 | 0.859 | 0.898 | 8.1e-10 | 0.0026 | 0.0026 |
| `histories@support64__kumo__early_concat` | 0.995 | 0.872 | 0.898 | 4.2e-10 | 0.0026 | 0.0026 |
| `histories@support64__kumo__late` | 0.980 | 0.820 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories@support64__kumo_random43__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support64__kumo_random44__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support64__kumo_random__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories@support64__limix__late` | 0.850 | 0.866 | 0.898 | 6.5e-12 | 0.0026 | 0.0026 |
| `histories@support64__pca16` | 0.911 | 0.858 | 0.898 | 2.1e-09 | 0.0026 | 0.0026 |
| `histories@support64__supervised_mlp16` | 0.786 | 0.662 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories@support64__tabfm__early_concat` | 0.979 | 0.882 | 0.898 | 8.3e-11 | 0.0026 | 0.0026 |
| `histories@support64__tabfm__late` | 0.989 | 0.817 | 0.898 | 9.5e-10 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full__late` | 0.934 | 0.833 | 0.898 | 2.3e-11 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full_random43__late` | 0.999 | 0.908 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full_random44__late` | 0.998 | 0.899 | 0.898 | 4.7e-10 | 0.0026 | 0.0026 |
| `histories@support64__tabpfn_full_random__late` | 0.999 | 0.906 | 0.898 | 1.7e-09 | 0.0026 | 0.0026 |
| `histories__direct` | 0.925 | 0.864 | 0.898 | 1.1e-09 | 0.0026 | 0.0026 |
| `histories__kumo__early_concat` | 0.995 | 0.886 | 0.898 | 9.2e-10 | 0.0026 | 0.0026 |
| `histories__kumo__late` | 0.981 | 0.809 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories__kumo_random43__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories__kumo_random44__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories__kumo_random__late` | 1.000 | 1.000 | 1.000 | 51 | 0.0023 | 0.0026 |
| `histories__limix__late` | 0.852 | 0.871 | 0.898 | 9.4e-11 | 0.0026 | 0.0026 |
| `histories__pca16` | 0.913 | 0.853 | 0.898 | 3.3e-10 | 0.0026 | 0.0026 |
| `histories__supervised_mlp16` | 0.784 | 0.655 | 0.898 | 1.4e-09 | 0.0026 | 0.0026 |
| `histories__tabfm__early_concat` | 0.972 | 0.905 | 0.898 | 6.5e-12 | 0.0026 | 0.0026 |
| `histories__tabfm__late` | 0.990 | 0.829 | 0.898 | 3.1e-10 | 0.0026 | 0.0026 |
| `histories__tabpfn_full__late` | 0.938 | 0.841 | 0.898 | 4e-11 | 0.0026 | 0.0026 |
| `histories__tabpfn_full_random43__late` | 0.999 | 0.920 | 0.898 | 1e-09 | 0.0026 | 0.0026 |
| `histories__tabpfn_full_random44__late` | 0.999 | 0.911 | 0.898 | 1.5e-09 | 0.0026 | 0.0026 |
| `histories__tabpfn_full_random__late` | 0.999 | 0.914 | 0.898 | 3.4e-10 | 0.0026 | 0.0026 |
| `reference_exposures` | 1.000 | 0.860 | 0.898 | 1.6e-09 | 0.0026 | 0.0026 |
| `uniform_network` | nan | nan | nan | nan | nan | 0.0026 |

## Interpretation limits

Retrospective current-survivor sample; checkpoints postdate some evaluated dates.
Daily Gaussian densities are working models; differences are paired and dependent,
and many networks were compared. No row is a selected winner. Designs differ in
firms and cannot be ranked against each other.
