import FreeFoundations.Kernel
import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.LinearAlgebra.Matrix.NonsingularInverse
import Mathlib.Algebra.Order.BigOperators.Ring.Finset

/-!
# Reversible row-normalized networks

Symmetry and positive degrees supply a weighted Euclidean contraction. The degree ratio
is retained when converting the weighted certificate to the ordinary Euclidean norm.
-/

namespace FreeFoundations.ReversibleNetwork

open Finset Matrix

variable {n : Type*} [Fintype n]

noncomputable def degree (K : Matrix n n ℝ) (i : n) : ℝ := ∑ j, K i j

noncomputable def normalize (K : Matrix n n ℝ) : Matrix n n ℝ :=
  fun i j => K i j / degree K i

/-- Detailed balance follows from symmetry of the unnormalized kernel. -/
theorem detailed_balance (K : Matrix n n ℝ) (hK : ∀ i j, K i j = K j i)
    (hs : ∀ i, 0 < degree K i) (i j : n) :
    degree K i * normalize K i j = degree K j * normalize K j i := by
  simp only [normalize]
  field_simp [(hs i).ne', (hs j).ne']
  exact hK i j

theorem normalize_nonneg (K : Matrix n n ℝ) (hK : ∀ i j, 0 ≤ K i j)
    (hs : ∀ i, 0 < degree K i) (i j : n) : 0 ≤ normalize K i j :=
  div_nonneg (hK i j) (hs i).le

theorem normalize_row_sum (K : Matrix n n ℝ) (hs : ∀ i, 0 < degree K i) (i : n) :
    ∑ j, normalize K i j = 1 := by
  simp only [normalize, ← sum_div]
  exact div_self (hs i).ne'

