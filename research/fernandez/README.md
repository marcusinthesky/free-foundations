# Fernández comparison and replication ladder

The reference is Viviana Fernández, *Spatial linkages in international financial
markets*, Quantitative Finance 11(2), 237–245 (2011),
[DOI](https://doi.org/10.1080/14697680903127403).
Completed forecasting results are in [the comparison report](RESULTS.md).

> **Superseded cross-section.** The paper-style two-stage exercise below used the
> 100-issuer pilot universe (79/57/75/13 firms on unequal cohorts). It is rebuilt on the
> 1,000-issuer universe, with one common cohort per characteristic arm, standard errors,
> exact residual Moran moments and a generated-beta bootstrap, in
> [`research/ladder`](../ladder/README.md). The files here are retained as history.
> The residual Moran statistic in `cross-section.csv` re-centred residuals; the code
> now uses uncentred least-squares residuals, so a rerun changes that column.
The [combined-network likelihood table](combined/RESULTS.md) uses one scalar
spatial parameter per model and input set, fitted on exactly the same firms.
Reproduce it with `devenv shell just python-fernandez-combined`.
Each learned vector combines all four histories, optionally adding broader SEC
concepts; the joint RMS benchmark is an extension of the original method.
The strict ten-year common cohort contains only six firms, so this is a
descriptive demonstration rather than evidence of model superiority.

The supplied PDF was reread from `~/Downloads/Spatial linkages in international financial markets.pdf`.
Its SHA-256 is `7391cb6ed0b986ff3dffd3f0870b7a3a5f94a2291f773d0ebed0a91149bfbabe`.

This is a **methodological replication on a different US sample**, followed by a
forecasting extension. It is not a reproduction of the original Economatica data
or of the numerical results in the paper. The earlier `fernandez_assets_history`
benchmark remains an exploratory proxy and is not the replication benchmark.

## What the paper actually establishes

- Section 2.2, equations (6)–(7), introduces a **spatial CAPM**, with spatial-lag
  and spatial-error alternatives. It does not derive a general spatial APT or
  establish that arbitrary learned distances measure economic fundamentals.
  FF5+momentum is our multifactor extension, not Fernández's original theory.
- Section 2.4, equations (9)–(10), uses histories of one characteristic at a time:
  Spearman correlation, `sqrt(2 * (1 - correlation))`, `exp(-distance)`, and row
  normalization. This is not Euclidean distance between current financial ratios.
- Section 3.2 uses four networks: market capitalization relative to firm size,
  market-to-book, dividend yield, and debt maturity. Debt/assets also appears in
  Table 1 and country-specific discussion, but is not one of Table 2's four
  pooled-sample networks.
- The original sample has 126 firms in Brazil, Chile and Mexico, 1997–2006.
  Annual characteristics construct the networks; quarterly returns estimate
  firm betas using a robust MM estimator. Median returns are then regressed
  cross-sectionally on those betas. Spatial lag uses two-stage least squares
  with `[WX, X]` instruments (equation 2); spatial error uses Gaussian ML
  (equation 4). This is an in-sample cross-sectional exercise, not an annual
  out-of-sample covariance forecast competition.
- Section 2.3 gives different covariance/VaR formulas: spatial lag transforms
  both systematic and innovation risk; spatial error transforms only innovation
  risk. Section 4 explores these through simulations, not realized portfolio
  backtests. Our forecasting ladder uses the spatial-error alternative.

The paper motivates characteristics as determinants of financial proximity.
Market capitalization, market-to-book and dividend yield also contain market
prices: calling that whole input set purely accounting fundamentals would be
inaccurate. Rich SEC disclosures add an accounting measurement layer; the
validity of its learned geometry remains the hypothesis to test.

## Theory boundary

Fernández supplies the spatial CAPM mechanism and its covariance implications.
Our multifactor spatial-error extension is `r = B f + u`,
`u = lambda W u + epsilon`; the spatial-lag alternative is
`r = rho W r + B f + epsilon`. Replacing the market factor by FF5+momentum
changes the factor specification. It does not by itself establish an APT
no-arbitrage theorem. Treating SEC features as measurements of fundamentals is
an economic interpretation to validate, not a theorem supplied by pretraining.
The controlled ladder asks whether learned distances improve that measurement,
conditional on a fixed spatial model and information cutoff.

## Comparison ladder

| Rung | Input | Geometry | Purpose |
| --- | --- | --- | --- |
| Original method | Each original characteristic's history | Spearman distance | Replicate the published construction |
| Joint classical control | All four histories | RMS of the four Spearman distances | Separate combining characteristics from pretraining |
| Matched learned inputs | The same four histories | Foundation-model chord distance | Test a learned representation without adding characteristic families |
| Rich classical control | Four histories plus up to 200 reported SEC concepts | Standardized input chord distance | Measure what adding disclosures alone buys |
| Rich learned inputs | Identical richer table | Foundation-model chord distance | Test pretraining conditional on the larger input set |

The individual-characteristic cross-sectional comparison also feeds each
characteristic's ten-year history to each foundation model on exactly that
characteristic's available cohort. It preserves larger samples than requiring
complete histories for all four characteristics simultaneously.

Models are TabPFN 3.5 Fast, TabPFN 3.5 full, Google TabFM 1.1 and EXAONE-Tabular,
using the already pinned checkpoints and audited late-state adapters. Chord
distance is Euclidean distance between unit-normalized vectors, in `[0, 2]`.
It is a metric on normalized vectors, a pseudometric on unnormalized states;
identical rank histories also have zero Spearman distance for distinct firms.
Every rung uses **the same `exp(-distance)` kernel**, row normalization and zero
self-links. No bandwidth or model is selected on test outcomes.

Foundation-model support uses two previous snapshot years, with the following
snapshot's characteristic as its regression label. The joint ladder uses
market-cap/assets; individual-characteristic readouts use that characteristic.
Labels are already available at the query cutoff. There are no return targets.
These are matched characteristic families and query histories, **not identical
information-processing procedures**: support examples and conditioning labels
are additional historical context used by the pretrained models. Context IDs,
features and checkpoint metadata are saved. Support-fitted median imputation,
missingness indicators, scaling and clipping are identical across learned rungs.
Matched PCA, trained denoising autoencoder and random-autoencoder controls use
the same support rows; these reuse the existing expanded-study implementations.
Direct controls receive the same prepared query table, with a constant coordinate
before normalization so a zero standardized row has defined geometry.

## Data construction and honest replication differences

- Use the original current-US-universe price and French-factor caches, plus
  cached SEC filings. Downloads of Yahoo closes, dividends and splits are frozen
  separately. Original returns remain dividend-adjusted; valuation inputs use
  split-adjusted Close with subsequent splits reversed for historical share units.
- Interpret the paper's otherwise unspecified denominator "firm size" as assets.
  Market capitalization uses the latest disclosed common share count and the
  historical close at its observation date. Cover-page DEI shares are preferred;
  US-GAAP common shares are the fallback. Market-cap/assets and market-to-book
  therefore combine a share-date market value with the latest annual balance
  sheet available at the year-end cutoff. Both dates are recorded. This is an
  explicitly documented US construction, not a verified Economatica field match.
- Book equity must be positive. Debt maturity uses a consistent **lease-inclusive**
  basis: noncurrent debt and finance/capital leases divided by total debt and
  finance/capital leases. Direct aggregate tags are preferred. When aggregating
  components, both debt and lease amounts must be explicitly disclosed at the
  annual asset period; missing leases and missing borrowings are never zero.
  `DebtCurrent` includes capital leases, whereas `LongTermDebtNoncurrent` excludes
  them: those two tags are not combined without the noncurrent lease component.
  Direct total debt minus current debt can recover the noncurrent component.
  Liabilities are never substituted for debt. This definition is explicit;
  the precise lease treatment in Economatica remains unverified.
- Dividend yield is trailing 365-day Yahoo cash dividends divided by Close at
  the share observation date. Their common split basis cancels. Explicit
  non-payment is zero; constant dividend histories cannot define a Spearman
  correlation and are excluded from a strict original-method comparison.
- All SEC facts must have been filed by the snapshot cutoff, with observation
  dates no more than 550 days old. A share disclosure filed across a split is
  rejected rather than guessing whether the count was restated. Known
  incompatible multiple share classes are excluded; this does not certify a
  comprehensive share-class reconciliation for every remaining issuer.
- The US sample, market factor, risk-free proxy and currency differ from the
  original Latin American sample. The original uses the MSCI EM Latin America
  index and a Treasury yield proxy; this run uses French market excess returns
  and RF. Inflation adjustment is not separately applied to these US ratios.
- Robust MM betas use [`robustbase::lmrob`](https://search.r-project.org/CRAN/refmans/robustbase/html/lmrob.html)
  with `method="MM"` and seed 42. This is an
  established MM implementation, not a claim to reproduce the author's
  unspecified S-Plus tuning. The first stage includes an intercept; the second
  stage follows the no-intercept equation with beta as its sole regressor.
  Generated-beta uncertainty is not included in this descriptive comparison.
- Equation (10) does not explicitly describe removing self-links. The primary
  convention is zero diagonal; cross-sectional tables also report the literal
  positive-diagonal construction. Constant histories are rejected, not assigned
  an invented correlation. The paper's printed mean of Moran's statistic has a
  positive sign; the standard zero-diagonal null mean is `-1/(N-1)`. We report
  descriptive Moran values, not significance from that printed formula.

Strict all-four coverage is **6–11 firms per annual cohort**, reported in
`cohorts.json` and the results table. Debt disclosures are the bottleneck. This small common
sample makes the comparison transparent, but is insufficient for a persuasive
100-firm empirical claim. Expanding audited debt mappings or obtaining verified
historical characteristics is necessary before treating this as the main paper
result. The original study's precise data/code are not supplied here.

## Two distinct evaluation tracks

**Paper-style cross-section:** use ten characteristic snapshots (2015–2024) and
forty quarterly excess returns (2016–2025). Compound total returns and RF
separately before subtraction. Estimate MM betas, then spatial IV/ML on median
excess returns. Save premiums, spatial coefficients, structural fitted-value
squared correlations, residual normality diagnostics and OLS-residual Moran I.
These are descriptive in-sample results; a larger fitted R-squared is not proof
of better forecasting. The IV estimate is not clipped into a stable interval;
stability is explicitly reported. ML estimates near the search boundary are
also flagged rather than interpreted as well-determined interior optima. ML searches `(-0.99, 0.99)`, rather than the
old pilot's overly restrictive `(-0.8, 0.8)`.

**Forecasting extension:** each evaluation year 2016–2025 uses four characteristic
snapshots available by the previous December 31, a common complete cohort, and
three preceding years of daily returns. Four years is a data-availability
extension; it is not the paper's ten-year network window. Fit CAPM and FF5+momentum
loadings on training data only. Construct

`Sigma = B Cov(f) B' + sigma² (I - lambda W)^(-1) (I - lambda W)^(-T)`.

The spherical innovation variance follows the paper, in original return units;
all networks use the same estimator. Include factor-only spherical and diagonal
residual covariances, unregularized sample covariance, and Ledoit–Wolf as a
reference. Forecast full excess-return covariance, with a common training-sample
mean for every method. No realized test factors enter a forecast. Report Gaussian
loss and realized demeaned volatility of frozen unconstrained GMV portfolios.
Portfolio results exclude costs and constraints. This differs from the earlier
pilot's residual-only RMS risk and should not be compared numerically to it.

Do not pick the best of four Fernández networks using test returns and label that
an implementable forecast. Report each separately and the predetermined joint
control. Likewise, all pretrained configurations are development comparisons,
not a selected winner on an untouched holdout. Beating Ledoit–Wolf is not a
success requirement; a later shrinkage combination is a separate experiment.

## Running and artifacts

Run `devenv shell just python-fernandez` from the repository root. The locked
Nix environment includes R and robustbase for the MM first stage. Python uses
existing locked model extras; successful downloads and readouts are cached.

- `characteristic-audit.csv`, `coverage.csv`, `excluded-issuers.csv`: inputs and gaps.
- `mm-betas.csv`, `quarterly-returns.csv`, `cross-section.csv`: two-stage replication.
- `cohorts.json`, `context-*.json`: common annual firms and model conditioning.
- `distances/`, `distance-inventory.csv`: labeled yearly distance matrices.
- `annual.csv`, `summary.csv`: matched full-return forecasting comparisons.
- `execution-status.json`, `manifest.json`: completion and input/source hashes.

The original expanded experiment remains intact in `research/expanded`.

## Section 4 simulation audit

`simulation.csv` evaluates equations (8a)–(8b) for both beta distributions,
portfolio sizes 20/40/80/150/300, spatial coefficients 0/0.1/0.5/0.8, and 200 draws
(seed 42). It uses the printed initial value of $1,000, one-day horizon, 95%
confidence, and standard deviations of 0.01. Random symmetric pairwise draws
follow the stated uniform-correlation recipe. Those draws need not form a valid
positive-semidefinite correlation matrix; they are used only to build weights,
not substituted as a return covariance. Standard deviations across draws and
Monte Carlo standard errors of the mean are both reported and distinguished.

**The printed Table 6 values do not follow from its stated calibration.**
At zero spatial dependence and N=20, equation (8) gives
`VaR = 1000 * 1.64485 * 0.01 * sqrt(mean(beta)^2 + 1/20)`.
For every beta in [0.5, 1], this is at most approximately **$16.85**, whereas
Table 6 reports **$36.27** for that cell. At beta=0.75 it is about **$12.87**.
The calibration on page 243 and Table 6 on page 244 were checked visually in
the supplied PDF. This discrepancy cannot be explained by random seeds or
self-link conventions, since W disappears when the spatial coefficient is zero.
An undocumented calibration or scaling difference would need the author's code
to resolve. The simulation tests the published equations; it does not claim to
numerically reproduce Table 6 by changing its inputs.
