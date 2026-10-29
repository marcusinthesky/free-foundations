module

public import FreeFoundations.Kernel
public import Mathlib.Analysis.SpecialFunctions.ExpDeriv
public import Mathlib.Analysis.SpecialFunctions.Log.Deriv
public import Mathlib.Analysis.Calculus.Deriv.MeanValue
public import Mathlib.Topology.Order.IntermediateValue

@[expose] public section

/-!
# Fixed-distance bandwidth comparative statics

All derivatives hold with the distance row fixed. These statements do not compare procedures
that refit distances, task heads, spatial coefficients or innovation variances.
-/

open scoped Topology

namespace FreeFoundations.Kernel

/-- The sharp sensitivity has derivative at most one everywhere. -/
theorem hasDerivAt_sensitivity (b : ℝ) :
    HasDerivAt sensitivity (4 * Real.exp b / (Real.exp b + 1) ^ 2) b := by
  have he : Real.exp b + 1 ≠ 0 := ne_of_gt (by positivity)
  convert (((Real.hasDerivAt_exp b).sub_const 1).const_mul 2).div
    ((Real.hasDerivAt_exp b).add_const 1) he using 1 <;>
    first | rfl | ring

/-- The sharp row certificate is bounded by its scaled-distance input. -/
theorem sensitivity_le_self {b : ℝ} (hb : 0 ≤ b) : sensitivity b ≤ b := by
  have hd : ∀ x, deriv sensitivity x ≤ 1 := by
    intro x
    rw [(hasDerivAt_sensitivity x).deriv]
    apply (div_le_iff₀ (sq_pos_of_pos (by positivity : 0 < Real.exp x + 1))).mpr
    nlinarith [sq_nonneg (Real.exp x - 1)]
  have h := image_sub_le_mul_sub_of_deriv_le
    (fun x => (hasDerivAt_sensitivity x).differentiableAt) hd hb
  simpa using h

theorem sensitivity_le_min {b : ℝ} (hb : 0 ≤ b) : sensitivity b ≤ min 2 b :=
  le_min (sensitivity_le_two b) (sensitivity_le_self hb)

end FreeFoundations.Kernel

namespace FreeFoundations.Bandwidth

open Finset

variable {ι : Type*}

/-- Expected reference distance under the row weights. -/
noncomputable def meanDistance (s : Finset ι) (d : ι → ℝ) (h : ℝ) : ℝ :=
  ∑ j ∈ s, Kernel.expRow s d h j * d j

/-- Weighted distance variance; finite nonnegative weights make it nonnegative. -/
noncomputable def distanceVariance (s : Finset ι) (d : ι → ℝ) (h : ℝ) : ℝ :=
  ∑ j ∈ s, Kernel.expRow s d h j * (d j - meanDistance s d h) ^ 2

noncomputable def entropy (s : Finset ι) (d : ι → ℝ) (h : ℝ) : ℝ :=
  -∑ j ∈ s, Kernel.expRow s d h j * Real.log (Kernel.expRow s d h j)

noncomputable def herfindahl (s : Finset ι) (d : ι → ℝ) (h : ℝ) : ℝ :=
  ∑ j ∈ s, Kernel.expRow s d h j ^ 2

noncomputable def effectiveNeighbors (s : Finset ι) (d : ι → ℝ) (h : ℝ) : ℝ :=
  (herfindahl s d h)⁻¹

/-- Each raw weight has a derivative for every nonzero bandwidth. -/
theorem hasDerivAt_raw (d h : ℝ) (hh : h ≠ 0) :
    HasDerivAt (fun u => Real.exp (-d / u)) (Real.exp (-d / h) * (d / h ^ 2)) h := by
  simpa only [Pi.div_def, id_eq, zero_mul, mul_one, zero_sub, neg_neg] using
    (((hasDerivAt_const h (-d)).div (hasDerivAt_id h) hh).exp)

/-- Derivative of the finite normalization denominator. -/
theorem hasDerivAt_partition (s : Finset ι) (d : ι → ℝ) {h : ℝ} (hh : h ≠ 0) :
    HasDerivAt (fun u => ∑ j ∈ s, Real.exp (-d j / u))
      (∑ j ∈ s, Real.exp (-d j / h) * (d j / h ^ 2)) h := by
  exact HasDerivAt.fun_sum fun j _ => hasDerivAt_raw (d j) h hh

