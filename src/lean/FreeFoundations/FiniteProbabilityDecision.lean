module

public import FreeFoundations.FiniteProbability
public import FreeFoundations.Decision

/-!
# Typed finite experiments and bounded financial decisions

The prior and every experiment row are finite simplex laws. The original raw
stochastic-matrix interface remains available, including its subprobability uses.
Approximate reverse simulation gives a one-sided risk bound; a forward garbling
is additionally required for the nonnegative, two-sided sufficiency gap.
-/

@[expose] public noncomputable section

namespace FreeFoundations.FiniteProbability

open Finset

variable {Θ X Y Z A : Type*} [Fintype Θ] [Fintype X] [Fintype Y] [Fintype Z]
  [Fintype A] [Nonempty A]

def rawKernel (K : FinKernel X Y) : X → Y → ℝ := fun x y => K x y

omit [Fintype X] in
theorem kernel_stochastic (K : FinKernel X Y) : FreeFoundations.Decision.Stochastic (rawKernel K) :=
  ⟨fun x => nonneg (K x), fun x => sum_one (K x)⟩

omit [Fintype X] in
/-- Existing stochastic matrices and simplex-valued kernel rows express the same condition. -/
theorem stochastic_iff_rows_simplex (K : X → Y → ℝ) :
    FreeFoundations.Decision.Stochastic K ↔ ∀ x, K x ∈ stdSimplex ℝ Y := by
  constructor
  · intro h x
    exact ⟨h.1 x, h.2 x⟩
  · intro h
    exact ⟨fun x => (h x).1, fun x => (h x).2⟩

def ofStochastic (K : X → Y → ℝ) (hK : FreeFoundations.Decision.Stochastic K) : FinKernel X Y :=
  fun x => ⟨K x, hK.1 x, hK.2 x⟩

omit [Fintype X] in
@[simp] theorem raw_ofStochastic (K : X → Y → ℝ) (hK : FreeFoundations.Decision.Stochastic K) :
    rawKernel (ofStochastic K hK) = K := rfl

omit [Fintype X] in
@[simp] theorem kernelComp_raw (K : FinKernel X Y) (H : FinKernel Y Z) :
    rawKernel (kernelComp K H) = FreeFoundations.Decision.compose (rawKernel K) (rawKernel H) := rfl

/-- Half-L1 total variation, stated independently of the simplex's ambient supremum norm. -/
def totalVariation (p q : FinDist X) : ℝ := (∑ x, |p x - q x|) / 2

theorem totalVariation_nonneg (p q : FinDist X) : 0 ≤ totalVariation p q := by
  exact div_nonneg (sum_nonneg fun x _ => abs_nonneg _) (by norm_num)

def averageTV (π : FinDist Θ) (P Q : FinKernel Θ X) : ℝ :=
  expect π (fun θ => totalVariation (P θ) (Q θ))

def decisionRisk (π : FinDist Θ) (loss : Θ → A → ℝ) (P : FinKernel Θ X) : ℝ :=
  FreeFoundations.Decision.bayesRisk (π : Θ → ℝ) loss (rawKernel P)

/-- Typed garbling reuses the existing finite decision theorem. -/
theorem garbling_risk (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (G : FinKernel X Z) :
    decisionRisk π loss P ≤ decisionRisk π loss (kernelComp P G) :=
  FreeFoundations.Decision.garbling_risk _ _ _ (kernel_stochastic G)

/-- Bounded-loss continuity scales with its actual range, including the degenerate range zero. -/
theorem bounded_expectation_tv (p q loss : X → ℝ) (hmass : ∑ x, p x = ∑ x, q x)
    {L : ℝ} (hL : 0 ≤ L) (hloss : ∀ x, 0 ≤ loss x ∧ loss x ≤ L) :
    |∑ x, (p x - q x) * loss x| ≤ L * ((∑ x, |p x - q x|) / 2) := by
  rcases hL.eq_or_lt with hzero | hpos
  · have hz : ∀ x, loss x = 0 := fun x => by linarith [(hloss x).1, (hloss x).2]
    simp [hz, ← hzero]
  · have hn : ∀ x, 0 ≤ loss x / L ∧ loss x / L ≤ 1 := by
      intro x
      exact ⟨div_nonneg (hloss x).1 hpos.le, (div_le_one hpos).mpr (hloss x).2⟩
    have h := FreeFoundations.Decision.bounded_expectation_tv p q (fun x => loss x / L) hmass hn
    have he : (∑ x, (p x - q x) * loss x) =
        L * ∑ x, (p x - q x) * (loss x / L) := by
      rw [mul_sum]
      apply sum_congr rfl
      intro x _
      field_simp
    rw [he, abs_mul, abs_of_pos hpos]
    exact mul_le_mul_of_nonneg_left h hpos.le

omit [Fintype A] [Nonempty A] in
/-- Prior-averaged continuity for a fixed deterministic policy. -/
theorem fixed_policy_tv (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P Q : FinKernel Θ X) {L : ℝ} (hL : 0 ≤ L)
    (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L) (f : X → A) :
    |(∑ x, FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel P) x (f x)) -
        ∑ x, FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel Q) x (f x)| ≤
      L * averageTV π P Q := by
  have he : (∑ x, FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel P) x (f x)) -
      ∑ x, FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel Q) x (f x) =
        ∑ θ, π θ * ∑ x, (P θ x - Q θ x) * loss θ (f x) := by
    simp only [FreeFoundations.Decision.cost, rawKernel, ← sum_sub_distrib]
    conv_lhs => arg 2; intro x; arg 2; intro θ; rw [show π θ * P θ x * loss θ (f x) -
      π θ * Q θ x * loss θ (f x) = π θ * ((P θ x - Q θ x) * loss θ (f x)) by ring]
    rw [sum_comm]
    simp_rw [mul_sum]
  rw [he]
  calc _ ≤ ∑ θ, |π θ * ∑ x, (P θ x - Q θ x) * loss θ (f x)| := abs_sum_le_sum_abs _ _
    _ ≤ ∑ θ, π θ * (L * totalVariation (P θ) (Q θ)) := by
      apply sum_le_sum
      intro θ _
      rw [abs_mul, abs_of_nonneg (nonneg π θ)]
      exact mul_le_mul_of_nonneg_left
        (bounded_expectation_tv _ _ _ (by rw [sum_one, sum_one]) hL (fun x => hloss θ (f x)))
        (nonneg π θ)
    _ = _ := by
      simp only [averageTV, expect, MathEconLib.Probability.FinDist.expect_eq_sum,
        MathEconLib.Probability.FinDist.pmf_eq_coe, smul_eq_mul, mul_sum]
      apply sum_congr rfl
      intro θ _
      ring

