module

public import FreeFoundations.Recovery
public import FreeFoundations.Kernel
public import FreeFoundations.Stability
public import FreeFoundations.MatrixBounds
public import FreeFoundations.EndToEnd

@[expose] public section

/-!
# A conditional exposure-to-covariance bound

The covariance norm is the Euclidean operator (spectral) norm. The kernel result uses
the maximum absolute row sum; `spectralNorm_le_sqrt_card_mul_rowNorm` supplies the explicit
`√N` conversion. These compatibility wrappers reuse `MatrixBounds`; the spatial map reuses `EndToEnd`.

All forecasts in a comparison share bandwidth, spatial coefficient and innovation covariance.
The result controls distance measurement error within this fixed spatial construction. It
neither bounds spatial misspecification nor proves that estimated historical proxies equal
latent exposures, and makes no assertion about a fitted parameter's sampling distribution.
-/

namespace FreeFoundations.Pipeline

open Finset Matrix

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The spectral norm, defined through the operator on Euclidean space. -/
noncomputable def spectralNorm (A : Matrix n n ℝ) : ℝ :=
  MatrixBounds.spectralNorm A

/-- The maximum absolute row sum, the `ℓ∞` operator norm. -/
noncomputable def rowNorm (A : Matrix n n ℝ) : ℝ :=
  MatrixBounds.rowSumNorm A

omit [DecidableEq n] in
theorem rowNorm_nonneg (A : Matrix n n ℝ) : 0 ≤ rowNorm A := MatrixBounds.rowSumNorm_nonneg A

omit [DecidableEq n] in
theorem row_sum_le_rowNorm (A : Matrix n n ℝ) (i : n) :
    ∑ j, |A i j| ≤ rowNorm A := by
  exact MatrixBounds.row_le_rowSumNorm A i

/-- Reuse the canonical matrix-norm comparison, valid without network symmetry. -/
theorem spectralNorm_le_sqrt_card_mul_rowNorm (A : Matrix n n ℝ) :
    spectralNorm A ≤ Real.sqrt (Fintype.card n) * rowNorm A :=
  MatrixBounds.spectralNorm_le_sqrt_card_mul_rowSumNorm A

attribute [local instance] Matrix.linftyOpSeminormedAddCommGroup in
/-- The existing kernel theorem, with its row norm made explicit. -/
theorem expKernel_rowNorm_le (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ) {h δ : ℝ}
    (hh : 0 < h) (hδ : ∀ i j, i ≠ j → |dh i j - d i j| ≤ δ) :
    rowNorm (Kernel.expKernel dh h - Kernel.expKernel d h) ≤
      min 2 (Real.exp (2 * δ / h) - 1) := by
  simpa only [rowNorm, MatrixBounds.rowSumNorm, Matrix.linfty_opNorm_def] using
    Kernel.expKernel_linfty_le hn d dh hh hδ

variable {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]

/-- Distances in one shared, risk-scaled exposure coordinate system. -/
noncomputable def exposureDistances (a : n → A) : Matrix n n ℝ :=
  EndToEnd.distances a

/-- The exponential neighbor network constructed from exposures. -/
noncomputable def exposureNetwork (a : n → A) (h : ℝ) : Matrix n n ℝ :=
  Kernel.expKernel (exposureDistances a) h

/-- The spatial residual covariance with common innovation covariance `D`. -/
noncomputable def spatialCovariance (W D : Matrix n n ℝ) (c : ℝ) : Matrix n n ℝ :=
  EndToEnd.spatial W c D

omit [InnerProductSpace ℝ A] in
/-- Uniform exposure error `r` produces the stated spectral network bound. -/
theorem exposureNetwork_error (hn : 2 ≤ Fintype.card n) (a ah : n → A) {h r : ℝ}
    (hh : 0 < h) (hr : ∀ i, ‖ah i - a i‖ ≤ r) :
    spectralNorm (exposureNetwork ah h - exposureNetwork a h) ≤
      Real.sqrt (Fintype.card n) * min 2 (Real.exp (4 * r / h) - 1) := by
  have hd : ∀ i j, i ≠ j →
      |exposureDistances ah i j - exposureDistances a i j| ≤ 2 * r := by
    intro i j _
    exact (Recovery.distance_error (ah i) (a i) (ah j) (a j)).trans (by linarith [hr i, hr j])
  have hk := expKernel_rowNorm_le hn (exposureDistances a) (exposureDistances ah) hh hd
  calc
    _ ≤ Real.sqrt (Fintype.card n) * rowNorm (exposureNetwork ah h - exposureNetwork a h) :=
      spectralNorm_le_sqrt_card_mul_rowNorm _
    _ ≤ _ := by
      have hfour : 2 * (2 * r) / h = 4 * r / h := by ring
      simpa only [exposureNetwork, hfour] using
        mul_le_mul_of_nonneg_left hk (Real.sqrt_nonneg _)

