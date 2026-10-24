# Lean

Machine-checked versions of the exact identities and conditional bounds behind the
theoretical spine:

> economic exposure → task-relevant information → recovered exposure distance →
> network → covariance → financial loss.

Each module proves one link *given its stated assumptions*. Nothing here shows that a given
checkpoint satisfies those assumptions, and nothing requires a pretrained model to win.

The results answer four separate questions about a learned measurement. Each needs its own
evidence, and a yes to one says nothing about the next.

1. **Information.** What does the objective make an optimal model keep? A proper score
   recovers its target's conditional law or moment (`Score`), and excess risk is the
   distance to it (`Recovery.excess_risk_condExp`).
2. **Sufficiency.** Is that enough for the economic state? Only if the economic prediction
   is a function of the pretraining prediction (`Alignment`, `Sufficiency`).
3. **Measurement and geometry.** Can the state, and distances between states, be read out
   stably, and are they identified? (`Recovery`, `Measurement`, `Geometry`)
4. **Econometric use.** What does the spatial model do with the distances? (`Kernel`,
   `Network`, `Value`, `Likelihood`, `Stability`)

Limits and research extensions:

- general mixing-process and function-class generalisation rates; `Selection`
  proves finite-family independent-block concentration and a supplied-coupling interface;
- statistical estimation of overlap, economic mismatch and task coverage; `Transfer`
  proves bounded-density transfer, and `TaskCoverage` proves a finite task-span certificate;
- objective-specific routes (contrastive, predictive-latent, diffusion, autoregressive),
  each of which would pair a proper-score statement with `Sufficiency`;
- the PFN posterior derivation and a prior-mismatch term;
- generated-network inference and nuisance-score orthogonality;
- Davis--Kahan eigenspace estimation, hierarchical PAC-Bayes and causal identification.

## Baseline and verification contract

The extension starts from commit `77607494773b0ab268f8d7ce8b91e6f39a077bc5`
(tree `b1828466a8a7ad94b5549625628168d1754154cf`) on a clean checkout.
Lean remains `leanprover/lean4:v4.31.0`; mathlib remains
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Baseline Lean, manuscript and
blueprint declaration builds passed. The implementation uses an isolated
`feat/economic-measurement-theory` worktree and changes no numerical datasets.

`Audit.lean` remains a readable public-theorem inspection aid. The enforced
project-wide checker is now `just proof-audit`: it discovers every production
source independently of umbrella imports, freshly compiles it, and checks private
declarations, proof bodies, discarded examples and transitive dependencies.
Only `propext`, `Classical.choice`, and `Quot.sound` are allowed. Parser-based
policy also rejects proof placeholders and native proof execution. Exact fixture
and trusted-tool exclusions are reported rather than hidden by directory skips.

`ApiStability` is a default Lake target containing complete, frozen type contracts.
`just lean-build` additionally verifies that every manuscript/blueprint tag has a
successfully elaborated contract. It queries the compiled environment extension,
so a commented-out command cannot satisfy coverage. Contracts compare types,
universe arity and correspondence, and explicit/implicit binder metadata; they
do not apply a theorem to a weaker example. They protect interfaces rather than
the semantics of dependency definitions or the empirical economic premises.

The [MathEconLib compatibility trial](compatibility/README.md) retained Lean 4.31.
The 4.35 trial compiled the selected upstream probability modules but exposed a
proved counterexample to an unchanged RMS theorem under the new `eLpNorm`
semantics. No theorem assumption or dependency pin was changed to adopt it.

## 1. Economic target (`Exposure`, `Score.response_sq`)

| Theorem | Statement |
| --- | --- |
| `Exposure.covariance_eq`, `inner_eq_half` | Common covariance is `½(kᵢ + kⱼ − ρᵢⱼ²)`. Distance alone does not order covariance; communality also matters. |
| `Score.response_sq` | `ρᵢⱼ² = (bᵢ − bⱼ)'Ω(bᵢ − bⱼ)` is the second moment of the response difference `(bᵢ − bⱼ)'q`, for any shock law with finite second moments. |
| `Exposure.pricing_error_lipschitz` | `\|⟪aᵢ, g⟫ − ⟪aⱼ, g⟫\| ≤ ρᵢⱼ‖g‖`. If the omitted factors are traded and firms earn no other expected return, close exposures imply close factor-implied expected returns, and `‖g‖ = (γ'Ω⁻¹γ)^½` is their maximum Sharpe ratio. The factor prices `γ` are common to all firms; a firm-specific expected return is not bounded. |

## 2. Task alignment (`Alignment`, `Sufficiency`, `Recovery`, `Measurement`): the central result

