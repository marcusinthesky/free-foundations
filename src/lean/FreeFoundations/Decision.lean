import Mathlib.Analysis.SpecialFunctions.Sqrt

/-! Finite experiments, randomized policies, and prior-averaged deficiency. -/

namespace FreeFoundations.Decision

open Finset

variable {Θ X Z A : Type*} [Fintype Θ] [Fintype X] [Fintype Z] [Fintype A]
  [Nonempty A]

/-- A finite stochastic matrix, with rows indexed by the input. -/
def Stochastic {I J : Type*} [Fintype J] (K : I → J → ℝ) : Prop :=
  (∀ i j, 0 ≤ K i j) ∧ ∀ i, ∑ j, K i j = 1

def compose {I J K : Type*} [Fintype J] (P : I → J → ℝ) (Q : J → K → ℝ) : I → K → ℝ :=
  fun i k => ∑ j, P i j * Q j k

theorem stochastic_compose {I J K : Type*} [Fintype J] [Fintype K]
    {P : I → J → ℝ} {Q : J → K → ℝ} (hP : Stochastic P) (hQ : Stochastic Q) :
    Stochastic (compose P Q) := by
  constructor
  · intro i k
    exact sum_nonneg fun j _ => mul_nonneg (hP.1 i j) (hQ.1 j k)
  · intro i
    simp only [compose]
    rw [sum_comm]
    simp_rw [← mul_sum, hQ.2, mul_one]
    exact hP.2 i

def cost (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ) (x : X) (a : A) : ℝ :=
  ∑ θ, π θ * P θ x * ℓ θ a

noncomputable def bestAction (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ) (x : X) : A :=
  Classical.choose (univ.exists_min_image (cost π ℓ P x) univ_nonempty)

omit [Fintype X] in
theorem bestAction_le (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ) (x : X) (a : A) :
    cost π ℓ P x (bestAction π ℓ P x) ≤ cost π ℓ P x a :=
  (Classical.choose_spec (univ.exists_min_image (cost π ℓ P x) univ_nonempty)).2 a (mem_univ a)

/-- Population Bayes risk; finite actions make a deterministic optimum attain it. -/
noncomputable def bayesRisk (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ) : ℝ :=
  ∑ x, cost π ℓ P x (bestAction π ℓ P x)

def policyRisk (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ) (q : X → A → ℝ) : ℝ :=
  ∑ x, ∑ a, q x a * cost π ℓ P x a

theorem bayes_le_policy (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ)
    {q : X → A → ℝ} (hq : Stochastic q) : bayesRisk π ℓ P ≤ policyRisk π ℓ P q := by
  apply sum_le_sum
  intro x _
  calc cost π ℓ P x (bestAction π ℓ P x) =
      ∑ a, q x a * cost π ℓ P x (bestAction π ℓ P x) := by rw [← sum_mul, hq.2, one_mul]
    _ ≤ _ := sum_le_sum fun a _ => mul_le_mul_of_nonneg_left (bestAction_le π ℓ P x a) (hq.1 x a)

/-- A bounded-loss expectation changes by at most TV, with TV = half the L1 distance. -/
theorem bounded_expectation_tv (p q l : X → ℝ) (hmass : ∑ x, p x = ∑ x, q x)
    (hl : ∀ x, 0 ≤ l x ∧ l x ≤ 1) :
    |∑ x, (p x - q x) * l x| ≤ (∑ x, |p x - q x|) / 2 := by
  have hz : (∑ x, (p x - q x)) = 0 := by rw [sum_sub_distrib, hmass, sub_self]
  have heq : ∑ x, (p x - q x) * l x = ∑ x, (p x - q x) * (l x - 1 / 2) := by
    simp_rw [mul_sub]
    rw [sum_sub_distrib, ← sum_mul, hz, zero_mul, sub_zero]
  rw [heq]
  calc |∑ x, (p x - q x) * (l x - 1 / 2)| ≤ ∑ x, |(p x - q x) * (l x - 1 / 2)| :=
      abs_sum_le_sum_abs _ _
    _ ≤ ∑ x, |p x - q x| * (1 / 2) := by
      apply sum_le_sum
      intro x _
      rw [abs_mul]
      apply mul_le_mul_of_nonneg_left _ (abs_nonneg _)
      rw [abs_le]
      constructor <;> linarith [(hl x).1, (hl x).2]
    _ = _ := by rw [← sum_mul]; ring

/-- Optimal finite decision risk cannot fall after a stochastic garbling. -/
theorem garbling_risk (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ)
    {G : X → Z → ℝ} (hG : Stochastic G) :
    bayesRisk π ℓ P ≤ bayesRisk π ℓ (compose P G) := by
  calc
    bayesRisk π ℓ P ≤ (∑ x, ∑ z, G x z * cost π ℓ P x
        (bestAction π ℓ (compose P G) z)) := by
      apply sum_le_sum
      intro x _
      calc cost π ℓ P x (bestAction π ℓ P x) =
          ∑ z, G x z * cost π ℓ P x (bestAction π ℓ P x) := by
            rw [← sum_mul, hG.2, one_mul]
        _ ≤ _ := sum_le_sum fun z _ => mul_le_mul_of_nonneg_left
          (bestAction_le π ℓ P x _) (hG.1 x z)
    _ = bayesRisk π ℓ (compose P G) := by
      simp only [bayesRisk, cost, compose, mul_sum, sum_mul]
      rw [sum_comm]
      apply sum_congr rfl
      intro z _
      rw [sum_comm]
      apply sum_congr rfl
      intro θ _
      apply sum_congr rfl
      intro x _
      ring


