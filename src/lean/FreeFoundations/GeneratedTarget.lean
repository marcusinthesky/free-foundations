import FreeFoundations.Stability
import FreeFoundations.GramDistance

/-! Generated reference exposures: deterministic normal-equation and target errors. -/

namespace FreeFoundations.GeneratedTarget

open Matrix Finset
open scoped Matrix.Norms.L2Operator

variable {k n t : Type*} [Fintype k] [DecidableEq k] [Fintype n] [DecidableEq n]
  [Fintype t] [DecidableEq t]

/-- Least-squares exposures, with reference factors in columns and firms in columns of Y. -/
noncomputable def exposures (F : Matrix t k ℝ) (Y : Matrix t n ℝ) : Matrix k n ℝ :=
  (Fᵀ * F)⁻¹ * (Fᵀ * Y)

/-- Independent Gram and cross-moment errors control generated exposures. -/
theorem normal_equation_error (H Hh : Matrix k k ℝ) (B Bh : Matrix k n ℝ)
    (hH : IsUnit H.det) (hHh : IsUnit Hh.det) {M εH εB : ℝ}
    (hM : ‖H⁻¹‖ ≤ M) (hMh : ‖Hh⁻¹‖ ≤ M)
    (hgram : ‖Hh - H‖ ≤ εH) (hcross : ‖Bh - B‖ ≤ εB) :
    ‖Hh⁻¹ * Bh - H⁻¹ * B‖ ≤ M * εB + M ^ 2 * εH * ‖B‖ := by
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  have hεH : 0 ≤ εH := (norm_nonneg _).trans hgram
  have hεB : 0 ≤ εB := (norm_nonneg _).trans hcross
  have hinv : ‖Hh⁻¹ - H⁻¹‖ ≤ M ^ 2 * εH := by
    have hb := Stability.norm_inverse_sub_le (Matrix.nonsing_inv_mul Hh hHh)
      (Matrix.mul_nonsing_inv H hH)
    rw [norm_sub_rev H Hh] at hb
    calc ‖Hh⁻¹ - H⁻¹‖ ≤ ‖Hh⁻¹‖ * ‖Hh - H‖ * ‖H⁻¹‖ := hb
      _ ≤ M * εH * M := by gcongr
      _ = _ := by ring
  have hsplit : Hh⁻¹ * Bh - H⁻¹ * B = Hh⁻¹ * (Bh - B) + (Hh⁻¹ - H⁻¹) * B := by
    simp only [Matrix.mul_sub, Matrix.sub_mul]
    abel
  rw [hsplit]
  calc _ ≤ ‖Hh⁻¹ * (Bh - B)‖ + ‖(Hh⁻¹ - H⁻¹) * B‖ := norm_add_le _ _
    _ ≤ ‖Hh⁻¹‖ * ‖Bh - B‖ + ‖Hh⁻¹ - H⁻¹‖ * ‖B‖ :=
      add_le_add (Matrix.l2_opNorm_mul _ _) (Matrix.l2_opNorm_mul _ _)
    _ ≤ _ := by gcongr

theorem factor_gram_error (F Fh : Matrix t k ℝ) {e : ℝ} (he : ‖Fh - F‖ ≤ e) :
    ‖Fhᵀ * Fh - Fᵀ * F‖ ≤ (‖Fh‖ + ‖F‖) * e := by
  have hs : Fhᵀ * Fh - Fᵀ * F = Fhᵀ * (Fh - F) + (Fh - F)ᵀ * F := by
    simp only [Matrix.mul_sub, Matrix.sub_mul, Matrix.transpose_sub]
    abel
  have htr (A : Matrix t k ℝ) : ‖Aᵀ‖ = ‖A‖ := by
    simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using Matrix.l2_opNorm_conjTranspose A
  rw [hs]
  calc _ ≤ ‖Fhᵀ * (Fh - F)‖ + ‖(Fh - F)ᵀ * F‖ := norm_add_le _ _
    _ ≤ ‖Fhᵀ‖ * ‖Fh - F‖ + ‖(Fh - F)ᵀ‖ * ‖F‖ :=
      add_le_add (Matrix.l2_opNorm_mul _ _) (Matrix.l2_opNorm_mul _ _)
    _ = (‖Fh‖ + ‖F‖) * ‖Fh - F‖ := by rw [htr, htr]; ring
    _ ≤ _ := mul_le_mul_of_nonneg_left he (by positivity)

