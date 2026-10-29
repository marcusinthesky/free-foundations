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

Left on paper:

- the dependent-data generalisation bounds (mixing, Rademacher complexity);
- transfer and task-diversity rates;
- objective-specific routes (contrastive, predictive-latent, diffusion, autoregressive),
  each of which would pair a proper-score statement with `Sufficiency`;
- the PFN posterior derivation and a prior-mismatch term;
- the log-determinant half of the loss-Lipschitz bound, which needs eigenvalue
  perturbation;
- generated-network inference.

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

## 7. State classes, proxy error and the composed bound

The following modules make the economic target and the limits of its recovery explicit.
They do not establish the assumptions for the empirical PCA/OLS exposure labels or any
pretrained checkpoint.

| Module | Results and assumptions |
| --- | --- |
| `RiskState` | For a declared linear risk-scaling map `L` and structural exposure map `b`, distance is `‖L(b(s)) − L(b(t))‖`. Zero distance identifies a kernel class, and identifies the entire state only when `L ∘ b` is injective. Risk classes embed injectively into the exposure space. Equal common exposures still leave idiosyncratic variances unspecified. |
| `Proxy` | Triangle, squared-error, finite-panel and L² bounds separate prediction of a historical proxy from proxy-to-latent error. Under an explicit zero integrated inner product between prediction residual and proxy noise, proxy risk equals latent risk plus noise energy. Predictor rankings agree only when this premise holds for both predictors with common noise. |
| `Recovery` | Hilbert-valued conditional-expectation identities split fitted risk into uncertainty after history, information lost by the representation, and readout error. Nested measurable information sets give an exact Bayes-risk ordering, not an ordering of fitted ridge regressions. |
| `Identifiability` | Under a common observation coupling, one of two expected state-estimation risks is at least one quarter of the expected squared separation between targets. Square integrability is explicit. Reparameterization is an impossibility application only when both worlds remain admissible; invariant economic targets can remain recoverable. |
| `Pipeline` | Uniform exposure error propagates to the spatial covariance spectral norm through the exponential network. Named row-sum and spectral norms make the `√N` norm conversion explicit. Bandwidth, spatial coefficient and positive diagonal innovation covariance are common; both inverse spectral norms must be bounded. |

`Pipeline.exposure_covariance_error` proves, for `N ≥ 2`, `h > 0`, and uniform
exposure error at most `r`,

```text
‖Σ̂ − Σ*‖₂ ≤ 2‖D‖₂ |λ| M³ √N min(2, exp(4r/h) − 1).
```

`proxy_covariance_error` substitutes the sum of uniform prediction-to-proxy and
proxy-to-latent errors. `covariance_error_of_sum_sq` uses the realized panel's
summed squared exposure errors. Its conversion from a panel mean squared error
is `r = √(N × MSE)`; a population mean risk is not a simultaneous panel bound.
The theorem neither controls fitted-parameter changes nor establishes a score improvement.

Boundary examples check singular scaling, distinct total variances under equal common
exposures, perfect proxy prediction with latent error, the sharp quarter-risk constant,
and zero exposure error or zero spatial coefficient.

## Axiom audit

Run `just lean-audit` from the repository root, or `lake env lean Audit.lean` after
building in `src/lean`. The audit selects declarations by their originating module,
including unused private helpers and declarations outside the `FreeFoundations` namespace.
It rejects project axioms and transitive dependencies other than `propext`,
`Classical.choice`, and `Quot.sound`; in particular, `sorryAx` fails. The audit does not
replace reviewing theorem statements or verifying their economic assumptions.

## Blueprint

[`blueprint/src/content.tex`](blueprint/src/content.tex) restates every declaration in
ordinary notation, in the [leanblueprint](https://github.com/PatrickMassot/leanblueprint)
format: each statement carries `\lean{...}` with the declaration it is checked against,
`\leanok` once the proof has no `sorry`, and `\uses{...}` for the results it builds on.
The [manuscript](../latex/main.tex) has its own appendix with selected results and
`\lean{...}` tags. The blueprint documents the larger library, including results beyond
the manuscript's current claims. Declaration checks establish that referenced names exist;
matching the prose, assumptions and formal statements remains a review task.

| Command | Output |
| --- | --- |
| `just lean-audit` | Builds the library and checks transitive axioms of all project declarations |
| `just blueprint-web` | HTML blueprint with the dependency graph in `blueprint/web/` (open `dep_graph_document.html`) |
| `just blueprint-pdf` | Printable blueprint in `blueprint/print/print.pdf` |
| `just blueprint-check` | Fails if any `\lean{...}` name in the blueprint or the manuscript is not a compiled declaration |
| `just blueprint-serve` | Serves `blueprint/web/` on port 8000 |

The Lean project is `src/lean`, not the repository root, so these recipes run the
`leanblueprint` CLI's steps (`plastex`, `lake exe checkdecls`) directly. They need the
devenv shell, which provides graphviz for the graph.

Run `just lean-build` from the repository root. A fresh checkout first needs the prebuilt
Mathlib files: `cd src/lean && lake exe cache get` (about 6–7 GB).
