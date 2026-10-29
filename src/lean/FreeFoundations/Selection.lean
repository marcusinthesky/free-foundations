module

public import FreeFoundations.Score
public import FreeFoundations.Recovery
public import Mathlib.Probability.Moments.SubGaussian
public import Mathlib.MeasureTheory.Measure.Real
public import Mathlib.Probability.IdentDistrib

@[expose] public section

/-!
# Finite-family learning and a dependence interface

The candidate loss functions are fixed in the theorem. Conditioning on separate
training information is one way to meet this contract for fitted candidates.
Block averages target the average marginal block law. Bounded task loss is
covered; an unbounded Gaussian score requires a different concentration theorem.
-/

noncomputable section

namespace FreeFoundations.Selection

open MeasureTheory ProbabilityTheory
open scoped NNReal

variable {Ω B K : Type*} [MeasurableSpace Ω] {μ : Measure Ω}

/-- Equal-weight empirical block risk. One block may contain the full cross-section. -/
def empirical [Fintype B] (loss : B → Ω → ℝ) (ω : Ω) : ℝ :=
  (∑ b, loss b ω) / Fintype.card B

/-- Average expected block risk; blocks need not have identical laws. -/
def marginalRisk [Fintype B] (loss : B → Ω → ℝ) (μ : Measure Ω) : ℝ :=
  (∑ b, ∫ ω, loss b ω ∂μ) / Fintype.card B

private theorem hoeffding_upper [Fintype B] [Nonempty B] [IsProbabilityMeasure μ]
    (loss : B → Ω → ℝ) (h_indep : iIndepFun loss μ)
    (hm : ∀ b, AEMeasurable (loss b) μ)
    (hb : ∀ b, ∀ᵐ ω ∂μ, loss b ω ∈ Set.Icc (0 : ℝ) 1)
    {ε : ℝ} (hε : 0 ≤ ε) :
    μ.real {ω | ε ≤ empirical loss ω - marginalRisk loss μ} ≤
      Real.exp (-2 * Fintype.card B * ε ^ 2) := by
  have hn : (0 : ℝ) < Fintype.card B := by exact_mod_cast Fintype.card_pos
  let X : B → Ω → ℝ := fun b ω => loss b ω - ∫ ω, loss b ω ∂μ
  have hi : iIndepFun X μ := h_indep.comp
    (fun b x => x - ∫ ω, loss b ω ∂μ) (fun _ => by fun_prop)
  have hs : ∀ b, HasSubgaussianMGF (X b) ((1 / 2 : ℝ≥0) ^ 2) μ := by
    intro b
    simpa [X] using hasSubgaussianMGF_of_mem_Icc (hm b) (hb b)
  have h := HasSubgaussianMGF.measure_sum_ge_le_of_iIndepFun hi
    (s := Finset.univ) (c := fun _ => ((1 / 2 : ℝ≥0) ^ 2))
    (fun b _ => hs b) (mul_nonneg hε hn.le)
  have he : {ω | ε ≤ empirical loss ω - marginalRisk loss μ} =
      {ω | ε * Fintype.card B ≤ ∑ b, X b ω} := by
    ext ω
    simp only [empirical, marginalRisk, X, Finset.sum_sub_distrib, ← sub_div,
      le_div_iff₀ hn]
  rw [he]
  convert h using 1
  congr 1
  simp only [Finset.sum_const, Finset.card_univ, nsmul_eq_mul]
  push_cast
  field_simp

