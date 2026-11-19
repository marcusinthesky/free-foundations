import FreeFoundations
import FreeFoundationsApi.Check

/-!
# Manuscript-facing public type contracts

Frozen from the reviewed theory at commit `9713a8d`, then elaborated and checked
independently of the declarations under test. These are complete type contracts,
not proofs obtained by applying the theorem. Do not regenerate them during builds.
Changing a contract requires review of the corresponding manuscript/blueprint claim.
-/

open MeasureTheory
open scoped Matrix.Norms.L2Operator MatrixOrder
set_option maxRecDepth 4096
set_option maxHeartbeats 800000
-- The complete public telescope intentionally retains unused parameters.
set_option linter.unusedVariables false

section Contract0
universe u
#assert_signature FreeFoundations.Alignment.Optimal [u] :
  {H T R : Type u} → (H → T) → (H → R) → Prop
end Contract0

section Contract1
universe u
#assert_signature FreeFoundations.Alignment.Sufficient [u] :
  {H S R : Type u} → (H → S) → (H → R) → Prop
end Contract1

section Contract2
universe u
#assert_signature FreeFoundations.Alignment.constant_target_loses_state [u] :
  ∀ {H T S : Type u} (F : H → T) (state : H → S),
    (∀ (h h' : H), F h = F h') →
      ∀ {h₀ h₁ : H},
        state h₀ ≠ state h₁ →
          (FreeFoundations.Alignment.Optimal F fun (x : H) => PUnit.unit) ∧
            ¬FreeFoundations.Alignment.Sufficient state fun (x : H) => PUnit.unit
end Contract2

section Contract3
#assert_signature FreeFoundations.Alignment.joint_depends_on_state [] :
  (FreeFoundations.Alignment.pair Bool.false) (Bool.true, Bool.true) = (1 / 2 : ENNReal) ∧
    (FreeFoundations.Alignment.pair Bool.true) (Bool.true, Bool.true) = (0 : ENNReal)
end Contract3

section Contract4
#assert_signature FreeFoundations.Alignment.marginals_free_of_state [] :
  ∀ (s : Bool),
    PMF.map Prod.fst (FreeFoundations.Alignment.pair s) = FreeFoundations.Alignment.fairCoin ∧
      PMF.map Prod.snd (FreeFoundations.Alignment.pair s) = FreeFoundations.Alignment.fairCoin
end Contract4

section Contract5
universe u
#assert_signature FreeFoundations.Alignment.optimal_imp_sufficient_iff [u] :
  ∀ {H T S : Type u} [Nonempty S] (F : H → T) (state : H → S),
    (∀ (R : Type u) (Z : H → R), FreeFoundations.Alignment.Optimal F Z → FreeFoundations.Alignment.Sufficient state Z) ↔
      ∀ (h h' : H), F h = F h' → state h = state h'
end Contract5

section Contract6
#assert_signature FreeFoundations.Alignment.pair [] :
  Bool → PMF (Bool × Bool)
end Contract6

section Contract7
universe u
#assert_signature FreeFoundations.Alignment.state_optimal_iff [u] :
  ∀ {H T S : Type u} [Nonempty T] (F : H → T) (state : H → S),
    (∃ (d : S → T), F = d ∘ state) ↔ ∀ (h h' : H), state h = state h' → F h = F h'
end Contract7

section Contract8
universe u_1
#assert_signature FreeFoundations.Bandwidth.effectiveNeighbors_monotoneOn [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s → ∀ (d : ι → ℝ), MonotoneOn (FreeFoundations.Bandwidth.effectiveNeighbors s d) (Set.Ioi (0 : ℝ))
end Contract8

section Contract9
universe u_1
#assert_signature FreeFoundations.Bandwidth.expRow_tendsto_atTop [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) (i : ι),
        Filter.Tendsto (fun (h : ℝ) => FreeFoundations.Kernel.expRow s d h i) Filter.atTop
          (nhds ((1 : ℝ) / ↑(Finset.card s)))
end Contract9

section Contract10
universe u_1
#assert_signature FreeFoundations.Bandwidth.expRow_tendsto_zero [u_1] :
  ∀ {ι : Type u_1} [DecidableEq ι] (s : Finset ι) (d : ι → ℝ) (m : ℝ),
    (∀ j ∈ s, m ≤ d j) →
      (∃ j ∈ s, d j = m) →
        ∀ {i : ι},
          i ∈ s →
            Filter.Tendsto (fun (h : ℝ) => FreeFoundations.Kernel.expRow s d h i) (nhdsWithin (0 : ℝ) (Set.Ioi (0 : ℝ)))
              (nhds ((if d i = m then (1 : ℝ) else (0 : ℝ)) / ↑(Finset.card ({j ∈ s | d j = m}))))
end Contract10

section Contract11
universe u_1
#assert_signature FreeFoundations.Bandwidth.hasDerivAt_entropy [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) {h : ℝ},
        h ≠ (0 : ℝ) →
          HasDerivAt (FreeFoundations.Bandwidth.entropy s d)
            (FreeFoundations.Bandwidth.distanceVariance s d h / h ^ (3 : ℕ)) h
end Contract11

section Contract12
universe u_1
#assert_signature FreeFoundations.Bandwidth.hasDerivAt_expRow [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) {h : ℝ},
        h ≠ (0 : ℝ) →
          ∀ (j : ι),
            HasDerivAt (fun (u : ℝ) => FreeFoundations.Kernel.expRow s d u j)
              (FreeFoundations.Kernel.expRow s d h j * (d j - FreeFoundations.Bandwidth.meanDistance s d h) / h ^ (2 : ℕ))
              h
end Contract12

section Contract13
universe u_1
#assert_signature FreeFoundations.Bandwidth.hasDerivAt_meanDistance [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) {h : ℝ},
        h ≠ (0 : ℝ) →
          HasDerivAt (FreeFoundations.Bandwidth.meanDistance s d)
            (FreeFoundations.Bandwidth.distanceVariance s d h / h ^ (2 : ℕ)) h
end Contract13

section Contract14
universe u_1
#assert_signature FreeFoundations.Bandwidth.herfindahl_antitoneOn [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s → ∀ (d : ι → ℝ), AntitoneOn (FreeFoundations.Bandwidth.herfindahl s d) (Set.Ioi (0 : ℝ))
end Contract14

section Contract15
#assert_signature FreeFoundations.Bandwidth.matched_effective_not_concentration [] :
  ((1 : ℝ) / (1 / 2 : ℝ) + (1 : ℝ) / (1 / 2 : ℝ)) / (2 : ℝ) = ((1 : ℝ) / (3 / 4 : ℝ) + (1 : ℝ) / (3 / 8 : ℝ)) / (2 : ℝ) ∧
    ((1 / 2 : ℝ) + (1 / 2 : ℝ)) / (2 : ℝ) ≠ ((3 / 4 : ℝ) + (3 / 8 : ℝ)) / (2 : ℝ)
end Contract15

section Contract16
#assert_signature FreeFoundations.ComparativeStatics.swap_covariance_common [] :
  ∀ {c : ℝ},
    |c| < (1 : ℝ) →
      Matrix.mulVec (FreeFoundations.ComparativeStatics.swapCovariance c)
          FreeFoundations.ComparativeStatics.commonDirection =
        ((1 : ℝ) - c)⁻¹ ^ (2 : ℕ) • FreeFoundations.ComparativeStatics.commonDirection
end Contract16

section Contract17
#assert_signature FreeFoundations.ComparativeStatics.swap_covariance_not_ge_identity [] :
  ∀ {c : ℝ},
    (0 : ℝ) < c →
      c < (1 : ℝ) →
        ¬Matrix.PosSemidef
            (FreeFoundations.ComparativeStatics.swapCovariance c - (1 : Matrix (Fin (2 : ℕ)) (Fin (2 : ℕ)) ℝ))
end Contract17

section Contract18
#assert_signature FreeFoundations.ComparativeStatics.swap_covariance_spread [] :
  ∀ {c : ℝ},
    |c| < (1 : ℝ) →
      Matrix.mulVec (FreeFoundations.ComparativeStatics.swapCovariance c)
          FreeFoundations.ComparativeStatics.spreadDirection =
        ((1 : ℝ) + c)⁻¹ ^ (2 : ℕ) • FreeFoundations.ComparativeStatics.spreadDirection
end Contract18

section Contract19
universe u_1 u_2 u_3 u_4
#assert_signature FreeFoundations.Decision.approximate_sufficiency [u_1, u_2, u_3, u_4] :
  ∀ {Θ : Type u_1} {X : Type u_2} {Z : Type u_3} {A : Type u_4} [inst : Fintype Θ] [inst_1 : Fintype X]
    [inst_2 : Fintype Z] [inst_3 : Fintype A] [inst_4 : Nonempty A] (π : Θ → ℝ),
    (∀ (θ : Θ), (0 : ℝ) ≤ π θ) →
      ∀ (ℓ : Θ → A → ℝ),
        (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ ℓ θ a ∧ ℓ θ a ≤ (1 : ℝ)) →
          ∀ {P : Θ → X → ℝ} {G : X → Z → ℝ} {D : Z → X → ℝ},
            FreeFoundations.Decision.Stochastic P →
              FreeFoundations.Decision.Stochastic G →
                FreeFoundations.Decision.Stochastic D →
                  ∀ {ε : ℝ},
                    ∑ θ : Θ,
                          π θ *
                            ((∑ x : X,
                                |FreeFoundations.Decision.compose (FreeFoundations.Decision.compose P G) D θ x - P θ x|) /
                              (2 : ℝ)) ≤
                        ε →
                      (0 : ℝ) ≤
                          FreeFoundations.Decision.bayesRisk π ℓ (FreeFoundations.Decision.compose P G) -
                            FreeFoundations.Decision.bayesRisk π ℓ P ∧
                        FreeFoundations.Decision.bayesRisk π ℓ (FreeFoundations.Decision.compose P G) -
                            FreeFoundations.Decision.bayesRisk π ℓ P ≤
                          ε
end Contract19

section Contract20
universe u_1 u_2 u_4
#assert_signature FreeFoundations.Decision.bayes_risk_tv [u_1, u_2, u_4] :
  ∀ {Θ : Type u_1} {X : Type u_2} {A : Type u_4} [inst : Fintype Θ] [inst_1 : Fintype X] [inst_2 : Fintype A]
    [inst_3 : Nonempty A] (π : Θ → ℝ),
    (∀ (θ : Θ), (0 : ℝ) ≤ π θ) →
      ∀ (ℓ : Θ → A → ℝ),
        (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ ℓ θ a ∧ ℓ θ a ≤ (1 : ℝ)) →
          ∀ (P Q : Θ → X → ℝ),
            (∀ (θ : Θ), ∑ x : X, P θ x = ∑ x : X, Q θ x) →
              FreeFoundations.Decision.bayesRisk π ℓ P ≤
                FreeFoundations.Decision.bayesRisk π ℓ Q + ∑ θ : Θ, π θ * ((∑ x : X, |P θ x - Q θ x|) / (2 : ℝ))
end Contract20

section Contract21
universe u_1 u_2 u_4
#assert_signature FreeFoundations.Decision.fixed_policy_tv [u_1, u_2, u_4] :
  ∀ {Θ : Type u_1} {X : Type u_2} {A : Type u_4} [inst : Fintype Θ] [inst_1 : Fintype X] (π : Θ → ℝ),
    (∀ (θ : Θ), (0 : ℝ) ≤ π θ) →
      ∀ (ℓ : Θ → A → ℝ),
        (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ ℓ θ a ∧ ℓ θ a ≤ (1 : ℝ)) →
          ∀ (P Q : Θ → X → ℝ),
            (∀ (θ : Θ), ∑ x : X, P θ x = ∑ x : X, Q θ x) →
              ∀ (f : X → A),
                |∑ x : X, FreeFoundations.Decision.cost π ℓ P x (f x) -
                      ∑ x : X, FreeFoundations.Decision.cost π ℓ Q x (f x)| ≤
                  ∑ θ : Θ, π θ * ((∑ x : X, |P θ x - Q θ x|) / (2 : ℝ))
end Contract21

section Contract22
universe u_1 u_2 u_3 u_4
#assert_signature FreeFoundations.Decision.garbling_risk [u_1, u_2, u_3, u_4] :
  ∀ {Θ : Type u_1} {X : Type u_2} {Z : Type u_3} {A : Type u_4} [inst : Fintype Θ] [inst_1 : Fintype X]
    [inst_2 : Fintype Z] [inst_3 : Fintype A] [inst_4 : Nonempty A] (π : Θ → ℝ) (ℓ : Θ → A → ℝ) (P : Θ → X → ℝ)
    {G : X → Z → ℝ},
    FreeFoundations.Decision.Stochastic G →
      FreeFoundations.Decision.bayesRisk π ℓ P ≤
        FreeFoundations.Decision.bayesRisk π ℓ (FreeFoundations.Decision.compose P G)
end Contract22

section Contract23
universe u_1 u_2
#assert_signature FreeFoundations.Dynamics.gramian_mono [u_1, u_2] :
  ∀ {n : Type u_1} {m : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n] [inst_2 : Fintype m] (H : ℕ)
    (C : Matrix m n ℝ) (F : Matrix n n ℝ),
    FreeFoundations.Dynamics.gramian H C F ≤ FreeFoundations.Dynamics.gramian (H + (1 : ℕ)) C F
end Contract23

section Contract24
universe u_1 u_2
#assert_signature FreeFoundations.Dynamics.gramian_succ [u_1, u_2] :
  ∀ {n : Type u_1} {m : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n] [inst_2 : Fintype m] (H : ℕ)
    (C : Matrix m n ℝ) (F : Matrix n n ℝ),
    FreeFoundations.Dynamics.gramian (H + (1 : ℕ)) C F =
      FreeFoundations.Dynamics.gramian H C F + Matrix.transpose (C * F ^ H) * (C * F ^ H)
end Contract24

section Contract25
universe u_1 u_2
#assert_signature FreeFoundations.Dynamics.observable_decoder [u_1, u_2] :
  ∀ {n : Type u_1} {m : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n] [inst_2 : Fintype m] (H : ℕ)
    (C : Matrix m n ℝ) (F : Matrix n n ℝ) {κ : ℝ},
    (0 : ℝ) < κ →
      FreeFoundations.Recovery.Distinguishes (Matrix.toEuclideanLin (FreeFoundations.Dynamics.observation H C F)) κ →
        ∃ (L : EuclideanSpace ℝ (Fin H × m) →ₗ[ℝ] EuclideanSpace ℝ n),
          FreeFoundations.Recovery.Decoder (Matrix.toEuclideanLin (FreeFoundations.Dynamics.observation H C F)) κ L
end Contract25

section Contract26
universe u_1 u_2
#assert_signature FreeFoundations.Dynamics.observation_gram [u_1, u_2] :
  ∀ {n : Type u_1} {m : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n] [inst_2 : Fintype m] (H : ℕ)
    (C : Matrix m n ℝ) (F : Matrix n n ℝ),
    Matrix.transpose (FreeFoundations.Dynamics.observation H C F) * FreeFoundations.Dynamics.observation H C F =
      FreeFoundations.Dynamics.gramian H C F
end Contract26

section Contract27
#assert_signature FreeFoundations.Dynamics.one_horizon_not_injective [] :
  ¬Function.Injective fun (a : EuclideanSpace ℝ (Fin (2 : ℕ))) =>
      Matrix.mulVec FreeFoundations.Dynamics.firstCoordinate (WithLp.ofLp a) (0 : Fin (1 : ℕ))
end Contract27

section Contract28
#assert_signature FreeFoundations.Dynamics.two_horizons [] :
  ∀ (a : EuclideanSpace ℝ (Fin (2 : ℕ))),
    Matrix.mulVec (FreeFoundations.Dynamics.firstCoordinate * FreeFoundations.Dynamics.swap ^ (0 : ℕ)) (WithLp.ofLp a)
          (0 : Fin (1 : ℕ)) =
        WithLp.ofLp a (0 : Fin (2 : ℕ)) ∧
      Matrix.mulVec (FreeFoundations.Dynamics.firstCoordinate * FreeFoundations.Dynamics.swap ^ (1 : ℕ)) (WithLp.ofLp a)
          (0 : Fin (1 : ℕ)) =
        WithLp.ofLp a (1 : Fin (2 : ℕ))
end Contract28

section Contract29
#assert_signature FreeFoundations.Dynamics.two_horizons_distinguish [] :
  FreeFoundations.Recovery.Distinguishes
    (Matrix.toEuclideanLin
      (FreeFoundations.Dynamics.observation (2 : ℕ) FreeFoundations.Dynamics.firstCoordinate
        FreeFoundations.Dynamics.swap))
    (1 : ℝ)
end Contract29

section Contract30
universe u_1
#assert_signature FreeFoundations.EndToEnd.common_component_error [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (F S T : Matrix n n ℝ), ‖F + S - (F + T)‖ = ‖S - T‖
end Contract30

section Contract31
universe u_1
#assert_signature FreeFoundations.EndToEnd.covariance_from_scaled [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (d dh D Dh T : Matrix n n ℝ) {h hh b c ch M V ec BW eD ρ : ℝ},
        (0 : ℝ) ≤ b →
          (∀ (i j : n), i ≠ j → |dh i j / hh - d i j / h| ≤ b) →
            IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • FreeFoundations.Kernel.expKernel d h)) →
              IsUnit (Matrix.det ((1 : Matrix n n ℝ) - ch • FreeFoundations.Kernel.expKernel dh hh)) →
                ‖((1 : Matrix n n ℝ) - c • FreeFoundations.Kernel.expKernel d h)⁻¹‖ ≤ M →
                  ‖((1 : Matrix n n ℝ) - ch • FreeFoundations.Kernel.expKernel dh hh)⁻¹‖ ≤ M →
                    ‖D‖ ≤ V →
                      |ch - c| ≤ ec →
                        ‖FreeFoundations.Kernel.expKernel dh hh‖ ≤ BW →
                          ‖D - Dh‖ ≤ eD →
                            ‖FreeFoundations.EndToEnd.spatial (FreeFoundations.Kernel.expKernel d h) c D - T‖ ≤ ρ →
                              ‖FreeFoundations.EndToEnd.spatial (FreeFoundations.Kernel.expKernel dh hh) ch Dh - T‖ ≤
                                FreeFoundations.EndToEnd.covarianceError (Fintype.card n) b V M c ec BW eD ρ
end Contract31

section Contract32
universe u_1 u_2
#assert_signature FreeFoundations.EndToEnd.empirical_rms_scaled [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {A : Type u_2} [inst_1 : NormedAddCommGroup A] [InnerProductSpace ℝ A]
    (a ah : n → A) {B h : ℝ},
    (0 : ℝ) ≤ B →
      (0 : ℝ) < h →
        ∑ i : n, ‖ah i - a i‖ ^ (2 : ℕ) ≤ ↑(Fintype.card n) * B ^ (2 : ℕ) →
          ∀ (i j : n),
            |FreeFoundations.EndToEnd.distances ah i j / h - FreeFoundations.EndToEnd.distances a i j / h| ≤
              (2 : ℝ) * (√↑(Fintype.card n) * B) / h
end Contract32

section Contract33
universe u_1 u_2
#assert_signature FreeFoundations.EndToEnd.exposure_scaled [u_1, u_2] :
  ∀ {n : Type u_1} {A : Type u_2} [inst : NormedAddCommGroup A] [InnerProductSpace ℝ A] (a ah : n → A) {e h : ℝ},
    (∀ (i : n), ‖ah i - a i‖ ≤ e) → (0 : ℝ) < h → ∀ (i j : n), |‖ah i - ah j‖ / h - ‖a i - a j‖ / h| ≤ (2 : ℝ) * e / h
end Contract33

section Contract34
universe u_1
#assert_signature FreeFoundations.EndToEnd.full_score_of_certificate [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (F S T : Matrix n n ℝ),
    Matrix.PosDef (F + S) →
      Matrix.PosDef (F + T) →
        ∀ {m e : ℝ},
          (0 : ℝ) < m →
            Matrix.PosSemidef (F + S - m • (1 : Matrix n n ℝ)) →
              ‖S - T‖ ≤ e →
                e < m →
                  (0 : ℝ) ≤ FreeFoundations.Score.loss (F + S) (F + T) - FreeFoundations.Score.loss (F + T) (F + T) ∧
                    FreeFoundations.Score.loss (F + S) (F + T) - FreeFoundations.Score.loss (F + T) (F + T) ≤
                      ↑(Fintype.card n) * (e / m) ^ (2 : ℕ) / ((2 : ℝ) * ((1 : ℝ) - e / m))
end Contract34

section Contract35
universe u_1
#assert_signature FreeFoundations.EndToEnd.gram_scaled [u_1] :
  ∀ {n : Type u_1} [Fintype n] [DecidableEq n] {G Gh : Matrix n n ℝ},
    Matrix.PosSemidef G →
      Matrix.PosSemidef Gh →
        ∀ {ε h : ℝ},
          (0 : ℝ) ≤ ε →
            (∀ (i j : n), |Gh i j - G i j| ≤ ε) →
              (0 : ℝ) < h →
                ∀ (i j : n),
                  |FreeFoundations.GramDistance.distance Gh i j / h - FreeFoundations.GramDistance.distance G i j / h| ≤
                    (2 : ℝ) * √ε / h
end Contract35

section Contract36
universe u_1
#assert_signature FreeFoundations.EndToEnd.kernel_spectral_scaled [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (d dh : Matrix n n ℝ) {h hh b : ℝ},
        (0 : ℝ) ≤ b →
          (∀ (i j : n), i ≠ j → |dh i j / hh - d i j / h| ≤ b) →
            ‖FreeFoundations.Kernel.expKernel dh hh - FreeFoundations.Kernel.expKernel d h‖ ≤
              √↑(Fintype.card n) * FreeFoundations.Kernel.sensitivity b
end Contract36

section Contract37
universe u_1 u_2
#assert_signature FreeFoundations.EndToEnd.measurement_to_finance [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A]
    [InnerProductSpace ℝ A],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (a ah : n → A) (D Dh T : Matrix n n ℝ) {e h c ch M V ec BW eD ρ m : ℝ},
        (0 : ℝ) ≤ e →
          (0 : ℝ) < h →
            (∀ (i : n), ‖ah i - a i‖ ≤ e) →
              IsUnit
                  (Matrix.det
                    ((1 : Matrix n n ℝ) -
                      c • FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances a) h)) →
                IsUnit
                    (Matrix.det
                      ((1 : Matrix n n ℝ) -
                        ch • FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h)) →
                  ‖((1 : Matrix n n ℝ) -
                            c • FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances a) h)⁻¹‖ ≤
                      M →
                    ‖((1 : Matrix n n ℝ) -
                              ch • FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h)⁻¹‖ ≤
                        M →
                      ‖D‖ ≤ V →
                        |ch - c| ≤ ec →
                          ‖FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h‖ ≤ BW →
                            ‖D - Dh‖ ≤ eD →
                              ‖FreeFoundations.EndToEnd.spatial
                                        (FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances a) h) c D -
                                      T‖ ≤
                                  ρ →
                                Matrix.PosDef
                                    (FreeFoundations.EndToEnd.spatial
                                      (FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h) ch
                                      Dh) →
                                  Matrix.PosDef T →
                                    (0 : ℝ) < m →
                                      Matrix.PosSemidef
                                          (FreeFoundations.EndToEnd.spatial
                                              (FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h)
                                              ch Dh -
                                            m • (1 : Matrix n n ℝ)) →
                                        FreeFoundations.EndToEnd.covarianceError (Fintype.card n) ((2 : ℝ) * e / h) V M c
                                              ec BW eD ρ <
                                            m →
                                          have S :=
                                            FreeFoundations.EndToEnd.spatial
                                              (FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances ah) h)
                                              ch Dh;
                                          have E :=
                                            FreeFoundations.EndToEnd.covarianceError (Fintype.card n) ((2 : ℝ) * e / h) V
                                              M c ec BW eD ρ;
                                          ‖S - T‖ ≤ E ∧
                                            (0 : ℝ) ≤ FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ∧
                                              FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ≤
                                                ↑(Fintype.card n) * (E / m) ^ (2 : ℕ) / ((2 : ℝ) * ((1 : ℝ) - E / m))
