import Mathlib.Logic.Function.Basic
import Mathlib.Probability.Distributions.Uniform

/-!
# A representation preserves what its target requires

Deterministic form of ANALYSIS.md §5.2. Histories `H`; `F : H → T` is the Bayes-optimal
statistic of the training target; `state : H → S` is the minimal state for the economic
tasks. A representation `Z : H → R` is *optimal* when the target reads it exactly
(`F = d ∘ Z`) and *sufficient* when the state reads it exactly (`state = r ∘ Z`).
-/

namespace FreeFoundations.Alignment

universe u

variable {H T S : Type u}

/-- `Z` loses nothing the target needs. -/
def Optimal {R : Type u} (F : H → T) (Z : H → R) : Prop := ∃ d : R → T, F = d ∘ Z

/-- `Z` loses nothing the economic tasks need. -/
def Sufficient {R : Type u} (state : H → S) (Z : H → R) : Prop :=
  ∃ r : R → S, state = r ∘ Z

/-- Every target-optimal representation is sufficient iff the target separates every pair of
histories that the economic state separates. -/
theorem optimal_imp_sufficient_iff [Nonempty S] (F : H → T) (state : H → S) :
    (∀ (R : Type u) (Z : H → R), Optimal F Z → Sufficient state Z) ↔
      ∀ h h', F h = F h' → state h = state h' := by
  constructor
  · intro hall h h' hF
    obtain ⟨r, hr⟩ := hall T F ⟨id, rfl⟩
    rw [hr]
    simp [Function.comp, hF]
  · rintro hsep R Z ⟨d, hd⟩
    refine ⟨Function.extend Z state (fun _ => Classical.arbitrary S), funext fun h => ?_⟩
    have hfac : Function.FactorsThrough state Z := fun a b hab =>
      hsep a b (by rw [hd]; simp [Function.comp, hab])
    exact (hfac.extend_apply _ h).symm

/-- The minimal state can itself be optimal for the target iff the target needs no
distinction that the economic state ignores. -/
theorem state_optimal_iff [Nonempty T] (F : H → T) (state : H → S) :
    (∃ d : S → T, F = d ∘ state) ↔ ∀ h h', state h = state h' → F h = F h' := by
  constructor
  · rintro ⟨d, hd⟩ h h' hs
    rw [hd]
    simp [Function.comp, hs]
  · intro hsep
    refine ⟨Function.extend state F (fun _ => Classical.arbitrary T), funext fun h => ?_⟩
    exact ((show Function.FactorsThrough F state from hsep).extend_apply _ h).symm

/-- **Label-null.** With a constant target, a representation that keeps nothing is optimal;
if the economic state varies at all, that representation is not sufficient. -/
theorem constant_target_loses_state (F : H → T) (state : H → S)
    (hF : ∀ h h', F h = F h') {h₀ h₁ : H} (hs : state h₀ ≠ state h₁) :
    Optimal F (fun _ : H => PUnit.unit.{u + 1}) ∧
      ¬ Sufficient state (fun _ : H => PUnit.unit.{u + 1}) := by
  refine ⟨⟨fun _ => F h₀, funext fun h => hF h h₀⟩, ?_⟩
  rintro ⟨r, hr⟩
  exact hs (by rw [hr]; rfl)

/-! ## Marginal targets do not determine dependence (ANALYSIS.md §5.3) -/

/-- `Y₁ = R`, `Y₂ = R xor S` for a fair coin `R` and an observed state `S`. -/
noncomputable def pair (s : Bool) : PMF (Bool × Bool) :=
  (PMF.uniformOfFintype Bool).map fun r => (r, xor r s)

/-- Both marginals are fair coins whatever the state, so a state-free forecast of each
marginal is exact. -/
theorem marginals_free_of_state (s : Bool) :
    (pair s).map Prod.fst = PMF.uniformOfFintype Bool ∧
      (pair s).map Prod.snd = PMF.uniformOfFintype Bool := by
  constructor <;> ext y <;> cases s <;> cases y <;>
    simp [pair, PMF.map_apply, tsum_fintype, Fintype.sum_prod_type, PMF.uniformOfFintype_apply]

/-- Yet the joint law is entirely determined by the state the forecast discarded:
`Y₁ = Y₂` surely when `S = false` and never when `S = true`. -/
theorem joint_depends_on_state :
    (pair false) (true, true) = 1 / 2 ∧ (pair true) (true, true) = 0 := by
  constructor <;> simp [pair, PMF.map_apply, tsum_fintype, PMF.uniformOfFintype_apply]

end FreeFoundations.Alignment
