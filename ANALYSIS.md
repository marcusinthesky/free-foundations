# Analysis: why measure financial proximity with pretrained tabular models?

**Status: 18 October 2026. Provisional.** All five panel designs and the encoder
measurement audit are complete. Figures below come from them and the
cross-sectional ladder; §3 and §6 read the predictions against the `three` and
`three-support` results. The empirical
record is [REPORT.md](REPORT.md); the formal results are in
[the LaTeX draft](src/latex/main.tex). This note sets out the theoretical
motivation for the study and reads the current evidence against it, drawing on
three recent Pricing Perspective research notes:

- *Learn, then Explain* (15 October 2026): statistical learning, model capacity
  and economic mechanisms as restrictions on learning;
- *Why use Pretraining?* (17 October 2026): pretraining as a better-informed
  prior, and the limits of transfer;
- *What Does AI Actually Measure About the Economy?* (20 October 2026): learned
  representations as predictive versus structural economic states.

All results here are development evidence on already inspected years. The
intervals quoted do not account for the model search.

## 1. The measurement question

Fernández (2011) treats financial contiguity as something to be *measured*:
firms are close when the histories of their characteristics co-move, distance is
`d = sqrt(2(1 − ρ_S))`, and an exponential kernel turns distance into a
row-normalized spatial weights matrix `W`. The spatial coefficient then describes
how strongly residual shocks are shared along that network.

This project asks whether pretrained tabular models can measure that proximity
better. The model's role is to supply `W`; it is not a new pricing factor and is
not given extra coefficients. Every network, classical or learned, enters with
exactly one spatial parameter. That design choice is the first theoretical
commitment of the study: it keeps estimation capacity constant so that
differences in fit can be attributed to the geometry rather than to flexibility.

Three questions then follow, one from each note.

1. **Capacity:** with few independent economic experiences, how can evidence
   distinguish many candidate networks, and what restricts the search?
2. **Transfer:** when should a model pretrained elsewhere improve a network
   learned from a small, scarce financial sample?
3. **Measurement:** when is a representation that helps prediction also a
   measurement of economic state?

## 2. Capacity, mechanisms and what the comparison controls

*Learn, then Explain* frames learning as selecting a hypothesis from a class
using a finite sample. For a finite class and `n` independent observations,

```text
R(h) ≤ R̂_n(h) + sqrt((log|H| + log(1/δ)) / 2n)   for all h ∈ H.
```

Two features of this study map directly onto that bound.

**The estimation class is deliberately small.** One λ per network, with
FF5+momentum loadings estimated from prior data, means the spatial model itself
adds one degree of freedom whichever representation produced `W`. The Fernández
networks are a mechanism-motivated restriction: similar financing and valuation
states imply exposure to common shocks. A learned network replaces the
characteristic-correlation mechanism with a representation, but does not
enlarge the estimated model.

**The search across networks is not small.** The `four` panel design scores
roughly 700 columns (readouts × input rungs × kernels × innovation arms).
Selecting the best of these is itself a choice from a class with
`log|H| ≈ log 700`. Reporting the best row and a paired interval would ignore
that penalty. The design therefore reports model confidence sets within each
innovation × kernel family, placebo permutations within size terciles, and
reference comparisons fixed in advance (the joint Fernández network and the
uniform network). The confidence sets are broad: in the diagonal-innovation,
exponential-kernel family 33 of 71 rows survive at the 10% level.

**Economic structure explained the largest gap.** In the first panel run,
spatial models trailed the FF5+momentum diagonal benchmark by about 4,600
log-likelihood units. The extended run shows that this gap was mostly
heterogeneous idiosyncratic volatility, not topology: once innovations are
diagonal, the joint Fernández network (224,826.7) exceeds both raw sample
covariance (224,819.9) and the diagonal factor model (224,657.1). This is the
note's argument in miniature: a known economic regularity (firms differ in
idiosyncratic risk) accounted for more than any increase in representational
flexibility.

## 3. Pretraining as a prior over networks

*Why use Pretraining?* reads pretraining as sequential Bayesian updating: the
pretraining corpus produces `p(M | D_pre)`, which becomes the prior for the task
sample. Under conditional independence, the log-odds between two models add the
evidence from both datasets:

```text
log posterior odds = log prior odds + Σ_pretraining evidence + Σ_task evidence.
```

