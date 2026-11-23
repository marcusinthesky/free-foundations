# MathEconLib compatibility and corrected migration

The current library uses Lean `leanprover/lean4:v4.35.0`, mathlib
`56a005855ea17e0b0958f73ec801ae140b0a1679`, and a direct Lake dependency on
[MathEconLib `6c0e61e`](https://github.com/matheconlib/matheconlib/tree/6c0e61ed4c95252e2c985ccc456e2c53617fb941).
These match the selected upstream toolchain and mathlib revision. The finite-law
interface imports upstream `FinDist.Basic`, `FinDist.Expect`,
`FinDist.ConditionalOn`, and `FinDist.Measure`, with local aliases and adapters
for the project's existing financial interfaces. The earlier copied finite-law
implementation and its separate license copy are removed.

## Historical trial

The first integration trial started from `9713a8d`. It compiled the selected
upstream probability modules under Lean 4.35, but the original project failed
in `Alignment`, `Network`, `Kernel`, `Score`, and `Measurement`. Proof-only
repairs resolved several failures. One remaining issue was semantic rather
than a renamed API or a tactic change.

Mathlib 4.35 defines `eLpNorm f p μ` to be infinite when `f` is not almost
everywhere strongly measurable. The old `Measurement.rms_measurement_error`
assumed measurability of the prediction and alignment distances, but not of the
measured-distance function on the left. Its unchanged statement is false under
that definition. The earlier trial therefore retained Lean 4.31 and used a local
finite-probability facade. That fallback describes the earlier revision, not
the current migration.

The preserved [counterexample source](lean435-rms-counterexample.txt) proves
`RmsCounterexample.old_rms_statement_false` with only `propext`,
`Classical.choice`, and `Quot.sound`. On `Bool` with its trivial sigma algebra
and probability measure, take `g = id`, `f = 0`, `s = 1`, and `fhat` with values
`1` and `-1`. Both premise distances are constant one. The measured distance
takes values zero and two and is not almost everywhere measurable. Its new
seminorm is infinity, while the proposed upper bound is two.

## Corrected migration

The reviewed migration adds one explicit premise to
`Measurement.rms_measurement_error`:

```lean
AEStronglyMeasurable (fun ω => dist (g (fhat ω)) (s ω)) μ
```

The two existing distance-measurability premises remain. The RMS inequality is
unchanged on this measurable domain. A measurable majorant alone cannot supply
the new premise; applications must establish it for the measured distance.
This preserves the intended finite, measurable statistical use while honestly
narrowing the earlier statement under the new dependency semantics. The frozen
public type contract is updated for this premise. The original counterexample
still refutes the old statement and does not refute the corrected theorem.

The remaining port updates module visibility and proof APIs, including the
new `MemLp` representation. The canonical vector conditional-expectation
identity and its Hilbert compatibility name are both retained. The local
`FreeFoundationsApi` library has a distinct module name from MathEconLib's
upstream `ApiStability` library.

To reproduce the negative result from `src/lean` under the pinned 4.35
dependencies:

```sh
lake env lean --stdin < compatibility/lean435-rms-counterexample.txt
```

The counterexample is retained as historical compatibility evidence, not as a
production module. Run the current build, API coverage, source proof audit, and
checker regression tests for the corrected library. Public type contracts
freeze interfaces rather than the bodies of dependency definitions; clean
builds and mathematical review remain necessary alongside signature checks.
