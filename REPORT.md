# Research report: financial proximity from tabular representations

**Status: 17 October 2026. Author: Marcus Gawronsky.**

This report consolidates the completed experiments in `free-foundations`. It
separates exploratory development results from the latest chronological panel,
records the actual estimation sample and information set, and identifies the
claims that the evidence supports. Figures below are taken from saved experiment
artifacts; no new model fitting was performed to prepare this report.

## 1. Main findings

The project now has an operational pipeline from dated SEC disclosures through
accounting characteristics, tabular representations, annual pairwise distance
matrices, spatial networks, and return-covariance evaluation.

The latest experiment compares **34 approaches on exactly the same 87,351
held-out firm-days over 2020–2025**. Every spatial approach has one scalar
coefficient, estimated on 2016–2019 and frozen thereafter. Each approach combines
its selected fundamentals into one annual network; foundation models do not
receive a separate spatial coefficient for each accounting feature.

The findings are:

- **No pretrained configuration exceeds the joint Fernández-style four-characteristic
  benchmark.** The closest is full TabPFN with broad disclosures: 219,990.10 versus
  219,993.24 held-out log-likelihood, a difference of only −3.13.
- **Richer accounting inputs help simple compression.** PCA with normalized metrics
  scores 220,054.56, a gain of 61.32 over the joint benchmark. The corresponding
  autoencoder scores 220,045.25, a gain of 52.01.
- **Raw covariance and FF5+momentum remain substantially ahead.** Raw sample
  covariance scores 224,819.87; FF5+momentum with diagonal residual covariance
  scores 224,657.11. These gains also reflect differences in covariance
  flexibility, not exclusively differences in financial geometry.
- **The acquired universe is much larger than the matched estimation sample.**
  We acquired 1,000 current issuers, with prices for 997, but strict complete
  histories of all four Fernández characteristics leave 47–70 firms per
  evaluation year.
- **The chronological experiment resolves the earlier boundary-fit problem.**
  No latest spatial estimate reaches the imposed coefficient boundary. The
  earlier six-firm in-sample fits frequently did.

These are development findings, not confirmatory significance statements.
“Held out” describes the chronological estimation procedure; these calendar
periods have already been examined during the research process.

## 2. Research question and relationship to Fernández

The substantive question is whether pretrained tabular models measure a useful
notion of economic proximity between firms from their financial disclosures.
The proposed role for AI is measurement of the spatial weights matrix, rather
than creation of an additional asset-pricing factor.

The local reading of Fernández (2011), *Spatial linkages in international
financial markets*, motivates the benchmark. The paper constructs financial
contiguity from histories of individual characteristics, using a
Spearman-correlation distance followed by an exponential kernel and row
normalization. This is materially different from simply taking Euclidean
distances between single-date accounting ratios. The repository's
[paper comparison methods](research/fernandez/README.md) and
[Python research notes](src/python/README.md) document the reading of the supplied
PDF and the distinction between its original exercise and our extensions.

We retain four individual reference networks: capitalization/assets,
market-to-book, dividend yield, and debt maturity. Combining their distances by
root mean square produces a joint-four control. **That joint control is our
extension**, not a claim that Fernández estimated this exact combined model.

Our chronological main comparison differs from the original application in
country, sample, available disclosure histories, return frequency, factor model,
and estimation design. It evaluates future daily excess-return densities after
estimating FF5+momentum loadings from prior data. It does not reproduce the
original Economatica sample or its robust cross-sectional spatial asset-pricing
exercise. The separate paper-style exercise remains useful for methodological
alignment, but should not be conflated with the forecasting panel.

The motivating economic hypothesis is that similar operating and financing
states imply similar exposure to omitted shocks. This is a hypothesis to test:
nearby accounting states do not automatically imply higher residual covariance,
and a spatial-error association does not identify causal shock transmission.

## 3. Experiment history and what changed

### 3.1 Initial 100-issuer pilot

The [original pilot](research/pilot/RESULTS.md) used Yahoo prices, dated SEC
facts, daily French factors, and actual TabPFN 3.5 Fast embeddings over
2016–2025. The screen reached rank 144 to obtain 100 eligible distinct issuers;
annual cohorts contained 80–95 firms. Inputs comprised 19 accounting features,
1,173 accounting states, and 18,517 selected facts. The date audit found no
future filing dates or future accounting-period ends.

The score was an average covariance-loss improvement over a diagonal residual
model, normalized per firm and omitting a common Gaussian constant. The portfolio
statistic was annualized **factor-residual GMV RMS**, not full-return volatility.

| Pilot approach | Loss improvement over diagonal | Residual GMV RMS |
| --- | ---: | ---: |
| Ledoit–Wolf | 0.13860 | 2.62% |
| Size | 0.02662 | 4.38% |
| PCA, five components | 0.01685 | 4.25% |
| Accounting ratios | 0.01500 | 4.21% |
| TabPFN 3.5 Fast | 0.01362 | 4.21% |
| Shuffled TabPFN links | 0.00125 | 3.76% |
| Diagonal | 0.00000 | 3.60% |

