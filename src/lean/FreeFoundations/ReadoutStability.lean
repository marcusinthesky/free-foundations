import FreeFoundations.ScoreStability

/-!
# Fixed-feature ridge readouts

Every coordinate is regularized by the same fixed positive coefficient. The support
replacement result concerns fixed features and bounded targets; it is not a stability
claim for feature extraction, preprocessing, tuning or an unregularized intercept.
-/

namespace FreeFoundations.ReadoutStability

open Matrix Finset
open scoped Matrix.Norms.L2Operator

variable {d ι : Type*} [Fintype d] [DecidableEq d] [Fintype ι]

noncomputable def outer (x : EuclideanSpace ℝ d) : Matrix d d ℝ := vecMulVec x.ofLp x.ofLp

omit [DecidableEq d] in
theorem outer_posSemidef (x : EuclideanSpace ℝ d) : (outer x).PosSemidef := by
  simpa only [outer, star_trivial] using posSemidef_vecMulVec_self_star x.ofLp

theorem outer_toCLM (x : EuclideanSpace ℝ d) :
    Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (outer x) = InnerProductSpace.rankOne ℝ x x := by
  ext v j
  simp only [Matrix.ofLp_toEuclideanCLM, outer, vecMulVec_mulVec,
    InnerProductSpace.rankOne_apply, PiLp.inner_apply, RCLike.inner_apply, conj_trivial,
    dotProduct, WithLp.ofLp_smul]
  simp [mul_comm]

theorem norm_outer (x : EuclideanSpace ℝ d) : ‖outer x‖ = ‖x‖ ^ 2 := by
  rw [← Matrix.l2_opNorm_toEuclideanCLM, outer_toCLM, InnerProductSpace.norm_rankOne, pow_two]

noncomputable def gram (x : ι → EuclideanSpace ℝ d) (μ : ℝ) : Matrix d d ℝ :=
  μ • 1 + (Fintype.card ι : ℝ)⁻¹ • ∑ i, outer (x i)

noncomputable def crossMoment (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) : EuclideanSpace ℝ d :=
  (Fintype.card ι : ℝ)⁻¹ • ∑ i, y i • x i

noncomputable def ridge (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) (μ : ℝ) : EuclideanSpace ℝ d :=
  Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)⁻¹ (crossMoment x y)

theorem gram_floor (x : ι → EuclideanSpace ℝ d) (μ : ℝ) :
    (gram x μ - μ • 1).PosSemidef := by
  have hs : (∑ i, outer (x i)).PosSemidef := by
    simpa using posSemidef_sum (univ : Finset ι) fun i _ => outer_posSemidef (x i)
  simpa only [gram, add_sub_cancel_left] using hs.smul (a := (Fintype.card ι : ℝ)⁻¹) (by positivity)

theorem gram_posDef (x : ι → EuclideanSpace ℝ d) {μ : ℝ} (hμ : 0 < μ) : (gram x μ).PosDef := by
  have hs := gram_floor x μ
  have hpos : (μ • (1 : Matrix d d ℝ)).PosDef := PosDef.one.smul hμ
  have ht := hpos.add_posSemidef hs
  simpa only [gram, add_sub_cancel_left] using ht

theorem normal_equation (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {μ : ℝ} (hμ : 0 < μ) :
    Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) (ridge x y μ) = crossMoment x y := by
  have hinv := mul_nonsing_inv (gram x μ) (isUnit_iff_ne_zero.mpr (gram_posDef x hμ).det_pos.ne')
  have ht := congrArg (fun A : Matrix d d ℝ => Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A (crossMoment x y)) hinv
  simpa only [map_mul, map_one, mul_apply_eq_comp, one_apply_eq_self, ridge] using ht

theorem inverse_gram_norm_le (x : ι → EuclideanSpace ℝ d) {μ : ℝ} (hμ : 0 < μ) :
    ‖(gram x μ)⁻¹‖ ≤ μ⁻¹ :=
  ScoreStability.norm_inverse_le_of_floor (gram_posDef x hμ) hμ (gram_floor x μ)

/-- The objective whose every coordinate receives positive ridge regularization. -/
noncomputable def objective (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) (μ : ℝ)
    (w : EuclideanSpace ℝ d) : ℝ :=
  (Fintype.card ι : ℝ)⁻¹ * ∑ i, (inner ℝ (x i) w - y i) ^ 2 + μ * ‖w‖ ^ 2

theorem gram_apply (x : ι → EuclideanSpace ℝ d) (μ : ℝ) (w : EuclideanSpace ℝ d) :
    Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) w =
      μ • w + (Fintype.card ι : ℝ)⁻¹ • ∑ i, inner ℝ (x i) w • x i := by
  simp only [gram, map_add, map_smul, map_sum, map_one, outer_toCLM,
    _root_.add_apply, _root_.smul_apply, _root_.sum_apply,
    one_apply_eq_self, InnerProductSpace.rankOne_apply]

