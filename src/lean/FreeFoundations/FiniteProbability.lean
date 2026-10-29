module

public import MathEconLib.Probability.FinDist.Basic
public import MathEconLib.Probability.FinDist.Expect
public import MathEconLib.Probability.FinDist.ConditionalOn
public import MathEconLib.Probability.FinDist.Measure
public import Mathlib.MeasureTheory.Function.LpSeminorm.LpNorm
public import FreeFoundations.Transfer

/-!
# MathEconLib finite laws at the financial measurement interface

The probability objects and their elementary operations below are aliases or adapters to
the pinned MathEconLib dependency. Its definitions and proofs are imported directly, not
reimplemented locally. Real-parameter mixture and positive-event conditioning adapters keep
the existing project API. RMS, overlap, kernel and financial-transfer bridges are local.
The raw-weight and subprobability interfaces in `Transfer` remain available.
-/

@[expose] public noncomputable section

namespace FreeFoundations.FiniteProbability

open MeasureTheory Finset

/-- The actual MathEconLib finite probability law. -/
abbrev FinDist (X : Type*) [Fintype X] := MathEconLib.Probability.FinDist X

variable {X Y Z I E : Type*} [Fintype X] [Fintype Y] [Fintype Z] [Fintype I]

theorem nonneg (p : FinDist X) (x : X) : 0 ≤ p x :=
  MathEconLib.Probability.FinDist.nonneg p x

theorem sum_one (p : FinDist X) : ∑ x, p x = 1 :=
  MathEconLib.Probability.FinDist.sum_one p

/-- A deterministic finite law. -/
def pure (x : X) : FinDist X := by
  classical
  exact MathEconLib.Probability.FinDist.pure x

@[simp] theorem pure_apply [DecidableEq X] (x y : X) :
    pure x y = if y = x then 1 else 0 := by
  classical
  simp only [pure, MathEconLib.Probability.FinDist.pure_apply, eq_comm]
  split_ifs <;> rfl

/-- The uniform finite law requires a nonempty outcome space. -/
abbrev uniform [Nonempty X] : FinDist X := MathEconLib.Probability.FinDist.uniform

@[simp] theorem uniform_apply [Nonempty X] (x : X) : uniform (X := X) x =
    (Fintype.card X : ℝ)⁻¹ := MathEconLib.Probability.FinDist.uniform_apply x

/-- Expectation in any real module; the integrability bridge below adds completeness. -/
abbrev expect [AddCommMonoid E] [Module ℝ E] (p : FinDist X) (f : X → E) : E :=
  MathEconLib.Probability.FinDist.expect p f

theorem expect_const [AddCommMonoid E] [Module ℝ E] (p : FinDist X) (c : E) :
    expect p (fun _ => c) = c := MathEconLib.Probability.FinDist.expect_const p c

@[simp] theorem expect_pure [AddCommMonoid E] [Module ℝ E] (x : X) (f : X → E) :
    expect (pure x) f = f x := by
  classical
  exact MathEconLib.Probability.FinDist.expect_pure x f

theorem expect_uniform [AddCommMonoid E] [Module ℝ E] [Nonempty X] (f : X → E) :
    expect (uniform : FinDist X) f = (Fintype.card X : ℝ)⁻¹ • ∑ x, f x := by
  simp only [expect, MathEconLib.Probability.FinDist.expect_eq_sum,
    MathEconLib.Probability.FinDist.uniform_pmf, smul_sum]

theorem expect_add [AddCommMonoid E] [Module ℝ E] (p : FinDist X) (f g : X → E) :
    expect p (fun x => f x + g x) = expect p f + expect p g :=
  MathEconLib.Probability.FinDist.expect_add p f g

theorem expect_smul [AddCommMonoid E] [Module ℝ E] (p : FinDist X) (c : ℝ) (f : X → E) :
    expect p (fun x => c • f x) = c • expect p f :=
  MathEconLib.Probability.FinDist.expect_smul p c f