TabPFN improved on shuffled links in every year, but beat accounting ratios in
only three years and PCA in two. The exploratory annual bootstrap gave a mean
gain of 0.01237 over shuffled links, with interval [0.00482, 0.02478], and a
mean difference of −0.00138 against accounting ratios, with interval
[−0.00380, 0.00052]. There were only ten annual observations, overlapping
estimation windows, and multiple comparisons. These intervals are not evidence
of a robust pretraining advantage. The improved covariance loss relative to the
diagonal model also failed to improve residual portfolio risk.

The pilot established feasibility. Its asset-history proxy was subsequently
replaced by a closer Fernández comparison. Ledoit–Wolf was retained as a
reference, not a necessary hurdle for the research question.

### 3.2 Expanded inputs, encoders, and geometry checks

The [expanded experiment](research/expanded/RESULTS.md) retained the original
annual cohorts and compared core accounting features, broad reported SEC
concepts, and normalized metrics. It added full TabPFN, Google TabFM, EXAONE,
PCA, trained and random autoencoders, alternative readouts, support contexts,
and distance choices.

The historical broad table had 5,010 candidate columns. The full development
grid contained 72 foundation-model configurations; none beat Ledoit–Wolf on
mean covariance loss. This was a descriptive result across a searched grid,
not an independent hypothesis test. For the displayed income-context,
late-readout, chord-distance variants, broad-input TabPFN Fast achieved
0.01506 loss improvement, compared with 0.01575 for broad PCA and 0.01604 for
the broad autoencoder.

Changing support context changed pairwise-distance rankings materially:
upper-triangle Spearman correlations ranged from 0.396 to 0.968, with median
0.734. Changing the metric produced correlations from 0.346 to 1.000, with
median 0.999. Firm pairs are dependent observations; these correlations are
geometry diagnostics, not independent-sample significance tests. They show
that checkpoint identity alone does not fully specify the measurement system.

### 3.3 Paper-aligned Fernández comparison

The [Fernández comparison](research/fernandez/RESULTS.md) introduced the four
characteristic histories and explicitly matched factors, firms, and return
dates. Requiring long complete histories reduced the annual forecasting cohort
to just 6–11 firms. All 210 saved labeled distance matrices passed the artifact
audit.

Among 16 learned configurations under the same FF5+momentum specification:

| Reference | Learned configurations with lower mean held-out loss |
| --- | ---: |
| Raw sample covariance | 0/16 |
| FF5+momentum with diagonal residual covariance | 0/16 |
| Fernández capitalization/assets | 0/16 |
| Fernández market-to-book | 0/16 |
| Fernández dividend yield | 0/16 |
| Fernández debt maturity | 16/16 |
| Joint-four RMS control | 0/16 |

This result demonstrated why comparing only against the weak asset-history
proxy was insufficient. It did not establish an advantage for learned geometry.
The portfolio statistic here changed to full excess-return GMV volatility;
it is not the pilot's residual RMS statistic.

A separate paper-style cross-sectional exercise estimated robust MM betas from
40 quarterly observations and fitted spatial IV and spatial-error ML to median
excess returns. Characteristic-specific samples contained 79, 57, 75, and
13 firms respectively. These unequal samples cannot be ranked by raw likelihood
as though they were a common comparison. Conditional significance and uncertainty
from generated betas were not estimated.

### 3.4 Six-firm combined-network ML demonstration

The [combined-network exercise](research/fernandez/combined/RESULTS.md) answered
the request for one coefficient and one likelihood per combined representation.
All rows used CVX, MDT, MPC, MU, VLO, and WMT. Each observation was a firm's
median quarterly excess return over 2016–2025, regressed without an intercept
on its saved robust beta. Each spatial model estimated one coefficient, one
premium, and one innovation variance.

The no-spatial likelihood was 15.356793. The joint-four likelihood was 15.933176;
the broader autoencoder reached 16.664786. However, those two spatial fits and
many others reached approximately −0.99, the imposed search boundary. These
six-observation in-sample gains were diagnostic, not evidence of useful
forecasting or positive shock propagation. Their likelihood scale is unrelated
to the current daily panel score.

### 3.5 Universe expansion and chronological panel

The next step acquired 1,000 issuers and return/factor histories from 2008 through
2025, then rebuilt the characteristics and ran the latest matched panel.
Shortening the required characteristic history to three annual observations
increased usable cohorts substantially. This is an explicit design compromise,
not an unchanged replication on a larger sample.

The remainder of this report treats that chronological panel as the principal
current comparison. Earlier files are retained as research history rather than
overwritten or pooled with the new results.

## 4. Current data, characteristics, and sample selection

### 4.1 Acquired universe versus usable observations

