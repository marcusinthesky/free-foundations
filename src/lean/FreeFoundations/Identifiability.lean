import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.Analysis.InnerProductSpace.Basic

/-!
# Observational equivalence and state-estimation risk

An invertible reparameterization of an unknown observation map leaves the observations
unchanged. This elementary construction becomes a statistical obstruction only if both
worlds remain admissible. The risk theorem works on a common coupling of those worlds:
the same observation record gives the same learner output, while the target states differ.
The record can include the training sample, query, and a randomized learner's seed.

The integrated bound concerns the maximum of the two expected risks, not the expectation
of their pointwise maximum. Explicit `MemLp` assumptions ensure that all squared-error
integrals are genuine finite risks. The bound does not assert that invariant economic
functionals are unidentified when state coordinates are unidentified.
-/

namespace FreeFoundations.Identifiability

section Exact

variable {S O : Type*}

/-- Reparameterizing both state and unknown observation map preserves every observation. -/
theorem reparameterized_observation (obs : S → O) (e : S ≃ S) (s : S) :
    (obs ∘ e.symm) (e s) = obs s := by simp

/-- A common learner cannot recover both numerical states when equivalent worlds disagree. -/
theorem not_both_exact (obs : S → O) (e : S ≃ S) (A : O → S) {s : S}
    (hs : e s ≠ s) :
    ¬ (A (obs s) = s ∧ A ((obs ∘ e.symm) (e s)) = e s) := by
  rintro ⟨hA, hB⟩
  rw [reparameterized_observation, hA] at hB
  exact hs hB.symm

/-- A concrete admissible coordinate ambiguity: observing a real number or the negation
of its negated state gives the same record, but the states `1` and `-1` cannot both be read. -/
theorem sign_ambiguity_example (A : ℝ → ℝ) : ¬ (A 1 = 1 ∧ A 1 = -1) := by
  simpa using not_both_exact id (Equiv.neg ℝ) A (s := 1) (by norm_num)

end Exact

section Risk

open MeasureTheory