omit [Fintype A] [Nonempty A] in
/-- Fixed-policy risk continuity under a prior-averaged TV bound. -/
theorem fixed_policy_tv (π : Θ → ℝ) (hπ : ∀ θ, 0 ≤ π θ) (ℓ : Θ → A → ℝ)
    (hl : ∀ θ a, 0 ≤ ℓ θ a ∧ ℓ θ a ≤ 1) (P Q : Θ → X → ℝ)
    (hmass : ∀ θ, ∑ x, P θ x = ∑ x, Q θ x) (f : X → A) :
    |(∑ x, cost π ℓ P x (f x)) - ∑ x, cost π ℓ Q x (f x)| ≤
      ∑ θ, π θ * ((∑ x, |P θ x - Q θ x|) / 2) := by
  have heq : (∑ x, cost π ℓ P x (f x)) - ∑ x, cost π ℓ Q x (f x) =
      ∑ θ, π θ * ∑ x, (P θ x - Q θ x) * ℓ θ (f x) := by
    simp only [cost, ← sum_sub_distrib]
    conv_lhs => arg 2; intro x; arg 2; intro θ; rw [show π θ * P θ x * ℓ θ (f x) -
      π θ * Q θ x * ℓ θ (f x) = π θ * ((P θ x - Q θ x) * ℓ θ (f x)) by ring]
    rw [sum_comm]
    simp_rw [mul_sum]
  rw [heq]
  calc _ ≤ ∑ θ, |π θ * ∑ x, (P θ x - Q θ x) * ℓ θ (f x)| := abs_sum_le_sum_abs _ _
    _ ≤ _ := sum_le_sum fun θ _ => by
      rw [abs_mul, abs_of_nonneg (hπ θ)]
      exact mul_le_mul_of_nonneg_left (bounded_expectation_tv (P θ) (Q θ)
        (fun x => ℓ θ (f x)) (hmass θ) (fun x => hl θ (f x))) (hπ θ)

/-- Optimal-risk continuity follows by evaluating the other experiment's optimal policy. -/
theorem bayes_risk_tv (π : Θ → ℝ) (hπ : ∀ θ, 0 ≤ π θ) (ℓ : Θ → A → ℝ)
    (hl : ∀ θ a, 0 ≤ ℓ θ a ∧ ℓ θ a ≤ 1) (P Q : Θ → X → ℝ)
    (hmass : ∀ θ, ∑ x, P θ x = ∑ x, Q θ x) :
    bayesRisk π ℓ P ≤ bayesRisk π ℓ Q +
      ∑ θ, π θ * ((∑ x, |P θ x - Q θ x|) / 2) := by
  have hb : bayesRisk π ℓ P ≤ ∑ x, cost π ℓ P x (bestAction π ℓ Q x) :=
    sum_le_sum fun x _ => bestAction_le π ℓ P x _
  have ht := (abs_le.mp (fixed_policy_tv π hπ ℓ hl P Q hmass (bestAction π ℓ Q))).2
  change (∑ x, cost π ℓ Q x (bestAction π ℓ Q x)) + _ ≥ _
  linarith

/-- Approximate sufficiency, with the fixed prior and half-L1 TV convention explicit. -/
theorem approximate_sufficiency (π : Θ → ℝ) (hπ : ∀ θ, 0 ≤ π θ)
    (ℓ : Θ → A → ℝ) (hl : ∀ θ a, 0 ≤ ℓ θ a ∧ ℓ θ a ≤ 1)
    {P : Θ → X → ℝ} {G : X → Z → ℝ} {D : Z → X → ℝ}
    (hP : Stochastic P) (hG : Stochastic G) (hD : Stochastic D) {ε : ℝ}
    (hε : (∑ θ, π θ * ((∑ x, |compose (compose P G) D θ x - P θ x|) / 2)) ≤ ε) :
    0 ≤ bayesRisk π ℓ (compose P G) - bayesRisk π ℓ P ∧
      bayesRisk π ℓ (compose P G) - bayesRisk π ℓ P ≤ ε := by
  have hrec := stochastic_compose (stochastic_compose hP hG) hD
  have hlower := garbling_risk π ℓ P hG
  have hupper := garbling_risk π ℓ (compose P G) hD
  have htv := bayes_risk_tv π hπ ℓ hl (compose (compose P G) D) P
    (fun θ => by rw [hrec.2, hP.2])
  constructor <;> linarith

end FreeFoundations.Decision
