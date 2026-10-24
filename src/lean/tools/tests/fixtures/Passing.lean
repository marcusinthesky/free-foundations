import Lean

-- The words sorry, admit, axiom and native_decide in comments are not proofs.
/- import AModuleThatDoesNotExist -/
def harmlessText : String := "sorry admit axiom unsafe native_decide"
def harmlessInterpolation : String := s!"{(7 : Nat)}: sorry"
def harmlessNativeInterpolation : String := s!"native_decide{(7 : Nat)}native_decide"
def harmlessPlaceholderInterpolation : String := s!"sorry{(7 : Nat)}admit"

private theorem privateProof : True := True.intro
theorem publicProof : True := privateProof

theorem classicalFoundation {P Q : Prop} (h : P ↔ Q) : P = Q := propext h
noncomputable def choiceFoundation {α : Sort u} (h : Nonempty α) : α := Classical.choice h
theorem quotientFoundation {α : Sort u} (r : α → α → Prop) {a b : α} (h : r a b) :
    Quot.mk r a = Quot.mk r b := Quot.sound h

example : True := True.intro
example : 1 + 1 = 2 := rfl
namespace Another
example : True := by trivial
end Another
