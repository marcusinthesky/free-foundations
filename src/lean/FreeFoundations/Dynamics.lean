module

public import FreeFoundations.Recovery
public import Mathlib.Analysis.Matrix.Order

@[expose] public section

/-! Known linear dynamics provide additional observable task directions. -/

namespace FreeFoundations.Dynamics

open Matrix Finset
open scoped MatrixOrder

variable {n m : Type*} [Fintype n] [DecidableEq n] [Fintype m] [DecidableEq m]

/-- Stacked finite-horizon observations, with a Euclidean row index. -/
def observation (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) :
    Matrix (Fin H × m) n ℝ := fun t j => (C * F ^ (t.1 : ℕ)) t.2 j

/-- Information accumulated from the first H known noiseless observation maps. -/
def gramian (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) : Matrix n n ℝ :=
  ∑ t ∈ range H, (C * F ^ t)ᵀ * (C * F ^ t)

omit [DecidableEq m] in
theorem gramian_succ (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) :
    gramian (H + 1) C F = gramian H C F + (C * F ^ H)ᵀ * (C * F ^ H) := by
  simp only [gramian, sum_range_succ]

omit [DecidableEq m] in
theorem gramian_mono (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) :
    gramian H C F ≤ gramian (H + 1) C F := by
  rw [gramian_succ, Matrix.le_iff, add_sub_cancel_left]
  simpa using Matrix.posSemidef_conjTranspose_mul_self (C * F ^ H)

omit [DecidableEq m] in
theorem observation_gram (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) :
    (observation H C F)ᵀ * observation H C F = gramian H C F := by
  ext i j
  simp only [Matrix.mul_apply, Matrix.transpose_apply, observation, gramian,
    Matrix.sum_apply, Fintype.sum_prod_type]
  exact Fin.sum_univ_eq_sum_range (fun t : ℕ => ∑ r : m,
    (C * F ^ t) r i * (C * F ^ t) r j) H

omit [DecidableEq m] in
/-- Reuse the existing decoder theorem on the stacked observation map. -/
theorem observable_decoder (H : ℕ) (C : Matrix m n ℝ) (F : Matrix n n ℝ) {κ : ℝ}
    (hκ : 0 < κ) (hobs : Recovery.Distinguishes (Matrix.toEuclideanLin (observation H C F)) κ) :
    ∃ L, Recovery.Decoder (Matrix.toEuclideanLin (observation H C F)) κ L :=
  Recovery.exists_decoder hκ hobs

/-- A coordinate exchange exposes the previously hidden second coordinate next period. -/
def swap : Matrix (Fin 2) (Fin 2) ℝ := !![0, 1; 1, 0]

def firstCoordinate : Matrix (Fin 1) (Fin 2) ℝ := !![1, 0]

theorem two_horizons (a : EuclideanSpace ℝ (Fin 2)) :
    ((firstCoordinate * swap ^ 0) *ᵥ a) 0 = a 0 ∧
    ((firstCoordinate * swap ^ 1) *ᵥ a) 0 = a 1 := by
  simp [firstCoordinate, swap, Matrix.mulVec, dotProduct, Matrix.mul_apply, Fin.sum_univ_two]

theorem one_horizon_not_injective :
    ¬ Function.Injective (fun a : EuclideanSpace ℝ (Fin 2) => (firstCoordinate *ᵥ a) 0) := by
  intro h
  have heq := h (a₁ := WithLp.toLp 2 ![0, 0]) (a₂ := WithLp.toLp 2 ![0, 1]) (by
    simp [firstCoordinate, Matrix.mulVec, dotProduct, Fin.sum_univ_two])
  have := congrArg (fun a : EuclideanSpace ℝ (Fin 2) => a 1) heq
  norm_num at this


/-- The two-horizon example has minimum gain one in its Euclidean stacked space. -/
theorem two_horizons_distinguish :
    Recovery.Distinguishes (Matrix.toEuclideanLin (observation 2 firstCoordinate swap)) 1 := by
  intro a
  have hs : ‖(Matrix.toEuclideanLin (observation 2 firstCoordinate swap)) a‖ ^ 2 = ‖a‖ ^ 2 := by
    change ‖(WithLp.toLp 2 ((observation 2 firstCoordinate swap) *ᵥ a.ofLp) :
      EuclideanSpace ℝ (Fin 2 × Fin 1))‖ ^ 2 = _
    simp only [PiLp.norm_sq_eq_of_L2, Real.norm_eq_abs, sq_abs,
      Fintype.sum_prod_type, Fin.sum_univ_two, Fin.sum_univ_one]
    simp [observation, firstCoordinate, swap, Matrix.mulVec, dotProduct, Matrix.mul_apply,
      Fin.sum_univ_two]
  simpa only [one_mul] using (sq_le_sq₀ (norm_nonneg a) (norm_nonneg _)).mp hs.ge

end FreeFoundations.Dynamics
