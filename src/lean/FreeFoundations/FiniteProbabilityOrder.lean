import FreeFoundations.FiniteProbability
import FreeFoundations.Bandwidth

/-! Typed finite stochastic-order interfaces for the fixed-cost bandwidth results. -/

noncomputable section

namespace FreeFoundations.FiniteProbability

open Finset

variable {X : Type*} [Fintype X]

/-- Pairwise cross-product concordance orders expectations of typed finite laws. -/
theorem expect_le_of_cross (p q : FinDist X) (f : X → ℝ)
    (hcross : ∀ i j, 0 ≤ (q i * p j - p i * q j) * (f i - f j)) :
    expect p f ≤ expect q f :=
  Bandwidth.sum_expectation_le_of_cross univ (p : X → ℝ) (q : X → ℝ) f
    (sum_one p) (sum_one q) (fun i _ j _ => hcross i j)

variable [Nonempty X]

/-- The normalized exponential row, packaged as a finite probability law. -/
def exponentialLaw (cost : X → ℝ) (h : ℝ) : FinDist X :=
  ⟨Kernel.expRow univ cost h,
    fun i => (Kernel.expRow_pos univ univ_nonempty cost h i).le,
    Kernel.expRow_sum univ univ_nonempty cost h⟩

@[simp] theorem exponentialLaw_apply (cost : X → ℝ) (h : ℝ) (i : X) :
    exponentialLaw cost h i = Kernel.expRow univ cost h i := rfl

/-- Every monotone observable of fixed cost increases weakly with positive bandwidth. -/
theorem exponentialLaw_expect_monotone (cost : X → ℝ) (φ : ℝ → ℝ) (hφ : Monotone φ) :
    MonotoneOn (fun h => expect (exponentialLaw cost h) (fun i => φ (cost i))) (Set.Ioi 0) :=
  Bandwidth.monotone_cost_expectation univ univ_nonempty cost φ hφ

theorem exponentialLaw_cross (cost : X → ℝ) {h₁ h₂ : ℝ}
    (hh₁ : 0 < h₁) (h₁₂ : h₁ ≤ h₂) (i j : X) (hcost : cost i ≤ cost j) :
    exponentialLaw cost h₂ i * exponentialLaw cost h₁ j ≤
      exponentialLaw cost h₁ i * exponentialLaw cost h₂ j :=
  Bandwidth.likelihoodRatio_cross_le univ univ_nonempty cost hh₁ h₁₂ i j hcost

end FreeFoundations.FiniteProbability
