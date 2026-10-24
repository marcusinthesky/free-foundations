# MathEconLib compatibility trial

The integration starts from `9713a8d`. The selected reference is
[MathEconLib `6c0e61e`](https://github.com/matheconlib/matheconlib/tree/6c0e61ed4c95252e2c985ccc456e2c53617fb941),
whose toolchain is Lean 4.35 and whose manifest pins mathlib
`56a005855ea17e0b0958f73ec801ae140b0a1679`.

An isolated trial installed Lean 4.35 and fetched those exact dependencies.
The selected upstream `FinDist.Measure` and `FinDist.ConditionalOn` modules
compiled. The original project build failed in `Alignment`, `Network`, `Kernel`,
`Score`, and `Measurement`. Small proof-only repairs made `Network`, `Kernel`,
and the new bandwidth results compile; those trial repairs were not adopted.

The decisive blocker is semantic. Mathlib 4.35 defines `eLpNorm f p μ` to be
infinite when `f` is not almost everywhere strongly measurable. The existing
`Measurement.rms_measurement_error` only assumes measurability of the prediction
and alignment distances. Those premises do not imply measurability of the
measured distance, so its unchanged statement is false under the new definition.

The accompanying [counterexample source](lean435-rms-counterexample.txt) was
compiled with Lean 4.35 against the pinned trial mathlib. It proves
`RmsCounterexample.old_rms_statement_false`, with dependencies only on
`propext`, `Classical.choice`, and `Quot.sound`.
On `Bool` with the trivial sigma algebra and its probability measure, set
`g = id`, `f = 0`, `s = 1`, and let `fhat` take values `1` and `-1`.
Both premise distances are constant one. The measured distance takes values
zero and two, is not AE measurable, and therefore has new seminorm infinity;
the proposed upper bound is two.

This triggers the agreed fallback: Lean 4.31 and its mathlib pin are retained.
Changing the theorem's assumptions, replacing its seminorm, or accepting
changed economic semantics would require a separate reviewed migration.
The finite facade instead uses existing simplex/PMF infrastructure directly,
with MathEconLib source attribution and its scoped Apache license. The proof
audit follows the upstream approach through an independently implemented
4.31 frontend. No MathEconLib dependency is added to the project.

To reproduce the negative compatibility result in a separate project pinned
to the trial toolchain and mathlib:

```sh
lake env lean --stdin < lean435-rms-counterexample.txt
```

The evidence is stored as text because it deliberately uses the rejected
toolchain's semantics. It is not a production module in the 4.31 library.
Public type contracts freeze interfaces, not the bodies of dependency
definitions; this trial illustrates why clean builds and mathematical review
remain necessary alongside signature checks.