/-- At a point mass the RMS is the norm at that point, regardless of other atom values. -/
@[simp] theorem rms_pure [NormedAddCommGroup E] [NormedSpace ℝ E] (x : X) (f : X → E) :
    Transfer.rms (pure x : X → ℝ) f = ‖f x‖ := by
  classical
  have hs := Transfer.rms_sq (pure x : X → ℝ) (nonneg (pure x)) f
  simp only [pure_apply, ite_mul, one_mul, zero_mul, sum_ite_eq', mem_univ, ite_true] at hs
  nlinarith [Transfer.rms_nonneg (pure x : X → ℝ) f, norm_nonneg (f x)]

/-- A zero-mass atom may change arbitrarily without affecting the finite RMS. -/
theorem zero_mass_atom_irrelevant (a b c : ℝ) :
    Transfer.rms (pure (0 : Fin 2) : Fin 2 → ℝ) ![a, b] =
      Transfer.rms (pure (0 : Fin 2) : Fin 2 → ℝ) ![a, c] ∧
      pure (0 : Fin 2) 1 = 0 := by
  constructor
  · rw [rms_pure, rms_pure]
    rfl
  · simp

theorem expect_nonneg (p : FinDist X) {f : X → ℝ} (hf : ∀ x, 0 ≤ f x) :
    0 ≤ expect p f := MathEconLib.Probability.FinDist.expect_nonneg p f hf

theorem expect_mono (p : FinDist X) {f g : X → ℝ} (hfg : ∀ x, f x ≤ g x) :
    expect p f ≤ expect p g := MathEconLib.Probability.FinDist.expect_mono p f g hfg

/-- Finite mixture with normalized mixing weights. No positivity of each atom is required. -/
abbrev finMixture (weights : FinDist I) (laws : I → FinDist X) : FinDist X :=
  MathEconLib.Probability.FinDist.finMixture weights laws

@[simp] theorem finMixture_apply (weights : FinDist I) (laws : I → FinDist X) (x : X) :
    finMixture weights laws x = ∑ i, weights i * laws i x :=
  MathEconLib.Probability.FinDist.finMixture_pmf weights laws x

/-- Vector-valued iterated finite expectation. -/
theorem expect_finMixture [AddCommMonoid E] [Module ℝ E]
    (weights : FinDist I) (laws : I → FinDist X) (f : X → E) :
    expect (finMixture weights laws) f = expect weights (fun i => expect (laws i) f) := by
  simp only [expect, MathEconLib.Probability.FinDist.expect_eq_sum,
    MathEconLib.Probability.FinDist.pmf_eq_coe, finMixture_apply, sum_smul, mul_smul, smul_sum]
  rw [sum_comm]

/-- Binary mixing weights, including the two endpoint laws. -/
def binaryWeights (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1) : FinDist (Fin 2) :=
  MathEconLib.Probability.FinDist.mixture ⟨t, ht, ht1⟩ (pure 0) (pure 1)

@[simp] theorem binaryWeights_zero (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1) :
    binaryWeights t ht ht1 0 = t := by
  change (MathEconLib.Probability.FinDist.mixture ⟨t, ht, ht1⟩ (pure 0) (pure 1)).pmf 0 = t
  rw [MathEconLib.Probability.FinDist.mixture_pmf]
  simp only [MathEconLib.Probability.FinDist.pmf_eq_coe, pure_apply]
  norm_num

@[simp] theorem binaryWeights_one (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1) :
    binaryWeights t ht ht1 1 = 1 - t := by
  change (MathEconLib.Probability.FinDist.mixture ⟨t, ht, ht1⟩ (pure 0) (pure 1)).pmf 1 = 1 - t
  rw [MathEconLib.Probability.FinDist.mixture_pmf]
  simp only [MathEconLib.Probability.FinDist.pmf_eq_coe, pure_apply]
  norm_num

abbrev mixture (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1) (p q : FinDist X) : FinDist X :=
  MathEconLib.Probability.FinDist.mixture ⟨t, ht, ht1⟩ p q

@[simp] theorem mixture_apply (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1)
    (p q : FinDist X) (x : X) : mixture t ht ht1 p q x = t * p x + (1 - t) * q x :=
  MathEconLib.Probability.FinDist.mixture_pmf ⟨t, ht, ht1⟩ p q x

theorem expect_mixture [AddCommMonoid E] [Module ℝ E] (t : ℝ) (ht : 0 ≤ t) (ht1 : t ≤ 1)
    (p q : FinDist X) (f : X → E) :
    expect (mixture t ht ht1 p q) f = t • expect p f + (1 - t) • expect q f :=
  MathEconLib.Probability.FinDist.expect_mixture ⟨t, ht, ht1⟩ p q f

@[simp] theorem mixture_zero (p q : FinDist X) : mixture 0 (by norm_num) (by norm_num) p q = q := by
  apply Subtype.ext
  funext x
  change mixture 0 (by norm_num) (by norm_num) p q x = q x
  rw [mixture_apply]
  ring

@[simp] theorem mixture_one (p q : FinDist X) : mixture 1 (by norm_num) (by norm_num) p q = p := by
  apply Subtype.ext
  funext x
  change mixture 1 (by norm_num) (by norm_num) p q x = p x
  rw [mixture_apply]
  ring

/-- The finite probability mass function represented by the real simplex weights. -/
abbrev toPMF (p : FinDist X) : PMF X := MathEconLib.Probability.FinDist.toPMF p

@[simp] theorem toPMF_apply (p : FinDist X) (x : X) :
    toPMF p x = ENNReal.ofReal (p x) := rfl

abbrev ofPMF (p : PMF X) : FinDist X := MathEconLib.Probability.FinDist.ofPMF p

@[simp] theorem toPMF_ofPMF (p : PMF X) : toPMF (ofPMF p) = p :=
  MathEconLib.Probability.FinDist.toPMF_ofPMF p

@[simp] theorem ofPMF_toPMF (p : FinDist X) : ofPMF (toPMF p) = p := by
  apply Subtype.ext
  funext x
  exact ENNReal.toReal_ofReal (nonneg p x)

def pmfEquiv : FinDist X ≃ PMF X where
  toFun := toPMF
  invFun := ofPMF
  left_inv := ofPMF_toPMF
  right_inv := toPMF_ofPMF

section Measure

variable [MeasurableSpace X] [MeasurableSingletonClass X]

abbrev toMeasure (p : FinDist X) : Measure X := MathEconLib.Probability.FinDist.toMeasure p

instance probability_toMeasure (p : FinDist X) : IsProbabilityMeasure (toMeasure p) :=
  inferInstance

/-- Only a probability measure can enter this normalized finite-law constructor. -/
def ofMeasure (μ : Measure X) [IsProbabilityMeasure μ] : FinDist X := ofPMF μ.toPMF

@[simp] theorem toMeasure_ofMeasure (μ : Measure X) [IsProbabilityMeasure μ] :
    toMeasure (ofMeasure μ) = μ := by
  simp only [toMeasure, MathEconLib.Probability.FinDist.toMeasure,
    ofMeasure, toPMF_ofPMF, Measure.toPMF_toMeasure]

@[simp] theorem ofMeasure_toMeasure (p : FinDist X) : ofMeasure (toMeasure p) = p := by
  simp only [ofMeasure, toMeasure, MathEconLib.Probability.FinDist.toMeasure,
    PMF.toMeasure_toPMF, ofPMF_toPMF]

@[simp] theorem toMeasure_singleton (p : FinDist X) (x : X) :
    toMeasure p {x} = ENNReal.ofReal (p x) :=
  PMF.toMeasure_apply_singleton _ _ (measurableSet_singleton x)

@[simp] theorem toMeasure_real_singleton (p : FinDist X) (x : X) :
    (toMeasure p).real {x} = p x := by
  rw [measureReal_def, toMeasure_singleton, ENNReal.toReal_ofReal (nonneg p x)]

theorem integrable [NormedAddCommGroup E] (p : FinDist X) (f : X → E) :
    Integrable f (toMeasure p) := MathEconLib.Probability.FinDist.integrable_toMeasure p f

theorem integral_eq_expect [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]
    (p : FinDist X) (f : X → E) : (∫ x, f x ∂toMeasure p) = expect p f :=
  (MathEconLib.Probability.FinDist.expect_eq_integral p f).symm

/-- Finite RMS and measure-theoretic second moments use exactly the same weights. -/
theorem rms_sq_eq_integral [NormedAddCommGroup E] [NormedSpace ℝ E]
    (p : FinDist X) (f : X → E) :
    Transfer.rms (p : X → ℝ) f ^ 2 = ∫ x, ‖f x‖ ^ 2 ∂toMeasure p := by
  rw [integral_eq_expect, expect, MathEconLib.Probability.FinDist.expect_eq_sum,
    Transfer.rms_sq _ (nonneg p)]
  rfl

/-- The finite Euclidean weighted RMS is the population L² seminorm under the
associated measure, including distributions with zero-mass atoms. -/
theorem eLpNorm_eq_ofReal_rms [NormedAddCommGroup E] [NormedSpace ℝ E]
    (p : FinDist X) (f : X → E) :
    eLpNorm f 2 (toMeasure p) = ENNReal.ofReal (Transfer.rms (p : X → ℝ) f) := by
  have hmeas := (integrable p f).aestronglyMeasurable
  have hmem : MemLp f 2 (toMeasure p) :=
    (memLp_two_iff_integrable_sq_norm hmeas).mpr (integrable p (fun x => ‖f x‖ ^ 2))
  have he : (eLpNorm f 2 (toMeasure p)).toReal = Transfer.rms (p : X → ℝ) f := by
    rw [toReal_eLpNorm, lpNorm_eq_integral_norm_rpow_toReal (by norm_num) (by norm_num) hmeas]
    norm_num only [ENNReal.toReal_ofNat, Real.rpow_two, one_div]
    rw [← Real.sqrt_eq_rpow, ← rms_sq_eq_integral, Real.sqrt_sq (Transfer.rms_nonneg _ _)]
  rw [← he, ENNReal.ofReal_toReal hmem.eLpNorm_ne_top]

/-- Pointwise overlap is equivalent to measure domination on the finite discrete space. -/
theorem domination_iff (p q : FinDist X) {ω : ℝ} (hω : 0 ≤ ω) :
    (∀ x, q x ≤ ω * p x) ↔ toMeasure q ≤ ENNReal.ofReal ω • toMeasure p := by
  constructor
  · intro h
    apply Measure.le_iff.mpr
    intro s hs
    rw [toMeasure, MathEconLib.Probability.FinDist.toMeasure,
      PMF.toMeasure_apply_fintype, Measure.smul_apply, toMeasure,
      MathEconLib.Probability.FinDist.toMeasure, PMF.toMeasure_apply_fintype,
      smul_eq_mul, mul_sum]
    apply sum_le_sum
    intro x _
    by_cases hx : x ∈ s
    · simp only [Set.indicator_of_mem hx, toPMF_apply]
      rw [← ENNReal.ofReal_mul hω]
      exact ENNReal.ofReal_le_ofReal (h x)
    · simp [Set.indicator_of_notMem hx]
  · intro h x
    have hx := Measure.le_iff.mp h {x} (measurableSet_singleton x)
    rw [Measure.smul_apply, smul_eq_mul, toMeasure_singleton, toMeasure_singleton,
      ← ENNReal.ofReal_mul hω] at hx
    exact (ENNReal.ofReal_le_ofReal_iff (mul_nonneg hω (nonneg p x))).mp hx

end Measure

/-- Typed stochastic kernels are functions into the finite simplex. -/
abbrev FinKernel (X Y : Type*) [Fintype Y] := X → FinDist Y

def kernelComp (K : FinKernel X Y) (H : FinKernel Y Z) : FinKernel X Z :=
  fun x => finMixture (K x) H

omit [Fintype X] in
@[simp] theorem kernelComp_apply (K : FinKernel X Y) (H : FinKernel Y Z) (x : X) (z : Z) :
    kernelComp K H x z = ∑ y, K x y * H y z := rfl

abbrev probEvent (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)] : ℝ :=
  MathEconLib.Probability.FinDist.probEvent p s

