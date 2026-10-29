module

public import FreeFoundations.Recovery
public import Mathlib.MeasureTheory.Function.L2Space
public import Mathlib.MeasureTheory.Function.LpSeminorm.TriangleInequality

@[expose] public section

/-!
# Historical proxies and latent exposures

A fitted prediction, a historical exposure proxy, and a latent exposure must be expressed
in common risk-scaled coordinates before their errors can be compared. Triangle bounds
need no claim that the proxy is unbiased, independent, or structurally identified.

An exact proxy-risk identity requires an additional assumption: proxy noise is orthogonal
in `L²` to the latent prediction residual. Its predictor-ranking corollary requires that
assumption for both predictors, with the same latent target and proxy noise. These results
do not establish the assumptions for estimated historical factor loadings.
-/

namespace FreeFoundations.Proxy

open MeasureTheory

section Pointwise

variable {A : Type*} [NormedAddCommGroup A]

/-- Prediction error against the latent exposure is controlled by fitted proxy error and
the proxy's own error. All three objects use the same coordinates. -/
theorem error_le (prediction proxy latent : A) :
    ‖prediction - latent‖ ≤ ‖prediction - proxy‖ + ‖proxy - latent‖ := by
  simpa only [sub_add_sub_cancel] using norm_add_le (prediction - proxy) (proxy - latent)

/-- A squared-error bound that does not assume unbiased or independent proxy noise. -/
theorem error_sq_le (prediction proxy latent : A) :
    ‖prediction - latent‖ ^ 2 ≤
      2 * ‖prediction - proxy‖ ^ 2 + 2 * ‖proxy - latent‖ ^ 2 := by
  have h := error_le prediction proxy latent
  have hs := pow_le_pow_left₀ (norm_nonneg _) h 2
  nlinarith [sq_nonneg (‖prediction - proxy‖ - ‖proxy - latent‖)]

/-- Finite panels may contain dependent firms; the bound is deterministic. -/
theorem sum_error_le {ι : Type*} (s : Finset ι) (prediction proxy latent : ι → A) :
    ∑ i ∈ s, ‖prediction i - latent i‖ ≤
      (∑ i ∈ s, ‖prediction i - proxy i‖) + ∑ i ∈ s, ‖proxy i - latent i‖ := by
  calc _ ≤ ∑ i ∈ s, (‖prediction i - proxy i‖ + ‖proxy i - latent i‖) :=
      Finset.sum_le_sum fun i _ => error_le (prediction i) (proxy i) (latent i)
    _ = _ := Finset.sum_add_distrib

/-- A finite-panel squared-error bound that does not require independent firms. -/
theorem sum_error_sq_le {ι : Type*} (s : Finset ι) (prediction proxy latent : ι → A) :
    ∑ i ∈ s, ‖prediction i - latent i‖ ^ 2 ≤
      2 * ∑ i ∈ s, ‖prediction i - proxy i‖ ^ 2 +
        2 * ∑ i ∈ s, ‖proxy i - latent i‖ ^ 2 := by
  calc _ ≤ ∑ i ∈ s, (2 * ‖prediction i - proxy i‖ ^ 2 +
          2 * ‖proxy i - latent i‖ ^ 2) :=
      Finset.sum_le_sum fun i _ => error_sq_le (prediction i) (proxy i) (latent i)
    _ = _ := by rw [Finset.sum_add_distrib, ← Finset.mul_sum, ← Finset.mul_sum]

end Pointwise

section L2Bounds