The [universe acquisition record](research/universe/README.md) documents
1,000 distinct SEC issuers, prices for 997, and observed prices and French factors
from 2 January 2008 to 31 December 2025. Candidates are current US exchange
listings ranked by current capitalization. One share class is selected per CIK.
This intentionally retains current-listing and survivorship bias; it is not a
historically reconstructed investable universe.

The original acquisition audit counted 11,483 annual filing-availability
snapshots. The later full characteristic build has a different scope and records
11,526 populated snapshots on a 16,000 issuer-year grid. These counts describe
different artifacts, not two conflicting estimates of the final return sample.

| Full disclosure audit | Count |
| --- | ---: |
| Issuers | 1,000 |
| Annual grid states | 16,000 |
| Populated snapshots | 11,526 |
| Candidate US-GAAP concepts | 9,014 |
| Selected facts | 2,685,172 |
| Facts with future filing dates | 0 |
| Facts with future period ends | 0 |
| Duplicate concepts within a snapshot | 0 |

Source: [disclosure audit](research/panel/disclosure-audit.json).

### 4.2 Filing and accounting rules

Snapshots use annual 10-K and 10-K/A disclosures available by the preceding
31 December. Accounting-period ends must also precede that cutoff and be no
more than 550 days old. Annual flows span 300–380 days; instantaneous balances
are separate features. Original filing dates, period ends, units, and accessions
are retained for audit.

The broad concept universe comprises standard entity-wide US-GAAP data in USD,
shares, USD/share, or dimensionless units. Concept identity includes namespace,
unit, and instant/annual status. This is broad structured disclosure coverage,
**not complete raw XBRL** and not a fully harmonized universe of economic ratios.
Company-specific extension tags, segment facts, IFRS reporters, and other
currencies are not included in this specification.

The four reference characteristics are:

1. Capitalization divided by assets.
2. Market value divided by positive book equity.
3. Trailing dividend yield.
4. Strict lease-inclusive noncurrent debt divided by total debt.

Missing debt components are never interpreted as zero. Debt components and
associated balances require period alignment. Capitalization uses shares and
prices at the share observation date; assets and equity use an aligned
balance-sheet date, which can differ from the share date. Those differences
are audited rather than assumed away.

Yahoo split-adjusted prices are reversed to the relevant share basis using the
available split history, including later splits beyond the return horizon.
Dividends and prices use the same split basis. Known unresolved multiple-share-class
cases are excluded; this is not a claim of exhaustive share-class reconciliation.

### 4.3 Strict matched panel

Eligibility requires three complete, nonconstant annual histories for all four
reference characteristics and at least 500 preceding daily returns within a
three-calendar-year window. Selection takes place before the evaluation year.
Strict debt coverage is particularly restrictive; non-dividend payers can also
be excluded because their dividend histories are constant and correlation
distance is undefined.

| Return year | Firms | Prior complete days | Scored days |
| --- | ---: | ---: | ---: |
| 2016 | 58 | 756 | 251 |
| 2017 | 63 | 756 | 250 |
| 2018 | 64 | 554 | 250 |
| 2019 | 64 | 754 | 251 |
| 2020 | 60 | 754 | 252 |
| 2021 | 47 | 756 | 251 |
| 2022 | 48 | 757 | 250 |
| 2023 | 60 | 756 | 249 |
| 2024 | 64 | 753 | 251 |
| 2025 | 70 | 753 | 249 |

The 2020–2025 sample contains 87,351 scored firm-days, not 1,000 firms observed
for six complete years. Missing future observations remove common dates for
all approaches; they do not cause the network to be rebuilt with a different
set of firms after outcomes arrive. Removed dates are recorded in the annual
sample files. Scores therefore condition on common observed dates.

The first return in each year is excluded. Its close-to-close interval can start
before a 31 December filing released after market close, while SEC filing dates
in this pipeline do not resolve intraday availability. This exclusion is applied
to every approach.

## 5. The matched input and representation ladder

### 5.1 Three input rungs

| Rung | Information supplied before imputation indicators |
| --- | --- |
| `four` | All four three-year characteristic histories, jointly: 12 fields |
| `broad` | Those histories plus up to 200 SEC concepts in signed-log levels |
| `metrics` | Those histories plus up to 100 concepts, normalized values, annual changes, and log assets |

For normalized metrics, USD quantities are divided by assets and share counts
are log-transformed. Annual differences are changes in snapshot values, not
necessarily percentage growth rates. The selected concepts are broad reported
measurements; some ratio numerators and denominators can refer to different
periods. This limits their economic comparability even when availability timing
is correct.

Schemas are selected using past support-period coverage, with at least 20%
coverage and deterministic tie-breaking. Preprocessing uses support-only median
imputation, missingness indicators, standardization, and clipping to [−8, 8].
Consequently, representation proximity can reflect reporting patterns as well
as operating fundamentals.

