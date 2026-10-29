module

import all FreeFoundations
import all FreeFoundations.Exposure
import all FreeFoundations.Alignment
import all FreeFoundations.Sufficiency
import all FreeFoundations.Network
import all FreeFoundations.Recovery
import all FreeFoundations.Measurement
import all FreeFoundations.Geometry
import all FreeFoundations.Kernel
import all FreeFoundations.Stability
import all FreeFoundations.Score
import all FreeFoundations.Value
import all FreeFoundations.Likelihood
import all FreeFoundations.MatrixBounds
import all FreeFoundations.GramDistance
import all FreeFoundations.ScoreStability
import all FreeFoundations.TaskInformation
import all FreeFoundations.Information
import all FreeFoundations.Transfer
import all FreeFoundations.Selection
import all FreeFoundations.TaskCoverage
import all FreeFoundations.Bandwidth
import all FreeFoundations.ReversibleNetwork
import all FreeFoundations.ComparativeStatics
import all FreeFoundations.EndToEnd
import all FreeFoundations.Decision
import all FreeFoundations.Dynamics
import all FreeFoundations.GeneratedTarget
import all FreeFoundations.ReadoutStability
import all FreeFoundations.StatisticalFinancial
import all FreeFoundations.FiniteProbability
import all FreeFoundations.FiniteProbabilityDecision
import all FreeFoundations.FiniteProbabilityFinancial
import all FreeFoundations.FiniteProbabilityOrder
import all FreeFoundations.RiskState
import all FreeFoundations.Proxy
import all FreeFoundations.Identifiability
import all FreeFoundations.Pipeline
public import Lean

@[expose] public section

/-!
# Transitive axiom audit

Run `lake env lean ModuleAudit.lean` after `lake build`. Selection uses the originating module,
not the declaration's namespace, so private helpers and declarations outside the project's
namespace are included. Every selected declaration is checked even when it is unused.
The only permitted dependencies are Lean's standard classical foundations.
This file is an audit command, not an import of the mathematical library.
-/

open Lean Elab Command

namespace FreeFoundationsAudit

/-- Check every declaration originating in one of the given module trees. -/
def audit (roots : Array Name) : CommandElabM Unit := do
  -- Each project module is imported with `all` above so theorem bodies and
  -- otherwise unused private declarations remain visible under Lean's module system.
  let env := (← getEnv).setExporting false
  let mut count : Nat := 0
  let mut theorems : Nat := 0
  let mut privateCount : Nat := 0
  let mut used : Array Name := #[]
  let allowed := #[``propext, ``Classical.choice, ``Quot.sound]
  for (name, info) in env.constants.toList do
    let origin := match env.getModuleIdxFor? name with
      | some idx => env.header.moduleNames[idx]!
      | none => env.mainModule
    if roots.any (·.isPrefixOf origin) then
      count := count + 1
      if info.isTheorem then theorems := theorems + 1
      if isPrivateName name then privateCount := privateCount + 1
      match info with
      | .axiomInfo _ => throwError "Project axiom: {name} (module {origin})"
      | _ => pure ()
      let deps ← collectAxioms name
      for dep in deps do
        unless allowed.contains dep do
          throwError "Unapproved axiom: {name} depends on {dep} (module {origin})"
        unless used.contains dep do used := used.push dep
  if count == 0 then throwError "No declarations found in module trees {roots}"
  logInfo m!"Axiom audit passed: {count} declarations ({theorems} theorems, \
    {privateCount} private declarations); dependencies {used.qsort Name.lt}"

end FreeFoundationsAudit

run_cmd FreeFoundationsAudit.audit #[`FreeFoundations]
