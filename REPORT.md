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
from generated betas were not estimated. **This pilot cross-section is superseded
by the R0 replication in §3.6**, which uses one common sample per arm on the
1,000-issuer universe.

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
to the current daily panel score. **Superseded by the cross-sectional ladder in
§3.7**; the files are retained only as history.

### 3.5 Universe expansion and chronological panel

The next step acquired 1,000 issuers and return/factor histories from 2008 through
2025, then rebuilt the characteristics and ran the latest matched panel.
Shortening the required characteristic history to three annual observations
increased usable cohorts substantially. This is an explicit design compromise,
not an unchanged replication on a larger sample.

The remainder of this report treats that chronological panel as the principal
current comparison. Earlier files are retained as research history rather than
overwritten or pooled with the new results. The first panel run (§7.1–7.3,
files at the `research/panel/` root) is kept unchanged as the **v1 record**;
the extended designs in §7.4 write to `research/panel/{four,four-h5,four-xqxo,three}/`
and reproduce the v1 rows exactly where the specification is unchanged.

### 3.6 R0: practical replication of Fernández on the 1,000-issuer universe

[R0](research/ladder/r0/RESULTS.md) re-runs the paper's own exercise as closely
as US public data permit; every substitution is typed in the
[replication manifest](research/ladder/r0/replication-manifest.md). Stage one
fits robust MM CAPM betas (`robustbase::lmrob`, seed reset before every firm)
on 40 quarterly excess returns, 2016–2025. Stage two regresses each firm's median
quarterly excess return on its beta without an intercept, by OLS, spatial-lag
S2SLS (eq. 2 standard errors), and SAR-error concentrated ML; lag-ML is a
labelled extension. Networks are Spearman chord distances between 2015–2024
annual characteristic histories under `exp(−d)`, row-normalized, zero diagonal.
Self-links and a median-scaled kernel are reported as sensitivities.

| Table | Firms | OLS premium | SEM λ (information SE) | SEM λ bootstrap 95% |
| --- | ---: | ---: | --- | --- |
| Common four, cap/assets W | 33 | 0.030 | 0.81 (0.14) | [−0.99, 0.87] |
| Common three, cap/assets W | 395 | 0.031 | 0.96 (0.03) | [0.90, 0.96] |
| Cap/assets coverage | 653 | 0.031 | 0.97 (0.03) | [0.91, 0.97] |
| Debt-maturity coverage | 62 | 0.030 | 0.90 (0.07) | [−0.99, 0.92] |

Main points:

- Ten-year complete histories of all four characteristics leave only **33
  firms**; debt maturity is the binding constraint. On that sample the SAR-error
  coefficient is not identified once generated-beta uncertainty is included.
- Without debt maturity, 395 firms remain. OLS-residual Moran's I is positive
  (p < 0.001 under exact moments) for every network, and the SAR-error coefficient
  is large and tightly bounded. The spatial premium falls to roughly 0.014 per
  quarter and its bootstrap interval includes zero.
- The generated-beta bootstrap (199 stationary-bootstrap quarter resamples, MM
  refitted, W fixed) gives premium standard errors several times the conditional
  ones. Conditional p-values in the R0 tables should not be read as final.
- Coefficients near the paper's 0.85–0.87 are not a calibration target; the
  sample, market, period and benchmark rate all differ.

### 3.7 Cross-sectional ladder R1–R4

The [ladder](research/ladder/README.md) keeps the R0 sample, outcome and
exposures fixed and changes one thing per rung: R1 combines characteristics
(joint RMS, direct and Ledoit–Wolf Mahalanobis distances), R2 replaces the
distance by representations of the same histories, R3 adds 2024 broad SEC
concepts, and R4 swaps CAPM for FF5+momentum MM exposures. Each row is one
SAR-error coefficient for one combined network under three kernels (§5.4).
The two arms are never ranked against each other.

Three-characteristic arm, 395 firms, CAPM exposures, SAR-error log-likelihood
gain over OLS (881.88):

