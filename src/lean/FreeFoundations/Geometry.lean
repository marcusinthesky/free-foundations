import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.SpecialFunctions.Pow.Real
import FreeFoundations.Alignment

/-!
# Information is not geometry

A representation can keep every distinction the economic state needs and still give the
wrong distances, because sufficiency is invariant under any bijection of the representation
space and distances are not.

* Reparametrising `Z` by a bijection preserves optimality and sufficiency
  (`Alignment.Optimal`, `Alignment.Sufficient`); rescaling by `c` multiplies every distance
  by `|c|`.
* The direct baseline maps a prepared vector `x` to `[x, 1]/‖[x, 1]‖`. The map is
  injective, so it discards nothing, yet every chord distance is at most 2 however far
  apart the inputs are. Its usefulness is an empirical fact about this geometry, not a
  consequence of preserving information.

So extraction, normalisation and kernel each need their own validation, or a readout that
fixes the geometry (`Recovery.readout_invariant`).

A readout fitted to task outputs does not fix it on its own. Task means `C a` identify
exposures only up to an invertible map `G`, since `(C G⁻¹)(G a) = C a`
(`observationally_equivalent`), and the two descriptions give the same distances only when
`G` preserves norms (`distances_preserved_iff`). An anchor is needed. The common covariance
is one: it fixes every inner product `⟪aᵢ, aⱼ⟫`, hence every distance
(`Exposure.inner_eq_half`), and leaves only rotations free.
-/

namespace FreeFoundations.Geometry

open FreeFoundations.Alignment

universe u

variable {H T S R R' : Type u}

/-- A bijective reparametrisation keeps a representation optimal. -/
theorem optimal_equiv (F : H → T) (Z : H → R) (e : R ≃ R') :
    Optimal F Z ↔ Optimal F (e ∘ Z) := by
  constructor
  · rintro ⟨d, hd⟩
    exact ⟨d ∘ e.symm, by rw [hd]; funext h; simp⟩
  · rintro ⟨d, hd⟩
    exact ⟨d ∘ e, by rw [hd]; rfl⟩

/-- A bijective reparametrisation keeps a representation sufficient. -/
theorem sufficient_equiv (state : H → S) (Z : H → R) (e : R ≃ R') :
    Sufficient state Z ↔ Sufficient state (e ∘ Z) := by
  constructor
  · rintro ⟨r, hr⟩
    exact ⟨r ∘ e.symm, by rw [hr]; funext h; simp⟩
  · rintro ⟨r, hr⟩
    exact ⟨r ∘ e, by rw [hr]; rfl⟩

/-- **Same information, different distances.** Scaling a representation by `c ≠ 0` keeps it
sufficient and multiplies every distance by `|c|`. -/
theorem rescale {E : Type u} [NormedAddCommGroup E] [NormedSpace ℝ E] (state : H → S)
    (Z : H → E) {c : ℝ} (hc : c ≠ 0) :
    (Sufficient state Z ↔ Sufficient state (fun h => c • Z h)) ∧
      ∀ h h', ‖c • Z h - c • Z h'‖ = |c| * ‖Z h - Z h'‖ := by
  refine ⟨sufficient_equiv state Z (Equiv.smulRight hc), fun h h' => ?_⟩
  rw [← smul_sub, norm_smul, Real.norm_eq_abs]

/-! ## The direct baseline -/

variable {n : Type*} [Fintype n]

/-- `[x, 1]/‖[x, 1]‖`, with `none` the appended constant coordinate. -/
noncomputable def chord (x : n → ℝ) (o : Option n) : ℝ :=
  (Real.sqrt (1 + ∑ i, x i ^ 2))⁻¹ * o.elim 1 x

theorem one_add_sq_pos (x : n → ℝ) : 0 < 1 + ∑ i, x i ^ 2 :=
  add_pos_of_pos_of_nonneg one_pos (Finset.sum_nonneg fun _ _ => sq_nonneg _)

theorem chord_scale_pos (x : n → ℝ) : 0 < (Real.sqrt (1 + ∑ i, x i ^ 2))⁻¹ :=
  inv_pos.mpr (Real.sqrt_pos.mpr (one_add_sq_pos x))

/-- **Injective.** `x` is recovered as `v_{1:p}/v_{p+1}`. -/
theorem chord_left_inverse (x : n → ℝ) : (fun i => chord x (some i) / chord x none) = x := by
  funext i
  simp only [chord, Option.elim, mul_one]
  rw [mul_div_cancel_left₀ _ (chord_scale_pos x).ne']

theorem chord_injective : Function.Injective (chord (n := n)) := fun x y h => by
  rw [← chord_left_inverse x, ← chord_left_inverse y, h]

/-- The baseline lies on the unit sphere. -/
theorem chord_sq_sum (x : n → ℝ) : ∑ o, chord x o ^ 2 = 1 := by
  have hpos := one_add_sq_pos x
  rw [Fintype.sum_option]
  simp only [chord, Option.elim, mul_one, mul_pow, inv_pow, Real.sq_sqrt hpos.le,
    ← Finset.mul_sum]
  field_simp

/-- **Bounded.** Every squared chord distance is at most 4, whatever the inputs. -/
theorem chord_dist_sq_le (x y : n → ℝ) : ∑ o, (chord x o - chord y o) ^ 2 ≤ 4 := by
  calc ∑ o, (chord x o - chord y o) ^ 2 ≤ ∑ o, (2 * chord x o ^ 2 + 2 * chord y o ^ 2) :=
        Finset.sum_le_sum fun o _ => by nlinarith [sq_nonneg (chord x o + chord y o)]
    _ = 4 := by
      rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, chord_sq_sum,
        chord_sq_sum]
      norm_num

/-! ## Identification -/

section Identification

variable {A B : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
  [NormedAddCommGroup B] [InnerProductSpace ℝ B]

/-- **Observational equivalence.** Task means identify exposures only up to an invertible
map: `(C G⁻¹)(G a) = C a`. -/
theorem observationally_equivalent (C : A →ₗ[ℝ] B) (G : A ≃ₗ[ℝ] A) (a : A) :
    (C ∘ₗ G.symm.toLinearMap) (G a) = C a := by
  simp

/-- The two descriptions give the same distances for every configuration iff `G` preserves
norms. Scaling by `c` (`rescale`) is observationally equivalent and multiplies every
distance by `|c|`. -/
theorem distances_preserved_iff (G : A →ₗ[ℝ] A) :
    (∀ x y, ‖G x - G y‖ = ‖x - y‖) ↔ ∀ x, ‖G x‖ = ‖x‖ := by
  constructor
  · intro h x
    simpa using h x 0
  · intro h x y
    rw [← map_sub]
    exact h _

end Identification

end FreeFoundations.Geometry