end Contract37

section Contract38
universe u_1
#assert_signature FreeFoundations.EndToEnd.score_of_certificate [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {S T : Matrix n n ℝ},
    Matrix.PosDef S →
      Matrix.PosDef T →
        ∀ {m e : ℝ},
          (0 : ℝ) < m →
            Matrix.PosSemidef (S - m • (1 : Matrix n n ℝ)) →
              ‖S - T‖ ≤ e →
                e < m →
                  (0 : ℝ) ≤ FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ∧
                    FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ≤
                      ↑(Fintype.card n) * (e / m) ^ (2 : ℕ) / ((2 : ℝ) * ((1 : ℝ) - e / m))
end Contract38

section Contract39
universe u_1 u_2 u_3
#assert_signature FreeFoundations.EndToEnd.task_exposure_certificate [u_1, u_2, u_3] :
  ∀ {n : Type u_1} {A : Type u_2} {T : Type u_3} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L →
      (0 : ℝ) < κ →
        ∀ (fitted : T → A) (a : n → A) (v pred : n → T) {ε ν εL B : ℝ},
          (0 : ℝ) ≤ εL →
            (∀ (y : T), ‖fitted y - L y‖ ≤ εL * ‖y‖) →
              (∀ (i : n), ‖pred i - (C (a i) + v i)‖ ≤ ε) →
                (∀ (i : n), ‖v i‖ ≤ ν) →
                  (∀ (i : n), ‖pred i‖ ≤ B) → ∀ (i : n), ‖fitted (pred i) - a i‖ ≤ (ε + ν) / κ + εL * B
end Contract39

section Contract40
universe u_1 u_2 u_3
#assert_signature FreeFoundations.EndToEnd.tasks_to_finance [u_1, u_2, u_3] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} {U : Type u_3}
    [inst_2 : NormedAddCommGroup A] [inst_3 : InnerProductSpace ℝ A] [inst_4 : NormedAddCommGroup U]
    [inst_5 : InnerProductSpace ℝ U],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ {C : A →ₗ[ℝ] U} {κ : ℝ} {L : U →ₗ[ℝ] A},
        FreeFoundations.Recovery.Decoder C κ L →
          (0 : ℝ) < κ →
            ∀ (fitted : U → A) (a : n → A) (v pred : n → U) {ε ν εL B : ℝ},
              (0 : ℝ) ≤ εL →
                (∀ (y : U), ‖fitted y - L y‖ ≤ εL * ‖y‖) →
                  (∀ (i : n), ‖pred i - (C (a i) + v i)‖ ≤ ε) →
                    (∀ (i : n), ‖v i‖ ≤ ν) →
                      (∀ (i : n), ‖pred i‖ ≤ B) →
                        ∀ (D Dh T : Matrix n n ℝ) {e h c ch M V ec BW eD ρ m : ℝ},
                          (0 : ℝ) ≤ e →
                            (0 : ℝ) < h →
                              e = (ε + ν) / κ + εL * B →
                                IsUnit
                                    (Matrix.det
                                      ((1 : Matrix n n ℝ) -
                                        c • FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances a) h)) →
                                  IsUnit
                                      (Matrix.det
                                        ((1 : Matrix n n ℝ) -
                                          ch •
                                            FreeFoundations.Kernel.expKernel
                                              (FreeFoundations.EndToEnd.distances fun (i : n) => fitted (pred i)) h)) →
                                    ‖((1 : Matrix n n ℝ) -
                                              c •
                                                FreeFoundations.Kernel.expKernel (FreeFoundations.EndToEnd.distances a)
                                                  h)⁻¹‖ ≤
                                        M →
                                      ‖((1 : Matrix n n ℝ) -
                                                ch •
                                                  FreeFoundations.Kernel.expKernel
                                                    (FreeFoundations.EndToEnd.distances fun (i : n) => fitted (pred i))
                                                    h)⁻¹‖ ≤
                                          M →
                                        ‖D‖ ≤ V →
                                          |ch - c| ≤ ec →
                                            ‖FreeFoundations.Kernel.expKernel
                                                    (FreeFoundations.EndToEnd.distances fun (i : n) => fitted (pred i))
                                                    h‖ ≤
                                                BW →
                                              ‖D - Dh‖ ≤ eD →
                                                ‖FreeFoundations.EndToEnd.spatial
                                                          (FreeFoundations.Kernel.expKernel
                                                            (FreeFoundations.EndToEnd.distances a) h)
                                                          c D -
                                                        T‖ ≤
                                                    ρ →
                                                  Matrix.PosDef
                                                      (FreeFoundations.EndToEnd.spatial
                                                        (FreeFoundations.Kernel.expKernel
                                                          (FreeFoundations.EndToEnd.distances fun (i : n) =>
                                                            fitted (pred i))
                                                          h)
                                                        ch Dh) →
                                                    Matrix.PosDef T →
                                                      (0 : ℝ) < m →
                                                        Matrix.PosSemidef
                                                            (FreeFoundations.EndToEnd.spatial
                                                                (FreeFoundations.Kernel.expKernel
                                                                  (FreeFoundations.EndToEnd.distances fun (i : n) =>
                                                                    fitted (pred i))
                                                                  h)
                                                                ch Dh -
                                                              m • (1 : Matrix n n ℝ)) →
                                                          FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                                                ((2 : ℝ) * e / h) V M c ec BW eD ρ <
                                                              m →
                                                            have S :=
                                                              FreeFoundations.EndToEnd.spatial
                                                                (FreeFoundations.Kernel.expKernel
                                                                  (FreeFoundations.EndToEnd.distances fun (i : n) =>
                                                                    fitted (pred i))
                                                                  h)
                                                                ch Dh;
                                                            have E :=
                                                              FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                                                ((2 : ℝ) * e / h) V M c ec BW eD ρ;
                                                            ‖S - T‖ ≤ E ∧
                                                              (0 : ℝ) ≤
                                                                  FreeFoundations.Score.loss S T -
                                                                    FreeFoundations.Score.loss T T ∧
                                                                FreeFoundations.Score.loss S T -
                                                                    FreeFoundations.Score.loss T T ≤
                                                                  ↑(Fintype.card n) * (E / m) ^ (2 : ℕ) /
                                                                    ((2 : ℝ) * ((1 : ℝ) - E / m))
end Contract40

section Contract41
universe u_1
#assert_signature FreeFoundations.Exposure.covariance_eq [u_1] :
  ∀ {k : Type u_1} [inst : Fintype k] (Ω : Matrix k k ℝ),
    Matrix.transpose Ω = Ω →
      ∀ (bᵢ bⱼ : k → ℝ),
        FreeFoundations.Exposure.form Ω bᵢ bⱼ =
          (FreeFoundations.Exposure.form Ω bᵢ bᵢ + FreeFoundations.Exposure.form Ω bⱼ bⱼ -
              FreeFoundations.Exposure.form Ω (bᵢ - bⱼ) (bᵢ - bⱼ)) /
            (2 : ℝ)
end Contract41

section Contract42
universe u_1
#assert_signature FreeFoundations.Exposure.form [u_1] :
  {k : Type u_1} → [Fintype k] → Matrix k k ℝ → (k → ℝ) → (k → ℝ) → ℝ
end Contract42

section Contract43
universe u_2
#assert_signature FreeFoundations.Exposure.inner_eq_half [u_2] :
  ∀ {E : Type u_2} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (aᵢ aⱼ : E),
    Inner.inner ℝ aᵢ aⱼ = (‖aᵢ‖ ^ (2 : ℕ) + ‖aⱼ‖ ^ (2 : ℕ) - ‖aᵢ - aⱼ‖ ^ (2 : ℕ)) / (2 : ℝ)
end Contract43

section Contract44
universe u_2
#assert_signature FreeFoundations.Exposure.pricing_error_lipschitz [u_2] :
  ∀ {E : Type u_2} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (aᵢ aⱼ g : E),
    |Inner.inner ℝ aᵢ g - Inner.inner ℝ aⱼ g| ≤ ‖aᵢ - aⱼ‖ * ‖g‖
end Contract44

section Contract45
universe u_1 u_2 u_3
#assert_signature FreeFoundations.GeneratedTarget.cross_moment_error [u_1, u_2, u_3] :
  ∀ {k : Type u_1} {n : Type u_2} {t : Type u_3} [inst : Fintype k] [inst_1 : DecidableEq k] [inst_2 : Fintype n]
    [inst_3 : DecidableEq n] [inst_4 : Fintype t] [DecidableEq t] (F Fh : Matrix t k ℝ) (Y Yh : Matrix t n ℝ) {eF eY : ℝ},
    ‖Fh - F‖ ≤ eF → ‖Yh - Y‖ ≤ eY → ‖Matrix.transpose Fh * Yh - Matrix.transpose F * Y‖ ≤ ‖Fh‖ * eY + eF * ‖Y‖
end Contract45

section Contract46
universe u_2 u_4
#assert_signature FreeFoundations.GeneratedTarget.exposure_gram_error [u_2, u_4] :
  ∀ {n : Type u_2} {A : Type u_4} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A] (a ah : n → A) {B e : ℝ},
    (0 : ℝ) ≤ B →
      (0 : ℝ) ≤ e →
        (∀ (i : n), ‖a i‖ ≤ B) →
          (∀ (i : n), ‖ah i - a i‖ ≤ e) →
            ∀ (i j : n), |Inner.inner ℝ (ah i) (ah j) - Inner.inner ℝ (a i) (a j)| ≤ (2 : ℝ) * B * e + e ^ (2 : ℕ)
end Contract46

section Contract47
universe u_1 u_3
#assert_signature FreeFoundations.GeneratedTarget.factor_gram_error [u_1, u_3] :
  ∀ {k : Type u_1} {t : Type u_3} [inst : Fintype k] [inst_1 : DecidableEq k] [inst_2 : Fintype t] [DecidableEq t]
    (F Fh : Matrix t k ℝ) {e : ℝ}, ‖Fh - F‖ ≤ e → ‖Matrix.transpose Fh * Fh - Matrix.transpose F * F‖ ≤ (‖Fh‖ + ‖F‖) * e
end Contract47

section Contract48
universe u_2 u_4
#assert_signature FreeFoundations.GeneratedTarget.generated_readout_error [u_2, u_4] :
  ∀ {n : Type u_2} {A : Type u_4} [inst : NormedAddCommGroup A] (a target predicted : n → A) {eRead eTarget : ℝ},
    (∀ (i : n), ‖predicted i - target i‖ ≤ eRead) →
      (∀ (i : n), ‖target i - a i‖ ≤ eTarget) → ∀ (i : n), ‖predicted i - a i‖ ≤ eRead + eTarget
end Contract48

section Contract49
universe u_1 u_2
#assert_signature FreeFoundations.GeneratedTarget.normal_equation_error [u_1, u_2] :
  ∀ {k : Type u_1} {n : Type u_2} [inst : Fintype k] [inst_1 : DecidableEq k] [inst_2 : Fintype n]
    [inst_3 : DecidableEq n] (H Hh : Matrix k k ℝ) (B Bh : Matrix k n ℝ),
    IsUnit (Matrix.det H) →
      IsUnit (Matrix.det Hh) →
        ∀ {M εH εB : ℝ},
          ‖H⁻¹‖ ≤ M → ‖Hh⁻¹‖ ≤ M → ‖Hh - H‖ ≤ εH → ‖Bh - B‖ ≤ εB → ‖Hh⁻¹ * Bh - H⁻¹ * B‖ ≤ M * εB + M ^ (2 : ℕ) * εH * ‖B‖
end Contract49

section Contract50
universe u_1
#assert_signature FreeFoundations.Geometry.chord [u_1] :
  {n : Type u_1} → [Fintype n] → (n → ℝ) → Option n → ℝ
end Contract50

section Contract51
universe u_1
#assert_signature FreeFoundations.Geometry.chord_dist_sq_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (x y : n → ℝ),
    ∑ o : Option n, (FreeFoundations.Geometry.chord x o - FreeFoundations.Geometry.chord y o) ^ (2 : ℕ) ≤ (4 : ℝ)
end Contract51

section Contract52
universe u_1
#assert_signature FreeFoundations.Geometry.chord_injective [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n], Function.Injective (FreeFoundations.Geometry.chord (n := n))
end Contract52

section Contract53
universe u_1
#assert_signature FreeFoundations.Geometry.chord_left_inverse [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (x : n → ℝ),
    (fun (i : n) => FreeFoundations.Geometry.chord x (Option.some i) / FreeFoundations.Geometry.chord x Option.none) = x
end Contract53

section Contract54
universe u_1
#assert_signature FreeFoundations.Geometry.chord_scale_pos [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (x : n → ℝ), (0 : ℝ) < (√((1 : ℝ) + ∑ i : n, x i ^ (2 : ℕ)))⁻¹
end Contract54

section Contract55
universe u_1
#assert_signature FreeFoundations.Geometry.chord_sq_sum [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (x : n → ℝ), ∑ o : Option n, FreeFoundations.Geometry.chord x o ^ (2 : ℕ) = (1 : ℝ)
end Contract55

section Contract56
universe u_2
#assert_signature FreeFoundations.Geometry.distances_preserved_iff [u_2] :
  ∀ {A : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A] (G : A →ₗ[ℝ] A),
    (∀ (x y : A), ‖G x - G y‖ = ‖x - y‖) ↔ ∀ (x : A), ‖G x‖ = ‖x‖
end Contract56

section Contract57
#assert_signature FreeFoundations.Geometry.nonlinear_codes_distort [] :
  |(0 : ℝ) - (1 : ℝ)| = (1 : ℝ) ∧
    |(1 : ℝ) - (2 : ℝ)| = (1 : ℝ) ∧
      |(0 : ℝ) ^ (2 : ℕ) - (1 : ℝ) ^ (2 : ℕ)| = (1 : ℝ) ∧ |(1 : ℝ) ^ (2 : ℕ) - (2 : ℝ) ^ (2 : ℕ)| = (3 : ℝ)
end Contract57

section Contract58
#assert_signature FreeFoundations.Geometry.nonlinear_codes_sufficient [] :
  FreeFoundations.Alignment.Sufficient (fun (i : Fin 3) => (i.val : ℝ)) (fun (i : Fin 3) => (i.val : ℝ) ^ 2)
end Contract58

section Contract59
universe u_2 u_3
#assert_signature FreeFoundations.Geometry.observationally_equivalent [u_2, u_3] :
  ∀ {A : Type u_2} {B : Type u_3} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup B] [inst_3 : InnerProductSpace ℝ B] (C : A →ₗ[ℝ] B) (G : A ≃ₗ[ℝ] A) (a : A),
    (C ∘ₗ ↑(LinearEquiv.symm G)) (G a) = C a
end Contract59

section Contract60
universe u_1
#assert_signature FreeFoundations.Geometry.one_add_sq_pos [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (x : n → ℝ), (0 : ℝ) < (1 : ℝ) + ∑ i : n, x i ^ (2 : ℕ)
end Contract60

section Contract61
universe u
#assert_signature FreeFoundations.Geometry.optimal_equiv [u] :
  ∀ {H T R R' : Type u} (F : H → T) (Z : H → R) (e : R ≃ R'),
    FreeFoundations.Alignment.Optimal F Z ↔ FreeFoundations.Alignment.Optimal F (⇑e ∘ Z)
end Contract61