| Theorem | Statement |
| --- | --- |
| `Alignment.optimal_imp_sufficient_iff` | Deterministic core: every target-optimal representation is sufficient iff the target separates what the economic state separates. |
| `Alignment.state_optimal_iff`, `constant_target_loses_state` | The state can be target-optimal iff the target needs nothing the state ignores. A constant (label-null) target admits an optimal representation that keeps no state. |
| `Alignment.marginals_free_of_state`, `joint_depends_on_state` | Exact marginal forecasts can discard the state that fixes the joint law. |
| `Sufficiency.condExp_eq_iff` | Statistical form: a representation `σ(Z) ⊆ σ(H)` attains `E[X \| H]` iff `E[X \| H]` is a.s. `σ(Z)`-measurable. |
| `Sufficiency.sufficient_iff` | Every representation attaining `E[X \| H]` also attains `E[Y \| H]` iff `E[Y \| H] = g(E[X \| H])` a.s. for a measurable `g`. Conditional laws follow from indicator targets. |
| `Sufficiency.constant_target_iff` | With an a.s. constant pretraining prediction, the guarantee covers only a.s. constant economic predictions. |
| `Recovery.aggregate_merges` | Limit: the target `a_f + a_o` merges `(1, 0)` and `(0, 1)`, which are `√2` apart. |
| `Recovery.diverse_distinguishes` | Diversity: `a_f ± a_o` together give `‖Ca‖² = 2‖a‖²`, so a margin of `√2`. |
| `Recovery.finrank_le_of_distinguishes`, `scalar_not_distinguishes` | Distinguishing exposures needs at least as many task dimensions as exposure dimensions. One scalar target cannot distinguish exposures of dimension two or more. |
| `Recovery.exists_decoder` | If tasks distinguish exposures (`‖Ca‖ ≥ κ‖a‖`, κ > 0), a linear decoder with left-inverse property and gain `1/κ` exists (project onto the range, then invert). |
| `Recovery.exposure_error` | `κ‖â − a‖ ≤ ‖τ̂ − Ca‖`. |
| `Recovery.exposure_error_mismatch`, `_sq` | With mismatch `τ = Ca + v`: `κ‖â − a‖ ≤ ‖τ̂ − τ‖ + ‖v‖` and `κ²‖â − a‖² ≤ 2(‖τ̂ − τ‖² + ‖v‖²)`. Accuracy cannot remove `v`. |
| `Recovery.mean_exposure_error` | The same bound in mean square under any measure. |
| `Recovery.excess_risk`, `excess_risk_condExp` | Excess squared task risk over `E[Y \| X]` equals `‖f − E[Y \| X]‖²` in `L²`. This is the `ε` the exposure bounds take. |
| `Measurement.measurement_error`, `rms_measurement_error` | Any `K`-Lipschitz readout `g`: `d(g(F̂), s) ≤ K d(F̂, F) + ξ`, and in root mean square `‖d(g(F̂), s)‖₂ ≤ K‖d(F̂, F)‖₂ + ‖ξ‖₂` (Minkowski), with alignment error `ξ = d(g(F), s)`. `ξ` belongs to the pair `(F, g)`: it adds information `F` lacks, `E‖s − E[s | F]‖²`, to readout error `E‖E[s | F] − g(F)‖²` (the L² projection identity; for a real state this is `Recovery.excess_risk_condExp`). |
| `Measurement.decoder_lipschitz` | The linear decoder is `1/κ`-Lipschitz, so `Recovery` is the special case `K = 1/κ`. |
| `Measurement.readout_error_ge`, `aggregate_readout_error` | Lower bound: if a representation merges two histories, every readout misses one state by at least half their distance. Reading `(1, 0)` and `(0, 1)` from their aggregate misses one by at least `√2/2`. |
| `Measurement.mean_sq_distance`, `sq_norm_mean_le` | `E‖D‖² = ‖E D‖² + E‖D − E D‖²` for `D = Aᵢ − Aⱼ`: distances between posterior-mean exposures understate expected distances by the posterior variance of the difference. |
| `Recovery.distance_error` | `\|‖âᵢ − âⱼ‖ − ‖aᵢ − aⱼ‖\| ≤ ‖âᵢ − aᵢ‖ + ‖âⱼ − aⱼ‖`. |
| `Recovery.pairwise_distance_error` | `Σᵢ≠ⱼ (d̂ᵢⱼ − dᵢⱼ)² ≤ 4(N − 1) Σᵢ ‖âᵢ − aᵢ‖²`, with no independence across pairs. |
| `Recovery.readout_invariant` | Distances between read-out exposures are invariant under any reparametrisation of the states, with the matching readout. |

The calibrated measurement bound (`Score.calibrated_measurement_bound`) combines
this projection identity with empirical risk minimization. For a fixed encoder
and context, financial prediction risk is bounded by information error,
readout approximation error, twice a uniform sample-to-population discrepancy,
and fitting slack. The theorem proves the deterministic implication; a
probabilistic rate requires a sampling model and a bound on the discrepancy.

## 3. Information is not geometry (`Geometry`)

