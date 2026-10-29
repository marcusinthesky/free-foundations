module

public import Mathlib.Algebra.BigOperators.Ring.Finset
public import Mathlib.Basic.Real.Basic
public import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
public import Mathlib.Data.Fintype.BigOperators
public import Mathlib.Algebra.BigOperators.Field
public import Mathlib.Tactic.Ring

@[expose] public section

/-!
# Where a network's value comes from

Against the uniform network `U`, a row-stochastic network `W` gains through the inner
product `⟨W − U, C⟩` with the common cross-moment `Cᵢⱼ = ½(kᵢ + kⱼ − ρᵢⱼ²)`
(`Exposure.covariance_eq`, with communality `k` and exposure distance `ρ`). The common part
cancels, because both networks have unit row sums, and two terms remain:

`⟨W − U, C⟩ = ½ Σⱼ (cⱼ − 1) kⱼ − ½ Σᵢⱼ (Wᵢⱼ − Uᵢⱼ) ρᵢⱼ²`,

where `cⱼ` is the column sum of `W`. The first is a *hub* term, which rewards in-weight on
high-communality firms. The second is a *proximity* term, which rewards weight on firms
with close exposures. A within-group placebo `PWPᵀ` keeps the hub term whenever
communality is constant within groups, so a placebo comparison isolates proximity only
under that condition.
-/

namespace FreeFoundations.Value

open Finset

variable {n : Type*} [Fintype n]

/-- **Hub plus proximity.** -/
theorem decomposition (W U ρ : n → n → ℝ) (k : n → ℝ) (hW : ∀ i, ∑ j, W i j = 1)
    (hU : ∀ i, ∑ j, U i j = 1) (hUc : ∀ j, ∑ i, U i j = 1) :
    ∑ i, ∑ j, (W i j - U i j) * ((k i + k j - ρ i j ^ 2) / 2) =
      (∑ j, ((∑ i, W i j) - 1) * k j) / 2 - (∑ i, ∑ j, (W i j - U i j) * ρ i j ^ 2) / 2 := by
  have h1 : ∑ i, ∑ j, (W i j - U i j) * k i = 0 := by
    refine sum_eq_zero fun i _ => ?_
    rw [← sum_mul, sum_sub_distrib, hW, hU, sub_self, zero_mul]
  have h2 : ∑ i, ∑ j, (W i j - U i j) * k j = ∑ j, ((∑ i, W i j) - 1) * k j := by
    rw [sum_comm]
    refine sum_congr rfl fun j _ => ?_
    rw [← sum_mul, sum_sub_distrib, hUc]
  have hsplit : ∀ i j, (W i j - U i j) * ((k i + k j - ρ i j ^ 2) / 2) =
      ((W i j - U i j) * k i + (W i j - U i j) * k j - (W i j - U i j) * ρ i j ^ 2) / 2 :=
    fun i j => by ring
  simp_rw [hsplit, ← sum_div, sum_sub_distrib, sum_add_distrib]
  rw [h1, h2]
  ring

/-- **Placebos keep the hub term** when communality is constant within the groups the
permutation respects. -/
theorem placebo_hub {G : Type*} (W : n → n → ℝ) (k : n → ℝ) (σ : Equiv.Perm n) (g : n → G)
    (hσ : ∀ j, g (σ j) = g j) (hk : ∀ i j, g i = g j → k i = k j) :
    ∑ j, ((∑ i, W (σ i) (σ j)) - 1) * k j = ∑ j, ((∑ i, W i j) - 1) * k j := by
  have hcol : ∀ j, ∑ i, W (σ i) (σ j) = ∑ i, W i (σ j) := fun j =>
    Equiv.sum_comp σ (fun i => W i (σ j))
  simp_rw [hcol]
  have hkσ : ∀ j, k j = k (σ j) := fun j => hk _ _ (hσ j).symm
  calc ∑ j, ((∑ i, W i (σ j)) - 1) * k j = ∑ j, ((∑ i, W i (σ j)) - 1) * k (σ j) :=
        sum_congr rfl fun j _ => by rw [← hkσ]
    _ = ∑ j, ((∑ i, W i j) - 1) * k j := Equiv.sum_comp σ (fun j => ((∑ i, W i j) - 1) * k j)

end FreeFoundations.Value