When the task sample is small, the pretraining term decides between models the
task data cannot separate. When the task sample is rich, the task term
dominates. Transfer helps only where the source relationships remain valid in
the target (the Ben-David `λ*` term is small).

Tabular foundation models fit this reading unusually closely. TabPFN-style
models are trained to approximate the posterior predictive over a prior of
synthetic tasks, so in-context learning on a support set is an amortized version
of the update above. The support set is `D_post`: 256 firm-years with their
characteristics and a next-year target.

The evidence lines up with the three predictions this implies.

**Prediction 1: the advantage is largest where task evidence is thinnest.**
On the histories rung (30–40 features, 47–70 firms per year), every foundation
model readout beats every non-pretrained control once kernels are calibrated.
Gains over the joint Fernández network, diagonal innovations, median kernel:

| Readout | `four` | `four-h5` |
| --- | ---: | ---: |
| TabFM early state | +130 | +75 |
| TabFM late | +129 | +69 |
| EXAONE last-layer items | +126 | +77 |
| EXAONE label token | +110 | +71 |
| TabPFN Fast late | +89 | +65 |
| TabPFN full late | +70 | +47 |
| PCA16 | −47 | −69 |
| Autoencoder | −80 | −71 |
| Supervised MLP16 | −78 | −28 |

The larger `three` design and the support-size experiment do not bear this
prediction out. With 329–459 firms a year, PCA16 and the direct history distance
beat every foundation readout under the exp and median kernels, and under the
matched kernel TabFM's early state (+2,294) is only level with PCA16 (+2,209).
Shrinking the in-context support from 256 to 32 rows on the same firms
(`three-support`) does not open a foundation-model advantage either: TabFM's
native gain falls from +2,294 to +1,507 while PCA16 stays near +2,460, so at 32
rows TabFM trails PCA by −949 [−1,706, −492]. The native foundation geometry needs
more task evidence, not less. The advantage that does appear is in decoded
states (Prediction 2), and it is flat in support size.

On the metrics rung (about 430 disclosure features), the prior matters less.
Under the matched kernel, standardized metrics with a plain distance gain +288,
level with TabFM's early state (+282). Richer task inputs let simple methods
recover what the prior supplied.

**Prediction 2: the same labels without the prior should not help.** The
supervised MLP16 sees the same 256 support rows and the same targets but has no
pretraining. It loses to the joint Fernández network (−78 in `four`). The
difference between it and TabFM given identical labels was the clearest estimate
we had of what the prior contributes. `three-support` adds a sharper one: full
TabPFN with its weights re-initialized, the same architecture and preprocessing
with no pretraining. Decoded through the same held-out readout, trained TabPFN
beats it by +1,288 to +1,694 at every support size, every interval above zero,
and decoder R² falls from 0.28 to 0.17–0.19 without trained weights. That is
evidence that the trained weights carry recoverable signal. It is not evidence for
the small-sample mechanism, since the gap does not grow as the support shrinks.

**Prediction 3: the prior alone is not a financial geometry.** Setting the
support labels to zero removes most of TabFM's advantage (+130 → +8 in `four`,
+75 → +5 in `four-h5`; both intervals include zero). A prior learned from
synthetic tabular tasks does not encode which firms share shocks; it becomes
useful when combined with task evidence. The data do not support the claim that
pretraining supplies economic structure on its own. Decoded through a held-out
readout, the label-null state loses less: TabFM with labels beats its label-null
twin by only +309 to +703 at each support size (`three-support`), so most of the
decodable signal survives constant labels.

**Large in rows, small in experiences.** The note warns that economic data can be
large in observations but small in independent experiences. That is literally
the case here. Year-by-year gains of TabFM's early state over the joint
Fernández network in the `four` design (diagonal innovations, median kernel)
are:

| 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
| ---: | ---: | ---: | ---: | ---: | ---: |
| +86 | +6 | +3 | +12 | +10 | +13 |

EXAONE and TabPFN show the same profile. The plain metrics distance under the
matched kernel is also strongest in 2020 (+109) but more even afterwards (+27 to
+42). Most of the 87,351 scored firm-days add
little independent evidence about which network is right; one market-wide shock
contributes most of the separation. The bootstrap resamples days, not regimes,
so it cannot represent this.