| Theorem | Statement |
| --- | --- |
| `Geometry.optimal_equiv`, `sufficient_equiv` | Any bijection of the representation preserves optimality and sufficiency. |
| `Geometry.rescale` | Scaling by `c ≠ 0` preserves sufficiency and multiplies every distance by `\|c\|`. |
| `Geometry.observationally_equivalent` | Task means identify exposures only up to an invertible map: `(C G⁻¹)(G a) = C a`. |
| `Geometry.distances_preserved_iff` | The two descriptions give the same distances for every configuration iff `G` preserves norms. The common covariance fixes the Gram matrix (`Exposure.inner_eq_half`) and so pins distances down up to rotation. |
| `Geometry.chord_injective`, `chord_left_inverse` | The direct baseline `[x, 1]/‖[x, 1]‖` is injective (`x = v₁:ₚ/vₚ₊₁`)... |
| `Geometry.chord_sq_sum`, `chord_dist_sq_le` | ...yet lies on the unit sphere, so every chord distance is at most 2. |

## 4. Kernel, network and likelihood (`Kernel`, `Network`, `Value`, `Likelihood`)

| Theorem | Statement |
| --- | --- |
| `Kernel.expRow_scale` | `(d, h)` and `(cd, ch)` give the same network. |
| `Kernel.normalized_l1_le`, `normalized_l1_le_two` | Weights with ratios in `[1/r, r]` normalise to rows within `ℓ₁` distance `min(2, r² − 1)`, twice the total variation. |
| `Kernel.expRow_l1_le`, `expKernel_linfty_le` | Distance error `δ` gives `‖Ŵ − W‖_∞ ≤ min(2, e^{2δ/h} − 1)`. The bound is uniform in `δ`. |
| `Network.inverse_expansion` | `(I − λW)⁻¹ = I + λW + λ²W²(I − λW)⁻¹`. |
| `Network.rowStochastic_const`, `rowStochastic_inverse_const` | Every row-normalised W has `(I − λW)⁻¹1 = 1/(1 − λ)`, a built-in common component. |
| `Network.uniform_const`, `uniform_sum_zero`, `inverse_on_eigenvector` | The uniform network is a pure common component. |
| `Network.placebo_det`, `placebo_group_mass` | `PWPᵀ` keeps `det(I − λW)` and the weight between size groups. |
| `Value.decomposition` | `⟨W − U, C⟩ = ½Σⱼ(cⱼ − 1)kⱼ − ½Σᵢⱼ(Wᵢⱼ − Uᵢⱼ)ρᵢⱼ²`: hub plus proximity. |
| `Value.placebo_hub` | Within-group placebos keep the hub term when communality is constant within groups. |
| `Likelihood.precision_eq`, `logdet_eq`, `quadratic_term`, `spatial_loss` | For `Σ = A⁻¹DA⁻ᵀ`, `A = I − λW`: expected loss `= Σᵢ log dᵢ − 2 log\|det A\| + Σᵢ mᵢ(λ)/dᵢ`, with filtered second moments `mᵢ(λ) = (AMAᵀ)ᵢᵢ`. |
| `Likelihood.filtered_second_moment` | For `M = Gram(a) + diag(η)` and zero-diagonal W: `mᵢ(λ) = ‖aᵢ − λΣⱼWᵢⱼaⱼ‖² + ηᵢ + λ²ΣⱼWᵢⱼ²ηⱼ`. |
| `Likelihood.filtered_second_moment_expand` | `mᵢ(λ) = (‖aᵢ‖² + ηᵢ) − 2λΣⱼWᵢⱼ⟪aᵢ, aⱼ⟫ + λ²(‖ΣⱼWᵢⱼaⱼ‖² + ΣⱼWᵢⱼ²ηⱼ)`. With equal `dᵢ`, the linear coefficient sums to `−2⟨W, C⟩/d`, the inner product `Value` decomposes; idiosyncratic variance never enters it. |
| `Likelihood.herfindahl_ge`, `herfindahl_uniform` | The noise cost `ΣⱼWᵢⱼ²ηⱼ` is `η` times the row's Herfindahl index, at least `1/m`, with equality for equal weights. |

## 5. Financial consequence (`Stability`)

| Theorem | Statement |
| --- | --- |
| `Stability.inverse_sub`, `norm_inverse_sub_le` | `P − P' = P(X' − X)P'`. |
| `Stability.resolvent_sub_le` | `‖P − P'‖ ≤ \|λ\|M²‖W − W'‖`. |
| `Stability.covariance_sub_le`, `matrix_covariance_sub_le` | `‖Σ(Ŵ) − Σ(W)‖₂ ≤ 2‖V‖\|λ\|M³‖Ŵ − W‖₂` for common `λ, V` (spectral norm). |
| `Stability.quadratic_inverse_sub_le` | `\|u'Σ⁻¹u − u'Σ̃⁻¹u\| ≤ ‖Σ⁻¹‖‖Σ̃⁻¹‖‖Σ − Σ̃‖‖u‖²`. |
| `Stability.portfolio_regret`, `long_only_sq_le` | A minimum-variance choice under covariance error `e` costs at most `2B²e`; `B = 1` for long-only, fully invested portfolios. |