section Contract62
universe u
#assert_signature FreeFoundations.Geometry.rescale [u] :
  ∀ {H S E : Type u} [inst : NormedAddCommGroup E] [inst_1 : NormedSpace ℝ E] (state : H → S) (Z : H → E) {c : ℝ},
    c ≠ (0 : ℝ) →
      (FreeFoundations.Alignment.Sufficient state Z ↔ FreeFoundations.Alignment.Sufficient state fun (h : H) => c • Z h) ∧
        ∀ (h h' : H), ‖c • Z h - c • Z h'‖ = |c| * ‖Z h - Z h'‖
end Contract62

section Contract63
universe u
#assert_signature FreeFoundations.Geometry.sufficient_equiv [u] :
  ∀ {H S R R' : Type u} (state : H → S) (Z : H → R) (e : R ≃ R'),
    FreeFoundations.Alignment.Sufficient state Z ↔ FreeFoundations.Alignment.Sufficient state (⇑e ∘ Z)
end Contract63

section Contract64
universe u_1
#assert_signature FreeFoundations.GramDistance.distance_error [u_1] :
  ∀ {n : Type u_1} [Fintype n] [DecidableEq n] {G Gh : Matrix n n ℝ},
    Matrix.PosSemidef G →
      Matrix.PosSemidef Gh →
        ∀ {ε : ℝ},
          (0 : ℝ) ≤ ε →
            (∀ (i j : n), |Gh i j - G i j| ≤ ε) →
              ∀ (i j : n),
                |FreeFoundations.GramDistance.distance Gh i j - FreeFoundations.GramDistance.distance G i j| ≤
                  (2 : ℝ) * √ε
end Contract64

section Contract65
universe u_1
#assert_signature FreeFoundations.GramDistance.distance_error_spectral [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {G Gh : Matrix n n ℝ},
    Matrix.PosSemidef G →
      Matrix.PosSemidef Gh →
        ∀ {ε : ℝ},
          (0 : ℝ) ≤ ε →
            FreeFoundations.MatrixBounds.spectralNorm (Gh - G) ≤ ε →
              ∀ (i j : n),
                |FreeFoundations.GramDistance.distance Gh i j - FreeFoundations.GramDistance.distance G i j| ≤
                  √((2 : ℝ) * ε)
end Contract65

section Contract66
universe u_1
#assert_signature FreeFoundations.GramDistance.empirical_rms_to_uniform [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (e : n → ℝ) {B : ℝ},
    (0 : ℝ) ≤ B → ∑ i : n, e i ^ (2 : ℕ) ≤ ↑(Fintype.card n) * B ^ (2 : ℕ) → ∀ (i : n), |e i| ≤ √↑(Fintype.card n) * B
end Contract66

section Contract67
#assert_signature FreeFoundations.GramDistance.sharpGram_distance [] :
  ∀ {ε : ℝ},
    (0 : ℝ) ≤ ε →
      FreeFoundations.GramDistance.distance (FreeFoundations.GramDistance.sharpGram ε) (0 : Fin (2 : ℕ))
          (1 : Fin (2 : ℕ)) =
        (2 : ℝ) * √ε
end Contract67

section Contract68
universe u_1
#assert_signature FreeFoundations.GramDistance.squared_eq_quadratic [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (G : Matrix n n ℝ) (i j : n),
    FreeFoundations.GramDistance.squared G i j =
      (Pi.single i (1 : ℝ) - Pi.single j (1 : ℝ)) ⬝ᵥ Matrix.mulVec G (Pi.single i (1 : ℝ) - Pi.single j (1 : ℝ))
end Contract68

section Contract69
universe u_1
#assert_signature FreeFoundations.GramDistance.squared_error [u_1] :
  ∀ {n : Type u_1} (G Gh : Matrix n n ℝ) {ε : ℝ},
    (∀ (i j : n), |Gh i j - G i j| ≤ ε) →
      ∀ (i j : n),
        |FreeFoundations.GramDistance.squared Gh i j - FreeFoundations.GramDistance.squared G i j| ≤ (4 : ℝ) * ε
end Contract69

section Contract70
universe u_1 u_2
#assert_signature FreeFoundations.GramDistance.uniform_exposure_distance [u_1, u_2] :
  ∀ {n : Type u_1} {A : Type u_2} [inst : NormedAddCommGroup A] (a ah : n → A) {e : ℝ},
    (∀ (i : n), ‖ah i - a i‖ ≤ e) → ∀ (i j : n), |‖ah i - ah j‖ - ‖a i - a j‖| ≤ (2 : ℝ) * e
end Contract70

section Contract71
universe u_1 u_2
#assert_signature FreeFoundations.Information.nested_condExp [u_1, u_2] :
  ∀ {Ω : Type u_1} {E : Type u_2} {mG mH m0 : MeasurableSpace Ω} {μ : MeasureTheory.Measure Ω}
    [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] [inst_2 : CompleteSpace E] (hGH : mG ≤ mH)
    (hH : mH ≤ m0) (a : ↥(MeasureTheory.Lp E (2 : ENNReal) μ)),
    ‖a - (((MeasureTheory.condExpL2 E ℝ (LE.le.trans hGH hH)) a) : MeasureTheory.Lp E 2 μ)‖ ^ (2 : ℕ) -
        ‖a - (((MeasureTheory.condExpL2 E ℝ hH) a) : MeasureTheory.Lp E 2 μ)‖ ^ (2 : ℕ) =
      ‖(((MeasureTheory.condExpL2 E ℝ hH) a) : MeasureTheory.Lp E 2 μ) - (((MeasureTheory.condExpL2 E ℝ (LE.le.trans hGH hH)) a) : MeasureTheory.Lp E 2 μ)‖ ^ (2 : ℕ)
end Contract71

section Contract72
universe u_1
#assert_signature FreeFoundations.Information.nested_projection [u_1] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (G H : Submodule ℝ E)
    [inst_2 : Submodule.HasOrthogonalProjection G] [inst_3 : Submodule.HasOrthogonalProjection H],
    G ≤ H →
      ∀ (a : E),
        ‖a - (Submodule.starProjection G) a‖ ^ (2 : ℕ) - ‖a - (Submodule.starProjection H) a‖ ^ (2 : ℕ) =
          ‖(Submodule.starProjection H) a - (Submodule.starProjection G) a‖ ^ (2 : ℕ)
end Contract72

section Contract73
universe u_1
#assert_signature FreeFoundations.Information.projection_risk_mono [u_1] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (G H : Submodule ℝ E)
    [inst_2 : Submodule.HasOrthogonalProjection G] [inst_3 : Submodule.HasOrthogonalProjection H],
    G ≤ H → ∀ (a : E), ‖a - (Submodule.starProjection H) a‖ ^ (2 : ℕ) ≤ ‖a - (Submodule.starProjection G) a‖ ^ (2 : ℕ)
end Contract73

section Contract74
universe u_2
#assert_signature FreeFoundations.Kernel.expKernel [u_2] :
  {n : Type u_2} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ → ℝ → Matrix n n ℝ
end Contract74

section Contract75
universe u_2
#assert_signature FreeFoundations.Kernel.expKernel_linfty_le [u_2] :
  ∀ {n : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (d dh : Matrix n n ℝ) {h δ : ℝ},
        (0 : ℝ) < h →
          (∀ (i j : n), i ≠ j → |dh i j - d i j| ≤ δ) →
            @Norm.norm (Matrix n n ℝ)
              (@SeminormedAddCommGroup.toNorm (Matrix n n ℝ) Matrix.linftyOpSeminormedAddCommGroup)
              (FreeFoundations.Kernel.expKernel dh h - FreeFoundations.Kernel.expKernel d h) ≤
              Min.min (2 : ℝ) (Real.exp ((2 : ℝ) * δ / h) - (1 : ℝ))
end Contract75

section Contract76
universe u_2
#assert_signature FreeFoundations.Kernel.expKernel_row_l1_le_scaled [u_2] :
  ∀ {n : Type u_2} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (d dh : Matrix n n ℝ) {h hh b : ℝ},
        (0 : ℝ) ≤ b →
          (∀ (i j : n), i ≠ j → |dh i j / hh - d i j / h| ≤ b) →
            ∀ (i : n),
              ∑ j : n, |(FreeFoundations.Kernel.expKernel dh hh - FreeFoundations.Kernel.expKernel d h) i j| ≤
                FreeFoundations.Kernel.sensitivity b
end Contract76

section Contract77
universe u_1
#assert_signature FreeFoundations.Kernel.expRow [u_1] :
  {ι : Type u_1} → Finset ι → (ι → ℝ) → ℝ → ι → ℝ
end Contract77

section Contract78
universe u_1
#assert_signature FreeFoundations.Kernel.expRow_l1_le [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d dh : ι → ℝ) {h δ : ℝ},
        (0 : ℝ) < h →
          (∀ j ∈ s, |dh j - d j| ≤ δ) →
            ∑ j ∈ s, |FreeFoundations.Kernel.expRow s dh h j - FreeFoundations.Kernel.expRow s d h j| ≤
              Min.min (2 : ℝ) (Real.exp ((2 : ℝ) * δ / h) - (1 : ℝ))
end Contract78

section Contract79
universe u_1
#assert_signature FreeFoundations.Kernel.expRow_l1_le_bandwidth [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d dh : ι → ℝ) {h hh hmin δ D : ℝ},
        (0 : ℝ) < hmin →
          hmin ≤ h →
            hmin ≤ hh →
              (∀ j ∈ s, |d j| ≤ D) →
                (∀ j ∈ s, |dh j - d j| ≤ δ) →
                  ∑ j ∈ s, |FreeFoundations.Kernel.expRow s dh hh j - FreeFoundations.Kernel.expRow s d h j| ≤
                    FreeFoundations.Kernel.sensitivity (δ / hmin + D * |hh - h| / hmin ^ (2 : ℕ))
end Contract79

section Contract80
universe u_1
#assert_signature FreeFoundations.Kernel.expRow_l1_le_scaled [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d dh : ι → ℝ) {h hh b : ℝ},
        (0 : ℝ) ≤ b →
          (∀ j ∈ s, |dh j / hh - d j / h| ≤ b) →
            ∑ j ∈ s, |FreeFoundations.Kernel.expRow s dh hh j - FreeFoundations.Kernel.expRow s d h j| ≤
              FreeFoundations.Kernel.sensitivity b
end Contract80

section Contract81
universe u_1
#assert_signature FreeFoundations.Kernel.expRow_scale [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι) (d : ι → ℝ) (h c : ℝ),
    c ≠ (0 : ℝ) → FreeFoundations.Kernel.expRow s (fun (j : ι) => c * d j) (c * h) = FreeFoundations.Kernel.expRow s d h
end Contract81

section Contract82
universe u_1
#assert_signature FreeFoundations.Kernel.normalized_l1_le [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι) (x y : ι → ℝ) {r : ℝ},
    (1 : ℝ) ≤ r →
      Finset.Nonempty s →
        (∀ j ∈ s, (0 : ℝ) < x j) →
          (∀ j ∈ s, x j ≤ r * y j) →
            (∀ j ∈ s, y j ≤ r * x j) → ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤ r ^ (2 : ℕ) - (1 : ℝ)
end Contract82

section Contract83
universe u_1
#assert_signature FreeFoundations.Kernel.normalized_l1_le_sharp [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι) (x y : ι → ℝ) {r : ℝ},
    (1 : ℝ) ≤ r →
      Finset.Nonempty s →
        (∀ j ∈ s, (0 : ℝ) < x j) →
          (∀ j ∈ s, x j ≤ r * y j) →
            (∀ j ∈ s, y j ≤ r * x j) →
              ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤ (2 : ℝ) * (r - (1 : ℝ)) / (r + (1 : ℝ))
end Contract83

section Contract84
universe u_1
#assert_signature FreeFoundations.Kernel.normalized_l1_le_two [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι) (x y : ι → ℝ),
    (∀ j ∈ s, (0 : ℝ) ≤ x j) → (∀ j ∈ s, (0 : ℝ) ≤ y j) → ∑ j ∈ s, |y j / ∑ k ∈ s, y k - x j / ∑ k ∈ s, x k| ≤ (2 : ℝ)
end Contract84

section Contract85
#assert_signature FreeFoundations.Kernel.scaled_distance_error [] :
  ∀ {d dh h hh hmin δ D : ℝ},
    (0 : ℝ) < hmin →
      hmin ≤ h → hmin ≤ hh → |d| ≤ D → |dh - d| ≤ δ → |dh / hh - d / h| ≤ δ / hmin + D * |hh - h| / hmin ^ (2 : ℕ)
end Contract85

section Contract86
universe u_1
#assert_signature FreeFoundations.Likelihood.diagonal_quadratic [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (x η : n → ℝ),
    ∑ j : n, ∑ k : n, (x j * if j = k then η j else (0 : ℝ)) * x k = ∑ j : n, x j ^ (2 : ℕ) * η j
end Contract86

section Contract87
universe u_1 u_2
#assert_signature FreeFoundations.Likelihood.filtered_second_moment [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {E : Type u_2} [inst_2 : NormedAddCommGroup E]
    [inst_3 : InnerProductSpace ℝ E] (W : Matrix n n ℝ),
    (∀ (i : n), W i i = (0 : ℝ)) →
      ∀ (a : n → E) (η : n → ℝ) (c : ℝ) (i : n),
        (((1 : Matrix n n ℝ) - c • W) * FreeFoundations.Likelihood.moment a η *
              Matrix.transpose ((1 : Matrix n n ℝ) - c • W))
            i i =
          ‖a i - c • ∑ j : n, W i j • a j‖ ^ (2 : ℕ) + η i + c ^ (2 : ℕ) * ∑ j : n, W i j ^ (2 : ℕ) * η j
end Contract87

section Contract88
universe u_1 u_2
#assert_signature FreeFoundations.Likelihood.filtered_second_moment_expand [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {E : Type u_2} [inst_2 : NormedAddCommGroup E]
    [inst_3 : InnerProductSpace ℝ E] (W : Matrix n n ℝ),
    (∀ (i : n), W i i = (0 : ℝ)) →
      ∀ (a : n → E) (η : n → ℝ) (c : ℝ) (i : n),
        (((1 : Matrix n n ℝ) - c • W) * FreeFoundations.Likelihood.moment a η *
              Matrix.transpose ((1 : Matrix n n ℝ) - c • W))
            i i =
          ‖a i‖ ^ (2 : ℕ) + η i - (2 : ℝ) * c * ∑ j : n, W i j * Inner.inner ℝ (a i) (a j) +
            c ^ (2 : ℕ) * (‖∑ j : n, W i j • a j‖ ^ (2 : ℕ) + ∑ j : n, W i j ^ (2 : ℕ) * η j)
end Contract88

section Contract89
universe u_1 u_2
#assert_signature FreeFoundations.Likelihood.gram_quadratic [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {E : Type u_2} [inst_1 : NormedAddCommGroup E] [inst_2 : InnerProductSpace ℝ E]
    (x : n → ℝ) (a : n → E), ∑ j : n, ∑ k : n, x j * Inner.inner ℝ (a j) (a k) * x k = ‖∑ j : n, x j • a j‖ ^ (2 : ℕ)
end Contract89

section Contract90
universe u_1
#assert_signature FreeFoundations.Likelihood.herfindahl_ge [u_1] :
  ∀ {n : Type u_1} (s : Finset n) (w : n → ℝ),
    ∑ j ∈ s, w j = (1 : ℝ) → (0 : ℕ) < Finset.card s → (1 : ℝ) / ↑(Finset.card s) ≤ ∑ j ∈ s, w j ^ (2 : ℕ)
end Contract90

section Contract91
universe u_1
#assert_signature FreeFoundations.Likelihood.herfindahl_uniform [u_1] :
  ∀ {n : Type u_1} (s : Finset n),
    (0 : ℕ) < Finset.card s → ∑ _j ∈ s, ((1 : ℝ) / ↑(Finset.card s)) ^ (2 : ℕ) = (1 : ℝ) / ↑(Finset.card s)
end Contract91

section Contract92
universe u_1
#assert_signature FreeFoundations.Likelihood.logdet_eq [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ),
    IsUnit (Matrix.det A) →
      ∀ (d : n → ℝ),
        (∀ (i : n), (0 : ℝ) < d i) →
          Real.log (Matrix.det (A⁻¹ * Matrix.diagonal d * Matrix.transpose A⁻¹)) =
            ∑ i : n, Real.log (d i) - (2 : ℝ) * Real.log |Matrix.det A|
end Contract92

section Contract93
universe u_1 u_2
#assert_signature FreeFoundations.Likelihood.moment [u_1, u_2] :
  {n : Type u_1} →
    [DecidableEq n] →
      {E : Type u_2} → [inst : NormedAddCommGroup E] → [InnerProductSpace ℝ E] → (n → E) → (n → ℝ) → Matrix n n ℝ
end Contract93

section Contract94
universe u_1
#assert_signature FreeFoundations.Likelihood.precision_eq [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ),
    IsUnit (Matrix.det A) →
      ∀ (d : n → ℝ),
        (∀ (i : n), d i ≠ (0 : ℝ)) →
          (A⁻¹ * Matrix.diagonal d * Matrix.transpose A⁻¹)⁻¹ =
            (Matrix.transpose A * Matrix.diagonal fun (i : n) => (d i)⁻¹) * A
end Contract94

section Contract95
universe u_1
#assert_signature FreeFoundations.Likelihood.quadratic_term [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ),
    IsUnit (Matrix.det A) →
      ∀ (d : n → ℝ),
        (∀ (i : n), d i ≠ (0 : ℝ)) →
          ∀ (M : Matrix n n ℝ),
            Matrix.trace ((A⁻¹ * Matrix.diagonal d * Matrix.transpose A⁻¹)⁻¹ * M) =
              ∑ i : n, (A * M * Matrix.transpose A) i i / d i
end Contract95

section Contract96
universe u_1
#assert_signature FreeFoundations.Likelihood.spatial_loss [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ),
    IsUnit (Matrix.det A) →
      ∀ (d : n → ℝ),
        (∀ (i : n), (0 : ℝ) < d i) →
          ∀ (M : Matrix n n ℝ),
            FreeFoundations.Score.loss (A⁻¹ * Matrix.diagonal d * Matrix.transpose A⁻¹) M =
              ∑ i : n, Real.log (d i) - (2 : ℝ) * Real.log |Matrix.det A| +
                ∑ i : n, (A * M * Matrix.transpose A) i i / d i
end Contract96

section Contract97
universe u_1
#assert_signature FreeFoundations.Likelihood.trace_precision [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ) (e : n → ℝ) (M : Matrix n n ℝ),
    Matrix.trace (Matrix.transpose A * Matrix.diagonal e * A * M) = ∑ i : n, e i * (A * M * Matrix.transpose A) i i
end Contract97

section Contract98
universe u_1 u_2
#assert_signature FreeFoundations.MatrixBounds.frobeniusNorm_le_sqrt_card_mul_rowSumNorm [u_1, u_2] :
  ∀ {m : Type u_1} {n : Type u_2} [inst : Fintype m] [inst_1 : Fintype n] (A : Matrix m n ℝ),
    FreeFoundations.MatrixBounds.frobeniusNorm A ≤ √↑(Fintype.card m) * FreeFoundations.MatrixBounds.rowSumNorm A
end Contract98

section Contract99
universe u_1 u_2
#assert_signature FreeFoundations.MatrixBounds.frobeniusNorm_sq_le_card_mul_spectralNorm_sq [u_1, u_2] :
  ∀ {m : Type u_1} {n : Type u_2} [inst : Fintype m] [inst_1 : Fintype n] [inst_2 : DecidableEq n] (A : Matrix m n ℝ),
    FreeFoundations.MatrixBounds.frobeniusNorm A ^ (2 : ℕ) ≤
      ↑(Fintype.card n) * FreeFoundations.MatrixBounds.spectralNorm A ^ (2 : ℕ)
end Contract99

section Contract100
universe u_1 u_2
#assert_signature FreeFoundations.MatrixBounds.spectralNorm_le_frobeniusNorm [u_1, u_2] :
  ∀ {m : Type u_1} {n : Type u_2} [inst : Fintype m] [inst_1 : Fintype n] [inst_2 : DecidableEq n] (A : Matrix m n ℝ),
    FreeFoundations.MatrixBounds.spectralNorm A ≤ FreeFoundations.MatrixBounds.frobeniusNorm A
end Contract100

section Contract101
#assert_signature FreeFoundations.Measurement.aggregate_readout_error [] :
  ∀ (r : ℝ → FreeFoundations.Recovery.Plane),
    √(2 : ℝ) / (2 : ℝ) ≤
      Max.max (Dist.dist (r (1 : ℝ)) (WithLp.toLp (2 : ENNReal) ![(1 : ℝ), (0 : ℝ)]))
        (Dist.dist (r (1 : ℝ)) (WithLp.toLp (2 : ENNReal) ![(0 : ℝ), (1 : ℝ)]))
end Contract101

section Contract102
universe u_1 u_2
#assert_signature FreeFoundations.Measurement.decoder_lipschitz [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L → (0 : ℝ) < κ → LipschitzWith (Real.toNNReal κ⁻¹) ⇑L
end Contract102

section Contract103
universe u_1 u_2
#assert_signature FreeFoundations.Measurement.mean_sq_distance [u_1, u_2] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] [CompleteSpace E] {Ω : Type u_2}
    [inst_3 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsProbabilityMeasure μ] {D : Ω → E},
    MeasureTheory.MemLp D (2 : ENNReal) μ →
      ∫ (ω : Ω), ‖D ω‖ ^ (2 : ℕ) ∂μ = ‖∫ (ω : Ω), D ω ∂μ‖ ^ (2 : ℕ) + ∫ (ω : Ω), ‖D ω - ∫ (ω' : Ω), D ω' ∂μ‖ ^ (2 : ℕ) ∂μ
end Contract103

section Contract104
universe u_1 u_2
#assert_signature FreeFoundations.Measurement.measurement_error [u_1, u_2] :
  ∀ {F : Type u_1} {S : Type u_2} [inst : PseudoMetricSpace F] [inst_1 : PseudoMetricSpace S] {g : F → S} {K : NNReal},
    LipschitzWith K g → ∀ (s : S) (f fhat : F), Dist.dist (g fhat) s ≤ ↑K * Dist.dist fhat f + Dist.dist (g f) s
end Contract104

section Contract105
universe u_2
#assert_signature FreeFoundations.Measurement.merged_error [u_2] :
  ∀ {S : Type u_2} [inst : PseudoMetricSpace S] (s s' r : S),
    Dist.dist s s' ≤ (2 : ℝ) * Max.max (Dist.dist r s) (Dist.dist r s')
end Contract105

section Contract106
universe u_2 u_3 u_4
#assert_signature FreeFoundations.Measurement.readout_error_ge [u_2, u_3, u_4] :
  ∀ {S : Type u_2} [inst : PseudoMetricSpace S] {H : Type u_3} {R : Type u_4} (Z : H → R) (state : H → S) (r : R → S)
    {h h' : H},
    Z h = Z h' →
      Dist.dist (state h) (state h') ≤ (2 : ℝ) * Max.max (Dist.dist (r (Z h)) (state h)) (Dist.dist (r (Z h')) (state h'))
end Contract106

section Contract107
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Measurement.rms_measurement_error [u_1, u_2, u_3] :
  ∀ {F : Type u_1} {S : Type u_2} [inst : PseudoMetricSpace F] [inst_1 : PseudoMetricSpace S] {Ω : Type u_3}
    [inst_2 : MeasurableSpace Ω] (μ : MeasureTheory.Measure Ω) {g : F → S} {K : NNReal},
    LipschitzWith K g →
      ∀ (s : Ω → S) (f fhat : Ω → F),
        MeasureTheory.AEStronglyMeasurable (fun (ω : Ω) => Dist.dist (fhat ω) (f ω)) μ →
          MeasureTheory.AEStronglyMeasurable (fun (ω : Ω) => Dist.dist (g (f ω)) (s ω)) μ →
            MeasureTheory.AEStronglyMeasurable (fun (ω : Ω) => Dist.dist (g (fhat ω)) (s ω)) μ →
            MeasureTheory.eLpNorm (fun (ω : Ω) => Dist.dist (g (fhat ω)) (s ω)) (2 : ENNReal) μ ≤
              ↑K * MeasureTheory.eLpNorm (fun (ω : Ω) => Dist.dist (fhat ω) (f ω)) (2 : ENNReal) μ +
                MeasureTheory.eLpNorm (fun (ω : Ω) => Dist.dist (g (f ω)) (s ω)) (2 : ENNReal) μ
end Contract107

section Contract108
universe u_1 u_2
#assert_signature FreeFoundations.Measurement.sq_norm_mean_le [u_1, u_2] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] [CompleteSpace E] {Ω : Type u_2}
    [inst_3 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsProbabilityMeasure μ] {D : Ω → E},
    MeasureTheory.MemLp D (2 : ENNReal) μ → ‖∫ (ω : Ω), D ω ∂μ‖ ^ (2 : ℕ) ≤ ∫ (ω : Ω), ‖D ω‖ ^ (2 : ℕ) ∂μ
end Contract108

section Contract109
universe u_1
#assert_signature FreeFoundations.Network.inverse_expansion [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ) (c : ℝ),
    IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W)) →
      ((1 : Matrix n n ℝ) - c • W)⁻¹ = (1 : Matrix n n ℝ) + c • W + c ^ (2 : ℕ) • (W * W) * ((1 : Matrix n n ℝ) - c • W)⁻¹
end Contract109

section Contract110
universe u_1
#assert_signature FreeFoundations.Network.inverse_on_eigenvector [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ) (c μ : ℝ) (v : n → ℝ),
    IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W)) →
      μ ≠ (0 : ℝ) →
        Matrix.mulVec ((1 : Matrix n n ℝ) - c • W) v = μ • v → Matrix.mulVec ((1 : Matrix n n ℝ) - c • W)⁻¹ v = μ⁻¹ • v
end Contract110

section Contract111
universe u_1
#assert_signature FreeFoundations.Network.placebo_det [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ) (σ : Equiv.Perm n) (c : ℝ),
    Matrix.det ((1 : Matrix n n ℝ) - c • Matrix.submatrix W ⇑σ ⇑σ) = Matrix.det ((1 : Matrix n n ℝ) - c • W)
end Contract111

section Contract112
universe u_1 u_2
#assert_signature FreeFoundations.Network.placebo_group_mass [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {G : Type u_2} [inst_1 : DecidableEq G] (W : Matrix n n ℝ) (σ : Equiv.Perm n)
    (g : n → G),
    (∀ (i : n), g (σ i) = g i) →
      ∀ (a b : G),
        (∑ i : n, ∑ j : n, if g i = a ∧ g j = b then W (σ i) (σ j) else (0 : ℝ)) =
          ∑ i : n, ∑ j : n, if g i = a ∧ g j = b then W i j else (0 : ℝ)
end Contract112

section Contract113
universe u_1
#assert_signature FreeFoundations.Network.rowStochastic_const [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ),
    ((Matrix.mulVec W fun (x : n) => (1 : ℝ)) = fun (x : n) => (1 : ℝ)) →
      ∀ (c : ℝ),
        (Matrix.mulVec ((1 : Matrix n n ℝ) - c • W) fun (x : n) => (1 : ℝ)) = ((1 : ℝ) - c) • fun (x : n) => (1 : ℝ)
end Contract113

section Contract114
universe u_1
#assert_signature FreeFoundations.Network.rowStochastic_inverse_const [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ),
    ((Matrix.mulVec W fun (x : n) => (1 : ℝ)) = fun (x : n) => (1 : ℝ)) →
      ∀ (c : ℝ),
        c ≠ (1 : ℝ) →
          IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W)) →
            (Matrix.mulVec ((1 : Matrix n n ℝ) - c • W)⁻¹ fun (x : n) => (1 : ℝ)) =
              ((1 : ℝ) - c)⁻¹ • fun (x : n) => (1 : ℝ)
end Contract114

section Contract115
universe u_1
#assert_signature FreeFoundations.Network.uniform [u_1] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ
end Contract115

section Contract116
universe u_1
#assert_signature FreeFoundations.Network.uniform_const [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      (Matrix.mulVec FreeFoundations.Network.uniform fun (x : n) => (1 : ℝ)) = fun (x : n) => (1 : ℝ)
end Contract116

section Contract117
universe u_1
#assert_signature FreeFoundations.Network.uniform_sum_zero [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (v : n → ℝ),
    ∑ j : n, v j = (0 : ℝ) → Matrix.mulVec FreeFoundations.Network.uniform v = -(↑(Fintype.card n) - (1 : ℝ))⁻¹ • v
end Contract117

section Contract118
universe u_1 u_2
#assert_signature FreeFoundations.ReadoutStability.inverse_gram_norm_le [u_1, u_2] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι]
    (x : ι → EuclideanSpace ℝ d) {μ : ℝ}, (0 : ℝ) < μ → ‖(FreeFoundations.ReadoutStability.gram x μ)⁻¹‖ ≤ μ⁻¹
end Contract118

section Contract119
universe u_1 u_2
#assert_signature FreeFoundations.ReadoutStability.objective_minimizer_unique [u_1, u_2] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι]
    (x : ι → EuclideanSpace ℝ d) (y : ι → ℝ) {μ : ℝ},
    (0 : ℝ) < μ →
      ∀ (w : EuclideanSpace ℝ d),
        FreeFoundations.ReadoutStability.objective x y μ w ≤
            FreeFoundations.ReadoutStability.objective x y μ (FreeFoundations.ReadoutStability.ridge x y μ) →
          w = FreeFoundations.ReadoutStability.ridge x y μ
end Contract119

section Contract120
universe u_1 u_2 u_3
#assert_signature FreeFoundations.ReadoutStability.operator_normal_equation [u_1, u_2, u_3] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] {E : Type u_3}
    [inst_3 : NormedAddCommGroup E] [inst_4 : InnerProductSpace ℝ E] (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ},
    (0 : ℝ) < μ →
      FreeFoundations.ReadoutStability.ridgeOperator x y μ ∘SL
          Matrix.toEuclideanCLM (n := d) (𝕜 := ℝ) (FreeFoundations.ReadoutStability.gram x μ) =
        FreeFoundations.ReadoutStability.crossOperator x y
end Contract120

section Contract121
universe u_1 u_2 u_3
#assert_signature FreeFoundations.ReadoutStability.operator_objective_gap [u_1, u_2, u_3] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] {E : Type u_3}
    [inst_3 : NormedAddCommGroup E] [inst_4 : InnerProductSpace ℝ E] (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ},
    (0 : ℝ) < μ →
      ∀ (Q : EuclideanSpace ℝ d →L[ℝ] E),
        FreeFoundations.ReadoutStability.operatorObjective x y μ Q -
            FreeFoundations.ReadoutStability.operatorObjective x y μ
              (FreeFoundations.ReadoutStability.ridgeOperator x y μ) =
          (↑(Fintype.card ι))⁻¹ * ∑ i : ι, ‖(Q - FreeFoundations.ReadoutStability.ridgeOperator x y μ) (x i)‖ ^ (2 : ℕ) +
            μ *
              ∑ j : d,
                ‖(Q - FreeFoundations.ReadoutStability.ridgeOperator x y μ) ((EuclideanSpace.basisFun d ℝ) j)‖ ^ (2 : ℕ)
end Contract121

section Contract122
universe u_1 u_2 u_3
#assert_signature FreeFoundations.ReadoutStability.operator_objective_minimizer_unique [u_1, u_2, u_3] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] {E : Type u_3}
    [inst_3 : NormedAddCommGroup E] [inst_4 : InnerProductSpace ℝ E] (x : ι → EuclideanSpace ℝ d) (y : ι → E) {μ : ℝ},
    (0 : ℝ) < μ →
      ∀ (Q : EuclideanSpace ℝ d →L[ℝ] E),
        FreeFoundations.ReadoutStability.operatorObjective x y μ Q ≤
            FreeFoundations.ReadoutStability.operatorObjective x y μ
              (FreeFoundations.ReadoutStability.ridgeOperator x y μ) →
          Q = FreeFoundations.ReadoutStability.ridgeOperator x y μ
end Contract122