| Network | exp | median | matched |
| --- | ---: | ---: | ---: |
| Fernández cap/assets | **+39.19** | +34.88 | +35.10 |
| Fernández market-to-book | +37.43 | +33.69 | +33.58 |
| Fernández joint | +36.65 | +32.80 | +36.65 |
| EXAONE label token, + broad | +27.64 | +36.56 | +28.78 |
| Supervised MLP16 (control) | +31.70 | +36.37 | +27.59 |
| TabFM late | +24.70 | +33.97 | +29.18 |
| TabFM early concat (state) | +26.14 | +30.11 | +28.40 |
| PCA16 | +26.68 | +27.68 | +26.14 |
| Uniform network | +22.49 | | |

All non-uniform networks beat 99 size-tercile placebo permutations (rank
p = 0.01). The single cap/assets network remains the best; under the median
kernel the best learned representations reach the joint network but not the
single characteristic. With FF5+momentum exposures (R4) the order is unchanged
and BIC prefers FF5+momentum to CAPM (−1842.9 versus −1819.1 for the joint
network). Conditional information criteria prefer spatial over nonspatial and
SAR-error over lag-ML; for rows with equal parameter counts they reproduce the
likelihood ranking and add nothing.

The 33-firm four-characteristic arm is uninformative: all gains lie between
0.4 and 2.1 log-likelihood units and most placebo rank p-values exceed 0.1.

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

The extended panel (§7.4) adds two cohorts alongside this one. Each requires
complete, nonconstant histories at every history length its networks use, so
every network in a design is built on the same firms:

| Design | Characteristics | Cohort histories | Role |
| --- | --- | --- | --- |
| `four` | all four | 3 years | primary strict design; reproduces v1 |
| `four-h5` | all four | 3 and 5 years | history-length sensitivity on one cohort |
| `three` | cap/assets, M/B, dividend yield | 3 and 5 years | broader cohort without debt maturity |

Designs are never ranked against each other; their firm-days differ.

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

The extended designs separate two readout arms, because every foundation
readout is `z = E(x | X_s, y_s)` and the support labels `y_s` can enter it:

| Arm | Readouts | Where support labels enter |
| --- | --- | --- |
| A, state | TabFM `early_concat` (primary), `early_mean`; EXAONE layer-0 item summaries | TabFM adds support `y` to training cells before column attention; EXAONE layer 0 is label-free |
| A, label-null check | TabFM `early_concat_labelnull` (support `y ≡ 0`) | none |
| B, task-conditioned | TabPFN late; TabFM late; EXAONE label token; EXAONE last-layer item summaries; supervised MLP16 | through in-context attention or training |

The supervised MLP16 (width→64→16→1, trained on the same support target) is a
task-conditioned control without pretraining. Classical rows add a Ledoit–Wolf
Mahalanobis distance fitted on the support. An alternate support target,
next-snapshot net income over assets, is run on the histories rung
(`histories@income_assets`). EXAONE's layer-0 summaries are nearly constant
across firms and induce an almost uniform network; they are reported, not
interpreted.

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

Bandwidth is fixed at one; no test-return optimization chooses it. Because
learned chord distances are compressed, this kernel makes their networks close
to uniform (mean effective-neighbour fraction 0.94–0.99 versus 0.87 for the
joint Fernández network). The extended runs therefore report two predetermined
alternatives, `exp(−d/h)` with the row minimum subtracted before
exponentiation:

- **median**: `h` is the median positive off-diagonal distance in that year;
- **matched**: `h` is bisected so that the mean effective number of neighbours
  equals that of the joint Fernández network in the same year.

Neither choice uses returns. The matched kernel equalizes concentration, so
remaining differences reflect who is near whom rather than how diffuse the
network is. A uniform
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
an evaluation year. (The extended runs add diagonal innovations; see the end
of §6.2.) Each approach estimates **one constant** `lambda` using
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

**Innovation arms (extended runs).** The v1 spatial rows use spherical
innovations while the factor benchmark is diagonal, which confounds topology
with volatility. The extended designs score every network under three arms,
each with its own frozen λ:

- *spherical*: `ε ~ N(0, σ²_y I)`, the v1 specification, reproduced exactly;
- *diagonal*: `ε ~ N(0, D_y)` with `D_y,ii = mean_t[((I − λW_y) u_t)_i²]` from
  prior residuals; at λ = 0 it equals the diagonal FF5+momentum benchmark bitwise;
