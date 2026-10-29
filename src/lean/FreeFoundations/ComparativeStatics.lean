module

public import FreeFoundations.Network
public import FreeFoundations.ReversibleNetwork
public import Mathlib.Analysis.Matrix.Order

@[expose] public section

/-!
# Limits of spatial-risk comparative statics

A two-firm network amplifies the common direction while reducing the spread direction.
Thus increasing a positive spatial coefficient need not increase covariance in Loewner order.
-/

namespace FreeFoundations.ComparativeStatics

open Matrix

noncomputable def swapNetwork : Matrix (Fin 2) (Fin 2) ℝ := !![0, 1; 1, 0]

noncomputable def swapCovariance (c : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  (1 - c • swapNetwork)⁻¹ * ((1 - c • swapNetwork)⁻¹)ᵀ

def commonDirection : Fin 2 → ℝ := ![1, 1]

def spreadDirection : Fin 2 → ℝ := ![1, -1]

/-- The swapping network meets the sufficient inverse condition without an inverse premise. -/
theorem swap_spatial_isUnit {c : ℝ} (hc : |c| < 1) : IsUnit (1 - c • swapNetwork) := by
  apply ReversibleNetwork.spatial_isUnit swapNetwork (fun _ => 1)
  · intro i j
    fin_cases i <;> fin_cases j <;> norm_num [swapNetwork]
  · intro i
    fin_cases i <;> norm_num [swapNetwork, Fin.sum_univ_two]
  · exact fun _ => zero_lt_one
  · intro j
    fin_cases j <;> norm_num [swapNetwork, Fin.sum_univ_two]
  · exact hc

theorem swap_symmetric : swapNetworkᵀ = swapNetwork := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [swapNetwork]

/-- The spatial inverse acts on the common direction with gain `(1−λ)⁻¹`. -/
theorem swap_inverse_common {c : ℝ} (hc : |c| < 1) :
    (1 - c • swapNetwork)⁻¹ *ᵥ commonDirection = (1 - c)⁻¹ • commonDirection := by
  apply Network.inverse_on_eigenvector swapNetwork c (1 - c) commonDirection
    ((Matrix.isUnit_iff_isUnit_det _).mp (swap_spatial_isUnit hc))
  · have := (abs_lt.mp hc).2
    linarith
  · ext i
    fin_cases i <;> simp [swapNetwork, commonDirection, Matrix.mulVec, dotProduct, Fin.sum_univ_two] <;> ring

theorem swap_inverse_spread {c : ℝ} (hc : |c| < 1) :
    (1 - c • swapNetwork)⁻¹ *ᵥ spreadDirection = (1 + c)⁻¹ • spreadDirection := by
  apply Network.inverse_on_eigenvector swapNetwork c (1 + c) spreadDirection
    ((Matrix.isUnit_iff_isUnit_det _).mp (swap_spatial_isUnit hc))
  · have := (abs_lt.mp hc).1
    linarith
  · ext i
    fin_cases i <;> simp [swapNetwork, spreadDirection, Matrix.mulVec, dotProduct, Fin.sum_univ_two]

/-- The common-direction covariance eigenvalue is `(1−λ)⁻²`. -/
theorem swap_covariance_common {c : ℝ} (hc : |c| < 1) :
    swapCovariance c *ᵥ commonDirection = (1 - c)⁻¹ ^ 2 • commonDirection := by
  have hsym : ((1 - c • swapNetwork)⁻¹)ᵀ = (1 - c • swapNetwork)⁻¹ := by
    rw [Matrix.transpose_nonsing_inv, transpose_sub, transpose_one, transpose_smul, swap_symmetric]
  rw [swapCovariance, ← mulVec_mulVec, hsym, swap_inverse_common hc, mulVec_smul,
    swap_inverse_common hc, smul_smul, sq]

/-- The spread-direction covariance eigenvalue is `(1+λ)⁻²`. -/
theorem swap_covariance_spread {c : ℝ} (hc : |c| < 1) :
    swapCovariance c *ᵥ spreadDirection = (1 + c)⁻¹ ^ 2 • spreadDirection := by
  have hsym : ((1 - c • swapNetwork)⁻¹)ᵀ = (1 - c • swapNetwork)⁻¹ := by
    rw [Matrix.transpose_nonsing_inv, transpose_sub, transpose_one, transpose_smul, swap_symmetric]
  rw [swapCovariance, ← mulVec_mulVec, hsym, swap_inverse_spread hc, mulVec_smul,
    swap_inverse_spread hc, smul_smul, sq]

/-- A positive spatial coefficient reduces risk in the spread direction. -/
theorem swap_spread_variance_lt_one {c : ℝ} (hc : 0 < c) : (1 + c)⁻¹ ^ 2 < 1 := by
  have hden : 1 < 1 + c := by linarith
  have hi : (1 + c)⁻¹ < 1 := inv_lt_one_of_one_lt₀ hden
  have hp : 0 < (1 + c)⁻¹ := inv_pos.mpr (by linarith)
  nlinarith

/-- Increasing persistence from zero need not increase covariance in Loewner order. -/
theorem swap_covariance_not_ge_identity {c : ℝ} (hc : 0 < c) (hc1 : c < 1) :
    ¬ (swapCovariance c - 1).PosSemidef := by
  intro hPSD
  have habs : |c| < 1 := by rw [abs_of_pos hc]; exact hc1
  have hquad := hPSD.dotProduct_mulVec_nonneg spreadDirection
  rw [sub_mulVec, one_mulVec, swap_covariance_spread habs] at hquad
  simp [spreadDirection, dotProduct, Fin.sum_univ_two] at hquad
  have hi := swap_spread_variance_lt_one hc
  rw [inv_pow] at hi
  linarith

/-- The common direction instead becomes riskier for `0<λ<1`. -/
theorem swap_common_variance_gt_one {c : ℝ} (hc : 0 < c) (hc1 : c < 1) :
    1 < (1 - c)⁻¹ ^ 2 := by
  have hp : 0 < 1 - c := by linarith
  have hi : 1 < (1 - c)⁻¹ := one_lt_inv₀ hp |>.mpr (by linarith)
  nlinarith

end FreeFoundations.ComparativeStatics
