import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.MeasureTheory.Function.ConditionalExpectation.CondexpL2

/-!
# Recovering exposure distance from auxiliary tasks

The central measurement result. Exposures `a ∈ A` are the risk-scaled responses
`Ω^{1/2}b(S)` to the declared common shocks, so `‖aᵢ − aⱼ‖` is the economic distance. A
vector of auxiliary targets `τ ∈ T` (support labels, pretext outcomes) has conditional mean
`τ = C a + v`, with `v` the task–state mismatch. The tasks *distinguish* the exposures
with margin `κ` when `‖C a‖ ≥ κ‖a‖`, that is when `σ_min(C) ≥ κ`.

Then a decoder exists (the Moore–Penrose pseudoinverse), and

* exposure error ≤ (task error + mismatch) / κ;
* each pairwise distance moves by at most the two firms' exposure errors;
* the mean squared distance error over pairs is at most `4/N` times the summed squared
  exposure errors, with no independence across pairs.

Task accuracy sets the numerator, task diversity sets `κ`, and no amount of accuracy
removes the mismatch `v`. Limits sit beside the positive result. Distinguishing needs at
least as many task dimensions as exposure dimensions, so one scalar target, such as a single
in-context support label, cannot do it for exposures of dimension two or more
(`scalar_not_distinguishes`). An aggregate target merges economically distinct firms, and
two distinct targets can separate them. The decoder exists given `C`; it is not identified
from task outputs alone (`Geometry.observationally_equivalent`).
-/

namespace FreeFoundations.Recovery

open InnerProductSpace