## 6. What the scores measure (`Score`)

| Theorem | Statement |
| --- | --- |
| `Score.integral_quadratic`, `expected_loss` | `E[u'Au] = tr(A E[uu'])`. The expected Gaussian loss is `log det Σ + tr(Σ⁻¹M)`, with no normality assumed. |
| `Score.realized_quadratic` | The realized score depends on the data only through `Σₜuₜuₜ'`. |
| `Score.stein_nonneg`, `loss_sub`, `loss_le` | Loss gap = Stein's loss `tr(Σ⁻¹M) − log det(Σ⁻¹M) − N ≥ 0`: the Gaussian score is proper for the second moment. |
| `Score.crossEntropy_eq`, `kl_nonneg`, `crossEntropy_le` | Cross-entropy = entropy + KL ≥ entropy: the log score is proper. |
| `Score.pretraining_excess` | PFN pretraining loss minus Bayes loss under the task prior is the expected KL to the posterior predictive. |
| `Score.erm_bound` | An `ε`-minimiser of a risk estimate within `g` of the population risk is within `2g + ε` of every candidate. |

## 7. Explicit finite geometry and financial error propagation

All matrix norms in the following ledger are Euclidean operator norms unless a
row-sum or Frobenius norm is named explicitly. `MatrixBounds` defines wrappers so
composition does not depend on a local norm instance. The finite panel contains
`N` firms; a zero-diagonal normalized network requires `N ≥ 2`.

| Compiled declarations | Contract and interpretation |
| --- | --- |
| `MatrixBounds.spectralNorm_le_frobeniusNorm`, `frobeniusNorm_le_sqrt_card_mul_rowSumNorm`, `frobeniusNorm_sq_le_card_mul_spectralNorm_sq` | `‖A‖₂ ≤ ‖A‖F ≤ √N ‖A‖∞`; squared Frobenius norm is at most the number of columns times squared spectral norm. Dimension factors are explicit. |
| `GramDistance.squared_eq_quadratic`, `squared_error`, `distance_error` | An anchored PSD Gram target with entrywise error `εG ≥ 0` has squared-distance error at most `4εG` and distance error at most `2√εG`. Zero distances are allowed; no division by pairwise separation is used. |
| `GramDistance.squared_error_spectral`, `distance_error_spectral`, `sharpGram_distance` | Spectral Gram error `εG` gives the different constants `2εG` and `√(2εG)`. A PSD two-point outer-product example attains the entrywise constants. |
| `GramDistance.uniform_exposure_distance`, `empirical_rms_to_uniform` | Uniform exposure error `e` gives pair-distance error `2e`. An actual-panel RMS certificate `B` gives maximum absolute error at most `√N B`; population RMS needs a separate sampling result. |
| `Kernel.normalized_l1_le_sharp`, `expRow_l1_le_scaled`, `expRow_l1_le_bandwidth`, `expKernel_row_l1_le_scaled` | Ratio-bounded positive weights normalize within `2(r−1)/(r+1)` in row L1. Scaled-distance error `b ≥ 0` gives `s(b)=2(exp b−1)/(exp b+1)`. With distinct bandwidths a valid choice is `b=δ/h_min + D_max |ĥ−h|/h_min²`; this assumes a bandwidth-error certificate, not stability of its estimator. |
| `Stability.matrix_covariance_joint_sub_le`, `matrix_covariance_target_sub_le` | Joint network/coefficient error and innovation error contribute `2VM³‖λ̂Ŵ−λW‖₂ + M²‖D̂−D‖₂`; a separately bounded spatial-model approximation error is added for the true second moment. Both inverse norms and nonsingularity are explicit. |
| `ScoreStability.loss_gap_local`, `loss_gap_le_of_norm_sub`, `abs_logdet_sub_le` | For positive-definite forecast and target, whitened relative error `E` with `‖E‖₂≤r<1` gives score gap at most `‖E‖F²/[2(1−r)]`. A forecast eigenvalue floor `m>e≥0` and total covariance error `e` give `N(e/m)²/[2(1−e/m)]`. A common floor gives global log-determinant continuity. `Score.loss` is twice the ordinary Gaussian negative log score up to constants. |
| `Stability.matrix_portfolio_regret` | The same spectral covariance error `e` implies variance regret at most `2B²e` on a feasible set with Euclidean portfolio norm bounded by `B`. |

## 8. Information, finite transfer and statistical contracts

