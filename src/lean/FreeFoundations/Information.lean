import FreeFoundations.Recovery

/-!
# The value of richer information

The claim is about optimal population projection risk. It supplies neither a
finite-learning rate nor a monotonicity claim for arbitrary fitted representations.
-/

namespace FreeFoundations.Information

open MeasureTheory

/-- Nested information reduces optimal squared error by exactly the squared
change in the optimal predictor. -/
theorem nested_projection {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (G H : Submodule ℝ E) [G.HasOrthogonalProjection] [H.HasOrthogonalProjection]
    (hGH : G ≤ H) (a : E) :
    ‖a - G.starProjection a‖ ^ 2 - ‖a - H.starProjection a‖ ^ 2 =
      ‖H.starProjection a - G.starProjection a‖ ^ 2 := by
  have h := Recovery.excess_risk H a (G.starProjection a)
    (hGH (G.starProjection_apply_mem a))
  simpa only [norm_sub_rev] using h

theorem projection_risk_mono {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (G H : Submodule ℝ E) [G.HasOrthogonalProjection] [H.HasOrthogonalProjection]
    (hGH : G ≤ H) (a : E) :
    ‖a - H.starProjection a‖ ^ 2 ≤ ‖a - G.starProjection a‖ ^ 2 := by
  have h := nested_projection G H hGH a
  nlinarith [sq_nonneg ‖H.starProjection a - G.starProjection a‖]

/-- The nested projection identity instantiated at L² conditional expectations.
The L² quotient records equality almost everywhere. -/
theorem nested_condExp {Ω E : Type*} {mG mH m0 : MeasurableSpace Ω}
    {μ : Measure Ω} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hGH : mG ≤ mH) (hH : mH ≤ m0) (a : Lp E 2 μ) :
    ‖a - (condExpL2 E ℝ (hGH.trans hH) a : Lp E 2 μ)‖ ^ 2 -
        ‖a - (condExpL2 E ℝ hH a : Lp E 2 μ)‖ ^ 2 =
      ‖(condExpL2 E ℝ hH a : Lp E 2 μ) -
        (condExpL2 E ℝ (hGH.trans hH) a : Lp E 2 μ)‖ ^ 2 := by
  haveI : Fact (mG ≤ m0) := ⟨hGH.trans hH⟩
  haveI : Fact (mH ≤ m0) := ⟨hH⟩
  apply nested_projection (lpMeas E ℝ mG 2 μ) (lpMeas E ℝ mH 2 μ) ?_ a
  intro f hf
  exact mem_lpMeas_iff_aestronglyMeasurable.mpr
    ((mem_lpMeas_iff_aestronglyMeasurable.mp hf).mono hGH)

end FreeFoundations.Information
