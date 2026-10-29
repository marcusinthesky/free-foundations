module

public import Lean

@[expose] public section

private theorem unusedPrivateGap : True := sorry
theorem publicCleanProof : True := True.intro

example : True := sorry
