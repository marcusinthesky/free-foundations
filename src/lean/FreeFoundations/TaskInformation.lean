import FreeFoundations.Recovery
import Mathlib.Analysis.Matrix.Order
import Mathlib.Analysis.CStarAlgebra.ContinuousFunctionalCalculus.Order

/-!
# Noise-weighted information about declared economic coordinates

The finite task operator uses Euclidean norms, with inverse-noise precisions.
Information order concerns the anchored economic coordinates. The inverse
precision identities are matrix algebra; a Gaussian-posterior interpretation
requires an additional observation model.
-/

noncomputable section

namespace FreeFoundations.TaskInformation

open Matrix WithLp
open scoped MatrixOrder

variable {n t : Type*} [Fintype n] [Fintype t]

/-- Information contributed by finitely many noisy task directions. -/
def information (c : t → n → ℝ) (w : t → ℝ) : Matrix n n ℝ :=
  ∑ k, w k • vecMulVec (c k) (c k)

theorem information_posSemidef (c : t → n → ℝ) {w : t → ℝ} (hw : ∀ k, 0 ≤ w k) :
    (information c w).PosSemidef := by
  apply posSemidef_sum Finset.univ
  intro k _
  have hp : (vecMulVec (c k) (c k)).PosSemidef := by
    simpa using posSemidef_vecMulVec_self_star (c k)
  exact hp.smul (hw k)

/-- A positive independent measurement adds a positive-semidefinite information increment. -/
theorem information_increment (J : Matrix n n ℝ) (c : n → ℝ) {w : ℝ} (hw : 0 ≤ w) :
    J ≤ J + w • vecMulVec c c := by
  have hc : (vecMulVec c c).PosSemidef := by simpa using posSemidef_vecMulVec_self_star c
  have hp : (w • vecMulVec c c).PosSemidef := hc.smul hw
  exact le_add_of_nonneg_right hp.nonneg

/-- Weighted linear task operator. -/
def taskOperator (c : t → EuclideanSpace ℝ n) (w : t → ℝ) :
    EuclideanSpace ℝ n →ₗ[ℝ] EuclideanSpace ℝ t where
  toFun a := toLp 2 fun k => Real.sqrt (w k) * inner ℝ (c k) a
  map_add' a b := by ext k; simp [inner_add_right, mul_add]
  map_smul' r a := by ext k; simp [inner_smul_right]; ring

theorem taskOperator_norm_sq (c : t → EuclideanSpace ℝ n) {w : t → ℝ}
    (hw : ∀ k, 0 ≤ w k) (a : EuclideanSpace ℝ n) :
    ‖taskOperator c w a‖ ^ 2 = ∑ k, w k * (inner ℝ (c k) a) ^ 2 := by
  rw [EuclideanSpace.norm_sq_eq]
  apply Finset.sum_congr rfl
  intro k _
  simp [taskOperator, mul_pow, Real.sq_sqrt (hw k)]

