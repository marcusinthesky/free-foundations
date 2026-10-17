import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Data.Real.Basic

/-!
# Network algebra

`A = I − λW` for a spatial weights matrix `W`. The spatial-error covariance is
`A⁻¹ D A⁻ᵀ`, so these facts about `A⁻¹` say what a network can represent.
-/

namespace FreeFoundations.Network

open Matrix

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- **Exact expansion.** `(I − λW)⁻¹ = I + λW + λ²W²(I − λW)⁻¹`: to first order a network is
a one-parameter kernel `λW`, and the remainder is explicit. -/
theorem inverse_expansion (W : Matrix n n ℝ) (c : ℝ) (h : IsUnit (1 - c • W).det) :
    (1 - c • W)⁻¹ = 1 + c • W + c ^ 2 • (W * W) * (1 - c • W)⁻¹ := by
  set X := (1 - c • W)⁻¹
  have hX : (1 - c • W) * X = 1 := mul_nonsing_inv _ h
  have hrec : X = 1 + c • (W * X) := by
    rw [sub_mul, one_mul, smul_mul_assoc] at hX
    rw [← hX]
    abel
  calc X = 1 + c • (W * X) := hrec
    _ = 1 + c • (W * (1 + c • (W * X))) := by conv_lhs => rw [hrec]
    _ = 1 + c • W + c ^ 2 • (W * W) * X := by
      rw [mul_add, mul_one, smul_add, mul_smul_comm, smul_smul, ← Matrix.mul_assoc,
        smul_mul_assoc, pow_two]
      abel

/-- If `(I − λW)v = μv` with `μ ≠ 0`, the inverse scales `v` by `μ⁻¹`. -/
theorem inverse_on_eigenvector (W : Matrix n n ℝ) (c μ : ℝ) (v : n → ℝ)
    (h : IsUnit (1 - c • W).det) (hμ : μ ≠ 0) (hv : (1 - c • W) *ᵥ v = μ • v) :
    (1 - c • W)⁻¹ *ᵥ v = μ⁻¹ • v := by
  have hinv : (1 - c • W)⁻¹ * (1 - c • W) = 1 := nonsing_inv_mul _ h
  have := congrArg (fun u => (1 - c • W)⁻¹ *ᵥ u) hv
  simp only [mulVec_mulVec, hinv, one_mulVec, mulVec_smul] at this
  conv_rhs => rw [this]
  rw [smul_smul, inv_mul_cancel₀ hμ, one_smul]

/-! ## The uniform network is a pure common component -/

/-- Equal weight `1/(N − 1)` on every other firm. -/
noncomputable def uniform : Matrix n n ℝ :=
  Matrix.of fun i j => if i = j then 0 else ((Fintype.card n : ℝ) - 1)⁻¹

/-- The uniform network maps the constant vector to itself... -/
theorem uniform_const (hn : 2 ≤ Fintype.card n) : uniform *ᵥ (fun _ : n => (1 : ℝ)) = fun _ => 1 := by
  funext i
  have hne : ((Fintype.card n : ℝ) - 1) ≠ 0 := by
    have : (2 : ℝ) ≤ Fintype.card n := by exact_mod_cast hn
    linarith
  simp only [uniform, mulVec, dotProduct, of_apply, mul_one]
  rw [Finset.sum_ite, Finset.sum_const_zero, zero_add, Finset.sum_const, nsmul_eq_mul,
    show (Finset.univ.filter fun x => ¬ i = x) = Finset.univ.erase i by ext x; simp [eq_comm],
    Finset.card_erase_of_mem (Finset.mem_univ i), Finset.card_univ, Nat.cast_sub (by omega),
    Nat.cast_one, mul_inv_cancel₀ hne]

/-- ...and every vector summing to zero to `−1/(N − 1)` times itself. So `(I − λU)⁻¹`
multiplies the cross-sectional mean by `1/(1 − λ)` and everything else by
`1/(1 + λ/(N − 1))`: one equicorrelated factor, or in a no-intercept cross-section a
random intercept whose variance grows without bound as `λ → 1`. -/
theorem uniform_sum_zero (v : n → ℝ) (hv : ∑ j, v j = 0) :
    uniform *ᵥ v = (-((Fintype.card n : ℝ) - 1)⁻¹) • v := by
  funext i
  simp only [uniform, mulVec, dotProduct, of_apply, Pi.smul_apply, smul_eq_mul]
  have hsplit : ∑ j, (if i = j then (0 : ℝ) else ((Fintype.card n : ℝ) - 1)⁻¹) * v j =
      ((Fintype.card n : ℝ) - 1)⁻¹ * (∑ j, v j - v i) := by
    have htotal : ∑ j, v j = ∑ j ∈ Finset.univ.filter (fun j => i = j), v j +
        ∑ j ∈ Finset.univ.filter (fun j => ¬ i = j), v j :=
      (Finset.sum_filter_add_sum_filter_not _ _ _).symm
    simp_rw [ite_mul, zero_mul]
    rw [Finset.sum_ite, Finset.sum_const_zero, zero_add, ← Finset.mul_sum, htotal,
      Finset.filter_eq, if_pos (Finset.mem_univ i), Finset.sum_singleton]
    ring
  rw [hsplit, hv]
  ring

/-! ## Size-tercile placebos -/

/-- Relabelling firms by a permutation leaves `det(I − λW)`, and so the Jacobian term of
every likelihood, unchanged. -/
theorem placebo_det (W : Matrix n n ℝ) (σ : Equiv.Perm n) (c : ℝ) :
    (1 - c • W.submatrix σ σ).det = (1 - c • W).det := by
  rw [← det_submatrix_equiv_self σ (1 - c • W)]
  congr 1
  ext i j
  simp [Matrix.one_apply, sub_apply, smul_apply, submatrix_apply, σ.injective.eq_iff]

omit [DecidableEq n] in
/-- A within-group permutation preserves the total weight linking any two groups. -/
theorem placebo_group_mass {G : Type*} [DecidableEq G] (W : Matrix n n ℝ)
    (σ : Equiv.Perm n) (g : n → G) (hσ : ∀ i, g (σ i) = g i) (a b : G) :
    (∑ i, ∑ j, if g i = a ∧ g j = b then W (σ i) (σ j) else 0) =
      ∑ i, ∑ j, if g i = a ∧ g j = b then W i j else 0 := by
  have key : ∀ i j, (if g i = a ∧ g j = b then W (σ i) (σ j) else 0) =
      (fun p q => if g p = a ∧ g q = b then W p q else 0) (σ i) (σ j) := by
    intro i j
    simp only [hσ]
  simp_rw [key]
  rw [Equiv.sum_comp σ (fun p => ∑ j, (fun p q => if g p = a ∧ g q = b then W p q else 0) p (σ j))]
  refine Finset.sum_congr rfl fun i _ => ?_
  exact Equiv.sum_comp σ (fun q => if g i = a ∧ g q = b then W i q else 0)

end FreeFoundations.Network
