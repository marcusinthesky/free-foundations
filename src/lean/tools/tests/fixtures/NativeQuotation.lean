import Lean
open Lean Elab Tactic
macro "unused_native_reflection" : tactic => `(tactic| native_decide)
example : True := True.intro
