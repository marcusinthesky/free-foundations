# Combined-network spatial-error ML comparison

> Superseded by the matched cross-sectional ladder in [`research/ladder`](../../ladder/README.md),
> which uses 33 (four-characteristic) and 395 (three-characteristic) firms.

All rows use the same 6 firms: CVX, MDT, MPC, MU, VLO, WMT.

The likelihood has one observation per firm: median quarterly excess return over
2016-2025, regressed on the saved 40-quarter robust MM beta without an intercept.
Each spatial row estimates one lambda, one premium, and one innovation variance.
The no-spatial row fixes lambda at zero. All Gaussian constants are included.

Fernández benchmarks use individual 2015-2024 characteristic histories.
Joint RMS combines their four distances; it is our extension of the paper.
Every learned representation combines all four histories in one vector per firm;
the broader input additionally contains up to 200 SEC concepts from the 2024 snapshot.
Support context and preprocessing follow the existing annual ladder and are saved.
All networks use exp(-distance), zero diagonal, and row normalization.

This is an in-sample, six-firm demonstration, not a forecast or a significance test.
A boundary flag means the estimate reaches the (-0.99, 0.99) search limit.

| Model / input | Lambda | Log-likelihood | Gain over nonspatial | Boundary |
| --- | ---: | ---: | ---: | --- |
| nonspatial_capm | 0.0000 | 15.356793 | 0.000000 | False |
| fernandez__market_cap_assets | -0.5894 | 15.521932 | 0.165139 | False |
| fernandez__market_to_book | -0.9891 | 15.715713 | 0.358920 | True |
| fernandez__dividend_yield | -0.4837 | 15.516434 | 0.159641 | False |
| fernandez__debt_maturity | -0.9900 | 16.294774 | 0.937981 | True |
| joint_four__rms | -0.9900 | 15.933176 | 0.576383 | True |
| four_histories__direct | -0.9900 | 16.167046 | 0.810253 | True |
| four_histories__pca16 | -0.9900 | 16.103046 | 0.746253 | True |
| four_histories__autoencoder | -0.9900 | 16.237048 | 0.880255 | True |
| four_histories__random_autoencoder | -0.9900 | 16.024769 | 0.667976 | True |
| four_histories__tabpfn_fast | -0.9900 | 15.907318 | 0.550525 | True |
| four_histories__tabpfn_full | -0.9900 | 15.840566 | 0.483773 | True |
| four_histories__tabfm | -0.9900 | 16.116700 | 0.759907 | True |
| four_histories__exaone | -0.9900 | 15.968379 | 0.611586 | True |
| four_plus_broad__direct | -0.9900 | 16.433942 | 1.077149 | True |
| four_plus_broad__pca16 | -0.9900 | 16.598035 | 1.241242 | True |
| four_plus_broad__autoencoder | -0.9900 | 16.664786 | 1.307993 | True |
| four_plus_broad__random_autoencoder | -0.9900 | 15.932336 | 0.575543 | True |
| four_plus_broad__tabpfn_fast | -0.9900 | 15.835739 | 0.478946 | True |
| four_plus_broad__tabpfn_full | -0.9900 | 15.757814 | 0.401021 | True |
| four_plus_broad__tabfm | -0.9900 | 16.101360 | 0.744567 | True |
| four_plus_broad__exaone | -0.9900 | 15.912741 | 0.555948 | True |