variable {Ω A : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [NormedAddCommGroup A]

/-- The `L²` triangle bound (root mean square for probability measures). Explicit `MemLp`
assumptions ensure that all three exposure functions are measurable and have finite
second moment, even when the underlying measure is not a probability measure. -/
theorem rms_error_le (prediction proxy latent : Ω → A)
    (hp : MemLp prediction 2 μ) (hq : MemLp proxy 2 μ) (ha : MemLp latent 2 μ) :
    eLpNorm (fun ω => prediction ω - latent ω) 2 μ ≤
      eLpNorm (fun ω => prediction ω - proxy ω) 2 μ +
        eLpNorm (fun ω => proxy ω - latent ω) 2 μ := by
  have hpq : AEStronglyMeasurable (fun ω => prediction ω - proxy ω) μ :=
    (hp.sub hq).aestronglyMeasurable
  have hqa : AEStronglyMeasurable (fun ω => proxy ω - latent ω) μ :=
    (hq.sub ha).aestronglyMeasurable
  have hsum : (fun ω => prediction ω - proxy ω) + (fun ω => proxy ω - latent ω) =
      (fun ω => prediction ω - latent ω) := by
    funext ω
    simp only [Pi.add_apply, sub_add_sub_cancel]
  rw [← hsum, eLpNorm_eq_eLpNorm' (by norm_num) (by norm_num) (hpq.add hqa),
    eLpNorm_eq_eLpNorm' (by norm_num) (by norm_num) hpq,
    eLpNorm_eq_eLpNorm' (by norm_num) (by norm_num) hqa]
  simpa using eLpNorm'_add_le hpq hqa (by norm_num : (1 : ℝ) ≤ 2)

/-- Integrated squared error, with finite second moments stated explicitly. -/
theorem integral_error_sq_le (prediction proxy latent : Ω → A)
    (hp : MemLp prediction 2 μ) (hq : MemLp proxy 2 μ) (ha : MemLp latent 2 μ) :
    ∫ ω, ‖prediction ω - latent ω‖ ^ 2 ∂μ ≤
      2 * (∫ ω, ‖prediction ω - proxy ω‖ ^ 2 ∂μ) +
        2 * (∫ ω, ‖proxy ω - latent ω‖ ^ 2 ∂μ) := by
  have hi₁ : Integrable (fun ω => ‖prediction ω - latent ω‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm (hp.sub ha).aestronglyMeasurable).mp (hp.sub ha)
  have hi₂ : Integrable (fun ω => ‖prediction ω - proxy ω‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm (hp.sub hq).aestronglyMeasurable).mp (hp.sub hq)
  have hi₃ : Integrable (fun ω => ‖proxy ω - latent ω‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm (hq.sub ha).aestronglyMeasurable).mp (hq.sub ha)
  calc _ ≤ ∫ ω, (2 * ‖prediction ω - proxy ω‖ ^ 2 +
        2 * ‖proxy ω - latent ω‖ ^ 2) ∂μ :=
      integral_mono hi₁ ((hi₂.const_mul 2).add (hi₃.const_mul 2))
        fun ω => error_sq_le (prediction ω) (proxy ω) (latent ω)
    _ = _ := by rw [integral_add (hi₂.const_mul 2) (hi₃.const_mul 2),
        integral_const_mul, integral_const_mul]

end L2Bounds

section OrthogonalNoise

variable {Ω A : Type*} [MeasurableSpace Ω] {μ : Measure Ω}
    [NormedAddCommGroup A] [InnerProductSpace ℝ A]

/-- **Proxy-risk identity.** The proxy is `latent + noise`. Orthogonality is an explicit
`L²` inner-product condition on the latent prediction residual and the noise, not a
consequence of good prediction or of historical OLS estimation. -/
theorem integral_risk_eq (prediction latent noise : Ω → A)
    (hp : MemLp prediction 2 μ) (ha : MemLp latent 2 μ) (hn : MemLp noise 2 μ)
    (horth : ∫ ω, inner ℝ (prediction ω - latent ω) (noise ω) ∂μ = 0) :
    ∫ ω, ‖prediction ω - (latent ω + noise ω)‖ ^ 2 ∂μ =
      (∫ ω, ‖prediction ω - latent ω‖ ^ 2 ∂μ) + ∫ ω, ‖noise ω‖ ^ 2 ∂μ := by
  have hr := hp.sub ha
  have hi₁ : Integrable (fun ω => ‖prediction ω - latent ω‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm hr.aestronglyMeasurable).mp hr
  have hi₂ : Integrable (fun ω => ‖noise ω‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm hn.aestronglyMeasurable).mp hn
  have hic : Integrable (fun ω => inner ℝ (prediction ω - latent ω) (noise ω)) μ :=
    (hi₁.add hi₂).mono' (hr.aestronglyMeasurable.inner hn.aestronglyMeasurable) (Filter.Eventually.of_forall fun ω => by
      refine (norm_inner_le_norm _ _).trans ?_
      change ‖prediction ω - latent ω‖ * ‖noise ω‖ ≤
        ‖prediction ω - latent ω‖ ^ 2 + ‖noise ω‖ ^ 2
      nlinarith [sq_nonneg (‖prediction ω - latent ω‖ - ‖noise ω‖),
        mul_nonneg (norm_nonneg (prediction ω - latent ω)) (norm_nonneg (noise ω))])
  have hpoint : ∀ ω, ‖prediction ω - (latent ω + noise ω)‖ ^ 2 =
      ‖prediction ω - latent ω‖ ^ 2 -
        2 * inner ℝ (prediction ω - latent ω) (noise ω) + ‖noise ω‖ ^ 2 := by
    intro ω
    rw [show prediction ω - (latent ω + noise ω) =
      (prediction ω - latent ω) - noise ω by abel, norm_sub_sq_real]
  simp_rw [hpoint]
  have hsum := integral_add (hi₁.sub (hic.const_mul 2)) hi₂
  have hsub := integral_sub hi₁ (hic.const_mul 2)
  simp only [Pi.sub_apply] at hsum hsub
  rw [hsum, hsub, integral_const_mul, horth]
  ring

/-- Under the orthogonality assumption for both predictors, their proxy-risk difference
equals their latent-risk difference. The same noise term cancels. -/
theorem integral_risk_difference (prediction₁ prediction₂ latent noise : Ω → A)
    (hp₁ : MemLp prediction₁ 2 μ) (hp₂ : MemLp prediction₂ 2 μ)
    (ha : MemLp latent 2 μ) (hn : MemLp noise 2 μ)
    (horth₁ : ∫ ω, inner ℝ (prediction₁ ω - latent ω) (noise ω) ∂μ = 0)
    (horth₂ : ∫ ω, inner ℝ (prediction₂ ω - latent ω) (noise ω) ∂μ = 0) :
    (∫ ω, ‖prediction₁ ω - (latent ω + noise ω)‖ ^ 2 ∂μ) -
        (∫ ω, ‖prediction₂ ω - (latent ω + noise ω)‖ ^ 2 ∂μ) =
      (∫ ω, ‖prediction₁ ω - latent ω‖ ^ 2 ∂μ) -
        (∫ ω, ‖prediction₂ ω - latent ω‖ ^ 2 ∂μ) := by
  rw [integral_risk_eq prediction₁ latent noise hp₁ ha hn horth₁,
    integral_risk_eq prediction₂ latent noise hp₂ ha hn horth₂]
  ring

/-- Proxy and latent risk rank two predictors identically under their common explicit
noise-orthogonality assumptions. -/
theorem integral_risk_le_iff (prediction₁ prediction₂ latent noise : Ω → A)
    (hp₁ : MemLp prediction₁ 2 μ) (hp₂ : MemLp prediction₂ 2 μ)
    (ha : MemLp latent 2 μ) (hn : MemLp noise 2 μ)
    (horth₁ : ∫ ω, inner ℝ (prediction₁ ω - latent ω) (noise ω) ∂μ = 0)
    (horth₂ : ∫ ω, inner ℝ (prediction₂ ω - latent ω) (noise ω) ∂μ = 0) :
    (∫ ω, ‖prediction₁ ω - (latent ω + noise ω)‖ ^ 2 ∂μ) ≤
        (∫ ω, ‖prediction₂ ω - (latent ω + noise ω)‖ ^ 2 ∂μ) ↔
      (∫ ω, ‖prediction₁ ω - latent ω‖ ^ 2 ∂μ) ≤
        (∫ ω, ‖prediction₂ ω - latent ω‖ ^ 2 ∂μ) := by
  rw [integral_risk_eq prediction₁ latent noise hp₁ ha hn horth₁,
    integral_risk_eq prediction₂ latent noise hp₂ ha hn horth₂, add_le_add_iff_right]

end OrthogonalNoise

/-! ## Boundary cases -/

/-- Exact historical-proxy prediction alone places no bound on latent error: any nonnegative
real discrepancy can remain. -/
example (r : ℝ) (hr : 0 ≤ r) : ‖r - r‖ = 0 ∧ ‖r - (0 : ℝ)‖ = r := by
  simp [Real.norm_eq_abs, abs_of_nonneg hr]

/-- Without orthogonality, proxy and latent squared error can rank predictors in opposite
orders: the proxy is one, the latent exposure is zero, and the two predictions are one and
zero. This is also a one-observation finite-panel counterexample. -/
example : ‖(1 : ℝ) - 1‖ ^ 2 < ‖(0 : ℝ) - 1‖ ^ 2 ∧
    ‖(0 : ℝ) - 0‖ ^ 2 < ‖(1 : ℝ) - 0‖ ^ 2 := by norm_num

/-- The exact identity allows nonzero noise. Here it is perpendicular to the latent
prediction residual in two exposure coordinates. -/
example : ‖(!₂[1, 0] : Recovery.Plane) - !₂[0, 1]‖ ^ 2 =
    ‖(!₂[1, 0] : Recovery.Plane)‖ ^ 2 + ‖(!₂[0, 1] : Recovery.Plane)‖ ^ 2 := by
  have horth : inner ℝ (!₂[1, 0] : Recovery.Plane) !₂[0, 1] = 0 := by
    simp [PiLp.inner_apply, Fin.sum_univ_two]
  rw [norm_sub_sq_real, horth]
  ring

/-- With an exact proxy, the integrated bound reduces to twice the fitted proxy risk. -/
example {Ω A : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [NormedAddCommGroup A]
    (prediction latent : Ω → A) (hp : MemLp prediction 2 μ) (ha : MemLp latent 2 μ) :
    ∫ ω, ‖prediction ω - latent ω‖ ^ 2 ∂μ ≤
      2 * ∫ ω, ‖prediction ω - latent ω‖ ^ 2 ∂μ := by
  simpa using integral_error_sq_le prediction latent latent hp ha ha

end FreeFoundations.Proxy
