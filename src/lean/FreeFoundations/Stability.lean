import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.Analysis.Normed.Operator.Basic

/-!
# From network error to covariance, loss and portfolio error

The spatial covariance is `Σ(W) = P V Pᵀ` with `P = (I − λW)⁻¹`. For a common `λ` and `V`,
and resolvents bounded by `M`,

`‖Σ(Ŵ) − Σ(W*)‖ ≤ 2‖V‖ |λ| M³ ‖Ŵ − W*‖`,

so the network error from `Kernel` reaches the covariance amplified by `M³`, which is large
near the unit root. The quadratic term of the Gaussian loss moves by at most
`‖u‖² ‖Σ⁻¹‖ ‖Σ̃⁻¹‖ ‖Σ − Σ̃‖`, and a covariance error `e` costs a minimum-variance
portfolio with `‖w‖ ≤ B` at most `2B²e` of avoidable variance.

The joint perturbation theorem also controls estimated spatial coefficients and innovation
covariances. A separate triangle-inequality corollary retains the spatial approximation error
`Σ(W*) − Σ_true`; that term requires an economic-model assumption or independent evidence.
-/

namespace FreeFoundations.Stability

section Ring

variable {R : Type*} [NormedRing R]

/-- **Inverse difference.** `P − P' = P (X' − X) P'` for a left inverse `P` of `X` and a
right inverse `P'` of `X'`. -/
theorem inverse_sub {X X' P P' : R} (hP : P * X = 1) (hP' : X' * P' = 1) :
    P - P' = P * (X' - X) * P' := by
  rw [mul_sub, sub_mul, mul_assoc, hP', mul_one, hP, one_mul]

theorem norm_inverse_sub_le {X X' P P' : R} (hP : P * X = 1) (hP' : X' * P' = 1) :
    ‖P - P'‖ ≤ ‖P‖ * ‖X' - X‖ * ‖P'‖ := by
  rw [inverse_sub hP hP']
  exact (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _))

variable [NormedAlgebra ℝ R]

/-- **Resolvent.** `‖(I − λŴ)⁻¹ − (I − λW)⁻¹‖ ≤ |λ| M² ‖Ŵ − W‖`. -/
theorem resolvent_sub_le {W W' P P' : R} {c M : ℝ} (hP : P * (1 - c • W) = 1)
    (hP' : (1 - c • W') * P' = 1) (hM : ‖P‖ ≤ M) (hM' : ‖P'‖ ≤ M) :
    ‖P - P'‖ ≤ |c| * M ^ 2 * ‖W - W'‖ := by
  have hX : (1 - c • W') - (1 - c • W) = c • (W - W') := by rw [smul_sub]; abel
  have h := norm_inverse_sub_le hP hP'
  rw [hX, norm_smul, Real.norm_eq_abs] at h
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  calc ‖P - P'‖ ≤ ‖P‖ * (|c| * ‖W - W'‖) * ‖P'‖ := h
    _ ≤ M * (|c| * ‖W - W'‖) * M := by gcongr
    _ = |c| * M ^ 2 * ‖W - W'‖ := by ring

variable [StarRing R] [NormedStarGroup R]

/-- **Covariance.** With common `λ` and `V`, `‖P V P* − P' V P'*‖ ≤ 2‖V‖ |λ| M³ ‖W − W'‖`. -/
theorem covariance_sub_le {W W' P P' V : R} {c M : ℝ} (hP : P * (1 - c • W) = 1)
    (hP' : (1 - c • W') * P' = 1) (hM : ‖P‖ ≤ M) (hM' : ‖P'‖ ≤ M) :
    ‖P * V * star P - P' * V * star P'‖ ≤ 2 * ‖V‖ * |c| * M ^ 3 * ‖W - W'‖ := by
  have hD := resolvent_sub_le hP hP' hM hM'
  have hsplit : P * V * star P - P' * V * star P' =
      (P - P') * V * star P + P' * V * star (P - P') := by
    rw [star_sub, sub_mul, sub_mul, mul_sub]
    abel
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  have h1 : ‖(P - P') * V * star P‖ ≤ ‖P - P'‖ * ‖V‖ * M := by
    refine (norm_mul_le _ _).trans ?_
    rw [norm_star]
    exact mul_le_mul (norm_mul_le _ _) hM (norm_nonneg _) (by positivity)
  have h2 : ‖P' * V * star (P - P')‖ ≤ M * ‖V‖ * ‖P - P'‖ := by
    refine (norm_mul_le _ _).trans ?_
    rw [norm_star]
    refine mul_le_mul_of_nonneg_right ((norm_mul_le _ _).trans ?_) (norm_nonneg _)
    exact mul_le_mul_of_nonneg_right hM' (norm_nonneg _)
  rw [hsplit]
  calc _ ≤ ‖(P - P') * V * star P‖ + ‖P' * V * star (P - P')‖ := norm_add_le _ _
    _ ≤ ‖P - P'‖ * ‖V‖ * M + M * ‖V‖ * ‖P - P'‖ := add_le_add h1 h2
    _ = 2 * M * ‖V‖ * ‖P - P'‖ := by ring
    _ ≤ 2 * M * ‖V‖ * (|c| * M ^ 2 * ‖W - W'‖) := by gcongr
    _ = 2 * ‖V‖ * |c| * M ^ 3 * ‖W - W'‖ := by ring

/-- Joint perturbation of the spatial operator and innovation covariance. The spatial
operator `H` is the product `λ • W`, so coefficient estimation is included. -/
theorem covariance_joint_sub_le {H H' P P' D D' : R} {M V : ℝ}
    (hP : P * (1 - H) = 1) (hP' : (1 - H') * P' = 1)
    (hM : ‖P‖ ≤ M) (hM' : ‖P'‖ ≤ M) (hV : ‖D‖ ≤ V) :
    ‖P * D * star P - P' * D' * star P'‖ ≤
      2 * V * M ^ 3 * ‖H - H'‖ + M ^ 2 * ‖D - D'‖ := by
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  have hV0 : 0 ≤ V := (norm_nonneg _).trans hV
  have hcommon := covariance_sub_le (c := 1) (W := H) (W' := H')
    (by simpa using hP) (by simpa using hP') hM hM' (V := D)
  simp only [abs_one, mul_one] at hcommon
  have hinnovation : ‖P' * D * star P' - P' * D' * star P'‖ ≤ M ^ 2 * ‖D - D'‖ := by
    rw [← sub_mul, ← mul_sub]
    calc ‖P' * (D - D') * star P'‖ ≤ ‖P'‖ * ‖D - D'‖ * ‖star P'‖ :=
        (norm_mul_le _ _).trans (mul_le_mul_of_nonneg_right (norm_mul_le _ _) (norm_nonneg _))
      _ ≤ M * ‖D - D'‖ * M := by rw [norm_star]; gcongr
      _ = M ^ 2 * ‖D - D'‖ := by ring
  calc ‖P * D * star P - P' * D' * star P'‖ ≤
        ‖P * D * star P - P' * D * star P'‖ + ‖P' * D * star P' - P' * D' * star P'‖ :=
      norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ 2 * ‖D‖ * M ^ 3 * ‖H - H'‖ + M ^ 2 * ‖D - D'‖ := add_le_add hcommon hinnovation
    _ ≤ 2 * V * M ^ 3 * ‖H - H'‖ + M ^ 2 * ‖D - D'‖ := by gcongr

omit [StarRing R] [NormedStarGroup R] in
/-- Separate coefficient error from network error, with the estimated network norm. -/
theorem smul_network_sub_le (W Wh : R) (c ch : ℝ) :
    ‖ch • Wh - c • W‖ ≤ |c| * ‖Wh - W‖ + |ch - c| * ‖Wh‖ := by
  have hsplit : ch • Wh - c • W = c • (Wh - W) + (ch - c) • Wh := by
    rw [smul_sub, sub_smul]; abel
  rw [hsplit]
  simpa only [norm_smul, Real.norm_eq_abs] using norm_add_le (c • (Wh - W)) ((ch - c) • Wh)

end Ring

section Matrices

open Matrix
open scoped Matrix.Norms.L2Operator

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The covariance bound for real matrices in the spectral norm, with
`P = (I − λW)⁻¹`. -/
theorem matrix_covariance_sub_le (W W' V : Matrix n n ℝ) {c M : ℝ}
    (h : IsUnit (1 - c • W).det) (h' : IsUnit (1 - c • W').det)
    (hM : ‖(1 - c • W)⁻¹‖ ≤ M) (hM' : ‖(1 - c • W')⁻¹‖ ≤ M) :
    ‖(1 - c • W)⁻¹ * V * ((1 - c • W)⁻¹)ᵀ - (1 - c • W')⁻¹ * V * ((1 - c • W')⁻¹)ᵀ‖ ≤
      2 * ‖V‖ * |c| * M ^ 3 * ‖W - W'‖ := by
  have := covariance_sub_le (nonsing_inv_mul _ h) (mul_nonsing_inv _ h') hM hM' (V := V)
  simpa [star_eq_conjTranspose, conjTranspose_eq_transpose_of_trivial] using this

/-- Joint matrix perturbation in the Euclidean operator norm. Only the reference
innovation norm is needed; a common bound on both innovations also supplies this premise. -/
theorem matrix_covariance_joint_sub_le (W Wh D Dh : Matrix n n ℝ) {c ch M V : ℝ}
    (h : IsUnit (1 - c • W).det) (hh : IsUnit (1 - ch • Wh).det)
    (hM : ‖(1 - c • W)⁻¹‖ ≤ M) (hMh : ‖(1 - ch • Wh)⁻¹‖ ≤ M) (hV : ‖D‖ ≤ V) :
    ‖(1 - c • W)⁻¹ * D * ((1 - c • W)⁻¹)ᵀ -
      (1 - ch • Wh)⁻¹ * Dh * ((1 - ch • Wh)⁻¹)ᵀ‖ ≤
      2 * V * M ^ 3 * ‖c • W - ch • Wh‖ + M ^ 2 * ‖D - Dh‖ := by
  have ht := covariance_joint_sub_le (nonsing_inv_mul _ h) (mul_nonsing_inv _ hh)
    hM hMh hV (D' := Dh)
  simpa only [star_eq_conjTranspose, conjTranspose_eq_transpose_of_trivial] using ht

/-- Add approximation error against a declared true second moment. -/
theorem matrix_covariance_target_sub_le (W Wh D Dh T : Matrix n n ℝ) {c ch M V ρ : ℝ}
    (h : IsUnit (1 - c • W).det) (hh : IsUnit (1 - ch • Wh).det)
    (hM : ‖(1 - c • W)⁻¹‖ ≤ M) (hMh : ‖(1 - ch • Wh)⁻¹‖ ≤ M) (hV : ‖D‖ ≤ V)
    (hρ : ‖(1 - c • W)⁻¹ * D * ((1 - c • W)⁻¹)ᵀ - T‖ ≤ ρ) :
    ‖(1 - ch • Wh)⁻¹ * Dh * ((1 - ch • Wh)⁻¹)ᵀ - T‖ ≤
      2 * V * M ^ 3 * ‖c • W - ch • Wh‖ + M ^ 2 * ‖D - Dh‖ + ρ := by
  have hb := matrix_covariance_joint_sub_le W Wh D Dh h hh hM hMh hV
  rw [norm_sub_rev] at hb
  exact (norm_sub_le_norm_sub_add_norm_sub _ _ _).trans (add_le_add hb hρ)

end Matrices

section Operators

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- `|⟪T v, v⟫| ≤ ‖T‖ ‖v‖²`. -/
theorem abs_quadratic_le (T : E →L[ℝ] E) (v : E) : |inner ℝ (T v) v| ≤ ‖T‖ * ‖v‖ ^ 2 := by
  calc |inner ℝ (T v) v| ≤ ‖T v‖ * ‖v‖ := abs_real_inner_le_norm _ _
    _ ≤ ‖T‖ * ‖v‖ * ‖v‖ := mul_le_mul_of_nonneg_right (T.le_opNorm v) (norm_nonneg _)
    _ = ‖T‖ * ‖v‖ ^ 2 := by ring

/-- **Loss, quadratic term.** For inverses `Q = Σ⁻¹`, `Q̃ = Σ̃⁻¹`,
`|u'Σ⁻¹u − u'Σ̃⁻¹u| ≤ ‖Q‖ ‖Q̃‖ ‖Σ − Σ̃‖ ‖u‖²`; with eigenvalues at least `a` the gains are
`1/a`. -/
theorem quadratic_inverse_sub_le {S S' Q Q' : E →L[ℝ] E} (hQ : Q * S = 1) (hQ' : S' * Q' = 1)
    (u : E) :
    |inner ℝ (Q u) u - inner ℝ (Q' u) u| ≤ ‖Q‖ * ‖Q'‖ * ‖S - S'‖ * ‖u‖ ^ 2 := by
  have hsub : inner ℝ (Q u) u - inner ℝ (Q' u) u = inner ℝ ((Q - Q') u) u := by
    rw [show (Q - Q') u = Q u - Q' u from rfl, inner_sub_left]
  rw [hsub]
  refine (abs_quadratic_le _ u).trans (mul_le_mul_of_nonneg_right ?_ (by positivity))
  calc ‖Q - Q'‖ ≤ ‖Q‖ * ‖S' - S‖ * ‖Q'‖ := norm_inverse_sub_le hQ hQ'
    _ = ‖Q‖ * ‖Q'‖ * ‖S - S'‖ := by rw [norm_sub_rev]; ring

/-- **Portfolio regret.** If `ŵ` minimises the estimated variance over a feasible set whose
portfolios have `‖w‖ ≤ B`, its true variance exceeds that of any feasible portfolio by at
most `2B²‖Σ̂ − Σ‖`. -/
theorem portfolio_regret (S Sh : E →L[ℝ] E) (K : Set E) {B : ℝ} (hB : ∀ w ∈ K, ‖w‖ ≤ B)
    {wh w : E} (hwh : wh ∈ K) (hw : w ∈ K)
    (hmin : ∀ v ∈ K, inner ℝ (Sh wh) wh ≤ inner ℝ (Sh v) v) :
    inner ℝ (S wh) wh - inner ℝ (S w) w ≤ 2 * B ^ 2 * ‖Sh - S‖ := by
  have hgap : ∀ v ∈ K, |inner ℝ (Sh v) v - inner ℝ (S v) v| ≤ B ^ 2 * ‖Sh - S‖ := by
    intro v hv
    have hsub : inner ℝ (Sh v) v - inner ℝ (S v) v = inner ℝ ((Sh - S) v) v := by
      rw [show (Sh - S) v = Sh v - S v from rfl, inner_sub_left]
    rw [hsub]
    refine (abs_quadratic_le _ v).trans ?_
    rw [mul_comm]
    exact mul_le_mul_of_nonneg_right
      (pow_le_pow_left₀ (norm_nonneg _) (hB v hv) 2) (norm_nonneg _)
  have h1 := abs_le.mp (hgap wh hwh)
  have h2 := abs_le.mp (hgap w hw)
  have h3 := hmin w hw
  linarith [h1.1, h2.2]

end Operators

open scoped Matrix.Norms.L2Operator in
/-- Matrix version of portfolio regret, using Euclidean vectors and the same spectral
matrix norm as the covariance perturbation results. -/
theorem matrix_portfolio_regret {n : Type*} [Fintype n] [DecidableEq n]
    (S Sh : Matrix n n ℝ) (K : Set (EuclideanSpace ℝ n)) {B : ℝ}
    (hB : ∀ w ∈ K, ‖w‖ ≤ B) {wh w : EuclideanSpace ℝ n} (hwh : wh ∈ K) (hw : w ∈ K)
    (hmin : ∀ v ∈ K, inner ℝ (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) Sh wh) wh ≤
      inner ℝ (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) Sh v) v) :
    inner ℝ (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) S wh) wh - inner ℝ (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) S w) w ≤
      2 * B ^ 2 * ‖Sh - S‖ := by
  have ht := portfolio_regret (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) S) (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) Sh) K hB hwh hw hmin
  simpa only [← map_sub, Matrix.l2_opNorm_toEuclideanCLM] using ht

/-- A long-only, fully invested portfolio has Euclidean norm at most one, so `B = 1`. -/
theorem long_only_sq_le {ι : Type*} (s : Finset ι) (w : ι → ℝ) (hw : ∀ i ∈ s, 0 ≤ w i)
    (hsum : ∑ i ∈ s, w i = 1) : ∑ i ∈ s, w i ^ 2 ≤ 1 := by
  calc ∑ i ∈ s, w i ^ 2 ≤ ∑ i ∈ s, w i := Finset.sum_le_sum fun i hi => by
        have h1 : w i ≤ 1 := hsum ▸ Finset.single_le_sum hw hi
        nlinarith [hw i hi]
    _ = 1 := hsum

end FreeFoundations.Stability