/-- Two-sided bounded-loss concentration over independent, possibly nonidentical blocks. -/
theorem bounded_blocks [Fintype B] [Nonempty B] [IsProbabilityMeasure μ]
    (loss : B → Ω → ℝ) (h_indep : iIndepFun loss μ)
    (hm : ∀ b, AEMeasurable (loss b) μ)
    (hb : ∀ b, ∀ᵐ ω ∂μ, loss b ω ∈ Set.Icc (0 : ℝ) 1)
    {ε : ℝ} (hε : 0 ≤ ε) :
    μ.real {ω | ε < |empirical loss ω - marginalRisk loss μ|} ≤
      2 * Real.exp (-2 * Fintype.card B * ε ^ 2) := by
  have hi : iIndepFun (fun b ω => 1 - loss b ω) μ :=
    h_indep.comp (fun _ x => 1 - x) (fun _ => by fun_prop)
  have hb' : ∀ b, ∀ᵐ ω ∂μ, 1 - loss b ω ∈ Set.Icc (0 : ℝ) 1 := by
    intro b
    filter_upwards [hb b] with ω h
    constructor <;> linarith [h.1, h.2]
  have hneg := hoeffding_upper (fun b ω => 1 - loss b ω) hi
    (fun b => (hm b).const_sub 1) hb' hε
  have he : ∀ ω, empirical (fun b ω => 1 - loss b ω) ω -
      marginalRisk (fun b ω => 1 - loss b ω) μ =
        -(empirical loss ω - marginalRisk loss μ) := by
    intro ω
    simp only [empirical, marginalRisk, Finset.sum_sub_distrib]
    simp_rw [integral_sub (integrable_const 1) (Integrable.of_mem_Icc 0 1 (hm _) (hb _))]
    simp only [integral_const, probReal_univ, smul_eq_mul, one_mul]
    rw [Finset.sum_sub_distrib]
    ring
  simp_rw [he] at hneg
  have hpos := hoeffding_upper loss h_indep hm hb hε
  have hsub : {ω | ε < |empirical loss ω - marginalRisk loss μ|} ⊆
      {ω | ε ≤ empirical loss ω - marginalRisk loss μ} ∪
        {ω | ε ≤ -(empirical loss ω - marginalRisk loss μ)} := by
    intro ω h
    change ε < |empirical loss ω - marginalRisk loss μ| at h
    rcases lt_abs.mp h with h | h
    · exact Or.inl h.le
    · exact Or.inr h.le
  exact (measureReal_mono hsub).trans
    ((measureReal_union_le _ _).trans (by linarith))

/-- Uniform finite-family concentration. Within-block candidate losses may be dependent. -/
theorem finite_family [Fintype B] [Nonempty B] [Fintype K] [IsProbabilityMeasure μ]
    (loss : K → B → Ω → ℝ) (h_indep : ∀ k, iIndepFun (loss k) μ)
    (hm : ∀ k b, AEMeasurable (loss k b) μ)
    (hb : ∀ k b, ∀ᵐ ω ∂μ, loss k b ω ∈ Set.Icc (0 : ℝ) 1)
    {ε : ℝ} (hε : 0 ≤ ε) :
    μ.real {ω | ∃ k, ε < |empirical (loss k) ω - marginalRisk (loss k) μ|} ≤
      2 * Fintype.card K * Real.exp (-2 * Fintype.card B * ε ^ 2) := by
  have he : {ω | ∃ k, ε < |empirical (loss k) ω - marginalRisk (loss k) μ|} =
      ⋃ k, {ω | ε < |empirical (loss k) ω - marginalRisk (loss k) μ|} := by ext; simp
  rw [he]
  apply (measureReal_iUnion_fintype_le _).trans
  calc
    _ ≤ ∑ _ : K, 2 * Real.exp (-2 * Fintype.card B * ε ^ 2) :=
      Finset.sum_le_sum fun k _ => bounded_blocks (loss k) (h_indep k) (hm k) (hb k) hε
    _ = _ := by simp; ring

/-- Coupling transfers an error event, charging the probability of any mismatch once.
Marginal agreement must be established before reusing a concentration center. -/
theorem coupling_event [IsFiniteMeasure μ] (original independent : Ω → Prop)
    (mismatch : Ω → Prop) {bound Δ : ℝ}
    (hagree : ∀ ω, ¬ mismatch ω → (original ω ↔ independent ω))
    (hind : μ.real {ω | independent ω} ≤ bound)
    (hmis : μ.real {ω | mismatch ω} ≤ Δ) :
    μ.real {ω | original ω} ≤ bound + Δ := by
  have hsub : {ω | original ω} ⊆ {ω | independent ω} ∪ {ω | mismatch ω} := by
    intro ω h
    by_cases hm : mismatch ω
    · exact Or.inr hm
    · exact Or.inl ((hagree ω hm).mp h)
  exact (measureReal_mono hsub).trans ((measureReal_union_le _ _).trans (add_le_add hind hmis))

