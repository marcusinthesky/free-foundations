module

public import Lean

@[expose] public section

private theorem privateModuleProof : True := True.intro
theorem publicModuleProof : True := privateModuleProof

example : True := True.intro