/-- Quadratic information equals squared weighted task signal. -/
theorem information_quadratic (c : t → n → ℝ) (w : t → ℝ) (a : n → ℝ) :
    a ⬝ᵥ (information c w *ᵥ a) = ∑ k, w k * (c k ⬝ᵥ a) ^ 2 := by
  rw [information, Matrix.sum_mulVec, dotProduct_sum]
  apply Finset.sum_congr rfl
  intro k _
  rw [smul_mulVec, dotProduct_smul]
  simp only [smul_eq_mul]
  congr 1
  simp only [dotProduct, mulVec, vecMulVec_apply, Finset.mul_sum, sq]
  simp_rw [Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  ring

/-- A quadratic information floor is the existing recovery margin, not a new framework. -/
theorem distinguishes_of_information_floor (c : t → EuclideanSpace ℝ n) {w : t → ℝ}
    (hw : ∀ k, 0 ≤ w k) {κ : ℝ} (_hκ : 0 ≤ κ)
    (hfloor : ∀ a : EuclideanSpace ℝ n,
      κ ^ 2 * ‖a‖ ^ 2 ≤ (a : n → ℝ) ⬝ᵥ
        (information (fun k => (c k : n → ℝ)) w *ᵥ (a : n → ℝ))) :
    Recovery.Distinguishes (taskOperator c w) κ := by
  intro a
  have hf := hfloor a
  rw [information_quadratic] at hf
  have he : ∀ k, (c k : n → ℝ) ⬝ᵥ (a : n → ℝ) = inner ℝ (c k) a := by
    intro k
    simp [PiLp.inner_apply, dotProduct, mul_comm]
  simp_rw [he] at hf
  rw [← taskOperator_norm_sq c hw a] at hf
  nlinarith [norm_nonneg (taskOperator c w a), norm_nonneg a]

/-- The information-floor condition supplies the declared economic decoder. -/
theorem exists_decoder_of_information_floor (c : t → EuclideanSpace ℝ n) {w : t → ℝ}
    (hw : ∀ k, 0 ≤ w k) {κ : ℝ} (hκ : 0 < κ)
    (hfloor : ∀ a : EuclideanSpace ℝ n,
      κ ^ 2 * ‖a‖ ^ 2 ≤ (a : n → ℝ) ⬝ᵥ
        (information (fun k => (c k : n → ℝ)) w *ᵥ (a : n → ℝ))) :
    ∃ L, Recovery.Decoder (taskOperator c w) κ L :=
  Recovery.exists_decoder hκ (distinguishes_of_information_floor c hw hκ.le hfloor)

/-- A Loewner information floor supplies the Euclidean recovery margin. -/
theorem distinguishes_of_loewner_floor [DecidableEq n] (c : t → EuclideanSpace ℝ n) {w : t → ℝ}
    (hw : ∀ k, 0 ≤ w k) {κ : ℝ} (hκ : 0 ≤ κ)
    (hfloor : κ ^ 2 • (1 : Matrix n n ℝ) ≤ information (fun k => (c k : n → ℝ)) w) :
    Recovery.Distinguishes (taskOperator c w) κ := by
  apply distinguishes_of_information_floor c hw hκ
  intro a
  have h := (Matrix.le_iff.mp hfloor).dotProduct_mulVec_nonneg (a : n → ℝ)
  simp only [star_trivial, sub_mulVec, dotProduct_sub, smul_mulVec, one_mulVec,
    dotProduct_smul, smul_eq_mul] at h
  have hn : (a : n → ℝ) ⬝ᵥ (a : n → ℝ) = ‖a‖ ^ 2 := by
    rw [EuclideanSpace.real_norm_sq_eq]
    simp only [dotProduct, pow_two]
  rw [hn] at h
  linarith

/-- Information with a full task-noise covariance. -/
def noiseInformation {s : Type*} [Fintype s] [DecidableEq s]
    (C : Matrix s n ℝ) (R : Matrix s s ℝ) : Matrix n n ℝ := Cᵀ * R⁻¹ * C

omit [Fintype n] in
/-- Simultaneously changing task units and the noise covariance preserves information. -/
theorem task_units_invariant {s : Type*} [Fintype s] [DecidableEq s]
    (C : Matrix s n ℝ) (R T : Matrix s s ℝ) (hT : IsUnit T) :
    noiseInformation (T * C) (T * R * Tᵀ) = noiseInformation C R := by
  have hTt : IsUnit Tᵀ := by
    rw [isUnit_iff_isUnit_det, det_transpose]
    exact (isUnit_iff_isUnit_det _).mp hT
  simp only [noiseInformation, transpose_mul, Matrix.mul_inv_rev]
  simp only [Matrix.mul_assoc]
  rw [← Matrix.mul_assoc Tᵀ, Matrix.mul_nonsing_inv _ ((isUnit_iff_isUnit_det _).mp hTt)]
  rw [← Matrix.mul_assoc T⁻¹, Matrix.nonsing_inv_mul _ ((isUnit_iff_isUnit_det _).mp hT)]
  simp

variable [DecidableEq n]

/-- Rank-one inverse update proved from the independently augmented precision.
`noise` is the strictly positive variance of the appended measurement. -/
theorem rank_one_inverse (Q : Matrix n n ℝ) (hQ : Q.PosDef) (c : n → ℝ)
    {noise : ℝ} (hnoise : 0 < noise) :
    (Q + noise⁻¹ • vecMulVec c c)⁻¹ =
      Q⁻¹ - (noise + c ⬝ᵥ (Q⁻¹ *ᵥ c))⁻¹ •
        vecMulVec (Q⁻¹ *ᵥ c) (Q⁻¹ *ᵥ c) := by
  let P := Q⁻¹
  let u := P *ᵥ c
  let q := c ⬝ᵥ u
  let V := vecMulVec c u
  let U := vecMulVec u u
  have hP : P.PosDef := hQ.inv
  have hPt : Pᵀ = P := isHermitian_iff_isSymm.mp hP.isHermitian
  have hQP : Q * P = 1 := Matrix.mul_nonsing_inv Q (isUnit_iff_ne_zero.mpr hQ.det_pos.ne')
  have hu : Q *ᵥ u = c := by
    rw [show u = P *ᵥ c from rfl, mulVec_mulVec, hQP, one_mulVec]
  have hv : c ᵥ* P = u := by
    rw [← hPt, vecMul_transpose]
  have hq : 0 ≤ q := by
    simpa only [q, u, star_trivial] using hP.posSemidef.dotProduct_mulVec_nonneg c
  have hd : 0 < noise + q := add_pos_of_pos_of_nonneg hnoise hq
  have hQU : Q * U = V := by
    change Q * vecMulVec u u = vecMulVec c u
    rw [mul_vecMulVec, hu]
  have hVP : vecMulVec c c * P = V := by rw [vecMulVec_mul, hv]
  have hVU : vecMulVec c c * U = q • V := by
    ext i j
    simp only [U, V, Matrix.mul_apply, vecMulVec_apply, Matrix.smul_apply, smul_eq_mul,
      q, dotProduct, Finset.sum_mul]
    apply Finset.sum_congr rfl
    intro k _
    ring
  have hc : -(noise + q)⁻¹ + noise⁻¹ - noise⁻¹ * (noise + q)⁻¹ * q = 0 := by
    field_simp
    ring
  apply Matrix.inv_eq_right_inv
  change (Q + noise⁻¹ • vecMulVec c c) * (P - (noise + q)⁻¹ • U) = 1
  simp only [add_mul, mul_sub, Matrix.mul_smul, Matrix.smul_mul,
    hQP, hQU, hVP, hVU, smul_smul]
  calc
    _ = 1 + (-(noise + q)⁻¹ + noise⁻¹ - noise⁻¹ * (noise + q)⁻¹ * q) • V := by module
    _ = 1 := by rw [hc]; simp

/-- An independent positive-precision measurement weakly lowers inverse precision. -/
theorem rank_one_inverse_le (Q : Matrix n n ℝ) (hQ : Q.PosDef) (c : n → ℝ)
    {noise : ℝ} (hnoise : 0 < noise) :
    (Q + noise⁻¹ • vecMulVec c c)⁻¹ ≤ Q⁻¹ := by
  rw [rank_one_inverse Q hQ c hnoise]
  apply sub_le_self
  apply PosSemidef.nonneg
  have hu : (vecMulVec (Q⁻¹ *ᵥ c) (Q⁻¹ *ᵥ c)).PosSemidef := by
    simpa using posSemidef_vecMulVec_self_star (Q⁻¹ *ᵥ c)
  apply hu.smul
  apply inv_nonneg.mpr
  have hq : 0 ≤ c ⬝ᵥ (Q⁻¹ *ᵥ c) := by
    simpa only [star_trivial] using hQ.inv.posSemidef.dotProduct_mulVec_nonneg c
  linarith

/-- Prior-plus-task precision version; the matrix identity itself makes no Gaussian claim. -/
theorem posterior_precision_update (P0 J : Matrix n n ℝ) (hP0 : P0.PosDef)
    (hJ : J.PosSemidef) (c : n → ℝ) {noise : ℝ} (hnoise : 0 < noise) :
    (P0⁻¹ + J + noise⁻¹ • vecMulVec c c)⁻¹ =
      (P0⁻¹ + J)⁻¹ - (noise + c ⬝ᵥ ((P0⁻¹ + J)⁻¹ *ᵥ c))⁻¹ •
        vecMulVec ((P0⁻¹ + J)⁻¹ *ᵥ c) ((P0⁻¹ + J)⁻¹ *ᵥ c) :=
  rank_one_inverse _ (hP0.inv.add_posSemidef hJ) c hnoise

theorem posterior_precision_mono (P0 J : Matrix n n ℝ) (hP0 : P0.PosDef)
    (hJ : J.PosSemidef) (c : n → ℝ) {noise : ℝ} (hnoise : 0 < noise) :
    (P0⁻¹ + J + noise⁻¹ • vecMulVec c c)⁻¹ ≤ (P0⁻¹ + J)⁻¹ :=
  rank_one_inverse_le _ (hP0.inv.add_posSemidef hJ) c hnoise

end FreeFoundations.TaskInformation
