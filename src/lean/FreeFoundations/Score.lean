module

public import Mathlib.Analysis.Matrix.Order
public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import Mathlib.MeasureTheory.Integral.Bochner.Basic
public import FreeFoundations.Exposure

@[expose] public section

set_option backward.isDefEq.respectTransparency false

/-!
# What the scores measure

**Gaussian loss.** `L(Σ; u) = log det Σ + u'Σ⁻¹u`. For any law of `u` with finite second
moments `M = E[uu']`, linearity gives `E L(Σ; u) = log det Σ + tr(Σ⁻¹M)`, and

`E L(Σ; u) − E L(M; u) = tr(Σ⁻¹M) − log det(Σ⁻¹M) − N ≥ 0` (Stein's loss).

No normality is used, so the Gaussian score ranks covariance forecasts by how well they match
the second moment around the imposed mean. It says nothing about tails or higher moments.
The same algebra with the realized second moment `S = T⁻¹Σₜuₜuₜ'` describes the realized
score.

**Log score.** For finite outcomes, cross-entropy is entropy plus KL, and KL ≥ 0. The
expected log loss of a PFN therefore exceeds the Bayes loss under its task prior by exactly
the expected KL to the posterior predictive. That interprets PFN prediction; it is not a
claim about any hidden state.

**Selection.** An `ε`-minimiser of an empirical risk within `g` of the population risk is
within `2g + ε` of every candidate: approximation, generalisation and optimisation error.
-/

namespace FreeFoundations.Score

open Matrix MeasureTheory

variable {n : Type*} [Fintype n] [DecidableEq n]

/-! ## Second moments -/

omit [DecidableEq n] in
/-- `u'Au = tr(A uu')`. -/
theorem quadratic_eq_trace (A : Matrix n n ℝ) (v : n → ℝ) :
    v ⬝ᵥ (A *ᵥ v) = trace (A * vecMulVec v v) := by
  simp only [trace, diag, mul_apply, vecMulVec_apply, dotProduct, mulVec, Finset.mul_sum]
  exact Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => by ring

omit [DecidableEq n] in
/-- **Realized score.** Summed quadratic terms depend on the observations only through
their summed outer products. -/
theorem realized_quadratic {ι : Type*} (s : Finset ι) (A : Matrix n n ℝ) (u : ι → n → ℝ) :
    ∑ t ∈ s, u t ⬝ᵥ (A *ᵥ u t) = trace (A * ∑ t ∈ s, vecMulVec (u t) (u t)) := by
  rw [Matrix.mul_sum, trace_sum]
  exact Finset.sum_congr rfl fun t _ => quadratic_eq_trace A (u t)

variable {Ω : Type*} [MeasurableSpace Ω]

/-- The second-moment matrix `E[uu']`. -/
noncomputable def secondMoment (μ : Measure Ω) (u : Ω → n → ℝ) : Matrix n n ℝ :=
  Matrix.of fun i j => ∫ ω, u ω i * u ω j ∂μ

omit [DecidableEq n] in
/-- **Expected quadratic form.** `E[u'Au] = tr(A E[uu'])` whenever the second moments are
finite. -/
theorem integral_quadratic (μ : Measure Ω) (A : Matrix n n ℝ) (u : Ω → n → ℝ)
    (hint : ∀ i j, Integrable (fun ω => u ω i * u ω j) μ) :
    ∫ ω, u ω ⬝ᵥ (A *ᵥ u ω) ∂μ = trace (A * secondMoment μ u) := by
  have hpoint : ∀ ω, u ω ⬝ᵥ (A *ᵥ u ω) = ∑ i, ∑ j, A i j * (u ω j * u ω i) := fun ω => by
    simp only [dotProduct, mulVec, Finset.mul_sum]
    exact Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => by ring
  simp_rw [hpoint]
  rw [integral_finsetSum _ fun i _ => integrable_finsetSum _ fun j _ => (hint j i).const_mul _]
  simp only [trace, diag, mul_apply, secondMoment, of_apply]
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [integral_finsetSum _ fun j _ => (hint j i).const_mul _]
  exact Finset.sum_congr rfl fun j _ => integral_const_mul _ _

omit [DecidableEq n] in
/-- **Exposure distance is a response variance.** For common shocks `q` with second moment
`Ω = E[qq']` (the covariance when `q` is centred), the squared exposure distance
`(bᵢ − bⱼ)'Ω(bᵢ − bⱼ)` is the second moment of the response difference `(bᵢ − bⱼ)'q`. -/
theorem response_sq (μ : Measure Ω) (q : Ω → n → ℝ)
    (hint : ∀ i j, Integrable (fun ω => q ω i * q ω j) μ) (c : n → ℝ) :
    ∫ ω, (c ⬝ᵥ q ω) ^ 2 ∂μ = Exposure.form (secondMoment μ q) c c := by
  have hpoint : ∀ ω, (c ⬝ᵥ q ω) ^ 2 = q ω ⬝ᵥ (vecMulVec c c *ᵥ q ω) := fun ω => by
    simp only [dotProduct, mulVec, vecMulVec_apply, sq, Finset.sum_mul, Finset.mul_sum]
    rw [Finset.sum_comm]
    exact Finset.sum_congr rfl fun i _ => Finset.sum_congr rfl fun j _ => by ring
  simp_rw [hpoint]
  rw [integral_quadratic μ _ q hint, trace_mul_comm, ← quadratic_eq_trace]
  rfl

/-! ## Stein's loss -/

/-- Stein's loss of a forecast `C` against a second moment `S`. -/
noncomputable def stein (C S : Matrix n n ℝ) : ℝ :=
  trace (C⁻¹ * S) - Real.log S.det + Real.log C.det - Fintype.card n

/-- Gaussian loss averaged against the second moment `S`: `log det C + tr(C⁻¹S)`. -/
noncomputable def loss (C S : Matrix n n ℝ) : ℝ := Real.log C.det + trace (C⁻¹ * S)

open scoped MatrixOrder in
/-- **Stein's loss is nonnegative.** Factor `C = B'B`; then `M = B'⁻¹SB⁻¹` is positive
definite with `tr M = tr(C⁻¹S)` and `det M = det S / det C`, so Stein's loss is
`Σₖ(μₖ − log μₖ − 1) ≥ 0` over the eigenvalues `μₖ > 0` of `M`. -/
theorem stein_nonneg {C S : Matrix n n ℝ} (hC : C.PosDef) (hS : S.PosDef) : 0 ≤ stein C S := by
  obtain ⟨B, hB⟩ := CStarAlgebra.nonneg_iff_eq_star_mul_self.mp hC.posSemidef.nonneg
  rw [star_eq_conjTranspose] at hB
  have hdetC : C.det = B.det ^ 2 := by
    rw [hB, det_mul, det_conjTranspose, star_trivial, sq]
  have hBdet : B.det ≠ 0 := by
    intro h0
    have := hC.det_pos
    rw [hdetC, h0] at this
    simp at this
  set Bi := B⁻¹
  have hBi : IsUnit Bi := (isUnit_iff_isUnit_det _).mpr (by
    rw [det_nonsing_inv, Ring.inverse_eq_inv']
    exact isUnit_iff_ne_zero.mpr (inv_ne_zero hBdet))
  set M := Biᴴ * S * Bi
  have hM : M.PosDef := hS.conjTranspose_mul_mul_same (mulVec_injective_of_isUnit hBi)
  have hCinv : C⁻¹ = Bi * Biᴴ := by
    rw [hB, Matrix.mul_inv_rev, conjTranspose_nonsing_inv]
  have htrace : trace (C⁻¹ * S) = trace M := by
    rw [hCinv, Matrix.mul_assoc, trace_mul_comm]
  have hdetM : M.det = S.det / C.det := by
    simp only [M, det_mul, det_conjTranspose, star_trivial, Bi, det_nonsing_inv,
      Ring.inverse_eq_inv', hdetC]
    field_simp
  have hlog : Real.log M.det = Real.log S.det - Real.log C.det := by
    rw [hdetM, Real.log_div hS.det_pos.ne' hC.det_pos.ne']
  have hval : stein C S = ∑ k, (hM.1.eigenvalues k - Real.log (hM.1.eigenvalues k) - 1) := by
    have ht := hM.1.trace_eq_sum_eigenvalues
    have hd := hM.1.det_eq_prod_eigenvalues
    simp only [RCLike.ofReal_real_eq_id, id] at ht hd
    rw [Finset.sum_sub_distrib, Finset.sum_sub_distrib, ← ht, ← Real.log_prod
      (fun k _ => (hM.eigenvalues_pos k).ne'), ← hd, hlog, ← htrace]
    simp [stein]
    ring
  rw [hval]
  exact Finset.sum_nonneg fun k _ => by
    have := Real.log_le_sub_one_of_pos (hM.eigenvalues_pos k)
    linarith

/-- The loss gap to the second moment is Stein's loss. -/
theorem loss_sub {C S : Matrix n n ℝ} (hS : S.PosDef) : loss C S - loss S S = stein C S := by
  have : trace (S⁻¹ * S) = Fintype.card n := by
    rw [nonsing_inv_mul _ ((isUnit_iff_ne_zero).mpr hS.det_pos.ne'), trace_one]
  simp only [loss, stein, this]
  ring

/-- **Proper.** The second moment itself has the smallest expected Gaussian loss. -/
theorem loss_le {C S : Matrix n n ℝ} (hC : C.PosDef) (hS : S.PosDef) : loss S S ≤ loss C S := by
  have := loss_sub (C := C) hS
  linarith [stein_nonneg hC hS]

/-- **Expected Gaussian loss.** With finite second moments `M`, a forecast `C` has expected
loss `log det C + tr(C⁻¹M)`: the law of `u` enters only through `M`. -/
theorem expected_loss (μ : Measure Ω) (C : Matrix n n ℝ) (u : Ω → n → ℝ)
    (hint : ∀ i j, Integrable (fun ω => u ω i * u ω j) μ) :
    Real.log C.det + ∫ ω, u ω ⬝ᵥ (C⁻¹ *ᵥ u ω) ∂μ = loss C (secondMoment μ u) := by
  rw [integral_quadratic μ _ u hint, loss]

/-! ## Log score -/

variable {Y : Type*} [Fintype Y]

/-- Expected log loss of forecast `q` under outcome law `p`. -/
noncomputable def crossEntropy (p q : Y → ℝ) : ℝ := -∑ y, p y * Real.log (q y)

/-- Kullback–Leibler divergence of `q` from `p`. -/
noncomputable def kl (p q : Y → ℝ) : ℝ := ∑ y, p y * Real.log (p y / q y)

/-- Cross-entropy is entropy plus KL. -/
theorem crossEntropy_eq {p q : Y → ℝ} (hq : ∀ y, 0 < q y) :
    crossEntropy p q = crossEntropy p p + kl p q := by
  have hy : ∀ y, p y * Real.log (q y) = p y * Real.log (p y) - p y * Real.log (p y / q y) := by
    intro y
    rcases eq_or_ne (p y) 0 with h0 | h0
    · simp [h0]
    · rw [Real.log_div h0 (hq y).ne']
      ring
  simp only [crossEntropy, kl, hy, Finset.sum_sub_distrib]
  ring

/-- Gibbs: KL is nonnegative between distributions with equal mass. -/
theorem kl_nonneg {p q : Y → ℝ} (hp : ∀ y, 0 ≤ p y) (hq : ∀ y, 0 < q y)
    (hmass : ∑ y, p y = ∑ y, q y) : 0 ≤ kl p q := by
  have hterm : ∀ y, p y - q y ≤ p y * Real.log (p y / q y) := by
    intro y
    rcases (hp y).eq_or_lt with h0 | hpos
    · rw [← h0]
      simp [(hq y).le]
    · have hlog := Real.log_le_sub_one_of_pos (div_pos (hq y) hpos)
      have hinv : Real.log (p y / q y) = -Real.log (q y / p y) := by
        rw [← Real.log_inv, inv_div]
      rw [hinv]
      have : p y * (q y / p y - 1) = q y - p y := by field_simp
      nlinarith
  calc (0 : ℝ) = ∑ y, (p y - q y) := by rw [Finset.sum_sub_distrib, hmass, sub_self]
    _ ≤ kl p q := Finset.sum_le_sum fun y _ => hterm y

/-- **Log score is proper.** The true law has the smallest expected log loss. -/
theorem crossEntropy_le {p q : Y → ℝ} (hp : ∀ y, 0 ≤ p y) (hq : ∀ y, 0 < q y)
    (hmass : ∑ y, p y = ∑ y, q y) : crossEntropy p p ≤ crossEntropy p q := by
  rw [crossEntropy_eq hq]
  linarith [kl_nonneg hp hq hmass]

/-- **Pretraining.** Averaged over contexts `c` with weights `π c`, the log loss of a
predictor `q` exceeds the Bayes loss of the posterior predictive `p` by the expected KL. -/
theorem pretraining_excess {Ctx : Type*} (s : Finset Ctx) (π : Ctx → ℝ) (p q : Ctx → Y → ℝ)
    (hq : ∀ c y, 0 < q c y) :
    ∑ c ∈ s, π c * crossEntropy (p c) (q c) - ∑ c ∈ s, π c * crossEntropy (p c) (p c) =
      ∑ c ∈ s, π c * kl (p c) (q c) := by
  rw [← Finset.sum_sub_distrib]
  exact Finset.sum_congr rfl fun c _ => by rw [crossEntropy_eq (hq c)]; ring

/-! ## Selection -/

/-- **Error decomposition.** If the empirical risk is within `g` of the population risk
everywhere and `ψ̂` minimises it to within `ε`, then `ψ̂` is within `2g + ε` of every
candidate, in particular of the best one in the class. -/
theorem erm_bound {Ψ : Type*} (R Rh : Ψ → ℝ) {g ε : ℝ} (hg : ∀ ψ, |Rh ψ - R ψ| ≤ g)
    {ψh : Ψ} (hopt : ∀ ψ, Rh ψh ≤ Rh ψ + ε) (ψ : Ψ) : R ψh ≤ R ψ + 2 * g + ε := by
  have h1 := abs_le.mp (hg ψh)
  have h2 := abs_le.mp (hg ψ)
  linarith [hopt ψ]

/-- **Calibrated measurement.** Conditional on a fixed representation, write population
risk as irreducible target uncertainty `I` plus readout approximation error `A ψ`.
Uniform empirical discrepancy and approximate fitting then give the class-level bound.
The projection identity establishing this decomposition is proved in `Recovery`.
This deterministic result imposes no independence assumption on the financial sample. -/
theorem calibrated_measurement_bound {Ψ : Type*} [Nonempty Ψ]
    (R Rh A : Ψ → ℝ) (I : ℝ) {g ε : ℝ}
    (hdecomp : ∀ ψ, R ψ = I + A ψ)
    (hg : ∀ ψ, |Rh ψ - R ψ| ≤ g)
    {ψh : Ψ} (hopt : ∀ ψ, Rh ψh ≤ Rh ψ + ε) :
    R ψh ≤ I + sInf (Set.range A) + 2 * g + ε := by
  have hlower : R ψh - I - 2 * g - ε ≤ sInf (Set.range A) := by
    apply le_csInf (Set.range_nonempty A)
    rintro _ ⟨ψ, rfl⟩
    have h := erm_bound R Rh hg hopt ψ
    rw [hdecomp ψ] at h
    linarith
  linarith

end FreeFoundations.Score