`Transfer.rms p f` is the norm of `sqrt(p_i) • f_i` in a finite **L2** product;
for nonnegative probability weights its square is `Σ p_i ‖f_i‖²`. The population
interface uses `eLpNorm f 2 P`, which is an extended nonnegative number until its
finiteness is established. Every source and target measure remains visible.

| Compiled declarations | Contract and interpretation |
| --- | --- |
| `TaskInformation.information_quadratic`, `information_increment`, `distinguishes_of_loewner_floor`, `exists_decoder_of_information_floor` | `J=Σ w_t c_t c_tᵀ`, `w_t≥0`; a task-information floor `J ⪰ κ²I` supplies `Recovery.Distinguishes` for the square-root-weighted task operator, and hence the existing decoder when `κ>0`. An appended positive precision increment raises information. |
| `TaskInformation.task_units_invariant` | `CᵀR⁻¹C` is invariant when both task units and noise covariance change by the same invertible map. This does not identify economic coordinates or their metric. |
| `TaskInformation.rank_one_inverse`, `rank_one_inverse_le`, `posterior_precision_update`, `posterior_precision_mono` | Starting from the independently augmented positive precision, prove the full rank-one inverse identity and inverse-precision ordering. These are matrix theorems; Gaussian posterior interpretation is an additional statistical model premise. |
| `Information.nested_projection`, `nested_condExp`, `projection_risk_mono` | With nested closed information subspaces, the decrease in optimal squared error equals the squared difference of projections. The conditional-expectation version holds in vector-valued L2, hence almost everywhere. It makes no finite-learner monotonicity claim. |
| `Recovery.excess_risk_condExp_vector` | Multitask conditional-mean excess squared risk equals squared vector-valued L2 prediction error. |
| `TaskCoverage.covered_signal`, `covered_error`, `predicted_task_error` | A declared economic loading in the finite span of training loadings has error multiplier equal to the Euclidean norm of its explicit coefficient vector. Task count alone supplies no coverage certificate. |
| `Transfer.change_of_weights`, `task_transfer`, `source_target_recovery` | Pointwise `q_i≤ωp_i` transports task RMS with `√ω`; task-mean drift and economic mismatch enter separately, divided by `κ>0` in exposure recovery. No sampling or independence assertion is implicit. |
| `Transfer.fitted_readout_error` | Uniform task error `ετ`, mismatch `ν`, predicted-statistic bound `Bτ`, and a fitted-map certificate give exposure error `(ετ+ν)/κ + εL Bτ`. The fitted and ideal maps act on the same task-statistic space. The actual clipped, standardized hidden-state ridge procedure needs its own general-readout certificate. |
| `Transfer.measure_change`, `density_change`, `rnDeriv_change`, `measure_source_target_recovery` | General-measure and Radon--Nikodym versions under bounded density, with target-law measurability for Minkowski. Latent realized states require irreducible uncertainty or a conditional-mean target. Learned functions must satisfy these contracts conditional on their training/support information. |
| `Selection.bounded_blocks`, `finite_family`, `coupled_finite_family` | Fixed bounded losses on `m≥1` independent blocks give finite-family tail `2K exp(−2mε²)`. A coupled independent copy with matching block marginals adds the probability of **any** coupling mismatch once. Blocks need not be identically distributed; the center is average marginal block risk. |
| `Selection.risk_discrepancy`, `source_excess`, `task_rms_of_excess` | Add a discrepancy if the block-mixture law differs from source or future-period risk. ERM then yields approximation `+2g+` optimization error; squared-risk excess becomes RMS only after taking a square root. Bounded task-loss normalization must be restored. |
| `Selection.panel_markov`, `random_panel` | Individual second-moment bounds `E e_i²≤B²` imply `P(∃i:e_i>B√(N/α))≤α`, with the `B=0` case included. Interfirm independence is unnecessary. This is a sampling/moment contract, not a bound on an arbitrary fixed panel. |
| `Transfer.small_mass_spike` | A finite probability law with mass `r²` at a unit-error point and zero error elsewhere has population RMS `r<1`; that specified point still has error one. Population RMS alone cannot supply a uniform fixed-panel error bound. |

The finite candidate class is fixed before evaluation, or the argument is
conditional on separate fitting data. Counting only realized models after
adaptive fitting does not meet the contract. Gaussian log scores are unbounded
and are not covered by the bounded-loss concentration theorem. Existing inspected
evaluation years remain development evidence.

`StatisticalFinancial.failure_probability` composes the moment/panel event with
`EndToEnd.measurement_to_finance`, rather than assuming its financial conclusion.
`failure_probability_with_learning` uses moments under **unnormalized**
`μ.restrict good` and adds the probability of the complement once. Fixed finite
input marginals and `Transfer.source_target_recovery` supply the moments in
`finite_transfer_failure_probability`. Interfirm independence is unnecessary;
fixed predictors/decoders, sampling marginals, spatial controls and the local
score condition remain explicit. These are outer-measure statements unless the
events are measurable. `EndToEnd.full_score_of_certificate` separately connects
residual covariance error to full forecasts with a shared conventional factor
component and a floor on the full forecast.

