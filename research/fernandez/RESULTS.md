# Fernández comparison results

This is a US methodological replication and a retrospective forecasting extension.
The original Economatica sample is not reproduced. See [methods](README.md).

## Main comparisons

Counts below use mean held-out Gaussian loss; they are not significance tests.

| Benchmark | Learned configurations with lower mean loss |
| --- | ---: |
| sample_covariance | 0/16 |
| ff5_mom__diagonal | 0/16 |
| Same-factor Fernández: market_cap_assets | 0/16 |
| Same-factor Fernández: market_to_book | 0/16 |
| Same-factor Fernández: dividend_yield | 0/16 |
| Same-factor Fernández: debt_maturity | 16/16 |
| Same-factor Fernández: joint_rms | 0/16 |

These results do not establish an advantage for learned geometry. The small
complete-case cohort limits their interpretation; the older asset-history proxy
is not an adequate substitute for this comparison.

## Matched annual forecasting ladder

Completed 10 years; common annual samples range from 6 to 11 firms.
All 210 labeled distance matrices passed the artifact audit.

Lower Gaussian loss is better. Risk is annualized realized GMV volatility of
full excess returns; all covariances use the same training-only mean forecast.

| Model | Mean loss | GMV volatility |
| --- | ---: | ---: |
| capm__diagonal | -6.89113 | 16.45% |
| capm__four_plus_broad__autoencoder | -6.85815 | 16.58% |
| capm__four_plus_broad__direct | -6.85197 | 16.62% |
| capm__four_plus_broad__exaone | -6.85263 | 16.64% |
| capm__four_plus_broad__pca16 | -6.85781 | 16.54% |
| capm__four_plus_broad__random_autoencoder | -6.85115 | 16.61% |
| capm__four_plus_broad__tabfm | -6.85001 | 16.64% |
| capm__four_plus_broad__tabpfn_fast | -6.85411 | 16.65% |
| capm__four_plus_broad__tabpfn_full | -6.85617 | 16.66% |
| capm__paper__debt_maturity | -6.84511 | 16.77% |
| capm__paper__dividend_yield | -6.89482 | 16.55% |
| capm__paper__joint_rms | -6.86920 | 16.64% |
| capm__paper__market_cap_assets | -6.87831 | 16.54% |
| capm__paper__market_to_book | -6.87356 | 16.61% |
| capm__same_four_histories__autoencoder | -6.85723 | 16.72% |
| capm__same_four_histories__direct | -6.85826 | 16.65% |
| capm__same_four_histories__exaone | -6.85347 | 16.64% |
| capm__same_four_histories__pca16 | -6.85776 | 16.66% |
| capm__same_four_histories__random_autoencoder | -6.85407 | 16.68% |
| capm__same_four_histories__tabfm | -6.85126 | 16.65% |
| capm__same_four_histories__tabpfn_fast | -6.85504 | 16.65% |
| capm__same_four_histories__tabpfn_full | -6.85851 | 16.68% |
| capm__spherical | -6.83745 | 16.76% |
| ff5_mom__diagonal | -6.98962 | 16.38% |
| ff5_mom__four_plus_broad__autoencoder | -6.94396 | 16.25% |
| ff5_mom__four_plus_broad__direct | -6.94088 | 16.24% |
| ff5_mom__four_plus_broad__exaone | -6.93970 | 16.22% |
| ff5_mom__four_plus_broad__pca16 | -6.94369 | 16.23% |
| ff5_mom__four_plus_broad__random_autoencoder | -6.94010 | 16.23% |
| ff5_mom__four_plus_broad__tabfm | -6.93955 | 16.23% |
| ff5_mom__four_plus_broad__tabpfn_fast | -6.94009 | 16.22% |
| ff5_mom__four_plus_broad__tabpfn_full | -6.94083 | 16.22% |
| ff5_mom__paper__debt_maturity | -6.93853 | 16.23% |
| ff5_mom__paper__dividend_yield | -6.95884 | 16.26% |
| ff5_mom__paper__joint_rms | -6.94789 | 16.24% |
| ff5_mom__paper__market_cap_assets | -6.95057 | 16.23% |
| ff5_mom__paper__market_to_book | -6.94832 | 16.25% |
| ff5_mom__same_four_histories__autoencoder | -6.94166 | 16.27% |
| ff5_mom__same_four_histories__direct | -6.94300 | 16.25% |
| ff5_mom__same_four_histories__exaone | -6.94013 | 16.22% |
| ff5_mom__same_four_histories__pca16 | -6.94276 | 16.25% |
| ff5_mom__same_four_histories__random_autoencoder | -6.94025 | 16.25% |
| ff5_mom__same_four_histories__tabfm | -6.94007 | 16.24% |
| ff5_mom__same_four_histories__tabpfn_fast | -6.94085 | 16.23% |
| ff5_mom__same_four_histories__tabpfn_full | -6.94234 | 16.23% |
| ff5_mom__spherical | -6.93282 | 16.25% |
| ledoit_wolf_reference | -7.08137 | 16.39% |
| sample_covariance | -7.07862 | 16.47% |

## Paper-style cross-sectional exercise

Robust MM betas use 40 quarterly observations. Both spatial IV and spatial-error
ML are estimated on median excess returns. These are descriptive in-sample fits.

| Characteristic | Firms |
| --- | ---: |
| market_cap_assets | 79 |
| market_to_book | 57 |
| dividend_yield | 75 |
| debt_maturity | 13 |

Full coefficients and stability flags are in `cross-section.csv`.
Conditional parameter significance and generated-beta uncertainty are not estimated.

## Interpretation limits

The all-four sample is small and selected for disclosure completeness and nonconstant
histories. The ten test years have already been examined; these are development
comparisons, not confirmatory evidence. Do not select a winning characteristic
or model using these test losses. The richer-input rung includes the same four
histories, so its incremental information is the added SEC concepts.

The paired-comparisons table reports each learned model against raw covariance,
factor-only covariance and every individual Fernández network, plus the joint
classical control. Ledoit-Wolf is only a reference, not a success requirement.
