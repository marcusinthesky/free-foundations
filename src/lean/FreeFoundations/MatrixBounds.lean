module

public import Mathlib.Analysis.CStarAlgebra.Matrix
public import Mathlib.Algebra.Order.BigOperators.Ring.Finset

@[expose] public section

/-! Explicit matrix norms and the dimension factors connecting them. -/

namespace FreeFoundations.MatrixBounds

open Matrix Finset
open scoped Matrix.Norms.L2Operator

variable {m n : Type*} [Fintype m] [Fintype n] [DecidableEq n]

/-- Euclidean operator norm, independent of the norm instance at the call site. -/
noncomputable def spectralNorm (A : Matrix m n ℝ) : ℝ := ‖A‖

/-- Frobenius norm, defined by its entries. -/
noncomputable def frobeniusNorm (A : Matrix m n ℝ) : ℝ :=
  Real.sqrt (∑ i, ∑ j, (A i j) ^ 2)

/-- Maximum absolute row sum; zero for a matrix without rows. -/
noncomputable def rowSumNorm (A : Matrix m n ℝ) : ℝ :=
  ↑(univ.sup fun i => ∑ j, ‖A i j‖₊)

theorem spectralNorm_eq (A : Matrix m n ℝ) : spectralNorm A = ‖A‖ := rfl

theorem spectralNorm_nonneg (A : Matrix m n ℝ) : 0 ≤ spectralNorm A := norm_nonneg _

omit [DecidableEq n] in
theorem frobeniusNorm_nonneg (A : Matrix m n ℝ) : 0 ≤ frobeniusNorm A := Real.sqrt_nonneg _

omit [DecidableEq n] in
theorem frobeniusNorm_sq (A : Matrix m n ℝ) :
    frobeniusNorm A ^ 2 = ∑ i, ∑ j, (A i j) ^ 2 :=
  Real.sq_sqrt (sum_nonneg fun _ _ => sum_nonneg fun _ _ => sq_nonneg _)

omit [DecidableEq n] in
theorem rowSumNorm_nonneg (A : Matrix m n ℝ) : 0 ≤ rowSumNorm A := NNReal.coe_nonneg _

omit [DecidableEq n] in
theorem row_le_rowSumNorm (A : Matrix m n ℝ) (i : m) :
    ∑ j, |A i j| ≤ rowSumNorm A := by
  have h := le_sup (f := fun i => ∑ j, ‖A i j‖₊) (mem_univ i)
  simpa only [rowSumNorm, NNReal.coe_sum, coe_nnnorm, Real.norm_eq_abs] using
    (NNReal.coe_le_coe.mpr h)

omit [DecidableEq n] in
theorem rowSumNorm_le (A : Matrix m n ℝ) {r : ℝ} (hr : 0 ≤ r)
    (h : ∀ i, ∑ j, |A i j| ≤ r) : rowSumNorm A ≤ r := by
  change (↑(univ.sup fun i => ∑ j, ‖A i j‖₊) : ℝ) ≤ ↑(⟨r, hr⟩ : NNReal)
  apply NNReal.coe_le_coe.mpr
  apply Finset.sup_le
  intro i _
  apply NNReal.coe_le_coe.mp
  simp only [NNReal.coe_sum, coe_nnnorm, Real.norm_eq_abs]
  change (∑ j, |A i j|) ≤ r
  exact h i

omit [DecidableEq n] in
theorem frobeniusNorm_sq_le_card_mul_rowSumNorm_sq (A : Matrix m n ℝ) :
    frobeniusNorm A ^ 2 ≤ Fintype.card m * rowSumNorm A ^ 2 := by
  rw [frobeniusNorm_sq]
  calc ∑ i, ∑ j, (A i j) ^ 2 ≤ ∑ _i : m, rowSumNorm A ^ 2 := by
        apply sum_le_sum
        intro i _
        calc ∑ j, (A i j) ^ 2 = ∑ j, |A i j| ^ 2 := by simp
          _ ≤ (∑ j, |A i j|) ^ 2 := sum_sq_le_sq_sum_of_nonneg fun _ _ => abs_nonneg _
          _ ≤ rowSumNorm A ^ 2 := pow_le_pow_left₀ (sum_nonneg fun _ _ => abs_nonneg _)
            (row_le_rowSumNorm A i) 2
    _ = _ := by simp