### 5.2 Shared support and training chronology

For return year `y`, query characteristics are known by the end of `y−1`.
Support snapshots come from `y−3` and `y−2`; their next-snapshot labels are
known by the query cutoff. The latest panel's supervised context label is
**next-snapshot capitalization/assets**. It is not a future return, and it is
not the income/assets label used in earlier exploratory experiments.

A deterministic, outcome-independent cap selects 256 historical support rows.
PCA, trained and random autoencoders, and pretrained models share these rows
within each input rung. Preprocessing is fitted on eligible past support before
that cap. Cross-rung eligibility is almost, but not completely, identical:
common support counts range from 254 to 256. The exact memberships are saved
in [context overlap](research/panel/context-overlap.csv) and annual context files.

PCA and the autoencoder are fitted afresh using historical support only. They
are not fitted once on the entire panel. A regression test checks that adding
a future snapshot does not alter earlier preprocessing. Unsupervised learning
still requires this timing discipline: absence of return labels alone would
not prevent future distributional information from entering the representation.

### 5.3 Representations actually evaluated

Each input rung has eight approaches:

| Approach | Representation |
| --- | --- |
| Direct | Standardized values, with a constant coordinate to avoid zero vectors |
| PCA | 16-component linear compression |
| Autoencoder | Small denoising network, 64 hidden units and 16 latent units, 200 training steps |
| Random autoencoder | Untrained counterpart of the same small network |
| TabPFN 3.5 Fast | Frozen native late query embedding |
| TabPFN 3.5 full | Frozen native late query embedding |
| Google TabFM 1.1 | Frozen post-ICL normalized query state |
| EXAONE Tabular | Frozen query label-token state entering the decoder |

The random autoencoder controls for a small random nonlinear projection. It is
**not** an architecture-matched untrained TabPFN, TabFM, or EXAONE model.
Foundation runs use one ensemble member, seed 42, and CPU execution. They use
internal row representations rather than point return predictions. Checkpoint
identity, context, schemas, and preprocessing provenance are saved.

The [typed encoder interface](src/python/README.md) distinguishes model-specific
extraction from mean, selected-token, and concatenation pooling. It checks row
identity, ordered schemas, and context availability. Equal vector dimensions do
not imply aligned coordinates across models. Distances are computed within each
model's representation; vectors from different models are not subtracted.
Table attention can also make a row's representation depend on the rest of the
query cohort. Annual cohort identity is therefore part of the experiment.

Only the four checkpoint variants above have results in this panel. Registry
support or a resolving dependency extra does not imply a completed experiment.
LimiX, Causilo, and SAP are not scored here. Nori was deferred because of recorded
dependency conflicts; Xiaomi-TabLDM was deferred for lack of an installable
runtime in the inspected source. These are implementation constraints, not
negative empirical findings about those models.

### 5.4 Pairwise distances and annual networks

For each original-style characteristic history, distance is

\[
 d_{ij}^{(k)}=\sqrt{2\{1-\rho_S(x_i^{(k)},x_j^{(k)})\}}.
\]

The joint reference uses

\[
 d_{ij}^{\mathrm{joint}}=
 \sqrt{\frac{1}{4}\sum_{k=1}^4(d_{ij}^{(k)})^2}.
\]

For representations, vectors are normalized and compared by chord distance:

\[
 v_i=z_i/\|z_i\|_2,\qquad d_{ij}=\|v_i-v_j\|_2.
\]

This yields distances between zero and two, removes overall vector magnitude,
and avoids imposing shared coordinates across checkpoints. It is a reasonable
fixed measurement choice, not proof that model geometry is economically valid.
It remains sensitive to anisotropic invertible transformations and to context.

Every nonuniform spatial network uses the same kernel:

\[
 W_{ij}=\frac{\exp(-d_{ij})}{\sum_{k\ne i}\exp(-d_{ik})},
 \quad i\ne j,\qquad W_{ii}=0.
\]

Bandwidth is fixed at one; no test-return optimization chooses it. A uniform
network with off-diagonal entries `1/(N−1)` controls for generic cross-sectional
dependence without characteristic geometry.

There are **290 saved annual distance matrices**: 29 distance-based approaches
over ten years. The corresponding weights, plus uniform and zero-network
references, yield 310 annual weight matrices. Geometry checks verify ticker
alignment, symmetry and zero diagonal of distances, finite values, expected
range, and reconstruction of normalized weights. No embeddings were flagged
as collapsed. These are dense networks; effective neighbor counts are recorded
in [the geometry audit](research/panel/geometry-audit.csv). A noncollapsed
embedding can still induce a diffuse network close to uniform.

## 6. Estimation and score definitions

### 6.1 One spatial parameter per approach

The factor and residual specification is

\[
 r_t=\alpha_y+B_yF_t+u_t,\qquad
 u_t=\lambda W_yu_t+\varepsilon_t,
 \qquad\varepsilon_t\sim N(0,\sigma_y^2I).
\]

