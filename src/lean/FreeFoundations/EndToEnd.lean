module

public import FreeFoundations.GramDistance
public import FreeFoundations.Kernel
public import FreeFoundations.ScoreStability
public import FreeFoundations.Transfer

@[expose] public section

/-! Composed certificates: economic measurement → network → covariance → decisions. -/

namespace FreeFoundations.EndToEnd

open Matrix Finset
open scoped Matrix.Norms.L2Operator

variable {n : Type*} [Fintype n] [DecidableEq n]

noncomputable def spatial (W : Matrix n n ℝ) (c : ℝ) (D : Matrix n n ℝ) : Matrix n n ℝ :=
  (1 - c • W)⁻¹ * D * ((1 - c • W)⁻¹)ᵀ

/-- Every norm and dimension factor is explicit in the error budget. -/
noncomputable def covarianceError (N : ℕ) (b V M c ec BW eD ρ : ℝ) : ℝ :=
  2 * V * M ^ 3 * (|c| * (Real.sqrt N * Kernel.sensitivity b) + ec * BW) + M ^ 2 * eD + ρ

theorem kernel_spectral_scaled (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ)
    {h hh b : ℝ} (hb : 0 ≤ b)
    (hscaled : ∀ i j, i ≠ j → |dh i j / hh - d i j / h| ≤ b) :
    ‖Kernel.expKernel dh hh - Kernel.expKernel d h‖ ≤
      Real.sqrt (Fintype.card n) * Kernel.sensitivity b := by
  have hr := MatrixBounds.rowSumNorm_le (Kernel.expKernel dh hh - Kernel.expKernel d h)
    (Kernel.sensitivity_nonneg hb) (Kernel.expKernel_row_l1_le_scaled hn d dh hb hscaled)
  exact (MatrixBounds.spectralNorm_le_sqrt_card_mul_rowSumNorm _).trans
    (mul_le_mul_of_nonneg_left hr (Real.sqrt_nonneg _))

theorem kernel_spectral_common (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ)
    {h δ : ℝ} (hh : 0 < h) (hδ : 0 ≤ δ)
    (hd : ∀ i j, i ≠ j → |dh i j - d i j| ≤ δ) :
    ‖Kernel.expKernel dh h - Kernel.expKernel d h‖ ≤
      Real.sqrt (Fintype.card n) * Kernel.sensitivity (δ / h) := by
  apply kernel_spectral_scaled hn d dh (div_nonneg hδ hh.le)
  intro i j hij
  rw [← sub_div, abs_div, abs_of_pos hh]
  exact div_le_div_of_nonneg_right (hd i j hij) hh.le

/-- Row stochasticity gives √N, rather than one, as a general spectral certificate. -/
theorem kernel_spectral_bound (hn : 2 ≤ Fintype.card n) (d : Matrix n n ℝ) (h : ℝ) :
    ‖Kernel.expKernel d h‖ ≤ Real.sqrt (Fintype.card n) := by
  have hr : MatrixBounds.rowSumNorm (Kernel.expKernel d h) ≤ 1 := by
    apply MatrixBounds.rowSumNorm_le _ zero_le_one
    intro i
    simpa only [abs_of_nonneg (Kernel.expKernel_nonneg d h i _)] using
      (Kernel.expKernel_row_sum hn d h i).le
  exact (MatrixBounds.spectralNorm_le_sqrt_card_mul_rowSumNorm _).trans
    (by simpa only [mul_one] using mul_le_mul_of_nonneg_left hr (Real.sqrt_nonneg _))