section Contract123
universe u_1 u_2
#assert_signature FreeFoundations.ReadoutStability.prediction_replacement_le [u_1, u_2] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] [Nonempty ι]
    (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → ℝ) (k : ι) {R Y μ : ℝ},
    (0 : ℝ) ≤ R →
      (0 : ℝ) ≤ Y →
        (0 : ℝ) < μ →
          (∀ (i : ι), ‖x i‖ ≤ R) →
            (∀ (i : ι), ‖x' i‖ ≤ R) →
              (∀ (i : ι), |y i| ≤ Y) →
                (∀ (i : ι), |y' i| ≤ Y) →
                  (∀ (i : ι), i ≠ k → x i = x' i) →
                    (∀ (i : ι), i ≠ k → y i = y' i) →
                      ∀ (z : EuclideanSpace ℝ d),
                        ‖z‖ ≤ R →
                          |Inner.inner ℝ z (FreeFoundations.ReadoutStability.ridge x y μ) -
                                Inner.inner ℝ z (FreeFoundations.ReadoutStability.ridge x' y' μ)| ≤
                            (2 : ℝ) * R ^ (2 : ℕ) * Y / (↑(Fintype.card ι) * μ) * ((1 : ℝ) + R ^ (2 : ℕ) / μ)
end Contract123

section Contract124
universe u_1 u_2
#assert_signature FreeFoundations.ReadoutStability.ridge_replacement_le [u_1, u_2] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] [Nonempty ι]
    (x x' : ι → EuclideanSpace ℝ d) (y y' : ι → ℝ) (k : ι) {R Y μ : ℝ},
    (0 : ℝ) ≤ R →
      (0 : ℝ) ≤ Y →
        (0 : ℝ) < μ →
          (∀ (i : ι), ‖x i‖ ≤ R) →
            (∀ (i : ι), ‖x' i‖ ≤ R) →
              (∀ (i : ι), |y i| ≤ Y) →
                (∀ (i : ι), |y' i| ≤ Y) →
                  (∀ (i : ι), i ≠ k → x i = x' i) →
                    (∀ (i : ι), i ≠ k → y i = y' i) →
                      ‖FreeFoundations.ReadoutStability.ridge x y μ - FreeFoundations.ReadoutStability.ridge x' y' μ‖ ≤
                        (2 : ℝ) * R * Y / (↑(Fintype.card ι) * μ) * ((1 : ℝ) + R ^ (2 : ℕ) / μ)
end Contract124

section Contract125
universe u_1 u_2 u_3
#assert_signature FreeFoundations.ReadoutStability.vector_prediction_replacement_le [u_1, u_2, u_3] :
  ∀ {d : Type u_1} {ι : Type u_2} [inst : Fintype d] [inst_1 : DecidableEq d] [inst_2 : Fintype ι] {E : Type u_3}
    [inst_3 : NormedAddCommGroup E] [inst_4 : InnerProductSpace ℝ E] [Nonempty ι] (x x' : ι → EuclideanSpace ℝ d)
    (y y' : ι → E) (k : ι) {R Y μ : ℝ},
    (0 : ℝ) ≤ R →
      (0 : ℝ) ≤ Y →
        (0 : ℝ) < μ →
          (∀ (i : ι), ‖x i‖ ≤ R) →
            (∀ (i : ι), ‖x' i‖ ≤ R) →
              (∀ (i : ι), ‖y i‖ ≤ Y) →
                (∀ (i : ι), ‖y' i‖ ≤ Y) →
                  (∀ (i : ι), i ≠ k → x i = x' i) →
                    (∀ (i : ι), i ≠ k → y i = y' i) →
                      ∀ (z : EuclideanSpace ℝ d),
                        ‖z‖ ≤ R →
                          ‖(FreeFoundations.ReadoutStability.ridgeOperator x y μ) z -
                                (FreeFoundations.ReadoutStability.ridgeOperator x' y' μ) z‖ ≤
                            (2 : ℝ) * R ^ (2 : ℕ) * Y / (↑(Fintype.card ι) * μ) * ((1 : ℝ) + R ^ (2 : ℕ) / μ)
end Contract125

section Contract126
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.Decoder [u_1, u_2] :
  {A : Type u_1} →
    {T : Type u_2} →
      [inst : NormedAddCommGroup A] →
        [inst_1 : InnerProductSpace ℝ A] →
          [inst_2 : NormedAddCommGroup T] → [inst_3 : InnerProductSpace ℝ T] → (A →ₗ[ℝ] T) → ℝ → (T →ₗ[ℝ] A) → Prop
end Contract126

section Contract127
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.Distinguishes [u_1, u_2] :
  {A : Type u_1} →
    {T : Type u_2} →
      [inst : NormedAddCommGroup A] →
        [inst_1 : InnerProductSpace ℝ A] →
          [inst_2 : NormedAddCommGroup T] → [inst_3 : InnerProductSpace ℝ T] → (A →ₗ[ℝ] T) → ℝ → Prop
end Contract127

section Contract128
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.Distinguishes.injective [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ},
    FreeFoundations.Recovery.Distinguishes C κ → (0 : ℝ) < κ → Function.Injective ⇑C
end Contract128

section Contract129
#assert_signature FreeFoundations.Recovery.Plane [] :
  Type
end Contract129

section Contract130
#assert_signature FreeFoundations.Recovery.aggregate_merges [] :
  have a := WithLp.toLp (2 : ENNReal) ![(1 : ℝ), (0 : ℝ)];
  have a' := WithLp.toLp (2 : ENNReal) ![(0 : ℝ), (1 : ℝ)];
  WithLp.ofLp a (0 : Fin (2 : ℕ)) + WithLp.ofLp a (1 : Fin (2 : ℕ)) =
      WithLp.ofLp a' (0 : Fin (2 : ℕ)) + WithLp.ofLp a' (1 : Fin (2 : ℕ)) ∧
    ‖a - a'‖ = √(2 : ℝ)
end Contract130

section Contract131
universe u_1
#assert_signature FreeFoundations.Recovery.distance_error [u_1] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] (ahᵢ aᵢ ahⱼ aⱼ : A), |‖ahᵢ - ahⱼ‖ - ‖aᵢ - aⱼ‖| ≤ ‖ahᵢ - aᵢ‖ + ‖ahⱼ - aⱼ‖
end Contract131

section Contract132
#assert_signature FreeFoundations.Recovery.diverse_distinguishes [] :
  ∀ (a : FreeFoundations.Recovery.Plane),
    (WithLp.ofLp a (0 : Fin (2 : ℕ)) + WithLp.ofLp a (1 : Fin (2 : ℕ))) ^ (2 : ℕ) +
        (WithLp.ofLp a (0 : Fin (2 : ℕ)) - WithLp.ofLp a (1 : Fin (2 : ℕ))) ^ (2 : ℕ) =
      (2 : (fun (x : Fin (2 : ℕ)) => ℝ) (0 : Fin (2 : ℕ))) * ‖a‖ ^ (2 : ℕ)
end Contract132

section Contract133
universe u_3
#assert_signature FreeFoundations.Recovery.excess_risk [u_3] :
  ∀ {E : Type u_3} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (K : Submodule ℝ E)
    [inst_2 : Submodule.HasOrthogonalProjection K] (Y f : E),
    f ∈ K →
      ‖f - Y‖ ^ (2 : ℕ) - ‖(Submodule.starProjection K) Y - Y‖ ^ (2 : ℕ) = ‖f - (Submodule.starProjection K) Y‖ ^ (2 : ℕ)
end Contract133

section Contract134
universe u_3
#assert_signature FreeFoundations.Recovery.excess_risk_condExp [u_3] :
  ∀ {α : Type u_3} {m m0 : MeasurableSpace α} {μ : MeasureTheory.Measure α} (hm : m ≤ m0)
    (Y : ↥(MeasureTheory.Lp ℝ (2 : ENNReal) μ)) (f : ↥(MeasureTheory.lpMeas ℝ ℝ m (2 : ENNReal) μ)),
    ‖↑f - Y‖ ^ (2 : ℕ) - ‖↑((MeasureTheory.condExpL2 ℝ ℝ hm) Y) - Y‖ ^ (2 : ℕ) =
      ‖↑f - ↑((MeasureTheory.condExpL2 ℝ ℝ hm) Y)‖ ^ (2 : ℕ)
end Contract134

section Contract135
universe u_3 u_4
#assert_signature FreeFoundations.Recovery.excess_risk_condExp_vector [u_3, u_4] :
  ∀ {α : Type u_3} {E : Type u_4} {m m0 : MeasurableSpace α} {μ : MeasureTheory.Measure α} [inst : NormedAddCommGroup E]
    [inst_1 : InnerProductSpace ℝ E] [inst_2 : CompleteSpace E] (hm : m ≤ m0) (Y : ↥(MeasureTheory.Lp E (2 : ENNReal) μ))
    (f : ↥(MeasureTheory.lpMeas E ℝ m (2 : ENNReal) μ)),
    ‖↑f - Y‖ ^ (2 : ℕ) - ‖↑((MeasureTheory.condExpL2 E ℝ hm) Y) - Y‖ ^ (2 : ℕ) =
      ‖↑f - ↑((MeasureTheory.condExpL2 E ℝ hm) Y)‖ ^ (2 : ℕ)
end Contract135

section Contract136
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.exists_decoder [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] [FiniteDimensional ℝ A] {C : A →ₗ[ℝ] T} {κ : ℝ},
    (0 : ℝ) < κ → FreeFoundations.Recovery.Distinguishes C κ → ∃ (L : T →ₗ[ℝ] A), FreeFoundations.Recovery.Decoder C κ L
end Contract136

section Contract137
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.exposure_error [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L → ∀ (a : A) (τhat : T), κ * ‖L τhat - a‖ ≤ ‖τhat - C a‖
end Contract137

section Contract138
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.exposure_error_mismatch [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L →
      (0 : ℝ) ≤ κ → ∀ (a : A) (v τhat : T), κ * ‖L τhat - a‖ ≤ ‖τhat - (C a + v)‖ + ‖v‖
end Contract138

section Contract139
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.exposure_error_mismatch_sq [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L →
      (0 : ℝ) ≤ κ →
        ∀ (a : A) (v τhat : T),
          κ ^ (2 : ℕ) * ‖L τhat - a‖ ^ (2 : ℕ) ≤ (2 : ℝ) * (‖τhat - (C a + v)‖ ^ (2 : ℕ) + ‖v‖ ^ (2 : ℕ))
end Contract139

section Contract140
universe u_1 u_2
#assert_signature FreeFoundations.Recovery.finrank_le_of_distinguishes [u_1, u_2] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] [FiniteDimensional ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ},
    FreeFoundations.Recovery.Distinguishes C κ → (0 : ℝ) < κ → Module.finrank ℝ A ≤ Module.finrank ℝ T
end Contract140

section Contract141
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Recovery.mean_exposure_error [u_1, u_2, u_3] :
  ∀ {A : Type u_1} {T : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A}
    {Ω : Type u_3} [inst_4 : MeasurableSpace Ω] (μ : MeasureTheory.Measure Ω),
    FreeFoundations.Recovery.Decoder C κ L →
      (0 : ℝ) ≤ κ →
        ∀ (a : Ω → A) (τhat : Ω → T),
          MeasureTheory.Integrable (fun (ω : Ω) => ‖τhat ω - C (a ω)‖ ^ (2 : ℕ)) μ →
            κ ^ (2 : ℕ) * ∫ (ω : Ω), ‖L (τhat ω) - a ω‖ ^ (2 : ℕ) ∂μ ≤ ∫ (ω : Ω), ‖τhat ω - C (a ω)‖ ^ (2 : ℕ) ∂μ
end Contract141

section Contract142
universe u_1 u_3
#assert_signature FreeFoundations.Recovery.pairwise_distance_error [u_1, u_3] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] {ι : Type u_3} [inst_1 : DecidableEq ι] (s : Finset ι) (ah a : ι → A),
    ∑ i ∈ s, ∑ j ∈ Finset.erase s i, (‖ah i - ah j‖ - ‖a i - a j‖) ^ (2 : ℕ) ≤
      (4 : ℝ) * (↑(Finset.card s) - (1 : ℝ)) * ∑ i ∈ s, ‖ah i - a i‖ ^ (2 : ℕ)
end Contract142

section Contract143
universe u_1 u_3
#assert_signature FreeFoundations.Recovery.readout_invariant [u_1, u_3] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A] {Z : Type u_3} [inst_2 : AddCommGroup Z]
    [inst_3 : _root_.Module ℝ Z] (G : Z →ₗ[ℝ] A) (e : Z ≃ₗ[ℝ] Z) (z z' : Z),
    ‖(G ∘ₗ ↑(LinearEquiv.symm e)) (e z) - (G ∘ₗ ↑(LinearEquiv.symm e)) (e z')‖ = ‖G z - G z'‖
end Contract143

section Contract144
universe u_1
#assert_signature FreeFoundations.Recovery.scalar_not_distinguishes [u_1] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A],
    (2 : ℕ) ≤ Module.finrank ℝ A → ∀ (C : A →ₗ[ℝ] ℝ) {κ : ℝ}, (0 : ℝ) < κ → ¬FreeFoundations.Recovery.Distinguishes C κ
end Contract144

section Contract145
universe u_1
#assert_signature FreeFoundations.ReversibleNetwork.detailed_balance [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (K : Matrix n n ℝ),
    (∀ (i j : n), K i j = K j i) →
      (∀ (i : n), (0 : ℝ) < FreeFoundations.ReversibleNetwork.degree K i) →
        ∀ (i j : n),
          FreeFoundations.ReversibleNetwork.degree K i * FreeFoundations.ReversibleNetwork.normalize K i j =
            FreeFoundations.ReversibleNetwork.degree K j * FreeFoundations.ReversibleNetwork.normalize K j i
end Contract145

section Contract146
universe u_1
#assert_signature FreeFoundations.ReversibleNetwork.exponential_resolvent_l2_bound [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (d : Matrix n n ℝ),
        (∀ (i j : n), d i j = d j i) →
          ∀ {h D c : ℝ},
            (0 : ℝ) < h →
              (∀ (i j : n), i ≠ j → (0 : ℝ) ≤ d i j ∧ d i j ≤ D) →
                |c| < (1 : ℝ) →
                  ‖((1 : Matrix n n ℝ) - c • FreeFoundations.Kernel.expKernel d h)⁻¹‖ ≤
                    Real.exp (D / ((2 : ℝ) * h)) / ((1 : ℝ) - |c|)
end Contract146

section Contract147
universe u_1
#assert_signature FreeFoundations.ReversibleNetwork.normalize_resolvent_l2_bound [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (K : Matrix n n ℝ),
    (∀ (i j : n), (0 : ℝ) ≤ K i j) →
      (∀ (i j : n), K i j = K j i) →
        ∀ {smin smax c : ℝ},
          (0 : ℝ) < smin →
            (0 : ℝ) ≤ smax →
              (∀ (i : n), smin ≤ FreeFoundations.ReversibleNetwork.degree K i) →
                (∀ (i : n), FreeFoundations.ReversibleNetwork.degree K i ≤ smax) →
                  |c| < (1 : ℝ) →
                    ‖((1 : Matrix n n ℝ) - c • FreeFoundations.ReversibleNetwork.normalize K)⁻¹‖ ≤
                      √(smax / smin) / ((1 : ℝ) - |c|)
end Contract147

section Contract148
universe u_1
#assert_signature FreeFoundations.ReversibleNetwork.weighted_resolvent_bound [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W : Matrix n n ℝ) (s : n → ℝ),
    (∀ (i j : n), (0 : ℝ) ≤ W i j) →
      (∀ (i : n), ∑ j : n, W i j = (1 : ℝ)) →
        (∀ (i : n), (0 : ℝ) < s i) →
          (∀ (j : n), ∑ i : n, s i * W i j = s j) →
            ∀ {c : ℝ},
              |c| < (1 : ℝ) →
                ∀ (x : n → ℝ),
                  FreeFoundations.ReversibleNetwork.weightedNorm s (Matrix.mulVec ((1 : Matrix n n ℝ) - c • W)⁻¹ x) ≤
                    FreeFoundations.ReversibleNetwork.weightedNorm s x / ((1 : ℝ) - |c|)
end Contract148

section Contract149
universe u_4
#assert_signature FreeFoundations.Score.calibrated_measurement_bound [u_4] :
  ∀ {Ψ : Type u_4} [Nonempty Ψ] (R Rh A : Ψ → ℝ) (I : ℝ) {g ε : ℝ},
    (∀ (ψ : Ψ), R ψ = I + A ψ) →
      (∀ (ψ : Ψ), |Rh ψ - R ψ| ≤ g) →
        ∀ {ψh : Ψ}, (∀ (ψ : Ψ), Rh ψh ≤ Rh ψ + ε) → R ψh ≤ I + InfSet.sInf (Set.range A) + (2 : ℝ) * g + ε
end Contract149

section Contract150
universe u_3
#assert_signature FreeFoundations.Score.crossEntropy [u_3] :
  {Y : Type u_3} → [Fintype Y] → (Y → ℝ) → (Y → ℝ) → ℝ
end Contract150

section Contract151
universe u_3
#assert_signature FreeFoundations.Score.crossEntropy_eq [u_3] :
  ∀ {Y : Type u_3} [inst : Fintype Y] {p q : Y → ℝ},
    (∀ (y : Y), (0 : ℝ) < q y) →
      FreeFoundations.Score.crossEntropy p q = FreeFoundations.Score.crossEntropy p p + FreeFoundations.Score.kl p q
end Contract151

section Contract152
universe u_3
#assert_signature FreeFoundations.Score.crossEntropy_le [u_3] :
  ∀ {Y : Type u_3} [inst : Fintype Y] {p q : Y → ℝ},
    (∀ (y : Y), (0 : ℝ) ≤ p y) →
      (∀ (y : Y), (0 : ℝ) < q y) →
        ∑ y : Y, p y = ∑ y : Y, q y → FreeFoundations.Score.crossEntropy p p ≤ FreeFoundations.Score.crossEntropy p q
end Contract152

section Contract153
universe u_4
#assert_signature FreeFoundations.Score.erm_bound [u_4] :
  ∀ {Ψ : Type u_4} (R Rh : Ψ → ℝ) {g ε : ℝ},
    (∀ (ψ : Ψ), |Rh ψ - R ψ| ≤ g) → ∀ {ψh : Ψ}, (∀ (ψ : Ψ), Rh ψh ≤ Rh ψ + ε) → ∀ (ψ : Ψ), R ψh ≤ R ψ + (2 : ℝ) * g + ε
end Contract153

section Contract154
universe u_1 u_2
#assert_signature FreeFoundations.Score.expected_loss [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {Ω : Type u_2} [inst_2 : MeasurableSpace Ω]
    (μ : MeasureTheory.Measure Ω) (C : Matrix n n ℝ) (u : Ω → n → ℝ),
    (∀ (i j : n), MeasureTheory.Integrable (fun (ω : Ω) => u ω i * u ω j) μ) →
      Real.log (Matrix.det C) + ∫ (ω : Ω), u ω ⬝ᵥ Matrix.mulVec C⁻¹ (u ω) ∂μ =
        FreeFoundations.Score.loss C (FreeFoundations.Score.secondMoment μ u)
end Contract154

section Contract155
universe u_1 u_2
#assert_signature FreeFoundations.Score.integral_quadratic [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {Ω : Type u_2} [inst_1 : MeasurableSpace Ω] (μ : MeasureTheory.Measure Ω)
    (A : Matrix n n ℝ) (u : Ω → n → ℝ),
    (∀ (i j : n), MeasureTheory.Integrable (fun (ω : Ω) => u ω i * u ω j) μ) →
      ∫ (ω : Ω), u ω ⬝ᵥ Matrix.mulVec A (u ω) ∂μ = Matrix.trace (A * FreeFoundations.Score.secondMoment μ u)
end Contract155

section Contract156
universe u_3
#assert_signature FreeFoundations.Score.kl [u_3] :
  {Y : Type u_3} → [Fintype Y] → (Y → ℝ) → (Y → ℝ) → ℝ
end Contract156

section Contract157
universe u_3
#assert_signature FreeFoundations.Score.kl_nonneg [u_3] :
  ∀ {Y : Type u_3} [inst : Fintype Y] {p q : Y → ℝ},
    (∀ (y : Y), (0 : ℝ) ≤ p y) →
      (∀ (y : Y), (0 : ℝ) < q y) → ∑ y : Y, p y = ∑ y : Y, q y → (0 : ℝ) ≤ FreeFoundations.Score.kl p q
end Contract157

section Contract158
universe u_1
#assert_signature FreeFoundations.Score.loss [u_1] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ → Matrix n n ℝ → ℝ
end Contract158

section Contract159
universe u_1
#assert_signature FreeFoundations.Score.loss_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {C S : Matrix n n ℝ},
    Matrix.PosDef C → Matrix.PosDef S → FreeFoundations.Score.loss S S ≤ FreeFoundations.Score.loss C S
end Contract159

section Contract160
universe u_1
#assert_signature FreeFoundations.Score.loss_sub [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {C S : Matrix n n ℝ},
    Matrix.PosDef S → FreeFoundations.Score.loss C S - FreeFoundations.Score.loss S S = FreeFoundations.Score.stein C S
end Contract160

section Contract161
universe u_3 u_4
#assert_signature FreeFoundations.Score.pretraining_excess [u_3, u_4] :
  ∀ {Y : Type u_3} [inst : Fintype Y] {Ctx : Type u_4} (s : Finset Ctx) (π : Ctx → ℝ) (p q : Ctx → Y → ℝ),
    (∀ (c : Ctx) (y : Y), (0 : ℝ) < q c y) →
      ∑ c ∈ s, π c * FreeFoundations.Score.crossEntropy (p c) (q c) -
          ∑ c ∈ s, π c * FreeFoundations.Score.crossEntropy (p c) (p c) =
        ∑ c ∈ s, π c * FreeFoundations.Score.kl (p c) (q c)
end Contract161

section Contract162
universe u_1
#assert_signature FreeFoundations.Score.quadratic_eq_trace [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (A : Matrix n n ℝ) (v : n → ℝ),
    v ⬝ᵥ Matrix.mulVec A v = Matrix.trace (A * Matrix.vecMulVec v v)
end Contract162

section Contract163
universe u_1 u_2
#assert_signature FreeFoundations.Score.realized_quadratic [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {ι : Type u_2} (s : Finset ι) (A : Matrix n n ℝ) (u : ι → n → ℝ),
    ∑ t ∈ s, u t ⬝ᵥ Matrix.mulVec A (u t) = Matrix.trace (A * ∑ t ∈ s, Matrix.vecMulVec (u t) (u t))
end Contract163

section Contract164
universe u_1 u_2
#assert_signature FreeFoundations.Score.response_sq [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {Ω : Type u_2} [inst_1 : MeasurableSpace Ω] (μ : MeasureTheory.Measure Ω)
    (q : Ω → n → ℝ),
    (∀ (i j : n), MeasureTheory.Integrable (fun (ω : Ω) => q ω i * q ω j) μ) →
      ∀ (c : n → ℝ),
        ∫ (ω : Ω), (c ⬝ᵥ q ω) ^ (2 : ℕ) ∂μ = FreeFoundations.Exposure.form (FreeFoundations.Score.secondMoment μ q) c c
end Contract164

section Contract165
universe u_1 u_2
#assert_signature FreeFoundations.Score.secondMoment [u_1, u_2] :
  {n : Type u_1} → {Ω : Type u_2} → [inst : MeasurableSpace Ω] → MeasureTheory.Measure Ω → (Ω → n → ℝ) → Matrix n n ℝ
end Contract165

section Contract166
universe u_1
#assert_signature FreeFoundations.Score.stein [u_1] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ → Matrix n n ℝ → ℝ
end Contract166

section Contract167
universe u_1
#assert_signature FreeFoundations.Score.stein_nonneg [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {C S : Matrix n n ℝ},
    Matrix.PosDef C → Matrix.PosDef S → (0 : ℝ) ≤ FreeFoundations.Score.stein C S
end Contract167

section Contract168
universe u_1
#assert_signature FreeFoundations.ScoreStability.abs_logdet_sub_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {S T : Matrix n n ℝ},
    Matrix.PosDef S →
      Matrix.PosDef T →
        ∀ {m : ℝ},
          (0 : ℝ) < m →
            Matrix.PosSemidef (S - m • (1 : Matrix n n ℝ)) →
              Matrix.PosSemidef (T - m • (1 : Matrix n n ℝ)) →
                |Real.log (Matrix.det S) - Real.log (Matrix.det T)| ≤ ↑(Fintype.card n) / m * ‖S - T‖
end Contract168

section Contract169
universe u_1
#assert_signature FreeFoundations.ScoreStability.loss_gap_le_of_norm_sub [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {S T : Matrix n n ℝ},
    Matrix.PosDef S →
      Matrix.PosDef T →
        ∀ {m e : ℝ},
          (0 : ℝ) < m →
            Matrix.PosSemidef (S - m • (1 : Matrix n n ℝ)) →
              ‖S - T‖ ≤ e →
                e < m →
                  (0 : ℝ) ≤ FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ∧
                    FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ≤
                      ↑(Fintype.card n) * (e / m) ^ (2 : ℕ) / ((2 : ℝ) * ((1 : ℝ) - e / m))
end Contract169

section Contract170
universe u_1
#assert_signature FreeFoundations.ScoreStability.loss_gap_local [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {S T B : Matrix n n ℝ},
    Matrix.PosDef S →
      Matrix.PosDef T →
        S = Matrix.transpose B * B →
          ∀ {r : ℝ},
            (0 : ℝ) ≤ r →
              r < (1 : ℝ) →
                ‖FreeFoundations.ScoreStability.whiten B T - (1 : Matrix n n ℝ)‖ ≤ r →
                  (0 : ℝ) ≤ FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ∧
                    FreeFoundations.Score.loss S T - FreeFoundations.Score.loss T T ≤
                      FreeFoundations.MatrixBounds.frobeniusNorm
                            (FreeFoundations.ScoreStability.whiten B T - (1 : Matrix n n ℝ)) ^
                          (2 : ℕ) /
                        ((2 : ℝ) * ((1 : ℝ) - r))
end Contract170

section Contract171
#assert_signature FreeFoundations.ScoreStability.sub_log_one_add_le [] :
  ∀ {x r : ℝ},
    (0 : ℝ) ≤ r →
      r < (1 : ℝ) →
        |x| ≤ r →
          (0 : ℝ) ≤ x - Real.log ((1 : ℝ) + x) ∧ x - Real.log ((1 : ℝ) + x) ≤ x ^ (2 : ℕ) / ((2 : ℝ) * ((1 : ℝ) - r))
end Contract171

section Contract172
universe u_1 u_2
#assert_signature FreeFoundations.Selection.bounded_blocks [u_1, u_2] :
  ∀ {Ω : Type u_1} {B : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : Fintype B]
    [Nonempty B] [MeasureTheory.IsProbabilityMeasure μ] (loss : B → Ω → ℝ),
    ProbabilityTheory.iIndepFun loss μ →
      (∀ (b : B), AEMeasurable (loss b) μ) →
        (∀ (b : B), ∀ᵐ (ω : Ω) ∂μ, loss b ω ∈ Set.Icc (0 : ℝ) (1 : ℝ)) →
          ∀ {ε : ℝ},
            (0 : ℝ) ≤ ε →
              MeasureTheory.Measure.real μ
                  {ω : Ω |
                    ε < |FreeFoundations.Selection.empirical loss ω - FreeFoundations.Selection.marginalRisk loss μ|} ≤
                (2 : ℝ) * Real.exp ((-2 : ℝ) * ↑(Fintype.card B) * ε ^ (2 : ℕ))
end Contract172

section Contract173
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Selection.coupled_finite_family [u_1, u_2, u_3] :
  ∀ {Ω : Type u_1} {B : Type u_2} {K : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [inst_1 : Fintype B] [Nonempty B] [inst_3 : Fintype K] [MeasureTheory.IsProbabilityMeasure μ]
    (original copy : K → B → Ω → ℝ),
    (∀ (k : K), ProbabilityTheory.iIndepFun (copy k) μ) →
      (∀ (k : K) (b : B), AEMeasurable (copy k b) μ) →
        (∀ (k : K) (b : B), ∀ᵐ (ω : Ω) ∂μ, copy k b ω ∈ Set.Icc (0 : ℝ) (1 : ℝ)) →
          (∀ (k : K) (b : B), ProbabilityTheory.IdentDistrib (original k b) (copy k b) μ μ) →
            ∀ {ε Δ : ℝ},
              (0 : ℝ) ≤ ε →
                MeasureTheory.Measure.real μ {ω : Ω | ∃ (k : K) (b : B), original k b ω ≠ copy k b ω} ≤ Δ →
                  MeasureTheory.Measure.real μ
                      {ω : Ω |
                        ∃ (k : K),
                          ε <
                            |FreeFoundations.Selection.empirical (original k) ω -
                                FreeFoundations.Selection.marginalRisk (original k) μ|} ≤
                    (2 : ℝ) * ↑(Fintype.card K) * Real.exp ((-2 : ℝ) * ↑(Fintype.card B) * ε ^ (2 : ℕ)) + Δ
end Contract173

section Contract174
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Selection.finite_family [u_1, u_2, u_3] :
  ∀ {Ω : Type u_1} {B : Type u_2} {K : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [inst_1 : Fintype B] [Nonempty B] [inst_3 : Fintype K] [MeasureTheory.IsProbabilityMeasure μ] (loss : K → B → Ω → ℝ),
    (∀ (k : K), ProbabilityTheory.iIndepFun (loss k) μ) →
      (∀ (k : K) (b : B), AEMeasurable (loss k b) μ) →
        (∀ (k : K) (b : B), ∀ᵐ (ω : Ω) ∂μ, loss k b ω ∈ Set.Icc (0 : ℝ) (1 : ℝ)) →
          ∀ {ε : ℝ},
            (0 : ℝ) ≤ ε →
              MeasureTheory.Measure.real μ
                  {ω : Ω |
                    ∃ (k : K),
                      ε <
                        |FreeFoundations.Selection.empirical (loss k) ω -
                            FreeFoundations.Selection.marginalRisk (loss k) μ|} ≤
                (2 : ℝ) * ↑(Fintype.card K) * Real.exp ((-2 : ℝ) * ↑(Fintype.card B) * ε ^ (2 : ℕ))
end Contract174

section Contract175
universe u_1 u_3
#assert_signature FreeFoundations.Selection.panel_markov [u_1, u_3] :
  ∀ {Ω : Type u_1} {K : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : Fintype K]
    [MeasureTheory.IsFiniteMeasure μ] (error : K → Ω → ℝ) {B t : ℝ},
    (0 : ℝ) < t →
      (∀ (i : K), MeasureTheory.Integrable (fun (ω : Ω) => error i ω ^ (2 : ℕ)) μ) →
        (∀ (i : K), ∫ (ω : Ω), error i ω ^ (2 : ℕ) ∂μ ≤ B ^ (2 : ℕ)) →
          MeasureTheory.Measure.real μ {ω : Ω | ∃ (i : K), t < error i ω} ≤ ↑(Fintype.card K) * B ^ (2 : ℕ) / t ^ (2 : ℕ)
end Contract175

section Contract176
universe u_1 u_3
#assert_signature FreeFoundations.Selection.random_panel [u_1, u_3] :
  ∀ {Ω : Type u_1} {K : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : Fintype K]
    [Nonempty K] [MeasureTheory.IsFiniteMeasure μ] (error : K → Ω → ℝ) {B α : ℝ},
    (0 : ℝ) ≤ B →
      (0 : ℝ) < α →
        (∀ (i : K), MeasureTheory.Integrable (fun (ω : Ω) => error i ω ^ (2 : ℕ)) μ) →
          (∀ (i : K), ∫ (ω : Ω), error i ω ^ (2 : ℕ) ∂μ ≤ B ^ (2 : ℕ)) →
            MeasureTheory.Measure.real μ {ω : Ω | ∃ (i : K), B * √(↑(Fintype.card K) / α) < error i ω} ≤ α
end Contract176

section Contract177
universe u_3
#assert_signature FreeFoundations.Selection.risk_discrepancy [u_3] :
  ∀ {K : Type u_3} {R Rh Rbar : K → ℝ} {g shift : ℝ},
    (∀ (k : K), |Rh k - Rbar k| ≤ g) → (∀ (k : K), |Rbar k - R k| ≤ shift) → ∀ (k : K), |Rh k - R k| ≤ g + shift
end Contract177

section Contract178
universe u_3
#assert_signature FreeFoundations.Selection.source_excess [u_3] :
  ∀ {K : Type u_3} (R Rh : K → ℝ) {bayes g opt app : ℝ},
    (∀ (k : K), |Rh k - R k| ≤ g) →
      ∀ {selected comparator : K},
        (∀ (k : K), Rh selected ≤ Rh k + opt) → R comparator - bayes ≤ app → R selected - bayes ≤ app + (2 : ℝ) * g + opt
end Contract178

section Contract179
universe u_4
#assert_signature FreeFoundations.Selection.task_rms_of_excess [u_4] :
  ∀ {E : Type u_4} [inst : NormedAddCommGroup E] {f target : E} {R Rbayes app g opt : ℝ},
    R - Rbayes = ‖f - target‖ ^ (2 : ℕ) → R - Rbayes ≤ app + (2 : ℝ) * g + opt → ‖f - target‖ ≤ √(app + (2 : ℝ) * g + opt)
end Contract179

section Contract180
universe u_1
#assert_signature FreeFoundations.Stability.abs_quadratic_le [u_1] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (T : E →L[ℝ] E) (v : E),
    |Inner.inner ℝ (T v) v| ≤ ‖T‖ * ‖v‖ ^ (2 : ℕ)
end Contract180

section Contract181
universe u_1
#assert_signature FreeFoundations.Stability.covariance_joint_sub_le [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] [NormedAlgebra ℝ R] [inst_2 : StarRing R] [NormedStarGroup R]
    {H H' P P' D D' : R} {M V : ℝ},
    P * ((1 : R) - H) = (1 : R) →
      ((1 : R) - H') * P' = (1 : R) →
        ‖P‖ ≤ M →
          ‖P'‖ ≤ M →
            ‖D‖ ≤ V →
              ‖P * D * Star.star P - P' * D' * Star.star P'‖ ≤
                (2 : ℝ) * V * M ^ (3 : ℕ) * ‖H - H'‖ + M ^ (2 : ℕ) * ‖D - D'‖
end Contract181

section Contract182
universe u_1
#assert_signature FreeFoundations.Stability.covariance_sub_le [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] [inst_1 : NormedAlgebra ℝ R] [inst_2 : StarRing R] [NormedStarGroup R]
    {W W' P P' V : R} {c M : ℝ},
    P * ((1 : R) - c • W) = (1 : R) →
      ((1 : R) - c • W') * P' = (1 : R) →
        ‖P‖ ≤ M → ‖P'‖ ≤ M → ‖P * V * Star.star P - P' * V * Star.star P'‖ ≤ (2 : ℝ) * ‖V‖ * |c| * M ^ (3 : ℕ) * ‖W - W'‖
end Contract182

section Contract183
universe u_1
#assert_signature FreeFoundations.Stability.inverse_sub [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] {X X' P P' : R}, P * X = (1 : R) → X' * P' = (1 : R) → P - P' = P * (X' - X) * P'
end Contract183

section Contract184
universe u_1
#assert_signature FreeFoundations.Stability.long_only_sq_le [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι) (w : ι → ℝ),
    (∀ i ∈ s, (0 : ℝ) ≤ w i) → ∑ i ∈ s, w i = (1 : ℝ) → ∑ i ∈ s, w i ^ (2 : ℕ) ≤ (1 : ℝ)
end Contract184

section Contract185
universe u_1
#assert_signature FreeFoundations.Stability.matrix_covariance_sub_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W W' V : Matrix n n ℝ) {c M : ℝ},
    IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W)) →
      IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W')) →
        ‖((1 : Matrix n n ℝ) - c • W)⁻¹‖ ≤ M →
          ‖((1 : Matrix n n ℝ) - c • W')⁻¹‖ ≤ M →
            ‖((1 : Matrix n n ℝ) - c • W)⁻¹ * V * Matrix.transpose ((1 : Matrix n n ℝ) - c • W)⁻¹ -
                  ((1 : Matrix n n ℝ) - c • W')⁻¹ * V * Matrix.transpose ((1 : Matrix n n ℝ) - c • W')⁻¹‖ ≤
              (2 : ℝ) * ‖V‖ * |c| * M ^ (3 : ℕ) * ‖W - W'‖
end Contract185

section Contract186
universe u_1
#assert_signature FreeFoundations.Stability.matrix_covariance_target_sub_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (W Wh D Dh T : Matrix n n ℝ) {c ch M V ρ : ℝ},
    IsUnit (Matrix.det ((1 : Matrix n n ℝ) - c • W)) →
      IsUnit (Matrix.det ((1 : Matrix n n ℝ) - ch • Wh)) →
        ‖((1 : Matrix n n ℝ) - c • W)⁻¹‖ ≤ M →
          ‖((1 : Matrix n n ℝ) - ch • Wh)⁻¹‖ ≤ M →
            ‖D‖ ≤ V →
              ‖((1 : Matrix n n ℝ) - c • W)⁻¹ * D * Matrix.transpose ((1 : Matrix n n ℝ) - c • W)⁻¹ - T‖ ≤ ρ →
                ‖((1 : Matrix n n ℝ) - ch • Wh)⁻¹ * Dh * Matrix.transpose ((1 : Matrix n n ℝ) - ch • Wh)⁻¹ - T‖ ≤
                  (2 : ℝ) * V * M ^ (3 : ℕ) * ‖c • W - ch • Wh‖ + M ^ (2 : ℕ) * ‖D - Dh‖ + ρ
end Contract186

section Contract187
universe u_1
#assert_signature FreeFoundations.Stability.matrix_portfolio_regret [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (S Sh : Matrix n n ℝ) (K : Set (EuclideanSpace ℝ n))
    {B : ℝ},
    (∀ w ∈ K, ‖w‖ ≤ B) →
      ∀ {wh w : EuclideanSpace ℝ n},
        wh ∈ K →
          w ∈ K →
            (∀ v ∈ K, Inner.inner ℝ ((Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) Sh) wh) wh ≤ Inner.inner ℝ ((Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) Sh) v) v) →
              Inner.inner ℝ ((Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) S) wh) wh - Inner.inner ℝ ((Matrix.toEuclideanCLM (n := n) (𝕜 := ℝ) S) w) w ≤
                (2 : ℝ) * B ^ (2 : ℕ) * ‖Sh - S‖
end Contract187

section Contract188
universe u_1
#assert_signature FreeFoundations.Stability.norm_inverse_sub_le [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] {X X' P P' : R},
    P * X = (1 : R) → X' * P' = (1 : R) → ‖P - P'‖ ≤ ‖P‖ * ‖X' - X‖ * ‖P'‖
end Contract188

section Contract189
universe u_1
#assert_signature FreeFoundations.Stability.portfolio_regret [u_1] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (S Sh : E →L[ℝ] E) (K : Set E) {B : ℝ},
    (∀ w ∈ K, ‖w‖ ≤ B) →
      ∀ {wh w : E},
        wh ∈ K →
          w ∈ K →
            (∀ v ∈ K, Inner.inner ℝ (Sh wh) wh ≤ Inner.inner ℝ (Sh v) v) →
              Inner.inner ℝ (S wh) wh - Inner.inner ℝ (S w) w ≤ (2 : ℝ) * B ^ (2 : ℕ) * ‖Sh - S‖
end Contract189

section Contract190
universe u_1
#assert_signature FreeFoundations.Stability.quadratic_inverse_sub_le [u_1] :
  ∀ {E : Type u_1} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] {S S' Q Q' : E →L[ℝ] E},
    Q * S = (1 : E →L[ℝ] E) →
      S' * Q' = (1 : E →L[ℝ] E) →
        ∀ (u : E), |Inner.inner ℝ (Q u) u - Inner.inner ℝ (Q' u) u| ≤ ‖Q‖ * ‖Q'‖ * ‖S - S'‖ * ‖u‖ ^ (2 : ℕ)
end Contract190

section Contract191
universe u_1
#assert_signature FreeFoundations.Stability.resolvent_sub_le [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] [inst_1 : NormedAlgebra ℝ R] {W W' P P' : R} {c M : ℝ},
    P * ((1 : R) - c • W) = (1 : R) →
      ((1 : R) - c • W') * P' = (1 : R) → ‖P‖ ≤ M → ‖P'‖ ≤ M → ‖P - P'‖ ≤ |c| * M ^ (2 : ℕ) * ‖W - W'‖
end Contract191

section Contract192
universe u_1
#assert_signature FreeFoundations.Stability.smul_network_sub_le [u_1] :
  ∀ {R : Type u_1} [inst : NormedRing R] [inst_1 : NormedAlgebra ℝ R] (W Wh : R) (c ch : ℝ),
    ‖ch • Wh - c • W‖ ≤ |c| * ‖Wh - W‖ + |ch - c| * ‖Wh‖
end Contract192

section Contract193
universe u_1 u_2 u_3
#assert_signature FreeFoundations.StatisticalFinancial.failure_probability [u_1, u_2, u_3] :
  ∀ {n : Type u_1} {A : Type u_2} {Ω : Type u_3} [inst : Fintype n] [inst_1 : DecidableEq n]
    [inst_2 : NormedAddCommGroup A] [InnerProductSpace ℝ A] [inst_4 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [MeasureTheory.IsProbabilityMeasure μ],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (a ah : Ω → n → A) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ) {B α h c M V ec BW eD ρ m : ℝ},
        (0 : ℝ) ≤ B →
          (0 : ℝ) < α →
            (0 : ℝ) < h →
              (0 : ℝ) < m →
                (∀ (i : n), MeasureTheory.Integrable (fun (ω : Ω) => ‖ah ω i - a ω i‖ ^ (2 : ℕ)) μ) →
                  (∀ (i : n), ∫ (ω : Ω), ‖ah ω i - a ω i‖ ^ (2 : ℕ) ∂μ ≤ B ^ (2 : ℕ)) →
                    (∀ (ω : Ω),
                        FreeFoundations.StatisticalFinancial.Controls (a ω) (ah ω) (D ω) (Dh ω) (T ω) h c (ch ω) M V ec BW
                          eD ρ m) →
                      FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                            ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW eD ρ <
                          m →
                        MeasureTheory.Measure.real μ
                            {ω : Ω |
                              ¬FreeFoundations.StatisticalFinancial.Certificate
                                  (FreeFoundations.StatisticalFinancial.forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
                                  (FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                    ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW eD ρ)
                                  m} ≤
                          α
end Contract193

section Contract194
universe u_1 u_2 u_3
#assert_signature FreeFoundations.StatisticalFinancial.failure_probability_with_learning [u_1, u_2, u_3] :
  ∀ {n : Type u_1} {A : Type u_2} {Ω : Type u_3} [inst : Fintype n] [inst_1 : DecidableEq n]
    [inst_2 : NormedAddCommGroup A] [InnerProductSpace ℝ A] [inst_4 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [MeasureTheory.IsProbabilityMeasure μ],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (a ah : Ω → n → A) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ) (good : Set Ω),
        MeasurableSet good →
          ∀ {B α αlearn h c M V ec BW eD ρ m : ℝ},
            (0 : ℝ) ≤ B →
              (0 : ℝ) < α →
                (0 : ℝ) < h →
                  (0 : ℝ) < m →
                    MeasureTheory.Measure.real μ goodᶜ ≤ αlearn →
                      (∀ (i : n),
                          MeasureTheory.Integrable (fun (ω : Ω) => ‖ah ω i - a ω i‖ ^ (2 : ℕ))
                            (MeasureTheory.Measure.restrict μ good)) →
                        (∀ (i : n), ∫ (ω : Ω) in good, ‖ah ω i - a ω i‖ ^ (2 : ℕ) ∂μ ≤ B ^ (2 : ℕ)) →
                          (∀ ω ∈ good,
                              FreeFoundations.StatisticalFinancial.Controls (a ω) (ah ω) (D ω) (Dh ω) (T ω) h c (ch ω) M V
                                ec BW eD ρ m) →
                            FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                  ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW eD ρ <
                                m →
                              MeasureTheory.Measure.real μ
                                  {ω : Ω |
                                    ¬FreeFoundations.StatisticalFinancial.Certificate
                                        (FreeFoundations.StatisticalFinancial.forecast (ah ω) (Dh ω) h (ch ω)) (T ω)
                                        (FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                          ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec BW
                                          eD ρ)
                                        m} ≤
                                α + αlearn
end Contract194

section Contract195
universe u_1 u_2 u_3 u_4 u_5
#assert_signature FreeFoundations.StatisticalFinancial.finite_transfer_failure_probability [u_1, u_2, u_3, u_4, u_5] :
  ∀ {n : Type u_1} {A : Type u_2} {Ω : Type u_3} [inst : Fintype n] [inst_1 : DecidableEq n]
    [inst_2 : NormedAddCommGroup A] [inst_3 : InnerProductSpace ℝ A] [inst_4 : MeasurableSpace Ω] {X : Type u_4}
    {U : Type u_5} [inst_5 : Fintype X] [inst_6 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_8 : NormedAddCommGroup U] [inst_9 : InnerProductSpace ℝ U] {μ : MeasureTheory.Measure Ω}
    [MeasureTheory.IsProbabilityMeasure μ],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (input : n → Ω → X),
        (∀ (i : n), Measurable (input i)) →
          ∀ {p q : X → ℝ},
            (∀ (x : X), (0 : ℝ) ≤ p x) →
              (∀ (x : X), (0 : ℝ) ≤ q x) →
                (∀ (i : n) (x : X), MeasureTheory.Measure.real μ {ω : Ω | input i ω = x} = q x) →
                  ∀ {overlap κ : ℝ},
                    (0 : ℝ) ≤ overlap →
                      (∀ (x : X), q x ≤ overlap * p x) →
                        ∀ {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A},
                          FreeFoundations.Recovery.Decoder C κ L →
                            (0 : ℝ) < κ →
                              ∀ (a : X → A) (v pred source : X → U) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ)
                                {B α h c M V ec BW eD ρ m : ℝ},
                                (0 : ℝ) ≤ B →
                                  (0 : ℝ) < α →
                                    (0 : ℝ) < h →
                                      (0 : ℝ) < m →
                                        (((√overlap * FreeFoundations.Transfer.rms p fun (x : X) => pred x - source x) +
                                                  FreeFoundations.Transfer.rms q fun (x : X) =>
                                                    source x - (C (a x) + v x)) +
                                                FreeFoundations.Transfer.rms q v) /
                                              κ ≤
                                            B →
                                          (∀ (ω : Ω),
                                              FreeFoundations.StatisticalFinancial.Controls (fun (i : n) => a (input i ω))
                                                (fun (i : n) => L (pred (input i ω))) (D ω) (Dh ω) (T ω) h c (ch ω) M V ec
                                                BW eD ρ m) →
                                            FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                                  ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M
                                                  c ec BW eD ρ <
                                                m →
                                              MeasureTheory.Measure.real μ
                                                  {ω : Ω |
                                                    ¬FreeFoundations.StatisticalFinancial.Certificate
                                                        (FreeFoundations.StatisticalFinancial.forecast
                                                          (fun (i : n) => L (pred (input i ω))) (Dh ω) h (ch ω))
                                                        (T ω)
                                                        (FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                                          ((2 : ℝ) *
                                                              FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α /
                                                            h)
                                                          V M c ec BW eD ρ)
                                                        m} ≤
                                                α
end Contract195

section Contract196
universe u_1 u_2
#assert_signature FreeFoundations.Sufficiency.condExp_eq_iff [u_1, u_2] :
  ∀ {Ω : Type u_1} {m0 : MeasurableSpace Ω} {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsFiniteMeasure μ] {E : Type u_2}
    [inst : NormedAddCommGroup E] [inst_1 : NormedSpace ℝ E] [CompleteSpace E] {mZ mH : MeasurableSpace Ω},
    mZ ≤ mH → mH ≤ m0 → ∀ (X : Ω → E), μ[X | mZ] =ᵐ[μ] μ[X | mH] ↔ MeasureTheory.AEStronglyMeasurable (m := mZ) (μ[X | mH]) μ
end Contract196

section Contract197
universe u_1 u_2
#assert_signature FreeFoundations.Sufficiency.constant_target_iff [u_1, u_2] :
  ∀ {Ω : Type u_1} {m0 : MeasurableSpace Ω} {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsFiniteMeasure μ] {E : Type u_2}
    [inst : NormedAddCommGroup E] [inst_1 : NormedSpace ℝ E] [CompleteSpace E] [inst_3 : MeasurableSpace E] [BorelSpace E]
    [SecondCountableTopology E] {mH : MeasurableSpace Ω},
    mH ≤ m0 →
      ∀ (X : Ω → E) (Y : Ω → ℝ) {c : E},
        (μ[X | mH] =ᵐ[μ] fun (x : Ω) => c) →
          ((∀ mZ ≤ mH, μ[X | mZ] =ᵐ[μ] μ[X | mH] → μ[Y | mZ] =ᵐ[μ] μ[Y | mH]) ↔
            ∃ (c' : ℝ), μ[Y | mH] =ᵐ[μ] fun (x : Ω) => c')
end Contract197

section Contract198
universe u_1 u_2
#assert_signature FreeFoundations.Sufficiency.sufficient_iff [u_1, u_2] :
  ∀ {Ω : Type u_1} {m0 : MeasurableSpace Ω} {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsFiniteMeasure μ] {E : Type u_2}
    [inst : NormedAddCommGroup E] [inst_1 : NormedSpace ℝ E] [CompleteSpace E] [inst_3 : MeasurableSpace E] [BorelSpace E]
    [SecondCountableTopology E] {mH : MeasurableSpace Ω},
    mH ≤ m0 →
      ∀ (X : Ω → E) (Y : Ω → ℝ),
        (∀ mZ ≤ mH, μ[X | mZ] =ᵐ[μ] μ[X | mH] → μ[Y | mZ] =ᵐ[μ] μ[Y | mH]) ↔
          ∃ (g : E → ℝ), Measurable g ∧ μ[Y | mH] =ᵐ[μ] g ∘ μ[X | mH]
end Contract198

section Contract199
universe u_1 u_2
#assert_signature FreeFoundations.TaskCoverage.covered_error [u_1, u_2] :
  ∀ {n : Type u_1} {t : Type u_2} [inst : Fintype n] [inst_1 : Fintype t] (tasks : t → EuclideanSpace ℝ n)
    (coeff : EuclideanSpace ℝ t) (a ahat : EuclideanSpace ℝ n),
    |Inner.inner ℝ (FreeFoundations.TaskCoverage.coveredLoading tasks coeff) ahat -
          Inner.inner ℝ (FreeFoundations.TaskCoverage.coveredLoading tasks coeff) a| ≤
      ‖coeff‖ * ‖(FreeFoundations.TaskInformation.taskOperator tasks fun (x : t) => (1 : ℝ)) (ahat - a)‖
end Contract199

section Contract200
universe u_1 u_2
#assert_signature FreeFoundations.TaskCoverage.covered_signal [u_1, u_2] :
  ∀ {n : Type u_1} {t : Type u_2} [inst : Fintype n] [inst_1 : Fintype t] (tasks : t → EuclideanSpace ℝ n)
    (coeff : EuclideanSpace ℝ t) (a : EuclideanSpace ℝ n),
    Inner.inner ℝ (FreeFoundations.TaskCoverage.coveredLoading tasks coeff) a =
      Inner.inner ℝ coeff ((FreeFoundations.TaskInformation.taskOperator tasks fun (x : t) => (1 : ℝ)) a)
end Contract200

section Contract201
universe u_2
#assert_signature FreeFoundations.TaskCoverage.predicted_task_error [u_2] :
  ∀ {t : Type u_2} [inst : Fintype t] (coeff prediction target : EuclideanSpace ℝ t),
    |Inner.inner ℝ coeff prediction - Inner.inner ℝ coeff target| ≤ ‖coeff‖ * ‖prediction - target‖
end Contract201

section Contract202
universe u_1 u_2
#assert_signature FreeFoundations.TaskInformation.distinguishes_of_loewner_floor [u_1, u_2] :
  ∀ {n : Type u_1} {t : Type u_2} [inst : Fintype n] [inst_1 : Fintype t] [inst_2 : DecidableEq n]
    (c : t → EuclideanSpace ℝ n) {w : t → ℝ},
    (∀ (k : t), (0 : ℝ) ≤ w k) →
      ∀ {κ : ℝ},
        (0 : ℝ) ≤ κ →
          κ ^ (2 : ℕ) • (1 : Matrix n n ℝ) ≤
              FreeFoundations.TaskInformation.information (fun (k : t) => WithLp.ofLp (c k)) w →
            FreeFoundations.Recovery.Distinguishes (FreeFoundations.TaskInformation.taskOperator c w) κ
end Contract202

section Contract203
universe u_1 u_2
#assert_signature FreeFoundations.TaskInformation.exists_decoder_of_information_floor [u_1, u_2] :
  ∀ {n : Type u_1} {t : Type u_2} [inst : Fintype n] [inst_1 : Fintype t] (c : t → EuclideanSpace ℝ n) {w : t → ℝ},
    (∀ (k : t), (0 : ℝ) ≤ w k) →
      ∀ {κ : ℝ},
        (0 : ℝ) < κ →
          (∀ (a : EuclideanSpace ℝ n),
              κ ^ (2 : ℕ) * ‖a‖ ^ (2 : ℕ) ≤
                WithLp.ofLp a ⬝ᵥ
                  Matrix.mulVec (FreeFoundations.TaskInformation.information (fun (k : t) => WithLp.ofLp (c k)) w)
                    (WithLp.ofLp a)) →
            ∃ (L : EuclideanSpace ℝ t →ₗ[ℝ] EuclideanSpace ℝ n),
              FreeFoundations.Recovery.Decoder (FreeFoundations.TaskInformation.taskOperator c w) κ L
end Contract203

section Contract204
universe u_1
#assert_signature FreeFoundations.TaskInformation.information_increment [u_1] :
  ∀ {n : Type u_1} [Fintype n] (J : Matrix n n ℝ) (c : n → ℝ) {w : ℝ}, (0 : ℝ) ≤ w → J ≤ J + w • Matrix.vecMulVec c c
end Contract204

section Contract205
universe u_1 u_2
#assert_signature FreeFoundations.TaskInformation.information_quadratic [u_1, u_2] :
  ∀ {n : Type u_1} {t : Type u_2} [inst : Fintype n] [inst_1 : Fintype t] (c : t → n → ℝ) (w : t → ℝ) (a : n → ℝ),
    a ⬝ᵥ Matrix.mulVec (FreeFoundations.TaskInformation.information c w) a = ∑ k : t, w k * (c k ⬝ᵥ a) ^ (2 : ℕ)
end Contract205

section Contract206
universe u_1
#assert_signature FreeFoundations.TaskInformation.posterior_precision_mono [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (P0 J : Matrix n n ℝ),
    Matrix.PosDef P0 →
      Matrix.PosSemidef J →
        ∀ (c : n → ℝ) {noise : ℝ}, (0 : ℝ) < noise → (P0⁻¹ + J + noise⁻¹ • Matrix.vecMulVec c c)⁻¹ ≤ (P0⁻¹ + J)⁻¹
end Contract206

section Contract207
universe u_1
#assert_signature FreeFoundations.TaskInformation.posterior_precision_update [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (P0 J : Matrix n n ℝ),
    Matrix.PosDef P0 →
      Matrix.PosSemidef J →
        ∀ (c : n → ℝ) {noise : ℝ},
          (0 : ℝ) < noise →
            (P0⁻¹ + J + noise⁻¹ • Matrix.vecMulVec c c)⁻¹ =
              (P0⁻¹ + J)⁻¹ -
                (noise + c ⬝ᵥ Matrix.mulVec (P0⁻¹ + J)⁻¹ c)⁻¹ •
                  Matrix.vecMulVec (Matrix.mulVec (P0⁻¹ + J)⁻¹ c) (Matrix.mulVec (P0⁻¹ + J)⁻¹ c)
end Contract207

section Contract208
universe u_1
#assert_signature FreeFoundations.TaskInformation.rank_one_inverse [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (Q : Matrix n n ℝ),
    Matrix.PosDef Q →
      ∀ (c : n → ℝ) {noise : ℝ},
        (0 : ℝ) < noise →
          (Q + noise⁻¹ • Matrix.vecMulVec c c)⁻¹ =
            Q⁻¹ - (noise + c ⬝ᵥ Matrix.mulVec Q⁻¹ c)⁻¹ • Matrix.vecMulVec (Matrix.mulVec Q⁻¹ c) (Matrix.mulVec Q⁻¹ c)
end Contract208

section Contract209
universe u_1 u_3
#assert_signature FreeFoundations.TaskInformation.task_units_invariant [u_1, u_3] :
  ∀ {n : Type u_1} {s : Type u_3} [inst : Fintype s] [inst_1 : DecidableEq s] (C : Matrix s n ℝ) (R T : Matrix s s ℝ),
    IsUnit T →
      FreeFoundations.TaskInformation.noiseInformation (T * C) (T * R * Matrix.transpose T) =
        FreeFoundations.TaskInformation.noiseInformation C R
end Contract209

section Contract210
universe u_1 u_2
#assert_signature FreeFoundations.Transfer.change_of_weights [u_1, u_2] :
  ∀ {ι : Type u_1} {E : Type u_2} [inst : Fintype ι] [inst_1 : NormedAddCommGroup E] [inst_2 : NormedSpace ℝ E]
    {p q : ι → ℝ},
    (∀ (i : ι), (0 : ℝ) ≤ p i) →
      (∀ (i : ι), (0 : ℝ) ≤ q i) →
        ∀ {ω : ℝ},
          (0 : ℝ) ≤ ω →
            (∀ (i : ι), q i ≤ ω * p i) →
              ∀ (f : ι → E), FreeFoundations.Transfer.rms q f ≤ √ω * FreeFoundations.Transfer.rms p f
end Contract210

section Contract211
universe u_3 u_4
#assert_signature FreeFoundations.Transfer.fitted_readout_error [u_3, u_4] :
  ∀ {A : Type u_3} {T : Type u_4} [inst : NormedAddCommGroup A] [inst_1 : InnerProductSpace ℝ A]
    [inst_2 : NormedAddCommGroup T] [inst_3 : InnerProductSpace ℝ T] {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
    FreeFoundations.Recovery.Decoder C κ L →
      (0 : ℝ) < κ →
        ∀ (fitted : T → A) {εL B ε ν : ℝ},
          (∀ (y : T), ‖fitted y - L y‖ ≤ εL * ‖y‖) →
            (0 : ℝ) ≤ εL →
              ∀ (a : A) (v pred : T),
                ‖pred - (C a + v)‖ ≤ ε → ‖v‖ ≤ ν → ‖pred‖ ≤ B → ‖fitted pred - a‖ ≤ (ε + ν) / κ + εL * B
end Contract211

section Contract212
universe u_3 u_4 u_5
#assert_signature FreeFoundations.Transfer.measure_source_target_recovery [u_3, u_4, u_5] :
  ∀ {Ω : Type u_3} [inst : MeasurableSpace Ω] {A : Type u_4} {T : Type u_5} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] [inst_3 : NormedAddCommGroup T] [inst_4 : InnerProductSpace ℝ T]
    {P Q : MeasureTheory.Measure Ω} {ω : ℝ},
    (0 : ℝ) ≤ ω →
      Q ≤ ENNReal.ofReal ω • P →
        ∀ {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
          FreeFoundations.Recovery.Decoder C κ L →
            (0 : ℝ) < κ →
              ∀ (a : Ω → A) (v pred source : Ω → T),
                MeasureTheory.AEStronglyMeasurable (fun (x : Ω) => pred x - source x) Q →
                  MeasureTheory.AEStronglyMeasurable (fun (x : Ω) => source x - (C (a x) + v x)) Q →
                    MeasureTheory.AEStronglyMeasurable v Q →
                      MeasureTheory.eLpNorm (fun (x : Ω) => L (pred x) - a x) (2 : ENNReal) Q ≤
                        ENNReal.ofReal κ⁻¹ *
                          (ENNReal.ofReal √ω * MeasureTheory.eLpNorm (fun (x : Ω) => pred x - source x) (2 : ENNReal) P +
                              MeasureTheory.eLpNorm (fun (x : Ω) => source x - (C (a x) + v x)) (2 : ENNReal) Q +
                            MeasureTheory.eLpNorm v (2 : ENNReal) Q)
end Contract212

section Contract213
universe u_2 u_3
#assert_signature FreeFoundations.Transfer.rnDeriv_change [u_2, u_3] :
  ∀ {E : Type u_2} [inst : NormedAddCommGroup E] {Ω : Type u_3} [inst_1 : MeasurableSpace Ω]
    {P Q : MeasureTheory.Measure Ω} [MeasureTheory.Measure.HaveLebesgueDecomposition Q P],
    MeasureTheory.Measure.AbsolutelyContinuous Q P →
      ∀ {ω : ℝ},
        (0 : ℝ) ≤ ω →
          (∀ᵐ (x : Ω) ∂P, MeasureTheory.Measure.rnDeriv Q P x ≤ ENNReal.ofReal ω) →
            ∀ (f : Ω → E),
              MeasureTheory.eLpNorm f (2 : ENNReal) Q ≤ ENNReal.ofReal √ω * MeasureTheory.eLpNorm f (2 : ENNReal) P
end Contract213

section Contract214
#assert_signature FreeFoundations.Transfer.small_mass_spike [] :
  ∀ {r : ℝ},
    (0 : ℝ) ≤ r →
      r < (1 : ℝ) →
        have p := ![r ^ (2 : ℕ), (1 : ℝ) - r ^ (2 : ℕ)];
        have f := ![(1 : ℝ), (0 : ℝ)];
        (∀ (i : Fin (2 : ℕ)), (0 : ℝ) ≤ p i) ∧
          ∑ i : Fin (2 : ℕ), p i = (1 : ℝ) ∧ FreeFoundations.Transfer.rms p f = r ∧ r < f (0 : Fin (2 : ℕ))
end Contract214

section Contract215
universe u_1 u_3 u_4
#assert_signature FreeFoundations.Transfer.source_target_recovery [u_1, u_3, u_4] :
  ∀ {ι : Type u_1} [inst : Fintype ι] {A : Type u_3} {T : Type u_4} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] [inst_3 : NormedAddCommGroup T] [inst_4 : InnerProductSpace ℝ T] {p q : ι → ℝ},
    (∀ (i : ι), (0 : ℝ) ≤ p i) →
      (∀ (i : ι), (0 : ℝ) ≤ q i) →
        ∀ {ω : ℝ},
          (0 : ℝ) ≤ ω →
            (∀ (i : ι), q i ≤ ω * p i) →
              ∀ {C : A →ₗ[ℝ] T} {κ : ℝ} {L : T →ₗ[ℝ] A},
                FreeFoundations.Recovery.Decoder C κ L →
                  (0 : ℝ) < κ →
                    ∀ (a : ι → A) (v pred source : ι → T),
                      (FreeFoundations.Transfer.rms q fun (i : ι) => L (pred i) - a i) ≤
                        (((√ω * FreeFoundations.Transfer.rms p fun (i : ι) => pred i - source i) +
                              FreeFoundations.Transfer.rms q fun (i : ι) => source i - (C (a i) + v i)) +
                            FreeFoundations.Transfer.rms q v) /
                          κ
end Contract215

section Contract216
universe u_1
#assert_signature FreeFoundations.Value.decomposition [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (W U ρ : n → n → ℝ) (k : n → ℝ),
    (∀ (i : n), ∑ j : n, W i j = (1 : ℝ)) →
      (∀ (i : n), ∑ j : n, U i j = (1 : ℝ)) →
        (∀ (j : n), ∑ i : n, U i j = (1 : ℝ)) →
          ∑ i : n, ∑ j : n, (W i j - U i j) * ((k i + k j - ρ i j ^ (2 : ℕ)) / (2 : ℝ)) =
            (∑ j : n, (∑ i : n, W i j - (1 : ℝ)) * k j) / (2 : ℝ) -
              (∑ i : n, ∑ j : n, (W i j - U i j) * ρ i j ^ (2 : ℕ)) / (2 : ℝ)
end Contract216

section Contract217
universe u_1 u_2
#assert_signature FreeFoundations.Value.placebo_hub [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {G : Type u_2} (W : n → n → ℝ) (k : n → ℝ) (σ : Equiv.Perm n) (g : n → G),
    (∀ (j : n), g (σ j) = g j) →
      (∀ (i j : n), g i = g j → k i = k j) →
        ∑ j : n, (∑ i : n, W (σ i) (σ j) - (1 : ℝ)) * k j = ∑ j : n, (∑ i : n, W i j - (1 : ℝ)) * k j
end Contract217


/-! Additional contracts for finite probability and bandwidth stochastic ordering. -/

section Contract218
universe u_1
#assert_signature FreeFoundations.Bandwidth.cdf_antitoneOn [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s → ∀ (d : ι → ℝ) (t : ℝ), AntitoneOn (FreeFoundations.Bandwidth.cdf s d t) (Set.Ioi (0 : ℝ))
end Contract218

section Contract219
universe u_1
#assert_signature FreeFoundations.Bandwidth.closedUpperTail_monotoneOn [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) (t : ℝ), MonotoneOn (FreeFoundations.Bandwidth.closedUpperTail s d t) (Set.Ioi (0 : ℝ))
end Contract219

section Contract220
universe u_1
#assert_signature FreeFoundations.Bandwidth.likelihoodRatio_cross_le [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) {h₁ h₂ : ℝ},
        (0 : ℝ) < h₁ →
          h₁ ≤ h₂ →
            ∀ (i j : ι),
              d i ≤ d j →
                FreeFoundations.Kernel.expRow s d h₂ i * FreeFoundations.Kernel.expRow s d h₁ j ≤
                  FreeFoundations.Kernel.expRow s d h₁ i * FreeFoundations.Kernel.expRow s d h₂ j
end Contract220

section Contract221
universe u_1
#assert_signature FreeFoundations.Bandwidth.monotone_cost_expectation [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s →
      ∀ (d : ι → ℝ) (φ : ℝ → ℝ),
        Monotone φ →
          MonotoneOn (fun (h : ℝ) => ∑ j ∈ s, FreeFoundations.Kernel.expRow s d h j * φ (d j)) (Set.Ioi (0 : ℝ))
end Contract221

section Contract222
universe u_1
#assert_signature FreeFoundations.Bandwidth.upperTail_monotoneOn [u_1] :
  ∀ {ι : Type u_1} (s : Finset ι),
    Finset.Nonempty s → ∀ (d : ι → ℝ) (t : ℝ), MonotoneOn (FreeFoundations.Bandwidth.upperTail s d t) (Set.Ioi (0 : ℝ))
end Contract222

section Contract223
universe u_1 u_2 u_4 u_5
#assert_signature FreeFoundations.FiniteProbability.approximate_decoder [u_1, u_2, u_4, u_5] :
  ∀ {Θ : Type u_1} {X : Type u_2} {Z : Type u_4} {A : Type u_5} [inst : Fintype Θ] [inst_1 : Fintype X]
    [inst_2 : Fintype Z] [inst_3 : Fintype A] [inst_4 : Nonempty A] (π : ↑(FreeFoundations.FiniteProbability.FinDist Θ))
    (loss : Θ → A → ℝ) (P : FreeFoundations.FiniteProbability.FinKernel Θ X)
    (Q : FreeFoundations.FiniteProbability.FinKernel Θ Z) (D : FreeFoundations.FiniteProbability.FinKernel Z X) {L ε : ℝ},
    (0 : ℝ) ≤ L →
      (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ loss θ a ∧ loss θ a ≤ L) →
        FreeFoundations.FiniteProbability.averageTV π (FreeFoundations.FiniteProbability.kernelComp Q D) P ≤ ε →
          FreeFoundations.FiniteProbability.decisionRisk π loss Q -
              FreeFoundations.FiniteProbability.decisionRisk π loss P ≤
            L * ε
end Contract223

section Contract224
universe u_1 u_2 u_4 u_5
#assert_signature FreeFoundations.FiniteProbability.approximate_decoder_uniform [u_1, u_2, u_4, u_5] :
  ∀ {Θ : Type u_1} {X : Type u_2} {Z : Type u_4} {A : Type u_5} [inst : Fintype Θ] [inst_1 : Fintype X]
    [inst_2 : Fintype Z] [inst_3 : Fintype A] [inst_4 : Nonempty A] (π : ↑(FreeFoundations.FiniteProbability.FinDist Θ))
    (loss : Θ → A → ℝ) (P : FreeFoundations.FiniteProbability.FinKernel Θ X)
    (Q : FreeFoundations.FiniteProbability.FinKernel Θ Z) (D : FreeFoundations.FiniteProbability.FinKernel Z X) {L ε : ℝ},
    (0 : ℝ) ≤ L →
      (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ loss θ a ∧ loss θ a ≤ L) →
        (∀ (θ : Θ),
            FreeFoundations.FiniteProbability.totalVariation (FreeFoundations.FiniteProbability.kernelComp Q D θ) (P θ) ≤
              ε) →
          FreeFoundations.FiniteProbability.decisionRisk π loss Q -
              FreeFoundations.FiniteProbability.decisionRisk π loss P ≤
            L * ε
end Contract224

section Contract225
universe u_1 u_2 u_4 u_5
#assert_signature FreeFoundations.FiniteProbability.approximate_sufficiency [u_1, u_2, u_4, u_5] :
  ∀ {Θ : Type u_1} {X : Type u_2} {Z : Type u_4} {A : Type u_5} [inst : Fintype Θ] [inst_1 : Fintype X]
    [inst_2 : Fintype Z] [inst_3 : Fintype A] [inst_4 : Nonempty A] (π : ↑(FreeFoundations.FiniteProbability.FinDist Θ))
    (loss : Θ → A → ℝ) (P : FreeFoundations.FiniteProbability.FinKernel Θ X)
    (G : FreeFoundations.FiniteProbability.FinKernel X Z) (D : FreeFoundations.FiniteProbability.FinKernel Z X) {L ε : ℝ},
    (0 : ℝ) ≤ L →
      (∀ (θ : Θ) (a : A), (0 : ℝ) ≤ loss θ a ∧ loss θ a ≤ L) →
        FreeFoundations.FiniteProbability.averageTV π
              (FreeFoundations.FiniteProbability.kernelComp (FreeFoundations.FiniteProbability.kernelComp P G) D) P ≤
            ε →
          (0 : ℝ) ≤
              FreeFoundations.FiniteProbability.decisionRisk π loss (FreeFoundations.FiniteProbability.kernelComp P G) -
                FreeFoundations.FiniteProbability.decisionRisk π loss P ∧
            FreeFoundations.FiniteProbability.decisionRisk π loss (FreeFoundations.FiniteProbability.kernelComp P G) -
                FreeFoundations.FiniteProbability.decisionRisk π loss P ≤
              L * ε
end Contract225

section Contract226
universe u_1
#assert_signature FreeFoundations.FiniteProbability.domination_iff [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    (p q : ↑(FreeFoundations.FiniteProbability.FinDist X)) {ω : ℝ},
    (0 : ℝ) ≤ ω →
      ((∀ (x : X), q x ≤ ω * p x) ↔
        FreeFoundations.FiniteProbability.toMeasure q ≤ ENNReal.ofReal ω • FreeFoundations.FiniteProbability.toMeasure p)
end Contract226

section Contract227
universe u_1 u_5
#assert_signature FreeFoundations.FiniteProbability.eLpNorm_eq_ofReal_rms [u_1, u_5] :
  ∀ {X : Type u_1} {E : Type u_5} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_3 : NormedAddCommGroup E] [inst_4 : NormedSpace ℝ E] (p : ↑(FreeFoundations.FiniteProbability.FinDist X))
    (f : X → E),
    MeasureTheory.eLpNorm f (2 : ENNReal) (FreeFoundations.FiniteProbability.toMeasure p) =
      ENNReal.ofReal (FreeFoundations.Transfer.rms (⇑p) f)
end Contract227

section Contract228
universe u_1 u_5
#assert_signature FreeFoundations.FiniteProbability.expect_conditionalOn [u_1, u_5] :
  ∀ {X : Type u_1} {E : Type u_5} [inst : Fintype X] [inst_1 : AddCommMonoid E] [inst_2 : _root_.Module ℝ E]
    (p : ↑(FreeFoundations.FiniteProbability.FinDist X)) (s : Set X) [inst_3 : DecidablePred fun (x : X) => x ∈ s]
    (hpos : (0 : ℝ) < FreeFoundations.FiniteProbability.probEvent p s) (f : X → E),
    FreeFoundations.FiniteProbability.expect (FreeFoundations.FiniteProbability.conditionalOn p s hpos) f =
      (FreeFoundations.FiniteProbability.probEvent p s)⁻¹ • ∑ x : X, if x ∈ s then p x • f x else (0 : E)
end Contract228

section Contract229
universe u_1 u_4 u_5
#assert_signature FreeFoundations.FiniteProbability.expect_finMixture [u_1, u_4, u_5] :
  ∀ {X : Type u_1} {I : Type u_4} {E : Type u_5} [inst : Fintype X] [inst_1 : Fintype I] [inst_2 : AddCommMonoid E]
    [inst_3 : _root_.Module ℝ E] (weights : ↑(FreeFoundations.FiniteProbability.FinDist I))
    (laws : I → ↑(FreeFoundations.FiniteProbability.FinDist X)) (f : X → E),
    FreeFoundations.FiniteProbability.expect (FreeFoundations.FiniteProbability.finMixture weights laws) f =
      FreeFoundations.FiniteProbability.expect weights fun (i : I) => FreeFoundations.FiniteProbability.expect (laws i) f
end Contract229

section Contract230
universe u_1
#assert_signature FreeFoundations.FiniteProbability.exponentialLaw_expect_monotone [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] [inst_1 : Nonempty X] (cost : X → ℝ) (φ : ℝ → ℝ),
    Monotone φ →
      MonotoneOn
        (fun (h : ℝ) =>
          FreeFoundations.FiniteProbability.expect (FreeFoundations.FiniteProbability.exponentialLaw cost h)
            fun (i : X) => φ (cost i))
        (Set.Ioi (0 : ℝ))
end Contract230

section Contract231
universe u_1 u_5
#assert_signature FreeFoundations.FiniteProbability.integral_eq_expect [u_1, u_5] :
  ∀ {X : Type u_1} {E : Type u_5} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_3 : NormedAddCommGroup E] [inst_4 : NormedSpace ℝ E] [CompleteSpace E]
    (p : ↑(FreeFoundations.FiniteProbability.FinDist X)) (f : X → E),
    ∫ (x : X), f x ∂FreeFoundations.FiniteProbability.toMeasure p = FreeFoundations.FiniteProbability.expect p f
end Contract231

section Contract232
universe u_1 u_2 u_3
#assert_signature FreeFoundations.FiniteProbability.marginalRisk_eq_mixture [u_1, u_2, u_3] :
  ∀ {X : Type u_1} {Ω : Type u_2} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_3 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsFiniteMeasure μ] {B : Type u_3}
    [inst_5 : Fintype B] [inst_6 : Nonempty B] (laws : B → ↑(FreeFoundations.FiniteProbability.FinDist X))
    (input : B → Ω → X),
    (∀ (b : B), Measurable (input b)) →
      (∀ (b : B), MeasureTheory.Measure.map (input b) μ = FreeFoundations.FiniteProbability.toMeasure (laws b)) →
        ∀ (loss : X → ℝ),
          FreeFoundations.Selection.marginalRisk (fun (b : B) (ω : Ω) => loss (input b ω)) μ =
            FreeFoundations.FiniteProbability.expect
              (FreeFoundations.FiniteProbability.finMixture stdSimplex.barycenter laws) loss
end Contract232

section Contract233
universe u_1
#assert_signature FreeFoundations.FiniteProbability.ofMeasure_toMeasure [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] [inst_1 : MeasurableSpace X] [inst_2 : MeasurableSingletonClass X]
    (p : ↑(FreeFoundations.FiniteProbability.FinDist X)),
    FreeFoundations.FiniteProbability.ofMeasure (FreeFoundations.FiniteProbability.toMeasure p) = p
end Contract233

section Contract234
universe u_1
#assert_signature FreeFoundations.FiniteProbability.ofPMF_toPMF [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] (p : ↑(FreeFoundations.FiniteProbability.FinDist X)),
    FreeFoundations.FiniteProbability.ofPMF (FreeFoundations.FiniteProbability.toPMF p) = p
end Contract234

section Contract235
universe u_1 u_5
#assert_signature FreeFoundations.FiniteProbability.rms_sq_eq_integral [u_1, u_5] :
  ∀ {X : Type u_1} {E : Type u_5} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_3 : NormedAddCommGroup E] [inst_4 : NormedSpace ℝ E] (p : ↑(FreeFoundations.FiniteProbability.FinDist X))
    (f : X → E),
    FreeFoundations.Transfer.rms (⇑p) f ^ (2 : ℕ) =
      ∫ (x : X), ‖f x‖ ^ (2 : ℕ) ∂FreeFoundations.FiniteProbability.toMeasure p
end Contract235

section Contract236
universe u_1 u_3 u_4
#assert_signature FreeFoundations.FiniteProbability.source_target_recovery [u_1, u_3, u_4] :
  ∀ {X : Type u_1} [inst : Fintype X] {A : Type u_3} {U : Type u_4} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] [inst_3 : NormedAddCommGroup U] [inst_4 : InnerProductSpace ℝ U]
    (p q : ↑(FreeFoundations.FiniteProbability.FinDist X)) {overlap κ : ℝ},
    (0 : ℝ) ≤ overlap →
      (∀ (x : X), q x ≤ overlap * p x) →
        ∀ {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A},
          FreeFoundations.Recovery.Decoder C κ L →
            (0 : ℝ) < κ →
              ∀ (a : X → A) (v pred source : X → U),
                (FreeFoundations.Transfer.rms ⇑q fun (x : X) => L (pred x) - a x) ≤
                  (((√overlap * FreeFoundations.Transfer.rms ⇑p fun (x : X) => pred x - source x) +
                        FreeFoundations.Transfer.rms ⇑q fun (x : X) => source x - (C (a x) + v x)) +
                      FreeFoundations.Transfer.rms (⇑q) v) /
                    κ
end Contract236

section Contract237
universe u_2 u_3
#assert_signature FreeFoundations.FiniteProbability.stochastic_iff_rows_simplex [u_2, u_3] :
  ∀ {X : Type u_2} {Y : Type u_3} [inst : Fintype Y] (K : X → Y → ℝ),
    FreeFoundations.Decision.Stochastic K ↔ ∀ (x : X), K x ∈ stdSimplex ℝ Y
end Contract237

section Contract238
universe u_1
#assert_signature FreeFoundations.FiniteProbability.toMeasure_ofMeasure [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] [inst_1 : MeasurableSpace X] [inst_2 : MeasurableSingletonClass X]
    (μ : MeasureTheory.Measure X) [inst_3 : MeasureTheory.IsProbabilityMeasure μ],
    FreeFoundations.FiniteProbability.toMeasure (FreeFoundations.FiniteProbability.ofMeasure μ) = μ
end Contract238

section Contract239
universe u_1
#assert_signature FreeFoundations.FiniteProbability.toPMF_ofPMF [u_1] :
  ∀ {X : Type u_1} [inst : Fintype X] (p : PMF X),
    FreeFoundations.FiniteProbability.toPMF (FreeFoundations.FiniteProbability.ofPMF p) = p
end Contract239

section Contract240
universe u_1 u_2 u_3 u_4 u_5
#assert_signature FreeFoundations.FiniteProbability.transfer_failure_probability [u_1, u_2, u_3, u_4, u_5] :
  ∀ {X : Type u_1} {Ω : Type u_2} [inst : Fintype X] [inst_1 : MeasurableSpace X] [MeasurableSingletonClass X]
    [inst_3 : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [MeasureTheory.IsProbabilityMeasure μ] {n : Type u_3}
    {A : Type u_4} {U : Type u_5} [inst_5 : Fintype n] [inst_6 : DecidableEq n] [inst_7 : NormedAddCommGroup A]
    [inst_8 : InnerProductSpace ℝ A] [inst_9 : NormedAddCommGroup U] [inst_10 : InnerProductSpace ℝ U],
    (2 : ℕ) ≤ Fintype.card n →
      ∀ (p q : ↑(FreeFoundations.FiniteProbability.FinDist X)) (input : n → Ω → X),
        (∀ (i : n), Measurable (input i)) →
          (∀ (i : n), MeasureTheory.Measure.map (input i) μ = FreeFoundations.FiniteProbability.toMeasure q) →
            ∀ {overlap κ : ℝ},
              (0 : ℝ) ≤ overlap →
                (∀ (x : X), q x ≤ overlap * p x) →
                  ∀ {C : A →ₗ[ℝ] U} {L : U →ₗ[ℝ] A},
                    FreeFoundations.Recovery.Decoder C κ L →
                      (0 : ℝ) < κ →
                        ∀ (a : X → A) (v pred source : X → U) (D Dh T : Ω → Matrix n n ℝ) (ch : Ω → ℝ)
                          {B α h c M V ec BW eD ρ m : ℝ},
                          (0 : ℝ) ≤ B →
                            (0 : ℝ) < α →
                              (0 : ℝ) < h →
                                (0 : ℝ) < m →
                                  (((√overlap * FreeFoundations.Transfer.rms ⇑p fun (x : X) => pred x - source x) +
                                            FreeFoundations.Transfer.rms ⇑q fun (x : X) => source x - (C (a x) + v x)) +
                                          FreeFoundations.Transfer.rms (⇑q) v) /
                                        κ ≤
                                      B →
                                    (∀ (ω : Ω),
                                        FreeFoundations.StatisticalFinancial.Controls (fun (i : n) => a (input i ω))
                                          (fun (i : n) => L (pred (input i ω))) (D ω) (Dh ω) (T ω) h c (ch ω) M V ec BW eD
                                          ρ m) →
                                      FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                            ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V M c ec
                                            BW eD ρ <
                                          m →
                                        MeasureTheory.Measure.real μ
                                            {ω : Ω |
                                              ¬FreeFoundations.StatisticalFinancial.Certificate
                                                  (FreeFoundations.StatisticalFinancial.forecast
                                                    (fun (i : n) => L (pred (input i ω))) (Dh ω) h (ch ω))
                                                  (T ω)
                                                  (FreeFoundations.EndToEnd.covarianceError (Fintype.card n)
                                                    ((2 : ℝ) * FreeFoundations.StatisticalFinancial.panelRadius (n := n) B α / h) V
                                                    M c ec BW eD ρ)
                                                  m} ≤
                                          α
end Contract240

/-! Frozen contracts for the reviewed local theory retained from `8a3403c`.
The static expected types retain the finite-panel constants, explicit noise
orthogonality, square integrability, nested information, and quotient assumptions.
They are checked against declarations; builds never regenerate these contracts. -/

section LocalTheoryContract0
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.exposure [u_1, u_2, u_3] :
  {S : Type u_1} →
    {V : Type u_2} →
      {E : Type u_3} →
        [inst : AddCommGroup V] →
          [inst_1 : _root_.Module ℝ V] →
            [inst_2 : NormedAddCommGroup E] → [inst_3 : NormedSpace ℝ E] → (V →ₗ[ℝ] E) → (S → V) → S → E
end LocalTheoryContract0

section LocalTheoryContract1
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance [u_1, u_2, u_3] :
  {S : Type u_1} →
    {V : Type u_2} →
      {E : Type u_3} →
        [inst : AddCommGroup V] →
          [inst_1 : _root_.Module ℝ V] →
            [inst_2 : NormedAddCommGroup E] → [inst_3 : NormedSpace ℝ E] → (V →ₗ[ℝ] E) → (S → V) → S → S → ℝ
end LocalTheoryContract1

section LocalTheoryContract2
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.riskSetoid [u_1, u_2, u_3] :
  {S : Type u_1} →
    {V : Type u_2} →
      {E : Type u_3} →
        [inst : AddCommGroup V] →
          [inst_1 : _root_.Module ℝ V] →
            [inst_2 : NormedAddCommGroup E] → [inst_3 : NormedSpace ℝ E] → (V →ₗ[ℝ] E) → (S → V) → Setoid S
end LocalTheoryContract2

section LocalTheoryContract3
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.equivalent_iff [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t : S),
    (FreeFoundations.RiskState.riskSetoid L b) s t ↔
      FreeFoundations.RiskState.exposure L b s = FreeFoundations.RiskState.exposure L b t
end LocalTheoryContract3

section LocalTheoryContract4
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_nonneg [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t : S),
    0 ≤ FreeFoundations.RiskState.distance L b s t
end LocalTheoryContract4

section LocalTheoryContract5
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_self [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s : S),
    FreeFoundations.RiskState.distance L b s s = 0
end LocalTheoryContract5

section LocalTheoryContract6
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_comm [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t : S),
    FreeFoundations.RiskState.distance L b s t = FreeFoundations.RiskState.distance L b t s
end LocalTheoryContract6

section LocalTheoryContract7
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_triangle [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t u : S),
    FreeFoundations.RiskState.distance L b s u ≤
      FreeFoundations.RiskState.distance L b s t + FreeFoundations.RiskState.distance L b t u
end LocalTheoryContract7

section LocalTheoryContract8
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_eq_zero_iff [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t : S),
    FreeFoundations.RiskState.distance L b s t = 0 ↔ (FreeFoundations.RiskState.riskSetoid L b) s t
end LocalTheoryContract8

section LocalTheoryContract9
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_eq_zero_iff_mem_ker [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) (s t : S),
    FreeFoundations.RiskState.distance L b s t = 0 ↔ b s - b t ∈ L.ker
end LocalTheoryContract9

section LocalTheoryContract10
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.separates_states_iff [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V),
    (∀ (s t : S), FreeFoundations.RiskState.distance L b s t = 0 → s = t) ↔
      Function.Injective (FreeFoundations.RiskState.exposure L b)
end LocalTheoryContract10

section LocalTheoryContract11
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.distance_representatives [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V) {s s' t t' : S},
    (FreeFoundations.RiskState.riskSetoid L b) s s' →
      (FreeFoundations.RiskState.riskSetoid L b) t t' →
        FreeFoundations.RiskState.distance L b s t = FreeFoundations.RiskState.distance L b s' t'
end LocalTheoryContract11

section LocalTheoryContract12
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.quotientExposure [u_1, u_2, u_3] :
  {S : Type u_1} →
    {V : Type u_2} →
      {E : Type u_3} →
        [inst : AddCommGroup V] →
          [inst_1 : _root_.Module ℝ V] →
            [inst_2 : NormedAddCommGroup E] →
              [inst_3 : NormedSpace ℝ E] →
                (L : V →ₗ[ℝ] E) → (b : S → V) → Quotient (FreeFoundations.RiskState.riskSetoid L b) → E
end LocalTheoryContract12

section LocalTheoryContract13
universe u_1 u_2 u_3
#assert_signature FreeFoundations.RiskState.quotientExposure_injective [u_1, u_2, u_3] :
  ∀ {S : Type u_1} {V : Type u_2} {E : Type u_3} [inst : AddCommGroup V] [inst_1 : _root_.Module ℝ V]
    [inst_2 : NormedAddCommGroup E] [inst_3 : NormedSpace ℝ E] (L : V →ₗ[ℝ] E) (b : S → V),
    Function.Injective (FreeFoundations.RiskState.quotientExposure L b)
end LocalTheoryContract13

section LocalTheoryContract14
#assert_signature FreeFoundations.RiskState.singular_scaling_example [] :
  FreeFoundations.RiskState.distance (LinearMap.fst ℝ ℝ ℝ) id (0, 0) (0, 1) = 0 ∧
    (0, 0) ≠ ((0, 1) : ℝ × ℝ)
end LocalTheoryContract14

section LocalTheoryContract15
universe u_4 u_5
#assert_signature FreeFoundations.RiskState.moment_eq_iff [u_4, u_5] :
  ∀ {n : Type u_4} [inst : DecidableEq n] {A : Type u_5} [inst_1 : NormedAddCommGroup A] [inst_2 : InnerProductSpace ℝ A]
    (a : n → A) (η η' : n → ℝ), FreeFoundations.Likelihood.moment a η = FreeFoundations.Likelihood.moment a η' ↔ η = η'
end LocalTheoryContract15

section LocalTheoryContract16
#assert_signature FreeFoundations.RiskState.same_exposures_different_total_covariance [] :
  FreeFoundations.Likelihood.moment (fun _ : Fin 1 => (0 : ℝ)) (fun _ => 1) ≠
    FreeFoundations.Likelihood.moment (fun _ : Fin 1 => (0 : ℝ)) (fun _ => 4)
end LocalTheoryContract16

section LocalTheoryContract17
universe u_1
#assert_signature FreeFoundations.Proxy.error_le [u_1] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] (prediction proxy latent : A),
    ‖prediction - latent‖ ≤ ‖prediction - proxy‖ + ‖proxy - latent‖
end LocalTheoryContract17

section LocalTheoryContract18
universe u_1
#assert_signature FreeFoundations.Proxy.error_sq_le [u_1] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] (prediction proxy latent : A),
    ‖prediction - latent‖ ^ 2 ≤ 2 * ‖prediction - proxy‖ ^ 2 + 2 * ‖proxy - latent‖ ^ 2
end LocalTheoryContract18

section LocalTheoryContract19
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.sum_error_le [u_1, u_2] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] {ι : Type u_2} (s : Finset ι) (prediction proxy latent : ι → A),
    ∑ i ∈ s, ‖prediction i - latent i‖ ≤ ∑ i ∈ s, ‖prediction i - proxy i‖ + ∑ i ∈ s, ‖proxy i - latent i‖
end LocalTheoryContract19

section LocalTheoryContract20
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.sum_error_sq_le [u_1, u_2] :
  ∀ {A : Type u_1} [inst : NormedAddCommGroup A] {ι : Type u_2} (s : Finset ι) (prediction proxy latent : ι → A),
    ∑ i ∈ s, ‖prediction i - latent i‖ ^ 2 ≤
      2 * ∑ i ∈ s, ‖prediction i - proxy i‖ ^ 2 + 2 * ∑ i ∈ s, ‖proxy i - latent i‖ ^ 2
end LocalTheoryContract20

section LocalTheoryContract21
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.rms_error_le [u_1, u_2] :
  ∀ {Ω : Type u_1} {A : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup A]
    (prediction proxy latent : Ω → A),
    MeasureTheory.MemLp prediction 2 μ →
      MeasureTheory.MemLp proxy 2 μ →
        MeasureTheory.MemLp latent 2 μ →
          MeasureTheory.eLpNorm (fun ω ↦ prediction ω - latent ω) 2 μ ≤
            MeasureTheory.eLpNorm (fun ω ↦ prediction ω - proxy ω) 2 μ +
              MeasureTheory.eLpNorm (fun ω ↦ proxy ω - latent ω) 2 μ
end LocalTheoryContract21

section LocalTheoryContract22
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.integral_error_sq_le [u_1, u_2] :
  ∀ {Ω : Type u_1} {A : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup A]
    (prediction proxy latent : Ω → A),
    MeasureTheory.MemLp prediction 2 μ →
      MeasureTheory.MemLp proxy 2 μ →
        MeasureTheory.MemLp latent 2 μ →
          ∫ (ω : Ω), ‖prediction ω - latent ω‖ ^ 2 ∂μ ≤
            2 * ∫ (ω : Ω), ‖prediction ω - proxy ω‖ ^ 2 ∂μ + 2 * ∫ (ω : Ω), ‖proxy ω - latent ω‖ ^ 2 ∂μ
end LocalTheoryContract22

section LocalTheoryContract23
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.integral_risk_eq [u_1, u_2] :
  ∀ {Ω : Type u_1} {A : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] (prediction latent noise : Ω → A),
    MeasureTheory.MemLp prediction 2 μ →
      MeasureTheory.MemLp latent 2 μ →
        MeasureTheory.MemLp noise 2 μ →
          ∫ (ω : Ω), Inner.inner ℝ (prediction ω - latent ω) (noise ω) ∂μ = 0 →
            ∫ (ω : Ω), ‖prediction ω - (latent ω + noise ω)‖ ^ 2 ∂μ =
              ∫ (ω : Ω), ‖prediction ω - latent ω‖ ^ 2 ∂μ + ∫ (ω : Ω), ‖noise ω‖ ^ 2 ∂μ
end LocalTheoryContract23

section LocalTheoryContract24
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.integral_risk_difference [u_1, u_2] :
  ∀ {Ω : Type u_1} {A : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] (prediction₁ prediction₂ latent noise : Ω → A),
    MeasureTheory.MemLp prediction₁ 2 μ →
      MeasureTheory.MemLp prediction₂ 2 μ →
        MeasureTheory.MemLp latent 2 μ →
          MeasureTheory.MemLp noise 2 μ →
            ∫ (ω : Ω), Inner.inner ℝ (prediction₁ ω - latent ω) (noise ω) ∂μ = 0 →
              ∫ (ω : Ω), Inner.inner ℝ (prediction₂ ω - latent ω) (noise ω) ∂μ = 0 →
                ∫ (ω : Ω), ‖prediction₁ ω - (latent ω + noise ω)‖ ^ 2 ∂μ -
                    ∫ (ω : Ω), ‖prediction₂ ω - (latent ω + noise ω)‖ ^ 2 ∂μ =
                  ∫ (ω : Ω), ‖prediction₁ ω - latent ω‖ ^ 2 ∂μ - ∫ (ω : Ω), ‖prediction₂ ω - latent ω‖ ^ 2 ∂μ
end LocalTheoryContract24

section LocalTheoryContract25
universe u_1 u_2
#assert_signature FreeFoundations.Proxy.integral_risk_le_iff [u_1, u_2] :
  ∀ {Ω : Type u_1} {A : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup A]
    [inst_2 : InnerProductSpace ℝ A] (prediction₁ prediction₂ latent noise : Ω → A),
    MeasureTheory.MemLp prediction₁ 2 μ →
      MeasureTheory.MemLp prediction₂ 2 μ →
        MeasureTheory.MemLp latent 2 μ →
          MeasureTheory.MemLp noise 2 μ →
            ∫ (ω : Ω), Inner.inner ℝ (prediction₁ ω - latent ω) (noise ω) ∂μ = 0 →
              ∫ (ω : Ω), Inner.inner ℝ (prediction₂ ω - latent ω) (noise ω) ∂μ = 0 →
                (∫ (ω : Ω), ‖prediction₁ ω - (latent ω + noise ω)‖ ^ 2 ∂μ ≤
                    ∫ (ω : Ω), ‖prediction₂ ω - (latent ω + noise ω)‖ ^ 2 ∂μ ↔
                  ∫ (ω : Ω), ‖prediction₁ ω - latent ω‖ ^ 2 ∂μ ≤ ∫ (ω : Ω), ‖prediction₂ ω - latent ω‖ ^ 2 ∂μ)
end LocalTheoryContract25

section LocalTheoryContract26
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.reparameterized_observation [u_1, u_2] :
  ∀ {S : Type u_1} {O : Type u_2} (obs : S → O) (e : S ≃ S) (s : S), (obs ∘ ⇑e.symm) (e s) = obs s
end LocalTheoryContract26

section LocalTheoryContract27
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.not_both_exact [u_1, u_2] :
  ∀ {S : Type u_1} {O : Type u_2} (obs : S → O) (e : S ≃ S) (A : O → S) {s : S},
    e s ≠ s → ¬(A (obs s) = s ∧ A ((obs ∘ ⇑e.symm) (e s)) = e s)
end LocalTheoryContract27

section LocalTheoryContract28
#assert_signature FreeFoundations.Identifiability.sign_ambiguity_example [] :
  ∀ (A : ℝ → ℝ), ¬(A 1 = 1 ∧ A 1 = -1)
end LocalTheoryContract28

section LocalTheoryContract29
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.risk [u_1, u_2] :
  {Ω : Type u_1} →
    {E : Type u_2} → [inst : MeasurableSpace Ω] → [NormedAddCommGroup E] → MeasureTheory.Measure Ω → (Ω → E) → (Ω → E) → ℝ
end LocalTheoryContract29

section LocalTheoryContract30
universe u_2
#assert_signature FreeFoundations.Identifiability.two_state_sq_error [u_2] :
  ∀ {E : Type u_2} [inst : NormedAddCommGroup E] [InnerProductSpace ℝ E] (a b v : E),
    ‖a - b‖ ^ 2 ≤ 2 * (‖v - a‖ ^ 2 + ‖v - b‖ ^ 2)
end LocalTheoryContract30

section LocalTheoryContract31
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.risk_sum_lower_bound [u_1, u_2] :
  ∀ {Ω : Type u_1} {E : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup E]
    [InnerProductSpace ℝ E] {a b v : Ω → E},
    MeasureTheory.MemLp a 2 μ →
      MeasureTheory.MemLp b 2 μ →
        MeasureTheory.MemLp v 2 μ →
          (∫ (ω : Ω), ‖a ω - b ω‖ ^ 2 ∂μ) / 2 ≤
            FreeFoundations.Identifiability.risk μ a v + FreeFoundations.Identifiability.risk μ b v
end LocalTheoryContract31

section LocalTheoryContract32
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.two_world_risk_lower_bound [u_1, u_2] :
  ∀ {Ω : Type u_1} {E : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup E]
    [InnerProductSpace ℝ E] {a b v : Ω → E},
    MeasureTheory.MemLp a 2 μ →
      MeasureTheory.MemLp b 2 μ →
        MeasureTheory.MemLp v 2 μ →
          (∫ (ω : Ω), ‖a ω - b ω‖ ^ 2 ∂μ) / 4 ≤
            Max.max (FreeFoundations.Identifiability.risk μ a v) (FreeFoundations.Identifiability.risk μ b v)
end LocalTheoryContract32

section LocalTheoryContract33
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Identifiability.same_observations_risk_lower_bound [u_1, u_2, u_3] :
  ∀ {Ω : Type u_1} {E : Type u_2} {O : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [inst_1 : NormedAddCommGroup E] [InnerProductSpace ℝ E] {a b : Ω → E} {obsA obsB : Ω → O},
    obsA =ᵐ[μ] obsB →
      ∀ (A : O → E),
        MeasureTheory.MemLp a 2 μ →
          MeasureTheory.MemLp b 2 μ →
            MeasureTheory.MemLp (A ∘ obsA) 2 μ →
              (∫ (ω : Ω), ‖a ω - b ω‖ ^ 2 ∂μ) / 4 ≤
                Max.max (FreeFoundations.Identifiability.risk μ a (A ∘ obsA))
                  (FreeFoundations.Identifiability.risk μ b (A ∘ obsB))
end LocalTheoryContract33

section LocalTheoryContract34
universe u_1 u_2 u_3
#assert_signature FreeFoundations.Identifiability.reparameterized_risk_lower_bound [u_1, u_2, u_3] :
  ∀ {Ω : Type u_1} {E : Type u_2} {O : Type u_3} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω}
    [inst_1 : NormedAddCommGroup E] [InnerProductSpace ℝ E] {a : Ω → E} (e : E ≃ E) (obs : E → O) (A : O → E),
    MeasureTheory.MemLp a 2 μ →
      MeasureTheory.MemLp (⇑e ∘ a) 2 μ →
        MeasureTheory.MemLp (A ∘ obs ∘ a) 2 μ →
          (∫ (ω : Ω), ‖a ω - e (a ω)‖ ^ 2 ∂μ) / 4 ≤
            Max.max (FreeFoundations.Identifiability.risk μ a (A ∘ obs ∘ a))
              (FreeFoundations.Identifiability.risk μ (⇑e ∘ a) (A ∘ (obs ∘ ⇑e.symm) ∘ ⇑e ∘ a))
end LocalTheoryContract34

section LocalTheoryContract35
universe u_1 u_2
#assert_signature FreeFoundations.Identifiability.positive_risk_in_one_world [u_1, u_2] :
  ∀ {Ω : Type u_1} {E : Type u_2} [inst : MeasurableSpace Ω] {μ : MeasureTheory.Measure Ω} [inst_1 : NormedAddCommGroup E]
    [InnerProductSpace ℝ E] {a b v : Ω → E},
    MeasureTheory.MemLp a 2 μ →
      MeasureTheory.MemLp b 2 μ →
        MeasureTheory.MemLp v 2 μ →
          0 < ∫ (ω : Ω), ‖a ω - b ω‖ ^ 2 ∂μ →
            0 < Max.max (FreeFoundations.Identifiability.risk μ a v) (FreeFoundations.Identifiability.risk μ b v)
end LocalTheoryContract35

section LocalTheoryContract36
universe u_1
#assert_signature FreeFoundations.Identifiability.constant_worlds_example [u_1] :
  ∀ {Ω : Type u_1} [MeasurableSpace Ω] {μ : Measure Ω} [IsProbabilityMeasure μ]
    {v : Ω → ℝ}, MemLp v 2 μ →
      1 ≤ max (FreeFoundations.Identifiability.risk μ (fun _ => (1 : ℝ)) v)
        (FreeFoundations.Identifiability.risk μ (fun _ => (-1 : ℝ)) v) ∧
      max (FreeFoundations.Identifiability.risk μ (fun _ => (1 : ℝ)) (fun _ => (0 : ℝ)))
        (FreeFoundations.Identifiability.risk μ (fun _ => (-1 : ℝ)) (fun _ => (0 : ℝ))) = 1
end LocalTheoryContract36

section LocalTheoryContract37
universe u_1
#assert_signature FreeFoundations.Pipeline.spectralNorm [u_1] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ → ℝ
end LocalTheoryContract37

section LocalTheoryContract38
universe u_1
#assert_signature FreeFoundations.Pipeline.rowNorm [u_1] :
  {n : Type u_1} → [Fintype n] → Matrix n n ℝ → ℝ
end LocalTheoryContract38

section LocalTheoryContract39
universe u_1
#assert_signature FreeFoundations.Pipeline.rowNorm_nonneg [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (A : Matrix n n ℝ), 0 ≤ FreeFoundations.Pipeline.rowNorm A
end LocalTheoryContract39

section LocalTheoryContract40
universe u_1
#assert_signature FreeFoundations.Pipeline.row_sum_le_rowNorm [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] (A : Matrix n n ℝ) (i : n), ∑ j, |A i j| ≤ FreeFoundations.Pipeline.rowNorm A
end LocalTheoryContract40

section LocalTheoryContract41
universe u_1
#assert_signature FreeFoundations.Pipeline.spectralNorm_le_sqrt_card_mul_rowNorm [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (A : Matrix n n ℝ),
    FreeFoundations.Pipeline.spectralNorm A ≤ √↑(Fintype.card n) * FreeFoundations.Pipeline.rowNorm A
end LocalTheoryContract41

section LocalTheoryContract42
universe u_1
#assert_signature FreeFoundations.Pipeline.expKernel_rowNorm_le [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n],
    2 ≤ Fintype.card n →
      ∀ (d dh : Matrix n n ℝ) {h δ : ℝ},
        0 < h →
          (∀ (i j : n), i ≠ j → |dh i j - d i j| ≤ δ) →
            FreeFoundations.Pipeline.rowNorm
                (FreeFoundations.Kernel.expKernel dh h - FreeFoundations.Kernel.expKernel d h) ≤
              Min.min 2 (Real.exp (2 * δ / h) - 1)
end LocalTheoryContract42

section LocalTheoryContract43
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.exposureDistances [u_1, u_2] :
  {n : Type u_1} → {A : Type u_2} → [NormedAddCommGroup A] → (n → A) → Matrix n n ℝ
end LocalTheoryContract43

section LocalTheoryContract44
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.exposureNetwork [u_1, u_2] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → {A : Type u_2} → [NormedAddCommGroup A] → (n → A) → ℝ → Matrix n n ℝ
end LocalTheoryContract44

section LocalTheoryContract45
universe u_1
#assert_signature FreeFoundations.Pipeline.spatialCovariance [u_1] :
  {n : Type u_1} → [Fintype n] → [DecidableEq n] → Matrix n n ℝ → Matrix n n ℝ → ℝ → Matrix n n ℝ
end LocalTheoryContract45

section LocalTheoryContract46
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.exposureNetwork_error [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A],
    2 ≤ Fintype.card n →
      ∀ (a ah : n → A) {h r : ℝ},
        0 < h →
          (∀ (i : n), ‖ah i - a i‖ ≤ r) →
            FreeFoundations.Pipeline.spectralNorm
                (FreeFoundations.Pipeline.exposureNetwork ah h - FreeFoundations.Pipeline.exposureNetwork a h) ≤
              √↑(Fintype.card n) * Min.min 2 (Real.exp (4 * r / h) - 1)
end LocalTheoryContract46

section LocalTheoryContract47
universe u_1
#assert_signature FreeFoundations.Pipeline.spectralNorm_eq [u_1] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] (B : Matrix n n ℝ),
    FreeFoundations.Pipeline.spectralNorm B = ‖B‖
end LocalTheoryContract47

section LocalTheoryContract48
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.exposure_covariance_error [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A],
    2 ≤ Fintype.card n →
      ∀ (a ah : n → A) (d : n → ℝ),
        (∀ (i : n), 0 < d i) →
          ∀ {h r c M : ℝ},
            0 < h →
              (∀ (i : n), ‖ah i - a i‖ ≤ r) →
                IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork a h).det →
                  IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h).det →
                    FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork a h)⁻¹ ≤ M →
                      FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h)⁻¹ ≤
                          M →
                        FreeFoundations.Pipeline.spectralNorm
                            (FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork ah h)
                                (Matrix.diagonal d) c -
                              FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork a h)
                                (Matrix.diagonal d) c) ≤
                          2 * FreeFoundations.Pipeline.spectralNorm (Matrix.diagonal d) * |c| * M ^ 3 *
                              √↑(Fintype.card n) *
                            Min.min 2 (Real.exp (4 * r / h) - 1)
end LocalTheoryContract48

section LocalTheoryContract49
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.proxy_covariance_error [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A],
    2 ≤ Fintype.card n →
      ∀ (a ap ah : n → A) (d : n → ℝ),
        (∀ (i : n), 0 < d i) →
          ∀ {h ε η c M : ℝ},
            0 < h →
              (∀ (i : n), ‖ah i - ap i‖ ≤ ε) →
                (∀ (i : n), ‖ap i - a i‖ ≤ η) →
                  IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork a h).det →
                    IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h).det →
                      FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork a h)⁻¹ ≤ M →
                        FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h)⁻¹ ≤
                            M →
                          FreeFoundations.Pipeline.spectralNorm
                              (FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork ah h)
                                  (Matrix.diagonal d) c -
                                FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork a h)
                                  (Matrix.diagonal d) c) ≤
                            2 * FreeFoundations.Pipeline.spectralNorm (Matrix.diagonal d) * |c| * M ^ 3 *
                                √↑(Fintype.card n) *
                              Min.min 2 (Real.exp (4 * (ε + η) / h) - 1)
end LocalTheoryContract49

section LocalTheoryContract50
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.uniform_error_le_sqrt_sum [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {A : Type u_2} [inst_1 : NormedAddCommGroup A] (a ah : n → A) (i : n),
    ‖ah i - a i‖ ≤ √(∑ j, ‖ah j - a j‖ ^ 2)
end LocalTheoryContract50

section LocalTheoryContract51
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.covariance_error_of_sum_sq [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A],
    2 ≤ Fintype.card n →
      ∀ (a ah : n → A) (d : n → ℝ),
        (∀ (i : n), 0 < d i) →
          ∀ {h c M : ℝ},
            0 < h →
              IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork a h).det →
                IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h).det →
                  FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork a h)⁻¹ ≤ M →
                    FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h)⁻¹ ≤ M →
                      FreeFoundations.Pipeline.spectralNorm
                          (FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork ah h)
                              (Matrix.diagonal d) c -
                            FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork a h)
                              (Matrix.diagonal d) c) ≤
                        2 * FreeFoundations.Pipeline.spectralNorm (Matrix.diagonal d) * |c| * M ^ 3 * √↑(Fintype.card n) *
                          Min.min 2 (Real.exp (4 * √(∑ j, ‖ah j - a j‖ ^ 2) / h) - 1)
end LocalTheoryContract51

section LocalTheoryContract52
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.panelMeanSqError [u_1, u_2] :
  {n : Type u_1} → [Fintype n] → {A : Type u_2} → [NormedAddCommGroup A] → (n → A) → (n → A) → ℝ
end LocalTheoryContract52

section LocalTheoryContract53
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.sqrt_sum_eq_sqrt_card_mul_mean [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] {A : Type u_2} [inst_1 : NormedAddCommGroup A],
    0 < Fintype.card n →
      ∀ (a ah : n → A), √(∑ j, ‖ah j - a j‖ ^ 2) = √(↑(Fintype.card n) * FreeFoundations.Pipeline.panelMeanSqError a ah)
end LocalTheoryContract53

section LocalTheoryContract54
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.zero_exposure_error [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A],
    2 ≤ Fintype.card n →
      ∀ (a ah : n → A) (d : n → ℝ),
        (∀ (i : n), 0 < d i) →
          ∀ {h c M : ℝ},
            0 < h →
              (∀ (i : n), ‖ah i - a i‖ ≤ 0) →
                IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork a h).det →
                  IsUnit (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h).det →
                    FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork a h)⁻¹ ≤ M →
                      FreeFoundations.Pipeline.spectralNorm (1 - c • FreeFoundations.Pipeline.exposureNetwork ah h)⁻¹ ≤
                          M →
                        FreeFoundations.Pipeline.spectralNorm
                            (FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork ah h)
                                (Matrix.diagonal d) c -
                              FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork a h)
                                (Matrix.diagonal d) c) ≤
                          0