/-- A coupled independent copy supplies concentration about the original marginal
block risk when each corresponding block has the same marginal distribution. -/
theorem coupled_finite_family [Fintype B] [Nonempty B] [Fintype K]
    [IsProbabilityMeasure μ] (original copy : K → B → Ω → ℝ)
    (h_indep : ∀ k, iIndepFun (copy k) μ)
    (hm : ∀ k b, AEMeasurable (copy k b) μ)
    (hb : ∀ k b, ∀ᵐ ω ∂μ, copy k b ω ∈ Set.Icc (0 : ℝ) 1)
    (hmarg : ∀ k b, IdentDistrib (original k b) (copy k b) μ μ)
    {ε Δ : ℝ} (hε : 0 ≤ ε)
    (hmis : μ.real {ω | ∃ k b, original k b ω ≠ copy k b ω} ≤ Δ) :
    μ.real {ω | ∃ k, ε < |empirical (original k) ω - marginalRisk (original k) μ|} ≤
      2 * Fintype.card K * Real.exp (-2 * Fintype.card B * ε ^ 2) + Δ := by
  have hcenter : ∀ k, marginalRisk (original k) μ = marginalRisk (copy k) μ := by
    intro k
    unfold marginalRisk
    congr 1
    exact Finset.sum_congr rfl fun b _ => (hmarg k b).integral_eq
  apply coupling_event _ _ (fun ω => ∃ k b, original k b ω ≠ copy k b ω) ?_
    (finite_family copy h_indep hm hb hε) hmis
  intro ω hn
  have he : ∀ k b, original k b ω = copy k b ω := by
    intro k b
    by_contra h
    exact hn ⟨k, b, h⟩
  have hemp : ∀ k, empirical (original k) ω = empirical (copy k) ω := by
    intro k
    simp only [empirical, he]
  simp only [hemp, hcenter]

/-- A discrepancy between average block risk and the desired source/future risk is additive. -/
theorem risk_discrepancy {R Rh Rbar : K → ℝ} {g shift : ℝ}
    (hg : ∀ k, |Rh k - Rbar k| ≤ g) (hs : ∀ k, |Rbar k - R k| ≤ shift) :
    ∀ k, |Rh k - R k| ≤ g + shift := by
  intro k
  calc
    |Rh k - R k| = |(Rh k - Rbar k) + (Rbar k - R k)| := by congr 1; ring
    _ ≤ |Rh k - Rbar k| + |Rbar k - R k| := abs_add_le _ _
    _ ≤ _ := add_le_add (hg k) (hs k)

/-- Source excess-risk decomposition with an explicit approximation comparator. -/
theorem source_excess (R Rh : K → ℝ) {bayes g opt app : ℝ}
    (hg : ∀ k, |Rh k - R k| ≤ g) {selected comparator : K}
    (hopt : ∀ k, Rh selected ≤ Rh k + opt)
    (happ : R comparator - bayes ≤ app) :
    R selected - bayes ≤ app + 2 * g + opt := by
  have h := Score.erm_bound R Rh hg hopt comparator
  linarith

/-- Squared-risk excess becomes RMS task error only after taking a square root. -/
theorem task_rms_of_excess {E : Type*} [NormedAddCommGroup E] {f target : E}
    {R Rbayes app g opt : ℝ}
    (hidentity : R - Rbayes = ‖f - target‖ ^ 2)
    (hbound : R - Rbayes ≤ app + 2 * g + opt) :
    ‖f - target‖ ≤ Real.sqrt (app + 2 * g + opt) := by
  have hn : 0 ≤ app + 2 * g + opt := by nlinarith [sq_nonneg ‖f - target‖]
  calc
    ‖f - target‖ = Real.sqrt (‖f - target‖ ^ 2) := (Real.sqrt_sq (norm_nonneg _)).symm
    _ ≤ _ := Real.sqrt_le_sqrt (by simpa only [← hidentity] using hbound)