theorem gram_quadratic (x : ι → EuclideanSpace ℝ d) (μ : ℝ) (w : EuclideanSpace ℝ d) :
    inner ℝ (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) w) w =
      μ * ‖w‖ ^ 2 + (Fintype.card ι : ℝ)⁻¹ * ∑ i, (inner ℝ (x i) w) ^ 2 := by
  rw [gram_apply, inner_add_left, real_inner_smul_left, real_inner_self_eq_norm_sq,
    real_inner_smul_left, sum_inner]
  simp only [real_inner_smul_left, pow_two]

theorem gram_inner_symmetric (x : ι → EuclideanSpace ℝ d) (μ : ℝ)
    (v w : EuclideanSpace ℝ d) :
    inner ℝ (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) v) w =
      inner ℝ v (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) w) := by
  simp only [gram_apply, inner_add_left, inner_add_right, real_inner_smul_left,
    real_inner_smul_right, sum_inner, inner_sum]
  congr 1
  congr 1
  exact sum_congr rfl fun i _ => by rw [real_inner_comm v (x i)]; ring

theorem objective_quadratic (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) (μ : ℝ)
    (w : EuclideanSpace ℝ d) :
    objective x y μ w =
      inner ℝ (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) w) w -
        2 * inner ℝ (crossMoment x y) w + (Fintype.card ι : ℝ)⁻¹ * ∑ i, y i ^ 2 := by
  rw [gram_quadratic]
  simp only [crossMoment, real_inner_smul_left, sum_inner]
  have hs : ∑ i, (inner ℝ (x i) w - y i) ^ 2 =
      ∑ i, (inner ℝ (x i) w) ^ 2 - 2 * ∑ i, y i * inner ℝ (x i) w + ∑ i, y i ^ 2 := by
    rw [mul_sum, ← sum_sub_distrib, ← sum_add_distrib]
    exact sum_congr rfl fun i _ => by ring
  rw [objective, hs]
  ring

/-- The normal-equation solution minimizes the declared regularized objective. -/
theorem objective_gap (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {μ : ℝ} (hμ : 0 < μ)
    (w : EuclideanSpace ℝ d) :
    objective x y μ w - objective x y μ (ridge x y μ) =
      μ * ‖w - ridge x y μ‖ ^ 2 + (Fintype.card ι : ℝ)⁻¹ *
        ∑ i, (inner ℝ (x i) (w - ridge x y μ)) ^ 2 := by
  rw [← gram_quadratic, objective_quadratic, objective_quadratic]
  have hn := normal_equation x y hμ
  have hcross : inner ℝ (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ) w) (ridge x y μ) =
      inner ℝ (crossMoment x y) w := by
    rw [gram_inner_symmetric, hn, real_inner_comm]
  simp only [map_sub, inner_sub_left, inner_sub_right]
  rw [hn, hcross]
  ring

