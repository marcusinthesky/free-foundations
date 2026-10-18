import Mathlib.MeasureTheory.Function.L2Space
import Mathlib.MeasureTheory.Function.LpSeminorm.TriangleInequality
import Mathlib.Topology.MetricSpace.Lipschitz
import FreeFoundations.Recovery

/-!
# Measurement through a readout

`Recovery` decodes exposures with a linear left inverse. The argument works for any readout.
A learning objective supplies a statistic `F(h)`: a conditional mean, a conditional law, a
posterior predictive. The economic state `s(h)` lives in its own metric space, and a readout
`g` maps the first to the second. The alignment error `ξ = d(g(F), s)` is the part of the
state that the objective's statistic does not carry.

* **Upper bound.** If `g` is `K`-Lipschitz, the measured state `g(F̂)` misses `s` by at most
  `K d(F̂, F) + ξ` (`measurement_error`). In root mean square the same holds by Minkowski
  (`rms_measurement_error`): `‖d(g(F̂), s)‖₂ ≤ K ‖d(F̂, F)‖₂ + ‖ξ‖₂`. When `F` is a
  conditional mean, `‖F̂ − F‖₂²` is the excess risk (`Recovery.excess_risk_condExp`).
  Squaring gives the weaker `E d² ≤ 2K² E d_F² + 2 E ξ²`. A linear decoder is
  `1/κ`-Lipschitz (`decoder_lipschitz`), which recovers `Recovery.exposure_error_mismatch`.
* **Lower bound.** If a representation gives two histories the same value, any readout
  misses one of their states by at least half the distance between them, however accurate
  the prediction (`readout_error_ge`). Reading two unit exposures from their aggregate
  misses one by at least `√2/2` (`aggregate_readout_error`).
* **Posterior means are not states.** For a random difference `D = Aᵢ − Aⱼ` with finite
  second moment, `E‖D‖² = ‖E D‖² + E‖D − E D‖²` (`mean_sq_distance`). Under the
  conditional law given the information, the distance between posterior-mean exposures
  understates the expected distance by `tr Var(Aᵢ − Aⱼ | H)`, which differs across pairs.

The alignment error is assumed, not estimated: the bounds say what a readout can deliver
given it.
-/

namespace FreeFoundations.Measurement

open MeasureTheory

section Metric

variable {F S : Type*} [PseudoMetricSpace F] [PseudoMetricSpace S]

/-- **Measurement error.** A `K`-Lipschitz readout misses the state by at most `K` times the
prediction error plus the alignment error. -/
theorem measurement_error {g : F → S} {K : NNReal} (hg : LipschitzWith K g) (s : S)
    (f fhat : F) : dist (g fhat) s ≤ K * dist fhat f + dist (g f) s :=
  (dist_triangle _ (g f) _).trans (by gcongr; exact hg.dist_le_mul fhat f)

/-- **In root mean square.** Under any measure, `‖d(g(F̂), s)‖₂ ≤ K ‖d(F̂, F)‖₂ + ‖ξ‖₂`. -/
theorem rms_measurement_error {Ω : Type*} [MeasurableSpace Ω] (μ : Measure Ω) {g : F → S}
    {K : NNReal} (hg : LipschitzWith K g) (s : Ω → S) (f fhat : Ω → F)
    (hpred : AEStronglyMeasurable (fun ω => dist (fhat ω) (f ω)) μ)
    (halign : AEStronglyMeasurable (fun ω => dist (g (f ω)) (s ω)) μ) :
    eLpNorm (fun ω => dist (g (fhat ω)) (s ω)) 2 μ ≤
      K * eLpNorm (fun ω => dist (fhat ω) (f ω)) 2 μ +
        eLpNorm (fun ω => dist (g (f ω)) (s ω)) 2 μ := by
  have hsmul : (fun ω => (K : ℝ) * dist (fhat ω) (f ω)) =
      (K : ℝ) • fun ω => dist (fhat ω) (f ω) := rfl
  calc eLpNorm (fun ω => dist (g (fhat ω)) (s ω)) 2 μ
      ≤ eLpNorm ((fun ω => (K : ℝ) * dist (fhat ω) (f ω)) +
          fun ω => dist (g (f ω)) (s ω)) 2 μ := by
        refine eLpNorm_mono_real fun ω => ?_
        rw [Real.norm_eq_abs, abs_of_nonneg dist_nonneg]
        exact measurement_error hg (s ω) (f ω) (fhat ω)
    _ ≤ eLpNorm (fun ω => (K : ℝ) * dist (fhat ω) (f ω)) 2 μ +
          eLpNorm (fun ω => dist (g (f ω)) (s ω)) 2 μ :=
        eLpNorm_add_le (hpred.const_mul _) halign (by norm_num)
    _ = _ := by
        rw [hsmul, eLpNorm_const_smul, Real.enorm_of_nonneg K.coe_nonneg,
          ENNReal.ofReal_coe_nnreal]