Annual factor regressions, including an intercept, use the preceding three
calendar years of complete common return dates. The network is frozen within
an evaluation year. Each approach estimates **one constant** `lambda` using
pooled 2016–2019 residual Gaussian ML. A separate spherical innovation variance
is profiled for each calibration year. The coefficient is constrained to
(−0.99, 0.99); boundary flags use absolute estimates of at least 0.985.

With `A_y = I − lambda W_y`, the residual calibration likelihood has the form

\[
 \ell(\lambda,\{\sigma_y^2\})=
 \sum_y\left[
 T_y\log|\det A_y|-\frac{T_yN_y}{2}\log(2\pi\sigma_y^2)
 -\frac{1}{2\sigma_y^2}\sum_{t\in y}\|A_yu_t\|_2^2
 \right].
\]

This permits changing firms and networks across years while retaining a single
spatial coefficient. Annual nuisance variances do not constitute extra spatial
coefficients. Factor loadings are prior estimates, rather than jointly estimated
original-paper cross-sectional risk premia.

### 6.2 Held-out unconditional return density

For 2020–2025, the calibrated coefficient remains fixed. Each year's innovation
variance is estimated from prior residuals at that coefficient. The forecast
covariance is

\[
 \widehat\Sigma_y=
 \widehat B_y\widehat{\operatorname{Cov}}(F)_y\widehat B_y^\top
 +\widehat\sigma_y^2
 (I-\widehat\lambda W_y)^{-1}
 (I-\widehat\lambda W_y)^{-\top}.
\]

The mean forecast is the prior mean excess return. Realized test-year factors
are not inserted into this forecast. The principal score sums the full Gaussian
log density of subsequent daily excess-return vectors:

\[
 \ell_{\mathrm{test}}=-\frac12\sum_y\sum_{t\in y}
 \left[N_y\log(2\pi)+\log\det\widehat\Sigma_y+
 (r_t-\widehat\mu_y)^\top\widehat\Sigma_y^{-1}
 (r_t-\widehat\mu_y)\right].
\]

Higher is better. Returns are decimals and all Gaussian constants are included.
Positive log densities are valid for continuous returns; they are not probabilities
larger than one. Absolute values depend on units, dimension, and observations.
Only rows using the same definition and data can be compared directly.

**Calibration ML likelihood and held-out log-likelihood are separate quantities.**
The former is maximized on calibration residuals. The latter evaluates an
unconditional forecast on later returns and is not maximized on the test set.
Subtracting one from the other has no useful interpretation here.

### 6.3 Nonspatial and covariance controls

The spherical FF5+momentum reference fixes the spatial coefficient at zero.
The diagonal reference permits separate residual variances. Raw sample
covariance uses the same prior return window and mean forecast, without hidden
shrinkage. With these cohorts, the number of firms is below the number of prior
observations, so this benchmark is estimable.

A factor model with the full sample residual covariance reconstructs the raw
sample covariance under OLS orthogonality. Their equal scores are an algebraic
consistency check, not two independent successes. The saved reconstruction
errors are below approximately `7e-18`.

## 7. Latest chronological results

### 7.1 Input ladder: held-out log-likelihood

All cells below score the same 87,351 firm-days. Each cell is one joint
representation, one annual network sequence, and one calibrated spatial
coefficient. The table does not report separate fits for individual features.

| Representation | Four histories | + Broad disclosures | + Normalized metrics |
| --- | ---: | ---: | ---: |
| Direct | 219,960.75 | 219,978.84 | 219,996.03 |
| PCA, 16 components | 219,959.65 | 220,033.65 | 220,054.56 |
| Autoencoder | 219,952.35 | 220,031.71 | 220,045.25 |
| Random autoencoder | 219,947.21 | 219,960.87 | 219,956.91 |
| TabPFN 3.5 Fast | 219,980.70 | 219,981.42 | 219,980.16 |
| TabPFN 3.5 full | 219,985.25 | 219,990.10 | 219,980.69 |
| Google TabFM 1.1 | 219,963.10 | 219,963.29 | 219,962.36 |
| EXAONE Tabular | 219,983.45 | 219,984.77 | 219,983.71 |

### 7.2 Complete comparison, including calibration ML

The identifiers match the machine-readable results. A dash denotes a quantity
not estimated or reported for that nonspatial covariance benchmark. Every row
has the same held-out observations; no fitted coefficient has a boundary flag.