/-- Principal deterministic result. Statistical modules supply the scaled-distance event. -/
theorem covariance_from_scaled (hn : 2 ≤ Fintype.card n) (d dh D Dh T : Matrix n n ℝ)
    {h hh b c ch M V ec BW eD ρ : ℝ} (hb : 0 ≤ b)
    (hscaled : ∀ i j, i ≠ j → |dh i j / hh - d i j / h| ≤ b)
    (hi : IsUnit (1 - c • Kernel.expKernel d h).det)
    (hih : IsUnit (1 - ch • Kernel.expKernel dh hh).det)
    (hM : ‖(1 - c • Kernel.expKernel d h)⁻¹‖ ≤ M)
    (hMh : ‖(1 - ch • Kernel.expKernel dh hh)⁻¹‖ ≤ M)
    (hV : ‖D‖ ≤ V) (hc : |ch - c| ≤ ec) (hW : ‖Kernel.expKernel dh hh‖ ≤ BW)
    (hD : ‖D - Dh‖ ≤ eD) (hρ : ‖spatial (Kernel.expKernel d h) c D - T‖ ≤ ρ) :
    ‖spatial (Kernel.expKernel dh hh) ch Dh - T‖ ≤
      covarianceError (Fintype.card n) b V M c ec BW eD ρ := by
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  have hV0 : 0 ≤ V := (norm_nonneg _).trans hV
  have hec : 0 ≤ ec := (abs_nonneg _).trans hc
  have hBW : 0 ≤ BW := (norm_nonneg _).trans hW
  have hw := kernel_spectral_scaled hn d dh hb hscaled
  have hp := Stability.smul_network_sub_le (Kernel.expKernel d h) (Kernel.expKernel dh hh) c ch
  have hproduct : ‖c • Kernel.expKernel d h - ch • Kernel.expKernel dh hh‖ ≤
      |c| * (Real.sqrt (Fintype.card n) * Kernel.sensitivity b) + ec * BW := by
    rw [norm_sub_rev]
    exact hp.trans (by gcongr)
  have ht := Stability.matrix_covariance_target_sub_le (Kernel.expKernel d h)
    (Kernel.expKernel dh hh) D Dh T hi hih hM hMh hV hρ
  exact ht.trans (by unfold covarianceError; gcongr)

