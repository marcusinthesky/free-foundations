import Mathlib.Analysis.Matrix.Normed
import Mathlib.Analysis.SpecialFunctions.Exp

/-!
# Kernel sensitivity

The networks are row-normalised exponential kernels on the other firms,
`Wᵢⱼ = exp(−dᵢⱼ/h) / Σₖ≠ᵢ exp(−dᵢₖ/h)`. Two facts govern how distance error reaches the
network:

* only `d/h` matters, so a distance scale and a bandwidth are never separately
  interpretable;
* if every scaled distance in a row moves by at most `b`, the sharp row `ℓ₁` bound is
  `2(eᵇ − 1)/(eᵇ + 1)`. With a common bandwidth, `b = δ/h`. Narrow bandwidths amplify error.

The second is uniform in `δ`: an average distance guarantee does not give it. Row bounds here
are in `ℓ₁`, whose maximum between probability vectors is 2. Total variation in the usual
probability convention is half of it; the Python geometry
summaries (`row_total_variation_gap`) use that convention.
-/

namespace FreeFoundations.Kernel

open Finset

variable {ι : Type*}

/-- Two positive weight vectors whose ratios lie in `[1/r, r]` normalise to probability
vectors within `ℓ₁` distance `r² − 1`. -/
theorem normalized_l1_le (s : Finset ι) (x y : ι → ℝ) {r : ℝ} (hr : 1 ≤ r)
    (hs : s.Nonempty) (hx : ∀ j ∈ s, 0 < x j) (hlo : ∀ j ∈ s, x j ≤ r * y j)
    (hhi : ∀ j ∈ s, y j ≤ r * x j) :
    ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤ r ^ 2 - 1 := by
  have hr0 : 0 < r := by linarith
  have hy : ∀ j ∈ s, 0 < y j := fun j hj => by
    have := hlo j hj
    have := hx j hj
    nlinarith
  set X := ∑ k ∈ s, x k
  set Y := ∑ k ∈ s, y k
  have hX : 0 < X := sum_pos hx hs
  have hY : 0 < Y := sum_pos hy hs
  have hXY : X ≤ r * Y := by rw [mul_sum]; exact sum_le_sum hlo
  have hYX : Y ≤ r * X := by rw [mul_sum]; exact sum_le_sum hhi
  have hterm : ∀ j ∈ s, |y j / Y - x j / X| ≤ (r ^ 2 - 1) * (x j / X) := by
    intro j hj
    have hxj := hx j hj
    have hyj := hy j hj
    have hqp : y j / Y ≤ r ^ 2 * (x j / X) := by
      rw [← mul_div_assoc, div_le_div_iff₀ hY hX]
      calc y j * X ≤ (r * x j) * (r * Y) :=
            mul_le_mul (hhi j hj) hXY hX.le (mul_nonneg hr0.le hxj.le)
        _ = r ^ 2 * x j * Y := by ring
    have hpq : x j / X ≤ r ^ 2 * (y j / Y) := by
      rw [← mul_div_assoc, div_le_div_iff₀ hX hY]
      calc x j * Y ≤ (r * y j) * (r * X) :=
            mul_le_mul (hlo j hj) hYX hY.le (mul_nonneg hr0.le hyj.le)
        _ = r ^ 2 * y j * X := by ring
    have hp : 0 ≤ x j / X := div_nonneg hxj.le hX.le
    generalize x j / X = p at hqp hpq hp ⊢
    generalize y j / Y = q at hqp hpq ⊢
    have hlow : 0 ≤ r ^ 2 * (q - (2 - r ^ 2) * p) := by
      nlinarith [mul_nonneg hp (sq_nonneg (r ^ 2 - 1))]
    have hlow' : 0 ≤ q - (2 - r ^ 2) * p := nonneg_of_mul_nonneg_right hlow (by positivity)
    rw [abs_le]
    constructor <;> nlinarith
  have hsum : ∑ j ∈ s, x j / X = 1 := by rw [← sum_div, div_self hX.ne']
  calc _ ≤ ∑ j ∈ s, (r ^ 2 - 1) * (x j / X) := sum_le_sum hterm
    _ = r ^ 2 - 1 := by rw [← mul_sum, hsum, mul_one]

/-- Any two normalisations are within `ℓ₁` distance 2. -/
theorem normalized_l1_le_two (s : Finset ι) (x y : ι → ℝ) (hx : ∀ j ∈ s, 0 ≤ x j)
    (hy : ∀ j ∈ s, 0 ≤ y j) :
    ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤ 2 := by
  have hX := sum_nonneg hx
  have hY := sum_nonneg hy
  calc _ ≤ ∑ j ∈ s, (y j / ∑ k ∈ s, y k + x j / ∑ k ∈ s, x k) :=
        sum_le_sum fun j hj => (abs_sub _ _).trans (by
          rw [abs_of_nonneg (div_nonneg (hy j hj) hY), abs_of_nonneg (div_nonneg (hx j hj) hX)])
    _ = (∑ j ∈ s, y j) / ∑ k ∈ s, y k + (∑ j ∈ s, x j) / ∑ k ∈ s, x k := by
        rw [sum_add_distrib, sum_div, sum_div]
    _ ≤ 1 + 1 := add_le_add (div_self_le_one _) (div_self_le_one _)
    _ = 2 := by norm_num

/-- Sharp normalization sensitivity. The hypotheses constrain ratios of the raw weights;
the conclusion is row L1 distance, twice conventional total variation. -/
theorem normalized_l1_le_sharp (s : Finset ι) (x y : ι → ℝ) {r : ℝ} (hr : 1 ≤ r)
    (hs : s.Nonempty) (hx : ∀ j ∈ s, 0 < x j) (hlo : ∀ j ∈ s, x j ≤ r * y j)
    (hhi : ∀ j ∈ s, y j ≤ r * x j) :
    ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤
      2 * (r - 1) / (r + 1) := by
  by_cases hr1 : r = 1
  · subst r
    have heq : ∀ j ∈ s, y j = x j := fun j hj => by
      have := hlo j hj
      have := hhi j hj
      linarith
    have hsum : ∑ k ∈ s, y k = ∑ k ∈ s, x k := sum_congr rfl heq
    simp only [hsum]
    have hz : ∑ j ∈ s, |y j / ∑ k ∈ s, x k - x j / ∑ k ∈ s, x k| = 0 := by
      apply sum_eq_zero
      intro j hj
      rw [heq j hj, sub_self, abs_zero]
    rw [hz]
    norm_num
  have hrpos : 0 < r := by linarith
  have hrsub : 0 < r - 1 := sub_pos.mpr (lt_of_le_of_ne hr (Ne.symm hr1))
  have hy : ∀ j ∈ s, 0 < y j := fun j hj => by
    have := hlo j hj
    have := hx j hj
    nlinarith
  set X := ∑ k ∈ s, x k
  set Y := ∑ k ∈ s, y k
  have hX : 0 < X := sum_pos hx hs
  have hY : 0 < Y := sum_pos hy hs
  have hXY : X ≤ r * Y := by rw [mul_sum]; exact sum_le_sum hlo
  have hYX : Y ≤ r * X := by rw [mul_sum]; exact sum_le_sum hhi
  have hsecant : ∀ j ∈ s,
      (r ^ 2 - 1) * |X * y j - Y * x j| ≤
        (r * X - Y) * (r * y j - x j) + (r * Y - X) * (r * x j - y j) := by
    intro j hj
    have h1 : 0 ≤ (r * Y - X) * (r * x j - y j) :=
      mul_nonneg (by linarith) (by linarith [hhi j hj])
    have h2 : 0 ≤ (r * X - Y) * (r * y j - x j) :=
      mul_nonneg (by linarith) (by linarith [hlo j hj])
    rcases le_total 0 (X * y j - Y * x j) with ht | ht
    · rw [abs_of_nonneg ht]
      nlinarith
    · rw [abs_of_nonpos ht]
      nlinarith
  set S := ∑ j ∈ s, |X * y j - Y * x j|
  have hsum : (r ^ 2 - 1) * S ≤ 2 * (r * X - Y) * (r * Y - X) := by
    calc _ = ∑ j ∈ s, (r ^ 2 - 1) * |X * y j - Y * x j| := by rw [mul_sum]
      _ ≤ ∑ j ∈ s, ((r * X - Y) * (r * y j - x j) +
          (r * Y - X) * (r * x j - y j)) := sum_le_sum hsecant
      _ = _ := by
        rw [sum_add_distrib, ← mul_sum, ← mul_sum, sum_sub_distrib,
          sum_sub_distrib, ← mul_sum, ← mul_sum]
        dsimp [X, Y]
        ring
  have hprod : (r * X - Y) * (r * Y - X) ≤ (r - 1) ^ 2 * X * Y := by
    nlinarith [mul_nonneg hrpos.le (sq_nonneg (X - Y))]
  have hcancel : (r + 1) * S ≤ 2 * (r - 1) * X * Y := by
    apply (mul_le_mul_iff_right₀ hrsub).mp
    calc (r - 1) * ((r + 1) * S) = (r ^ 2 - 1) * S := by ring
      _ ≤ 2 * (r * X - Y) * (r * Y - X) := hsum
      _ ≤ 2 * ((r - 1) ^ 2 * X * Y) := by linarith
      _ = _ := by ring
  have hterm : ∀ j, |y j / Y - x j / X| = |X * y j - Y * x j| / (X * Y) := by
    intro j
    have heq : y j / Y - x j / X = (X * y j - Y * x j) / (X * Y) := by
      field_simp
    rw [heq, abs_div, abs_of_pos (mul_pos hX hY)]
  simp_rw [hterm]
  rw [← sum_div]
  exact (div_le_div_iff₀ (mul_pos hX hY) (by linarith : 0 < r + 1)).mpr (by
    dsimp [S] at hcancel
    nlinarith)

/-- One row of the exponential kernel over the firms `s`. -/
noncomputable def expRow (s : Finset ι) (d : ι → ℝ) (h : ℝ) (j : ι) : ℝ :=
  Real.exp (-d j / h) / ∑ k ∈ s, Real.exp (-d k / h)

/-- **Scale.** Rescaling distances and bandwidth together leaves the kernel unchanged. -/
theorem expRow_scale (s : Finset ι) (d : ι → ℝ) (h c : ℝ) (hc : c ≠ 0) :
    expRow s (fun j => c * d j) (c * h) = expRow s d h := by
  funext j
  have key : ∀ k, -(c * d k) / (c * h) = -d k / h := fun k => by
    rw [neg_div, neg_div, mul_div_mul_left _ _ hc]
  simp only [expRow, key]

/-- A common additive distance shift cancels in row normalization. -/
theorem expRow_add_const (s : Finset ι) (d : ι → ℝ) (h c : ℝ) :
    expRow s (fun j => d j + c) h = expRow s d h := by
  funext j
  have hraw : ∀ k, Real.exp (-(d k + c) / h) =
      Real.exp (-c / h) * Real.exp (-d k / h) := by
    intro k
    rw [← Real.exp_add]
    congr 1
    ring
  simp only [expRow, hraw, ← mul_sum]
  rw [mul_div_mul_left _ _ (Real.exp_pos _).ne']

/-- **Row sensitivity.** If each distance in the row moves by at most `δ`, the row moves in
`ℓ₁` by at most `min(2, e^{2δ/h} − 1)`. -/
theorem expRow_l1_le (s : Finset ι) (hs : s.Nonempty) (d dh : ι → ℝ) {h δ : ℝ} (hh : 0 < h)
    (hδ : ∀ j ∈ s, |dh j - d j| ≤ δ) :
    ∑ j ∈ s, |expRow s dh h j - expRow s d h j| ≤ min 2 (Real.exp (2 * δ / h) - 1) := by
  obtain ⟨j₀, hj₀⟩ := hs
  have hδ0 : 0 ≤ δ := (abs_nonneg _).trans (hδ j₀ hj₀)
  have hr : 1 ≤ Real.exp (δ / h) := Real.one_le_exp (div_nonneg hδ0 hh.le)
  have hbound : ∀ j ∈ s, ∀ a b : ℝ, |a - b| ≤ δ →
      Real.exp (-b / h) ≤ Real.exp (δ / h) * Real.exp (-a / h) := by
    intro j _ a b hab
    rw [← Real.exp_add, Real.exp_le_exp, ← add_div, div_le_div_iff_of_pos_right hh]
    linarith [(abs_le.mp hab).2]
  refine le_min (normalized_l1_le_two s _ _ (fun _ _ => (Real.exp_pos _).le)
    (fun _ _ => (Real.exp_pos _).le)) ?_
  have hsq : Real.exp (2 * δ / h) = Real.exp (δ / h) ^ 2 := by
    rw [sq, ← Real.exp_add]
    ring_nf
  rw [hsq]
  exact normalized_l1_le s _ _ hr ⟨j₀, hj₀⟩ (fun _ _ => Real.exp_pos _)
    (fun j hj => hbound j hj (dh j) (d j) (hδ j hj))
    (fun j hj => hbound j hj (d j) (dh j) (by rw [abs_sub_comm]; exact hδ j hj))

/-- The sharp row-L1 sensitivity as a function of scaled-distance error. -/
noncomputable def sensitivity (b : ℝ) : ℝ :=
  2 * (Real.exp b - 1) / (Real.exp b + 1)

theorem sensitivity_nonneg {b : ℝ} (hb : 0 ≤ b) : 0 ≤ sensitivity b := by
  exact div_nonneg (mul_nonneg (by norm_num) (by linarith [Real.one_le_exp hb]))
    (by positivity)

theorem sensitivity_le_two (b : ℝ) : sensitivity b ≤ 2 := by
  unfold sensitivity
  apply (div_le_iff₀ (by positivity : 0 < Real.exp b + 1)).mpr
  linarith

@[simp] theorem sensitivity_zero : sensitivity 0 = 0 := by simp [sensitivity]

/-- Master sensitivity statement. Bandwidths may differ: only the scaled distances enter. -/
theorem expRow_l1_le_scaled (s : Finset ι) (hs : s.Nonempty) (d dh : ι → ℝ)
    {h hh b : ℝ} (hb : 0 ≤ b)
    (hscaled : ∀ j ∈ s, |dh j / hh - d j / h| ≤ b) :
    ∑ j ∈ s, |expRow s dh hh j - expRow s d h j| ≤ sensitivity b := by
  have hratio : ∀ a c : ℝ, |c - a| ≤ b → Real.exp (-c) ≤ Real.exp b * Real.exp (-a) := by
    intro a c hac
    rw [← Real.exp_add, Real.exp_le_exp]
    linarith [(abs_le.mp hac).1]
  simpa only [expRow, neg_div, sensitivity] using
    normalized_l1_le_sharp s (fun j => Real.exp (-d j / h))
      (fun j => Real.exp (-dh j / hh)) (Real.one_le_exp hb) hs
      (fun _ _ => Real.exp_pos _)
      (fun j hj => by
        simpa only [neg_div] using
          hratio (dh j / hh) (d j / h) (by rw [abs_sub_comm]; exact hscaled j hj))
      (fun j hj => by
        simpa only [neg_div] using hratio (d j / h) (dh j / hh) (hscaled j hj))

/-- Sharp common-bandwidth sensitivity; no nonzero-distance assumption is needed. -/
theorem expRow_l1_le_sharp (s : Finset ι) (hs : s.Nonempty) (d dh : ι → ℝ)
    {h δ : ℝ} (hh : 0 < h) (hδ : ∀ j ∈ s, |dh j - d j| ≤ δ) :
    ∑ j ∈ s, |expRow s dh h j - expRow s d h j| ≤ sensitivity (δ / h) := by
  obtain ⟨j, hj⟩ := hs
  have hδ0 : 0 ≤ δ := (abs_nonneg _).trans (hδ j hj)
  apply expRow_l1_le_scaled s ⟨j, hj⟩ d dh (div_nonneg hδ0 hh.le)
  intro k hk
  rw [← sub_div, abs_div, abs_of_pos hh]
  exact div_le_div_of_nonneg_right (hδ k hk) hh.le

/-- Different-bandwidth scaled-distance error. The distance bound is for the reference row. -/
theorem scaled_distance_error {d dh h hh hmin δ D : ℝ}
    (hminpos : 0 < hmin) (hhmin : hmin ≤ h) (hhhmin : hmin ≤ hh)
    (hd : |d| ≤ D) (hδ : |dh - d| ≤ δ) :
    |dh / hh - d / h| ≤ δ / hmin + D * |hh - h| / hmin ^ 2 := by
  have hhpos : 0 < h := lt_of_lt_of_le hminpos hhmin
  have hhhpos : 0 < hh := lt_of_lt_of_le hminpos hhhmin
  have hD : 0 ≤ D := (abs_nonneg _).trans hd
  have hδ0 : 0 ≤ δ := (abs_nonneg _).trans hδ
  have hsplit : dh / hh - d / h = (dh - d) / hh + d * (h - hh) / (hh * h) := by
    field_simp
    ring
  have hprod : hmin ^ 2 ≤ hh * h := by nlinarith [mul_le_mul hhhmin hhmin hminpos.le hhhpos.le]
  calc |dh / hh - d / h| = |(dh - d) / hh + d * (h - hh) / (hh * h)| := by rw [hsplit]
    _ ≤ |(dh - d) / hh| + |d * (h - hh) / (hh * h)| := abs_add_le _ _
    _ = |dh - d| / hh + |d| * |hh - h| / (hh * h) := by
      rw [abs_div, abs_div, abs_of_pos hhhpos, abs_of_pos (mul_pos hhhpos hhpos),
        abs_mul, abs_sub_comm h hh]
    _ ≤ δ / hmin + D * |hh - h| / hmin ^ 2 := by
      apply add_le_add
      · exact div_le_div₀ hδ0 hδ hminpos hhhmin
      · exact div_le_div₀ (mul_nonneg hD (abs_nonneg _))
          (mul_le_mul_of_nonneg_right hd (abs_nonneg _)) (sq_pos_of_pos hminpos) hprod

/-- Varying-bandwidth row sensitivity, retaining the bandwidth-estimation term. -/
theorem expRow_l1_le_bandwidth (s : Finset ι) (hs : s.Nonempty) (d dh : ι → ℝ)
    {h hh hmin δ D : ℝ} (hminpos : 0 < hmin) (hhmin : hmin ≤ h) (hhhmin : hmin ≤ hh)
    (hd : ∀ j ∈ s, |d j| ≤ D) (hδ : ∀ j ∈ s, |dh j - d j| ≤ δ) :
    ∑ j ∈ s, |expRow s dh hh j - expRow s d h j| ≤
      sensitivity (δ / hmin + D * |hh - h| / hmin ^ 2) := by
  obtain ⟨j, hj⟩ := hs
  have hD : 0 ≤ D := (abs_nonneg _).trans (hd j hj)
  have hδ0 : 0 ≤ δ := (abs_nonneg _).trans (hδ j hj)
  apply expRow_l1_le_scaled s ⟨j, hj⟩ d dh (by positivity)
  exact fun k hk => scaled_distance_error hminpos hhmin hhhmin (hd k hk) (hδ k hk)

/-- Positive exponential rows sum to one on a nonempty support. -/
theorem expRow_sum (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) :
    ∑ j ∈ s, expRow s d h j = 1 := by
  simp only [expRow, ← sum_div]
  exact div_self (ne_of_gt (sum_pos (fun _ _ => Real.exp_pos _) hs))

theorem expRow_pos (s : Finset ι) (hs : s.Nonempty) (d : ι → ℝ) (h : ℝ) (j : ι) :
    0 < expRow s d h j :=
  div_pos (Real.exp_pos _) (sum_pos (fun _ _ => Real.exp_pos _) hs)

@[simp] theorem expRow_singleton (i : ι) (d : ι → ℝ) (h : ℝ) :
    expRow {i} d h i = 1 := by simp [expRow]

/-! ## The whole network in the `ℓ∞` operator norm -/

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- The exponential kernel network with zero diagonal. -/
noncomputable def expKernel (d : Matrix n n ℝ) (h : ℝ) : Matrix n n ℝ :=
  Matrix.of fun i j => if i = j then 0 else expRow (univ.erase i) (d i) h j

attribute [local instance] Matrix.linftyOpSeminormedAddCommGroup in
/-- **Network sensitivity.** With at least two firms, if every off-diagonal distance moves
by at most `δ`, then `‖Ŵ − W‖_∞ ≤ min(2, e^{2δ/h} − 1)`. -/
theorem expKernel_linfty_le (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ) {h δ : ℝ}
    (hh : 0 < h) (hδ : ∀ i j, i ≠ j → |dh i j - d i j| ≤ δ) :
    ‖expKernel dh h - expKernel d h‖ ≤ min 2 (Real.exp (2 * δ / h) - 1) := by
  have hrow : ∀ i, ∑ j, |(expKernel dh h - expKernel d h) i j| ≤
      min 2 (Real.exp (2 * δ / h) - 1) := by
    intro i
    have hne : (univ.erase i).Nonempty := by
      rw [← card_pos, card_erase_of_mem (mem_univ i), card_univ]
      omega
    rw [← sum_erase_add _ _ (mem_univ i)]
    simp only [expKernel, Matrix.sub_apply, Matrix.of_apply, if_true, sub_self, abs_zero,
      add_zero]
    rw [sum_congr rfl fun j hj => by rw [if_neg (ne_of_mem_erase hj).symm,
      if_neg (ne_of_mem_erase hj).symm]]
    exact expRow_l1_le _ hne (d i) (dh i) hh fun j hj => hδ i j (ne_of_mem_erase hj).symm
  have : Nonempty n := Fintype.card_pos_iff.mp (by omega)
  have h0 : 0 ≤ min 2 (Real.exp (2 * δ / h) - 1) :=
    (sum_nonneg fun _ _ => abs_nonneg _).trans (hrow (Classical.arbitrary n))
  rw [Matrix.linfty_opNorm_def]
  have : (univ.sup fun i => ∑ j, ‖(expKernel dh h - expKernel d h) i j‖₊) ≤
      ⟨min 2 (Real.exp (2 * δ / h) - 1), h0⟩ :=
    Finset.sup_le fun i _ => by
      rw [← NNReal.coe_le_coe]
      push_cast
      simp only [Real.norm_eq_abs]
      exact hrow i
  exact NNReal.coe_le_coe.mpr this

/-- Sharp row-sum bound without an implicit matrix norm instance. -/
theorem expKernel_row_l1_le_scaled (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ)
    {h hh b : ℝ} (hb : 0 ≤ b)
    (hscaled : ∀ i j, i ≠ j → |dh i j / hh - d i j / h| ≤ b) (i : n) :
    ∑ j, |(expKernel dh hh - expKernel d h) i j| ≤ sensitivity b := by
  have hne : (univ.erase i).Nonempty := by
    rw [← card_pos, card_erase_of_mem (mem_univ i), card_univ]
    omega
  rw [← sum_erase_add _ _ (mem_univ i)]
  simp only [expKernel, Matrix.sub_apply, Matrix.of_apply, if_true, sub_self, abs_zero,
    add_zero]
  rw [sum_congr rfl fun j hj => by rw [if_neg (ne_of_mem_erase hj).symm,
    if_neg (ne_of_mem_erase hj).symm]]
  exact expRow_l1_le_scaled _ hne (d i) (dh i) hb
    fun j hj => hscaled i j (ne_of_mem_erase hj).symm

/-- Sharp common-bandwidth row-sum bound. -/
theorem expKernel_row_l1_le_sharp (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ)
    {h δ : ℝ} (hh : 0 < h) (hδ0 : 0 ≤ δ)
    (hδ : ∀ i j, i ≠ j → |dh i j - d i j| ≤ δ) (i : n) :
    ∑ j, |(expKernel dh h - expKernel d h) i j| ≤ sensitivity (δ / h) := by
  apply expKernel_row_l1_le_scaled hn d dh (div_nonneg hδ0 hh.le)
  intro k j hkj
  rw [← sub_div, abs_div, abs_of_pos hh]
  exact div_le_div_of_nonneg_right (hδ k j hkj) hh.le

/-- Every entry of the zero-diagonal exponential network is nonnegative. -/
theorem expKernel_nonneg (d : Matrix n n ℝ) (h : ℝ) (i j : n) :
    0 ≤ expKernel d h i j := by
  simp only [expKernel, Matrix.of_apply]
  split_ifs
  · exact le_rfl
  · exact div_nonneg (Real.exp_pos _).le (sum_nonneg fun _ _ => (Real.exp_pos _).le)

/-- The zero-diagonal exponential network is row stochastic for at least two firms. -/
theorem expKernel_row_sum (hn : 2 ≤ Fintype.card n) (d : Matrix n n ℝ) (h : ℝ) (i : n) :
    ∑ j, expKernel d h i j = 1 := by
  have hne : (univ.erase i).Nonempty := by
    rw [← card_pos, card_erase_of_mem (mem_univ i), card_univ]
    omega
  rw [← sum_erase_add _ _ (mem_univ i)]
  simp only [expKernel, Matrix.of_apply, if_true, add_zero]
  rw [sum_congr rfl fun j hj => by rw [if_neg (ne_of_mem_erase hj).symm]]
  exact expRow_sum _ hne _ _

attribute [local instance] Matrix.linftyOpSeminormedAddCommGroup in
/-- Sharp sensitivity in the row-sum matrix norm; the row theorem is instance independent. -/
theorem expKernel_linfty_le_sharp (hn : 2 ≤ Fintype.card n) (d dh : Matrix n n ℝ)
    {h δ : ℝ} (hh : 0 < h) (hδ0 : 0 ≤ δ)
    (hδ : ∀ i j, i ≠ j → |dh i j - d i j| ≤ δ) :
    ‖expKernel dh h - expKernel d h‖ ≤ sensitivity (δ / h) := by
  rw [Matrix.linfty_opNorm_def]
  have hb := sensitivity_nonneg (div_nonneg hδ0 hh.le)
  have : (univ.sup fun i => ∑ j, ‖(expKernel dh h - expKernel d h) i j‖₊) ≤
      ⟨sensitivity (δ / h), hb⟩ := Finset.sup_le fun i _ => by
    rw [← NNReal.coe_le_coe]
    push_cast
    simp only [Real.norm_eq_abs]
    exact expKernel_row_l1_le_sharp hn d dh hh hδ0 hδ i
  exact NNReal.coe_le_coe.mpr this

/-- Two coordinates attain the sharp normalized-weight constant. -/
theorem normalized_two_sharp {r : ℝ} (hr : 1 ≤ r) :
    ∑ j : Fin 2,
      |(![1, r] j : ℝ) / (1 + r) - (![r, 1] j : ℝ) / (r + 1)| =
        2 * (r - 1) / (r + 1) := by
  have hp : 0 < r + 1 := by linarith
  have heq : 1 + r = r + 1 := by ring
  simp only [Fin.sum_univ_two, Matrix.cons_val_zero, Matrix.cons_val_one, heq]
  have hle : 1 / (r + 1) ≤ r / (r + 1) := div_le_div_of_nonneg_right hr hp.le
  rw [abs_of_nonpos (by linarith : 1 / (r + 1) - r / (r + 1) ≤ 0),
    abs_of_nonneg (by linarith : 0 ≤ r / (r + 1) - 1 / (r + 1))]
  ring

end FreeFoundations.Kernel