| Approach | Frozen lambda | Calibration residual ML LL | Held-out return LL | Gain vs joint four |
| --- | ---: | ---: | ---: | ---: |
| `fernandez_market_cap_assets` | 0.2088 | 177,843.41 | 219,946.41 | -46.83 |
| `fernandez_market_to_book` | 0.2086 | 177,843.31 | 219,894.13 | -99.11 |
| `fernandez_dividend_yield` | 0.1994 | 177,836.90 | 219,999.94 | +6.70 |
| `fernandez_debt_maturity` | 0.1331 | 177,791.17 | 219,900.80 | -92.44 |
| `fernandez_joint_four` | 0.2276 | 177,839.95 | 219,993.24 | +0.00 |
| `four__direct` | 0.2190 | 177,828.93 | 219,960.75 | -32.49 |
| `four__pca16` | 0.2178 | 177,828.17 | 219,959.65 | -33.59 |
| `four__autoencoder` | 0.2156 | 177,826.13 | 219,952.35 | -40.89 |
| `four__random_autoencoder` | 0.2147 | 177,824.49 | 219,947.21 | -46.03 |
| `four__tabpfn_fast` | 0.2272 | 177,834.57 | 219,980.70 | -12.54 |
| `four__tabpfn_full` | 0.2300 | 177,838.08 | 219,985.25 | -7.99 |
| `four__tabfm` | 0.2158 | 177,824.92 | 219,963.10 | -30.14 |
| `four__exaone` | 0.2270 | 177,834.84 | 219,983.45 | -9.79 |
| `broad__direct` | 0.2269 | 177,832.29 | 219,978.84 | -14.40 |
| `broad__pca16` | 0.2602 | 177,862.38 | 220,033.65 | +40.41 |
| `broad__autoencoder` | 0.2573 | 177,860.22 | 220,031.71 | +38.47 |
| `broad__random_autoencoder` | 0.2189 | 177,827.99 | 219,960.87 | -32.37 |
| `broad__tabpfn_fast` | 0.2288 | 177,835.83 | 219,981.42 | -11.82 |
| `broad__tabpfn_full` | 0.2320 | 177,839.93 | 219,990.10 | -3.13 |
| `broad__tabfm` | 0.2161 | 177,825.03 | 219,963.29 | -29.95 |
| `broad__exaone` | 0.2299 | 177,837.34 | 219,984.77 | -8.47 |
| `metrics__direct` | 0.2376 | 177,841.05 | 219,996.03 | +2.79 |
| `metrics__pca16` | 0.2668 | 177,870.59 | 220,054.56 | +61.32 |
| `metrics__autoencoder` | 0.2641 | 177,868.49 | 220,045.25 | +52.01 |
| `metrics__random_autoencoder` | 0.2299 | 177,836.66 | 219,956.91 | -36.33 |
| `metrics__tabpfn_fast` | 0.2285 | 177,835.67 | 219,980.16 | -13.07 |
| `metrics__tabpfn_full` | 0.2305 | 177,838.83 | 219,980.69 | -12.55 |
| `metrics__tabfm` | 0.2157 | 177,824.79 | 219,962.36 | -30.88 |
| `metrics__exaone` | 0.2296 | 177,837.00 | 219,983.71 | -9.53 |
| `ff5_mom_spherical` | 0.0000 | 177,754.77 | 219,784.95 | -208.29 |
| `uniform_network` | 0.2043 | 177,816.62 | 219,939.50 | -53.74 |
| `ff5_mom_diagonal` | — | — | 224,657.11 | +4,663.87 |
| `ff5_mom_sample_residual_covariance` | — | — | 224,819.87 | +4,826.63 |
| `raw_sample_covariance` | — | — | 224,819.87 | +4,826.63 |

Source: [full precision comparison](research/panel/comparison.csv).
Annual decompositions are in [annual scores](research/panel/annual-scores.csv).

### 7.3 Interpretation of the differences

The best pretrained row, full TabPFN with broad disclosures, falls only 3.13
log-score units short of the joint-four control across 87,351 firm-days. This is
approximately −0.000036 per firm-day. The result is near parity in this design,
not evidence that pretrained methods are generally inferior.

PCA with normalized metrics improves on the joint control by 61.32, or about
0.000702 per firm-day. The autoencoder's gain is 52.01. Both also exceed the best
individual-characteristic reference, dividend yield at 219,999.94. Their gains
suggest that additional accounting information can help when compressed simply;
they do not identify an advantage from external pretraining.

All evaluated pretrained rows exceed the uniform-network reference of
219,939.50. Thus, the results do not show that learned geometry contains no
information at all. They show that these particular learned networks do not
improve on the matched joint characteristic benchmark.

Raw covariance exceeds the best spatial row by 4,765.31, and the diagonal-residual
factor model exceeds it by 4,602.55. The current spatial specification uses
spherical innovation variance, whereas the diagonal benchmark allows firm-specific
residual variances and raw covariance allows considerably more structure.
Consequently, this gap cannot be attributed entirely to embedding quality.
Comparisons among the spatial rows isolate network choice more closely.

The spatial coefficients are positive and interior in this run. They describe
conditional dependence under the model; neither their signs nor likelihood
gains establish causality or priced risk. No nonnested likelihood-ratio p-values,
confirmatory model-ranking significance, or comparable R-squared statistics have
been estimated. The best configurations in this report were identified after
observing the development results.