**The cross-section is the counterpoint.** In the 395-firm cross-sectional
ladder, with ten-year histories, no learned network beats the single
capitalization/assets Fernández network. The best learned rows (EXAONE label
token and the supervised MLP under the median kernel) only reach the joint
network. With longer histories and more firms, the task evidence may be enough
on its own. The `three` panel design (329–459 firms per year) found the same in
the panel setting: simple distances match or beat the native foundation readouts.

## 4. Predictive state versus economic state

*What Does AI Actually Measure About the Economy?* distinguishes a predictive
economic state from a structural one. A representation `Z = f(H)` is predictively
sufficient for outcomes `C` when `P(Y_c | H) = P(Y_c | Z)`, and the natural notion
of similarity is task-weighted dissimilarity between implied outcome
distributions:

```text
d_C(h, h') = Σ_c ω_c d(Q_c(· | h), Q_c(· | h')).
```

### The label dependence is task-weighted geometry

Every foundation readout here is `z = E(x | X_s, y_s)`: a function of the query
row and a support set that includes targets. The label-null result says the
useful geometry comes from conditioning on `y_s`. In the note's terms, the
network approximates `d_C` for `C` = next-year capitalization/assets. That is not a
defect, but it changes the question from "what does the model know about firms"
to "which outcomes is this geometry sufficient for".

One check is already available. Replacing the target with next-year net income
over assets leaves the gains almost unchanged (TabFM early state by year:
+94, +5, −5, +10, +9, +11 against +86, +6, +3, +12, +10, +13). The specific
label matters less than conditioning on *some* financial outcome. A plausible
reading is that any financial target directs the in-context state toward
dimensions shared across outcomes, such as size, profitability and leverage;
this is a hypothesis, not yet a result.

### Kernel calibration is an invariance requirement

The note asks that a representation be invariant to transformations that leave
economic state unchanged and sensitive to those that change it. Learned chord
distances are compressed, so the paper's `exp(−d)` kernel turned them into
nearly uniform networks (mean effective-neighbour fraction 0.94–0.99, against
0.87 for the joint Fernández network). Ranking models under that kernel ranks
how diffuse their networks are, not who is near whom. Overall distance scale is
a nuisance transformation, not economic content.

The extended runs therefore report two bandwidth rules that use no returns: the
median positive distance, and a bandwidth matched so that each network has the
same mean effective number of neighbours as the joint Fernández network. The
matched kernel holds concentration fixed, so remaining differences reflect
topology. Within-size-tercile placebo permutations are a further invariance
check: they keep the spectrum and size structure and destroy the specific
neighbour assignments.

### Which of the note's criteria have been tested

The note proposes five criteria. The current evidence covers them unevenly.

| Criterion | Current evidence | Status |
| --- | --- | --- |
| Recovery of independently observed quantities | Held-out decoding of a reliable statistical common-risk target: R² at most 0.10 (`four`) and 0.30 (`three`) against a 0.90 ceiling; no economically identified target | Partial |
| Sensitivity to economically material changes | Placebo permutations; kernel and history-length sensitivity | Partial |
| Invariance to nuisance transformations | Kernel scale; query cohort (distance Spearman ≥ 0.999); support redraws (median 0.90–0.97, minimum 0.57); shuffled labels change task-readout rankings almost completely (TabPFN median 0.13–0.20) | Partial |
| Calibration of uncertainty | Gaussian densities only; no state uncertainty | Not tested |
| Stability across regimes | Gains concentrated in 2020 | Weak |

By the note's own standard, the foundation-model networks are useful
predictive geometries, not yet measurements of economic state.

### Two observation systems

The note's multiview framing also applies. The characteristic histories and the
SEC disclosure concepts are two imperfect observation systems of the same
firms. The foundation-model advantage is clearest on the histories alone and
narrows when the broad and metrics rungs add a second channel. That is
consistent with the models compensating for a thin single channel rather than
recovering a latent state that the richer channel lacks. A sharper test would
predict one channel's future values from the other and ask whether the learned
state reconciles them.

## 5. A formal lens: sufficiency is relative to a target

The 9–10 October working conversation on self-supervised learning and economic
state (ChatGPT, exported 17 October 2026) contains a useful formal core. Its
literature survey and model rankings are not relied on here; the arguments
below are standard and were checked independently.