variable {Ω E O : Type*} [MeasurableSpace Ω]
variable {μ : Measure Ω}
variable [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Squared state-estimation risk under a specified coupling measure. -/
noncomputable def risk (μ : Measure Ω) (state prediction : Ω → E) : ℝ :=
  ∫ ω, ‖prediction ω - state ω‖ ^ 2 ∂μ

/-- The Hilbert-space inequality underlying the two-world risk obstruction. -/
theorem two_state_sq_error (a b v : E) :
    ‖a - b‖ ^ 2 ≤ 2 * (‖v - a‖ ^ 2 + ‖v - b‖ ^ 2) := by
  have hp := parallelogram_law_with_norm ℝ (v - a) (v - b)
  have hsub : (v - a) - (v - b) = b - a := by abel
  rw [hsub, norm_sub_rev b a] at hp
  nlinarith [sq_nonneg ‖(v - a) + (v - b)‖]

omit [InnerProductSpace ℝ E] in
private theorem integrable_sq_sub {f g : Ω → E} (hf : MemLp f 2 μ) (hg : MemLp g 2 μ) :
    Integrable (fun ω => ‖f ω - g ω‖ ^ 2) μ :=
  (memLp_two_iff_integrable_sq_norm (hf.sub hg).1).mp (hf.sub hg)

/-- The sum of the two expected risks is at least half the expected squared state gap. -/
theorem risk_sum_lower_bound {a b v : Ω → E} (ha : MemLp a 2 μ) (hb : MemLp b 2 μ)
    (hv : MemLp v 2 μ) :
    (∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ) / 2 ≤ risk μ a v + risk μ b v := by
  have hab := integrable_sq_sub ha hb
  have hva := integrable_sq_sub hv ha
  have hvb := integrable_sq_sub hv hb
  have hi : (∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ) ≤
      2 * (risk μ a v + risk μ b v) := by
    calc (∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ)
        ≤ ∫ ω, 2 * (‖v ω - a ω‖ ^ 2 + ‖v ω - b ω‖ ^ 2) ∂μ :=
          integral_mono hab ((hva.add hvb).const_mul 2)
            (fun ω => two_state_sq_error (a ω) (b ω) (v ω))
      _ = 2 * (risk μ a v + risk μ b v) := by
        rw [integral_const_mul, integral_add hva hvb]
        rfl
  linarith

/-- For every common prediction, one world's expected risk is at least a quarter of
the expected squared separation between the worlds' targets. -/
theorem two_world_risk_lower_bound {a b v : Ω → E} (ha : MemLp a 2 μ) (hb : MemLp b 2 μ)
    (hv : MemLp v 2 μ) :
    (∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ) / 4 ≤ max (risk μ a v) (risk μ b v) := by
  have hsum := risk_sum_lower_bound ha hb hv
  linarith [le_max_left (risk μ a v) (risk μ b v),
    le_max_right (risk μ a v) (risk μ b v)]

/-- Observationally identical records, with a shared learner and random seed, give the
same prediction almost surely. No measurability of the learner beyond the stated `MemLp`
assumption is needed. -/
theorem same_observations_risk_lower_bound {a b : Ω → E} {obsA obsB : Ω → O}
    (hobs : obsA =ᵐ[μ] obsB) (A : O → E)
    (ha : MemLp a 2 μ) (hb : MemLp b 2 μ) (hv : MemLp (A ∘ obsA) 2 μ) :
    (∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ) / 4 ≤
      max (risk μ a (A ∘ obsA)) (risk μ b (A ∘ obsB)) := by
  have hr : risk μ b (A ∘ obsA) = risk μ b (A ∘ obsB) := by
    apply integral_congr_ae
    filter_upwards [hobs] with ω hω
    simp only [Function.comp_apply, hω]
  rw [← hr]
  exact two_world_risk_lower_bound ha hb hv

/-- The reparameterization construction specializes the risk obstruction. Both transformed
models must still be admissible, and transformed targets must remain square-integrable. -/
theorem reparameterized_risk_lower_bound {a : Ω → E} (e : E ≃ E) (obs : E → O) (A : O → E)
    (ha : MemLp a 2 μ) (hb : MemLp (e ∘ a) 2 μ) (hv : MemLp (A ∘ obs ∘ a) 2 μ) :
    (∫ ω, ‖a ω - e (a ω)‖ ^ 2 ∂μ) / 4 ≤
      max (risk μ a (A ∘ obs ∘ a))
        (risk μ (e ∘ a) (A ∘ (obs ∘ e.symm) ∘ (e ∘ a))) := by
  apply same_observations_risk_lower_bound (A := A) (a := a) (b := e ∘ a)
    (obsA := obs ∘ a) (obsB := (obs ∘ e.symm) ∘ (e ∘ a)) _ ha hb hv
  exact Filter.Eventually.of_forall fun ω => by simp

/-- A positive state gap forces a positive risk in at least one equivalent world. -/
theorem positive_risk_in_one_world {a b v : Ω → E} (ha : MemLp a 2 μ) (hb : MemLp b 2 μ)
    (hv : MemLp v 2 μ) (hgap : 0 < ∫ ω, ‖a ω - b ω‖ ^ 2 ∂μ) :
    0 < max (risk μ a v) (risk μ b v) := by
  have := two_world_risk_lower_bound ha hb hv
  linarith

/-- The quarter constant is sharp: for targets `1` and `-1`, every common prediction has
maximum risk at least `1`, and the constant prediction `0` attains it. -/
theorem constant_worlds_example [IsProbabilityMeasure μ] {v : Ω → ℝ} (hv : MemLp v 2 μ) :
    1 ≤ max (risk μ (fun _ => (1 : ℝ)) v) (risk μ (fun _ => (-1 : ℝ)) v) ∧
      max (risk μ (fun _ => (1 : ℝ)) (fun _ => 0))
        (risk μ (fun _ => (-1 : ℝ)) (fun _ => 0)) = 1 := by
  constructor
  · have h := two_world_risk_lower_bound
      (memLp_const (1 : ℝ) : MemLp (fun _ : Ω => (1 : ℝ)) 2 μ)
      (memLp_const (-1 : ℝ) : MemLp (fun _ : Ω => (-1 : ℝ)) 2 μ) hv
    norm_num at h
    exact le_max_iff.mpr h
  · norm_num [risk]

end Risk

end FreeFoundations.Identifiability
