# Lean

Machine-checked versions of the exact identities behind [ANALYSIS.md](../../ANALYSIS.md).
Approximations and statistical arguments (generalization and regret bounds, local KL,
the inverse-Wishart reading) stay on paper.

| Theorem | Statement | Where |
| --- | --- | --- |
| `Exposure.covariance_eq` | Common covariance is `½(κᵢ + κⱼ − ρᵢⱼ²)` for symmetric `Ω` | Proposed spine (LaTeX §2 model) |
| `Exposure.inner_eq_half` | The same identity in whitened coordinates | Proposed spine (LaTeX §2 model) |
| `Exposure.pricing_error_lipschitz` | `\|αᵢ − αⱼ\| ≤ ρᵢⱼ · (γ'Ω⁻¹γ)^½` | Proposed spine (LaTeX §2 model) |
| `Alignment.optimal_imp_sufficient_iff` | Every target-optimal representation is sufficient iff the target separates what the state separates | §5.2 |
| `Alignment.state_optimal_iff` | The minimal state can be target-optimal iff the target needs nothing the state ignores | §5.2 |
| `Alignment.constant_target_loses_state` | A constant (label-null) target admits an optimal representation that keeps no state | §5.2 |
| `Alignment.marginals_free_of_state`, `joint_depends_on_state` | Marginals that ignore the state, joint law that does not | §5.3 |
| `Network.inverse_expansion` | `(I − λW)⁻¹ = I + λW + λ²W²(I − λW)⁻¹` | Proposed spine (LaTeX §2 model) |
| `Network.inverse_on_eigenvector`, `uniform_const`, `uniform_sum_zero` | The uniform network keeps the cross-sectional mean and scales every zero-sum direction by `−1/(N − 1)`, so it is a pure common component | Proposed spine (LaTeX §2 model) |
| `Network.placebo_det`, `placebo_group_mass` | `PWPᵀ` keeps `det(I − λW)` and the weight between size groups | §4 (placebos) |

Run `just lean-build` from the repository root. A fresh checkout first needs the prebuilt
Mathlib files: `cd src/lean && lake exe cache get` (about 6–7 GB).