## 8. Leakage controls and remaining sources of bias

| Issue | Implemented control | Remaining limitation |
| --- | --- | --- |
| Filing availability | Filing and period-end cutoffs; retained accessions | Current source vintage and economic comparability remain concerns |
| Feature vocabulary | Select concepts on historical support coverage | Coverage selection can favor particular reporting patterns |
| Imputation and scaling | Fit using historical support only | Missingness can become an informative proxy for firm type |
| PCA and autoencoder | Fit on historical support; future-snapshot regression test | Architecture and feature-design choices were researched on inspected periods |
| Foundation context labels | Labels available by cutoff; no return labels | Checkpoint pretraining information is not a verified historical information set |
| Spatial coefficient | Fit on 2016–2019 and freeze for 2020–2025 | These later years are already inspected development evidence |
| Covariance and mean | Estimate from preceding returns and factors | Annual forecasts may adapt poorly to changing volatility |
| Cohort selection | Determine before the return year | Current-listing selection and strict accounting completeness bias the sample |
| Missing outcomes | Remove identical dates for all methods | Scores condition on observed dates and omit unavailable outcomes |
| Year-boundary filing timing | Exclude first daily return each year | Date-level data do not provide a full intraday information audit |

A past-only PCA or autoencoder is acceptable for this chronological design.
Fitting either to all years before splitting would leak future distributional
information, even without future return labels. The same principle applies to
feature selection, scaling, support-context construction, and distance tuning.

Modern pretrained checkpoints are applied retrospectively. Some were released
after evaluated dates. The implementation's information-cutoff checks do not
prove absence of historical-data contamination in external pretraining and do
not establish that investors could have deployed these models at the time.

Daily Gaussian densities are working approximations. Serial dependence,
volatility clustering, overlapping estimation windows, and model selection make
naive independent-observation inference inappropriate. A single chronological
split also provides limited evidence about stability across regimes.

## 9. Theoretical contribution: current status

The [LaTeX working draft](src/latex/main.tex) separates predictive sufficiency,
economic information, and geometric validity. An invertible transformation of
an embedding can preserve predictions after a corresponding readout change
while altering distances. Successful pretraining therefore does not, by itself,
justify Euclidean or normalized embedding geometry as an economic metric.

The draft contains a conditional covariance-stability proposition. For two
networks on the same firms, the same coefficient and innovation covariance,
write

\[
 A=(I-\lambda W)^{-1},\qquad A^*=(I-\lambda W^*)^{-1}.
\]

If both spectral norms are at most `M`, the resolvent identity implies

\[
 \|ADA^\top-A^*D(A^*)^\top\|_2
 \le 2\|D\|_2|\lambda|M^3\|W-W^*\|_2.
\]

For exponential kernels with common bandwidth `h` and maximum distance error
`epsilon`, the draft also bounds the maximum absolute row-sum norm:

\[
 \|W-W^*\|_\infty
 \le\min\{2,\exp(2\epsilon/h)-1\}.
\]

This links distance error to network error and, conditionally, to covariance
error. It does not prove that pretraining recovers the true economic distance.
The resolvent bound must be assumed or checked; row normalization and a
coefficient below one do not supply the same simple spectral-norm bound for a
nonsymmetric network. Converting between these norms can introduce dependence
on the number of firms.

The result is a standard perturbation argument supporting the research design,
not an asserted new learning-theory theorem. It has not been established here
that pretraining loss bounds economic-distance distortion, that nearby firms
must have higher covariance, or that the learned network identifies transmission.
Those stronger claims require additional assumptions and evidence.

Finance Research Letters remains a provisional outlet. A defensible manuscript
could focus on measurement validity and a tightly controlled empirical comparison.
The present results do not support a headline claim that foundation models
outperform conventional financial proximity. The working draft is a design
and proof document; some acquisition passages describe earlier targets and
should be updated before it is treated as an empirical manuscript.

## 10. Engineering, verification, and reproducibility

The repository provides a typed encoder contract, explicit extraction and
pooling, immutable representation outputs, a model registry, checkpoint/context
provenance, cached public data, and labeled matrix exports. The panel
implementation separates characteristic construction, observations, networks,
likelihood estimation, orchestration, and reporting.

The last implementation validation recorded **33 passing tests**, including
Hypothesis-based numerical checks and focused chronology tests. The meaningful
checks include Gaussian-density equivalence, estimation of one coefficient
across changing networks, invariance to future preprocessing observations, and
an integration test of cohort timing and first-return exclusion. Ruff, Pyrefly,
Tach, Vulture, and the repository quality gates passed for that implementation.
These tests verify specific implementation properties, not economic validity or
external checkpoint training provenance.

Numerical and artifact checks also established:

