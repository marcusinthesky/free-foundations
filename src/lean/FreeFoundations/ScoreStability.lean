module

public import Mathlib.Analysis.Calculus.Deriv.MeanValue
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv
public import Mathlib.Analysis.Matrix.Order
public import FreeFoundations.Score
public import FreeFoundations.Stability
public import FreeFoundations.MatrixBounds

@[expose] public section

/-!
# Quantitative continuity of covariance scores

The loss convention is `log det S + tr (S⁻¹ T)`. Its Gaussian negative log score
has half this loss gap. The factor form of whitening avoids choosing coordinates
for a principal matrix square root.
-/

namespace FreeFoundations.ScoreStability

open Matrix
open scoped Matrix.Norms.L2Operator MatrixOrder

/-- A local quadratic bound for the scalar contribution to Stein's loss. -/
theorem sub_log_one_add_le {x r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1) (hx : |x| ≤ r) :
    0 ≤ x - Real.log (1 + x) ∧ x - Real.log (1 + x) ≤ x ^ 2 / (2 * (1 - r)) := by
  have hx' := abs_le.mp hx
  have hpos : 0 < 1 + x := by linarith
  refine ⟨by linarith [Real.log_le_sub_one_of_pos hpos], ?_⟩
  let F : ℝ → ℝ := fun y => y ^ 2 / (2 * (1 - r)) - y + Real.log (1 + y)
  let F' : ℝ → ℝ := fun y => y / (1 - r) - 1 + (1 + y)⁻¹
  have hd : ∀ y, -r ≤ y → HasDerivAt F (F' y) y := by
    intro y hy
    have hypos : 0 < 1 + y := by linarith
    convert (((hasDerivAt_id y).pow 2).div_const (2 * (1 - r))).sub
      (hasDerivAt_id y) |>.add (((hasDerivAt_id y).const_add 1).log hypos.ne') using 1 <;>
      first | rfl | (dsimp [F, F']; field_simp)
  have heq : ∀ y, -r ≤ y → F' y = y * (y + r) / ((1 - r) * (1 + y)) := by
    intro y hy
    have hp : 0 < 1 + y := by linarith
    dsimp [F']
    field_simp [ne_of_gt (sub_pos.mpr hr1), hp.ne']
    ring
  have hc : ContinuousOn F (Set.Icc (-r) r) := fun y hy => (hd y hy.1).continuousAt.continuousWithinAt
  have hzero : F 0 = 0 := by simp [F]
  have hF : 0 ≤ F x := by
    by_cases hx0 : 0 ≤ x
    · have hm : MonotoneOn F (Set.Icc 0 r) := by
        apply monotoneOn_of_hasDerivWithinAt_nonneg (convex_Icc _ _)
          (hc.mono (Set.Icc_subset_Icc (by linarith) le_rfl))
          (fun y hy => (hd y (by have := interior_subset hy; exact le_trans (by linarith) this.1)).hasDerivWithinAt)
        intro y hy
        have hy' := interior_subset hy
        rw [heq y (by linarith [hy'.1])]
        have hy0 : 0 ≤ y := hy'.1
        have hyr0 : 0 ≤ y + r := by linarith
        have hrpos : 0 < 1 - r := by linarith
        positivity
      have ht := hm (by constructor <;> linarith) (by exact ⟨hx0, hx'.2⟩) hx0
      simpa [hzero] using ht
    · have hm : AntitoneOn F (Set.Icc (-r) 0) := by
        apply antitoneOn_of_hasDerivWithinAt_nonpos (convex_Icc _ _)
          (hc.mono (Set.Icc_subset_Icc le_rfl hr))
          (fun y hy => (hd y (interior_subset hy).1).hasDerivWithinAt)
        intro y hy
        have hy' := interior_subset hy
        rw [heq y hy'.1]
        apply div_nonpos_of_nonpos_of_nonneg
        · exact mul_nonpos_of_nonpos_of_nonneg hy'.2 (by linarith [hy'.1])
        · have hp : 0 < 1 + y := by linarith [hy'.1]
          positivity
      have ht := hm (by exact ⟨hx'.1, le_of_not_ge hx0⟩) (by constructor <;> linarith)
        (le_of_not_ge hx0)
      simpa [hzero] using ht
  dsimp [F] at hF
  linarith

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The sum of squared entries, with no matrix norm instance implicit in its definition. -/
def entrySquares (A : Matrix n n ℝ) : ℝ := ∑ i, ∑ j, A i j ^ 2

omit [DecidableEq n] in
theorem entrySquares_eq_frobeniusNorm_sq (A : Matrix n n ℝ) :
    entrySquares A = MatrixBounds.frobeniusNorm A ^ 2 :=
  (MatrixBounds.frobeniusNorm_sq A).symm

omit [DecidableEq n] in
/-- For a symmetric matrix, the entry sum of squares equals the trace of its square. -/
theorem entrySquares_eq_trace_sq {A : Matrix n n ℝ} (hA : A.IsHermitian) :
    entrySquares A = trace (A * A) := by
  simp only [entrySquares, trace, diag, mul_apply]
  apply Finset.sum_congr rfl
  intro i _
  apply Finset.sum_congr rfl
  intro j _
  have hij : A j i = A i j := by simpa using hA.apply i j
  rw [hij, pow_two]

/-- Unitary changes of coordinates preserve trace. -/
theorem trace_unitary_conjugate (U : unitary (Matrix n n ℝ)) (A : Matrix n n ℝ) :
    trace (Unitary.conjStarAlgAut ℝ _ U A) = trace A := by
  rw [Unitary.conjStarAlgAut_apply, trace_mul_cycle, Unitary.coe_star_mul_self, one_mul]

/-- The squared eigenvalues sum to the squared Frobenius quantity. -/
theorem eigenvalues_sq_sum {A : Matrix n n ℝ} (hA : A.IsHermitian) :
    ∑ i, (hA.eigenvalues i) ^ 2 = entrySquares A := by
  rw [entrySquares_eq_trace_sq hA]
  conv_rhs => rw [hA.spectral_theorem]
  rw [← map_mul, trace_unitary_conjugate, diagonal_mul_diagonal, trace_diagonal]
  simp [pow_two]

/-- Spectral control of a centered eigenvalue, proved by applying the operator to its
unit eigenvector. -/
theorem abs_eigenvalue_sub_one_le {A : Matrix n n ℝ} (hA : A.IsHermitian) (i : n) :
    |hA.eigenvalues i - 1| ≤ ‖A - 1‖ := by
  let v := hA.eigenvectorBasis i
  have hv : ‖v‖ = 1 := hA.eigenvectorBasis.orthonormal.1 i
  have heig : Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) (A - 1) v =
      (hA.eigenvalues i - 1) • v := by
    apply WithLp.ofLp_injective
    rw [Matrix.ofLp_toEuclideanCLM]
    change (A - 1) *ᵥ (hA.eigenvectorBasis i).ofLp =
      ((hA.eigenvalues i - 1) • hA.eigenvectorBasis i).ofLp
    rw [sub_mulVec, one_mulVec, hA.mulVec_eigenvectorBasis]
    ext j
    simp [sub_mul]
  have ht := (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) (A - 1)).le_opNorm v
  rw [heig, norm_smul, hv, mul_one, Real.norm_eq_abs, Matrix.l2_opNorm_toEuclideanCLM] at ht
  simpa only [mul_one] using ht

/-- Centering the eigenvalues at one gives the squared Frobenius quantity of `A-I`. -/
theorem centered_eigenvalues_sq_sum {A : Matrix n n ℝ} (hA : A.IsHermitian) :
    ∑ i, (hA.eigenvalues i - 1) ^ 2 = entrySquares (A - 1) := by
  have hE : (A - 1).IsHermitian := hA.sub (isHermitian_one)
  rw [entrySquares_eq_trace_sq hE]
  have hsq : (A - 1) * (A - 1) = A * A - A - A + 1 := by noncomm_ring
  rw [hsq, trace_add, trace_sub, trace_sub, trace_one,
    ← entrySquares_eq_trace_sq hA, ← eigenvalues_sq_sum hA, hA.trace_eq_sum_eigenvalues]
  simp only [RCLike.ofReal_real_eq_id, id_eq]
  rw [← Finset.sum_sub_distrib, ← Finset.sum_sub_distrib]
  have hcard : (Fintype.card n : ℝ) = ∑ _i : n, (1 : ℝ) := by simp
  rw [hcard, ← Finset.sum_add_distrib]
  exact Finset.sum_congr rfl fun i _ => by ring

/-- The whitened covariance score has a quadratic upper bound. This theorem proves its
spectral identities rather than assuming an eigenvalue expansion. -/
theorem stein_identity_local {A : Matrix n n ℝ} (hA : A.PosDef) {r : ℝ}
    (hr : 0 ≤ r) (hr1 : r < 1) (herror : ‖A - 1‖ ≤ r) :
    0 ≤ trace A - Real.log A.det - Fintype.card n ∧
      trace A - Real.log A.det - Fintype.card n ≤ entrySquares (A - 1) / (2 * (1 - r)) := by
  have hsum : trace A - Real.log A.det - Fintype.card n =
      ∑ i, ((hA.1.eigenvalues i - 1) - Real.log (1 + (hA.1.eigenvalues i - 1))) := by
    have ht := hA.1.trace_eq_sum_eigenvalues
    simp only [RCLike.ofReal_real_eq_id, id_eq] at ht
    rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← ht]
    simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul,
      mul_one, add_sub_cancel]
    have hd := hA.1.det_eq_prod_eigenvalues
    simp only [RCLike.ofReal_real_eq_id, id_eq] at hd
    rw [← Real.log_prod (fun i _ => (hA.eigenvalues_pos i).ne'), ← hd]
    ring
  have hb : ∀ i, 0 ≤ (hA.1.eigenvalues i - 1) - Real.log (1 + (hA.1.eigenvalues i - 1)) ∧
      (hA.1.eigenvalues i - 1) - Real.log (1 + (hA.1.eigenvalues i - 1)) ≤
        (hA.1.eigenvalues i - 1) ^ 2 / (2 * (1 - r)) := fun i =>
    sub_log_one_add_le hr hr1 ((abs_eigenvalue_sub_one_le hA.1 i).trans herror)
  rw [hsum]
  refine ⟨Finset.sum_nonneg fun i _ => (hb i).1, ?_⟩
  calc _ ≤ ∑ i, (hA.1.eigenvalues i - 1) ^ 2 / (2 * (1 - r)) :=
      Finset.sum_le_sum fun i _ => (hb i).2
    _ = entrySquares (A - 1) / (2 * (1 - r)) := by
      rw [← Finset.sum_div, centered_eigenvalues_sq_sum hA.1]

/-- Whitening by any invertible forecast factor. -/
noncomputable def whiten (B T : Matrix n n ℝ) : Matrix n n ℝ := B⁻¹ᵀ * T * B⁻¹

theorem whiten_posDef {B T : Matrix n n ℝ} (hB : IsUnit B.det) (hT : T.PosDef) :
    (whiten B T).PosDef := by
  have hBi : IsUnit B⁻¹ := (isUnit_iff_isUnit_det _).mpr (by
    rw [det_nonsing_inv, Ring.inverse_eq_inv']
    exact isUnit_iff_ne_zero.mpr (inv_ne_zero hB.ne_zero))
  simpa only [whiten, conjTranspose_eq_transpose_of_trivial] using
    hT.conjTranspose_mul_mul_same (mulVec_injective_of_isUnit hBi)

/-- Exact loss reduction to the positive definite whitened matrix. -/
theorem loss_whiten_identity {S T B : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    (hfactor : S = Bᵀ * B) :
    Score.loss S T - Score.loss T T =
      trace (whiten B T) - Real.log (whiten B T).det - Fintype.card n := by
  have hdetS : S.det = B.det ^ 2 := by rw [hfactor, det_mul, det_transpose, sq]
  have hBdet : B.det ≠ 0 := by
    intro hzero
    have := hS.det_pos
    rw [hdetS, hzero] at this
    simp at this
  have hSinv : S⁻¹ = B⁻¹ * B⁻¹ᵀ := by rw [hfactor, Matrix.mul_inv_rev, transpose_nonsing_inv]
  have htrace : trace (S⁻¹ * T) = trace (whiten B T) := by
    rw [hSinv, Matrix.mul_assoc, trace_mul_comm]
    rfl
  have hdet : (whiten B T).det = T.det / S.det := by
    simp only [whiten, det_mul, det_transpose, det_nonsing_inv, Ring.inverse_eq_inv', hdetS]
    field_simp
  have hlog : Real.log (whiten B T).det = Real.log T.det - Real.log S.det := by
    rw [hdet, Real.log_div hT.det_pos.ne' hS.det_pos.ne']
  rw [Score.loss_sub hT]
  simp only [Score.stein, htrace, hlog]
  ring

/-- Local quadratic covariance-score regret, in an arbitrary invertible whitening
factor. `entrySquares` is the squared Frobenius norm. -/
theorem loss_gap_local_factor {S T B : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    (hfactor : S = Bᵀ * B) {r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1)
    (herror : ‖whiten B T - 1‖ ≤ r) :
    0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤ entrySquares (whiten B T - 1) / (2 * (1 - r)) := by
  have hB : IsUnit B.det := isUnit_iff_ne_zero.mpr fun hz => by
    have hp := hS.det_pos
    rw [hfactor, det_mul, det_transpose, hz] at hp
    simp at hp
  rw [loss_whiten_identity hS hT hfactor]
  exact stein_identity_local (whiten_posDef hB hT) hr hr1 herror

/-- The same local theorem with an explicit Frobenius norm in its public statement. -/
theorem loss_gap_local {S T B : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    (hfactor : S = Bᵀ * B) {r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1)
    (herror : ‖whiten B T - 1‖ ≤ r) :
    0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤
        MatrixBounds.frobeniusNorm (whiten B T - 1) ^ 2 / (2 * (1 - r)) := by
  simpa only [entrySquares_eq_frobeniusNorm_sq] using
    loss_gap_local_factor hS hT hfactor hr hr1 herror

/-- An order floor bounds each eigenvalue, with the Euclidean normalization explicit. -/
theorem eigenvalues_ge_of_floor {S : Matrix n n ℝ} (hS : S.IsHermitian) {m : ℝ}
    (hfloor : (S - m • 1).PosSemidef) (i : n) : m ≤ hS.eigenvalues i := by
  let v := hS.eigenvectorBasis i
  have hv : ‖v‖ = 1 := hS.eigenvectorBasis.orthonormal.1 i
  have hvdot : v.ofLp ⬝ᵥ v.ofLp = 1 := by
    have ht := real_inner_self_eq_norm_sq v
    simpa only [PiLp.inner_apply, RCLike.inner_apply, conj_trivial, hv, one_pow,
      dotProduct] using ht
  have hp := hfloor.re_dotProduct_nonneg v.ofLp
  rw [sub_mulVec, smul_mulVec, one_mulVec, hS.mulVec_eigenvectorBasis] at hp
  simp only [dotProduct_sub, dotProduct_smul, star_trivial, smul_eq_mul] at hp
  change 0 ≤ hS.eigenvalues i * (v.ofLp ⬝ᵥ v.ofLp) - m * (v.ofLp ⬝ᵥ v.ofLp) at hp
  rw [hvdot] at hp
  linarith

/-- Unitary conjugation preserves the Euclidean operator norm, including real matrices. -/
theorem norm_unitary_conjugate (U : unitary (Matrix n n ℝ)) (A : Matrix n n ℝ) :
    ‖Unitary.conjStarAlgAut ℝ _ U A‖ = ‖A‖ := by
  rw [Unitary.conjStarAlgAut_apply]
  change ‖(U : Matrix n n ℝ) * A * ((star U : unitary (Matrix n n ℝ)) : Matrix n n ℝ)‖ = _
  rw [CStarRing.norm_mul_coe_unitary, CStarRing.norm_coe_unitary_mul]

/-- A positive eigenvalue floor controls the norm of the inverse. -/
theorem norm_inverse_le_of_floor {S : Matrix n n ℝ} (hS : S.PosDef) {m : ℝ}
    (hm : 0 < m) (hfloor : (S - m • 1).PosSemidef) : ‖S⁻¹‖ ≤ m⁻¹ := by
  let U := hS.1.eigenvectorUnitary
  let e := hS.1.eigenvalues
  have he : ∀ i, m ≤ e i := eigenvalues_ge_of_floor hS.1 hfloor
  have hinv : S⁻¹ = Unitary.conjStarAlgAut ℝ _ U (diagonal fun i => (e i)⁻¹) := by
    apply inv_eq_left_inv
    conv_lhs => arg 2; rw [hS.1.spectral_theorem]
    rw [← map_mul, diagonal_mul_diagonal]
    have hd : diagonal (fun i => (e i)⁻¹ * (RCLike.ofReal ∘ e) i) = (1 : Matrix n n ℝ) := by
      ext i j
      have hei : e i ≠ 0 := (hS.eigenvalues_pos i).ne'
      simp [diagonal_apply, Matrix.one_apply, hei]
    rw [hd, map_one]
  rw [hinv, norm_unitary_conjugate, Matrix.l2_opNorm_diagonal]
  apply (pi_norm_le_iff_of_nonneg (inv_nonneg.mpr hm.le)).mpr
  intro i
  rw [Real.norm_eq_abs, abs_of_nonneg (inv_nonneg.mpr (hm.le.trans (he i)))]
  exact inv_anti₀ hm (he i)

theorem norm_transpose (A : Matrix n n ℝ) : ‖Aᵀ‖ = ‖A‖ := by
  simpa only [conjTranspose_eq_transpose_of_trivial] using l2_opNorm_conjTranspose A

/-- The squared inverse-factor norm is the inverse forecast norm. -/
theorem norm_inverse_factor_sq {S B : Matrix n n ℝ} (hfactor : S = Bᵀ * B) :
    ‖B⁻¹‖ ^ 2 = ‖S⁻¹‖ := by
  rw [hfactor, Matrix.mul_inv_rev, ← transpose_nonsing_inv]
  have ht := l2_opNorm_conjTranspose_mul_self B⁻¹ᵀ
  simpa only [conjTranspose_eq_transpose_of_trivial, transpose_transpose, norm_transpose,
    pow_two] using ht.symm

/-- Centered whitening is a congruence of the original covariance error. -/
theorem whiten_sub_one {S B T : Matrix n n ℝ} (hB : IsUnit B.det)
    (hfactor : S = Bᵀ * B) : whiten B T - 1 = B⁻¹ᵀ * (T - S) * B⁻¹ := by
  have hself : B⁻¹ᵀ * S * B⁻¹ = 1 := by
    rw [hfactor]
    have hleft : B⁻¹ᵀ * Bᵀ = 1 := by rw [← transpose_mul, mul_nonsing_inv _ hB, transpose_one]
    calc B⁻¹ᵀ * (Bᵀ * B) * B⁻¹ = (B⁻¹ᵀ * Bᵀ) * (B * B⁻¹) := by simp only [mul_assoc]
      _ = 1 := by rw [hleft, mul_nonsing_inv _ hB, one_mul]
  rw [mul_sub, sub_mul, hself]
  rfl

/-- An absolute covariance error and forecast floor bound the relative whitened error. -/
theorem whiten_error_le {S B T : Matrix n n ℝ} (hS : S.PosDef)
    (hfactor : S = Bᵀ * B) {m : ℝ} (hm : 0 < m) (hfloor : (S - m • 1).PosSemidef) :
    ‖whiten B T - 1‖ ≤ ‖T - S‖ / m := by
  have hB : IsUnit B.det := isUnit_iff_ne_zero.mpr fun hz => by
    have hp := hS.det_pos
    rw [hfactor, det_mul, det_transpose, hz] at hp
    simp at hp
  rw [whiten_sub_one hB hfactor]
  calc ‖B⁻¹ᵀ * (T - S) * B⁻¹‖ ≤ ‖B⁻¹ᵀ‖ * ‖T - S‖ * ‖B⁻¹‖ :=
        (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _))
    _ = ‖B⁻¹‖ ^ 2 * ‖T - S‖ := by rw [norm_transpose]; ring
    _ = ‖S⁻¹‖ * ‖T - S‖ := by rw [norm_inverse_factor_sq hfactor]
    _ ≤ m⁻¹ * ‖T - S‖ := mul_le_mul_of_nonneg_right
        (norm_inverse_le_of_floor hS hm hfloor) (norm_nonneg _)
    _ = ‖T - S‖ / m := by ring

/-- Absolute covariance error to local quadratic score regret. The eigenvalue floor,
local radius and dimension factor are explicit. -/
theorem loss_gap_le_of_norm_sub {S T : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    {m e : ℝ} (hm : 0 < m) (hfloor : (S - m • 1).PosSemidef)
    (herror : ‖S - T‖ ≤ e) (helocal : e < m) :
    0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤
        Fintype.card n * (e / m) ^ 2 / (2 * (1 - e / m)) := by
  obtain ⟨B, hB⟩ := CStarAlgebra.nonneg_iff_eq_star_mul_self.mp hS.posSemidef.nonneg
  rw [star_eq_conjTranspose, conjTranspose_eq_transpose_of_trivial] at hB
  have he : 0 ≤ e := (norm_nonneg _).trans herror
  have hr : 0 ≤ e / m := div_nonneg he hm.le
  have hr1 : e / m < 1 := (div_lt_one hm).mpr helocal
  have hE : ‖whiten B T - 1‖ ≤ e / m := by
    refine (whiten_error_le hS hB hm hfloor).trans ?_
    exact div_le_div_of_nonneg_right (by rwa [norm_sub_rev]) hm.le
  have hl := loss_gap_local_factor hS hT hB hr hr1 hE
  refine ⟨hl.1, hl.2.trans ?_⟩
  apply div_le_div_of_nonneg_right _ (by positivity)
  rw [entrySquares_eq_frobeniusNorm_sq]
  calc MatrixBounds.frobeniusNorm (whiten B T - 1) ^ 2 ≤
        Fintype.card n * MatrixBounds.spectralNorm (whiten B T - 1) ^ 2 :=
      MatrixBounds.frobeniusNorm_sq_le_card_mul_spectralNorm_sq _
    _ ≤ Fintype.card n * (e / m) ^ 2 := by
      change (Fintype.card n : ℝ) * ‖whiten B T - 1‖ ^ 2 ≤ _
      gcongr

/-- Every matrix entry is bounded by the Euclidean operator norm. -/
theorem abs_entry_le_norm (A : Matrix n n ℝ) (i j : n) : |A i j| ≤ ‖A‖ := by
  let v : EuclideanSpace ℝ n := WithLp.toLp 2 (Pi.single j 1)
  have hv : ‖v‖ = 1 := by simp [v]
  have hb := Matrix.l2_opNorm_mulVec A v
  rw [hv, mul_one] at hb
  have hcol : A *ᵥ v = fun k => A k j := by
    simpa only [v, WithLp.ofLp_toLp, Matrix.col_apply'] using Matrix.mulVec_single_one A j
  rw [hcol] at hb
  have hi := PiLp.norm_apply_le (WithLp.toLp 2 (fun k => A k j)) i
  have hi' : |A i j| ≤ ‖(WithLp.toLp 2 (fun k => A k j) : EuclideanSpace ℝ n)‖ := by
    simpa only [WithLp.ofLp_toLp, Real.norm_eq_abs] using hi
  exact hi'.trans hb

/-- Trace is Lipschitz in the spectral norm with its explicit dimension factor. -/
theorem abs_trace_le_card_mul_norm (A : Matrix n n ℝ) :
    |trace A| ≤ Fintype.card n * ‖A‖ := by
  calc |trace A| ≤ ∑ i, |A i i| := by simpa only [trace, diag] using Finset.abs_sum_le_sum_abs (fun i : n => A i i) Finset.univ
    _ ≤ ∑ _i : n, ‖A‖ := Finset.sum_le_sum fun i _ => abs_entry_le_norm A i i
    _ = _ := by simp

/-- One-sided log-determinant continuity follows from the supporting-hyperplane
inequality already certified by nonnegativity of Stein's loss. -/
theorem logdet_sub_le {S T : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef) :
    Real.log S.det - Real.log T.det ≤ Fintype.card n * ‖T⁻¹‖ * ‖S - T‖ := by
  have hstein := Score.stein_nonneg hT hS
  have hTinv : trace (T⁻¹ * T) = Fintype.card n := by
    rw [nonsing_inv_mul _ (isUnit_iff_ne_zero.mpr hT.det_pos.ne'), trace_one]
  have htrace : trace (T⁻¹ * S) - Fintype.card n = trace (T⁻¹ * (S - T)) := by
    rw [mul_sub, trace_sub, hTinv]
  have hs : Real.log S.det - Real.log T.det ≤ trace (T⁻¹ * (S - T)) := by
    dsimp [Score.stein] at hstein
    rw [← htrace]
    linarith
  calc Real.log S.det - Real.log T.det ≤ trace (T⁻¹ * (S - T)) := hs
    _ ≤ |trace (T⁻¹ * (S - T))| := le_abs_self _
    _ ≤ Fintype.card n * ‖T⁻¹ * (S - T)‖ := abs_trace_le_card_mul_norm _
    _ ≤ Fintype.card n * (‖T⁻¹‖ * ‖S - T‖) := mul_le_mul_of_nonneg_left
        (norm_mul_le _ _) (by positivity)
    _ = _ := by ring

/-- Global log-determinant continuity under a common positive eigenvalue floor. -/
theorem abs_logdet_sub_le {S T : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    {m : ℝ} (hm : 0 < m) (hfloorS : (S - m • 1).PosSemidef)
    (hfloorT : (T - m • 1).PosSemidef) :
    |Real.log S.det - Real.log T.det| ≤ (Fintype.card n : ℝ) / m * ‖S - T‖ := by
  have hs : Real.log S.det - Real.log T.det ≤ (Fintype.card n : ℝ) / m * ‖S - T‖ := by
    calc _ ≤ Fintype.card n * ‖T⁻¹‖ * ‖S - T‖ := logdet_sub_le hS hT
      _ ≤ Fintype.card n * m⁻¹ * ‖S - T‖ := by
        gcongr
        exact norm_inverse_le_of_floor hT hm hfloorT
      _ = _ := by ring
  have ht : Real.log T.det - Real.log S.det ≤ (Fintype.card n : ℝ) / m * ‖S - T‖ := by
    calc _ ≤ Fintype.card n * ‖S⁻¹‖ * ‖T - S‖ := logdet_sub_le hT hS
      _ ≤ Fintype.card n * m⁻¹ * ‖T - S‖ := by
        gcongr
        exact norm_inverse_le_of_floor hS hm hfloorS
      _ = _ := by rw [norm_sub_rev]; ring
  exact abs_le.mpr ⟨by linarith, hs⟩

end FreeFoundations.ScoreStability