open scoped Matrix.Norms.L2Operator

/-- The norm wrapper agrees with the explicitly selected spectral matrix instance. -/
theorem spectralNorm_eq (B : Matrix n n ℝ) : spectralNorm B = ‖B‖ :=
  MatrixBounds.spectralNorm_eq B

omit [InnerProductSpace ℝ A] in
/-- **Conditional pipeline.** No estimated scales or coefficients change in the comparison.
Positive diagonal innovations give the economic covariance interpretation; perturbation of a
general common matrix obeys the same algebraic bound. -/
theorem exposure_covariance_error (hn : 2 ≤ Fintype.card n) (a ah : n → A)
    (d : n → ℝ) (_hd : ∀ i, 0 < d i) {h r c M : ℝ} (hh : 0 < h)
    (hr : ∀ i, ‖ah i - a i‖ ≤ r)
    (hinv : IsUnit (1 - c • exposureNetwork a h).det)
    (hinvh : IsUnit (1 - c • exposureNetwork ah h).det)
    (hM : spectralNorm ((1 - c • exposureNetwork a h)⁻¹) ≤ M)
    (hMh : spectralNorm ((1 - c • exposureNetwork ah h)⁻¹) ≤ M) :
    spectralNorm (spatialCovariance (exposureNetwork ah h) (diagonal d) c -
      spatialCovariance (exposureNetwork a h) (diagonal d) c) ≤
      2 * spectralNorm (diagonal d) * |c| * M ^ 3 * Real.sqrt (Fintype.card n) *
        min 2 (Real.exp (4 * r / h) - 1) := by
  have hM0 : 0 ≤ M := (norm_nonneg _).trans (by simpa only [spectralNorm_eq] using hM)
  have hs := Stability.matrix_covariance_sub_le (exposureNetwork ah h) (exposureNetwork a h)
    (diagonal d) hinvh hinv (by simpa only [spectralNorm_eq] using hMh)
    (by simpa only [spectralNorm_eq] using hM)
  have hnw := exposureNetwork_error hn a ah hh hr
  rw [spectralNorm_eq] at hnw
  calc
    _ ≤ 2 * ‖diagonal d‖ * |c| * M ^ 3 * ‖exposureNetwork ah h - exposureNetwork a h‖ := by
      simpa only [spectralNorm_eq, spatialCovariance, EndToEnd.spatial] using hs
    _ ≤ _ := by
      rw [spectralNorm_eq]
      calc
        _ ≤ (2 * ‖diagonal d‖ * |c| * M ^ 3) *
            (Real.sqrt (Fintype.card n) * min 2 (Real.exp (4 * r / h) - 1)) :=
          mul_le_mul_of_nonneg_left hnw (by positivity)
        _ = _ := by ring

omit [InnerProductSpace ℝ A] in
/-- Prediction error against a proxy and proxy error against the latent exposure add before
the kernel is constructed. Both errors must be uniform over the same finite panel. -/
theorem proxy_covariance_error (hn : 2 ≤ Fintype.card n) (a ap ah : n → A)
    (d : n → ℝ) (hd : ∀ i, 0 < d i) {h ε η c M : ℝ} (hh : 0 < h)
    (hpred : ∀ i, ‖ah i - ap i‖ ≤ ε) (hproxy : ∀ i, ‖ap i - a i‖ ≤ η)
    (hinv : IsUnit (1 - c • exposureNetwork a h).det)
    (hinvh : IsUnit (1 - c • exposureNetwork ah h).det)
    (hM : spectralNorm ((1 - c • exposureNetwork a h)⁻¹) ≤ M)
    (hMh : spectralNorm ((1 - c • exposureNetwork ah h)⁻¹) ≤ M) :
    spectralNorm (spatialCovariance (exposureNetwork ah h) (diagonal d) c -
      spatialCovariance (exposureNetwork a h) (diagonal d) c) ≤
      2 * spectralNorm (diagonal d) * |c| * M ^ 3 * Real.sqrt (Fintype.card n) *
        min 2 (Real.exp (4 * (ε + η) / h) - 1) := by
  apply exposure_covariance_error hn a ah d hd hh _ hinv hinvh hM hMh
  intro i
  calc
    ‖ah i - a i‖ ≤ ‖ah i - ap i‖ + ‖ap i - a i‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ ε + η := add_le_add (hpred i) (hproxy i)

