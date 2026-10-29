import FreeFoundations
import Lean

/-!
# Transitive axiom audit

Run `lake env lean Audit.lean` after `lake build`. Selection uses the originating module,
not the declaration's namespace, so private helpers and declarations outside the project's
namespace are included. Every selected declaration is checked even when it is unused.
The only permitted dependencies are Lean's standard classical foundations.
This file is an audit command, not an import of the mathematical library.
-/

open Lean Elab Command

namespace FreeFoundationsAudit

/-- Check every declaration originating in one of the given module trees. -/
def audit (roots : Array Name) : CommandElabM Unit := do
  let env := (← getEnv).setExporting false
  let mut count := 0
  let mut theorems := 0
  let mut privateCount := 0
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
