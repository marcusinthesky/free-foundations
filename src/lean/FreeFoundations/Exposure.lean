import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.LinearAlgebra.Matrix.DotProduct

/-!
# Exposure identities

Residual returns `uᵢ = b(Sᵢ)'q + ηᵢ` with `Var q = Ω` and `E q = γ`. The common
covariance is `Kᵢⱼ = bᵢ'Ω bⱼ`, the common variance `κᵢ = Kᵢᵢ`, and the exposure
distance `ρᵢⱼ² = (bᵢ − bⱼ)'Ω(bᵢ − bⱼ)` (ANALYSIS.md, the exposure-kernel spine).
-/

namespace FreeFoundations.Exposure

open Matrix

variable {k : Type*} [Fintype k]

/-- The quadratic form `x'Ω y`. -/
def form (Ω : Matrix k k ℝ) (x y : k → ℝ) : ℝ := x ⬝ᵥ (Ω *ᵥ y)

/-- **Second moment.** For symmetric `Ω`, the covariance of two firms' common components
is half their common variances minus half their squared exposure distance. -/
theorem covariance_eq (Ω : Matrix k k ℝ) (hΩ : Ωᵀ = Ω) (bᵢ bⱼ : k → ℝ) :
    form Ω bᵢ bⱼ =
      (form Ω bᵢ bᵢ + form Ω bⱼ bⱼ - form Ω (bᵢ - bⱼ) (bᵢ - bⱼ)) / 2 := by
  have hsymm : form Ω bⱼ bᵢ = form Ω bᵢ bⱼ := by
    unfold form
    rw [dotProduct_mulVec, ← mulVec_transpose, hΩ, dotProduct_comm]
  have hexpand : form Ω (bᵢ - bⱼ) (bᵢ - bⱼ) =
      form Ω bᵢ bᵢ - form Ω bᵢ bⱼ - form Ω bⱼ bᵢ + form Ω bⱼ bⱼ := by
    unfold form
    simp only [mulVec_sub, sub_dotProduct, dotProduct_sub]
    ring
  rw [hexpand, hsymm]
  ring

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- **First moment.** In whitened coordinates `aᵢ = Ω^{1/2}bᵢ` and `g = Ω^{-1/2}γ`, pricing
errors are `αᵢ = ⟪aᵢ, g⟫`. Their difference is at most the exposure distance times
`‖g‖ = (γ'Ω⁻¹γ)^{1/2}`, the maximum Sharpe ratio of the omitted factors. -/
theorem pricing_error_lipschitz (aᵢ aⱼ g : E) :
    |inner ℝ aᵢ g - inner ℝ aⱼ g| ≤ ‖aᵢ - aⱼ‖ * ‖g‖ := by
  rw [← inner_sub_left]
  exact abs_real_inner_le_norm _ _

/-- The second-moment identity in whitened coordinates: closer exposures mean larger
covariance once both common variances are held fixed. -/
theorem inner_eq_half (aᵢ aⱼ : E) :
    inner ℝ aᵢ aⱼ = (‖aᵢ‖ ^ 2 + ‖aⱼ‖ ^ 2 - ‖aᵢ - aⱼ‖ ^ 2) / 2 := by
  rw [norm_sub_sq_real]
  ring

end FreeFoundations.Exposure
