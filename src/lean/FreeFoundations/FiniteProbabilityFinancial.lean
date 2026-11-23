module

public import FreeFoundations.FiniteProbability
public import FreeFoundations.StatisticalFinancial

/-!
# Typed finite laws at the learning-to-finance interface

These wrappers use a normalized declared law for evaluation inputs. The raw
`StatisticalFinancial` interfaces still handle unnormalized good-event restrictions.
Block-mixture identities identify the source risk before concentration or ERM is used.
-/

@[expose] public noncomputable section

namespace FreeFoundations.FiniteProbability

open MeasureTheory Matrix Finset
open scoped Matrix.Norms.L2Operator

variable {X Ω : Type*} [Fintype X] [MeasurableSpace X] [MeasurableSingletonClass X]
  [MeasurableSpace Ω] {μ : Measure Ω}

/-- An equality of pushforward measures supplies the existing pointwise marginal contract. -/
theorem marginal_weights_of_map (q : FinDist X) (input : Ω → X) (hinput : Measurable input)
    (hmap : μ.map input = toMeasure q) (x : X) :
    μ.real {ω | input ω = x} = q x := by
  have hm := map_measureReal_apply (μ := μ) hinput (measurableSet_singleton x)
  rw [hmap, toMeasure_real_singleton] at hm
  exact hm.symm

/-- Finite target law and evaluated squared moments agree exactly. -/
theorem moment_of_map [IsFiniteMeasure μ] {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
    (q : FinDist X) (input : Ω → X) (hinput : Measurable input)
    (hmap : μ.map input = toMeasure q) (f : X → E) :
    Integrable (fun ω => ‖f (input ω)‖ ^ 2) μ ∧
      (∫ ω, ‖f (input ω)‖ ^ 2 ∂μ) = Transfer.rms (q : X → ℝ) f ^ 2 := by
  have h := StatisticalFinancial.finite_marginal_moment input hinput (q : X → ℝ)
    (marginal_weights_of_map q input hinput hmap) (fun x => ‖f x‖ ^ 2)
  exact ⟨h.1, h.2.trans (Transfer.rms_sq _ (nonneg q) f).symm⟩

/-- A uniform mixture of block marginals is the exact risk centered by equal-weight
block concentration. Independence is not needed to identify this expectation. -/
theorem marginalRisk_eq_mixture [IsFiniteMeasure μ] {B : Type*} [Fintype B] [Nonempty B]
    (laws : B → FinDist X) (input : B → Ω → X) (hinput : ∀ b, Measurable (input b))
    (hmap : ∀ b, μ.map (input b) = toMeasure (laws b)) (loss : X → ℝ) :
    Selection.marginalRisk (fun b ω => loss (input b ω)) μ =
      expect (finMixture (stdSimplex.barycenter : FinDist B) laws) loss := by
  have he : ∀ b, (∫ ω, loss (input b ω) ∂μ) = expect (laws b) loss := by
    intro b
    have hm := StatisticalFinancial.finite_marginal_moment (input b) (hinput b)
      (laws b : X → ℝ) (marginal_weights_of_map (laws b) (input b) (hinput b) (hmap b)) loss
    simpa only [expect, MathEconLib.Probability.FinDist.expect_eq_sum,
      MathEconLib.Probability.FinDist.pmf_eq_coe, smul_eq_mul] using hm.2
  rw [expect_finMixture]
  simp only [Selection.marginalRisk, he, expect,
    MathEconLib.Probability.FinDist.expect_eq_sum,
    MathEconLib.Probability.FinDist.pmf_eq_coe, smul_eq_mul]
  change (∑ b, ∑ x, laws b x * loss x) / (Fintype.card B : ℝ) =
    ∑ b, (Fintype.card B : ℝ)⁻¹ * ∑ x, laws b x * loss x
  rw [sum_div]
  apply sum_congr rfl
  intro b _
  ring

omit [MeasurableSpace X] [MeasurableSingletonClass X] in
/-- Typed source-to-target exposure recovery does not change the original raw theorem. -/
theorem source_target_recovery {A U : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    [NormedAddCommGroup U] [InnerProductSpace ℝ U]
    (p q : FinDist X) {overlap κ : ℝ} (hoverlap : 0 ≤ overlap)
    (hqp : ∀ x, q x ≤ overlap * p x) {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : X → A) (v pred source : X → U) :
    Transfer.rms (q : X → ℝ) (fun x => L (pred x) - a x) ≤
      (Real.sqrt overlap * Transfer.rms (p : X → ℝ) (fun x => pred x - source x) +
        Transfer.rms (q : X → ℝ) (fun x => source x - (C (a x) + v x)) +
        Transfer.rms (q : X → ℝ) v) / κ :=
  Transfer.source_target_recovery (nonneg p) (nonneg q) hoverlap hqp hL hκ a v pred source

/-- Full finite source-transfer financial certificate, with marginal laws supplied
as pushforward equalities rather than independent point-mass assumptions. -/
theorem transfer_failure_probability [IsProbabilityMeasure μ]
    {n A U : Type*} [Fintype n] [DecidableEq n]
    [NormedAddCommGroup A] [InnerProductSpace ℝ A]
    [NormedAddCommGroup U] [InnerProductSpace ℝ U]
    (hn : 2 ≤ Fintype.card n) (p q : FinDist X)
    (input : n → Ω → X) (hinput : ∀ i, Measurable (input i))
    (hmap : ∀ i, μ.map (input i) = toMeasure q)
    {overlap κ : ℝ} (hoverlap : 0 ≤ overlap) (hqp : ∀ x, q x ≤ overlap * p x)
    {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A} (hL : Recovery.Decoder C κ L) (hκ : 0 < κ)
    (a : X → A) (v pred source : X → U) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ)
    {B α h c M V ec BW eD ρ m : ℝ} (hB : 0 ≤ B) (hα : 0 < α) (hh : 0 < h) (hm : 0 < m)
    (hbudget : (Real.sqrt overlap * Transfer.rms (p : X → ℝ) (fun x => pred x - source x) +
      Transfer.rms (q : X → ℝ) (fun x => source x - (C (a x) + v x)) +
      Transfer.rms (q : X → ℝ) v) / κ ≤ B)
    (hcontrols : ∀ ω, StatisticalFinancial.Controls (fun i => a (input i ω))
      (fun i => L (pred (input i ω))) (D ω) (Dh ω) (T ω) h c (ch ω) M V ec BW eD ρ m)
    (hlocal : EndToEnd.covarianceError (Fintype.card n)
      (2 * StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW eD ρ < m) :
    μ.real {ω | ¬ StatisticalFinancial.Certificate
      (StatisticalFinancial.forecast (fun i => L (pred (input i ω))) (Dh ω) h (ch ω)) (T ω)
      (EndToEnd.covarianceError (Fintype.card n)
        (2 * StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW eD ρ) m} ≤ α :=
  StatisticalFinancial.finite_transfer_failure_probability hn input hinput (nonneg p) (nonneg q)
    (fun i => marginal_weights_of_map q (input i) (hinput i) (hmap i)) hoverlap hqp hL hκ
    a v pred source D Dh T ch hB hα hh hm hbudget hcontrols hlocal

end FreeFoundations.FiniteProbability