theorem cross_moment_error (F Fh : Matrix t k ℝ) (Y Yh : Matrix t n ℝ)
    {eF eY : ℝ} (hF : ‖Fh - F‖ ≤ eF) (hY : ‖Yh - Y‖ ≤ eY) :
    ‖Fhᵀ * Yh - Fᵀ * Y‖ ≤ ‖Fh‖ * eY + eF * ‖Y‖ := by
  have hs : Fhᵀ * Yh - Fᵀ * Y = Fhᵀ * (Yh - Y) + (Fh - F)ᵀ * Y := by
    simp only [Matrix.mul_sub, Matrix.sub_mul, Matrix.transpose_sub]
    abel
  have htr (A : Matrix t k ℝ) : ‖Aᵀ‖ = ‖A‖ := by
    simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using Matrix.l2_opNorm_conjTranspose A
  rw [hs]
  calc _ ≤ ‖Fhᵀ * (Yh - Y)‖ + ‖(Fh - F)ᵀ * Y‖ := norm_add_le _ _
    _ ≤ ‖Fhᵀ‖ * ‖Yh - Y‖ + ‖(Fh - F)ᵀ‖ * ‖Y‖ :=
      add_le_add (Matrix.l2_opNorm_mul _ _) (Matrix.l2_opNorm_mul _ _)
    _ ≤ _ := by rw [htr, htr]; gcongr

variable {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]

omit [Fintype n] [DecidableEq n] [InnerProductSpace ℝ A] in
/-- Readout error and uncertainty of its generated target are separate quantities. -/
theorem generated_readout_error (a target predicted : n → A) {eRead eTarget : ℝ}
    (hr : ∀ i, ‖predicted i - target i‖ ≤ eRead)
    (ht : ∀ i, ‖target i - a i‖ ≤ eTarget) (i : n) :
    ‖predicted i - a i‖ ≤ eRead + eTarget :=
  (norm_sub_le_norm_sub_add_norm_sub _ _ _).trans (add_le_add (hr i) (ht i))

omit [Fintype n] [DecidableEq n] in
/-- Anchored exposure errors control the uncentered Gram target as well as distances. -/
theorem exposure_gram_error (a ah : n → A) {B e : ℝ} (hB : 0 ≤ B) (he : 0 ≤ e)
    (ha : ∀ i, ‖a i‖ ≤ B) (herr : ∀ i, ‖ah i - a i‖ ≤ e) (i j : n) :
    |inner ℝ (ah i) (ah j) - inner ℝ (a i) (a j)| ≤ 2 * B * e + e ^ 2 := by
  have hah : ‖ah j‖ ≤ B + e := by
    calc ‖ah j‖ ≤ ‖a j‖ + ‖ah j - a j‖ := by
          simpa only [add_sub_cancel] using norm_add_le (a j) (ah j - a j)
      _ ≤ _ := add_le_add (ha j) (herr j)
  have hs : inner ℝ (ah i) (ah j) - inner ℝ (a i) (a j) =
      inner ℝ (ah i - a i) (ah j) + inner ℝ (a i) (ah j - a j) := by
    simp only [inner_sub_left, inner_sub_right]
    ring
  rw [hs]
  calc _ ≤ |inner ℝ (ah i - a i) (ah j)| + |inner ℝ (a i) (ah j - a j)| := abs_add_le _ _
    _ ≤ ‖ah i - a i‖ * ‖ah j‖ + ‖a i‖ * ‖ah j - a j‖ :=
      add_le_add (abs_real_inner_le_norm _ _) (abs_real_inner_le_norm _ _)
    _ ≤ e * (B + e) + B * e := by
      gcongr
      · exact herr i
      · exact ha i
      · exact herr j
    _ = _ := by ring

end FreeFoundations.GeneratedTarget