variable {A T : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
  [NormedAddCommGroup T] [InnerProductSpace ℝ T]

/-- The tasks `C` distinguish every exposure direction with margin `κ`: `σ_min(C) ≥ κ`. -/
def Distinguishes (C : A →ₗ[ℝ] T) (κ : ℝ) : Prop := ∀ a, κ * ‖a‖ ≤ ‖C a‖

/-- Tasks that distinguish exposures with a positive margin lose no exposure direction. -/
theorem Distinguishes.injective {C : A →ₗ[ℝ] T} {κ : ℝ} (hC : Distinguishes C κ) (hκ : 0 < κ) :
    Function.Injective C := by
  rw [← LinearMap.ker_eq_bot, LinearMap.ker_eq_bot']
  intro a ha
  have h := hC a
  rw [ha, norm_zero] at h
  exact norm_le_zero_iff.mp (nonpos_of_mul_nonpos_right h hκ)

/-- **Dimension.** Tasks that distinguish exposures need at least as many dimensions as the
exposures. -/
theorem finrank_le_of_distinguishes [FiniteDimensional ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ}
    (hC : Distinguishes C κ) (hκ : 0 < κ) : Module.finrank ℝ A ≤ Module.finrank ℝ T :=
  LinearMap.finrank_le_finrank_of_injective (hC.injective hκ)

/-- **One target is not enough.** A single scalar task cannot distinguish exposures of
dimension two or more, however accurately it is predicted. Multiple hidden coordinates do not
help: the margin is a property of the tasks, not of the representation. -/
theorem scalar_not_distinguishes (hA : 2 ≤ Module.finrank ℝ A) (C : A →ₗ[ℝ] ℝ) {κ : ℝ}
    (hκ : 0 < κ) : ¬ Distinguishes C κ := fun hC => by
  have := finrank_le_of_distinguishes hC hκ
  rw [Module.finrank_self] at this
  omega

/-- A left inverse of the tasks whose gain is at most `1/κ`. -/
structure Decoder (C : A →ₗ[ℝ] T) (κ : ℝ) (L : T →ₗ[ℝ] A) : Prop where
  left_inv : ∀ a, L (C a) = a
  bound : ∀ y, κ * ‖L y‖ ≤ ‖y‖

/-- **Decoder.** Tasks that distinguish exposures with a positive margin admit a decoder:
project onto the tasks' range, then invert there. -/
theorem exists_decoder [FiniteDimensional ℝ A] {C : A →ₗ[ℝ] T} {κ : ℝ} (hκ : 0 < κ)
    (hC : Distinguishes C κ) : ∃ L, Decoder C κ L := by
  have hinj : Function.Injective C := hC.injective hκ
  set K := LinearMap.range C
  let e := LinearEquiv.ofInjective C hinj
  let P := K.orthogonalProjectionOnto
  refine ⟨e.symm.toLinearMap ∘ₗ P.toLinearMap, ⟨fun a => ?_, fun y => ?_⟩⟩
  · have hP : P (C a) = e a :=
      Subtype.ext (by
        simp [P, e, Submodule.orthogonalProjectionOnto_mem_subspace_eq_self
          (K := K) ⟨C a, LinearMap.mem_range_self C a⟩])
    simp [hP]
  · have hCx : C (e.symm (P y)) = (P y : T) := by
      simp [e]
    calc κ * ‖(e.symm.toLinearMap ∘ₗ P.toLinearMap) y‖ = κ * ‖e.symm (P y)‖ := rfl
      _ ≤ ‖C (e.symm (P y))‖ := hC _
      _ = ‖P y‖ := by rw [hCx]; rfl
      _ ≤ ‖y‖ := K.norm_orthogonalProjectionOnto_apply_le y

variable {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}

/-- **Exposure error.** Decoding a task forecast `τ̂` misses the exposure by at most the
forecast's error over `κ`. -/
theorem exposure_error (hL : Decoder C κ L) (a : A) (τhat : T) :
    κ * ‖L τhat - a‖ ≤ ‖τhat - C a‖ := by
  have : L τhat - a = L (τhat - C a) := by rw [map_sub, hL.left_inv]
  rw [this]
  exact hL.bound _

/-- **With mismatch.** When the conditional task mean is `τ = C a + v`, the decoded
exposure error is bounded by the forecast error plus the mismatch, over `κ`. -/
theorem exposure_error_mismatch (hL : Decoder C κ L) (hκ : 0 ≤ κ) (a : A) (v τhat : T) :
    κ * ‖L τhat - a‖ ≤ ‖τhat - (C a + v)‖ + ‖v‖ := by
  have hsplit : L τhat - a = L (τhat - (C a + v)) + L v := by
    rw [map_sub, map_add, hL.left_inv]
    abel
  calc κ * ‖L τhat - a‖ ≤ κ * ‖L (τhat - (C a + v))‖ + κ * ‖L v‖ := by
        rw [hsplit, ← mul_add]
        exact mul_le_mul_of_nonneg_left (norm_add_le _ _) hκ
    _ ≤ _ := add_le_add (hL.bound _) (hL.bound _)

/-- The squared form: `κ²‖â − a‖² ≤ 2(‖τ̂ − τ‖² + ‖v‖²)`. -/
theorem exposure_error_mismatch_sq (hL : Decoder C κ L) (hκ : 0 ≤ κ) (a : A) (v τhat : T) :
    κ ^ 2 * ‖L τhat - a‖ ^ 2 ≤ 2 * (‖τhat - (C a + v)‖ ^ 2 + ‖v‖ ^ 2) := by
  have h := exposure_error_mismatch hL hκ a v τhat
  have h0 : 0 ≤ κ * ‖L τhat - a‖ := mul_nonneg hκ (norm_nonneg _)
  calc κ ^ 2 * ‖L τhat - a‖ ^ 2 = (κ * ‖L τhat - a‖) ^ 2 := by ring
    _ ≤ (‖τhat - (C a + v)‖ + ‖v‖) ^ 2 := pow_le_pow_left₀ h0 h 2
    _ ≤ _ := by nlinarith [sq_nonneg (‖τhat - (C a + v)‖ - ‖v‖)]

/-- **In mean square.** For any measure over firms, information sets or both, the mean
squared exposure error is at most the mean squared task error over `κ²`. A finite sample is
the case of a counting measure. -/
theorem mean_exposure_error {Ω : Type*} [MeasurableSpace Ω] (μ : MeasureTheory.Measure Ω)
    (hL : Decoder C κ L) (hκ : 0 ≤ κ) (a : Ω → A) (τhat : Ω → T)
    (hint : MeasureTheory.Integrable (fun ω => ‖τhat ω - C (a ω)‖ ^ 2) μ) :
    κ ^ 2 * ∫ ω, ‖L (τhat ω) - a ω‖ ^ 2 ∂μ ≤ ∫ ω, ‖τhat ω - C (a ω)‖ ^ 2 ∂μ := by
  rw [← MeasureTheory.integral_const_mul]
  refine MeasureTheory.integral_mono_of_nonneg (Filter.Eventually.of_forall fun ω => ?_) hint
    (Filter.Eventually.of_forall fun ω => ?_)
  · positivity
  · have h := exposure_error hL (a ω) (τhat ω)
    have h0 : 0 ≤ κ * ‖L (τhat ω) - a ω‖ := mul_nonneg hκ (norm_nonneg _)
    calc κ ^ 2 * ‖L (τhat ω) - a ω‖ ^ 2 = (κ * ‖L (τhat ω) - a ω‖) ^ 2 := by ring
      _ ≤ _ := pow_le_pow_left₀ h0 h 2

/-! ## From exposures to distances -/

omit [InnerProductSpace ℝ A] in
/-- **Distance error.** A pairwise distance moves by at most the two exposure errors. -/
theorem distance_error (ahᵢ aᵢ ahⱼ aⱼ : A) :
    |‖ahᵢ - ahⱼ‖ - ‖aᵢ - aⱼ‖| ≤ ‖ahᵢ - aᵢ‖ + ‖ahⱼ - aⱼ‖ := by
  calc |‖ahᵢ - ahⱼ‖ - ‖aᵢ - aⱼ‖| ≤ ‖(ahᵢ - ahⱼ) - (aᵢ - aⱼ)‖ := abs_norm_sub_norm_le _ _
    _ = ‖(ahᵢ - aᵢ) - (ahⱼ - aⱼ)‖ := by congr 1; abel
    _ ≤ _ := norm_sub_le _ _

omit [InnerProductSpace ℝ A] in
/-- **Over all pairs.** Summed over ordered pairs of distinct firms, squared distance errors
are at most `4(N − 1)` times the summed squared exposure errors; dividing by `N(N − 1)`
gives the `4/N` bound. The inequality is deterministic, so dependence across pairs is
irrelevant. -/
theorem pairwise_distance_error {ι : Type*} [DecidableEq ι] (s : Finset ι) (ah a : ι → A) :
    ∑ i ∈ s, ∑ j ∈ s.erase i, (‖ah i - ah j‖ - ‖a i - a j‖) ^ 2 ≤
      4 * (s.card - 1 : ℝ) * ∑ i ∈ s, ‖ah i - a i‖ ^ 2 := by
  set e := fun i => ‖ah i - a i‖
  set S := ∑ i ∈ s, e i ^ 2
  have hterm : ∀ i j, (‖ah i - ah j‖ - ‖a i - a j‖) ^ 2 ≤ 2 * e i ^ 2 + 2 * e j ^ 2 := by
    intro i j
    have h := distance_error (ah i) (a i) (ah j) (a j)
    have hsq : (‖ah i - ah j‖ - ‖a i - a j‖) ^ 2 ≤ (e i + e j) ^ 2 := by
      rw [← sq_abs]
      exact pow_le_pow_left₀ (abs_nonneg _) h 2
    nlinarith [sq_nonneg (e i - e j)]
  have hinner : ∀ i ∈ s, ∑ j ∈ s.erase i, (2 * e i ^ 2 + 2 * e j ^ 2) =
      2 * (s.card - 1 : ℝ) * e i ^ 2 + 2 * (S - e i ^ 2) := by
    intro i hi
    rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_erase_of_mem hi, nsmul_eq_mul,
      ← Finset.mul_sum, Finset.sum_erase_eq_sub hi, Nat.cast_sub (Finset.card_pos.mpr ⟨i, hi⟩),
      Nat.cast_one]
    ring
  calc _ ≤ ∑ i ∈ s, ∑ j ∈ s.erase i, (2 * e i ^ 2 + 2 * e j ^ 2) :=
        Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun j _ => hterm i j
    _ = ∑ i ∈ s, (2 * (s.card - 1 : ℝ) * e i ^ 2 + 2 * (S - e i ^ 2)) := Finset.sum_congr rfl hinner
    _ = 4 * (s.card - 1 : ℝ) * S := by
      rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum, Finset.sum_sub_distrib,
        Finset.sum_const, nsmul_eq_mul]
      ring

