module

public import FreeFoundations.EndToEnd
public import FreeFoundations.Selection

@[expose] public section

/-!
# High-probability financial certificates

The moment contract refers to each evaluated firm's exposure error, with a frozen
predictor or under an explicitly justified training restriction. No independence
between firms is required. These theorems do not infer this sampling contract from
an average population RMS bound or from chronological evaluation alone.
-/

noncomputable section

namespace FreeFoundations.StatisticalFinancial

open MeasureTheory Matrix
open scoped Matrix.Norms.L2Operator

variable {n A Ω : Type*} [Fintype n] [DecidableEq n]
  [NormedAddCommGroup A] [InnerProductSpace ℝ A] [MeasurableSpace Ω]

/-- The covariance forecast constructed from the calibrated exposure readout. -/
def forecast (ah : n → A) (Dh : Matrix n n ℝ) (h ch : ℝ) : Matrix n n ℝ :=
  EndToEnd.spatial (Kernel.expKernel (EndToEnd.distances ah) h) ch Dh

/-- Structural and conditioning inputs to the deterministic financial theorem.
No covariance-error or score conclusion is assumed. -/
structure Controls (a ah : n → A) (D Dh T : Matrix n n ℝ)
    (h c ch M V ec BW eD ρ m : ℝ) : Prop where
  reference_invertible : IsUnit (1 - c • Kernel.expKernel (EndToEnd.distances a) h).det
  forecast_invertible : IsUnit (1 - ch • Kernel.expKernel (EndToEnd.distances ah) h).det
  reference_resolvent : ‖(1 - c • Kernel.expKernel (EndToEnd.distances a) h)⁻¹‖ ≤ M
  forecast_resolvent : ‖(1 - ch • Kernel.expKernel (EndToEnd.distances ah) h)⁻¹‖ ≤ M
  innovation_bound : ‖D‖ ≤ V
  coefficient_error : |ch - c| ≤ ec
  network_bound : ‖Kernel.expKernel (EndToEnd.distances ah) h‖ ≤ BW
  innovation_error : ‖D - Dh‖ ≤ eD
  spatial_approximation : ‖EndToEnd.spatial (Kernel.expKernel (EndToEnd.distances a) h) c D - T‖ ≤ ρ
  forecast_positive : (forecast ah Dh h ch).PosDef
  target_positive : T.PosDef
  forecast_floor : (forecast ah Dh h ch - m • 1).PosSemidef

/-- The joint covariance and local score certificate whose failure probability is bounded. -/
def Certificate (S T : Matrix n n ℝ) (E m : ℝ) : Prop :=
  ‖S - T‖ ≤ E ∧ 0 ≤ Score.loss S T - Score.loss T T ∧
    Score.loss S T - Score.loss T T ≤ Fintype.card n * (E / m) ^ 2 / (2 * (1 - E / m))

/-- The numerical exposure budget produced by the second-moment/union-bound interface. -/
def panelRadius (B α : ℝ) : ℝ := B * Real.sqrt (Fintype.card n / α)

theorem certificate_of_uniform (hn : 2 ≤ Fintype.card n) (a ah : n → A)
    (D Dh T : Matrix n n ℝ) {e h c ch M V ec BW eD ρ m : ℝ}
    (he : 0 ≤ e) (hh : 0 < h) (hm : 0 < m)
    (herr : ∀ i, ‖ah i - a i‖ ≤ e)
    (hc : Controls a ah D Dh T h c ch M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ < m) :
    Certificate (forecast ah Dh h ch) T
      (EndToEnd.covarianceError (Fintype.card n) (2 * e / h) V M c ec BW eD ρ) m := by
  exact EndToEnd.measurement_to_finance hn a ah D Dh T he hh herr
    hc.reference_invertible hc.forecast_invertible hc.reference_resolvent hc.forecast_resolvent
    hc.innovation_bound hc.coefficient_error hc.network_bound hc.innovation_error hc.spatial_approximation
    hc.forecast_positive hc.target_positive hm hc.forecast_floor hlocal

