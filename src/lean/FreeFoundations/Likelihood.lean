import Mathlib.Algebra.Order.Chebyshev
import Mathlib.Analysis.InnerProductSpace.Basic
import Mathlib.LinearAlgebra.Matrix.Trace
import FreeFoundations.Score

/-!
# What the Gaussian likelihood sees of a network

The spatial-error forecast is `Σ = A⁻¹ D A⁻ᵀ` with `A = I − λW` and positive diagonal `D`.
Its precision is `Aᵀ D⁻¹ A` (`precision_eq`), so the expected Gaussian loss against a second
moment `M` (`Score.expected_loss`) splits into three terms (`spatial_loss`):

`log det Σ + tr(Σ⁻¹M) = Σᵢ log dᵢ − 2 log |det(I − λW)| + Σᵢ mᵢ(λ)/dᵢ`.

The first is a variance term. The second depends on `W` only through its eigenvalues. The
third weights the *filtered second moments* `mᵢ(λ) = [(I − λW) M (I − λW)ᵀ]ᵢᵢ`, the second
moments of the filtered residuals `((I − λW)u)ᵢ`, by `D⁻¹`.

When the second moment is a common part plus idiosyncratic noise,
`Mⱼₖ = ⟪aⱼ, aₖ⟫ + ηⱼ[j = k]` (`moment`), and `W` has zero diagonal, firm `i`'s filtered
second moment is

`mᵢ(λ) = ‖aᵢ − λ Σⱼ Wᵢⱼ aⱼ‖² + ηᵢ + λ² Σⱼ Wᵢⱼ² ηⱼ`

(`filtered_second_moment`): how badly the neighbours' exposures reconstruct the firm's own,
its own noise, and the noise its neighbours bring in. In powers of `λ`
(`filtered_second_moment_expand`):

* the constant `‖aᵢ‖² + ηᵢ` does not depend on the network;
* the linear coefficient is `−2 Σⱼ Wᵢⱼ ⟪aᵢ, aⱼ⟫`. Idiosyncratic variance never enters it,
  and with equal `dᵢ = d` its sum over firms is `−2⟨W, C⟩/d` for the common covariance `C`,
  the inner product that `Value.decomposition` splits into hub and proximity terms;
* the quadratic coefficient is `‖Σⱼ Wᵢⱼ aⱼ‖² + Σⱼ Wᵢⱼ² ηⱼ`. With equal noise `η` the second
  part is `η` times the row's Herfindahl index `Σⱼ Wᵢⱼ²`, the reciprocal of its effective
  neighbours, which is at least `1/m` for a row spread over `m` firms and equals it for equal
  weights (`herfindahl_ge`, `herfindahl_uniform`).

So a network earns through the linear term and pays for concentration through the quadratic
one. A diffuse row has the smallest noise cost, which is one way a near-uniform network can
score well without proximity information. Two networks matched on mean effective neighbours
can still differ in this cost, which depends on the mean Herfindahl index instead.
-/

namespace FreeFoundations.Likelihood

open Matrix

variable {n : Type*} [Fintype n] [DecidableEq n]

/-! ## The spatial-error loss -/

/-- The spatial-error precision: `(A⁻¹ D A⁻ᵀ)⁻¹ = Aᵀ D⁻¹ A`. -/
theorem precision_eq (A : Matrix n n ℝ) (hA : IsUnit A.det) (d : n → ℝ) (hd : ∀ i, d i ≠ 0) :
    (A⁻¹ * diagonal d * A⁻¹ᵀ)⁻¹ = Aᵀ * diagonal (fun i => (d i)⁻¹) * A := by
  apply inv_eq_right_inv
  have h1 : A⁻¹ᵀ * Aᵀ = 1 := by rw [← transpose_mul, mul_nonsing_inv _ hA, transpose_one]
  have h2 : diagonal d * diagonal (fun i => (d i)⁻¹) = 1 := by
    rw [diagonal_mul_diagonal, ← diagonal_one]
    congr 1
    funext i
    exact mul_inv_cancel₀ (hd i)
  calc A⁻¹ * diagonal d * A⁻¹ᵀ * (Aᵀ * diagonal (fun i => (d i)⁻¹) * A)
      = A⁻¹ * (diagonal d * (A⁻¹ᵀ * Aᵀ) * diagonal (fun i => (d i)⁻¹)) * A := by
        simp only [Matrix.mul_assoc]
    _ = 1 := by rw [h1, Matrix.mul_one, h2, Matrix.mul_one, nonsing_inv_mul _ hA]