/-! ## Excess task risk is distance to the conditional mean -/

/-- **Pythagoras for task risk.** With `τ` the projection of `Y` onto a closed subspace `K`
of predictors and `f ∈ K`, the excess squared risk of `f` over `τ` is exactly `‖f − τ‖²`. -/
theorem excess_risk {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    (K : Submodule ℝ E) [K.HasOrthogonalProjection] (Y f : E) (hf : f ∈ K) :
    ‖f - Y‖ ^ 2 - ‖K.starProjection Y - Y‖ ^ 2 = ‖f - K.starProjection Y‖ ^ 2 := by
  set τ := K.starProjection Y
  have horth : inner ℝ (Y - τ) (f - τ) = 0 :=
    K.starProjection_inner_eq_zero Y (f - τ) (K.sub_mem hf (K.starProjection_apply_mem Y))
  have hsplit : f - Y = (f - τ) - (Y - τ) := by abel
  rw [hsplit, norm_sub_sq_real, real_inner_comm, horth, norm_sub_rev τ Y]
  ring

/-- The same identity for conditional expectation in `L²`: the excess squared risk of any
`m`-measurable predictor `f` over `E[Y | m]` is `‖f − E[Y | m]‖²`. This is the `ε` that the
exposure bounds take as task error. -/
theorem excess_risk_condExp {α : Type*} {m m0 : MeasurableSpace α} {μ : MeasureTheory.Measure α}
    (hm : m ≤ m0) (Y : MeasureTheory.Lp ℝ 2 μ) (f : MeasureTheory.lpMeas ℝ ℝ m 2 μ) :
    ‖(f : MeasureTheory.Lp ℝ 2 μ) - Y‖ ^ 2 -
        ‖(MeasureTheory.condExpL2 ℝ ℝ hm Y : MeasureTheory.Lp ℝ 2 μ) - Y‖ ^ 2 =
      ‖(f : MeasureTheory.Lp ℝ 2 μ) - MeasureTheory.condExpL2 ℝ ℝ hm Y‖ ^ 2 := by
  haveI : Fact (m ≤ m0) := ⟨hm⟩
  exact excess_risk (MeasureTheory.lpMeas ℝ ℝ m 2 μ) Y f f.2

/-- The conditional-expectation projection identity for a Hilbert-valued exposure target.
Membership in `Lp _ 2` makes square integrability explicit; no sampling independence or
finite-measure assumption is needed. -/
theorem excess_risk_condExp_hilbert {α E : Type*} {m m0 : MeasurableSpace α}
    {μ : MeasureTheory.Measure α} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [CompleteSpace E] (hm : m ≤ m0) (Y : MeasureTheory.Lp E 2 μ)
    (f : MeasureTheory.lpMeas E ℝ m 2 μ) :
    ‖(f : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 -
        ‖(MeasureTheory.condExpL2 E ℝ hm Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 =
      ‖(f : MeasureTheory.Lp E 2 μ) - MeasureTheory.condExpL2 E ℝ hm Y‖ ^ 2 := by
  haveI : Fact (m ≤ m0) := ⟨hm⟩
  exact excess_risk (MeasureTheory.lpMeas E ℝ m 2 μ) Y f f.2

/-- **Nested information.** Projecting a target onto a smaller predictor space costs
exactly the squared distance between the two Bayes predictors. -/
theorem nested_projection_risk {E : Type*} [NormedAddCommGroup E]
    [InnerProductSpace ℝ E] (K L : Submodule ℝ E) [K.HasOrthogonalProjection]
    [L.HasOrthogonalProjection] (hKL : K ≤ L) (Y : E) :
    ‖K.starProjection Y - Y‖ ^ 2 = ‖L.starProjection Y - Y‖ ^ 2 +
      ‖K.starProjection Y - L.starProjection Y‖ ^ 2 := by
  have h := excess_risk L Y (K.starProjection Y) (hKL (K.starProjection_apply_mem Y))
  linarith

/-- **Fitted risk with nested information.** The three terms are uncertainty after full
history, information lost by the representation, and the fitted predictor's error relative
to the representation's Bayes predictor. -/
theorem nested_projection_fitted_risk {E : Type*} [NormedAddCommGroup E]
    [InnerProductSpace ℝ E] (K L : Submodule ℝ E) [K.HasOrthogonalProjection]
    [L.HasOrthogonalProjection] (hKL : K ≤ L) (Y f : E) (hf : f ∈ K) :
    ‖f - Y‖ ^ 2 = ‖L.starProjection Y - Y‖ ^ 2 +
      ‖K.starProjection Y - L.starProjection Y‖ ^ 2 + ‖f - K.starProjection Y‖ ^ 2 := by
  have hfit := excess_risk K Y f hf
  have hinfo := nested_projection_risk K L hKL Y
  linarith

/-- **History versus encoder information.** If `mZ ≤ mH`, history has no larger optimal
squared prediction risk than its representation. The equality records the exact loss, for
Hilbert-valued square-integrable targets as well as scalar ones. -/
theorem nested_information_risk {α E : Type*} {mZ mH m0 : MeasurableSpace α}
    {μ : MeasureTheory.Measure α} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [CompleteSpace E] (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : MeasureTheory.Lp E 2 μ) :
    ‖(MeasureTheory.condExpL2 E ℝ (hZH.trans hH) Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 =
      ‖(MeasureTheory.condExpL2 E ℝ hH Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 +
      ‖(MeasureTheory.condExpL2 E ℝ (hZH.trans hH) Y : MeasureTheory.Lp E 2 μ) -
        MeasureTheory.condExpL2 E ℝ hH Y‖ ^ 2 := by
  haveI : Fact (mZ ≤ m0) := ⟨hZH.trans hH⟩
  haveI : Fact (mH ≤ m0) := ⟨hH⟩
  apply nested_projection_risk (MeasureTheory.lpMeas E ℝ mZ 2 μ)
    (MeasureTheory.lpMeas E ℝ mH 2 μ) _ Y
  intro f hf
  exact MeasureTheory.mem_lpMeas_iff_aestronglyMeasurable.mpr
    ((MeasureTheory.mem_lpMeas_iff_aestronglyMeasurable.mp hf).mono hZH)

/-- A fitted encoder-measurable predictor has uncertainty, encoder-information-loss and
readout-error terms. It need not be the unrestricted population minimizer. -/
theorem nested_information_fitted_risk {α E : Type*} {mZ mH m0 : MeasurableSpace α}
    {μ : MeasureTheory.Measure α} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [CompleteSpace E] (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : MeasureTheory.Lp E 2 μ)
    (f : MeasureTheory.lpMeas E ℝ mZ 2 μ) :
    ‖(f : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 =
      ‖(MeasureTheory.condExpL2 E ℝ hH Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 +
      ‖(MeasureTheory.condExpL2 E ℝ (hZH.trans hH) Y : MeasureTheory.Lp E 2 μ) -
        MeasureTheory.condExpL2 E ℝ hH Y‖ ^ 2 +
      ‖(f : MeasureTheory.Lp E 2 μ) - MeasureTheory.condExpL2 E ℝ (hZH.trans hH) Y‖ ^ 2 := by
  have hfit := excess_risk_condExp_hilbert (hZH.trans hH) Y f
  have hinfo := nested_information_risk hZH hH Y
  linarith

/-- Processing history into a representation cannot lower its unrestricted Bayes risk.
This does not compare restricted fitted regressions. -/
theorem history_information_risk_le {α E : Type*} {mZ mH m0 : MeasurableSpace α}
    {μ : MeasureTheory.Measure α} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
    [CompleteSpace E] (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : MeasureTheory.Lp E 2 μ) :
    ‖(MeasureTheory.condExpL2 E ℝ hH Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 ≤
      ‖(MeasureTheory.condExpL2 E ℝ (hZH.trans hH) Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 := by
  rw [nested_information_risk hZH hH Y]
  exact le_add_of_nonneg_right (sq_nonneg _)

/-- If the representation retains exactly the history information, the three-term fitted
risk identity reduces to the usual two-term projection identity. -/
example {α E : Type*} {m m0 : MeasurableSpace α} {μ : MeasureTheory.Measure α}
    [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hm : m ≤ m0) (Y : MeasureTheory.Lp E 2 μ) (f : MeasureTheory.lpMeas E ℝ m 2 μ) :
    ‖(f : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 =
      ‖(MeasureTheory.condExpL2 E ℝ hm Y : MeasureTheory.Lp E 2 μ) - Y‖ ^ 2 +
      ‖(f : MeasureTheory.Lp E 2 μ) - MeasureTheory.condExpL2 E ℝ hm Y‖ ^ 2 := by
  simpa using nested_information_fitted_risk (le_refl m) hm Y f

/-! ## Economic meaning belongs to representation and readout together -/

/-- If a linear readout `G` gives exposures from states `Z`, the reparametrised states `eZ`
with readout `G e⁻¹` give the same exposures and so the same distances. Native distances
between states are not invariant this way (`Geometry`). -/
theorem readout_invariant {Z : Type*} [AddCommGroup Z] [Module ℝ Z] (G : Z →ₗ[ℝ] A)
    (e : Z ≃ₗ[ℝ] Z) (z z' : Z) :
    ‖(G ∘ₗ e.symm.toLinearMap) (e z) - (G ∘ₗ e.symm.toLinearMap) (e z')‖ = ‖G z - G z'‖ := by
  simp

/-! ## One target merges what two targets separate -/

/-- Two exposure coordinates, say financing and operating. -/
abbrev Plane := EuclideanSpace ℝ (Fin 2)

/-- **Limit.** The aggregate target `a_f + a_o` takes the same value on `(1, 0)` and
`(0, 1)`, which are `√2` apart: perfect prediction of it can merge distinct firms. -/
theorem aggregate_merges :
    let a : Plane := !₂[1, 0]
    let a' : Plane := !₂[0, 1]
    a 0 + a 1 = a' 0 + a' 1 ∧ ‖a - a'‖ = Real.sqrt 2 := by
  refine ⟨by simp, ?_⟩
  rw [EuclideanSpace.norm_eq]
  norm_num [Fin.sum_univ_two]

/-- **Diversity.** The two targets `a_f + a_o` and `a_f − a_o` together have
`‖C a‖² = 2‖a‖²`, so they distinguish exposures with margin `√2`. -/
theorem diverse_distinguishes (a : Plane) :
    (a 0 + a 1) ^ 2 + (a 0 - a 1) ^ 2 = 2 * ‖a‖ ^ 2 := by
  rw [EuclideanSpace.norm_eq, Real.sq_sqrt (by positivity), Fin.sum_univ_two]
  simp only [Real.norm_eq_abs, sq_abs]
  ring

end FreeFoundations.Recovery