/-- A restricted good-training moment contract produces an actual financial guarantee
on that event. The restriction is unnormalized: its moment bound is an explicit input,
not a claim that conditioning preserves the target law. -/
theorem failure_on_good {μ : Measure Ω} [IsFiniteMeasure μ]
    (hn : 2 ≤ Fintype.card n) (a ah : Ω → n → A) (D Dh T : Ω → Matrix n n ℝ)
    (ch : Ω → ℝ) (good : Set Ω) (hgood : MeasurableSet good)
    {B α h c M V ec BW eD ρ m : ℝ} (hB : 0 ≤ B) (hα : 0 < α)
    (hh : 0 < h) (hm : 0 < m)
    (hint : ∀ i, Integrable (fun ω => ‖ah ω i - a ω i‖ ^ 2) (μ.restrict good))
    (hrisk : ∀ i, ∫ ω, ‖ah ω i - a ω i‖ ^ 2 ∂μ.restrict good ≤ B ^ 2)
    (hcontrols : ∀ ω ∈ good, Controls (a ω) (ah ω) (D ω) (Dh ω) (T ω)
      h c (ch ω) M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n)
      (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ < m) :
    μ.real ({ω | ¬ Certificate (forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ∩ good) ≤ α := by
  have hnpos : 0 < Fintype.card n := by omega
  let : Nonempty n := Fintype.card_pos_iff.mp hnpos
  have hp := Selection.random_panel (μ := μ.restrict good)
    (fun i ω => ‖ah ω i - a ω i‖) hB hα hint hrisk
  rw [measureReal_restrict_apply' hgood] at hp
  apply (measureReal_mono (μ := μ) ?_).trans hp
  intro ω hω
  refine ⟨?_, hω.2⟩
  by_contra hevent
  have herr : ∀ i, ‖ah ω i - a ω i‖ ≤ panelRadius (n := n) B α := by
    intro i
    by_contra hi
    exact hevent ⟨i, lt_of_not_ge hi⟩
  have hc := certificate_of_uniform hn (a ω) (ah ω) (D ω) (Dh ω) (T ω)
    (mul_nonneg hB (Real.sqrt_nonneg _)) hh hm herr (hcontrols ω hω.2) hlocal
  exact hω.1 hc

/-- Frozen-predictor moment bounds yield a covariance-and-score failure probability.
Each firm's second moment is required; a single average population RMS is insufficient. -/
theorem failure_probability {μ : Measure Ω} [IsProbabilityMeasure μ]
    (hn : 2 ≤ Fintype.card n) (a ah : Ω → n → A) (D Dh T : Ω → Matrix n n ℝ)
    (ch : Ω → ℝ) {B α h c M V ec BW eD ρ m : ℝ} (hB : 0 ≤ B) (hα : 0 < α)
    (hh : 0 < h) (hm : 0 < m)
    (hint : ∀ i, Integrable (fun ω => ‖ah ω i - a ω i‖ ^ 2) μ)
    (hrisk : ∀ i, ∫ ω, ‖ah ω i - a ω i‖ ^ 2 ∂μ ≤ B ^ 2)
    (hcontrols : ∀ ω, Controls (a ω) (ah ω) (D ω) (Dh ω) (T ω)
      h c (ch ω) M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n)
      (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ < m) :
    μ.real {ω | ¬ Certificate (forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ≤ α := by
  simpa only [Measure.restrict_univ, Set.inter_univ] using
    failure_on_good hn a ah D Dh T ch Set.univ MeasurableSet.univ hB hα hh hm
      (by simpa using hint) (by simpa using hrisk) (fun ω _ => hcontrols ω) hlocal

/-- Learning failure and conditional panel failure add. The moment hypotheses are under
the good-training restriction and must be supplied by a valid learning/sampling argument. -/
theorem failure_probability_with_learning {μ : Measure Ω} [IsProbabilityMeasure μ]
    (hn : 2 ≤ Fintype.card n) (a ah : Ω → n → A) (D Dh T : Ω → Matrix n n ℝ)
    (ch : Ω → ℝ) (good : Set Ω) (hgood : MeasurableSet good)
    {B α αlearn h c M V ec BW eD ρ m : ℝ} (hB : 0 ≤ B) (hα : 0 < α)
    (hh : 0 < h) (hm : 0 < m) (hlearning : μ.real goodᶜ ≤ αlearn)
    (hint : ∀ i, Integrable (fun ω => ‖ah ω i - a ω i‖ ^ 2) (μ.restrict good))
    (hrisk : ∀ i, ∫ ω, ‖ah ω i - a ω i‖ ^ 2 ∂μ.restrict good ≤ B ^ 2)
    (hcontrols : ∀ ω ∈ good, Controls (a ω) (ah ω) (D ω) (Dh ω) (T ω)
      h c (ch ω) M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n)
      (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ < m) :
    μ.real {ω | ¬ Certificate (forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ≤ α + αlearn := by
  have hp := failure_on_good hn a ah D Dh T ch good hgood hB hα hh hm hint hrisk hcontrols hlocal
  apply (measureReal_mono (μ := μ) (show {ω | ¬ Certificate (forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ⊆
      ({ω | ¬ Certificate (forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
        (EndToEnd.covarianceError (Fintype.card n)
          (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ∩ good) ∪ goodᶜ from
    fun ω hω => by by_cases hg : ω ∈ good; exact Or.inl ⟨hω, hg⟩; exact Or.inr hg)).trans
  exact (measureReal_union_le _ _).trans (add_le_add hp hlearning)

section FiniteInput

variable {X U : Type*} [Fintype X] [MeasurableSpace X] [MeasurableSingletonClass X]
  [NormedAddCommGroup U] [InnerProductSpace ℝ U]

/-- An explicit finite marginal law identifies a firm's evaluated second moment with
the finite target-weighted quantity. Dependence between firms is unrestricted. -/
theorem finite_marginal_moment {μ : Measure Ω} [IsFiniteMeasure μ]
    (input : Ω → X) (hinput : Measurable input) (q : X → ℝ)
    (hmarginal : ∀ x, μ.real {ω | input ω = x} = q x) (f : X → ℝ) :
    Integrable (fun ω => f (input ω)) μ ∧
      (∫ ω, f (input ω) ∂μ) = ∑ x, q x * f x := by
  have hf : Integrable f (μ.map input) := Integrable.of_finite
  refine ⟨hf.comp_measurable hinput, ?_⟩
  rw [← integral_map hinput.aemeasurable hf.aestronglyMeasurable, integral_fintype hf]
  apply Finset.sum_congr rfl
  intro x _
  have heq : (μ.map input).real {x} = q x := by
    rw [measureReal_def, Measure.map_apply hinput (measurableSet_singleton x)]
    change μ.real {ω | input ω = x} = q x
    exact hmarginal x
  rw [heq, smul_eq_mul]

/-- A fixed finite source-transfer problem supplies the per-firm moment premise when
the evaluation firm's marginal is the declared target law. The economically anchored
decoder and alignment term are exactly those of `Transfer.source_target_recovery`. -/
theorem finite_transfer_moment {μ : Measure Ω} [IsFiniteMeasure μ]
    (input : Ω → X) (hinput : Measurable input) {p q : X → ℝ}
    (hp : ∀ x, 0 ≤ p x) (hq : ∀ x, 0 ≤ q x)
    (hmarginal : ∀ x, μ.real {ω | input ω = x} = q x)
    {overlap κ : ℝ} (hoverlap : 0 ≤ overlap) (hqp : ∀ x, q x ≤ overlap * p x)
    {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : X → A) (v pred source : X → U) {B : ℝ} (_hB : 0 ≤ B)
    (hbudget : (Real.sqrt overlap * Transfer.rms p (fun x => pred x - source x) +
      Transfer.rms q (fun x => source x - (C (a x) + v x)) + Transfer.rms q v) / κ ≤ B) :
    Integrable (fun ω => ‖L (pred (input ω)) - a (input ω)‖ ^ 2) μ ∧
      (∫ ω, ‖L (pred (input ω)) - a (input ω)‖ ^ 2 ∂μ) ≤ B ^ 2 := by
  have hmoment := finite_marginal_moment input hinput q hmarginal
    (fun x => ‖L (pred x) - a x‖ ^ 2)
  have hrms := (Transfer.source_target_recovery hp hq hoverlap hqp hL hκ a v pred source).trans hbudget
  refine ⟨hmoment.1, ?_⟩
  rw [hmoment.2, ← Transfer.rms_sq q hq]
  exact pow_le_pow_left₀ (Transfer.rms_nonneg _ _) hrms 2

/-- Complete fixed-predictor finite-source transfer to covariance and score probability.
The source error, conditional drift and task alignment enter through `hbudget`; the
evaluated firms have their declared finite target marginals. -/
theorem finite_transfer_failure_probability {μ : Measure Ω} [IsProbabilityMeasure μ]
    (hn : 2 ≤ Fintype.card n) (input : n → Ω → X) (hinput : ∀ i, Measurable (input i))
    {p q : X → ℝ} (hp : ∀ x, 0 ≤ p x) (hq : ∀ x, 0 ≤ q x)
    (hmarginal : ∀ i x, μ.real {ω | input i ω = x} = q x)
    {overlap κ : ℝ} (hoverlap : 0 ≤ overlap) (hqp : ∀ x, q x ≤ overlap * p x)
    {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : X → A) (v pred source : X → U) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ)
    {B α h c M V ec BW eD ρ m : ℝ} (hB : 0 ≤ B) (hα : 0 < α) (hh : 0 < h) (hm : 0 < m)
    (hbudget : (Real.sqrt overlap * Transfer.rms p (fun x => pred x - source x) +
      Transfer.rms q (fun x => source x - (C (a x) + v x)) + Transfer.rms q v) / κ ≤ B)
    (hcontrols : ∀ ω, Controls (fun i => a (input i ω)) (fun i => L (pred (input i ω)))
      (D ω) (Dh ω) (T ω) h c (ch ω) M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n)
      (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ < m) :
    μ.real {ω | ¬ Certificate (forecast (fun i => L (pred (input i ω))) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ≤ α := by
  have hmom := fun i => finite_transfer_moment (input i) (hinput i) hp hq (hmarginal i)
    hoverlap hqp hL hκ a v pred source hB hbudget
  exact failure_probability hn (fun ω i => a (input i ω)) (fun ω i => L (pred (input i ω)))
    D Dh T ch hB hα hh hm (fun i => (hmom i).1) (fun i => (hmom i).2) hcontrols hlocal

end FiniteInput

end FreeFoundations.StatisticalFinancial