/-- `tr(Aᵀ diag(e) A M) = Σᵢ eᵢ (A M Aᵀ)ᵢᵢ`. -/
theorem trace_precision (A : Matrix n n ℝ) (e : n → ℝ) (M : Matrix n n ℝ) :
    trace (Aᵀ * diagonal e * A * M) = ∑ i, e i * (A * M * Aᵀ) i i := by
  have h : Aᵀ * diagonal e * A * M = Aᵀ * (diagonal e * A * M) := by
    simp only [Matrix.mul_assoc]
  rw [h, trace_mul_comm]
  simp only [trace, Matrix.mul_assoc, diagonal_mul, diag_apply]

/-- **The quadratic term** is the `D⁻¹`-weighted sum of filtered second moments. -/
theorem quadratic_term (A : Matrix n n ℝ) (hA : IsUnit A.det) (d : n → ℝ) (hd : ∀ i, d i ≠ 0)
    (M : Matrix n n ℝ) :
    trace ((A⁻¹ * diagonal d * A⁻¹ᵀ)⁻¹ * M) = ∑ i, (A * M * Aᵀ) i i / d i := by
  rw [precision_eq A hA d hd, trace_precision]
  exact Finset.sum_congr rfl fun i _ => by rw [inv_mul_eq_div]

/-- **The log-determinant** is a variance term plus a spectrum term. -/
theorem logdet_eq (A : Matrix n n ℝ) (hA : IsUnit A.det) (d : n → ℝ) (hd : ∀ i, 0 < d i) :
    Real.log (A⁻¹ * diagonal d * A⁻¹ᵀ).det = ∑ i, Real.log (d i) - 2 * Real.log |A.det| := by
  have hI : A.det⁻¹ ≠ 0 := inv_ne_zero hA.ne_zero
  have hP : ∏ i, d i ≠ 0 := Finset.prod_ne_zero_iff.mpr fun i _ => (hd i).ne'
  rw [det_mul, det_mul, det_transpose, det_nonsing_inv, Ring.inverse_eq_inv', det_diagonal,
    Real.log_mul (mul_ne_zero hI hP) hI, Real.log_mul hI hP, Real.log_inv,
    Real.log_prod fun i _ => (hd i).ne', Real.log_abs]
  ring

/-- **Expected loss of the spatial-error forecast:** variance, spectrum, and the
`D⁻¹`-weighted filtered second moments. -/
theorem spatial_loss (A : Matrix n n ℝ) (hA : IsUnit A.det) (d : n → ℝ) (hd : ∀ i, 0 < d i)
    (M : Matrix n n ℝ) :
    Score.loss (A⁻¹ * diagonal d * A⁻¹ᵀ) M =
      ∑ i, Real.log (d i) - 2 * Real.log |A.det| + ∑ i, (A * M * Aᵀ) i i / d i := by
  rw [Score.loss, logdet_eq A hA d hd, quadratic_term A hA d (fun i => (hd i).ne') M]

/-! ## Filtered second moments -/

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

/-- The second moment of a common part with exposures `a` plus idiosyncratic variances `η`. -/
noncomputable def moment (a : n → E) (η : n → ℝ) : Matrix n n ℝ :=
  Matrix.of fun j k => inner ℝ (a j) (a k) + if j = k then η j else 0

omit [DecidableEq n] in
theorem gram_quadratic (x : n → ℝ) (a : n → E) :
    ∑ j, ∑ k, x j * inner ℝ (a j) (a k) * x k = ‖∑ j, x j • a j‖ ^ 2 := by
  rw [← real_inner_self_eq_norm_sq, sum_inner]
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [inner_sum]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [real_inner_smul_left, real_inner_smul_right]
  ring

theorem diagonal_quadratic (x η : n → ℝ) :
    ∑ j, ∑ k, x j * (if j = k then η j else 0) * x k = ∑ j, x j ^ 2 * η j := by
  refine Finset.sum_congr rfl fun j _ => ?_
  rw [Finset.sum_eq_single j (fun k _ hk => by rw [if_neg (Ne.symm hk)]; ring)
    (fun h => absurd (Finset.mem_univ j) h), if_pos rfl]
  ring

/-- **Filtered second moment.** With a zero-diagonal network, firm `i`'s filtered residual
has second moment equal to the neighbour-reconstruction error of its exposure, plus its own
noise, plus the noise its neighbours bring in. -/
theorem filtered_second_moment (W : Matrix n n ℝ) (hW : ∀ i, W i i = 0) (a : n → E)
    (η : n → ℝ) (c : ℝ) (i : n) :
    ((1 - c • W) * moment a η * (1 - c • W)ᵀ : Matrix n n ℝ) i i =
      ‖a i - c • ∑ j, W i j • a j‖ ^ 2 + η i + c ^ 2 * ∑ j, W i j ^ 2 * η j := by
  set x : n → ℝ := fun j => (if i = j then 1 else 0) - c * W i j with hx
  have hentry : ((1 - c • W) * moment a η * (1 - c • W)ᵀ : Matrix n n ℝ) i i =
      ∑ j, ∑ k, x j * (inner ℝ (a j) (a k) + if j = k then η j else 0) * x k := by
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.sub_apply, Matrix.one_apply,
      Matrix.smul_apply, smul_eq_mul, moment, Matrix.of_apply, Finset.sum_mul, hx]
    exact Finset.sum_comm
  have hvec : ∑ j, x j • a j = a i - c • ∑ j, W i j • a j := by
    simp only [hx, sub_smul, Finset.sum_sub_distrib, ite_smul, one_smul, zero_smul,
      Finset.sum_ite_eq, Finset.mem_univ, if_true, Finset.smul_sum, mul_smul]
  have hsq : ∀ j, x j ^ 2 * η j = (if i = j then η j else 0) + c ^ 2 * (W i j ^ 2 * η j) := by
    intro j
    by_cases h : i = j
    · subst h
      simp [hx, hW]
    · simp only [hx, if_neg h]
      ring
  rw [hentry]
  calc _ = ∑ j, ∑ k, (x j * inner ℝ (a j) (a k) * x k +
          x j * (if j = k then η j else 0) * x k) := by
        refine Finset.sum_congr rfl fun j _ => Finset.sum_congr rfl fun k _ => ?_
        ring
    _ = ‖a i - c • ∑ j, W i j • a j‖ ^ 2 + η i + c ^ 2 * ∑ j, W i j ^ 2 * η j := by
        simp_rw [Finset.sum_add_distrib]
        rw [gram_quadratic, diagonal_quadratic, hvec]
        simp_rw [hsq, Finset.sum_add_distrib, Finset.sum_ite_eq, Finset.mem_univ, if_true,
          ← Finset.mul_sum]
        ring

/-- **In powers of `λ`:** a network-free constant, a linear term that only common covariance
enters, and a concentration term. -/
theorem filtered_second_moment_expand (W : Matrix n n ℝ) (hW : ∀ i, W i i = 0) (a : n → E)
    (η : n → ℝ) (c : ℝ) (i : n) :
    ((1 - c • W) * moment a η * (1 - c • W)ᵀ : Matrix n n ℝ) i i =
      (‖a i‖ ^ 2 + η i) - 2 * c * ∑ j, W i j * inner ℝ (a i) (a j) +
        c ^ 2 * (‖∑ j, W i j • a j‖ ^ 2 + ∑ j, W i j ^ 2 * η j) := by
  rw [filtered_second_moment W hW a η c i, norm_sub_sq_real, norm_smul, real_inner_smul_right,
    inner_sum, Real.norm_eq_abs, mul_pow, sq_abs]
  simp_rw [real_inner_smul_right]
  ring

/-! ## Concentration -/

omit [Fintype n] [DecidableEq n] in
/-- **Concentrated rows bring in more noise.** A weight vector summing to one over `m` firms
has Herfindahl index at least `1/m`. -/
theorem herfindahl_ge (s : Finset n) (w : n → ℝ) (hw : ∑ j ∈ s, w j = 1) (hs : 0 < s.card) :
    1 / (s.card : ℝ) ≤ ∑ j ∈ s, w j ^ 2 := by
  have h := sq_sum_le_card_mul_sum_sq (s := s) (f := w)
  rw [hw, one_pow] at h
  rw [div_le_iff₀ (by exact_mod_cast hs)]
  linarith

omit [Fintype n] [DecidableEq n] in
/-- Equal weights attain the bound. -/
theorem herfindahl_uniform (s : Finset n) (hs : 0 < s.card) :
    ∑ _j ∈ s, (1 / (s.card : ℝ)) ^ 2 = 1 / (s.card : ℝ) := by
  have h : (s.card : ℝ) ≠ 0 := Nat.cast_ne_zero.mpr hs.ne'
  rw [Finset.sum_const, nsmul_eq_mul]
  field_simp

end FreeFoundations.Likelihood