omit [Fintype n] [DecidableEq n] in
/-- An exposure certificate supplies the common-bandwidth scaled-distance condition. -/
theorem exposure_scaled {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    (a ah : n → A) {e h : ℝ} (he : ∀ i, ‖ah i - a i‖ ≤ e) (hh : 0 < h) (i j : n) :
    |‖ah i - ah j‖ / h - ‖a i - a j‖ / h| ≤ 2 * e / h := by
  rw [← sub_div, abs_div, abs_of_pos hh]
  exact div_le_div_of_nonneg_right (GramDistance.uniform_exposure_distance a ah he i j) hh.le

/-- The alternative anchored-Gram route has no decoder premise. -/
theorem gram_scaled {G Gh : Matrix n n ℝ} (hG : G.PosSemidef) (hGh : Gh.PosSemidef)
    {ε h : ℝ} (hε : 0 ≤ ε) (herror : ∀ i j, |Gh i j - G i j| ≤ ε) (hh : 0 < h) (i j : n) :
    |GramDistance.distance Gh i j / h - GramDistance.distance G i j / h| ≤
      2 * Real.sqrt ε / h := by
  rw [← sub_div, abs_div, abs_of_pos hh]
  exact div_le_div_of_nonneg_right (GramDistance.distance_error hG hGh hε herror i j) hh.le

/-- Financial score consequence of any certified total covariance error. -/
theorem score_of_certificate {S T : Matrix n n ℝ} (hS : S.PosDef) (hT : T.PosDef)
    {m e : ℝ} (hm : 0 < m) (hfloor : (S - m • 1).PosSemidef)
    (herror : ‖S - T‖ ≤ e) (hlocal : e < m) :
    0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤
        Fintype.card n * (e / m) ^ 2 / (2 * (1 - e / m)) :=
  ScoreStability.loss_gap_le_of_norm_sub hS hT hm hfloor herror hlocal


/-- Explicit distances in the declared exposure coordinates. -/
noncomputable def distances {A : Type*} [NormedAddCommGroup A] (a : n → A) : Matrix n n ℝ :=
  fun i j => ‖a i - a j‖

/-- The complete deterministic measurement-to-score theorem. -/
theorem measurement_to_finance {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    (hn : 2 ≤ Fintype.card n) (a ah : n → A) (D Dh T : Matrix n n ℝ)
    {e h c ch M V ec BW eD ρ m : ℝ} (he : 0 ≤ e) (hh : 0 < h)
    (herr : ∀ i, ‖ah i - a i‖ ≤ e)
    (hi : IsUnit (1 - c • Kernel.expKernel (distances a) h).det)
    (hih : IsUnit (1 - ch • Kernel.expKernel (distances ah) h).det)
    (hM : ‖(1 - c • Kernel.expKernel (distances a) h)⁻¹‖ ≤ M)
    (hMh : ‖(1 - ch • Kernel.expKernel (distances ah) h)⁻¹‖ ≤ M)
    (hV : ‖D‖ ≤ V) (hc : |ch - c| ≤ ec) (hW : ‖Kernel.expKernel (distances ah) h‖ ≤ BW)
    (hD : ‖D - Dh‖ ≤ eD) (hρ : ‖spatial (Kernel.expKernel (distances a) h) c D - T‖ ≤ ρ)
    (hS : (spatial (Kernel.expKernel (distances ah) h) ch Dh).PosDef) (hT : T.PosDef)
    (hm : 0 < m) (hfloor : (spatial (Kernel.expKernel (distances ah) h) ch Dh - m • 1).PosSemidef)
    (hlocal : covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ < m) :
    let S := spatial (Kernel.expKernel (distances ah) h) ch Dh
    let E := covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ
    ‖S - T‖ ≤ E ∧ 0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤ Fintype.card n * (E / m) ^ 2 / (2 * (1 - E / m)) := by
  have hb := covariance_from_scaled hn (distances a) (distances ah) D Dh T
    (by positivity : 0 ≤ 2 * e / h) (fun i j _ => exposure_scaled a ah herr hh i j)
    hi hih hM hMh hV hc hW hD hρ
  exact ⟨hb, score_of_certificate hS hT hm hfloor hb hlocal⟩

omit [Fintype n] [DecidableEq n] in
/-- Prediction, alignment and fitted-task-readout errors supply a uniform panel certificate. -/
theorem task_exposure_certificate {A T : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    [NormedAddCommGroup T] [InnerProductSpace ℝ T]
    {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L)
    (hκ : 0 < κ) (fitted : T → A) (a : n → A) (v pred : n → T)
    {ε ν εL B : ℝ} (hεL : 0 ≤ εL) (hfit : ∀ y, ‖fitted y - L y‖ ≤ εL * ‖y‖)
    (hp : ∀ i, ‖pred i - (C (a i) + v i)‖ ≤ ε) (hv : ∀ i, ‖v i‖ ≤ ν)
    (hB : ∀ i, ‖pred i‖ ≤ B) :
    ∀ i, ‖fitted (pred i) - a i‖ ≤ (ε + ν) / κ + εL * B :=
  fun i => Transfer.fitted_readout_error hL hκ fitted hfit hεL (a i) (v i) (pred i)
    (hp i) (hv i) (hB i)

omit [DecidableEq n] in
/-- Fixed-panel RMS reaches kernel sensitivity only after its √N conversion. -/
theorem empirical_rms_scaled {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    (a ah : n → A) {B h : ℝ} (hB : 0 ≤ B) (hh : 0 < h)
    (herr : ∑ i, ‖ah i - a i‖ ^ 2 ≤ Fintype.card n * B ^ 2) (i j : n) :
    |distances ah i j / h - distances a i j / h| ≤
      2 * (Real.sqrt (Fintype.card n) * B) / h := by
  apply exposure_scaled a ah _ hh i j
  intro k
  simpa only [abs_of_nonneg (norm_nonneg _)] using
    GramDistance.empirical_rms_to_uniform (fun k => ‖ah k - a k‖) hB herr k

/-- One compiled theorem from task/readout errors to covariance and score regret. -/
theorem tasks_to_finance {A U : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    [NormedAddCommGroup U] [InnerProductSpace ℝ U]
    (hn : 2 ≤ Fintype.card n) {C : A →ₗ[ℝ] U} {κ : ℝ} {L : U →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ) (fitted : U → A)
    (a : n → A) (v pred : n → U) {ε ν εL B : ℝ} (hεL : 0 ≤ εL)
    (hfit : ∀ y, ‖fitted y - L y‖ ≤ εL * ‖y‖)
    (hp : ∀ i, ‖pred i - (C (a i) + v i)‖ ≤ ε) (hv : ∀ i, ‖v i‖ ≤ ν)
    (hB : ∀ i, ‖pred i‖ ≤ B) (D Dh T : Matrix n n ℝ)
    {e h c ch M V ec BW eD ρ m : ℝ} (he : 0 ≤ e) (hh : 0 < h)
    (heq : e = (ε + ν) / κ + εL * B)
    (hi : IsUnit (1 - c • Kernel.expKernel (distances a) h).det)
    (hih : IsUnit (1 - ch • Kernel.expKernel (distances (fun i => fitted (pred i))) h).det)
    (hM : ‖(1 - c • Kernel.expKernel (distances a) h)⁻¹‖ ≤ M)
    (hMh : ‖(1 - ch • Kernel.expKernel (distances (fun i => fitted (pred i))) h)⁻¹‖ ≤ M)
    (hV : ‖D‖ ≤ V) (hc : |ch - c| ≤ ec) (hW : ‖Kernel.expKernel (distances (fun i => fitted (pred i))) h‖ ≤ BW)
    (hD : ‖D - Dh‖ ≤ eD) (hρ : ‖spatial (Kernel.expKernel (distances a) h) c D - T‖ ≤ ρ)
    (hS : (spatial (Kernel.expKernel (distances (fun i => fitted (pred i))) h) ch Dh).PosDef) (hT : T.PosDef)
    (hm : 0 < m) (hfloor : (spatial (Kernel.expKernel (distances (fun i => fitted (pred i))) h) ch Dh - m • 1).PosSemidef)
    (hlocal : covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ < m) :
    let S := spatial (Kernel.expKernel (distances (fun i => fitted (pred i))) h) ch Dh
    let E := covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ
    ‖S - T‖ ≤ E ∧ 0 ≤ Score.loss S T - Score.loss T T ∧
      Score.loss S T - Score.loss T T ≤ Fintype.card n * (E / m) ^ 2 / (2 * (1 - E / m)) := by
  have herr : ∀ i, ‖fitted (pred i) - a i‖ ≤ e := by
    rw [heq]
    exact task_exposure_certificate hL hκ fitted a v pred hεL hfit hp hv hB
  exact measurement_to_finance hn a (fun i => fitted (pred i)) D Dh T he hh herr
    hi hih hM hMh hV hc hW hD hρ hS hT hm hfloor hlocal


/-- A shared conventional factor component cancels in the covariance error. -/
theorem common_component_error (F S T : Matrix n n ℝ) :
    ‖(F + S) - (F + T)‖ = ‖S - T‖ := by
  congr 1
  abel

/-- Full-forecast scores use the full covariance floor, with the same residual error. -/
theorem full_score_of_certificate (F S T : Matrix n n ℝ)
    (hS : (F + S).PosDef) (hT : (F + T).PosDef) {m e : ℝ}
    (hm : 0 < m) (hfloor : (F + S - m • 1).PosSemidef)
    (herror : ‖S - T‖ ≤ e) (hlocal : e < m) :
    0 ≤ Score.loss (F + S) (F + T) - Score.loss (F + T) (F + T) ∧
      Score.loss (F + S) (F + T) - Score.loss (F + T) (F + T) ≤
        Fintype.card n * (e / m) ^ 2 / (2 * (1 - e / m)) := by
  apply score_of_certificate hS hT hm hfloor _ hlocal
  simpa only [common_component_error] using herror

end FreeFoundations.EndToEnd
