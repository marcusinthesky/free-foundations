import FreeFoundations.TaskInformation
import FreeFoundations.Transfer

/-!
# Finite task coverage by an explicit span certificate

A downstream economic loading in the span of training loadings has a computable
error multiplier: the Euclidean norm of its coefficient vector. This is a
linear-algebra condition on the tasks, rather than an assumption of the desired
downstream risk inequality. Missing economic directions remain unmeasured.
-/

noncomputable section

namespace FreeFoundations.TaskCoverage

open WithLp

variable {n t : Type*} [Fintype n] [Fintype t]

/-- An explicitly covered economic loading. Coefficients describe the actual span. -/
def coveredLoading (tasks : t → EuclideanSpace ℝ n) (coeff : EuclideanSpace ℝ t) :
    EuclideanSpace ℝ n := ∑ k, coeff k • tasks k

/-- The economic target is a linear combination of the training-task signals. -/
theorem covered_signal (tasks : t → EuclideanSpace ℝ n)
    (coeff : EuclideanSpace ℝ t) (a : EuclideanSpace ℝ n) :
    inner ℝ (coveredLoading tasks coeff) a =
      inner ℝ coeff (TaskInformation.taskOperator tasks (fun _ => 1) a) := by
  simp [coveredLoading, sum_inner, inner_smul_left, PiLp.inner_apply,
    TaskInformation.taskOperator, mul_comm]

/-- Task-span coverage with its explicit conditioning constant. -/
theorem covered_error (tasks : t → EuclideanSpace ℝ n)
    (coeff : EuclideanSpace ℝ t) (a ahat : EuclideanSpace ℝ n) :
    |inner ℝ (coveredLoading tasks coeff) ahat -
        inner ℝ (coveredLoading tasks coeff) a| ≤
      ‖coeff‖ * ‖TaskInformation.taskOperator tasks (fun _ => 1) (ahat - a)‖ := by
  rw [← inner_sub_right, covered_signal]
  exact abs_real_inner_le_norm _ _

/-- The same coefficient certificate applies to predicted task statistics directly. -/
theorem predicted_task_error (coeff : EuclideanSpace ℝ t)
    (prediction target : EuclideanSpace ℝ t) :
    |inner ℝ coeff prediction - inner ℝ coeff target| ≤ ‖coeff‖ * ‖prediction - target‖ := by
  rw [← inner_sub_right]
  exact abs_real_inner_le_norm _ _

end FreeFoundations.TaskCoverage