- *correlation-only*: `Σ* = S corr(Σ̂) S`, with `S` the prior raw sample
  standard deviations, applied to every row including the controls, so all rows
  share identical marginal variances and differ only in correlation structure.

Per-day log densities are saved, and paired score differences against the
joint Fernández network (exp kernel) and the uniform network are bootstrapped
with `arch`'s stationary bootstrap (9,999 replicates, expected block 21 days,
63 days and the Politis–White choice as sensitivities). A model confidence set
(`method="max"`, size 0.10) is computed within each innovation × kernel family,
and 19 within-size-tercile `PWPᵀ` permutations of selected networks give
placebo rank p-values. All of this is development evidence on already
inspected years; the intervals do not account for the model search.

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

### 7.4 Panel extension: measurement variants and likelihood attribution

The [panel extension](research/panel/README.md) re-runs the comparison in four
declared designs with three kernels and three innovation arms. Designs differ in
firms (`four` scores 87,351 firm-days, `three` 642,024) and are not ranked
against each other. Unless stated, figures are held-out gains over the joint
Fernández network with diagonal innovations; intervals are 95% stationary
bootstrap intervals with 21-day blocks. These are development results: the years
were inspected and the variants were added after earlier runs.

**Support redraws.** Re-encoding the history rung on two differently salted
256-row supports changes the measured gains by up to a third:

| Design, exp kernel | Native | Redraw 1 | Redraw 2 | Native interval |
| --- | ---: | ---: | ---: | ---: |
| `four`, TabFM early concat | +37.8 | +26.5 | +24.9 | [−17.1, +115.3] |
| `four`, TabPFN full late | +21.4 | +33.3 | +18.8 | [−32.3, +97.9] |
| `four`, EXAONE late | +21.6 | +21.0 | +14.7 | — |
| `three`, TabFM early concat | −1,035.2 | −1,052.3 | −952.6 | [−1,873.6, −440.3] |
| `three`, TabPFN full late | −225.8 | −297.1 | −88.8 | [−784.6, +440.5] |

In `four` no learned interval excludes zero. In `three` the direct history
distance (+1,217.0, [+363.1, +2,412.5]) beats every foundation readout under the
exp kernel. Changing only the support target on shared rows moves results as much
as a redraw (`four` EXAONE late: +23.1 with cap/assets, −0.4 with income/assets).
These shifts are why §9 grades every learned procedure as an exploratory
comparator, not an economic dissimilarity measure.

**Calibrated readouts.** Decoding five prior-covariance exposures out of fold
works poorly in `four`: every representation has negative mean out-of-fold R²
(best −0.005), with roughly 60 firms per year. In `three` the foundation states
decode better than the classical compressions (R² 0.17–0.23 against at most 0.04
for PCA and the autoencoders; decoded-distance Spearman 0.36–0.42 against
0.18–0.23). Under the exp kernel every decoded network is effectively the uniform
network (`four` −39.9 against −40.2; `three` −4,541 against −4,591; same mean
Herfindahl index): decoded exposures are shrunk, so `exp(-d)` is flat. The
rescaled kernels separate them. With the matched kernel in `three`, decoded
TabPFN full (+3,390.8) and EXAONE late (+3,451.4) exceed their native readouts
(+716.7, −149.1), and the `covariance_exposures` control reaches +7,347.1. In
`four` decoding lowers the matched-kernel gains (TabFM +103.6 against +179.7
native). One decoder is numerically unstable (`three`
`exaone__item_first_concat`, mean R² −301.6) and is not interpreted.