omit [InnerProductSpace ℝ A] [DecidableEq n] in
/-- A finite panel's sum of squared errors gives a uniform bound. This deterministic
conversion imposes no independence assumption and does not give a population rate. -/
theorem uniform_error_le_sqrt_sum (a ah : n → A) (i : n) :
    ‖ah i - a i‖ ≤ Real.sqrt (∑ j, ‖ah j - a j‖ ^ 2) := by
  apply Real.le_sqrt_of_sq_le
  exact single_le_sum (fun j _ => sq_nonneg ‖ah j - a j‖) (mem_univ i)

omit [InnerProductSpace ℝ A] in
/-- The same fixed-construction bound expressed using the realized finite-panel sum. -/
theorem covariance_error_of_sum_sq (hn : 2 ≤ Fintype.card n) (a ah : n → A)
    (d : n → ℝ) (hd : ∀ i, 0 < d i) {h c M : ℝ} (hh : 0 < h)
    (hinv : IsUnit (1 - c • exposureNetwork a h).det)
    (hinvh : IsUnit (1 - c • exposureNetwork ah h).det)
    (hM : spectralNorm ((1 - c • exposureNetwork a h)⁻¹) ≤ M)
    (hMh : spectralNorm ((1 - c • exposureNetwork ah h)⁻¹) ≤ M) :
    spectralNorm (spatialCovariance (exposureNetwork ah h) (diagonal d) c -
      spatialCovariance (exposureNetwork a h) (diagonal d) c) ≤
      2 * spectralNorm (diagonal d) * |c| * M ^ 3 * Real.sqrt (Fintype.card n) *
        min 2 (Real.exp (4 * Real.sqrt (∑ j, ‖ah j - a j‖ ^ 2) / h) - 1) :=
  exposure_covariance_error hn a ah d hd hh (uniform_error_le_sqrt_sum a ah)
    hinv hinvh hM hMh

/-- Realized finite-panel exposure mean squared error; this is not population risk. -/
noncomputable def panelMeanSqError (a ah : n → A) : ℝ :=
  (∑ j, ‖ah j - a j‖ ^ 2) / Fintype.card n

omit [InnerProductSpace ℝ A] [DecidableEq n] in
/-- The uniform bound from a realized mean squared error is `√(N * MSE)`. It can grow
with panel size; an average risk bound must not silently be substituted for uniform error. -/
theorem sqrt_sum_eq_sqrt_card_mul_mean (hn : 0 < Fintype.card n) (a ah : n → A) :
    Real.sqrt (∑ j, ‖ah j - a j‖ ^ 2) =
      Real.sqrt ((Fintype.card n : ℝ) * panelMeanSqError a ah) := by
  unfold panelMeanSqError
  rw [mul_div_cancel₀ _ (show (Fintype.card n : ℝ) ≠ 0 by exact_mod_cast hn.ne')]

omit [InnerProductSpace ℝ A] in
/-- Check at zero exposure error: the conditional bound reduces to zero. -/
theorem zero_exposure_error (hn : 2 ≤ Fintype.card n) (a ah : n → A)
    (d : n → ℝ) (hd : ∀ i, 0 < d i) {h c M : ℝ} (hh : 0 < h)
    (hr : ∀ i, ‖ah i - a i‖ ≤ 0)
    (hinv : IsUnit (1 - c • exposureNetwork a h).det)
    (hinvh : IsUnit (1 - c • exposureNetwork ah h).det)
    (hM : spectralNorm ((1 - c • exposureNetwork a h)⁻¹) ≤ M)
    (hMh : spectralNorm ((1 - c • exposureNetwork ah h)⁻¹) ≤ M) :
    spectralNorm (spatialCovariance (exposureNetwork ah h) (diagonal d) c -
      spatialCovariance (exposureNetwork a h) (diagonal d) c) ≤ 0 := by
  simpa using exposure_covariance_error hn a ah d hd hh hr hinv hinvh hM hMh

omit [InnerProductSpace ℝ A] in
/-- Check at zero spatial coefficient: both forecasts equal the shared innovations. -/
theorem zero_spatial_coefficient (a ah : n → A) (D : Matrix n n ℝ) (h : ℝ) :
    spectralNorm (spatialCovariance (exposureNetwork ah h) D 0 -
      spatialCovariance (exposureNetwork a h) D 0) = 0 := by
  simp [spatialCovariance, EndToEnd.spatial, spectralNorm, MatrixBounds.spectralNorm]

end FreeFoundations.Pipeline