- 34 unique approaches and 204 annual evaluation rows, with common firm-day counts.
- Annual scores sum to their corresponding pooled scores.
- Distance labels align with observations and derived network weights.
- No collapsed geometry was flagged across 290 distance matrices.
- No future filings, future period ends, or duplicate snapshot concepts were
  found in the completed disclosure audit.
- Full residual factor covariance reconstructs raw sample covariance to
  floating-point precision.
- Checkpoint hashes and input/source provenance are retained in the manifests.

Two implementation corrections relevant to interpreting the final outputs were
made during the completed work: missing price history at a share observation
date now yields a missing characteristic rather than an indexing failure, and
kernel exponentiation is stabilized without changing normalized weights. The
final comparison includes the first-return timing exclusion described above.
Earlier interrupted development logs are not the authoritative results.

### 10.1 Artifact map

| Purpose | Artifact |
| --- | --- |
| Latest generated methods and results | [Panel results](research/panel/RESULTS.md) |
| All coefficients and scores | [Comparison CSV](research/panel/comparison.csv) |
| Annual score contributions | [Annual scores](research/panel/annual-scores.csv) |
| Final sample sizes | [Panel coverage](research/panel/panel-coverage.csv) |
| Characteristic availability | [Characteristic coverage](research/panel/characteristic-coverage.csv) |
| Frozen configuration | [Configuration](research/panel/configuration.json) |
| Fact timing audit | [Disclosure audit](research/panel/disclosure-audit.json) |
| Network geometry diagnostics | [Geometry audit](research/panel/geometry-audit.csv) |
| Cross-rung context comparison | [Context overlap](research/panel/context-overlap.csv) |
| Model provenance | [Checkpoint record](research/panel/checkpoints.json) |
| Covariance identity check | [Reference check](research/panel/reference-check.csv) |
| Reproduction hashes | [Manifest](research/panel/manifest.json) |
| Earlier 100-issuer pilot | [Pilot results](research/pilot/RESULTS.md) |
| Earlier expanded model grid | [Expanded results](research/expanded/RESULTS.md) |
| Paper-aligned comparison | [Fernández results](research/fernandez/RESULTS.md) |
| Six-firm combined fit | [Combined results](research/fernandez/combined/RESULTS.md) |

Year-specific contexts live under `research/panel/contexts/`. Labeled pairwise
distance and weight matrices live under `research/panel/distances/<year>/` and
`research/panel/weights/<year>/`. Observations, prior residuals, and sample timing
records live under `research/panel/observations/`. Downloaded inputs and expensive
intermediate caches are ignored by Git; possession of the source alone is not
the same as possession of every reproduction input.

### 10.2 Reproduction commands

From the repository root, with the existing development environment and model
access configured:

```sh
devenv shell just python-universe
devenv shell just python-panel
```

Acquisition requires `EDGAR_IDENTITY` in the environment. The panel command uses
the acquired universe and retained model runtimes, checkpoint files, and caches.
Downloads depend on source availability and any applicable checkpoint access.
The saved manifests, rather than a fresh changing upstream download alone,
define the provenance of these reported results.

Earlier stages have their own documented commands and input prerequisites in
the linked experiment READMEs. Rerunning them is not required to interpret this
report, and their numerical outputs must not be combined with panel scores.

## 11. Priorities for the next experimental stage

These are proposed follow-ups, not completed results:

1. **Separate covariance restrictions from topology.** Repeat the matched network
   comparison with a predetermined heterogeneous diagonal innovation covariance
   while retaining one spatial coefficient per approach. This addresses the
   strong diagonal-factor benchmark without giving encoders different samples.
2. **Improve usable coverage transparently.** Reconcile additional debt and share
   mappings where justified; report a strict Fernández cohort alongside any
   broader cohort. Do not silently replace debt with liabilities, impute missing
   debt as zero, or compare likelihoods across different firm samples.
3. **Check history and geometry sensitivity.** Compare longer characteristic
   histories, fixed-reference contexts, and prespecified distance/kernel choices
   using development windows. Audit concentration and distinguish genuine state
   movement from changes in scaling, schema, support, or query composition.
4. **Add economic validation.** Test future exposure similarity and industry,
   size, leverage, and reporting-pattern controls. Establish what the network
   measures before interpreting it as a mechanism or an asset-pricing signal.
5. **Quantify uncertainty appropriately.** Use paired time-block procedures and
   explicitly account for overlapping estimation windows and model search.
   Reserve genuinely new evidence where possible; do not relabel already
   inspected years as an untouched confirmatory holdout.
6. **Keep the manuscript claim aligned with the evidence.** Report near parity or
   failure to improve if it persists. A stronger learning-to-economic-geometry
   theorem requires assumptions beyond the conditional perturbation result.

The immediate empirical contribution is a reproducible, audited comparison of
financial proximity measurements. A foundation-model advantage remains an open
hypothesis rather than an established result.
