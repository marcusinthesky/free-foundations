import Lean

/-!
# Exact public type contracts

Unlike applying a theorem to an example, this command compares the declaration's
complete type with an independently written expected type. Universe arity and
implicit/explicit telescope binders are checked as well as definitional equality.
This is verification tooling, not a source of mathematical axioms.
-/

open Lean Meta Elab Command Term

namespace FreeFoundations.ApiCheck

/-- Persist successfully checked contracts; commented-out commands do not count. -/
initialize signatureContracts : SimplePersistentEnvExtension Name (Array Name) ←
  registerSimplePersistentEnvExtension {
    name := `FreeFoundations.ApiCheck.signatureContracts
    addEntryFn := fun entries name => entries.push name
    addImportedFn := fun entries => entries.foldl (· ++ ·) #[] }

private partial def checkBinders (expected actual : Expr) : MetaM Unit := do
  let expected ← whnf expected
  let actual ← whnf actual
  match expected, actual with
  | .forallE n et eb ei, .forallE _ aty ab ai =>
    unless ei == ai do
      throwError "signature binder visibility changed at {n}: expected {repr ei}, found {repr ai}"
    checkBinders et aty
    withLocalDecl n ei et fun x =>
      checkBinders (eb.instantiate1 x) (ab.instantiate1 x)
  | .forallE .., _ | _, .forallE .. =>
    throwError "signature telescope changed"
  | _, _ => pure ()

syntax (name := assertSignature) "#assert_signature " ident "[" ident,* "]" ":" term : command

@[command_elab assertSignature] def elabAssertSignature : CommandElab := fun stx => do
  let `(#assert_signature $decl:ident [$universes:ident,*] : $expectedSyntax:term) := stx
    | throwUnsupportedSyntax
  let name := decl.getId
  if (signatureContracts.getState (← getEnv)).contains name then
    throwErrorAt decl "duplicate signature contract for {name}"
  let info ← getConstInfo name
  let universeNames := universes.getElems.toList.map (·.getId)
  unless universeNames.eraseDups.length == universeNames.length do
    throwErrorAt decl "signature universe correspondence must be injective"
  let levels := universeNames.map Level.param
  unless info.levelParams.length == levels.length do
    throwErrorAt decl "universe arity changed for {name}: expected {levels.length}, found {info.levelParams.length}"
  liftTermElabM do
    let expected ← elabType expectedSyntax
    synthesizeSyntheticMVarsNoPostponing
    let expected ← instantiateMVars expected
    if expected.hasMVar || expected.hasLevelMVar then
      throwErrorAt expectedSyntax "signature contract contains unresolved metavariables"
    let actual := info.type.instantiateLevelParams info.levelParams levels
    unless ← isDefEq expected actual do
      throwErrorAt decl "type contract changed for {name}\nexpected: {expected}\nactual: {actual}"
    checkBinders expected actual
  modifyEnv fun env => signatureContracts.addEntry env name

end FreeFoundations.ApiCheck
