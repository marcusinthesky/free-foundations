import Lean

/-!
Original proof-integrity frontend for this repository, using Lean's public APIs.
It checks declaration types and values, including private and discarded example
declarations. The executable is part of the explicitly documented audit TCB.
-/

open Lean Elab

namespace ProofIntegrity

def allowedAxioms : Array Name := #[``propext, ``Classical.choice, ``Quot.sound]

structure Issue where
  kind : String
  declaration : String
  line : Nat := 0
  column : Nat := 0
  dependencies : Array String := #[]
  detail : String := ""
  deriving ToJson, BEq

structure DeclarationRecord where
  name : String
  kind : String
  privateDeclaration : Bool
  line : Nat
  column : Nat
  axioms : Array String
  deriving ToJson

structure Report where
  schema : Nat := 1
  mode : String
  module : String
  source : String := ""
  declarations : Nat := 0
  privateDeclarations : Nat := 0
  examples : Nat := 0
  bodyNodes : Nat := 0
  issues : Array Issue := #[]
  imports : Array String := #[]
  declarationRecords : Array DeclarationRecord := #[]
  deriving ToJson

def options : Options := ({} : Options)
  |>.setBool `Elab.async false
  |>.setBool `internal.cmdlineSnapshots false

def withEnv (env : Environment) (action : CoreM α) : IO α := do
  return (← action.toIO { fileName := "<proof-integrity>", fileMap := default, options }
    { env := env.setExporting false }).1

def unexpected (axioms : Array Name) : Array String :=
  axioms.filterMap fun ax => if allowedAxioms.contains ax then none else some ax.toString

def constantKind : ConstantInfo → String
  | .axiomInfo _ => "axiom"
  | .defnInfo _ => "definition"
  | .thmInfo _ => "theorem"
  | .opaqueInfo _ => "opaque"
  | .quotInfo _ => "quotient"
  | .inductInfo _ => "inductive"
  | .ctorInfo _ => "constructor"
  | .recInfo _ => "recursor"