## 9. Comparative statics and deeper finite interfaces

| Compiled declarations | Contract and interpretation |
| --- | --- |
| `Bandwidth.hasDerivAt_expRow`, `hasDerivAt_meanDistance`, `hasDerivAt_entropy`, `herfindahl_antitoneOn`, `effectiveNeighbors_monotoneOn` | At fixed distances and positive bandwidth, mean distance and entropy rise, Herfindahl concentration falls, and effective neighbor count rises. Equal-distance/tied rows are permitted; these weak monotonicity theorems do not establish a unique matching bandwidth. |
| `Bandwidth.constant_distance_effectiveNeighbors`, `expRow_tendsto_atTop`, `expRow_tendsto_zero`, `matched_effective_not_concentration` | Constant-distance rows are uniform; infinite bandwidth tends to uniform weights and vanishing positive bandwidth tends to uniform weights over all nearest ties. The two explicit Herfindahl profiles `(1/2,1/2)` and `(3/4,3/8)` have equal mean effective-neighbor counts but different mean concentration. |
| `ReversibleNetwork.detailed_balance`, `weighted_resolvent_bound`, `normalize_resolvent_l2_bound`, `exponential_resolvent_l2_bound` | Symmetric nonnegative kernels have degree-stationary normalized rows. Positive degrees and `|λ|<1` give weighted contraction/invertibility and the Euclidean certificate `√(smax/smin)/(1−|λ|)`. Bounded symmetric exponential distances specialize it to `exp(Dmax/(2h))/(1−|λ|)`. |
| `ComparativeStatics.swap_covariance_common`, `swap_covariance_spread`, `swap_covariance_not_ge_identity` | Two-firm exchange network: common and spread eigenvalues are `(1−λ)⁻²` and `(1+λ)⁻²`; covariance is not generally increasing in Loewner order. |
| `Decision.garbling_risk`, `approximate_sufficiency` | Finite states, signals and actions: garbling cannot improve optimal risk. A reverse simulator with prior-weighted TV error at most `ε` preserves optimal risk within `ε` for losses in `[0,1]`. TV is half L1; unrestricted quadratic or Gaussian losses are outside this result. |
| `Dynamics.gramian_succ`, `gramian_mono`, `observation_gram`, `observable_decoder`, `two_horizons` | Known noiseless finite linear dynamics append PSD observability information; a positive stacked-map margin reuses `Recovery.exists_decoder`. A coordinate-swap example reveals an initially hidden direction. Process noise, unknown maps and causal interpretation remain separate obligations. |
| `GeneratedTarget.normal_equation_error`, `factor_gram_error`, `cross_moment_error`, `generated_readout_error`, `exposure_gram_error` | Deterministic generated-target errors split factor Gram and cross-moment perturbations, inverse conditioning, readout error and target uncertainty. No covariance sampling rate or structural common-component identification is inferred. |
| `ReadoutStability.objective_minimizer_unique`, `operator_objective_gap`, `operator_objective_minimizer_unique`, `vector_prediction_replacement_le` | The scalar and Hilbert-valued normal-equation ridge solutions uniquely minimize their regularized quadratic objectives; the vector-target prediction bound has no output dimension factor. With bounded fixed features/targets, `N≥1` support observations and regularization `μ>0`, one replaced observation changes coefficients by at most `2RY(1+R²/μ)/(Nμ)`, and bounded-feature predictions by at most an additional factor `R`. Context-induced feature changes, scaling, clipping and regularization selection require extra terms. |
| `Geometry.nonlinear_codes_sufficient`, `nonlinear_codes_distort` | The finite recoding `x↦x²` retains states `0,1,2` but sends two equal adjacent intervals to lengths `1` and `3`. Conditional/invertible recovery alone does not identify Euclidean geometry. |

## 10. The compiled composition

`EndToEnd.covariance_from_scaled` accepts a scaled-distance certificate from
either `exposure_scaled` or `gram_scaled`. For `s(b)=2(exp b−1)/(exp b+1)` it
uses the explicit error budget

```text
EΣ = 2 V M³ (|λ| √N s(b) + ελ BW) + M² εD + ρspatial.
```

`EndToEnd.measurement_to_finance` proves the uniform exposure-error route with
`b=2e/h`: total spectral covariance error is at most `EΣ`, and a forecast
eigenvalue floor `m>EΣ` gives score regret at most
`N(EΣ/m)²/[2(1−EΣ/m)]`. `EndToEnd.tasks_to_finance` supplies the exposure
certificate using task prediction, economic mismatch and fitted-readout error.
`EndToEnd.empirical_rms_scaled` retains the extra `√N` factor when the input is
an actual-panel empirical RMS bound. The alternative Gram route does not need
a task decoder.