omit [DecidableEq n] in
theorem frobeniusNorm_le_sqrt_card_mul_rowSumNorm (A : Matrix m n ℝ) :
    frobeniusNorm A ≤ Real.sqrt (Fintype.card m) * rowSumNorm A := by
  have h := frobeniusNorm_sq_le_card_mul_rowSumNorm_sq A
  have hs : Real.sqrt (Fintype.card m : ℝ) ^ 2 = Fintype.card m := Real.sq_sqrt (by positivity)
  apply (sq_le_sq₀ (frobeniusNorm_nonneg A) (mul_nonneg (Real.sqrt_nonneg _) (rowSumNorm_nonneg A))).mp
  simpa only [mul_pow, hs] using h

set_option maxHeartbeats 800000 in
theorem spectralNorm_le_frobeniusNorm (A : Matrix m n ℝ) :
    spectralNorm A ≤ frobeniusNorm A := by
  rw [spectralNorm, Matrix.l2_opNorm_def]
  apply ContinuousLinearMap.opNorm_le_bound _ (frobeniusNorm_nonneg A)
  intro x
  have hx : ‖x‖ ^ 2 = ∑ j, (x j) ^ 2 := by
    simpa [Real.norm_eq_abs] using PiLp.norm_sq_eq_of_L2 (fun _ : n => ℝ) x
  have himageSq : ‖((Matrix.toEuclideanLin.trans LinearMap.toContinuousLinearMap) A) x‖ ^ 2 =
      ∑ i, (∑ j, A i j * x j) ^ 2 := by
    change ‖WithLp.toLp 2 (A *ᵥ x.ofLp)‖ ^ 2 = _
    simp only [PiLp.norm_sq_eq_of_L2, Real.norm_eq_abs, sq_abs, Matrix.mulVec,
      dotProduct]
  have hs : ∑ i, (∑ j, A i j * x j) ^ 2 ≤
      (∑ i, ∑ j, (A i j) ^ 2) * (∑ j, (x j) ^ 2) := by
    rw [sum_mul]
    exact sum_le_sum fun i _ => sum_mul_sq_le_sq_mul_sq univ (A i) (fun j => x j)
  rw [← frobeniusNorm_sq, ← hx, ← himageSq] at hs
  apply (sq_le_sq₀ (norm_nonneg _) (mul_nonneg (frobeniusNorm_nonneg A) (norm_nonneg x))).mp
  simpa only [mul_pow] using hs

theorem spectralNorm_le_sqrt_card_mul_rowSumNorm (A : Matrix m n ℝ) :
    spectralNorm A ≤ Real.sqrt (Fintype.card m) * rowSumNorm A :=
  (spectralNorm_le_frobeniusNorm A).trans (frobeniusNorm_le_sqrt_card_mul_rowSumNorm A)


/-- Squared Frobenius error is at most the number of columns times squared spectral error. -/
theorem frobeniusNorm_sq_le_card_mul_spectralNorm_sq (A : Matrix m n ℝ) :
    frobeniusNorm A ^ 2 ≤ Fintype.card n * spectralNorm A ^ 2 := by
  classical
  have hcol (j : n) : ∑ i, (A i j) ^ 2 ≤ spectralNorm A ^ 2 := by
    let e : EuclideanSpace ℝ n := WithLp.toLp 2 (Pi.single j 1)
    have he : ‖e‖ = 1 := by simp [e]
    have hb := Matrix.l2_opNorm_mulVec A e
    rw [he, mul_one] at hb
    have hv : A *ᵥ e = fun i => A i j := by simpa only [e, WithLp.ofLp_toLp, Matrix.col_apply'] using (Matrix.mulVec_single_one A j)
    rw [hv] at hb
    change ‖(WithLp.toLp 2 (fun i => A i j) : EuclideanSpace ℝ m)‖ ≤ spectralNorm A at hb
    have hsq := pow_le_pow_left₀ (norm_nonneg _) hb 2
    simpa only [PiLp.norm_sq_eq_of_L2, Real.norm_eq_abs, sq_abs, WithLp.ofLp_toLp] using hsq
  rw [frobeniusNorm_sq, sum_comm]
  calc ∑ j, ∑ i, (A i j) ^ 2 ≤ ∑ _j : n, spectralNorm A ^ 2 := sum_le_sum fun j _ => hcol j
    _ = _ := by simp

end FreeFoundations.MatrixBounds