### 5.1 The minimal predictive state

Fix histories `H`, a task set `C` and outcome laws `Q_c(· | h) = P(Y_c | H = h)`.
Call two histories equivalent when they imply the same law for every task. The
map `S*(h) = (Q_c(· | h))_c` is then sufficient, and every sufficient
representation `Z` determines it: `S* = r(Z)` almost surely. This is the
predictive-state construction of computational mechanics and the formal
version of the 20 October note's equivalence classes. Its consequence for this
study is that **sufficiency is always relative to `C`**; there is no
target-free notion of "the" economic state to recover.

### 5.2 A representation preserves what its target requires

Let a model be trained to predict a target `W` under a loss with unique
Bayes-optimal statistic `F(h)` (the conditional mean for squared error, the
conditional law for a strictly proper score), with the predictor reading `H`
only through `Z = f(H)`. At the population optimum, `d(Z) = F(H)`. Then:

- every optimal `Z` is sufficient for `C` **if and only if** `F(h) = F(h')`
  implies `S*(h) = S*(h')`, so the target must separate every pair of histories
  the economic tasks separate;
- the minimal economic state can itself be optimal for the target **if and only
  if** the converse holds, so the target must not require distinctions economics
  treats as irrelevant.

The proof is a factorization argument: if two histories share `F` but differ in
`S*`, then `Z = F(H)` is optimal and merges them. Both statements are
machine-checked: `Alignment.optimal_imp_sufficient_iff` in deterministic form and
`Sufficiency.sufficient_iff` with conditional expectations, almost-sure equality
and a measurable readout (every representation that attains `E[X | H]` attains
`E[Y | H]` iff `E[Y | H] = g(E[X | H])` a.s.). The statistical form also says
what a failure means: the objective alone guarantees nothing, and whatever a
particular non-optimal checkpoint keeps has to be measured.

This applies to the loss, target and readout together, not to a model family.
Our foundation readouts are frozen internal states, not trained bottlenecks, so
the theorem is a lens rather than a result about them. It nonetheless predicts
the label-null finding. With support labels, the in-context target is next-year
capitalization/assets and the state is organized around `F = E[target | x]`.
With labels set to zero the target is constant, `F` separates nothing, and the
readout has no reason to preserve any economic distinction. That is what we
observe (+130 → +8). The alternate-target result says the two financial targets
require largely overlapping distinctions.

### 5.3 Marginal targets do not determine dependence

A short counterexample shows why per-firm targets are a weak foundation for a
*covariance* network. Let `S ∈ {0, 1}` be observed and `R` an independent fair
coin; set `Y₁ = R` and `Y₂ = R ⊕ S`. Each marginal is a fair coin for either value
of `S`, so a constant representation forecasts both marginals perfectly. Yet
`Y₁ = Y₂` when `S = 0` and `Y₁ = 1 − Y₂` when `S = 1`: the dependence is entirely
determined by the state the representation discarded.

Every support target in this study is a per-firm marginal (next-year
capitalization/assets or income/assets), while the evaluation scores the
*joint* law of daily returns. Nothing in the target forces the state to preserve
which firms co-move. The gains observed are therefore an empirical regularity,
not something the readouts were asked to deliver. A target that is itself
joint, such as pairwise co-movement or shared exposure to identified shocks,
would align the readout with the evaluation. The calibrated readouts in the
panel (`histories@decoded__X`) take the first step: they decode exposures of the
prior-window residual covariance, a joint target, out of each representation
and build the network from the decoded exposures (`Measurement` gives the
error bound such a readout inherits).

### 5.4 The score already measures lost information

For any two forecast distributions `q₁` and `q₂` of the true law `P`,

```text
E_P[log q₁(Y) − log q₂(Y)] = KL(P ‖ q₂) − KL(P ‖ q₁).
```

The held-out log-likelihood difference between two networks is therefore an
estimate of how much less divergence from the true joint return law one
network's covariance forecast incurs than the other's. When the forecasts are
the optimal ones using `H` and using `Z`, the expected gap is exactly the
conditional mutual information `I(Y; H | Z)` that compression loses. The log score
is strictly proper, so this is the correct currency for "information about
joint returns retained by a network", subject to the Gaussian working model and
to serial dependence in the daily observations.