The financial hypotheses explicitly include nonsingular spatial operators,
bounded resolvents, innovation and coefficient error certificates,
positive-definite forecast and target, and spatial-model approximation. The
statistical modules supply conditional learning and sampling events separately;
their bounds do not certify an arbitrary fixed financial cohort automatically.
`Stability.matrix_portfolio_regret` consumes the same total covariance error.

Principal blueprint traceability (all names have prefix `FreeFoundations.`;
each source is under `src/lean/FreeFoundations/`):

| TeX label | Exact conditional statement | Lean declaration | File | Key conditions | Status |
| --- | --- | --- | --- | --- | --- |
| `thm:gram-distance` | Entrywise Gram error gives distance error `2√εG` | `GramDistance.distance_error` | `GramDistance.lean` | Both Gram matrices PSD; `εG≥0` | Proved, compiled, integrated |
| `thm:task-information` | Information floor supplies recovery margin | `TaskInformation.distinguishes_of_loewner_floor` | `TaskInformation.lean` | Finite Euclidean spaces; nonnegative precisions and margin | Proved, compiled, integrated |
| `thm:transfer-recovery` | Source error, target drift and mismatch bound target exposure RMS | `Transfer.measure_source_target_recovery` | `Transfer.lean` | Measure domination, positive decoder margin, measurability | Proved, compiled, integrated |
| `thm:finite-block-concentration` | Uniform finite-family tail plus total coupling mismatch | `Selection.coupled_finite_family` | `Selection.lean` | Fixed bounded losses, independent copy, matching marginals | Proved, compiled, integrated |
| `thm:random-panel` | Individual second moments give a random-panel maximum event | `Selection.random_panel` | `Selection.lean` | Integrable squared errors, moment contract, `α>0` | Proved, compiled, integrated |
| `thm:score-local-stability` | Spectral covariance error gives local quadratic score regret | `ScoreStability.loss_gap_le_of_norm_sub` | `ScoreStability.lean` | Positive definiteness, eigenvalue floor `m>e` | Proved, compiled, integrated |
| `thm:end-to-end-tasks` | Task/readout certificates imply covariance and score bounds | `EndToEnd.tasks_to_finance` | `EndToEnd.lean` | Finite uniform panel certificate and all financial conditions above | Proved, compiled, integrated |

Every row above is proved and compiled. The ledger records conditional statements,
not verification of their economic premises for a checkpoint or financial panel.

Principal manuscript labels use the same compiled declarations:

| Manuscript label | Declaration | Additional review condition |
| --- | --- | --- |
| `prop:measurement-stability` | `EndToEnd.measurement_to_finance`, `tasks_to_finance` | Uniform finite-panel error, matrix floors, resolvent bounds, and model approximation |
| `prop:stability` | `EndToEnd.covariance_from_scaled` | Scaled distances and explicit bandwidth certificate |
| `eq:task-recovery` | `Transfer.fitted_readout_error` | Same task-statistic space and nonnegative fitted-map error |
| `eq:block-concentration` | `Selection.finite_family` | Predetermined candidates, nonempty blocks, bounded loss, nonnegative threshold |
| `thm:statistical-finance` (blueprint) | `StatisticalFinancial.finite_transfer_failure_probability` | Fixed predictor/decoder, declared finite input marginals, structural controls and local domain |

## 11. Finite probability compatibility and stochastic order

All four modules use namespace `FreeFoundations.FiniteProbability`. The facade
uses the pinned mathlib's real simplex and PMF APIs, following the reviewed
MathEconLib finite-law conventions with source attribution and a scoped
[Apache license](FreeFoundations/FiniteProbability.LICENSE). There is no new
MathEconLib dependency. Raw weighted and restricted-measure APIs remain intact.

| Blueprint/manuscript label | Compiled interface | Assumptions and meaning |
| --- | --- | --- |
| `thm:finite-measure-bridge`, `app:finite-probability` | `integral_eq_expect`, `rms_sq_eq_integral`, `eLpNorm_eq_ofReal_rms` | Finite simplex law, measurable singletons; complete normed real target for vector integration |
| `thm:finite-mixtures` | `expect_finMixture`, `expect_conditionalOn`, `domination_iff` | Normalized mixture probabilities; positive conditioning mass; nonnegative overlap factor |
| `thm:finite-typed-simulation` | `approximate_decoder`, `approximate_sufficiency`, `approximate_decoder_uniform` | Probability prior; finite signals/actions; bounded loss in `[0,L]`, including `L=0`; half-L1 TV |
| `thm:finite-typed-simulation` | `marginalRisk_eq_mixture`, `source_target_recovery`, `transfer_failure_probability` | Exact finite marginal/pushforward laws; existing alignment, overlap, sampling and financial controls |
| `thm:bandwidth-stochastic-order`, `app:comparatives` | `Bandwidth.likelihoodRatio_cross_le`, `monotone_cost_expectation`, `upperTail_monotoneOn`, `closedUpperTail_monotoneOn`, `cdf_antitoneOn` | Fixed nonempty support and real costs, positive ordered bandwidths; cost ties retained |
| `thm:bandwidth-stochastic-order` | `exponentialLaw_expect_monotone` | Typed finite law wrapper around the existing exponential row |