/-- Moment-to-panel maximum bridge. Dependence between evaluation firms is unrestricted;
each individual error must satisfy the declared second-moment contract. -/
theorem panel_markov [Fintype K] [IsFiniteMeasure μ] (error : K → Ω → ℝ)
    {B t : ℝ} (ht : 0 < t)
    (hint : ∀ i, Integrable (fun ω => error i ω ^ 2) μ)
    (hrisk : ∀ i, ∫ ω, error i ω ^ 2 ∂μ ≤ B ^ 2) :
    μ.real {ω | ∃ i, t < error i ω} ≤ Fintype.card K * B ^ 2 / t ^ 2 := by
  have hi : ∀ i, μ.real {ω | t < error i ω} ≤ B ^ 2 / t ^ 2 := by
    intro i
    apply (le_div_iff₀ (sq_pos_of_pos ht)).mpr
    have hm := mul_meas_ge_le_integral_of_nonneg
      (Filter.Eventually.of_forall fun ω => sq_nonneg (error i ω)) (hint i) (t ^ 2)
    have hsub : {ω | t < error i ω} ⊆ {ω | t ^ 2 ≤ error i ω ^ 2} := by
      intro ω h
      change t < error i ω at h
      change t ^ 2 ≤ error i ω ^ 2
      nlinarith
    have hmono := mul_le_mul_of_nonneg_left (measureReal_mono (μ := μ) hsub) (sq_nonneg t)
    nlinarith [hrisk i]
  have he : {ω | ∃ i, t < error i ω} = ⋃ i, {ω | t < error i ω} := by ext; simp
  rw [he]
  calc
    _ ≤ ∑ i, μ.real {ω | t < error i ω} := measureReal_iUnion_fintype_le _
    _ ≤ ∑ _ : K, B ^ 2 / t ^ 2 := Finset.sum_le_sum fun i _ => hi i
    _ = _ := by simp [div_eq_mul_inv]; ring

/-- Frozen-predictor confidence wrapper, conditional on training when the moment
hypotheses are conditional. No interfirm independence is used. -/
theorem random_panel [Fintype K] [Nonempty K] [IsFiniteMeasure μ]
    (error : K → Ω → ℝ) {B α : ℝ} (hB : 0 ≤ B) (hα : 0 < α)
    (hint : ∀ i, Integrable (fun ω => error i ω ^ 2) μ)
    (hrisk : ∀ i, ∫ ω, error i ω ^ 2 ∂μ ≤ B ^ 2) :
    μ.real {ω | ∃ i, B * Real.sqrt (Fintype.card K / α) < error i ω} ≤ α := by
  have hn : (0 : ℝ) < Fintype.card K := by exact_mod_cast Fintype.card_pos
  rcases hB.eq_or_lt with hB0 | hBp
  · have hz : ∀ i, error i =ᵐ[μ] 0 := by
      intro i
      have he : ∫ ω, error i ω ^ 2 ∂μ = 0 := by
        apply le_antisymm
        · simpa [← hB0] using hrisk i
        · exact integral_nonneg fun ω => sq_nonneg _
      have ha := (integral_eq_zero_iff_of_nonneg
        (fun ω => sq_nonneg (error i ω)) (hint i)).mp he
      filter_upwards [ha] with ω h
      simpa using h
    have hzall : ∀ᵐ ω ∂μ, ∀ i, error i ω = 0 := ae_all_iff.mpr hz
    have hnull : μ {ω | ∃ i, B * Real.sqrt (Fintype.card K / α) < error i ω} = 0 := by
      have hevent : ∀ᵐ ω ∂μ, ¬ ∃ i,
          B * Real.sqrt (Fintype.card K / α) < error i ω := by
        filter_upwards [hzall] with ω h
        simp [← hB0, h]
      simpa only [not_not] using ae_iff.mp hevent
    rw [measureReal_def, hnull, ENNReal.toReal_zero]
    exact hα.le
  · have ht : 0 < B * Real.sqrt (Fintype.card K / α) :=
      mul_pos hBp (Real.sqrt_pos.mpr (div_pos hn hα))
    have hp := panel_markov error ht hint hrisk
    have he : Fintype.card K * B ^ 2 /
        (B * Real.sqrt (Fintype.card K / α)) ^ 2 = α := by
      rw [mul_pow, Real.sq_sqrt (div_pos hn hα).le]
      field_simp
    exact hp.trans_eq he

end FreeFoundations.Selection
