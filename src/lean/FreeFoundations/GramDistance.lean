module

public import FreeFoundations.Recovery
public import FreeFoundations.MatrixBounds
public import Mathlib.Analysis.Matrix.PosDef
public import Mathlib.Algebra.Order.Star.Real
public import FreeFoundations.Stability

@[expose] public section

/-! Distances of an anchored Gram matrix and finite-panel error certificates. -/

namespace FreeFoundations.GramDistance

open Matrix Finset

variable {n : Type*} [Fintype n] [DecidableEq n]

/-- Squared distance defined without a symmetry assumption. -/
def squared (G : Matrix n n ℝ) (i j : n) : ℝ := G i i + G j j - G i j - G j i

noncomputable def distance (G : Matrix n n ℝ) (i j : n) : ℝ := Real.sqrt (squared G i j)

theorem squared_eq_quadratic (G : Matrix n n ℝ) (i j : n) :
    squared G i j = (Pi.single i 1 - Pi.single j 1) ⬝ᵥ
      (G *ᵥ (Pi.single i 1 - Pi.single j 1)) := by
  simp [squared, Matrix.mulVec_sub, dotProduct_sub, sub_dotProduct]
  ring

theorem squared_nonneg {G : Matrix n n ℝ} (hG : G.PosSemidef) (i j : n) :
    0 ≤ squared G i j := by
  rw [squared_eq_quadratic]
  simpa only [star_trivial] using hG.dotProduct_mulVec_nonneg (Pi.single i 1 - Pi.single j 1)

omit [Fintype n] [DecidableEq n] in
theorem squared_eq_entry {G : Matrix n n ℝ} (hG : G.IsHermitian) (i j : n) :
    squared G i j = G i i + G j j - 2 * G i j := by
  have h : G j i = G i j := by simpa using congrFun (congrFun hG.eq i) j
  simp only [squared, h]
  ring

omit [Fintype n] [DecidableEq n] in
theorem squared_error (G Gh : Matrix n n ℝ) {ε : ℝ}
    (h : ∀ i j, |Gh i j - G i j| ≤ ε) (i j : n) :
    |squared Gh i j - squared G i j| ≤ 4 * ε := by
  have h1 := abs_le.mp (h i i)
  have h2 := abs_le.mp (h j j)
  have h3 := abs_le.mp (h i j)
  have h4 := abs_le.mp (h j i)
  rw [abs_le]
  simp only [squared]
  constructor <;> linarith

/-- Square-root continuity at zero; no positive separation of firms is assumed. -/
theorem sqrt_error {x y ε : ℝ} (hx : 0 ≤ x) (hy : 0 ≤ y) (hε : 0 ≤ ε)
    (h : |x - y| ≤ ε) : |Real.sqrt x - Real.sqrt y| ≤ Real.sqrt ε := by
  have hsx := Real.sq_sqrt hx
  have hsy := Real.sq_sqrt hy
  have hse := Real.sq_sqrt hε
  have hp := mul_nonneg (Real.sqrt_nonneg x) (Real.sqrt_nonneg y)
  have hxy := abs_le.mp h
  rw [abs_le]
  constructor
  · by_cases horder : Real.sqrt x ≤ Real.sqrt y
    · have hdiff : 0 ≤ Real.sqrt y - Real.sqrt x := sub_nonneg.mpr horder
      have hsmall : (Real.sqrt y - Real.sqrt x) ^ 2 ≤ ε := by nlinarith
      have := (sq_le_sq₀ hdiff (Real.sqrt_nonneg ε)).mp (by simpa [hse] using hsmall)
      linarith
    · linarith [Real.sqrt_nonneg ε]
  · by_cases horder : Real.sqrt y ≤ Real.sqrt x
    · have hdiff : 0 ≤ Real.sqrt x - Real.sqrt y := sub_nonneg.mpr horder
      have hsmall : (Real.sqrt x - Real.sqrt y) ^ 2 ≤ ε := by nlinarith
      exact (sq_le_sq₀ hdiff (Real.sqrt_nonneg ε)).mp (by simpa [hse] using hsmall)
    · linarith [Real.sqrt_nonneg ε]

theorem distance_error {G Gh : Matrix n n ℝ} (hG : G.PosSemidef) (hGh : Gh.PosSemidef)
    {ε : ℝ} (hε : 0 ≤ ε) (h : ∀ i j, |Gh i j - G i j| ≤ ε) (i j : n) :
    |distance Gh i j - distance G i j| ≤ 2 * Real.sqrt ε := by
  have hb := sqrt_error (squared_nonneg hGh i j) (squared_nonneg hG i j)
    (by positivity : 0 ≤ 4 * ε) (squared_error G Gh h i j)
  have hs : Real.sqrt (4 * ε) = 2 * Real.sqrt ε := by
    rw [Real.sqrt_mul (by norm_num : (0 : ℝ) ≤ 4)]
    rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.sqrt_sq (by norm_num : (0 : ℝ) ≤ 2)]
  simpa only [distance, hs] using hb

omit [Fintype n] [DecidableEq n] in
@[simp]
theorem squared_self (G : Matrix n n ℝ) (i : n) : squared G i i = 0 := by simp [squared]

omit [Fintype n] [DecidableEq n] in
@[simp]
theorem distance_self (G : Matrix n n ℝ) (i : n) : distance G i i = 0 := by simp [distance]

omit [Fintype n] [DecidableEq n] in
@[simp]
theorem distance_zero (i j : n) : distance (0 : Matrix n n ℝ) i j = 0 := by simp [distance, squared]