def inspectConstant (env : Environment) (name : Name) (line column : Nat := 0) :
    IO (Array Issue × Option DeclarationRecord) := do
  let some info := env.find? name
    | return (#[{ kind := "missing-declaration", declaration := name.toString, line, column }], none)
  let ranges ← withEnv env (findDeclarationRanges? name)
  let hasPosition := line != 0
  let line := if hasPosition then line else ranges.map (·.range.pos.line) |>.getD 0
  let column := if hasPosition then column else ranges.map (·.range.pos.column) |>.getD 0
  let mut issues := #[]
  if info.isUnsafe then
    issues := issues.push { kind := "unsafe-declaration", declaration := name.toString, line, column }
  if info.type.hasSorry || (info.value? (allowOpaque := true)).any (·.hasSorry) then
    issues := issues.push { kind := "placeholder", declaration := name.toString, line := line, column := column, dependencies := #["sorryAx"] }
  let deps ← withEnv env (collectAxioms name)
  let bad := unexpected deps
  if !bad.isEmpty then
    issues := issues.push { kind := "unsupported-axioms", declaration := name.toString, line := line, column := column, dependencies := bad }
  return (issues, some { name := name.toString, kind := constantKind info, privateDeclaration := isPrivateName name, line, column, axioms := deps.map Name.toString })

def inspectExpr (env : Environment) (name : Name) (expr : Expr) (line column : Nat) : IO (Array Issue) := do
  let mut issues := #[]
  if expr.hasSorry then
    issues := issues.push { kind := "placeholder", declaration := name.toString, line := line, column := column, dependencies := #["sorryAx"] }
  let mut bad : Array String := #[]
  for dep in expr.getUsedConstants do
    for ax in unexpected (← withEnv env (collectAxioms dep)) do
      if !bad.contains ax then bad := bad.push ax
  if !bad.isEmpty then
    issues := issues.push { kind := "unsupported-axioms", declaration := name.toString, line := line, column := column, dependencies := bad }
  return issues

def nameHasExample : Name → Bool
  | .str parent component => component == "_example" || nameHasExample parent
  | .num parent _ => nameHasExample parent
  | .anonymous => false

def isExample (name : Name) : Bool := nameHasExample name.eraseMacroScopes

def forbiddenProofKeyword (value : String) : Bool :=
  #["sorry", "admit", "native_decide"].contains value

def nameProofKeyword : Name → Option String
  | .str _ component => if forbiddenProofKeyword component then some component else none
  | .num parent _ => nameProofKeyword parent
  | .anonymous => none

/-- Walk Lean's parsed commands, including uninvoked syntax quotations. String
literal payloads and comments are not identifier/keyword syntax atoms. -/
partial def forbiddenProofSyntax (stx : Syntax) : Array (Syntax × String) :=
  match stx with
  | .atom _ value => if forbiddenProofKeyword value then #[(stx, value)] else #[]
  | .ident _ _ value _ => match nameProofKeyword value.eraseMacroScopes with
    | some keyword => #[(stx, keyword)]
    | none => #[]
  | .node _ _ args => args.foldl (fun found arg => found ++ forbiddenProofSyntax arg) #[]
  | .missing => #[]

structure Body where
  name : Name
  env : Environment
  value : Expr
  line : Nat
  column : Nat

def exampleBodies (state : Command.State) : Array Body :=
  state.infoState.trees.toArray.foldl (init := #[]) fun bodies tree =>
    tree.foldInfo (fun ctx info bodies => Id.run do
      let some parent := ctx.parentDecl? | return bodies
      if !isExample parent then return bodies
      let some body := Term.getBodyInfo? info | return bodies
      let some value := body.value? | return bodies
      let pos := ctx.fileMap.toPosition (info.stx.getPos?.getD 0)
      let env := if (ctx.env.setExporting false).contains parent then ctx.env
        else ctx.cmdEnv?.getD ctx.env
      return bodies.push { name := parent, env, value, line := pos.line, column := pos.column })
      bodies

def localConstants (env : Environment) : Array (Name × ConstantInfo) :=
  env.checked.get.constants.foldStage2 (fun result name info => result.push (name, info)) #[]

def messagesIssues (messages : MessageLog) : IO (Array Issue) := do
  let mut result := #[]
  for msg in messages.toList do
    if msg.severity == .error then
      result := result.push { kind := "elaboration-error", declaration := "", line := msg.pos.line, column := msg.pos.column, detail := (← msg.data.toString) }
  return result

def sourceReport (moduleName : Name) (path : String) (headersOnly : Bool) : IO Report := do
  let text ← IO.FS.readFile path
  let input := Parser.mkInputContext text path
  let (header, parser, messages) ← Parser.parseHeader input
  let mut report : Report := { mode := (if headersOnly then "header" else "source"), module := moduleName.toString, source := path, imports := (Elab.headerToImports header).map (·.module.toString), issues := (← messagesIssues messages) }
  if headersOnly || !report.issues.isEmpty then return report
  let (env, messages) ← processHeader header options messages input (trustLevel := 0)
    (mainModule := moduleName)
  if messages.hasErrors then return { report with issues := ← messagesIssues messages }
  let state ← IO.processCommands input parser (Command.mkState env messages options)
  report := { report with issues := ← messagesIssues state.commandState.messages }
  if !report.issues.isEmpty then return report
  for command in state.commands do
    for (token, keyword) in forbiddenProofSyntax command do
      let pos := input.fileMap.toPosition (token.getPos?.getD 0)
      report := { report with issues := report.issues.push {
        kind := (if keyword == "native_decide" then "native-decide-syntax" else "placeholder-syntax"),
        declaration := "", line := pos.line, column := pos.column,
        detail := keyword ++ " is excluded even in an uninvoked syntax quotation" } }
  let env := state.commandState.env.setExporting false
  for (name, info) in localConstants env do
    report := { report with declarations := report.declarations + 1, privateDeclarations := report.privateDeclarations + (if isPrivateName name then 1 else 0) }
    if info matches .axiomInfo _ then
      report := { report with issues := report.issues.push {
        kind := "local-axiom", declaration := name.toString } }
    let (issues, record) ← inspectConstant env name
    report := { report with issues := report.issues ++ issues, declarationRecords := report.declarationRecords ++ record.toArray }
  let bodies := exampleBodies state.commandState
  report := { report with examples := bodies.size, bodyNodes := bodies.size }
  for body in bodies do
    if (body.env.setExporting false).contains body.name then
      let (issues, record) ← inspectConstant (body.env.setExporting false) body.name body.line body.column
      report := { report with issues := report.issues ++ issues, declarationRecords := report.declarationRecords ++ record.toArray }
    -- Inspect the elaborated expression even when the frontend did not retain a
    -- temporary declaration. No name-only cache is used for repeated examples.
    report := { report with issues := report.issues ++
      (← inspectExpr body.env body.name body.value body.line body.column) }
  return report

def moduleReport (moduleName : Name) : IO Report := do
  let env ← importModules #[{ module := moduleName }] options (trustLevel := 0)
    (loadExts := true) (level := .private)
  let mut report : Report := { mode := "module", module := moduleName.toString }
  for (name, info) in env.constants.toList do
    let some index := env.getModuleIdxFor? name | continue
    if env.header.moduleNames[index.toNat]! != moduleName then continue
    report := { report with declarations := report.declarations + 1, privateDeclarations := report.privateDeclarations + (if isPrivateName name then 1 else 0) }
    if info matches .axiomInfo _ then
      report := { report with issues := report.issues.push {
        kind := "local-axiom", declaration := name.toString } }
    let (issues, record) ← inspectConstant env name
    report := { report with issues := report.issues ++ issues, declarationRecords := report.declarationRecords ++ record.toArray }
  return report

end ProofIntegrity

unsafe def main (args : List String) : IO UInt32 := do
  Lean.initSearchPath (← Lean.findSysroot)
  Lean.enableInitializersExecution
  try
    let report ← match args with
      | ["header", name, path] => ProofIntegrity.sourceReport name.toName path true
      | ["source", name, path] => ProofIntegrity.sourceReport name.toName path false
      | ["module", name] => ProofIntegrity.moduleReport name.toName
      | _ => throw <| IO.userError "usage: CheckProofIntegrity (header|source) MODULE FILE | module MODULE"
    let issues := report.issues.foldl (init := #[]) fun result issue =>
      if result.contains issue then result else result.push issue
    let report := { report with issues }
    IO.println s!"PROOF_INTEGRITY_JSON {Lean.Json.compress (Lean.toJson report)}"
    return if report.issues.isEmpty then 0 else 1
  catch ex =>
    IO.eprintln s!"proof-integrity backend failed: {ex}"
    return 2
