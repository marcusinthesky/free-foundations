import FreeFoundations.Measurement
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.MeasureTheory.Function.LpSeminorm.Basic
import Mathlib.MeasureTheory.Measure.Decomposition.RadonNikodym

/-!
# Transfer of a declared economic measurement

Finite weighted RMS bounds are deterministic: the weights may be source and target
probabilities, but no sampling or independence claim is implicit. The task map and
economic metric are held fixed. The fitted-readout bound acts on task statistics;
an arbitrary hidden-state decoder instead needs its own measurement certificate.
-/

noncomputable section

namespace FreeFoundations.Transfer

open WithLp

variable {ι E : Type*} [Fintype ι] [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Square-root weighting puts the finite weighted RMS in an explicit `L²` product. -/
def weightedEmbed (p : ι → ℝ) (f : ι → E) : PiLp 2 (fun _ : ι => E) :=
  toLp 2 fun i => Real.sqrt (p i) • f i

/-- Weighted root mean square; probability weights give the usual RMS convention. -/
def rms (p : ι → ℝ) (f : ι → E) : ℝ := ‖weightedEmbed p f‖

theorem rms_nonneg (p : ι → ℝ) (f : ι → E) : 0 ≤ rms p f := norm_nonneg _

theorem rms_sq (p : ι → ℝ) (hp : ∀ i, 0 ≤ p i) (f : ι → E) :
    rms p f ^ 2 = ∑ i, p i * ‖f i‖ ^ 2 := by
  rw [rms, PiLp.norm_sq_eq_of_L2]
  apply Finset.sum_congr rfl
  intro i _
  simp only [weightedEmbed, PiLp.toLp_apply, norm_smul, Real.norm_eq_abs,
    abs_of_nonneg (Real.sqrt_nonneg _), mul_pow, Real.sq_sqrt (hp i)]

theorem rms_add_le (p : ι → ℝ) (f g : ι → E) :
    rms p (fun i => f i + g i) ≤ rms p f + rms p g := by
  have he : weightedEmbed p (fun i => f i + g i) = weightedEmbed p f + weightedEmbed p g := by
    ext i
    simp [weightedEmbed, smul_add]
  unfold rms
  rw [he]
  exact norm_add_le _ _

/-- A pointwise gain bound passes to finite weighted RMS. -/
theorem rms_mono {p : ι → ℝ} (hp : ∀ i, 0 ≤ p i) {f g : ι → E}
    (hfg : ∀ i, ‖f i‖ ≤ ‖g i‖) : rms p f ≤ rms p g := by
  have hs : rms p f ^ 2 ≤ rms p g ^ 2 := by
    rw [rms_sq p hp, rms_sq p hp]
    exact Finset.sum_le_sum fun i _ => mul_le_mul_of_nonneg_left
      (pow_le_pow_left₀ (norm_nonneg _) (hfg i) 2) (hp i)
  nlinarith [rms_nonneg p f, rms_nonneg p g]

theorem rms_const_smul (p : ι → ℝ) (c : ℝ) (f : ι → E) :
    rms p (fun i => c • f i) = |c| * rms p f := by
  have he : weightedEmbed p (fun i => c • f i) = c • weightedEmbed p f := by
    ext i
    change Real.sqrt (p i) • (c • f i) = c • (Real.sqrt (p i) • f i)
    exact smul_comm _ _ _
  unfold rms
  rw [he, norm_smul, Real.norm_eq_abs]

/-- Bounded density ratio transports RMS with factor `sqrt ω`. -/
theorem change_of_weights {p q : ι → ℝ} (hp : ∀ i, 0 ≤ p i) (hq : ∀ i, 0 ≤ q i)
    {ω : ℝ} (hω : 0 ≤ ω) (hqp : ∀ i, q i ≤ ω * p i) (f : ι → E) :
    rms q f ≤ Real.sqrt ω * rms p f := by
  have hs : rms q f ^ 2 ≤ ω * rms p f ^ 2 := by
    rw [rms_sq q hq, rms_sq p hp, Finset.mul_sum]
    exact Finset.sum_le_sum fun i _ => by
      simpa [mul_assoc] using mul_le_mul_of_nonneg_right (hqp i) (sq_nonneg ‖f i‖)
  have he : (Real.sqrt ω * rms p f) ^ 2 = ω * rms p f ^ 2 := by
    rw [mul_pow, Real.sq_sqrt hω]
  nlinarith [rms_nonneg q f, rms_nonneg p f, Real.sqrt_nonneg ω,
    mul_nonneg (Real.sqrt_nonneg ω) (rms_nonneg p f)]

/-- Source prediction error and target conditional-mean drift are separate terms. -/
theorem task_transfer {p q : ι → ℝ} (hp : ∀ i, 0 ≤ p i) (hq : ∀ i, 0 ≤ q i)
    {ω : ℝ} (hω : 0 ≤ ω) (hqp : ∀ i, q i ≤ ω * p i)
    (pred source target : ι → E) :
    rms q (fun i => pred i - target i) ≤
      Real.sqrt ω * rms p (fun i => pred i - source i) +
        rms q (fun i => source i - target i) := by
  have he : (fun i => pred i - target i) =
      (fun i => (pred i - source i) + (source i - target i)) := by
    funext i
    abel
  rw [he]
  exact (rms_add_le q _ _).trans (add_le_add
    (change_of_weights hp hq hω hqp _) le_rfl)

section Recovery

variable {A T : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
  [NormedAddCommGroup T] [InnerProductSpace ℝ T]

/-- A declared decoder's gain passes to finite RMS without any sample independence. -/
theorem decoder_rms {p : ι → ℝ} (hp : ∀ i, 0 ≤ p i)
    {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ) (f : ι → T) :
    rms p (fun i => L (f i)) ≤ rms p f / κ := by
  have hs : κ ^ 2 * rms p (fun i => L (f i)) ^ 2 ≤ rms p f ^ 2 := by
    rw [rms_sq p hp, rms_sq p hp, Finset.mul_sum]
    apply Finset.sum_le_sum
    intro i _
    have h := hL.bound (f i)
    have hsq := pow_le_pow_left₀ (mul_nonneg hκ.le (norm_nonneg _)) h 2
    nlinarith [mul_le_mul_of_nonneg_left hsq (hp i)]
  apply (le_div_iff₀ hκ).mpr
  nlinarith [rms_nonneg p (fun i => L (f i)), rms_nonneg p f]

/-- Finite RMS exposure recovery with task mismatch. -/
theorem recovery_rms {q : ι → ℝ} (hq : ∀ i, 0 ≤ q i)
    {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : ι → A) (v pred : ι → T) :
    rms q (fun i => L (pred i) - a i) ≤
      (rms q (fun i => pred i - (C (a i) + v i)) + rms q v) / κ := by
  have he : (fun i => L (pred i) - a i) =
      (fun i => L ((pred i - (C (a i) + v i)) + v i)) := by
    funext i
    simp [map_sub, map_add, hL.left_inv]
    abel
  rw [he]
  exact (decoder_rms hq hL hκ _).trans
    (div_le_div_of_nonneg_right (rms_add_le q _ _) hκ.le)

/-- Source-to-target recovery separates overlap, drift and economic alignment. -/
theorem source_target_recovery {p q : ι → ℝ} (hp : ∀ i, 0 ≤ p i) (hq : ∀ i, 0 ≤ q i)
    {ω : ℝ} (hω : 0 ≤ ω) (hqp : ∀ i, q i ≤ ω * p i)
    {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : ι → A) (v pred source : ι → T) :
    rms q (fun i => L (pred i) - a i) ≤
      (Real.sqrt ω * rms p (fun i => pred i - source i) +
        rms q (fun i => source i - (C (a i) + v i)) + rms q v) / κ := by
  exact (recovery_rms hq hL hκ a v pred).trans
    (div_le_div_of_nonneg_right (add_le_add
      (task_transfer hp hq hω hqp pred source (fun i => C (a i) + v i)) le_rfl) hκ.le)

/-- Fitted maps on the task-statistic space require a separate estimation certificate. -/
theorem fitted_readout_error {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ) (fitted : T → A)
    {εL B ε ν : ℝ} (hfit : ∀ y, ‖fitted y - L y‖ ≤ εL * ‖y‖)
    (hεL : 0 ≤ εL) (a : A) (v pred : T)
    (hp : ‖pred - (C a + v)‖ ≤ ε) (hv : ‖v‖ ≤ ν) (hB : ‖pred‖ ≤ B) :
    ‖fitted pred - a‖ ≤ (ε + ν) / κ + εL * B := by
  have hr := Recovery.exposure_error_mismatch hL hκ.le a v pred
  have he : fitted pred - a = (fitted pred - L pred) + (L pred - a) := by abel
  rw [he]
  apply (norm_add_le _ _).trans
  have hd : ‖L pred - a‖ ≤ (ε + ν) / κ := by
    apply (le_div_iff₀ hκ).mpr
    nlinarith
  have hf := (hfit pred).trans (mul_le_mul_of_nonneg_left hB hεL)
  linarith

end Recovery

section Measures

open MeasureTheory
open scoped ENNReal

variable {Ω : Type*} [MeasurableSpace Ω]

omit [NormedSpace ℝ E] in
/-- General-measure change of measure under domination. `eLpNorm` states explicitly
which measure is used and remains meaningful before finiteness is discharged. -/
theorem measure_change {P Q : Measure Ω} {ω : ℝ} (hω : 0 ≤ ω)
    (hQP : Q ≤ ENNReal.ofReal ω • P) (f : Ω → E) :
    eLpNorm f 2 Q ≤ ENNReal.ofReal (Real.sqrt ω) * eLpNorm f 2 P := by
  apply (eLpNorm_mono_measure f hQP).trans_eq
  rw [eLpNorm_smul_measure_of_ne_top (by norm_num)]
  congr 1
  rw [Real.sqrt_eq_rpow, ENNReal.ofReal_rpow_of_nonneg hω (by norm_num)]
  norm_num

omit [NormedSpace ℝ E] in
/-- A bounded density supplies the measure-domination contract. -/
theorem density_change (P : Measure Ω) (density : Ω → ENNReal) {ω : ℝ}
    (hω : 0 ≤ ω) (hd : ∀ᵐ x ∂P, density x ≤ ENNReal.ofReal ω) (f : Ω → E) :
    eLpNorm f 2 (P.withDensity density) ≤
      ENNReal.ofReal (Real.sqrt ω) * eLpNorm f 2 P := by
  apply measure_change hω _ f
  simpa only [withDensity_const] using withDensity_mono hd

omit [NormedSpace ℝ E] in
/-- Radon–Nikodym convenience wrapper. Absolute continuity and the bounded density
are hypotheses; this theorem does not estimate overlap in a financial sample. -/
theorem rnDeriv_change {P Q : Measure Ω} [Q.HaveLebesgueDecomposition P]
    (hAC : Q ≪ P) {ω : ℝ} (hω : 0 ≤ ω)
    (hd : ∀ᵐ x ∂P, Q.rnDeriv P x ≤ ENNReal.ofReal ω) (f : Ω → E) :
    eLpNorm f 2 Q ≤ ENNReal.ofReal (Real.sqrt ω) * eLpNorm f 2 P := by
  rw [← Measure.withDensity_rnDeriv_eq Q P hAC]
  exact density_change P _ hω hd f

omit [NormedSpace ℝ E] in
/-- General-measure task transfer. Measurability is required for the target-law
Minkowski step; source and drift norms retain their distinct measures. -/
theorem measure_task_transfer {P Q : Measure Ω} {ω : ℝ} (hω : 0 ≤ ω)
    (hQP : Q ≤ ENNReal.ofReal ω • P) (pred source target : Ω → E)
    (hpred : AEStronglyMeasurable (fun x => pred x - source x) Q)
    (hdrift : AEStronglyMeasurable (fun x => source x - target x) Q) :
    eLpNorm (fun x => pred x - target x) 2 Q ≤
      ENNReal.ofReal (Real.sqrt ω) * eLpNorm (fun x => pred x - source x) 2 P +
        eLpNorm (fun x => source x - target x) 2 Q := by
  have he : (fun x => pred x - target x) =
      ((fun x => pred x - source x) + fun x => source x - target x) := by
    funext x
    simp only [Pi.add_apply]
    abel
  rw [he]
  exact (eLpNorm_add_le hpred hdrift (by norm_num)).trans
    (add_le_add (measure_change hω hQP _) le_rfl)

variable {A T : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
  [NormedAddCommGroup T] [InnerProductSpace ℝ T]

/-- Decoder gain in population RMS, keeping the measure explicit. -/
theorem measure_decoder (Q : Measure Ω) {C : A →ₗ[ℝ] T} {κ : ℝ}
    {L : T →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ) (f : Ω → T) :
    eLpNorm (fun x => L (f x)) 2 Q ≤ ENNReal.ofReal κ⁻¹ * eLpNorm f 2 Q := by
  apply eLpNorm_le_mul_eLpNorm_of_ae_le_mul _ 2
  apply Filter.Eventually.of_forall
  intro x
  rw [inv_mul_eq_div, le_div_iff₀ hκ, mul_comm]
  exact hL.bound _

/-- Population RMS exposure recovery, with task error and economic mismatch separate. -/
theorem measure_recovery (Q : Measure Ω) {C : A →ₗ[ℝ] T} {κ : ℝ}
    {L : T →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : Ω → A) (v pred : Ω → T)
    (hpred : AEStronglyMeasurable (fun x => pred x - (C (a x) + v x)) Q)
    (hv : AEStronglyMeasurable v Q) :
    eLpNorm (fun x => L (pred x) - a x) 2 Q ≤
      ENNReal.ofReal κ⁻¹ *
        (eLpNorm (fun x => pred x - (C (a x) + v x)) 2 Q + eLpNorm v 2 Q) := by
  have he : (fun x => L (pred x) - a x) =
      (fun x => L (((fun x => pred x - (C (a x) + v x)) + v) x)) := by
    funext x
    simp only [Pi.add_apply, map_add, map_sub, hL.left_inv]
    abel
  rw [he]
  exact (measure_decoder Q hL hκ _).trans
    (mul_le_mul_right (eLpNorm_add_le hpred hv (by norm_num)) _)

/-- Complete measure-level source-to-target recovery: overlap, conditional drift,
and task/economic mismatch are explicit, with no population-to-panel substitution. -/
theorem measure_source_target_recovery {P Q : Measure Ω} {ω : ℝ} (hω : 0 ≤ ω)
    (hQP : Q ≤ ENNReal.ofReal ω • P) {C : A →ₗ[ℝ] T} {κ : ℝ}
    {L : T →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : Ω → A) (v pred source : Ω → T)
    (hpred : AEStronglyMeasurable (fun x => pred x - source x) Q)
    (hdrift : AEStronglyMeasurable (fun x => source x - (C (a x) + v x)) Q)
    (hv : AEStronglyMeasurable v Q) :
    eLpNorm (fun x => L (pred x) - a x) 2 Q ≤ ENNReal.ofReal κ⁻¹ *
      (ENNReal.ofReal (Real.sqrt ω) * eLpNorm (fun x => pred x - source x) 2 P +
        eLpNorm (fun x => source x - (C (a x) + v x)) 2 Q + eLpNorm v 2 Q) := by
  have he : (fun x => pred x - (C (a x) + v x)) =
      ((fun x => pred x - source x) + fun x => source x - (C (a x) + v x)) := by
    funext x
    simp only [Pi.add_apply]
    abel
  have hm : AEStronglyMeasurable (fun x => pred x - (C (a x) + v x)) Q := by
    rw [he]
    exact hpred.add hdrift
  exact (measure_recovery Q hL hκ a v pred hm hv).trans
    (mul_le_mul_right (add_le_add
      (measure_task_transfer hω hQP pred source (fun x => C (a x) + v x) hpred hdrift) le_rfl) _)

end Measures

/-- Arbitrarily small population RMS can coexist with unit error at a specified
evaluation point. This prevents a population-to-fixed-panel substitution. -/
theorem small_mass_spike {r : ℝ} (hr : 0 ≤ r) (hr1 : r < 1) :
    let p : Fin 2 → ℝ := ![r ^ 2, 1 - r ^ 2]
    let f : Fin 2 → ℝ := ![1, 0]
    (∀ i, 0 ≤ p i) ∧ (∑ i, p i = 1) ∧ rms p f = r ∧ r < f 0 := by
  dsimp only
  have hp : ∀ i : Fin 2, 0 ≤ (![r ^ 2, 1 - r ^ 2] : Fin 2 → ℝ) i := by
    intro i
    fin_cases i
    · change 0 ≤ r ^ 2
      positivity
    · change 0 ≤ 1 - r ^ 2
      nlinarith
  refine ⟨hp, by simp [Fin.sum_univ_two], ?_, by simpa using hr1⟩
  have hs := rms_sq (![r ^ 2, 1 - r ^ 2] : Fin 2 → ℝ) hp (![1, 0] : Fin 2 → ℝ)
  simp only [Fin.sum_univ_two, Matrix.cons_val_zero, Matrix.cons_val_one,
    norm_one, norm_zero, one_pow, zero_pow (by norm_num : 2 ≠ 0),
    mul_one, mul_zero, add_zero] at hs
  nlinarith [rms_nonneg (![r ^ 2, 1 - r ^ 2] : Fin 2 → ℝ) (![1, 0] : Fin 2 → ℝ)]

end FreeFoundations.Transfer