/-- Degree weights are stationary for a symmetric normalized kernel. -/
theorem stationary_degree (K : Matrix n n ℝ) (hK : ∀ i j, K i j = K j i)
    (hs : ∀ i, 0 < degree K i) (j : n) :
    ∑ i, degree K i * normalize K i j = degree K j := by
  calc _ = ∑ i, K j i := by
          apply sum_congr rfl
          intro i _
          simp only [normalize]
          rw [mul_div_cancel₀ _ (hs i).ne', hK i j]
    _ = _ := rfl

/-- Weighted squared Euclidean norm, kept explicit rather than installing another norm. -/
noncomputable def energy (s : n → ℝ) (x : n → ℝ) : ℝ := ∑ i, s i * x i ^ 2

/-- A stochastic row contracts second moments (finite weighted Cauchy--Schwarz). -/
theorem row_square_le (w x : n → ℝ) (hw : ∀ j, 0 ≤ w j) (hsum : ∑ j, w j = 1) :
    (∑ j, w j * x j) ^ 2 ≤ ∑ j, w j * x j ^ 2 := by
  have h := sum_sq_le_sum_mul_sum_of_sq_le_mul (univ : Finset n)
    (r := fun j => w j * x j) (f := w) (g := fun j => w j * x j ^ 2)
    (fun j _ => hw j) (fun j _ => mul_nonneg (hw j) (sq_nonneg _))
    (fun j _ => by ring_nf; rfl)
  simpa only [hsum, one_mul] using h

/-- Any stationary nonnegative weights give a weighted squared-norm contraction. -/
theorem energy_contraction (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    (hs : ∀ i, 0 ≤ s i) (hstationary : ∀ j, ∑ i, s i * W i j = s j) (x : n → ℝ) :
    energy s (W *ᵥ x) ≤ energy s x := by
  calc _ ≤ ∑ i, s i * ∑ j, W i j * x j ^ 2 := by
          apply sum_le_sum
          intro i _
          exact mul_le_mul_of_nonneg_left (row_square_le (W i) x (hW i) (hrow i)) (hs i)
    _ = ∑ j, (∑ i, s i * W i j) * x j ^ 2 := by
          simp_rw [mul_sum, sum_mul]
          rw [sum_comm]
          apply sum_congr rfl
          intro j _
          apply sum_congr rfl
          intro i _
          ring
    _ = _ := by simp only [hstationary, energy]

/-- Symmetric nonnegative kernels contract the degree-weighted squared norm. -/
theorem normalize_energy_contraction (K : Matrix n n ℝ)
    (hK : ∀ i j, 0 ≤ K i j) (hSym : ∀ i j, K i j = K j i)
    (hs : ∀ i, 0 < degree K i) (x : n → ℝ) :
    energy (degree K) (normalize K *ᵥ x) ≤ energy (degree K) x :=
  energy_contraction _ _ (normalize_nonneg K hK hs) (normalize_row_sum K hs)
    (fun i => (hs i).le) (stationary_degree K hSym hs) x

/-- The corresponding explicit weighted norm. -/
noncomputable def weightedNorm (s : n → ℝ) (x : n → ℝ) : ℝ :=
  ‖(WithLp.toLp 2 fun i => Real.sqrt (s i) * x i : EuclideanSpace ℝ n)‖

theorem weightedNorm_sq (s : n → ℝ) (hs : ∀ i, 0 ≤ s i) (x : n → ℝ) :
    weightedNorm s x ^ 2 = energy s x := by
  simp only [weightedNorm, EuclideanSpace.real_norm_sq_eq, mul_pow,
    Real.sq_sqrt (hs _), energy]

theorem weightedNorm_nonneg (s : n → ℝ) (x : n → ℝ) : 0 ≤ weightedNorm s x := norm_nonneg _

theorem weightedNorm_sub_le (s : n → ℝ) (x y : n → ℝ) :
    weightedNorm s (x - y) ≤ weightedNorm s x + weightedNorm s y := by
  have heq : (WithLp.toLp 2 fun i => Real.sqrt (s i) * (x - y) i : EuclideanSpace ℝ n) =
      (WithLp.toLp 2 fun i => Real.sqrt (s i) * x i : EuclideanSpace ℝ n) -
      (WithLp.toLp 2 fun i => Real.sqrt (s i) * y i : EuclideanSpace ℝ n) := by
    ext i
    simp [mul_sub]
  unfold weightedNorm
  rw [heq]
  exact norm_sub_le _ _

theorem weightedNorm_smul (s : n → ℝ) (c : ℝ) (x : n → ℝ) :
    weightedNorm s (c • x) = |c| * weightedNorm s x := by
  have heq : (WithLp.toLp 2 fun i => Real.sqrt (s i) * (c • x) i : EuclideanSpace ℝ n) =
      c • (WithLp.toLp 2 fun i => Real.sqrt (s i) * x i : EuclideanSpace ℝ n) := by
    ext i
    simp
    ring
  simpa only [weightedNorm, Real.norm_eq_abs, norm_smul] using congrArg norm heq

/-- Weighted Euclidean contraction, requiring stationarity rather than reversibility. -/
theorem weightedNorm_contraction (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    (hs : ∀ i, 0 ≤ s i) (hstationary : ∀ j, ∑ i, s i * W i j = s j) (x : n → ℝ) :
    weightedNorm s (W *ᵥ x) ≤ weightedNorm s x := by
  apply (sq_le_sq₀ (weightedNorm_nonneg _ _) (weightedNorm_nonneg _ _)).mp
  rw [weightedNorm_sq _ hs, weightedNorm_sq _ hs]
  exact energy_contraction W s hW hrow hs hstationary x

/-- Positive weights make the explicit weighted norm definite. -/
theorem weightedNorm_eq_zero_iff (s : n → ℝ) (hs : ∀ i, 0 < s i) (x : n → ℝ) :
    weightedNorm s x = 0 ↔ x = 0 := by
  constructor
  · intro hx
    have he : energy s x = 0 := by rw [← weightedNorm_sq s (fun i => (hs i).le) x, hx]; norm_num
    ext i
    have ht : s i * x i ^ 2 ≤ energy s x :=
      single_le_sum (fun j _ => mul_nonneg (hs j).le (sq_nonneg _)) (mem_univ i)
    rw [he] at ht
    have hsq : x i ^ 2 = 0 := by nlinarith [hs i, sq_nonneg (x i)]
    exact sq_eq_zero_iff.mp hsq
  · rintro rfl
    simp [weightedNorm]
    rfl

variable [DecidableEq n]

/-- The spatial map is bounded below in the weighted norm. -/
theorem weighted_resolvent_lower (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    (hs : ∀ i, 0 ≤ s i) (hstationary : ∀ j, ∑ i, s i * W i j = s j)
    (c : ℝ) (x : n → ℝ) :
    (1 - |c|) * weightedNorm s x ≤ weightedNorm s ((1 - c • W) *ᵥ x) := by
  have heq : (1 - c • W) *ᵥ x - (-c) • (W *ᵥ x) = x := by
    rw [sub_mulVec, one_mulVec, smul_mulVec]
    module
  have ht := weightedNorm_sub_le s ((1 - c • W) *ᵥ x) ((-c) • (W *ᵥ x))
  rw [heq, weightedNorm_smul, abs_neg] at ht
  have hc := mul_le_mul_of_nonneg_left (weightedNorm_contraction W s hW hrow hs hstationary x)
    (abs_nonneg c)
  linarith

/-- `|λ|<1` ensures nonsingularity under the stochastic and stationary-weight conditions. -/
theorem spatial_isUnit (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    (hs : ∀ i, 0 < s i) (hstationary : ∀ j, ∑ i, s i * W i j = s j)
    {c : ℝ} (hc : |c| < 1) : IsUnit (1 - c • W) := by
  apply mulVec_injective_iff_isUnit.mp
  intro x y hxy
  have hz : (1 - c • W) *ᵥ (x - y) = 0 := by rw [mulVec_sub, hxy, sub_self]
  have hb := weighted_resolvent_lower W s hW hrow (fun i => (hs i).le) hstationary c (x - y)
  rw [hz] at hb
  have hzero : weightedNorm s (x - y) = 0 := by
    have hn := weightedNorm_nonneg s (x - y)
    have : weightedNorm s (0 : n → ℝ) = 0 := by
      simp [weightedNorm]
      rfl
    rw [this] at hb
    nlinarith
  exact sub_eq_zero.mp ((weightedNorm_eq_zero_iff s hs (x - y)).mp hzero)

/-- The inverse has weighted gain at most `1/(1−|λ|)`; invertibility is derived. -/
theorem weighted_resolvent_bound (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    (hs : ∀ i, 0 < s i) (hstationary : ∀ j, ∑ i, s i * W i j = s j)
    {c : ℝ} (hc : |c| < 1) (x : n → ℝ) :
    weightedNorm s ((1 - c • W)⁻¹ *ᵥ x) ≤ weightedNorm s x / (1 - |c|) := by
  have hunit := (isUnit_iff_isUnit_det _).mp (spatial_isUnit W s hW hrow hs hstationary hc)
  have hb := weighted_resolvent_lower W s hW hrow (fun i => (hs i).le) hstationary c
    ((1 - c • W)⁻¹ *ᵥ x)
  rw [mulVec_mulVec, mul_nonsing_inv _ hunit, one_mulVec] at hb
  exact (le_div_iff₀ (by linarith : 0 < 1 - |c|)).mpr (by nlinarith)

omit [DecidableEq n] in
/-- Lower comparison with the ordinary Euclidean norm. -/
theorem weightedNorm_lower (s : n → ℝ) {smin : ℝ} (hsmin : 0 < smin)
    (hs : ∀ i, smin ≤ s i) (x : n → ℝ) :
    Real.sqrt smin * ‖(WithLp.toLp 2 x : EuclideanSpace ℝ n)‖ ≤ weightedNorm s x := by
  apply (sq_le_sq₀ (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _))
    (weightedNorm_nonneg _ _)).mp
  rw [mul_pow, Real.sq_sqrt hsmin.le, weightedNorm_sq s (fun i => (hsmin.le).trans (hs i)),
    EuclideanSpace.real_norm_sq_eq, energy, mul_sum]
  exact sum_le_sum fun i _ => mul_le_mul_of_nonneg_right (hs i) (sq_nonneg _)

omit [DecidableEq n] in
/-- Upper comparison with the ordinary Euclidean norm. -/
theorem weightedNorm_upper (s : n → ℝ) (hs : ∀ i, 0 ≤ s i) {smax : ℝ}
    (hsmax : 0 ≤ smax) (hbound : ∀ i, s i ≤ smax) (x : n → ℝ) :
    weightedNorm s x ≤ Real.sqrt smax * ‖(WithLp.toLp 2 x : EuclideanSpace ℝ n)‖ := by
  apply (sq_le_sq₀ (weightedNorm_nonneg _ _)
    (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _))).mp
  rw [mul_pow, Real.sq_sqrt hsmax, weightedNorm_sq s hs,
    EuclideanSpace.real_norm_sq_eq, energy, mul_sum]
  exact sum_le_sum fun i _ => mul_le_mul_of_nonneg_right (hbound i) (sq_nonneg _)

open scoped Matrix.Norms.L2Operator

/-- Euclidean resolvent certificate with the stationary-weight imbalance visible. -/
theorem resolvent_l2_bound (W : Matrix n n ℝ) (s : n → ℝ)
    (hW : ∀ i j, 0 ≤ W i j) (hrow : ∀ i, ∑ j, W i j = 1)
    {smin smax c : ℝ} (hsmin : 0 < smin) (hsmax : 0 ≤ smax)
    (hlower : ∀ i, smin ≤ s i) (hupper : ∀ i, s i ≤ smax)
    (hstationary : ∀ j, ∑ i, s i * W i j = s j) (hc : |c| < 1) :
    ‖(1 - c • W)⁻¹‖ ≤ Real.sqrt (smax / smin) / (1 - |c|) := by
  have hs : ∀ i, 0 < s i := fun i => hsmin.trans_le (hlower i)
  have hcpos : 0 < 1 - |c| := by linarith
  rw [Matrix.l2_opNorm_def]
  apply ContinuousLinearMap.opNorm_le_bound _ (div_nonneg (Real.sqrt_nonneg _) hcpos.le)
  intro x
  have h1 := weightedNorm_lower s hsmin hlower ((1 - c • W)⁻¹ *ᵥ x)
  have h2 := weighted_resolvent_bound W s hW hrow hs hstationary hc x
  have h3 := weightedNorm_upper s (fun i => (hs i).le) hsmax hupper x
  change ‖(WithLp.toLp 2 ((1 - c • W)⁻¹ *ᵥ x) : EuclideanSpace ℝ n)‖ ≤ _
  calc _ ≤ weightedNorm s ((1 - c • W)⁻¹ *ᵥ x) / Real.sqrt smin :=
          (le_div_iff₀ (Real.sqrt_pos.mpr hsmin)).mpr (by nlinarith)
    _ ≤ (weightedNorm s x / (1 - |c|)) / Real.sqrt smin :=
          div_le_div_of_nonneg_right h2 (Real.sqrt_nonneg _)
    _ ≤ ((Real.sqrt smax * ‖x‖) / (1 - |c|)) / Real.sqrt smin := by
          apply div_le_div_of_nonneg_right _ (Real.sqrt_nonneg _)
          exact div_le_div_of_nonneg_right h3 hcpos.le
    _ = _ := by
          rw [Real.sqrt_div hsmax]
          ring

/-- Symmetric nonnegative kernels meet the stochastic/stationary certificate. -/
theorem normalize_resolvent_l2_bound (K : Matrix n n ℝ)
    (hK : ∀ i j, 0 ≤ K i j) (hSym : ∀ i j, K i j = K j i)
    {smin smax c : ℝ} (hsmin : 0 < smin) (hsmax : 0 ≤ smax)
    (hlower : ∀ i, smin ≤ degree K i) (hupper : ∀ i, degree K i ≤ smax)
    (hc : |c| < 1) :
    ‖(1 - c • normalize K)⁻¹‖ ≤ Real.sqrt (smax / smin) / (1 - |c|) := by
  have hs : ∀ i, 0 < degree K i := fun i => hsmin.trans_le (hlower i)
  exact resolvent_l2_bound _ _ (normalize_nonneg K hK hs) (normalize_row_sum K hs)
    hsmin hsmax hlower hupper (stationary_degree K hSym hs) hc

/-- Symmetric exponential weights before row normalization, with zero diagonal. -/
noncomputable def exponentialRaw (d : Matrix n n ℝ) (h : ℝ) : Matrix n n ℝ :=
  fun i j => if i = j then 0 else Real.exp (-d i j / h)

omit [Fintype n] in
theorem exponentialRaw_nonneg (d : Matrix n n ℝ) (h : ℝ) (i j : n) :
    0 ≤ exponentialRaw d h i j := by
  simp only [exponentialRaw]
  split_ifs <;> positivity

omit [Fintype n] in
theorem exponentialRaw_symmetric (d : Matrix n n ℝ) (hd : ∀ i j, d i j = d j i) (h : ℝ)
    (i j : n) : exponentialRaw d h i j = exponentialRaw d h j i := by
  simp only [exponentialRaw, eq_comm, hd i j]

theorem exponential_degree_eq (d : Matrix n n ℝ) (h : ℝ) (i : n) :
    degree (exponentialRaw d h) i = ∑ j ∈ univ.erase i, Real.exp (-d i j / h) := by
  unfold degree
  rw [← sum_erase_add _ _ (mem_univ i)]
  simp only [exponentialRaw, if_true, add_zero]
  apply sum_congr rfl
  intro j hj
  rw [if_neg (ne_of_mem_erase hj).symm]

theorem normalize_exponentialRaw (d : Matrix n n ℝ) (h : ℝ) :
    normalize (exponentialRaw d h) = Kernel.expKernel d h := by
  ext i j
  simp only [normalize, Kernel.expKernel, Kernel.expRow, Matrix.of_apply, exponentialRaw]
  split_ifs <;> simp [exponential_degree_eq]

/-- Bounded nonnegative distances bound every unnormalized degree. -/
theorem exponential_degree_bounds (hn : 2 ≤ Fintype.card n) (d : Matrix n n ℝ)
    {h D : ℝ} (hh : 0 < h) (hd : ∀ i j, i ≠ j → 0 ≤ d i j ∧ d i j ≤ D) (i : n) :
    ((Fintype.card n : ℝ) - 1) * Real.exp (-D / h) ≤ degree (exponentialRaw d h) i ∧
      degree (exponentialRaw d h) i ≤ (Fintype.card n : ℝ) - 1 := by
  rw [exponential_degree_eq]
  have hcard : ((univ.erase i).card : ℝ) = (Fintype.card n : ℝ) - 1 := by
    rw [card_erase_of_mem (mem_univ i), card_univ, Nat.cast_sub (by omega), Nat.cast_one]
  constructor
  · calc _ = ∑ j ∈ univ.erase i, Real.exp (-D / h) := by rw [sum_const, nsmul_eq_mul, hcard]
      _ ≤ _ := sum_le_sum fun j hj => by
        rw [Real.exp_le_exp]
        exact div_le_div_of_nonneg_right (by linarith [(hd i j (ne_of_mem_erase hj).symm).2]) hh.le
  · calc _ ≤ ∑ j ∈ univ.erase i, (1 : ℝ) := sum_le_sum fun j hj => by
          apply Real.exp_le_one_iff.mpr
          exact div_nonpos_of_nonpos_of_nonneg (by linarith [(hd i j (ne_of_mem_erase hj).symm).1]) hh.le
      _ = _ := by rw [sum_const, nsmul_eq_mul, mul_one, hcard]

/-- The explicit exponential-kernel Euclidean resolvent bound. -/
theorem exponential_resolvent_l2_bound (hn : 2 ≤ Fintype.card n) (d : Matrix n n ℝ)
    (hSym : ∀ i j, d i j = d j i) {h D c : ℝ} (hh : 0 < h)
    (hd : ∀ i j, i ≠ j → 0 ≤ d i j ∧ d i j ≤ D) (hc : |c| < 1) :
    ‖(1 - c • Kernel.expKernel d h)⁻¹‖ ≤ Real.exp (D / (2 * h)) / (1 - |c|) := by
  have hN : 0 < (Fintype.card n : ℝ) - 1 := by
    have : (2 : ℝ) ≤ Fintype.card n := by exact_mod_cast hn
    linarith
  have hb := normalize_resolvent_l2_bound (exponentialRaw d h) (exponentialRaw_nonneg d h)
    (exponentialRaw_symmetric d hSym h) (mul_pos hN (Real.exp_pos _)) hN.le
    (fun i => (exponential_degree_bounds hn d hh hd i).1)
    (fun i => (exponential_degree_bounds hn d hh hd i).2) hc
  rw [normalize_exponentialRaw] at hb
  have hratio : ((Fintype.card n : ℝ) - 1) /
      (((Fintype.card n : ℝ) - 1) * Real.exp (-D / h)) = Real.exp (D / h) := by
    rw [div_mul_eq_div_div, div_self hN.ne', one_div, neg_div, Real.exp_neg, inv_inv]
  have hexp : D / h / 2 = D / (2 * h) := by ring
  rw [hratio, ← Real.exp_half, hexp] at hb
  exact hb

end FreeFoundations.ReversibleNetwork