/-- The difference of coordinate unit vectors has squared Euclidean norm at most two,
including the coincident-index case. -/
theorem coordinate_difference_sq_le (i j : n) :
    ‖EuclideanSpace.single i (1 : ℝ) - EuclideanSpace.single j 1‖ ^ 2 ≤ 2 := by
  rw [norm_sub_sq_real]
  simp only [EuclideanSpace.single, PiLp.norm_single, norm_one, one_pow, EuclideanSpace.inner_single_left,
    map_one, one_mul, PiLp.single_apply]
  split_ifs <;> norm_num

open scoped Matrix.Norms.L2Operator in
/-- The spectral Gram-error convention yields constant two, rather than the entrywise
constant four. Positive semidefiniteness is unnecessary for this algebraic bound. -/
theorem squared_error_spectral (G Gh : Matrix n n ℝ) {ε : ℝ} (hε : 0 ≤ ε)
    (herror : MatrixBounds.spectralNorm (Gh - G) ≤ ε) (i j : n) :
    |squared Gh i j - squared G i j| ≤ 2 * ε := by
  let v : EuclideanSpace ℝ n := EuclideanSpace.single i 1 - EuclideanSpace.single j 1
  have hquad : squared Gh i j - squared G i j =
      inner ℝ (Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) (Gh - G) v) v := by
    have hs : squared Gh i j - squared G i j = squared (Gh - G) i j := by
      simp only [squared, Matrix.sub_apply]
      ring
    rw [hs, squared_eq_quadratic]
    simp only [PiLp.inner_apply, Matrix.ofLp_toEuclideanCLM, RCLike.inner_apply,
      conj_trivial, v, WithLp.ofLp_sub, EuclideanSpace.single, PiLp.ofLp_single, dotProduct]
  rw [hquad]
  calc _ ≤ ‖Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) (Gh - G)‖ * ‖v‖ ^ 2 :=
      Stability.abs_quadratic_le _ _
    _ ≤ ε * 2 := by
      rw [Matrix.l2_opNorm_toEuclideanCLM]
      exact mul_le_mul herror (coordinate_difference_sq_le i j) (sq_nonneg _) hε
    _ = _ := by ring

/-- Spectral Gram error to distances, valid even for zero target distances. -/
theorem distance_error_spectral {G Gh : Matrix n n ℝ} (hG : G.PosSemidef) (hGh : Gh.PosSemidef)
    {ε : ℝ} (hε : 0 ≤ ε) (herror : MatrixBounds.spectralNorm (Gh - G) ≤ ε) (i j : n) :
    |distance Gh i j - distance G i j| ≤ Real.sqrt (2 * ε) :=
  sqrt_error (squared_nonneg hGh i j) (squared_nonneg hG i j) (by positivity)
    (squared_error_spectral G Gh hε herror i j)

/-- A PSD two-point Gram matrix attaining the entrywise constants. -/
noncomputable def sharpGram (ε : ℝ) : Matrix (Fin 2) (Fin 2) ℝ :=
  ε • vecMulVec ![(1 : ℝ), -1] ![(1 : ℝ), -1]

theorem sharpGram_posSemidef {ε : ℝ} (hε : 0 ≤ ε) : (sharpGram ε).PosSemidef := by
  have hp := posSemidef_vecMulVec_self_star (![(1 : ℝ), -1] : Fin 2 → ℝ)
  simpa only [sharpGram, star_trivial] using hp.smul hε

theorem sharpGram_entry_bound {ε : ℝ} (hε : 0 ≤ ε) (i j : Fin 2) :
    |sharpGram ε i j - (0 : Matrix (Fin 2) (Fin 2) ℝ) i j| = ε := by
  fin_cases i <;> fin_cases j <;> simp [sharpGram, vecMulVec, abs_of_nonneg hε]

theorem sharpGram_squared (ε : ℝ) : squared (sharpGram ε) 0 1 = 4 * ε := by
  simp [squared, sharpGram, vecMulVec]
  ring

theorem sharpGram_distance {ε : ℝ} (_hε : 0 ≤ ε) : distance (sharpGram ε) 0 1 = 2 * Real.sqrt ε := by
  rw [distance, sharpGram_squared, Real.sqrt_mul (by norm_num : (0 : ℝ) ≤ 4)]
  rw [show (4 : ℝ) = 2 ^ 2 by norm_num, Real.sqrt_sq (by norm_num : (0 : ℝ) ≤ 2)]

variable {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]

omit [Fintype n] [DecidableEq n] [InnerProductSpace ℝ A] in
theorem uniform_exposure_distance (a ah : n → A) {e : ℝ}
    (h : ∀ i, ‖ah i - a i‖ ≤ e) (i j : n) :
    |‖ah i - ah j‖ - ‖a i - a j‖| ≤ 2 * e := by
  exact (Recovery.distance_error (ah i) (a i) (ah j) (a j)).trans (by linarith [h i, h j])

omit [DecidableEq n] in
/-- A certificate about the actual finite panel, with its dimension factor retained. -/
theorem empirical_rms_to_uniform (e : n → ℝ) {B : ℝ} (hB : 0 ≤ B)
    (h : ∑ i, (e i) ^ 2 ≤ Fintype.card n * B ^ 2) (i : n) :
    |e i| ≤ Real.sqrt (Fintype.card n) * B := by
  have hi : (e i) ^ 2 ≤ ∑ j, (e j) ^ 2 := single_le_sum (fun _ _ => sq_nonneg _) (mem_univ i)
  have hs := Real.sq_sqrt (Nat.cast_nonneg (Fintype.card n) : (0 : ℝ) ≤ Fintype.card n)
  apply (sq_le_sq₀ (abs_nonneg _) (mul_nonneg (Real.sqrt_nonneg _) hB)).mp
  rw [sq_abs, mul_pow, hs]
  exact hi.trans h

end FreeFoundations.GramDistance
