module

public import Mathlib.Analysis.InnerProductSpace.PiL2
public import FreeFoundations.Recovery

@[expose] public section

/-!
# Neighbour sets: when an estimated geometry keeps the economic peers

Spatial networks in the application are k-nearest-neighbour graphs, so only the order of
each firm's distances matters. This module states when that order survives a
perturbation, and shows that a prediction-preserving reparametrisation can reverse it.

* `IsNeighbourSet d i S`: every member of `S` is strictly closer to firm `i` than every
  non-member other than `i`. Two such sets of equal size coincide
  (`neighbourSet_unique`), so the strict k-NN set is well defined.
* **Margin certificate** (`neighbourSet_stable`): if every member/non-member gap is at
  least `γ` and every distance moves by at most `ε` with `2ε < γ`, the neighbour set is
  unchanged. The factor two is sharp (`neighbourSet_margin_sharp`).
* **Exposure form** (`neighbourSet_of_exposures`): exposure errors `δⱼ ≤ δ` move row
  `i`'s distances by at most `δᵢ + δ` (`Recovery.distance_error`), so `γ > 2(δᵢ + δ)`
  suffices.
* **Reparametrisation form** (`neighbourSet_linear`): a linear map with norm bounds
  `σmin‖x‖ ≤ ‖g x‖ ≤ σmax‖x‖` keeps the set when `σmax dᵢⱼ < σmin dᵢₗ` for every member
  `j` and non-member `l`; the condition number must exceed the distance ratio to flip.
* **Flip** (`anisotropic_flip`): with `A = 0`, `B = (1, 0)` and `C = (0, 2)`, stretching
  the first coordinate by three makes `C`, not `B`, the nearer neighbour of `A`. Any
  readout `h` composed with the inverse stretch predicts exactly as before.

These are deterministic statements about given distances; they say nothing about how
well a fitted readout estimates exposures.
-/

namespace FreeFoundations.Neighbours

variable {ι : Type*}

/-- `S` is a strict neighbour set of firm `i` under row distances `d`. -/
def IsNeighbourSet (d : ι → ℝ) (i : ι) (S : Set ι) : Prop :=
  ∀ j ∈ S, ∀ l, l ∉ S → l ≠ i → d j < d l

/-- Every member/non-member gap in row `i` is at least `γ`. -/
def HasMargin (d : ι → ℝ) (i : ι) (S : Set ι) (γ : ℝ) : Prop :=
  ∀ j ∈ S, ∀ l, l ∉ S → l ≠ i → γ ≤ d l - d j

/-- Two strict neighbour sets of the same finite size that omit `i` are equal. -/
theorem neighbourSet_unique [DecidableEq ι] {d : ι → ℝ} {i : ι} {S T : Finset ι}
    (hS : IsNeighbourSet d i (S : Set ι)) (hT : IsNeighbourSet d i (T : Set ι))
    (hiS : i ∉ S) (hiT : i ∉ T) (hcard : S.card = T.card) : S = T := by
  by_contra hne
  have hTS : ¬ T ⊆ S := fun h => hne (Finset.eq_of_subset_of_card_le h hcard.le).symm
  have hST : ¬ S ⊆ T := fun h => hne (Finset.eq_of_subset_of_card_le h hcard.ge)
  obtain ⟨l, hlT, hlS⟩ := Finset.not_subset.mp hTS
  obtain ⟨j, hjS, hjT⟩ := Finset.not_subset.mp hST
  have hli : l ≠ i := fun h => hiT (h ▸ hlT)
  have hji : j ≠ i := fun h => hiS (h ▸ hjS)
  have h1 := hS j (by simpa using hjS) l (by simpa using hlS) hli
  have h2 := hT l (by simpa using hlT) j (by simpa using hjT) hji
  linarith