end LocalTheoryContract54

section LocalTheoryContract55
universe u_1 u_2
#assert_signature FreeFoundations.Pipeline.zero_spatial_coefficient [u_1, u_2] :
  ∀ {n : Type u_1} [inst : Fintype n] [inst_1 : DecidableEq n] {A : Type u_2} [inst_2 : NormedAddCommGroup A]
    (a ah : n → A) (D : Matrix n n ℝ) (h : ℝ),
    FreeFoundations.Pipeline.spectralNorm
        (FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork ah h) D 0 -
          FreeFoundations.Pipeline.spatialCovariance (FreeFoundations.Pipeline.exposureNetwork a h) D 0) =
      0
end LocalTheoryContract55

section LocalTheoryContract56
universe u_3 u_4
#assert_signature FreeFoundations.Recovery.excess_risk_condExp_hilbert [u_3, u_4] :
  ∀ {α : Type u_3} {E : Type u_4} {m m0 : MeasurableSpace α} {μ : Measure α}
    [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hm : m ≤ m0) (Y : Lp E 2 μ) (f : lpMeas E ℝ m 2 μ),
    ‖(f : Lp E 2 μ) - Y‖ ^ 2 -
      ‖(condExpL2 E ℝ hm Y : Lp E 2 μ) - Y‖ ^ 2 =
        ‖(f : Lp E 2 μ) - condExpL2 E ℝ hm Y‖ ^ 2
