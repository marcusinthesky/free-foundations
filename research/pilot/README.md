# Financial-topology pilot

The completed run is summarized in [Pilot results](RESULTS.md).

A small extension of Fernández's financial-contiguity idea: construct a network
from previously filed accounting states, then test whether it organizes future
FF5+momentum residual dependence. This is an exploratory research experiment,
not a replication of Fernández's cross-sectional spatial CAPM.

## Run

From the repository root, provide the SEC request identity through the environment:

```sh
export EDGAR_IDENTITY="Your Name your.email@example.com"
just python-pilot
```

The identity is used only in SEC requests; it is not written into the artifacts.
The command installs the locked CPU TabPFN runtime, caches the data, and runs the
full comparison. The first run downloads a roughly 334 MB Fast checkpoint.
Subsequent runs reuse cached inputs and embeddings. To run individual stages:

```sh
uv run --project src/python --frozen python -m free_foundations.pilot markets
uv run --project src/python --frozen python -m free_foundations.pilot data
uv run --project src/python --frozen --extra tabpfn python -m free_foundations.pilot run --pretrained
```

Omit `--pretrained` for the accounting/PCA baselines alone. The CLI can be called
with `--output PATH` to keep a separate input vintage and its results. Existing
cache files are never silently refreshed; use a new output directory to refresh.

## Sample and timing

- Yahoo's current market-cap ranking on NYSE, Nasdaq, and NYSE American; screen
  150 candidates and retain the first 100 distinct SEC CIKs with USD US-GAAP assets reported in annual 10-Ks.
  Duplicate share classes and issuers without this annual coverage are listed in
  the exclusion file. This also excludes some newly reorganized issuers whose
  current CIK has no annual history; predecessor CIKs are not linked in this pilot.
- Evaluate calendar years **2016–2025**. Download daily prices and factors from
  2012 for estimation and accounting-history warm-up. Ignore survivorship bias as
  requested; the sample is a current ranking, not historical top-100 membership.
- For each year, estimate intercept plus FF5+momentum loadings from the preceding
  three years of daily excess returns. Freeze the coefficients for the test year.
  Subtract realized test-year factors only to measure residual dependence; these
  are not ex ante predictions of total returns.
- At the preceding December 31, select the latest annual facts that were actually
  filed by that date, retaining accession, period end, and filing date. Future
  restatements are excluded. Use USD US-GAAP companyfacts from 10-K/10-K amendments,
  annual flow periods of 300–380 days, and a maximum period-end age of 550 days.
- Use the same eligible cohort for every network within a year: complete daily
  prices across estimation/evaluation and four annual asset snapshots. Thus the
  selected universe has 100 firms, but annual estimation cohorts can be smaller.
  The complete-test-year requirement adds an acknowledged availability selection.

The 19 features are log assets plus 18 asset-scaled balance-sheet/annual-flow
variables (liabilities, equity, cash, receivables, inventory, current assets and
liabilities, PPE, goodwill, intangibles, retained earnings, revenue, net income,
operating income/cash, capex, R&D, interest). This deliberately small pilot does
not yet test the proposed hundreds/thousands-variable XBRL representation.
Facts are selected independently; annual periods may differ across tags. Banks,
missing tags, taxonomy choices, and accounting comparability require later review.
Missing features are mean-imputed, never silently interpreted as zero; entirely
missing columns become zero after imputation and standardization.

## Networks and pretrained readout

1. Fernández-inspired asset-history weights: four annual log-asset snapshots,
   Spearman correlation distance `sqrt(2(1-rho))`, then `exp(-distance)`.
   This is an adaptation: assets replace market capitalization, with much shorter
   characteristic histories than Fernández's original application.
2. Single-date size and liabilities/assets distance.
3. Standardized accounting ratios, five-component PCA, and an eight-dimensional
   Gaussian random projection. The projection is a simple control, not a randomly
   initialized transformer with an identical architecture.
4. TabPFN **3.5 Fast**, one ensemble member, seed 42, CPU. Its `get_embeddings`
   query states pass through the shared `from_fitted` adapter, yielding 1,024
   dimensions. The checkpoint revision and context digests are recorded.
5. The same TabPFN network with firm labels randomly permuted (seed 42).

TabPFN's support examples use accounting states from years t-3 and t-2 to predict
next-year snapshot annual net income/assets. Both labels are available by the end
of t-1. Query rows are t-1 accounting states. Imputation, missingness indicators,
and scaling are fitted only on support examples. This tests one explicitly
profitability-conditioned geometry, not a unique context-free firm embedding.

Other than the historical-correlation benchmark, all networks use
`exp(-squared_distance / median_positive_squared_distance)`, zero diagonal, and
row normalization. The bandwidth is fixed by the available feature geometry;
there is no search using evaluation returns. There is no claim that raw embedding
geometry is identified or economically valid merely because pretraining worked.

## Estimation and outputs

Fit a Gaussian spatial-error model to standardized training residuals, with
lambda constrained to [-0.8, 0.8] and diagonal innovation variance profiled out.
Freeze the resulting covariance for the following year. Compare against diagonal
and Ledoit–Wolf residual covariance forecasts. This small estimator handles the
actual row-normalized network directly; it does not yet estimate dynamic lambda.

- `universe.csv`, `universe-exclusions.json`, `cohorts.json`: sample audit.
- `annual.csv`, `summary.csv`: held-out Gaussian covariance loss, residual GMV
  RMS risk (the `gmv_volatility` column), mean daily Moran I, and fitted lambda. Lower Gaussian loss is better;
  its irrelevant Gaussian constant is omitted. Risk is an average of annualized yearly root-mean-square residual returns,
  including nonzero residual means, not demeaned total-return volatility.
- `paired-comparisons.csv`: paired annual loss differences against TabPFN.
- `comparison.svg`, `comparison.png`: exportable comparison figures.
- `run-summary.json`: sample range and experiment settings.
- `manifest.json`: input hashes and runtime versions.
- Ignored `cache/`: downloaded facts/prices/factors, point-in-time accounting panel,
  selected-fact audit trail, embeddings, checkpoint metadata, and daily scores.

The reported 95% intervals resample the ten annual paired loss differences versus
the diagonal forecast. They are exploratory: ten years are few, training windows
overlap, annual observations need not be independent, and several specifications
are compared. Daily firm pairs are not treated as independent observations.
Moran I is descriptive here, not a reported significance test or causal spillover
estimate. The GMV calculation is unconstrained and measures residual risk without
transaction costs, exposure controls, or a tradable strategy construction.

## Sources and limits

- [Fernández (2011)](https://doi.org/10.1080/14697680903127403): the conceptual
  financial-contiguity benchmark, read from the supplied local PDF.
- [Yahoo screener API](https://ranaroussi.github.io/yfinance/reference/api/yfinance.screen.html)
  and adjusted daily closes through yfinance.
- [French data library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html):
  daily five factors, momentum, and risk-free return via pandas-datareader over
  HTTPS. The current revised data vintage is used, not archived real-time factors.
- [EdgarTools](https://edgartools.readthedocs.io/en/latest/): SEC companyfacts and
  ticker mapping, with a required name/email request identity.
- [TabPFN 3.5](https://huggingface.co/Prior-Labs/tabpfn_3_5): frozen externally
  pretrained checkpoint. Its 2026 release makes this a retrospective historical
  experiment, not a simulation of a model available to investors in 2016.

Industry controls, full characteristic-history benchmarks, industry-matched
permutations, identical random transformer/autoencoder controls, dense XBRL
coverage, multiple context/pooling choices, and formal inference remain follow-up
work. Findings from this pilot cannot establish the proposed pretraining advantage.