/-- **Margin certificate.** Perturbations below half the margin keep the neighbour set. -/
theorem neighbourSet_stable {d d' : ι → ℝ} {i : ι} {S : Set ι} {γ ε : ℝ}
    (hm : HasMargin d i S γ) (herr : ∀ j, |d' j - d j| ≤ ε) (hε : 2 * ε < γ) :
    IsNeighbourSet d' i S := by
  intro j hj l hl hli
  have h1 := hm j hj l hl hli
  have h2 := abs_le.mp (herr j)
  have h3 := abs_le.mp (herr l)
  linarith [h2.1, h2.2, h3.1, h3.2]

/-- **Sharpness.** At margin exactly `2ε` (here `ε = 1`) a perturbation of size `ε` can
break the strict neighbour set: row distances `(0, 1, 3)` move to `(0, 2, 2)`. -/
theorem neighbourSet_margin_sharp :
    HasMargin ![(0 : ℝ), 1, 3] 0 {1} 2 ∧
      (∀ j, |![(0 : ℝ), 2, 2] j - ![(0 : ℝ), 1, 3] j| ≤ 1) ∧
        ¬ IsNeighbourSet ![(0 : ℝ), 2, 2] 0 {1} := by
  refine ⟨?_, ?_, ?_⟩
  · intro j hj l hl hli
    simp only [Set.mem_singleton_iff] at hj hl
    subst hj
    fin_cases l <;> simp_all
    norm_num
  · intro j
    fin_cases j <;> norm_num
  · intro h
    have := h 1 rfl 2 (by simp) (by decide)
    norm_num at this

variable {A : Type*} [NormedAddCommGroup A]

/-- **Exposure form.** Exposure errors `‖âⱼ - aⱼ‖ ≤ δⱼ ≤ δ` keep row `i`'s economic
neighbour set when its margin exceeds `2(δᵢ + δ)`. -/
theorem neighbourSet_of_exposures {a ah : ι → A} {δ : ι → ℝ} {δmax γ : ℝ} {i : ι}
    {S : Set ι} (hm : HasMargin (fun j => ‖a i - a j‖) i S γ)
    (herr : ∀ j, ‖ah j - a j‖ ≤ δ j) (hmax : ∀ j, δ j ≤ δmax)
    (hγ : 2 * (δ i + δmax) < γ) :
    IsNeighbourSet (fun j => ‖ah i - ah j‖) i S := by
  refine neighbourSet_stable hm (fun j => ?_) hγ
  calc |‖ah i - ah j‖ - ‖a i - a j‖| ≤ ‖ah i - a i‖ + ‖ah j - a j‖ :=
        Recovery.distance_error _ _ _ _
    _ ≤ δ i + δmax := add_le_add (herr i) ((herr j).trans (hmax j))

/-- **Checkable form.** The same certificate read from estimated distances: if the
estimated row has margin above `2(δᵢ + δ)`, its neighbour set is the economic one. -/
theorem neighbourSet_of_estimated_margin {a ah : ι → A} {δ : ι → ℝ} {δmax γ : ℝ}
    {i : ι} {S : Set ι} (hm : HasMargin (fun j => ‖ah i - ah j‖) i S γ)
    (herr : ∀ j, ‖ah j - a j‖ ≤ δ j) (hmax : ∀ j, δ j ≤ δmax)
    (hγ : 2 * (δ i + δmax) < γ) :
    IsNeighbourSet (fun j => ‖a i - a j‖) i S := by
  refine neighbourSet_stable hm (fun j => ?_) hγ
  calc |‖a i - a j‖ - ‖ah i - ah j‖| = |‖ah i - ah j‖ - ‖a i - a j‖| := abs_sub_comm _ _
    _ ≤ ‖ah i - a i‖ + ‖ah j - a j‖ := Recovery.distance_error _ _ _ _
    _ ≤ δ i + δmax := add_le_add (herr i) ((herr j).trans (hmax j))

/-- **Reparametrisation form.** A linear map keeps the neighbour set when its largest
stretch times each member distance stays below its smallest stretch times each
non-member distance. -/
theorem neighbourSet_linear [Module ℝ A] (g : A →ₗ[ℝ] A) {z : ι → A} {σmin σmax : ℝ}
    {i : ι} {S : Set ι} (hlo : ∀ x, σmin * ‖x‖ ≤ ‖g x‖) (hhi : ∀ x, ‖g x‖ ≤ σmax * ‖x‖)
    (hratio : ∀ j ∈ S, ∀ l, l ∉ S → l ≠ i → σmax * ‖z i - z j‖ < σmin * ‖z i - z l‖) :
    IsNeighbourSet (fun j => ‖g (z i) - g (z j)‖) i S := by
  intro j hj l hl hli
  simp only [← map_sub]
  calc ‖g (z i - z j)‖ ≤ σmax * ‖z i - z j‖ := hhi _
    _ < σmin * ‖z i - z l‖ := hratio j hj l hl hli
    _ ≤ ‖g (z i - z l)‖ := hlo _

/-- The plane with the Euclidean norm. -/
abbrev Plane := EuclideanSpace ℝ (Fin 2)

/-- The anisotropic stretch `diag(3, 1)`. -/
noncomputable def stretch : Plane →ₗ[ℝ] Plane :=
  (WithLp.linearEquiv 2 ℝ (Fin 2 → ℝ)).symm.toLinearMap ∘ₗ
    Matrix.toLin' !![(3 : ℝ), 0; 0, 1] ∘ₗ (WithLp.linearEquiv 2 ℝ (Fin 2 → ℝ)).toLinearMap

/-- **Flip.** `B = (1, 0)` is nearer to the origin than `C = (0, 2)`, but after the stretch
`diag(3, 1)` the order reverses. -/
theorem anisotropic_flip :
    ‖(!₂[(1 : ℝ), 0] : Plane)‖ < ‖(!₂[(0 : ℝ), 2] : Plane)‖ ∧
      ‖stretch !₂[(0 : ℝ), 2]‖ < ‖stretch !₂[(1 : ℝ), 0]‖ := by
  have hB : stretch !₂[(1 : ℝ), 0] = !₂[(3 : ℝ), 0] := by
    ext k; fin_cases k <;> simp [stretch]
  have hC : stretch !₂[(0 : ℝ), 2] = !₂[(0 : ℝ), 2] := by
    ext k; fin_cases k <;> simp [stretch]
  rw [hB, hC]
  simp only [EuclideanSpace.norm_eq, Fin.sum_univ_two]
  constructor <;> apply Real.sqrt_lt_sqrt <;> norm_num

/-- Composing any readout with the inverse stretch reproduces its predictions, so the
flip changes geometry without changing predictive content. -/
theorem stretch_predictions {Y : Type*} (e : Plane ≃ₗ[ℝ] Plane) (h : Plane → Y) (z : Plane) :
    (h ∘ e.symm) (e z) = h z := by
  simp

end FreeFoundations.Neighbours
