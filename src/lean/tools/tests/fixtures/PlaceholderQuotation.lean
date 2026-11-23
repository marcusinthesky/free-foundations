import Lean
open Lean Elab Tactic
macro "unused_sorry_placeholder" : tactic => `(tactic| sorry)
macro "unused_admit_placeholder" : tactic => `(tactic| admit)
example : True := True.intro
