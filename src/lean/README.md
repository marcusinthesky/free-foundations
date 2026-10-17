# Lean

Machine-checked versions of the exact identities and conditional bounds behind the
theoretical spine:

> economic exposure → task-relevant information → recovered exposure distance →
> network → covariance → financial loss.

Each module proves one link *given its stated assumptions*. Nothing here shows that a given
checkpoint satisfies those assumptions, and nothing requires a pretrained model to win.

Left on paper:

- the dependent-data generalisation bounds (mixing, Rademacher complexity);
- transfer and task-diversity rates;
- the log-determinant half of the loss-Lipschitz bound, which needs eigenvalue
  perturbation;
- generated-network inference.

## 1. Economic target (`Exposure`, `Score.response_sq`)

| Theorem | Statement |
| --- | --- |
| `Exposure.covariance_eq`, `inner_eq_half` | Common covariance is `½(kᵢ + kⱼ − ρᵢⱼ²)`. Distance alone does not order covariance; communality also matters. |
| `Score.response_sq` | `ρᵢⱼ² = (bᵢ − bⱼ)'Ω(bᵢ − bⱼ)` is the second moment of the response difference `(bᵢ − bⱼ)'q`, for any shock law with finite second moments. |
| `Exposure.pricing_error_lipschitz` | `\|αᵢ − αⱼ\| ≤ ρᵢⱼ · (γ'Ω⁻¹γ)^½`. Close exposures cannot carry very different prices of risk; the converse fails. |

## 2. Task alignment (`Alignment`, `Recovery`): the central result

| Theorem | Statement |
| --- | --- |
| `Alignment.optimal_imp_sufficient_iff` | Every target-optimal representation is sufficient iff the target separates what the economic state separates. |
| `Alignment.state_optimal_iff`, `constant_target_loses_state` | The state can be target-optimal iff the target needs nothing the state ignores. A constant (label-null) target admits an optimal representation that keeps no state. |
| `Alignment.marginals_free_of_state`, `joint_depends_on_state` | Exact marginal forecasts can discard the state that fixes the joint law. |
| `Recovery.aggregate_merges` | Limit: the target `a_f + a_o` merges `(1, 0)` and `(0, 1)`, which are `√2` apart. |
| `Recovery.diverse_distinguishes` | Diversity: `a_f ± a_o` together give `‖Ca‖² = 2‖a‖²`, so a margin of `√2`. |
| `Recovery.exists_decoder` | If tasks distinguish exposures (`‖Ca‖ ≥ κ‖a‖`, κ > 0), a linear decoder with left-inverse property and gain `1/κ` exists (project onto the range, then invert). |
| `Recovery.exposure_error` | `κ‖â − a‖ ≤ ‖τ̂ − Ca‖`. |
| `Recovery.exposure_error_mismatch`, `_sq` | With mismatch `τ = Ca + v`: `κ‖â − a‖ ≤ ‖τ̂ − τ‖ + ‖v‖` and `κ²‖â − a‖² ≤ 2(‖τ̂ − τ‖² + ‖v‖²)`. Accuracy cannot remove `v`. |
| `Recovery.mean_exposure_error` | The same bound in mean square under any measure. |
| `Recovery.excess_risk`, `excess_risk_condExp` | Excess squared task risk over `E[Y \| X]` equals `‖f − E[Y \| X]‖²` in `L²`. This is the `ε` the exposure bounds take. |
| `Recovery.distance_error` | `\|‖âᵢ − âⱼ‖ − ‖aᵢ − aⱼ‖\| ≤ ‖âᵢ − aᵢ‖ + ‖âⱼ − aⱼ‖`. |
| `Recovery.pairwise_distance_error` | `Σᵢ≠ⱼ (d̂ᵢⱼ − dᵢⱼ)² ≤ 4(N − 1) Σᵢ ‖âᵢ − aᵢ‖²`, with no independence across pairs. |
| `Recovery.readout_invariant` | Distances between read-out exposures are invariant under any reparametrisation of the states, with the matching readout. |

## 3. Information is not geometry (`Geometry`)

| Theorem | Statement |
| --- | --- |
| `Geometry.optimal_equiv`, `sufficient_equiv` | Any bijection of the representation preserves optimality and sufficiency. |
| `Geometry.rescale` | Scaling by `c ≠ 0` preserves sufficiency and multiplies every distance by `\|c\|`. |
| `Geometry.chord_injective`, `chord_left_inverse` | The direct baseline `[x, 1]/‖[x, 1]‖` is injective (`x = v₁:ₚ/vₚ₊₁`)... |
| `Geometry.chord_sq_sum`, `chord_dist_sq_le` | ...yet lies on the unit sphere, so every chord distance is at most 2. |

## 4. Kernel and network (`Kernel`, `Network`, `Value`)

| Theorem | Statement |
| --- | --- |
| `Kernel.expRow_scale` | `(d, h)` and `(cd, ch)` give the same network. |
| `Kernel.normalized_tv_le`, `normalized_tv_le_two` | Weights with ratios in `[1/r, r]` normalise to rows within total variation `min(2, r² − 1)`. |
| `Kernel.expRow_tv_le`, `expKernel_linfty_le` | Distance error `δ` gives `‖Ŵ − W‖_∞ ≤ min(2, e^{2δ/h} − 1)`. The bound is uniform in `δ`. |
| `Network.inverse_expansion` | `(I − λW)⁻¹ = I + λW + λ²W²(I − λW)⁻¹`. |
| `Network.rowStochastic_const`, `rowStochastic_inverse_const` | Every row-normalised W has `(I − λW)⁻¹1 = 1/(1 − λ)`, a built-in common component. |
| `Network.uniform_const`, `uniform_sum_zero`, `inverse_on_eigenvector` | The uniform network is a pure common component. |
| `Network.placebo_det`, `placebo_group_mass` | `PWPᵀ` keeps `det(I − λW)` and the weight between size groups. |
| `Value.decomposition` | `⟨W − U, C⟩ = ½Σⱼ(cⱼ − 1)kⱼ − ½Σᵢⱼ(Wᵢⱼ − Uᵢⱼ)ρᵢⱼ²`: hub plus proximity. |
| `Value.placebo_hub` | Within-group placebos keep the hub term when communality is constant within groups. |

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

Run `just lean-build` from the repository root. A fresh checkout first needs the prebuilt
Mathlib files: `cd src/lean && lake exe cache get` (about 6–7 GB).