/-- **Merged states.** Any single estimate `r` misses one of two states by at least half
their distance. -/
theorem merged_error (s s' r : S) : dist s s' ≤ 2 * max (dist r s) (dist r s') := by
  have := dist_triangle s r s'
  rw [dist_comm s r] at this
  linarith [le_max_left (dist r s) (dist r s'), le_max_right (dist r s) (dist r s')]

/-- **Lower bound.** If a representation `Z` gives two histories the same value, any readout
`r` misses one of their states by at least half the distance between them. -/
theorem readout_error_ge {H R : Type*} (Z : H → R) (state : H → S) (r : R → S) {h h' : H}
    (hZ : Z h = Z h') :
    dist (state h) (state h') ≤
      2 * max (dist (r (Z h)) (state h)) (dist (r (Z h')) (state h')) := by
  rw [← hZ]
  exact merged_error _ _ _

end Metric

/-- **One aggregate target.** The unit exposures `(1, 0)` and `(0, 1)` have the same
aggregate `a_f + a_o = 1`, so any readout `r` of the aggregate misses one of them by at
least `√2/2`. -/
theorem aggregate_readout_error (r : ℝ → Recovery.Plane) :
    Real.sqrt 2 / 2 ≤ max (dist (r 1) !₂[1, 0]) (dist (r 1) !₂[0, 1]) := by
  have hd : dist (!₂[1, 0] : Recovery.Plane) !₂[0, 1] = Real.sqrt 2 := by
    rw [EuclideanSpace.dist_eq]
    norm_num [Fin.sum_univ_two]
  have h := merged_error (!₂[1, 0] : Recovery.Plane) !₂[0, 1] (r 1)
  rw [hd] at h
  linarith

section Decoder

variable {A T : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]
  [NormedAddCommGroup T] [InnerProductSpace ℝ T]

/-- A linear decoder with margin `κ > 0` is `1/κ`-Lipschitz. With `g = L` and `F = Ca + v`,
`measurement_error` is `Recovery.exposure_error_mismatch` divided by `κ`. -/
theorem decoder_lipschitz {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    (hL : Recovery.Decoder C κ L) (hκ : 0 < κ) : LipschitzWith (Real.toNNReal κ⁻¹) L := by
  refine LipschitzWith.of_dist_le_mul fun x y => ?_
  rw [dist_eq_norm, dist_eq_norm, ← map_sub, Real.coe_toNNReal _ (inv_nonneg.mpr hκ.le),
    inv_mul_eq_div, le_div_iff₀ hκ, mul_comm]
  exact hL.bound (x - y)

end Decoder

section Moments

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
variable {Ω : Type*} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]

/-- **Posterior means understate distances.** For a random difference `D` with finite second
moment, `E‖D‖² = ‖E D‖² + E‖D − E D‖²`. -/
theorem mean_sq_distance {D : Ω → E} (hD : MemLp D 2 μ) :
    ∫ ω, ‖D ω‖ ^ 2 ∂μ = ‖∫ ω, D ω ∂μ‖ ^ 2 + ∫ ω, ‖D ω - ∫ ω', D ω' ∂μ‖ ^ 2 ∂μ := by
  set m := ∫ ω, D ω ∂μ
  have hDi : Integrable D μ := hD.integrable one_le_two
  have hDm : Integrable (fun ω => D ω - m) μ := hDi.sub (integrable_const m)
  have hc : MemLp (fun ω => D ω - m) 2 μ := hD.sub (memLp_const m)
  have hsq : Integrable (fun ω => ‖D ω - m‖ ^ 2) μ :=
    (memLp_two_iff_integrable_sq_norm hc.1).mp hc
  have hin : Integrable (fun ω => inner ℝ m (D ω - m)) μ := hDm.const_inner m
  have h1 : Integrable (fun ω => ‖D ω - m‖ ^ 2 + 2 * inner ℝ m (D ω - m)) μ :=
    hsq.add (hin.const_mul 2)
  have hpoint : ∀ ω, ‖D ω‖ ^ 2 = ‖D ω - m‖ ^ 2 + 2 * inner ℝ m (D ω - m) + ‖m‖ ^ 2 := by
    intro ω
    rw [real_inner_comm, ← norm_add_sq_real, sub_add_cancel]
  have hzero : ∫ ω, inner ℝ m (D ω - m) ∂μ = 0 := by
    rw [integral_inner hDm m, integral_sub hDi (integrable_const m)]
    simp [m]
  have hsplit : ∫ ω, (‖D ω - m‖ ^ 2 + 2 * inner ℝ m (D ω - m) + ‖m‖ ^ 2) ∂μ =
      ∫ ω, ‖D ω - m‖ ^ 2 ∂μ + 2 * ∫ ω, inner ℝ m (D ω - m) ∂μ + ‖m‖ ^ 2 := by
    rw [integral_add h1 (integrable_const _), integral_add hsq (hin.const_mul 2),
      integral_const_mul]
    simp
  simp_rw [hpoint]
  rw [hsplit, hzero]
  ring

/-- Hence `‖E D‖² ≤ E‖D‖²`: the distance between means is never more than the
root-mean-square distance. -/
theorem sq_norm_mean_le {D : Ω → E} (hD : MemLp D 2 μ) :
    ‖∫ ω, D ω ∂μ‖ ^ 2 ≤ ∫ ω, ‖D ω‖ ^ 2 ∂μ := by
  rw [mean_sq_distance hD]
  exact le_add_of_nonneg_right (integral_nonneg fun _ => sq_nonneg _)

end Moments

end FreeFoundations.Measurement