For bounded decision losses, the lost information also bounds decision regret:
if `0 ≤ ℓ ≤ 1`, the best policy using `Z` loses at most `sqrt(2 I(Y; H | Z))` in
expected loss relative to the best policy using `H` (total-variation bound on
regret, then Pinsker and Jensen; not formalized in `src/lean`). This is the decision-theoretic sense in which
Blackwell sufficiency for a class of portfolio decisions is weaker than full
distributional sufficiency, and why a network can be adequate for minimum
variance portfolios without preserving the whole joint law.

### 5.5 What the pretrained prior is a prior over

TabPFN-style models are trained to approximate the posterior predictive under
a prior of synthetic structural causal models (Hollmann et al., *Nature*, 2025;
Müller et al., 2022). That prior is generic, not economic. Section 3's
label-null result is consistent with this: the prior supplies an inference
procedure, not a financial geometry. The natural extension is a prior built from
economic structure, with synthetic firms generated from production,
accounting and financing relationships, so that in-context inference is
amortized over mechanisms the study cares about. The obvious risk is that the
model then learns the simulator's assumptions; it would need testing on
regimes and firms outside the synthetic distribution.

### 5.6 Invariance must preserve the predictive law

If a representation is forced to treat `h` and `h'` identically while some task
law differs between them by total variation `δ`, any shared prediction is wrong
by at least `δ / 2` on one of them. Invariances are admissible only for
transformations that leave every task law unchanged. Here, overall distance
scale qualifies (it does not change who is near whom, which is why kernels are
calibrated). Random feature corruption, as in denoising or contrastive tabular
pretraining, does not obviously qualify: replacing debt with a value implying
much higher leverage changes the firm's state.

## 6. What the evidence supports

**Supported, as development evidence:** states from pretrained tabular models
contain a common-risk signal that a held-out linear readout recovers better than
from the same inputs, their PCA or autoencoder compressions, or a supervised
network trained on the same labels. For TabPFN the signal depends on the trained
weights: an untrained copy of the architecture recovers much less of it.

**Qualifications that belong in the same sentence:** the recovered share is small
against the target's reliability; the target is a statistical return-based
coordinate, not an identified economic exposure; native distances between the same
states are no better than simple distances once the firm sample is larger; and
nothing shrinks or grows with the support size as the prior mechanism predicts.

**Not supported:** that pretrained models recover economic state, that the
advantage is a small-sample prior effect, that the native geometry is label-free
or stable under support changes, or that gains generalize across regimes.

The defensible contribution is therefore the measurement design itself: a
comparison of financial proximity measurements that holds the information set,
cohort, estimation capacity and network concentration fixed, with label-null,
placebo and alternate-target controls. It sits in the empirical programme the
20 October note describes, applied to tabular foundation models.

## 7. Tests that would close the gap

In order of value for the theoretical claim:

1. **Recovery probes.** Partly done: held-out decoding of reference-factor
   exposures (REPORT §7.4). Still open: an economically identified target, such
   as exposures to declared shocks, and probes against leverage, size,
   profitability, industry and *future* factor exposures, with Fernández and direct
   distances as competitors.
2. **Regime stability.** Report all panel comparisons excluding 2020 and by
   year; treat 2020 as a separate experience rather than a share of firm-days.
3. **Invariance.** Done for the encoder audit (§4 table): no query-cohort
   dependence, material support-draw and label dependence.
4. **Transfer diagnostics.** Estimate how distinguishable the support rows are
   from synthetic pretraining tasks (the `d_HΔH` term of the transfer bound), and
   relate that to where the prior helps.
5. **Joint targets.** Replace the per-firm support target with one that is
   itself about dependence (§5.3), for example pairwise prior-period
   co-movement or shared exposure to identified shocks, and test whether the
   readout's network improves where the per-firm target did not require it.
6. **Mechanism.** Ask whether proximity in the label-conditioned state predicts
   shared exposure to identifiable shocks (rates, credit spreads, commodity
   prices) out of sample. That would connect the network to a mechanism rather
   than to fit alone.

These tests would decide whether the study can claim more than a predictive
improvement. Until then, the theoretical contribution remains the conditional
perturbation result in the LaTeX draft, which links distance error to network
error and, under stated assumptions, to covariance error, and does not assert
that pretraining recovers true economic distance.