theorem objective_minimal (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {μ : ℝ} (hμ : 0 < μ)
    (w : EuclideanSpace ℝ d) : objective x y μ (ridge x y μ) ≤ objective x y μ w := by
  have hgap := objective_gap x y hμ w
  have hnonneg : 0 ≤ μ * ‖w - ridge x y μ‖ ^ 2 + (Fintype.card ι : ℝ)⁻¹ *
      ∑ i, (inner ℝ (x i) (w - ridge x y μ)) ^ 2 := by positivity
  linarith

/-- Positive regularization makes the objective minimizer unique. -/
theorem objective_minimizer_unique (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {μ : ℝ}
    (hμ : 0 < μ) (w : EuclideanSpace ℝ d)
    (hmin : objective x y μ w ≤ objective x y μ (ridge x y μ)) : w = ridge x y μ := by
  have hgap := objective_gap x y hμ w
  have hsum : 0 ≤ (Fintype.card ι : ℝ)⁻¹ *
      ∑ i, (inner ℝ (x i) (w - ridge x y μ)) ^ 2 := by positivity
  have hnorm : ‖w - ridge x y μ‖ ^ 2 = 0 := by nlinarith [sq_nonneg ‖w - ridge x y μ‖]
  exact sub_eq_zero.mp (norm_eq_zero.mp ((sq_eq_zero_iff).mp hnorm))

section Support

variable [Nonempty ι]

theorem sample_card_pos : 0 < (Fintype.card ι : ℝ) := by exact_mod_cast Fintype.card_pos

omit [DecidableEq d] in
theorem crossMoment_norm_le (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {R Y : ℝ}
    (_hR : 0 ≤ R) (hY : 0 ≤ Y) (hx : ∀ i, ‖x i‖ ≤ R) (hy : ∀ i, |y i| ≤ Y) :
    ‖crossMoment x y‖ ≤ R * Y := by
  have hN : 0 < (Fintype.card ι : ℝ) := sample_card_pos
  rw [crossMoment, norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc (Fintype.card ι : ℝ)⁻¹ * ‖∑ i, y i • x i‖ ≤
        (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖y i • x i‖ := by gcongr; exact norm_sum_le _ _
    _ ≤ (Fintype.card ι : ℝ)⁻¹ * ∑ _i : ι, Y * R := by
      gcongr with i
      rw [norm_smul, Real.norm_eq_abs]
      exact mul_le_mul (hy i) (hx i) (norm_nonneg _) hY
    _ = R * Y := by simp [hN.ne', mul_comm]

variable [DecidableEq ι]

omit [Nonempty ι] [DecidableEq ι] in
theorem sum_sub_of_eq_off {E : Type*} [AddCommGroup E] (f g : ι → E) (k : ι)
    (heq : ∀ i, i ≠ k → f i = g i) : ∑ i, f i - ∑ i, g i = f k - g k := by
  rw [← sum_sub_distrib]
  exact sum_eq_single k (fun i _ hik => by rw [heq i hik, sub_self])
    (fun h => (h (mem_univ k)).elim)

omit [Fintype d] [Nonempty ι] [DecidableEq ι] in
theorem gram_sub_replacement (x x' : ι → EuclideanSpace ℝ d) (μ : ℝ) (k : ι)
    (heq : ∀ i, i ≠ k → x i = x' i) :
    gram x μ - gram x' μ = (Fintype.card ι : ℝ)⁻¹ • (outer (x k) - outer (x' k)) := by
  calc gram x μ - gram x' μ = (Fintype.card ι : ℝ)⁻¹ •
        (∑ i, outer (x i) - ∑ i, outer (x' i)) := by simp only [gram, smul_sub]; abel
    _ = _ := by rw [sum_sub_of_eq_off _ _ k (fun i hi => congrArg outer (heq i hi))]

omit [DecidableEq ι] in
theorem gram_sub_norm_le (x x' : ι → EuclideanSpace ℝ d) (μ : ℝ) (k : ι) {R : ℝ}
    (_hR : 0 ≤ R) (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (heq : ∀ i, i ≠ k → x i = x' i) :
    ‖gram x μ - gram x' μ‖ ≤ 2 * R ^ 2 / Fintype.card ι := by
  rw [gram_sub_replacement x x' μ k heq, norm_smul, Real.norm_eq_abs,
    abs_of_nonneg (by positivity)]
  calc (Fintype.card ι : ℝ)⁻¹ * ‖outer (x k) - outer (x' k)‖ ≤
        (Fintype.card ι : ℝ)⁻¹ * (‖outer (x k)‖ + ‖outer (x' k)‖) := by gcongr; exact norm_sub_le _ _
    _ ≤ (Fintype.card ι : ℝ)⁻¹ * (R ^ 2 + R ^ 2) := by
      rw [norm_outer, norm_outer]
      gcongr
      · exact hx k
      · exact hx' k
    _ = _ := by ring

omit [DecidableEq d] [DecidableEq ι] in
theorem crossMoment_sub_norm_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → ℝ) (k : ι)
    {R Y : ℝ} (_hR : 0 ≤ R) (hY : 0 ≤ Y)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, |y i| ≤ Y) (hy' : ∀ i, |y' i| ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i) :
    ‖crossMoment x y - crossMoment x' y'‖ ≤ 2 * R * Y / Fintype.card ι := by
  have heq : ∀ i, i ≠ k → y i • x i = y' i • x' i := fun i hi => by rw [heqx i hi, heqy i hi]
  rw [crossMoment, crossMoment, ← smul_sub, sum_sub_of_eq_off _ _ k heq,
    norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc (Fintype.card ι : ℝ)⁻¹ * ‖y k • x k - y' k • x' k‖ ≤
        (Fintype.card ι : ℝ)⁻¹ * (‖y k • x k‖ + ‖y' k • x' k‖) := by gcongr; exact norm_sub_le _ _
    _ ≤ (Fintype.card ι : ℝ)⁻¹ * (Y * R + Y * R) := by
      rw [norm_smul, norm_smul, Real.norm_eq_abs, Real.norm_eq_abs]
      gcongr
      · exact hy k
      · exact hx k
      · exact hy' k
      · exact hx' k
    _ = _ := by ring

/-- Perturbing both normal-equation matrices and cross moments. This is deterministic
and can also consume generated-target error certificates. -/
theorem linear_readout_sub_le (A A' : Matrix d d ℝ) (b b' : EuclideanSpace ℝ d)
    (hA : IsUnit A.det) (hA' : IsUnit A'.det) {M eA eb B : ℝ}
    (hM : ‖A⁻¹‖ ≤ M) (hM' : ‖A'⁻¹‖ ≤ M) (heA : ‖A - A'‖ ≤ eA)
    (heb : ‖b - b'‖ ≤ eb) (hB : ‖b'‖ ≤ B) :
    ‖Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A⁻¹ b -
      Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A'⁻¹ b'‖ ≤ M * eb + M ^ 2 * eA * B := by
  let P := Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A⁻¹
  let P' := Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A'⁻¹
  have hM0 : 0 ≤ M := (norm_nonneg _).trans hM
  have heA0 : 0 ≤ eA := (norm_nonneg _).trans heA
  have heb0 : 0 ≤ eb := (norm_nonneg _).trans heb
  have hB0 : 0 ≤ B := (norm_nonneg _).trans hB
  have hdiff : ‖A⁻¹ - A'⁻¹‖ ≤ M ^ 2 * eA := by
    calc _ ≤ ‖A⁻¹‖ * ‖A' - A‖ * ‖A'⁻¹‖ :=
        Stability.norm_inverse_sub_le (nonsing_inv_mul _ hA) (mul_nonsing_inv _ hA')
      _ ≤ M * eA * M := by rw [norm_sub_rev]; gcongr
      _ = _ := by ring
  have hb : ‖P b - P b'‖ ≤ M * eb := by
    rw [← map_sub]
    calc ‖P (b - b')‖ ≤ ‖P‖ * ‖b - b'‖ := P.le_opNorm _
      _ ≤ M * eb := by change ‖A⁻¹‖ * ‖b - b'‖ ≤ _; gcongr
  have hb' : ‖P b' - P' b'‖ ≤ M ^ 2 * eA * B := by
    change ‖(P - P') b'‖ ≤ _
    calc ‖(P - P') b'‖ ≤ ‖P - P'‖ * ‖b'‖ := (P - P').le_opNorm _
      _ = ‖A⁻¹ - A'⁻¹‖ * ‖b'‖ := by
        change ‖Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A⁻¹ -
          Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) A'⁻¹‖ * ‖b'‖ = _
        rw [← map_sub, Matrix.l2_opNorm_toEuclideanCLM]
      _ ≤ M ^ 2 * eA * B := by gcongr
  exact (norm_sub_le_norm_sub_add_norm_sub (P b) (P b') (P' b')).trans (add_le_add hb hb')

omit [DecidableEq ι] in
/-- Replacing one bounded support observation changes ridge coefficients by order
`1 / (N μ)`, with a separate contribution from the feature Gram matrix. -/
theorem ridge_replacement_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → ℝ) (k : ι)
    {R Y μ : ℝ} (hR : 0 ≤ R) (hY : 0 ≤ Y) (hμ : 0 < μ)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, |y i| ≤ Y) (hy' : ∀ i, |y' i| ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i) :
    ‖ridge x y μ - ridge x' y' μ‖ ≤
      2 * R * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ) := by
  have hb := linear_readout_sub_le (gram x μ) (gram x' μ) (crossMoment x y) (crossMoment x' y')
    (isUnit_iff_ne_zero.mpr (gram_posDef x hμ).det_pos.ne')
    (isUnit_iff_ne_zero.mpr (gram_posDef x' hμ).det_pos.ne')
    (inverse_gram_norm_le x hμ) (inverse_gram_norm_le x' hμ)
    (gram_sub_norm_le x x' μ k hR hx hx' heqx)
    (crossMoment_sub_norm_le x x' y y' k hR hY hx hx' hy hy' heqx heqy)
    (crossMoment_norm_le x' y' hR hY hx' hy')
  change ‖ridge x y μ - ridge x' y' μ‖ ≤ _ at hb
  convert hb using 1
  ring

omit [DecidableEq ι] in
/-- Fixed-feature prediction stability for one replaced support observation. -/
theorem prediction_replacement_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → ℝ) (k : ι)
    {R Y μ : ℝ} (hR : 0 ≤ R) (hY : 0 ≤ Y) (hμ : 0 < μ)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, |y i| ≤ Y) (hy' : ∀ i, |y' i| ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i)
    (z : EuclideanSpace ℝ d) (hz : ‖z‖ ≤ R) :
    |inner ℝ z (ridge x y μ) - inner ℝ z (ridge x' y' μ)| ≤
      2 * R ^ 2 * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ) := by
  rw [← inner_sub_right]
  calc |inner ℝ z (ridge x y μ - ridge x' y' μ)| ≤ ‖z‖ * ‖ridge x y μ - ridge x' y' μ‖ :=
      abs_real_inner_le_norm _ _
    _ ≤ R * (2 * R * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ)) := by
      gcongr
      exact ridge_replacement_le x x' y y' k hR hY hμ hx hx' hy hy' heqx heqy
    _ = _ := by ring

end Support

section VectorTargets

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- Vector-target cross moment, as a linear map from features to target coordinates. -/
noncomputable def crossOperator (x : ι → EuclideanSpace ℝ d) (y : ι → E) :
    EuclideanSpace ℝ d →L[ℝ] E :=
  (Fintype.card ι : ℝ)⁻¹ • ∑ i, InnerProductSpace.rankOne ℝ (y i) (x i)

/-- Multioutput ridge readout. All output coordinates share the same regularized Gram
matrix; this is equivalently the usual matrix ridge normal-equation solution. -/
noncomputable def ridgeOperator (x : ι → EuclideanSpace ℝ d) (y : ι → E) (μ : ℝ) :
    EuclideanSpace ℝ d →L[ℝ] E :=
  (crossOperator x y).comp (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)⁻¹)

omit [DecidableEq d] in
theorem crossOperator_apply (x : ι → EuclideanSpace ℝ d) (y : ι → E) (w : EuclideanSpace ℝ d) :
    crossOperator x y w = (Fintype.card ι : ℝ)⁻¹ • ∑ i, inner ℝ (x i) w • y i := by
  simp only [crossOperator, _root_.smul_apply, _root_.sum_apply, InnerProductSpace.rankOne_apply]

/-- Multioutput normal equations are an identity of linear maps. -/
theorem operator_normal_equation (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ}
    (hμ : 0 < μ) :
    (ridgeOperator x y μ).comp (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)) =
      crossOperator x y := by
  have hinv := nonsing_inv_mul (gram x μ) (isUnit_iff_ne_zero.mpr (gram_posDef x hμ).det_pos.ne')
  have ht := congrArg (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ)) hinv
  simp only [map_mul, map_one] at ht
  change (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)⁻¹).comp
    (Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)) = 1 at ht
  rw [ridgeOperator, ContinuousLinearMap.comp_assoc, ht]
  ext w
  rfl

/-- The multioutput objective uses the squared Hilbert--Schmidt norm of the coefficient
map, expressed in the feature orthonormal basis. -/
noncomputable def operatorObjective (x : ι → EuclideanSpace ℝ d) (y : ι → E) (μ : ℝ)
    (F : EuclideanSpace ℝ d →L[ℝ] E) : ℝ :=
  (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖F (x i) - y i‖ ^ 2 +
    μ * ∑ j, ‖F (EuclideanSpace.basisFun d ℝ j)‖ ^ 2

omit [DecidableEq d] in
private theorem basis_cross_sum (r : E) (z : EuclideanSpace ℝ d)
    (H : EuclideanSpace ℝ d →L[ℝ] E) :
    ∑ j, inner ℝ z (EuclideanSpace.basisFun d ℝ j) *
      inner ℝ r (H (EuclideanSpace.basisFun d ℝ j)) = inner ℝ r (H z) := by
  have hz := congrArg H ((EuclideanSpace.basisFun d ℝ).sum_repr' z)
  simp only [map_sum, map_smul] at hz
  rw [← hz, inner_sum]
  exact sum_congr rfl fun j _ => by rw [real_inner_smul_right, real_inner_comm z]

private theorem operator_cross_zero (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ}
    (hμ : 0 < μ) (H : EuclideanSpace ℝ d →L[ℝ] E) :
    μ * ∑ j, inner ℝ (ridgeOperator x y μ (EuclideanSpace.basisFun d ℝ j))
      (H (EuclideanSpace.basisFun d ℝ j)) +
      (Fintype.card ι : ℝ)⁻¹ * ∑ i, inner ℝ (ridgeOperator x y μ (x i) - y i) (H (x i)) = 0 := by
  let F := ridgeOperator x y μ
  let e := EuclideanSpace.basisFun d ℝ
  have heq (j : d) : μ * inner ℝ (F (e j)) (H (e j)) +
      (Fintype.card ι : ℝ)⁻¹ * ∑ i, inner ℝ (x i) (e j) *
        inner ℝ (F (x i) - y i) (H (e j)) = 0 := by
    have hn := congrArg (fun Q : EuclideanSpace ℝ d →L[ℝ] E => Q (e j))
      (operator_normal_equation x y hμ)
    simp only [ContinuousLinearMap.comp_apply, gram_apply, crossOperator_apply,
      map_add, map_smul, map_sum] at hn
    have ht := congrArg (fun v : E => inner ℝ v (H (e j))) hn
    simp only [inner_add_left, real_inner_smul_left, sum_inner] at ht
    have hs : ∑ i, inner ℝ (x i) (e j) * inner ℝ (F (x i) - y i) (H (e j)) =
        ∑ i, inner ℝ (x i) (e j) * inner ℝ (F (x i)) (H (e j)) -
          ∑ i, inner ℝ (x i) (e j) * inner ℝ (y i) (H (e j)) := by
      simp only [inner_sub_left, mul_sub, sum_sub_distrib]
    rw [hs]
    change μ * inner ℝ (F (e j)) (H (e j)) +
      (Fintype.card ι : ℝ)⁻¹ * ∑ i, inner ℝ (x i) (e j) * inner ℝ (F (x i)) (H (e j)) =
      (Fintype.card ι : ℝ)⁻¹ * ∑ i, inner ℝ (x i) (e j) * inner ℝ (y i) (H (e j)) at ht
    linarith
  have hs := congrArg (fun f : d → ℝ => ∑ j, f j) (funext heq)
  simp only [sum_add_distrib, ← mul_sum, sum_const_zero] at hs
  rw [sum_comm] at hs
  dsimp [e] at hs
  simp_rw [basis_cross_sum] at hs
  exact hs

/-- Exact objective gap proves that the operator normal-equation solution is the
multioutput ridge estimator, rather than merely a coordinatewise candidate. -/
theorem operator_objective_gap (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ}
    (hμ : 0 < μ) (Q : EuclideanSpace ℝ d →L[ℝ] E) :
    operatorObjective x y μ Q - operatorObjective x y μ (ridgeOperator x y μ) =
      (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖(Q - ridgeOperator x y μ) (x i)‖ ^ 2 +
        μ * ∑ j, ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 := by
  let F := ridgeOperator x y μ
  let H := Q - F
  have hd : ∑ i, ‖Q (x i) - y i‖ ^ 2 - ∑ i, ‖F (x i) - y i‖ ^ 2 =
      2 * ∑ i, inner ℝ (F (x i) - y i) (H (x i)) + ∑ i, ‖H (x i)‖ ^ 2 := by
    rw [← sum_sub_distrib, mul_sum, ← sum_add_distrib]
    apply sum_congr rfl
    intro i _
    have hi : Q (x i) - y i = (F (x i) - y i) + H (x i) := by dsimp [H]; simp
    rw [hi, norm_add_sq_real]
    ring
  have hr : ∑ j, ‖Q (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 -
      ∑ j, ‖F (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 =
      2 * ∑ j, inner ℝ (F (EuclideanSpace.basisFun d ℝ j)) (H (EuclideanSpace.basisFun d ℝ j)) +
        ∑ j, ‖H (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 := by
    rw [← sum_sub_distrib, mul_sum, ← sum_add_distrib]
    apply sum_congr rfl
    intro j _
    have hj : Q (EuclideanSpace.basisFun d ℝ j) =
        F (EuclideanSpace.basisFun d ℝ j) + H (EuclideanSpace.basisFun d ℝ j) := by dsimp [H]; simp
    rw [hj, norm_add_sq_real]
    ring
  have hc := operator_cross_zero x y hμ H
  change μ * ∑ j, inner ℝ (F (EuclideanSpace.basisFun d ℝ j)) (H (EuclideanSpace.basisFun d ℝ j)) +
    (Fintype.card ι : ℝ)⁻¹ * ∑ i, inner ℝ (F (x i) - y i) (H (x i)) = 0 at hc
  change (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖Q (x i) - y i‖ ^ 2 +
      μ * ∑ j, ‖Q (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 -
      ((Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖F (x i) - y i‖ ^ 2 +
        μ * ∑ j, ‖F (EuclideanSpace.basisFun d ℝ j)‖ ^ 2) = _
  have hs : (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖Q (x i) - y i‖ ^ 2 +
      μ * ∑ j, ‖Q (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 -
      ((Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖F (x i) - y i‖ ^ 2 +
        μ * ∑ j, ‖F (EuclideanSpace.basisFun d ℝ j)‖ ^ 2) =
      (Fintype.card ι : ℝ)⁻¹ * (∑ i, ‖Q (x i) - y i‖ ^ 2 - ∑ i, ‖F (x i) - y i‖ ^ 2) +
        μ * (∑ j, ‖Q (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 -
          ∑ j, ‖F (EuclideanSpace.basisFun d ℝ j)‖ ^ 2) := by ring
  rw [hs, hd, hr]
  change _ = (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖H (x i)‖ ^ 2 +
    μ * ∑ j, ‖H (EuclideanSpace.basisFun d ℝ j)‖ ^ 2
  linarith

theorem operator_objective_minimal (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ}
    (hμ : 0 < μ) (Q : EuclideanSpace ℝ d →L[ℝ] E) :
    operatorObjective x y μ (ridgeOperator x y μ) ≤ operatorObjective x y μ Q := by
  have hg := operator_objective_gap x y hμ Q
  have hnonneg : 0 ≤ (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖(Q - ridgeOperator x y μ) (x i)‖ ^ 2 +
      μ * ∑ j, ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 := by positivity
  linarith

/-- Positive regularization makes the multioutput objective minimizer unique. -/
theorem operator_objective_minimizer_unique (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ}
    (hμ : 0 < μ) (Q : EuclideanSpace ℝ d →L[ℝ] E)
    (hmin : operatorObjective x y μ Q ≤ operatorObjective x y μ (ridgeOperator x y μ)) :
    Q = ridgeOperator x y μ := by
  have hg := operator_objective_gap x y hμ Q
  have hdata : 0 ≤ (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖(Q - ridgeOperator x y μ) (x i)‖ ^ 2 := by positivity
  have hreg : ∑ j, ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 = 0 := by
    have hp : 0 ≤ ∑ j, ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j)‖ ^ 2 :=
      sum_nonneg fun _ _ => sq_nonneg _
    nlinarith
  have hb (j : d) : Q (EuclideanSpace.basisFun d ℝ j) =
      ridgeOperator x y μ (EuclideanSpace.basisFun d ℝ j) := by
    have hs := single_le_sum (fun k (_ : k ∈ (univ : Finset d)) =>
      sq_nonneg ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ k)‖) (mem_univ j)
    rw [hreg] at hs
    have hz : ‖(Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j)‖ = 0 := by nlinarith [norm_nonneg ((Q - ridgeOperator x y μ) (EuclideanSpace.basisFun d ℝ j))]
    exact sub_eq_zero.mp (norm_eq_zero.mp hz)
  ext z
  have hq := congrArg Q ((EuclideanSpace.basisFun d ℝ).sum_repr' z)
  have hf := congrArg (ridgeOperator x y μ) ((EuclideanSpace.basisFun d ℝ).sum_repr' z)
  simp only [map_sum, map_smul] at hq hf
  rw [← hq, ← hf]
  exact sum_congr rfl fun j _ => by rw [hb j]

variable [Nonempty ι]

omit [DecidableEq d] in
theorem crossOperator_norm_le (x : ι → EuclideanSpace ℝ d) (y : ι → E) {R Y : ℝ}
    (_hR : 0 ≤ R) (hY : 0 ≤ Y) (hx : ∀ i, ‖x i‖ ≤ R) (hy : ∀ i, ‖y i‖ ≤ Y) :
    ‖crossOperator x y‖ ≤ R * Y := by
  have hN : 0 < (Fintype.card ι : ℝ) := sample_card_pos
  rw [crossOperator, norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc (Fintype.card ι : ℝ)⁻¹ * ‖∑ i, InnerProductSpace.rankOne ℝ (y i) (x i)‖ ≤
        (Fintype.card ι : ℝ)⁻¹ * ∑ i, ‖InnerProductSpace.rankOne ℝ (y i) (x i)‖ := by gcongr; exact norm_sum_le _ _
    _ ≤ (Fintype.card ι : ℝ)⁻¹ * ∑ _i : ι, Y * R := by
      gcongr with i
      rw [InnerProductSpace.norm_rankOne]
      exact mul_le_mul (hy i) (hx i) (norm_nonneg _) hY
    _ = R * Y := by simp [hN.ne', mul_comm]

omit [DecidableEq d] in
theorem crossOperator_sub_norm_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → E) (k : ι)
    {R Y : ℝ} (_hR : 0 ≤ R) (hY : 0 ≤ Y)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, ‖y i‖ ≤ Y) (hy' : ∀ i, ‖y' i‖ ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i) :
    ‖crossOperator x y - crossOperator x' y'‖ ≤ 2 * R * Y / Fintype.card ι := by
  have heq : ∀ i, i ≠ k → InnerProductSpace.rankOne ℝ (y i) (x i) =
      InnerProductSpace.rankOne ℝ (y' i) (x' i) := fun i hi => by rw [heqx i hi, heqy i hi]
  rw [crossOperator, crossOperator, ← smul_sub, sum_sub_of_eq_off _ _ k heq,
    norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
  calc (Fintype.card ι : ℝ)⁻¹ * ‖InnerProductSpace.rankOne ℝ (y k) (x k) -
        InnerProductSpace.rankOne ℝ (y' k) (x' k)‖ ≤
        (Fintype.card ι : ℝ)⁻¹ * (‖InnerProductSpace.rankOne ℝ (y k) (x k)‖ +
          ‖InnerProductSpace.rankOne ℝ (y' k) (x' k)‖) := by gcongr; exact norm_sub_le _ _
    _ ≤ (Fintype.card ι : ℝ)⁻¹ * (Y * R + Y * R) := by
      rw [InnerProductSpace.norm_rankOne, InnerProductSpace.norm_rankOne]
      gcongr
      · exact hy k
      · exact hx k
      · exact hy' k
      · exact hx' k
    _ = _ := by ring

set_option maxHeartbeats 1200000 in
/-- Dimension-free stability of the complete vector-target readout in operator norm. -/
theorem ridgeOperator_replacement_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → E) (k : ι)
    {R Y μ : ℝ} (hR : 0 ≤ R) (hY : 0 ≤ Y) (hμ : 0 < μ)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, ‖y i‖ ≤ Y) (hy' : ∀ i, ‖y' i‖ ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i) :
    ‖ridgeOperator x y μ - ridgeOperator x' y' μ‖ ≤
      2 * R * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ) := by
  let P := Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)⁻¹
  let P' := Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x' μ)⁻¹
  let B := crossOperator x y
  let B' := crossOperator x' y'
  have hM : ‖P‖ ≤ μ⁻¹ := inverse_gram_norm_le x hμ
  have hM' : ‖P'‖ ≤ μ⁻¹ := inverse_gram_norm_le x' hμ
  have hP : ‖P - P'‖ ≤ μ⁻¹ ^ 2 * (2 * R ^ 2 / Fintype.card ι) := by
    have hb := Stability.norm_inverse_sub_le
      (nonsing_inv_mul _ (isUnit_iff_ne_zero.mpr (gram_posDef x hμ).det_pos.ne'))
      (mul_nonsing_inv _ (isUnit_iff_ne_zero.mpr (gram_posDef x' hμ).det_pos.ne'))
    rw [norm_sub_rev (gram x' μ) (gram x μ)] at hb
    have hg := gram_sub_norm_le x x' μ k hR hx hx' heqx
    change ‖Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x μ)⁻¹ -
      Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (gram x' μ)⁻¹‖ ≤ _
    rw [← map_sub, Matrix.l2_opNorm_toEuclideanCLM]
    calc _ ≤ ‖(gram x μ)⁻¹‖ * ‖gram x μ - gram x' μ‖ * ‖(gram x' μ)⁻¹‖ := hb
      _ ≤ μ⁻¹ * (2 * R ^ 2 / Fintype.card ι) * μ⁻¹ := by
        apply mul_le_mul
        · exact mul_le_mul (inverse_gram_norm_le x hμ) hg (norm_nonneg _) (by positivity)
        · exact inverse_gram_norm_le x' hμ
        · exact norm_nonneg _
        · positivity
      _ = _ := by ring
  have hB := crossOperator_norm_le x' y' hR hY hx' hy'
  have hdiff := crossOperator_sub_norm_le x x' y y' k hR hY hx hx' hy hy' heqx heqy
  have hs : ridgeOperator x y μ - ridgeOperator x' y' μ =
      (B - B').comp P + B'.comp (P - P') := by
    simp only [ContinuousLinearMap.sub_comp, ContinuousLinearMap.comp_sub, ridgeOperator, B, B', P, P']
    abel
  rw [hs]
  calc _ ≤ ‖(B - B').comp P‖ + ‖B'.comp (P - P')‖ := norm_add_le _ _
    _ ≤ ‖B - B'‖ * ‖P‖ + ‖B'‖ * ‖P - P'‖ :=
      add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
    _ ≤ (2 * R * Y / Fintype.card ι) * μ⁻¹ + (R * Y) *
        (μ⁻¹ ^ 2 * (2 * R ^ 2 / Fintype.card ι)) := by gcongr
    _ = _ := by ring

/-- Replacement prediction bound for norm-bounded vector targets, without an output
dimension factor. -/
theorem vector_prediction_replacement_le (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → E) (k : ι)
    {R Y μ : ℝ} (hR : 0 ≤ R) (hY : 0 ≤ Y) (hμ : 0 < μ)
    (hx : ∀ i, ‖x i‖ ≤ R) (hx' : ∀ i, ‖x' i‖ ≤ R)
    (hy : ∀ i, ‖y i‖ ≤ Y) (hy' : ∀ i, ‖y' i‖ ≤ Y)
    (heqx : ∀ i, i ≠ k → x i = x' i) (heqy : ∀ i, i ≠ k → y i = y' i)
    (z : EuclideanSpace ℝ d) (hz : ‖z‖ ≤ R) :
    ‖ridgeOperator x y μ z - ridgeOperator x' y' μ z‖ ≤
      2 * R ^ 2 * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ) := by
  change ‖(ridgeOperator x y μ - ridgeOperator x' y' μ) z‖ ≤ _
  calc _ ≤ ‖ridgeOperator x y μ - ridgeOperator x' y' μ‖ * ‖z‖ :=
      (ridgeOperator x y μ - ridgeOperator x' y' μ).le_opNorm z
    _ ≤ (2 * R * Y / ((Fintype.card ι : ℝ) * μ) * (1 + R ^ 2 / μ)) * R := by
      gcongr
      exact ridgeOperator_replacement_le x x' y y' k hR hY hμ hx hx' hy hy' heqx heqy
    _ = _ := by ring

end VectorTargets

end FreeFoundations.ReadoutStability
