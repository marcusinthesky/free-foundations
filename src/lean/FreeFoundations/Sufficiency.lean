import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic
import Mathlib.MeasureTheory.Function.FactorsThrough

/-!
# Statistical sufficiency

The probability-space form of `Alignment.optimal_imp_sufficient_iff`. The histories generate
a σ-algebra `mH`, and a representation computed from them generates `mZ ≤ mH`. Under squared
loss the pretraining target `X` has Bayes predictor `E[X | H]` and the economic target `Y`
has `E[Y | H]`; the best predictor of `X` from the representation is `E[X | Z]`, and its
excess risk over the Bayes predictor is `‖E[X | Z] − E[X | H]‖²` (`Recovery.excess_risk_condExp`).

* A representation attains the pretraining optimum, `E[X | Z] = E[X | H]` a.s., exactly when
  `E[X | H]` is a.s. a function of it (`condExp_eq_iff`).
* Every representation that attains it also attains the economic optimum iff
  `E[Y | H] = g(E[X | H])` a.s. for some measurable `g` (`sufficient_iff`).
* With a label-null target, every representation attains the pretraining optimum, so the
  guarantee holds only for an economic target that is a.s. constant (`constant_target_iff`).

So an objective guarantees economic sufficiency only when the economic prediction is a
measurable function of the pretraining prediction. A conditional law is covered by applying
the result to the indicators `Y = 1{Y_c ∈ B}`, one task at a time. When the condition fails,
the objective alone guarantees nothing; whatever a particular non-optimal checkpoint happens
to keep has to be measured, not inferred from its loss.
-/

namespace FreeFoundations.Sufficiency

open MeasureTheory

variable {Ω : Type*} {m0 : MeasurableSpace Ω} {μ : Measure Ω} [IsFiniteMeasure μ]
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E] [CompleteSpace E]

/-- **Attaining the Bayes predictor.** A representation `mZ ≤ mH` reproduces `E[X | H]` iff
`E[X | H]` is a.s. `mZ`-measurable. -/
theorem condExp_eq_iff {mZ mH : MeasurableSpace Ω} (hZH : mZ ≤ mH) (hH : mH ≤ m0)
    (X : Ω → E) :
    μ[X | mZ] =ᵐ[μ] μ[X | mH] ↔ AEStronglyMeasurable[mZ] (μ[X | mH]) μ := by
  constructor
  · intro h
    exact ⟨μ[X | mZ], stronglyMeasurable_condExp, h.symm⟩
  · intro h
    exact (condExp_condExp_of_le (f := X) hZH hH).symm.trans
      (condExp_of_aestronglyMeasurable' (hZH.trans hH) h integrable_condExp)

variable [MeasurableSpace E] [BorelSpace E] [SecondCountableTopology E]

/-- **Statistical alignment.** Every representation that reproduces the pretraining Bayes
predictor `E[X | H]` also reproduces the economic one `E[Y | H]` iff the latter is a.s. a
measurable function of the former. -/
theorem sufficient_iff {mH : MeasurableSpace Ω} (hH : mH ≤ m0) (X : Ω → E) (Y : Ω → ℝ) :
    (∀ mZ : MeasurableSpace Ω, mZ ≤ mH →
        μ[X | mZ] =ᵐ[μ] μ[X | mH] → μ[Y | mZ] =ᵐ[μ] μ[Y | mH]) ↔
      ∃ g : E → ℝ, Measurable g ∧ μ[Y | mH] =ᵐ[μ] g ∘ μ[X | mH] := by
  have hF : StronglyMeasurable[mH] (μ[X | mH]) := stronglyMeasurable_condExp
  constructor
  · intro hall
    set mZ := MeasurableSpace.comap (μ[X | mH]) (inferInstance : MeasurableSpace E)
    have hle : mZ ≤ mH := hF.measurable.comap_le
    have hX : μ[X | mZ] =ᵐ[μ] μ[X | mH] := (condExp_eq_iff hle hH X).mpr
      (comap_measurable (μ[X | mH])).stronglyMeasurable.aestronglyMeasurable
    obtain ⟨g', hg', hYg'⟩ := (condExp_eq_iff hle hH Y).mp (hall mZ hle hX)
    obtain ⟨g, hg, rfl⟩ := hg'.exists_eq_measurable_comp
    exact ⟨g, hg.measurable, hYg'⟩
  · rintro ⟨g, hg, hYg⟩ mZ hZH hX
    obtain ⟨F', hF', hFF'⟩ := (condExp_eq_iff hZH hH X).mp hX
    exact (condExp_eq_iff hZH hH Y).mpr
      ⟨g ∘ F', (hg.comp hF'.measurable).stronglyMeasurable, hYg.trans (hFF'.fun_comp g)⟩

/-- **Label-null.** If the pretraining prediction is a.s. constant, as with constant support
labels, every representation reproduces it, so the objective guarantees economic sufficiency
only for an economic prediction that is itself a.s. constant. -/
theorem constant_target_iff {mH : MeasurableSpace Ω} (hH : mH ≤ m0) (X : Ω → E) (Y : Ω → ℝ)
    {c : E} (hc : μ[X | mH] =ᵐ[μ] fun _ => c) :
    (∀ mZ : MeasurableSpace Ω, mZ ≤ mH →
        μ[X | mZ] =ᵐ[μ] μ[X | mH] → μ[Y | mZ] =ᵐ[μ] μ[Y | mH]) ↔
      ∃ c' : ℝ, μ[Y | mH] =ᵐ[μ] fun _ => c' := by
  rw [sufficient_iff hH X Y]
  constructor
  · rintro ⟨g, -, hYg⟩
    exact ⟨g c, hYg.trans (hc.fun_comp g)⟩
  · rintro ⟨c', hc'⟩
    exact ⟨fun _ => c', measurable_const, hc'⟩

end FreeFoundations.Sufficiency
