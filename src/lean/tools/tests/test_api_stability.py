"""Regression tests for frozen public Lean type contracts (stdlib only)."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
HEADER = """\
import ApiStability.Check
import Mathlib.Analysis.InnerProductSpace.PiL2
set_option autoImplicit false
"""


class ApiStabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Compile the checker source itself, so stale artifacts cannot conceal a regression.
        artifact = PROJECT / ".lake/build/lib/lean/ApiStability/Check.olean"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        checked = subprocess.run(
            ["lake", "env", "lean", "-o", str(artifact), "ApiStability/Check.lean"],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            timeout=90,
            check=False,
        )
        if checked.returncode:
            raise RuntimeError(checked.stdout + checked.stderr)

    def check_contract(
        self, source: str, *, accepts: bool, diagnostic: str = ""
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="lean-api-contract-") as directory:
            fixture = Path(directory) / "Contract.lean"
            fixture.write_text(HEADER + textwrap.dedent(source))
            checked = subprocess.run(
                ["lake", "env", "lean", str(fixture)],
                cwd=PROJECT,
                text=True,
                capture_output=True,
                timeout=90,
                check=False,
            )
        output = checked.stdout + checked.stderr
        if accepts:
            self.assertEqual(checked.returncode, 0, output)
            self.assertNotIn("declaration uses 'sorry'", output)
        else:
            self.assertNotEqual(checked.returncode, 0, output)
            self.assertIn(diagnostic, output)

    def test_binder_renaming_and_definitional_alias_pass(self) -> None:
        self.check_contract(
            """
            universe u
            theorem same {α : Type u} (original : α) : original = original := rfl
            #assert_signature same [u] : ∀ {α : Type u} (renamed : α), renamed = renamed
            abbrev NaturalFunction := Nat → Nat
            def identityNat (value : Nat) : Nat := value
            #assert_signature identityNat [] : NaturalFunction
            """,
            accepts=True,
        )

    def test_coverage_uses_checked_commands_and_rejects_duplicates(self) -> None:
        self.check_contract(
            """
            def identityNat (n : Nat) : Nat := n
            #assert_signature identityNat [] : Nat → Nat
            /- #assert_signature disabled [] : False -/
            open Lean Elab Command
            run_cmd do
              let checked := FreeFoundations.ApiCheck.signatureContracts.getState (← getEnv)
              unless checked == #[`identityNat] do
                throwError "coverage included an unchecked contract"
            """,
            accepts=True,
        )
        self.check_contract(
            """
            def identityNat (n : Nat) : Nat := n
            #assert_signature identityNat [] : Nat → Nat
            #assert_signature identityNat [] : Nat → Nat
            """,
            accepts=False,
            diagnostic="duplicate signature contract",
        )

    def test_added_and_removed_hypotheses_are_rejected(self) -> None:
        cases = {
            "added": """
                theorem same (n : Nat) : n = n := rfl
                #assert_signature same [] : ∀ (n : Nat), 0 ≤ n → n = n
                """,
            "removed": """
                theorem retained (p : Prop) (hypothesis : p) : p := hypothesis
                #assert_signature retained [] : ∀ (p : Prop), p
                """,
        }
        for name, source in cases.items():
            with self.subTest(change=name):
                self.check_contract(
                    source, accepts=False, diagnostic="type contract changed"
                )

    def test_changed_bound_is_rejected(self) -> None:
        self.check_contract(
            """
            theorem bounded (x : ℝ) (hx : x ≤ 1) : x ≤ 1 := hx
            #assert_signature bounded [] : ∀ (x : ℝ), x ≤ 2 → x ≤ 2
            """,
            accepts=False,
            diagnostic="type contract changed",
        )

    def test_euclidean_and_coordinate_supremum_norms_are_distinguished(self) -> None:
        self.check_contract(
            """
            theorem euclidean_norm (v : EuclideanSpace ℝ (Fin 2)) : 0 ≤ ‖v‖ := norm_nonneg v
            #assert_signature euclidean_norm [] :
              ∀ (v : EuclideanSpace ℝ (Fin 2)), 0 ≤ ‖v.ofLp‖
            """,
            accepts=False,
            diagnostic="type contract changed",
        )

    def test_changed_universe_arity_is_rejected(self) -> None:
        self.check_contract(
            """
            universe u v
            def identity {α : Type u} (x : α) : α := x
            #assert_signature identity [u, v] : ∀ {α : Type u}, α → α
            """,
            accepts=False,
            diagnostic="universe arity changed",
        )

    def test_changed_universe_relationship_is_rejected(self) -> None:
        self.check_contract(
            """
            universe u v
            def firstType (α : Type u) (_β : Type v) : Type u := α
            #assert_signature firstType [u, v] : (α : Type v) → (β : Type u) → Type v
            """,
            accepts=False,
            diagnostic="type contract changed",
        )

    def test_binder_visibility_changes_are_rejected(self) -> None:
        cases = {
            "outer": """
                def identityNat (x : Nat) : Nat := x
                #assert_signature identityNat [] : {x : Nat} → Nat
                """,
            "strict_implicit": """
                def strictImplicit ⦃n : Nat⦄ (x : Nat) : Nat := n + x
                #assert_signature strictImplicit [] : {n : Nat} → Nat → Nat
                """,
            "nested": """
                def applyImplicit (f : {n : Nat} → Nat) : Nat := f (n := 0)
                #assert_signature applyImplicit [] : (f : (n : Nat) → Nat) → Nat
                """,
            "instance": """
                universe u
                def withInstance {α : Type u} [Inhabited α] (x : α) : α := x
                #assert_signature withInstance [u] : ∀ {α : Type u}, Inhabited α → α → α
                """,
        }
        for name, source in cases.items():
            with self.subTest(change=name):
                self.check_contract(
                    source,
                    accepts=False,
                    diagnostic="signature binder visibility changed",
                )

    def test_unresolved_expected_type_is_rejected(self) -> None:
        self.check_contract(
            """
            def identityNat (x : Nat) : Nat := x
            #assert_signature identityNat [] : _
            """,
            accepts=False,
            diagnostic="signature contract contains unresolved",
        )

    def test_duplicate_universe_identifiers_are_rejected(self) -> None:
        self.check_contract(
            """
            universe u v
            def pairTypes (α : Type u) (β : Type v) := α × β
            #assert_signature pairTypes [u, u] : (α : Type u) → (β : Type u) → Type u
            """,
            accepts=False,
            diagnostic="universe",
        )

    def test_unresolved_expected_universe_is_rejected(self) -> None:
        self.check_contract(
            """
            universe u
            def identity {α : Type u} (x : α) : α := x
            #assert_signature identity [u] : ∀ {α : Type _}, α → α
            """,
            accepts=False,
            diagnostic="signature contract contains unresolved",
        )


if __name__ == "__main__":
    unittest.main()
