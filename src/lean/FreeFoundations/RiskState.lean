module

public import Mathlib.Order.Setoid.Basic
public import FreeFoundations.Likelihood

@[expose] public section

/-!
# The state relevant to common-shock proximity

A declared linear risk-scaling map `L` sends structural exposures `b(s)` to common-risk
exposures. The distance is a pseudometric on states: it identifies the kernel classes of
`L`, rather than necessarily identifying structural exposures or the entire state.
In the economic application `L` is the square root of the declared shock covariance.
No existence, estimation, or identification of that covariance is assumed to be proved here.

Equal common exposures also do not determine total return covariance: the idiosyncratic
variances in `Likelihood.moment` remain necessary.
-/

namespace FreeFoundations.RiskState

variable {S V E : Type*} [AddCommGroup V] [Module ℝ V]
  [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- The common-risk exposure relevant to the declared shock system. -/
def exposure (L : V →ₗ[ℝ] E) (b : S → V) : S → E := fun s => L (b s)

/-- Common-shock dissimilarity, which can vanish between distinct states. -/
def distance (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) : ℝ :=
  dist (exposure L b s) (exposure L b t)

/-- States are equivalent precisely when their risk-scaled exposures agree. -/
def riskSetoid (L : V →ₗ[ℝ] E) (b : S → V) : Setoid S :=
  Setoid.ker (exposure L b)

theorem equivalent_iff (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) :
    (riskSetoid L b).r s t ↔ exposure L b s = exposure L b t := Iff.rfl

theorem distance_nonneg (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) :
    0 ≤ distance L b s t := dist_nonneg

theorem distance_self (L : V →ₗ[ℝ] E) (b : S → V) (s : S) :
    distance L b s s = 0 := dist_self _

theorem distance_comm (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) :
    distance L b s t = distance L b t s := dist_comm _ _

theorem distance_triangle (L : V →ₗ[ℝ] E) (b : S → V) (s t u : S) :
    distance L b s u ≤ distance L b s t + distance L b t u := dist_triangle _ _ _

theorem distance_eq_zero_iff (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) :
    distance L b s t = 0 ↔ (riskSetoid L b).r s t := dist_eq_zero

/-- Zero common-risk distance identifies exposure differences in the scaling map's kernel. -/
theorem distance_eq_zero_iff_mem_ker (L : V →ₗ[ℝ] E) (b : S → V) (s t : S) :
    distance L b s t = 0 ↔ b s - b t ∈ LinearMap.ker L := by
  rw [distance_eq_zero_iff, equivalent_iff]
  change L (b s) = L (b t) ↔ L (b s - b t) = 0
  rw [map_sub, sub_eq_zero]

/-- Distance separates entire states exactly when their common-risk exposure map is injective. -/
theorem separates_states_iff (L : V →ₗ[ℝ] E) (b : S → V) :
    (∀ s t, distance L b s t = 0 → s = t) ↔ Function.Injective (exposure L b) := by
  constructor
  · intro h s t heq
    exact h s t (dist_eq_zero.mpr heq)
  · intro h s t hzero
    exact h (dist_eq_zero.mp hzero)

/-- Changing either representative within its risk class does not change distance. -/
theorem distance_representatives (L : V →ₗ[ℝ] E) (b : S → V) {s s' t t' : S}
    (hs : (riskSetoid L b).r s s') (ht : (riskSetoid L b).r t t') :
    distance L b s t = distance L b s' t' := by
  change dist (exposure L b s) (exposure L b t) =
    dist (exposure L b s') (exposure L b t')
  rw [(equivalent_iff L b s s').mp hs, (equivalent_iff L b t t').mp ht]

/-- The exposure map on risk classes is injective; the quotient retains exactly these exposures. -/
def quotientExposure (L : V →ₗ[ℝ] E) (b : S → V) : Quotient (riskSetoid L b) → E :=
  Setoid.kerLift (exposure L b)

theorem quotientExposure_injective (L : V →ₗ[ℝ] E) (b : S → V) :
    Function.Injective (quotientExposure L b) := Setoid.kerLift_injective _

/-- With a singular scaling map, different structural exposures can have zero risk distance. -/
theorem singular_scaling_example :
    distance (LinearMap.fst ℝ ℝ ℝ) id (0, 0) (0, 1) = 0 ∧
      (0, 0) ≠ ((0, 1) : ℝ × ℝ) := by
  constructor <;> norm_num [distance, exposure]

section TotalCovariance

variable {n : Type*} [DecidableEq n]
variable {A : Type*} [NormedAddCommGroup A] [InnerProductSpace ℝ A]

/-- Even with common exposures fixed, total covariance agrees only when idiosyncratic
variances agree. This is not a statement that exposures determine the full return law. -/
theorem moment_eq_iff (a : n → A) (η η' : n → ℝ) :
    Likelihood.moment a η = Likelihood.moment a η' ↔ η = η' := by
  constructor
  · intro h
    funext i
    have hii := congrFun (congrFun h i) i
    simpa [Likelihood.moment] using hii
  · rintro rfl
    rfl

/-- Identical zero common exposures can coexist with different total variances. -/
theorem same_exposures_different_total_covariance :
    Likelihood.moment (fun _ : Fin 1 => (0 : ℝ)) (fun _ => 1) ≠
      Likelihood.moment (fun _ : Fin 1 => (0 : ℝ)) (fun _ => 4) := by
  intro h
  have hη := (moment_eq_iff (fun _ : Fin 1 => (0 : ℝ)) (fun _ => 1) (fun _ => 4)).mp h
  have := congrFun hη 0
  norm_num at this

end TotalCovariance

end FreeFoundations.RiskState