theorem probEvent_nonneg (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)] :
    0 ≤ probEvent p s := MathEconLib.Probability.FinDist.probEvent_nonneg p s

@[simp] theorem probEvent_empty (p : FinDist X) : probEvent p ∅ = 0 := by
  simp [probEvent, MathEconLib.Probability.FinDist.probEvent_eq_sum_ite]

/-- A null event cannot supply the premise of the strict conditioning interface. -/
theorem null_event_not_conditionable (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)]
    (hzero : probEvent p s = 0) : ¬ 0 < probEvent p s := by rw [hzero]; exact lt_irrefl 0

/-- Conditioning is only exposed for an event with strictly positive probability. -/
abbrev conditionalOn (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)]
    (hpos : 0 < probEvent p s) : FinDist X :=
  MathEconLib.Probability.FinDist.conditionalOn p s hpos

@[simp] theorem conditionalOn_apply (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)]
    (hpos : 0 < probEvent p s) (x : X) :
    conditionalOn p s hpos x = if x ∈ s then p x / probEvent p s else 0 := by
  simpa only [MathEconLib.Probability.FinDist.condProb_eq_ite, hpos, and_true] using
    MathEconLib.Probability.FinDist.conditionalOn_apply p s hpos x

/-- Conditional expectation has the usual numerator/positive-event-mass formula. -/
theorem expect_conditionalOn [AddCommMonoid E] [Module ℝ E]
    (p : FinDist X) (s : Set X) [DecidablePred (· ∈ s)]
    (hpos : 0 < probEvent p s) (f : X → E) :
    expect (conditionalOn p s hpos) f =
      (probEvent p s)⁻¹ • ∑ x, if x ∈ s then p x • f x else 0 := by
  rw [expect, MathEconLib.Probability.FinDist.expect_eq_sum, smul_sum]
  simp only [MathEconLib.Probability.FinDist.pmf_eq_coe]
  apply sum_congr rfl
  intro x _
  by_cases hx : x ∈ s
  · simp only [conditionalOn_apply, ite_eq_left hx, div_eq_mul_inv, mul_smul]
    exact smul_comm _ _ _
  · simp [conditionalOn_apply, hx]

/-- Typed finite source/target transfer reuses the raw-weight theorem. -/
theorem task_transfer [NormedAddCommGroup E] [NormedSpace ℝ E]
    (p q : FinDist X) {ω : ℝ} (hω : 0 ≤ ω) (hqp : ∀ x, q x ≤ ω * p x)
    (pred source target : X → E) :
    Transfer.rms (q : X → ℝ) (fun x => pred x - target x) ≤
      Real.sqrt ω * Transfer.rms (p : X → ℝ) (fun x => pred x - source x) +
        Transfer.rms (q : X → ℝ) (fun x => source x - target x) :=
  Transfer.task_transfer (nonneg p) (nonneg q) hω hqp pred source target

end FreeFoundations.FiniteProbability