/-- The denominator times the weighted mean is the unnormalized first moment. -/
theorem partition_mul_mean (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    (∑ j ∈ s, Real.exp (-d j / h)) * meanDistance s d h =
      ∑ j ∈ s, Real.exp (-d j / h) * d j := by
  have hZ : (∑ j ∈ s, Real.exp (-d j / h)) ≠ 0 :=
    ne_of_gt (sum_pos (fun _ _ => Real.exp_pos _) hs)
  unfold meanDistance Kernel.expRow
  rw [mul_sum]
  apply sum_congr rfl
  intro j _
  field_simp

/-- Derivative of an individual normalized weight, with the distance row fixed. -/
theorem hasDerivAt_expRow (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h : ℝ} (hh : h ≠ 0) (j : ι) :
    HasDerivAt (fun u => Kernel.expRow s d u j)
      (Kernel.expRow s d h j * (d j - meanDistance s d h) / h ^ 2) h := by
  set Z := ∑ k ∈ s, Real.exp (-d k / h)
  have hZ : Z ≠ 0 := ne_of_gt (sum_pos (fun _ _ => Real.exp_pos _) hs)
  have hZD : (∑ k ∈ s, Real.exp (-d k / h) * (d k / h ^ 2)) =
      Z * meanDistance s d h / h ^ 2 := by
    calc _ = (∑ k ∈ s, Real.exp (-d k / h) * d k) / h ^ 2 := by
          rw [sum_div]
          apply sum_congr rfl
          intro k _
          ring
      _ = _ := by rw [← partition_mul_mean s hs d h]
  have hdZ := hasDerivAt_partition s d hh
  rw [hZD] at hdZ
  convert (hasDerivAt_raw (d j) h hh).div hdZ hZ using 1 <;>
    first | rfl | (dsimp [Kernel.expRow, Z]; field_simp)

/-- Weighted distance variance as a second moment minus squared mean. -/
theorem distanceVariance_eq (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    distanceVariance s d h =
      (∑ j ∈ s, Kernel.expRow s d h j * d j ^ 2) - meanDistance s d h ^ 2 := by
  unfold distanceVariance
  have heq : ∀ j, Kernel.expRow s d h j * (d j - meanDistance s d h) ^ 2 =
      Kernel.expRow s d h j * d j ^ 2 -
      2 * meanDistance s d h * (Kernel.expRow s d h j * d j) +
      meanDistance s d h ^ 2 * Kernel.expRow s d h j := by intro j; ring
  simp_rw [heq]
  rw [sum_add_distrib, sum_sub_distrib, ← mul_sum, ← mul_sum,
    Kernel.expRow_sum s hs d h]
  change _ - 2 * meanDistance s d h * meanDistance s d h + meanDistance s d h ^ 2 * 1 = _
  ring

theorem distanceVariance_nonneg (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    0 ≤ distanceVariance s d h :=
  sum_nonneg fun j _ => mul_nonneg (Kernel.expRow_pos s hs d h j).le (sq_nonneg _)

/-- A wider bandwidth raises expected neighbor distance at rate variance divided by `h²`. -/
theorem hasDerivAt_meanDistance (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h : ℝ} (hh : h ≠ 0) :
    HasDerivAt (meanDistance s d) (distanceVariance s d h / h ^ 2) h := by
  have hd := HasDerivAt.fun_sum (u := s) fun j _ =>
    (hasDerivAt_expRow s hs d hh j).mul_const (d j)
  have hval : distanceVariance s d h / h ^ 2 =
      ∑ j ∈ s, Kernel.expRow s d h j * (d j - meanDistance s d h) / h ^ 2 * d j := by
    rw [distanceVariance_eq s hs d h]
    calc _ = ((∑ j ∈ s, Kernel.expRow s d h j * d j ^ 2) -
        meanDistance s d h * (∑ j ∈ s, Kernel.expRow s d h j * d j)) / h ^ 2 := by
          change (_ - meanDistance s d h ^ 2) / _ = (_ - meanDistance s d h * meanDistance s d h) / _
          ring
      _ = _ := by
        rw [mul_sum, ← sum_sub_distrib, sum_div]
        apply sum_congr rfl
        intro j _
        ring
  rw [hval]
  exact hd

/-- Expected neighbor distance is nondecreasing on positive bandwidths. -/
theorem meanDistance_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    MonotoneOn (meanDistance s d) (Set.Ioi 0) := by
  apply monotoneOn_of_deriv_nonneg (convex_Ioi 0)
  · exact fun h hh => (hasDerivAt_meanDistance s hs d (ne_of_gt hh)).continuousAt.continuousWithinAt
  · intro h hh
    exact (hasDerivAt_meanDistance s hs d (ne_of_gt (by simpa using hh))).differentiableAt.differentiableWithinAt
  · intro h hh
    rw [(hasDerivAt_meanDistance s hs d (ne_of_gt (by simpa using hh))).deriv]
    exact div_nonneg (distanceVariance_nonneg s hs d h) (sq_nonneg _)

/-- Entropy equals the log partition function plus the scaled mean distance. -/
theorem entropy_eq (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    entropy s d h = meanDistance s d h / h + Real.log (∑ j ∈ s, Real.exp (-d j / h)) := by
  have hZ : (∑ j ∈ s, Real.exp (-d j / h)) ≠ 0 :=
    ne_of_gt (sum_pos (fun _ _ => Real.exp_pos _) hs)
  have hlog : ∀ j, Real.log (Kernel.expRow s d h j) =
      -d j / h - Real.log (∑ k ∈ s, Real.exp (-d k / h)) := by
    intro j
    rw [Kernel.expRow, Real.log_div (Real.exp_pos _).ne' hZ, Real.log_exp]
  unfold entropy
  simp_rw [hlog]
  have heq : ∀ j, Kernel.expRow s d h j *
      (-d j / h - Real.log (∑ k ∈ s, Real.exp (-d k / h))) =
      -(Kernel.expRow s d h j * d j / h) -
        Real.log (∑ k ∈ s, Real.exp (-d k / h)) * Kernel.expRow s d h j := by
    intro j
    ring
  simp_rw [heq]
  rw [sum_sub_distrib, sum_neg_distrib, ← sum_div, ← mul_sum, Kernel.expRow_sum s hs d h]
  simp only [meanDistance]
  ring

/-- Entropy increases at distance variance divided by `h³`. -/
theorem hasDerivAt_entropy (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h : ℝ} (hh : h ≠ 0) :
    HasDerivAt (entropy s d) (distanceVariance s d h / h ^ 3) h := by
  set Z := ∑ k ∈ s, Real.exp (-d k / h)
  have hZ : Z ≠ 0 := ne_of_gt (sum_pos (fun _ _ => Real.exp_pos _) hs)
  have hZD : (∑ k ∈ s, Real.exp (-d k / h) * (d k / h ^ 2)) =
      Z * meanDistance s d h / h ^ 2 := by
    calc _ = (∑ k ∈ s, Real.exp (-d k / h) * d k) / h ^ 2 := by
          rw [sum_div]
          apply sum_congr rfl
          intro k _
          ring
      _ = _ := by rw [← partition_mul_mean s hs d h]
  have hdZ := hasDerivAt_partition s d hh
  rw [hZD] at hdZ
  have hd := ((hasDerivAt_meanDistance s hs d hh).div (hasDerivAt_id h) hh).add (hdZ.log hZ)
  have hval : (distanceVariance s d h / h ^ 2 * h - meanDistance s d h * 1) / h ^ 2 +
      (Z * meanDistance s d h / h ^ 2) / Z = distanceVariance s d h / h ^ 3 := by
    field_simp
    ring
  have hfun : entropy s d = fun u => meanDistance s d u / u +
      Real.log (∑ j ∈ s, Real.exp (-d j / u)) := funext (entropy_eq s hs d)
  rw [hfun, ← hval]
  exact hd

/-- Entropy is nondecreasing with bandwidth for a fixed row of distances. -/
theorem entropy_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    MonotoneOn (entropy s d) (Set.Ioi 0) := by
  apply monotoneOn_of_deriv_nonneg (convex_Ioi 0)
  · exact fun h hh => (hasDerivAt_entropy s hs d (ne_of_gt hh)).continuousAt.continuousWithinAt
  · intro h hh
    exact (hasDerivAt_entropy s hs d (ne_of_gt (by simpa using hh))).differentiableAt.differentiableWithinAt
  · intro h hh
    rw [(hasDerivAt_entropy s hs d (ne_of_gt (by simpa using hh))).deriv]
    have hhpos : 0 < h := by simpa using hh
    exact div_nonneg (distanceVariance_nonneg s hs d h) (pow_nonneg hhpos.le _)

/-- Oppositely ordered finite statistics have nonpositive weighted covariance. -/
theorem weighted_covariance_nonpos (s : Finset ι) (p f g : ι → ℝ)
    (hp : ∀ i ∈ s, 0 ≤ p i) (hsum : ∑ i ∈ s, p i = 1)
    (hopp : ∀ i ∈ s, ∀ j ∈ s, (f i - f j) * (g i - g j) ≤ 0) :
    ∑ i ∈ s, p i * f i * g i ≤
      (∑ i ∈ s, p i * f i) * (∑ i ∈ s, p i * g i) := by
  have hdouble : ∑ i ∈ s, ∑ j ∈ s,
      p i * p j * ((f i - f j) * (g i - g j)) ≤ 0 := by
    apply sum_nonpos
    intro i hi
    apply sum_nonpos
    intro j hj
    exact mul_nonpos_of_nonneg_of_nonpos (mul_nonneg (hp i hi) (hp j hj)) (hopp i hi j hj)
  have heq : ∀ i j,
      p i * p j * ((f i - f j) * (g i - g j)) =
        (p i * f i * g i) * p j + p i * (p j * f j * g j) -
        (p i * f i) * (p j * g j) - (p i * g i) * (p j * f j) := by
    intro i j
    ring
  simp_rw [heq, sum_sub_distrib, sum_add_distrib, ← mul_sum, hsum, mul_one] at hdouble
  rw [← sum_mul, ← sum_mul, ← sum_mul, hsum] at hdouble
  nlinarith

/-- Exponential weights and distances are oppositely ordered at positive bandwidth. -/
theorem weight_distance_antivary (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h : ℝ} (hh : 0 < h) (i j : ι) :
    (Kernel.expRow s d h i - Kernel.expRow s d h j) * (d i - d j) ≤ 0 := by
  have hZ : 0 < ∑ k ∈ s, Real.exp (-d k / h) := sum_pos (fun _ _ => Real.exp_pos _) hs
  by_cases hd : d i ≤ d j
  · have hp : Kernel.expRow s d h j ≤ Kernel.expRow s d h i := by
      apply div_le_div_of_nonneg_right _ hZ.le
      rw [Real.exp_le_exp]
      exact div_le_div_of_nonneg_right (by linarith) hh.le
    exact mul_nonpos_of_nonneg_of_nonpos (by linarith) (by linarith)
  · have hp : Kernel.expRow s d h i ≤ Kernel.expRow s d h j := by
      apply div_le_div_of_nonneg_right _ hZ.le
      rw [Real.exp_le_exp]
      exact div_le_div_of_nonneg_right (by linarith) hh.le
    exact mul_nonpos_of_nonpos_of_nonneg (by linarith) (by linarith)

/-- Derivative of row concentration, before imposing its sign. -/
theorem hasDerivAt_herfindahl (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h : ℝ} (hh : h ≠ 0) :
    HasDerivAt (herfindahl s d)
      (2 / h ^ 2 * ((∑ j ∈ s, Kernel.expRow s d h j ^ 2 * d j) -
        herfindahl s d h * meanDistance s d h)) h := by
  have hd := HasDerivAt.fun_sum (u := s) fun j _ =>
    (hasDerivAt_expRow s hs d hh j).pow 2
  have hval : 2 / h ^ 2 * ((∑ j ∈ s, Kernel.expRow s d h j ^ 2 * d j) -
      herfindahl s d h * meanDistance s d h) =
      ∑ j ∈ s, 2 * Kernel.expRow s d h j ^ (2 - 1) *
        (Kernel.expRow s d h j * (d j - meanDistance s d h) / h ^ 2) := by
    unfold herfindahl
    rw [sum_mul, ← sum_sub_distrib, mul_sum]
    apply sum_congr rfl
    intro j _
    norm_num
    ring
  rw [hval]
  exact hd

/-- Herfindahl concentration is nonincreasing for a fixed row of distances. -/
theorem herfindahl_antitoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    AntitoneOn (herfindahl s d) (Set.Ioi 0) := by
  apply antitoneOn_of_deriv_nonpos (convex_Ioi 0)
  · exact fun h hh => (hasDerivAt_herfindahl s hs d (ne_of_gt hh)).continuousAt.continuousWithinAt
  · intro h hh
    exact (hasDerivAt_herfindahl s hs d (ne_of_gt (by simpa using hh))).differentiableAt.differentiableWithinAt
  · intro h hh
    have hhpos : 0 < h := by simpa using hh
    rw [(hasDerivAt_herfindahl s hs d hhpos.ne').deriv]
    apply mul_nonpos_of_nonneg_of_nonpos (by positivity)
    have hc := weighted_covariance_nonpos s (Kernel.expRow s d h) (Kernel.expRow s d h) d
      (fun i _ => (Kernel.expRow_pos s hs d h i).le) (Kernel.expRow_sum s hs d h)
      (fun i _ j _ => weight_distance_antivary s hs d hhpos i j)
    simp only [← sq, herfindahl, meanDistance] at *
    linarith

/-- Effective neighbor count is nondecreasing wherever bandwidth is positive. -/
theorem effectiveNeighbors_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    MonotoneOn (effectiveNeighbors s d) (Set.Ioi 0) := by
  intro h hh u hu hhu
  apply inv_anti₀ _ (herfindahl_antitoneOn s hs d hh hu hhu)
  exact sum_pos (fun j _ => sq_pos_of_pos (Kernel.expRow_pos s hs d u j)) hs

/-- Tied distances always receive identical weights, including nearest-distance ties. -/
theorem equal_distance_weights (s : Finset ι) (d : ι → ℝ) (h : ℝ) {i j : ι}
    (hd : d i = d j) : Kernel.expRow s d h i = Kernel.expRow s d h j := by
  simp only [Kernel.expRow, hd]

/-- A constant row is uniform for every bandwidth, so a matched bandwidth is not unique. -/
theorem constant_distance_weights [DecidableEq ι] (s : Finset ι) (hs : s.Nonempty)
    (d : ι → ℝ) (h c : ℝ) (hd : ∀ j ∈ s, d j = c) {i : ι} (hi : i ∈ s) :
    Kernel.expRow s d h i = 1 / (s.card : ℝ) := by
  have hcard : (s.card : ℝ) ≠ 0 := by exact_mod_cast (card_pos.mpr hs).ne'
  have hsum : ∑ j ∈ s, Real.exp (-d j / h) = s.card * Real.exp (-c / h) := by
    calc _ = ∑ j ∈ s, Real.exp (-c / h) := sum_congr rfl (fun j hj => by rw [hd j hj])
      _ = _ := by rw [sum_const, nsmul_eq_mul]
  rw [Kernel.expRow, hd i hi, hsum]
  field_simp

/-- Constant-distance concentration has its exact uniform value. -/
theorem constant_distance_herfindahl [DecidableEq ι] (s : Finset ι) (hs : s.Nonempty)
    (d : ι → ℝ) (h c : ℝ) (hd : ∀ j ∈ s, d j = c) :
    herfindahl s d h = 1 / (s.card : ℝ) := by
  have hcard : (s.card : ℝ) ≠ 0 := by exact_mod_cast (card_pos.mpr hs).ne'
  unfold herfindahl
  calc _ = ∑ _j ∈ s, (1 / (s.card : ℝ)) ^ 2 :=
          sum_congr rfl (fun j hj => by rw [constant_distance_weights s hs d h c hd hj])
    _ = _ := by rw [sum_const, nsmul_eq_mul]; field_simp

/-- The effective neighbor count of a constant-distance row is its support size. -/
theorem constant_distance_effectiveNeighbors [DecidableEq ι] (s : Finset ι) (hs : s.Nonempty)
    (d : ι → ℝ) (h c : ℝ) (hd : ∀ j ∈ s, d j = c) :
    effectiveNeighbors s d h = (s.card : ℝ) := by
  simp only [effectiveNeighbors, constant_distance_herfindahl s hs d h c hd, one_div, inv_inv]

/-- Matching mean effective neighbors does not equalize mean Herfindahl concentration. -/
theorem matched_effective_not_concentration :
    ((1 / (1 / 2 : ℝ) + 1 / (1 / 2 : ℝ)) / 2 =
      (1 / (3 / 4 : ℝ) + 1 / (3 / 8 : ℝ)) / 2) ∧
    (((1 / 2 : ℝ) + 1 / 2) / 2 ≠ ((3 / 4 : ℝ) + 3 / 8) / 2) := by
  norm_num

open Filter in
/-- At infinite bandwidth every finite nonempty row tends to uniform weights. -/
theorem expRow_tendsto_atTop (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (i : ι) :
    Tendsto (fun h => Kernel.expRow s d h i) atTop (𝓝 (1 / (s.card : ℝ))) := by
  have hraw : ∀ j, Tendsto (fun h : ℝ => Real.exp (-d j / h)) atTop (𝓝 1) := by
    intro j
    simpa only [Function.comp_def, Real.exp_zero, id_eq] using Real.continuous_exp.continuousAt.tendsto.comp
      ((tendsto_const_nhds : Tendsto (fun _ : ℝ => -d j) atTop (𝓝 (-d j))).div_atTop tendsto_id)
  have hden := tendsto_finsetSum s (fun j _ => hraw j)
  have hcard : (s.card : ℝ) ≠ 0 := by exact_mod_cast (card_pos.mpr hs).ne'
  simpa only [Kernel.expRow, sum_const, nsmul_eq_mul, mul_one, Pi.div_def] using
    (hraw i).div hden (by simpa using hcard)

open Filter in
/-- At vanishing positive bandwidth the row is uniform among all nearest-distance ties. -/
theorem expRow_tendsto_zero [DecidableEq ι] (s : Finset ι) (d : ι → ℝ) (m : ℝ)
    (hmin : ∀ j ∈ s, m ≤ d j) (hattain : ∃ j ∈ s, d j = m) {i : ι} (hi : i ∈ s) :
    Tendsto (fun h => Kernel.expRow s d h i) (𝓝[>] 0)
      (𝓝 ((if d i = m then 1 else 0) / ((s.filter fun j => d j = m).card : ℝ))) := by
  classical
  have hs : s.Nonempty := by obtain ⟨j, hj, _⟩ := hattain; exact ⟨j, hj⟩
  have hties : (s.filter fun j => d j = m).Nonempty := by
    obtain ⟨j, hj, hd⟩ := hattain
    exact ⟨j, mem_filter.mpr ⟨hj, hd⟩⟩
  have hraw : ∀ j ∈ s, Tendsto (fun h : ℝ => Real.exp (-(d j - m) / h)) (𝓝[>] 0)
      (𝓝 (if d j = m then 1 else 0)) := by
    intro j hj
    by_cases hd : d j = m
    · simp [hd]
    · have hpos : 0 < d j - m := by have := hmin j hj; exact sub_pos.mpr (lt_of_le_of_ne this (Ne.symm hd))
      have ht : Tendsto (fun h : ℝ => (d j - m) / h) (𝓝[>] 0) atTop := by
        simpa only [div_eq_mul_inv] using Tendsto.const_mul_atTop hpos tendsto_inv_nhdsGT_zero
      simpa only [neg_div, ite_eq_right hd, Function.comp_def] using Real.tendsto_exp_neg_atTop_nhds_zero.comp ht
  have hden := tendsto_finsetSum s hraw
  have hden' : Tendsto (fun h : ℝ => ∑ j ∈ s, Real.exp (-(d j - m) / h)) (𝓝[>] 0)
      (𝓝 ((s.filter fun j => d j = m).card : ℝ)) := by simpa using hden
  have hcard : ((s.filter fun j => d j = m).card : ℝ) ≠ 0 := by
    exact_mod_cast (card_pos.mpr hties).ne'
  have hshift : ∀ h, Kernel.expRow s d h i = Kernel.expRow s (fun j => d j - m) h i := by
    intro h
    have hd : (fun j => (d j - m) + m) = d := by funext j; ring
    have hc := congrFun (Kernel.expRow_add_const s (fun j => d j - m) h m) i
    simpa only [hd] using hc
  have ht : Tendsto (fun h => Kernel.expRow s (fun j => d j - m) h i) (𝓝[>] 0)
      (𝓝 ((if d i = m then 1 else 0) / ((s.filter fun j => d j = m).card : ℝ))) := by
    simpa only [Kernel.expRow, Pi.div_def] using (hraw i hi).div hden' hcard
  exact ht.congr (fun h => (hshift h).symm)

open Filter in
/-- The upper limiting effective-neighbor count is the whole support size. -/
theorem effectiveNeighbors_tendsto_atTop (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    Tendsto (effectiveNeighbors s d) atTop (𝓝 (s.card : ℝ)) := by
  have hcard : (s.card : ℝ) ≠ 0 := by exact_mod_cast (card_pos.mpr hs).ne'
  have hconst : (∑ _j ∈ s, (1 / (s.card : ℝ)) ^ 2) = 1 / (s.card : ℝ) := by
    rw [sum_const, nsmul_eq_mul]
    field_simp
  have ht := tendsto_finsetSum s (fun j _ => (expRow_tendsto_atTop s hs d j).pow 2)
  rw [hconst] at ht
  change Tendsto (fun h => (∑ j ∈ s, Kernel.expRow s d h j ^ 2)⁻¹) atTop (𝓝 (s.card : ℝ))
  simpa only [Pi.inv_def, one_div, inv_inv] using ht.inv₀ (one_div_ne_zero hcard)

open Filter in
/-- The lower limiting effective-neighbor count includes every nearest-distance tie. -/
theorem effectiveNeighbors_tendsto_zero [DecidableEq ι] (s : Finset ι) (d : ι → ℝ) (m : ℝ)
    (hmin : ∀ j ∈ s, m ≤ d j) (hattain : ∃ j ∈ s, d j = m) :
    Tendsto (effectiveNeighbors s d) (𝓝[>] 0)
      (𝓝 ((s.filter fun j => d j = m).card : ℝ)) := by
  classical
  have hties : (s.filter fun j => d j = m).Nonempty := by
    obtain ⟨j, hj, hd⟩ := hattain
    exact ⟨j, mem_filter.mpr ⟨hj, hd⟩⟩
  set M : ℝ := ((s.filter fun j => d j = m).card : ℝ)
  have hM : M ≠ 0 := by
    dsimp [M]
    exact_mod_cast (card_pos.mpr hties).ne'
  have hconst : (∑ j ∈ s, ((if d j = m then 1 else 0) / M) ^ 2) = 1 / M := by
    have heq : ∀ j, ((if d j = m then 1 else 0) / M) ^ 2 =
        if d j = m then (1 / M) ^ 2 else 0 := by intro j; split_ifs <;> simp
    simp_rw [heq]
    rw [sum_ite, sum_const_zero, add_zero, sum_const, nsmul_eq_mul]
    change M * (1 / M) ^ 2 = 1 / M
    field_simp
  have ht := tendsto_finsetSum s
    (fun j hj => (expRow_tendsto_zero s d m hmin hattain hj).pow 2)
  change Tendsto (fun h => ∑ j ∈ s, Kernel.expRow s d h j ^ 2) (𝓝[>] 0)
    (𝓝 (∑ j ∈ s, ((if d j = m then 1 else 0) / M) ^ 2)) at ht
  rw [hconst] at ht
  change Tendsto (fun h => (∑ j ∈ s, Kernel.expRow s d h j ^ 2)⁻¹) (𝓝[>] 0) (𝓝 M)
  simpa only [Pi.inv_def, one_div, inv_inv] using ht.inv₀ (one_div_ne_zero hM)

/-- Positive finite rows have positive Herfindahl concentration. -/
theorem herfindahl_pos (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    0 < herfindahl s d h :=
  sum_pos (fun j _ => sq_pos_of_pos (Kernel.expRow_pos s hs d h j)) hs

/-- Effective-neighbor count is continuous on positive bandwidths. -/
theorem effectiveNeighbors_continuousOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) :
    ContinuousOn (effectiveNeighbors s d) (Set.Ioi 0) := by
  intro h hh
  change ContinuousWithinAt (fun u => (herfindahl s d u)⁻¹) (Set.Ioi 0) h
  exact ((hasDerivAt_herfindahl s hs d (ne_of_gt hh)).continuousAt.inv₀
    (herfindahl_pos s hs d h).ne').continuousWithinAt

open Filter in
/-- Every count strictly between the nearest-tie size and full support is attained.
No uniqueness is asserted; constant rows have no such interior target. -/
theorem exists_matched_bandwidth [DecidableEq ι] (s : Finset ι) (d : ι → ℝ) (m : ℝ)
    (hmin : ∀ j ∈ s, m ≤ d j) (hattain : ∃ j ∈ s, d j = m) {q : ℝ}
    (hqlo : ((s.filter fun j => d j = m).card : ℝ) < q) (hqhi : q < (s.card : ℝ)) :
    ∃ h, 0 < h ∧ effectiveNeighbors s d h = q := by
  classical
  have hs : s.Nonempty := by obtain ⟨j, hj, _⟩ := hattain; exact ⟨j, hj⟩
  have hl := effectiveNeighbors_tendsto_zero s d m hmin hattain
  have hu := effectiveNeighbors_tendsto_atTop s hs d
  have hsmall : ∀ᶠ h in 𝓝[>] (0 : ℝ), 0 < h ∧ effectiveNeighbors s d h < q :=
    Filter.Eventually.and self_mem_nhdsWithin (hl.eventually (eventually_lt_nhds hqlo))
  obtain ⟨a, ha, haq⟩ := hsmall.exists
  have hlarge : ∀ᶠ h : ℝ in atTop, a < h ∧ q < effectiveNeighbors s d h :=
    (eventually_gt_atTop a).and (hu.eventually (eventually_gt_nhds hqhi))
  obtain ⟨b, hab, hqb⟩ := hlarge.exists
  have hcont : ContinuousOn (effectiveNeighbors s d) (Set.Icc a b) :=
    (effectiveNeighbors_continuousOn s hs d).mono fun h hh => ha.trans_le hh.1
  obtain ⟨h, hhab, hhq⟩ := intermediate_value_Icc hab.le hcont ⟨haq.le, hqb.le⟩
  exact ⟨h, ha.trans_le hhab.1, hhq⟩

/-- The imported idiosyncratic-noise cost, with heterogeneous fixed variances. -/
noncomputable def noisePenalty (s : Finset ι) (d η : ι → ℝ) (h : ℝ) : ℝ :=
  ∑ j ∈ s, Kernel.expRow s d h j ^ 2 * η j

/-- A wider bandwidth lowers Herfindahl concentration while raising the heterogeneous
noise penalty. Both bandwidths, all raw weights and both innovation variances are positive. -/
theorem heterogeneous_noise_can_increase :
    let d : Fin 2 → ℝ := ![0, 2 * Real.log 3]
    let η : Fin 2 → ℝ := ![1, 9]
    herfindahl univ d 2 < herfindahl univ d 1 ∧
      noisePenalty univ d η 1 < noisePenalty univ d η 2 := by
  dsimp
  have h1 : Real.exp (-(2 * Real.log 3)) = 1 / 9 := by
    rw [Real.exp_neg, show 2 * Real.log 3 = Real.log 3 + Real.log 3 by ring,
      Real.exp_add, Real.exp_log (by norm_num : (0 : ℝ) < 3)]
    norm_num
  have h2 : Real.exp (-(2 * Real.log 3) / 2) = 1 / 3 := by
    rw [show -(2 * Real.log 3) / 2 = -Real.log 3 by ring,
      Real.exp_neg, Real.exp_log (by norm_num : (0 : ℝ) < 3)]
    norm_num
  norm_num [herfindahl, noisePenalty, Kernel.expRow, Fin.sum_univ_two, h1, h2]

/-! ## Likelihood-ratio and stochastic ordering at fixed costs -/

/-- Increasing positive bandwidth gives an increasing likelihood ratio in the fixed cost.
The division-free form avoids assigning an order to firm indices. -/
theorem likelihoodRatio_cross_le (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    {h₁ h₂ : ℝ} (hh₁ : 0 < h₁) (h₁₂ : h₁ ≤ h₂) (i j : ι) (hd : d i ≤ d j) :
    Kernel.expRow s d h₂ i * Kernel.expRow s d h₁ j ≤
      Kernel.expRow s d h₁ i * Kernel.expRow s d h₂ j := by
  have hh₂ : 0 < h₂ := hh₁.trans_le h₁₂
  have hZ₁ : 0 < ∑ k ∈ s, Real.exp (-d k / h₁) := sum_pos (fun _ _ => Real.exp_pos _) hs
  have hZ₂ : 0 < ∑ k ∈ s, Real.exp (-d k / h₂) := sum_pos (fun _ _ => Real.exp_pos _) hs
  have hinv : h₂⁻¹ ≤ h₁⁻¹ := inv_anti₀ hh₁ h₁₂
  have hexp : Real.exp (-d i / h₂) * Real.exp (-d j / h₁) ≤
      Real.exp (-d i / h₁) * Real.exp (-d j / h₂) := by
    rw [← Real.exp_add, ← Real.exp_add, Real.exp_le_exp]
    simp only [div_eq_mul_inv]
    nlinarith [mul_nonneg (sub_nonneg.mpr hd) (sub_nonneg.mpr hinv)]
  unfold Kernel.expRow
  rw [div_mul_div_comm, div_mul_div_comm,
    mul_comm (∑ k ∈ s, Real.exp (-d k / h₂)) (∑ k ∈ s, Real.exp (-d k / h₁))]
  exact div_le_div_of_nonneg_right hexp (mul_pos hZ₁ hZ₂).le

/-- At tied costs the likelihood-ratio cross-products are equal. -/
theorem likelihoodRatio_cross_eq_of_cost_eq (s : Finset ι) (d : ι → ℝ)
    (h₁ h₂ : ℝ) {i j : ι} (hd : d i = d j) :
    Kernel.expRow s d h₂ i * Kernel.expRow s d h₁ j =
      Kernel.expRow s d h₁ i * Kernel.expRow s d h₂ j := by
  rw [equal_distance_weights s d h₂ hd, equal_distance_weights s d h₁ hd]
  exact mul_comm _ _

/-- Pairwise concordance of cross-products orders expectations of unit-mass arrays.
The identity is finite algebra; probability interpretations additionally require nonnegativity. -/
theorem sum_expectation_le_of_cross (s : Finset ι) (p q g : ι → ℝ)
    (hp : ∑ i ∈ s, p i = 1) (hq : ∑ i ∈ s, q i = 1)
    (hcross : ∀ i ∈ s, ∀ j ∈ s, 0 ≤ (q i * p j - p i * q j) * (g i - g j)) :
    ∑ i ∈ s, p i * g i ≤ ∑ i ∈ s, q i * g i := by
  have hdouble : 0 ≤ ∑ i ∈ s, ∑ j ∈ s,
      (q i * p j - p i * q j) * (g i - g j) :=
    sum_nonneg fun i hi => sum_nonneg fun j hj => hcross i hi j hj
  have heq : ∀ i j, (q i * p j - p i * q j) * (g i - g j) =
      (q i * g i) * p j + p i * (q j * g j) -
        q i * (p j * g j) - (p i * g i) * q j := by
    intro i j
    ring
  simp_rw [heq, sum_sub_distrib, sum_add_distrib, ← mul_sum, hp, hq, mul_one] at hdouble
  rw [← sum_mul, ← sum_mul, hp, hq] at hdouble
  linarith

/-- A fixed observable of cost, averaged under the exponential row. -/
noncomputable def observableMean (s : Finset ι) (d φ : ι → ℝ) (h : ℝ) : ℝ :=
  ∑ j ∈ s, Kernel.expRow s d h j * φ j

/-- Every observable increasing in fixed cost has increasing expectation with bandwidth.
Only ordering on the finite support is needed; no order is imposed on the indices. -/
theorem observableMean_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d φ : ι → ℝ)
    (hφ : ∀ i ∈ s, ∀ j ∈ s, d i ≤ d j → φ i ≤ φ j) :
    MonotoneOn (observableMean s d φ) (Set.Ioi 0) := by
  intro h₁ hh₁ h₂ hh₂ h₁₂
  apply sum_expectation_le_of_cross s (Kernel.expRow s d h₁) (Kernel.expRow s d h₂) φ
    (Kernel.expRow_sum s hs d h₁) (Kernel.expRow_sum s hs d h₂)
  intro i hi j hj
  by_cases hd : d i ≤ d j
  · exact mul_nonneg_of_nonpos_of_nonpos
      (sub_nonpos.mpr (likelihoodRatio_cross_le s hs d hh₁ h₁₂ i j hd))
      (sub_nonpos.mpr (hφ i hi j hj hd))
  · have hji : d j ≤ d i := le_of_not_ge hd
    have hcross := likelihoodRatio_cross_le s hs d hh₁ h₁₂ j i hji
    apply mul_nonneg
    · nlinarith
    · exact sub_nonneg.mpr (hφ j hj i hi hji)

/-- The usual real-valued monotone-test-function formulation of stochastic ordering. -/
theorem monotone_cost_expectation (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    (φ : ℝ → ℝ) (hφ : Monotone φ) :
    MonotoneOn (fun h => ∑ j ∈ s, Kernel.expRow s d h j * φ (d j)) (Set.Ioi 0) :=
  observableMean_monotoneOn s hs d (φ ∘ d) (fun _ _ _ _ hij => hφ hij)

/-- Mass strictly above a fixed cost threshold. -/
noncomputable def upperTail (s : Finset ι) (d : ι → ℝ) (t h : ℝ) : ℝ :=
  ∑ j ∈ s.filter (fun j => t < d j), Kernel.expRow s d h j

/-- Mass at or above a fixed cost threshold, retaining threshold ties. -/
noncomputable def closedUpperTail (s : Finset ι) (d : ι → ℝ) (t h : ℝ) : ℝ :=
  ∑ j ∈ s.filter (fun j => t ≤ d j), Kernel.expRow s d h j

/-- The cost CDF, with all mass tied at the threshold included. -/
noncomputable def cdf (s : Finset ι) (d : ι → ℝ) (t h : ℝ) : ℝ :=
  ∑ j ∈ s.filter (fun j => d j ≤ t), Kernel.expRow s d h j

/-- Strict upper tails are nondecreasing with positive bandwidth. -/
theorem upperTail_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t : ℝ) :
    MonotoneOn (upperTail s d t) (Set.Ioi 0) := by
  have htest : ∀ i ∈ s, ∀ j ∈ s, d i ≤ d j →
      (if t < d i then (1 : ℝ) else 0) ≤ (if t < d j then (1 : ℝ) else 0) := by
    intro i hi j hj hij
    by_cases hti : t < d i
    · simp [hti, hti.trans_le hij]
    · split_ifs <;> norm_num
  have hm := observableMean_monotoneOn s hs d (fun j => if t < d j then 1 else 0) htest
  intro h₁ hh₁ h₂ hh₂ h₁₂
  simpa only [observableMean, upperTail, sum_filter, mul_ite, mul_one, mul_zero] using
    hm hh₁ hh₂ h₁₂

/-- Closed upper tails are nondecreasing as well, including every cost tie. -/
theorem closedUpperTail_monotoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t : ℝ) :
    MonotoneOn (closedUpperTail s d t) (Set.Ioi 0) := by
  have htest : ∀ i ∈ s, ∀ j ∈ s, d i ≤ d j →
      (if t ≤ d i then (1 : ℝ) else 0) ≤ (if t ≤ d j then (1 : ℝ) else 0) := by
    intro i hi j hj hij
    by_cases hti : t ≤ d i
    · simp [hti, hti.trans hij]
    · split_ifs <;> norm_num
  have hm := observableMean_monotoneOn s hs d (fun j => if t ≤ d j then 1 else 0) htest
  intro h₁ hh₁ h₂ hh₂ h₁₂
  simpa only [observableMean, closedUpperTail, sum_filter, mul_ite, mul_one, mul_zero] using
    hm hh₁ hh₂ h₁₂

/-- Strict upper-tail mass and the closed lower tail partition unit mass. -/
theorem upperTail_add_cdf (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t h : ℝ) :
    upperTail s d t h + cdf s d t h = 1 := by
  have hsum := sum_filter_add_sum_filter_not s (fun j => t < d j) (fun j => Kernel.expRow s d h j)
  simpa only [upperTail, cdf, not_lt, Kernel.expRow_sum s hs d h] using hsum

/-- The cost CDF decreases with positive bandwidth: first-order stochastic dominance. -/
theorem cdf_antitoneOn (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t : ℝ) :
    AntitoneOn (cdf s d t) (Set.Ioi 0) := by
  intro h₁ hh₁ h₂ hh₂ h₁₂
  have htail := upperTail_monotoneOn s hs d t hh₁ hh₂ h₁₂
  linarith [upperTail_add_cdf s hs d t h₁, upperTail_add_cdf s hs d t h₂]

/-- A singleton support has the same observable expectation at every bandwidth. -/
@[simp] theorem observableMean_singleton (i : ι) (d φ : ι → ℝ) (h : ℝ) :
    observableMean {i} d φ h = φ i := by
  simp [observableMean, Kernel.expRow_singleton]

/-- A constant cost row has constant cost-observable expectations, including tied costs. -/
theorem constant_cost_expectation (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ)
    (φ : ℝ → ℝ) (c h : ℝ) (hd : ∀ j ∈ s, d j = c) :
    (∑ j ∈ s, Kernel.expRow s d h j * φ (d j)) = φ c := by
  calc _ = ∑ j ∈ s, φ c * Kernel.expRow s d h j :=
          sum_congr rfl (fun j hj => by rw [hd j hj]; ring)
    _ = _ := by rw [← mul_sum, Kernel.expRow_sum s hs d h, mul_one]

/-- Above the whole cost range the strict upper tail is zero. -/
theorem upperTail_eq_zero (s : Finset ι) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, d j ≤ t) : upperTail s d t h = 0 := by
  have hfilter : s.filter (fun j => t < d j) = ∅ :=
    filter_eq_empty_iff.mpr fun j hj => not_lt.mpr (hd j hj)
  simp [upperTail, hfilter]

/-- Below the whole cost range the strict upper tail is one. -/
theorem upperTail_eq_one (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, t < d j) : upperTail s d t h = 1 := by
  rw [upperTail, filter_eq_self.mpr hd]
  exact Kernel.expRow_sum s hs d h

/-- A closed upper threshold strictly above all costs has zero mass. -/
theorem closedUpperTail_eq_zero (s : Finset ι) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, d j < t) : closedUpperTail s d t h = 0 := by
  have hfilter : s.filter (fun j => t ≤ d j) = ∅ :=
    filter_eq_empty_iff.mpr fun j hj => not_le.mpr (hd j hj)
  simp [closedUpperTail, hfilter]

/-- A closed upper threshold at or below all costs has unit mass. -/
theorem closedUpperTail_eq_one (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, t ≤ d j) : closedUpperTail s d t h = 1 := by
  rw [closedUpperTail, filter_eq_self.mpr hd]
  exact Kernel.expRow_sum s hs d h

/-- Below the whole cost range the cost CDF is zero. -/
theorem cdf_eq_zero (s : Finset ι) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, t < d j) : cdf s d t h = 0 := by
  have hfilter : s.filter (fun j => d j ≤ t) = ∅ :=
    filter_eq_empty_iff.mpr fun j hj => not_le.mpr (hd j hj)
  simp [cdf, hfilter]

/-- At or above the whole cost range the cost CDF is one. -/
theorem cdf_eq_one (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (t h : ℝ)
    (hd : ∀ j ∈ s, d j ≤ t) : cdf s d t h = 1 := by
  rw [cdf, filter_eq_self.mpr hd]
  exact Kernel.expRow_sum s hs d h

/-- The totalized zero-bandwidth expression is uniform; it is not the positive-bandwidth
limit at zero. Order results therefore use the open positive domain. -/
@[simp] theorem expRow_zero_bandwidth (s : Finset ι) (d : ι → ℝ) (i : ι) :
    Kernel.expRow s d 0 i = 1 / (s.card : ℝ) := by
  simp [Kernel.expRow]

end FreeFoundations.Bandwidth