end LocalTheoryContract56

section LocalTheoryContract57
universe u_3
#assert_signature FreeFoundations.Recovery.nested_projection_risk [u_3] :
  ∀ {E : Type u_3} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (K L : Submodule ℝ E)
    [inst_2 : K.HasOrthogonalProjection] [inst_3 : L.HasOrthogonalProjection],
    K ≤ L →
      ∀ (Y : E),
        ‖K.starProjection Y - Y‖ ^ 2 = ‖L.starProjection Y - Y‖ ^ 2 + ‖K.starProjection Y - L.starProjection Y‖ ^ 2
end LocalTheoryContract57

section LocalTheoryContract58
universe u_3
#assert_signature FreeFoundations.Recovery.nested_projection_fitted_risk [u_3] :
  ∀ {E : Type u_3} [inst : NormedAddCommGroup E] [inst_1 : InnerProductSpace ℝ E] (K L : Submodule ℝ E)
    [inst_2 : K.HasOrthogonalProjection] [inst_3 : L.HasOrthogonalProjection],
    K ≤ L →
      ∀ (Y f : E),
        f ∈ K →
          ‖f - Y‖ ^ 2 =
            ‖L.starProjection Y - Y‖ ^ 2 + ‖K.starProjection Y - L.starProjection Y‖ ^ 2 + ‖f - K.starProjection Y‖ ^ 2