/-- Optimal-risk continuity uses the other experiment's optimal policy. -/
theorem bayes_risk_tv (π : FinDist Θ) (loss : Θ → A → ℝ) (P Q : FinKernel Θ X)
    {L : ℝ} (hL : 0 ≤ L) (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L) :
    decisionRisk π loss P ≤ decisionRisk π loss Q + L * averageTV π P Q := by
  have hb : decisionRisk π loss P ≤ ∑ x,
      FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel P) x
        (FreeFoundations.Decision.bestAction (π : Θ → ℝ) loss (rawKernel Q) x) :=
    sum_le_sum fun x _ => FreeFoundations.Decision.bestAction_le _ _ _ _ _
  have ht := (abs_le.mp (fixed_policy_tv π loss P Q hL hloss
    (FreeFoundations.Decision.bestAction (π : Θ → ℝ) loss (rawKernel Q)))).2
  change (∑ x, FreeFoundations.Decision.cost (π : Θ → ℝ) loss (rawKernel Q) x
    (FreeFoundations.Decision.bestAction (π : Θ → ℝ) loss (rawKernel Q) x)) + _ ≥ _
  linarith

/-- Reverse simulation alone controls only the upper decision-risk gap. -/
theorem approximate_decoder (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (Q : FinKernel Θ Z) (D : FinKernel Z X)
    {L ε : ℝ} (hL : 0 ≤ L) (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L)
    (hε : averageTV π (kernelComp Q D) P ≤ ε) :
    decisionRisk π loss Q - decisionRisk π loss P ≤ L * ε := by
  have hgarble := garbling_risk π loss Q D
  have htv := bayes_risk_tv π loss (kernelComp Q D) P hL hloss
  have hscale := mul_le_mul_of_nonneg_left hε hL
  linarith

/-- Uniform statewise TV controls prior-average TV for every normalized prior. -/
theorem approximate_decoder_uniform (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (Q : FinKernel Θ Z) (D : FinKernel Z X)
    {L ε : ℝ} (hL : 0 ≤ L) (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L)
    (hε : ∀ θ, totalVariation (kernelComp Q D θ) (P θ) ≤ ε) :
    decisionRisk π loss Q - decisionRisk π loss P ≤ L * ε := by
  apply approximate_decoder π loss P Q D hL hloss
  exact (expect_mono π hε).trans_eq (expect_const π ε)

/-- Forward garbling supplies the lower bound absent from reverse simulation alone. -/
theorem approximate_sufficiency (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (G : FinKernel X Z) (D : FinKernel Z X)
    {L ε : ℝ} (hL : 0 ≤ L) (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L)
    (hε : averageTV π (kernelComp (kernelComp P G) D) P ≤ ε) :
    0 ≤ decisionRisk π loss (kernelComp P G) - decisionRisk π loss P ∧
      decisionRisk π loss (kernelComp P G) - decisionRisk π loss P ≤ L * ε := by
  have hlower := garbling_risk π loss P G
  exact ⟨sub_nonneg.mpr hlower, approximate_decoder π loss P (kernelComp P G) D hL hloss hε⟩

theorem approximate_sufficiency_uniform (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (G : FinKernel X Z) (D : FinKernel Z X)
    {L ε : ℝ} (hL : 0 ≤ L) (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ L)
    (hε : ∀ θ, totalVariation (kernelComp (kernelComp P G) D θ) (P θ) ≤ ε) :
    0 ≤ decisionRisk π loss (kernelComp P G) - decisionRisk π loss P ∧
      decisionRisk π loss (kernelComp P G) - decisionRisk π loss P ≤ L * ε := by
  exact ⟨sub_nonneg.mpr (garbling_risk π loss P G),
    approximate_decoder_uniform π loss P (kernelComp P G) D hL hloss hε⟩

/-- The degenerate loss range is handled without dividing by its bound. -/
theorem zero_range_risk (π : FinDist Θ) (loss : Θ → A → ℝ) (P : FinKernel Θ X)
    (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ 0) : decisionRisk π loss P = 0 := by
  have hz : loss = fun _ _ => 0 := by
    funext θ a
    exact le_antisymm (hloss θ a).2 (hloss θ a).1
  simp [decisionRisk, FreeFoundations.Decision.bayesRisk, FreeFoundations.Decision.cost, hz]

theorem zero_range_gap (π : FinDist Θ) (loss : Θ → A → ℝ)
    (P : FinKernel Θ X) (Q : FinKernel Θ Z)
    (hloss : ∀ θ a, 0 ≤ loss θ a ∧ loss θ a ≤ 0) :
    decisionRisk π loss Q - decisionRisk π loss P = 0 := by
  rw [zero_range_risk π loss Q hloss, zero_range_risk π loss P hloss, sub_self]

end FreeFoundations.FiniteProbability