Each row is proved, compiled and integrated. Task precisions are not normalized
probabilities without a retained precision budget. Finite candidate families do
not make observations finite. A reverse decoder alone supplies only the upper
risk gap; a forward garbling is needed for its nonnegative lower bound.

The bandwidth theorem orders every increasing observable and threshold tail of
the fixed cost distribution. It does not order portfolio loss, and it excludes
the totalized expression at bandwidth zero. Fixed-feature and economic
identification qualifications from the preceding sections continue to apply.

## 12. Verification tooling

| Command | Enforced check |
| --- | --- |
| `just lean-build` | Core library, `ApiStability`, and compiled contract coverage |
| `just proof-audit` | Fresh source discovery/build and declaration/example integrity |
| `just proof-audit-test` | Positive and negative integrity/API fixtures using stdlib unittest |

The audit writes [`.lake/build/proof-integrity.json`](.lake/build/proof-integrity.json).
It records the revision and dirty state, toolchain, manifest and actual dependency
revisions, source/checker hashes, exclusions, coverage, and each declaration's
axioms. Files changed, added or removed during a run invalidate the report.
The two explicitly trusted implementation files are `ApiStability/Check.lean`
and `tools/CheckProofIntegrity.lean`; both are compiled. The expected contracts
and ordinary audit file are fully audited. Production imports of excluded
negative fixtures are rejected.

The test suite checks orphan sources, private and opaque placeholders, repeated
anonymous examples, disabled warnings, interpolated proof terms, imported axioms,
native reflection and syntax quotations, source drift, and exact exclusions.
Contract tests reject changed hypotheses, constants, norms, universes and binder
visibility while accepting harmless renaming and definitional aliases. Changes
to these tools rerun the regression hook; Lean changes rerun the integrity hook.

## Blueprint

[`blueprint/src/content.tex`](blueprint/src/content.tex) restates the principal public
contracts in ordinary notation, in the [leanblueprint](https://github.com/PatrickMassot/leanblueprint)
format: each statement carries `\lean{...}` with the declaration it is checked against,
`\leanok` once the proof has no `sorry`, and `\uses{...}` for the results it builds on.
The [manuscript](../latex/main.tex) maintains a curated mathematical appendix
and its own `\lean{...}` tags. Both sources are checked against the same compiled
library; the manuscript does not include the full blueprint source.

| Command | Output |
| --- | --- |
| `just blueprint-web` | HTML blueprint with the dependency graph in `blueprint/web/` (open `dep_graph_document.html`) |
| `just blueprint-pdf` | Printable blueprint in `blueprint/print/print.pdf` |
| `just blueprint-check` | Fails if any `\lean{...}` name in the blueprint or the manuscript is not a compiled declaration |
| `just blueprint-serve` | Serves `blueprint/web/` on port 8000 |

The Lean project is `src/lean`, not the repository root, so these recipes run the
`leanblueprint` CLI's steps (`plastex`, `lake exe checkdecls`) directly. They need the
devenv shell, which provides graphviz for the graph.

Run `just lean-build` from the repository root. A fresh checkout first needs the prebuilt
Mathlib files: `cd src/lean && lake exe cache get` (about 6–7 GB).

## Verification outcome (24 October 2026)

- `just lean-build`: passed with the pinned dependencies (3169 build jobs),
  including all 241 manuscript/blueprint type contracts and compiled coverage.
- `just proof-audit`: 38 production sources freshly compiled, including 36
  strictly audited files and two explicitly trusted checker implementations;
  785 declarations, including 12 private declarations, use no unsupported axioms.
  The 18 exact fixture exclusions are separately tested.
- `just proof-audit-test`: all 26 integrity and API regression tests passed.
- `just blueprint-check`, manuscript format/lint and `just latex-build`: passed.
  The 41-page PDF has no unresolved references or overflowing equations/tables;
  the finite-law, bandwidth, decision, traceability and bibliography pages were inspected.
- Main text: 3897 words including headings/captions and excluding title/abstract;
  abstract: 199 words, under the documented TeXcount convention.
- Repository language, Python test/type/boundary/dead-code, DVC and semflow checks
  passed. The complete gate still reports two existing SEC URLs returning HTTP 403.
  The unchanged baseline `src/python/uv.lock` also fails Tombi's read-only
  formatting check; the broad gate skips that formatter to preserve the lockfile.
  Neither issue changes the Lean or manuscript build result.

The isolated checkout uses saved research artifacts without rerunning empirical
estimation. No data, dependency pins or numerical results are part of this change.