**Where the likelihood comes from.** The exact attribution (`Likelihood.spatial_loss`,
[`four`](research/panel/four/RESULTS.md#where-the-residual-likelihood-comes-from))
puts almost all of each network's residual gain over the uniform network in the
alignment term, which is linear in λ. Under the exp kernel the joint network
gains +411 (alignment +617) and TabFM early concat +211 (alignment +393). Mean
row Herfindahl indices stay between 0.018 and 0.023, so the concentration
charges are small (at most −104 for the joint network). Under the matched kernel
the covariance-exposure control gains +2,058 from +4,080 alignment less −950
concentration. That is the largest residual gain recorded, and it comes from a
target the representations do not yet decode reliably.

**QXO sensitivity.** Excluding QXO (`four-xqxo`), whose genuine −80% day falls on
2024-07-30, moves no history-rung gain in `four` by more than 1.1 (TabFM early
concat +37.8 → +37.4; TabPFN full late +21.4 → +20.5). The single extreme day
does not drive the learned rows.

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
| Support labels in readouts | Arm A/B split; TabFM label-null pass; shuffled-label audit | Arm A TabFM `early_concat` still sees support `y` (§5.3) |
| Query-cohort dependence | Audit of halves, reversed order and singletons (`research/panel/audit/`) | FeatureEncoder statistics span support and query rows |
| Stale cached distances | Distances recomputed every run; sidecar context digest checked | Embedding cache is keyed by context digest, checkpoint and readout version |
| Kernel choice | Median and matched bandwidths fixed by rule, not by returns | Both rules were added after inspecting v1 geometry |

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

The theory is organised as four separate questions about a learned measurement.
Each has machine-checked results in [`src/lean`](src/lean/README.md), proved
*given their stated assumptions*; none shows that a particular checkpoint
satisfies those assumptions.

| Level | Question | Formal results | Status in the evidence |
| --- | --- | --- | --- |
| 1. Information | What does the objective make an optimal model keep? | `Score` (proper scores recover a conditional law or moment), `Recovery.excess_risk_condExp` (excess risk is distance to the Bayes predictor) | Not tested: no checkpoint is shown to be near-optimal for its own objective |
| 2. Sufficiency | Is that enough for the economic state? | `Alignment` (deterministic core), `Sufficiency.sufficient_iff` (statistical form: every representation reproducing `E[X\|H]` reproduces `E[Y\|H]` iff `E[Y\|H] = g(E[X\|H])` a.s.), `Sufficiency.constant_target_iff` (label-null targets guarantee nothing) | Label pathways audited (§8); no support target is shown to determine the exposure state |
| 3. Measurement and geometry | Can the state and its distances be read out stably, and are they identified? | `Recovery` (linear decoder, `1/κ` gain), `Measurement` (any `K`-Lipschitz readout: `‖d(g(F̂), s)‖₂ ≤ K‖d(F̂, F)‖₂ + ‖ξ‖₂`; merged histories force error ≥ half their distance), `Recovery.scalar_not_distinguishes` (one scalar target cannot distinguish ≥ 2-dimensional exposures), `Geometry.observationally_equivalent`, `distances_preserved_iff` (task means identify exposures only up to an invertible map; distances survive only isometries) | Native distances are not covered by `Recovery`; the calibrated-readout rows (§7.4) are the first empirical counterpart |
| 4. Econometric use | What does the spatial model do with the distances? | `Kernel`, `Network`, `Value`, `Stability`, and `Likelihood.spatial_loss` (below) | Exact attribution of every residual likelihood (§7.4); generated-network inference remains on paper |

**What the likelihood sees of a network.** For the spatial-error forecast
`Σ = A⁻¹DA⁻ᵀ`, `A = I − λW`, the expected Gaussian loss against a second moment
`M` is exactly

\[
\sum_i \log d_i \;-\; 2\log|\det(I-\lambda W)| \;+\; \sum_i m_i(\lambda)/d_i ,
\]

with filtered second moments `mᵢ(λ) = [(I − λW)M(I − λW)ᵀ]ᵢᵢ`
(`Likelihood.spatial_loss`). When `M` is a common part `⟪aⱼ, aₖ⟫` plus
idiosyncratic variances `ηⱼ` and `W` has zero diagonal,

\[
m_i(\lambda) = (\|a_i\|^2+\eta_i) - 2\lambda\sum_j W_{ij}\langle a_i,a_j\rangle +
 \lambda^2\Big(\big\|\sum_j W_{ij}a_j\big\|^2 + \sum_j W_{ij}^2\eta_j\Big)
\]

(`Likelihood.filtered_second_moment_expand`). The term linear in `λ` is the
covariance inner product that `Value.decomposition` splits into hub and
proximity parts; idiosyncratic variance never enters it. The quadratic term
charges a concentration cost whose noise part is the row Herfindahl index
times `η`, at least `1/m` for a row spread over `m` firms
(`Likelihood.herfindahl_ge`). A diffuse row pays the least, which is one reason
near-uniform learned networks can score well without proximity information.
Matching mean effective neighbours (the `matched` kernel) does not equalise
this cost, which depends on the mean Herfindahl index instead.

**Native versus calibrated geometry.** The learned rows in §7 measure chord
distance between raw hidden states. No decoder is fitted, so the recovery
theorems certify none of them. A calibrated readout decodes a declared economic
target from the states and measures distance between decoded values. Its error
is bounded by `Measurement.rms_measurement_error` given an alignment error that
must itself be estimated. Distances between posterior-mean exposures understate
expected distances by the posterior variance of each pair's difference
(`Measurement.mean_sq_distance`).

**Claim grades.** Following the external review, every learned procedure is
graded by the strongest claim its evidence supports:

| Grade | Requires | Procedures here |
| --- | --- | --- |
| Exploratory comparator | A reproducible measurement procedure (checkpoint, context, extraction, readout, metric) | Every learned row |
| Economic proxy | Independent validation against a declared economic target | Calibrated readouts, to the extent their decoders fit prior-covariance exposures out of fold (§7.4) |
| Economic dissimilarity measure | Metric evidence: distances stable under declared nuisance changes and aligned with target distances | None. Support redraws move learned distance rankings materially (§7.4, §8) |
| Structural or causal | Identification of responses under intervention | None |

The covariance-stability proposition in the [working draft](src/latex/main.tex)
(`Stability`, `Kernel`) links distance error to network error and,
conditionally, to covariance error. It is a standard perturbation argument
supporting the design, not a learning-theory theorem. Not established here:
that pretraining loss bounds economic-distance distortion, that nearby firms
must have higher covariance, or that a learned network identifies transmission.

Finance Research Letters remains a provisional outlet. The defensible
contribution is a task-relative account of when pretrained representations can
serve as economic measurements, with the Fernández replication and extension as
a controlled application. The present results do not support a headline claim
that foundation models outperform conventional financial proximity.

## 10. Engineering, verification, and reproducibility

The repository provides a typed encoder contract, explicit extraction and
pooling, immutable representation outputs, a model registry, checkpoint/context
provenance, cached public data, and labeled matrix exports. The panel
implementation separates characteristic construction, observations, networks,
likelihood estimation, orchestration, and reporting.

The current implementation records **69 passing tests** (the v1 panel had 33),
including checks of `lag_iv`, `error_ml` and `lag_ml` against PySAL `spreg`, exact
residual Moran moments with and without self-links, kernel monotonicity and
placebo spectra, diagonal and correlation-only panel densities, and an R smoke
test of the MM first stage (outlier robustness, firm-order invariance, identity
bootstrap replicate). The v1 panel validation recorded 33 tests, including
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
| Six-firm combined fit (superseded) | [Combined results](research/fernandez/combined/RESULTS.md) |
| R0 replication | [R0 results](research/ladder/r0/RESULTS.md), [replication manifest](research/ladder/r0/replication-manifest.md) |
| Cross-sectional ladder | [Three arm](research/ladder/three/RESULTS.md), [four arm](research/ladder/four/RESULTS.md) |
| Extended panel designs | [Panel index](research/panel/README.md) and `research/panel/{four,four-h5,three}/RESULTS.md` |
| Encoder measurement audit | `research/panel/audit/` |

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
devenv shell just python-panel            # extended designs: four, four-h5, three
devenv shell just python-ladder-r0        # R0 replication and generated-beta bootstrap (needs R)
devenv shell just python-ladder           # R1–R4 cross-sectional ladder
devenv shell just python-encoder-audit    # context, query-cohort and label audits
```

The MM first stage runs `src/python/free_foundations/fernandez/betas.R` with
`robustbase`; manifests hash `.R` as well as `.py` sources. Embeddings,
matrices, bootstrap draws and daily scores are parquet/npz files ignored by Git.

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