end LocalTheoryContract58

section LocalTheoryContract59
universe u_3 u_4
#assert_signature FreeFoundations.Recovery.nested_information_risk [u_3, u_4] :
  ∀ {α : Type u_3} {E : Type u_4} {mZ mH m0 : MeasurableSpace α} {μ : Measure α}
    [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : Lp E 2 μ),
    ‖(condExpL2 E ℝ (hZH.trans hH) Y : Lp E 2 μ) - Y‖ ^ 2 =
      ‖(condExpL2 E ℝ hH Y : Lp E 2 μ) - Y‖ ^ 2 +
        ‖(condExpL2 E ℝ (hZH.trans hH) Y : Lp E 2 μ) - condExpL2 E ℝ hH Y‖ ^ 2
end LocalTheoryContract59

section LocalTheoryContract60
universe u_3 u_4
#assert_signature FreeFoundations.Recovery.nested_information_fitted_risk [u_3, u_4] :
  ∀ {α : Type u_3} {E : Type u_4} {mZ mH m0 : MeasurableSpace α} {μ : Measure α}
    [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : Lp E 2 μ) (f : lpMeas E ℝ mZ 2 μ),
    ‖(f : Lp E 2 μ) - Y‖ ^ 2 =
      ‖(condExpL2 E ℝ hH Y : Lp E 2 μ) - Y‖ ^ 2 +
        ‖(condExpL2 E ℝ (hZH.trans hH) Y : Lp E 2 μ) - condExpL2 E ℝ hH Y‖ ^ 2 +
        ‖(f : Lp E 2 μ) - condExpL2 E ℝ (hZH.trans hH) Y‖ ^ 2
