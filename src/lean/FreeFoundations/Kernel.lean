import Mathlib.Analysis.Matrix.Normed
import Mathlib.Analysis.SpecialFunctions.Exp

/-!
# Kernel sensitivity

The networks are row-normalised exponential kernels on the other firms,
`Wᵢⱼ = exp(−dᵢⱼ/h) / Σₖ≠ᵢ exp(−dᵢₖ/h)`. Two facts govern how distance error reaches the
network:

* only `d/h` matters, so a distance scale and a bandwidth are never separately
  interpretable;
* if every distance in a row moves by at most `δ`, the row moves in `ℓ₁` by at most
  `min(2, e^{2δ/h} − 1)`. Narrow bandwidths amplify distance error.

The second is uniform in `δ`: an average distance guarantee does not give it. Row bounds here
are in `ℓ₁`, whose maximum between probability vectors is 2. Total variation in the usual
probability convention is half of it, `min(1, (e^{2δ/h} − 1)/2)`; the Python geometry
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

end FreeFoundations.Kernel