end LocalTheoryContract60

section LocalTheoryContract61
universe u_3 u_4
#assert_signature FreeFoundations.Recovery.history_information_risk_le [u_3, u_4] :
  ∀ {α : Type u_3} {E : Type u_4} {mZ mH m0 : MeasurableSpace α} {μ : Measure α}
    [NormedAddCommGroup E] [InnerProductSpace ℝ E] [CompleteSpace E]
    (hZH : mZ ≤ mH) (hH : mH ≤ m0) (Y : Lp E 2 μ),
    ‖(condExpL2 E ℝ hH Y : Lp E 2 μ) - Y‖ ^ 2 ≤
      ‖(condExpL2 E ℝ (hZH.trans hH) Y : Lp E 2 μ) - Y‖ ^ 2
end LocalTheoryContract61

-- Neighbour-set contracts added for the FinFM workshop paper (2026-11-19).
section NeighbourContract0
universe u_1
#assert_signature FreeFoundations.Neighbours.neighbourSet_unique [u_1] :
  ∀ {ι : Type u_1} [inst : DecidableEq ι] {d : ι → ℝ} {i : ι} {S T : Finset ι},
    FreeFoundations.Neighbours.IsNeighbourSet d i (S : Set ι) →
      FreeFoundations.Neighbours.IsNeighbourSet d i (T : Set ι) →
        i ∉ S → i ∉ T → S.card = T.card → S = T
end NeighbourContract0

section NeighbourContract1
universe u_1
#assert_signature FreeFoundations.Neighbours.neighbourSet_stable [u_1] :
  ∀ {ι : Type u_1} {d d' : ι → ℝ} {i : ι} {S : Set ι} {γ ε : ℝ},
    FreeFoundations.Neighbours.HasMargin d i S γ →
      (∀ (j : ι), |d' j - d j| ≤ ε) →
        2 * ε < γ → FreeFoundations.Neighbours.IsNeighbourSet d' i S
end NeighbourContract1

section NeighbourContract2
universe u_1 u_2
#assert_signature FreeFoundations.Neighbours.neighbourSet_of_exposures [u_1, u_2] :
  ∀ {ι : Type u_1} {A : Type u_2} [inst : NormedAddCommGroup A] {a ah : ι → A} {δ : ι → ℝ}
    {δmax γ : ℝ} {i : ι} {S : Set ι},
    FreeFoundations.Neighbours.HasMargin (fun (j : ι) => ‖a i - a j‖) i S γ →
      (∀ (j : ι), ‖ah j - a j‖ ≤ δ j) →
        (∀ (j : ι), δ j ≤ δmax) →
          2 * (δ i + δmax) < γ →
            FreeFoundations.Neighbours.IsNeighbourSet (fun (j : ι) => ‖ah i - ah j‖) i S
end NeighbourContract2

section NeighbourContract3
universe u_1 u_2
#assert_signature FreeFoundations.Neighbours.neighbourSet_of_estimated_margin [u_1, u_2] :
  ∀ {ι : Type u_1} {A : Type u_2} [inst : NormedAddCommGroup A] {a ah : ι → A} {δ : ι → ℝ}
    {δmax γ : ℝ} {i : ι} {S : Set ι},
    FreeFoundations.Neighbours.HasMargin (fun (j : ι) => ‖ah i - ah j‖) i S γ →
      (∀ (j : ι), ‖ah j - a j‖ ≤ δ j) →
        (∀ (j : ι), δ j ≤ δmax) →
          2 * (δ i + δmax) < γ →
            FreeFoundations.Neighbours.IsNeighbourSet (fun (j : ι) => ‖a i - a j‖) i S
end NeighbourContract3

section NeighbourContract4
universe u_1 u_2
#assert_signature FreeFoundations.Neighbours.neighbourSet_linear [u_1, u_2] :
  ∀ {ι : Type u_1} {A : Type u_2} [inst : NormedAddCommGroup A] [inst_1 : Module ℝ A]
    (g : A →ₗ[ℝ] A) {z : ι → A} {σmin σmax : ℝ} {i : ι} {S : Set ι},
    (∀ (x : A), σmin * ‖x‖ ≤ ‖g x‖) →
      (∀ (x : A), ‖g x‖ ≤ σmax * ‖x‖) →
        (∀ j ∈ S, ∀ l ∉ S, l ≠ i → σmax * ‖z i - z j‖ < σmin * ‖z i - z l‖) →
          FreeFoundations.Neighbours.IsNeighbourSet (fun (j : ι) => ‖g (z i) - g (z j)‖) i S
end NeighbourContract4

section NeighbourContract5
#assert_signature FreeFoundations.Neighbours.anisotropic_flip [] :
  ‖(!₂[(1 : ℝ), 0] : FreeFoundations.Neighbours.Plane)‖ <
      ‖(!₂[(0 : ℝ), 2] : FreeFoundations.Neighbours.Plane)‖ ∧
    ‖FreeFoundations.Neighbours.stretch !₂[(0 : ℝ), 2]‖ <
      ‖FreeFoundations.Neighbours.stretch !₂[(1 : ℝ), 0]‖
end NeighbourContract5

section NeighbourContract6
universe u_1
#assert_signature FreeFoundations.Neighbours.IsNeighbourSet [u_1] :
  {ι : Type u_1} → (ι → ℝ) → ι → Set ι → Prop
end NeighbourContract6

section NeighbourContract7
universe u_1
#assert_signature FreeFoundations.Neighbours.HasMargin [u_1] :
  {ι : Type u_1} → (ι → ℝ) → ι → Set ι → ℝ → Prop
end NeighbourContract7

section NeighbourContract8
#assert_signature FreeFoundations.Neighbours.neighbourSet_margin_sharp [] :
  FreeFoundations.Neighbours.HasMargin ![(0 : ℝ), 1, 3] 0 {1} 2 ∧
    (∀ (j : Fin 3), |![(0 : ℝ), 2, 2] j - ![(0 : ℝ), 1, 3] j| ≤ 1) ∧
      ¬FreeFoundations.Neighbours.IsNeighbourSet ![(0 : ℝ), 2, 2] 0 {1}
end NeighbourContract8
