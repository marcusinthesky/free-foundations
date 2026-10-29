"""Substantive integration regressions for the elaborated proof audit (stdlib only)."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

TOOLS = Path(__file__).resolve().parents[1]
PROJECT = TOOLS.parent
FIXTURES = TOOLS / "tests/fixtures"
SPEC = importlib.util.spec_from_file_location(
    "proof_integrity", TOOLS / "proof_integrity.py"
)
assert SPEC and SPEC.loader
DRIVER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DRIVER)


class ProofIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        command = subprocess.run(
            ["lake", "env", "printenv", "LEAN_PATH"],
            cwd=PROJECT,
            text=True,
            capture_output=True,
            check=True,
        )
        cls.env = os.environ.copy()
        cls.env["LEAN_PATH"] = command.stdout.strip()

    def source(self, name: str, env: dict[str, str] | None = None) -> tuple[int, dict]:
        return DRIVER.backend(
            "source",
            name,
            FIXTURES / f"{name}.lean",
            project=PROJECT,
            env=env or self.env,
        )

    def test_standard_foundations_comments_strings_and_private_proofs_pass(
        self,
    ) -> None:
        status, report = self.source("Passing")
        self.assertEqual(status, 0)
        self.assertEqual(report["examples"], 3)
        self.assertGreaterEqual(report["privateDeclarations"], 1)
        self.assertFalse(report["issues"])

    def test_substantive_rejection_fixtures(self) -> None:
        fixtures = json.loads((TOOLS / "tests/fixtures.json").read_text())["fixtures"]
        for name, expected in fixtures.items():
            if expected != "reject" or name.startswith("Imported"):
                continue
            with self.subTest(fixture=name):
                status, report = self.source(name)
                self.assertEqual(status, 1, report)
                self.assertTrue(report["issues"])
                expected_kind = {
                    "UnfinishedGoal": "elaboration-error",
                    "LocalAxiom": "local-axiom",
                    "UnsafeDefinition": "unsafe-declaration",
                    "NativeExample": "unsupported-axioms",
                    "NativeQuotation": "native-decide-syntax",
                    "PlaceholderQuotation": "placeholder-syntax",
                }.get(name, "placeholder")
                self.assertIn(
                    expected_kind, {issue["kind"] for issue in report["issues"]}, report
                )

    def test_module_system_private_declarations_and_examples_are_audited(self) -> None:
        status, report = self.source("ModulePassing")
        self.assertEqual(status, 0, report)
        self.assertGreaterEqual(report["privateDeclarations"], 1)
        self.assertEqual(report["examples"], 1)
        status, report = self.source("ModulePrivate")
        self.assertEqual(status, 1, report)
        self.assertGreaterEqual(report["privateDeclarations"], 1)
        self.assertEqual(report["examples"], 1)
        self.assertTrue(
            any(
                issue["kind"] == "placeholder"
                and "unusedPrivateGap" in issue["declaration"]
                for issue in report["issues"]
            ),
            report,
        )
        self.assertTrue(
            any(
                issue["kind"] == "placeholder" and issue["line"] == 10
                for issue in report["issues"]
            ),
            report,
        )

    def test_unused_sorry_and_admit_quotations_are_rejected(self) -> None:
        status, report = self.source("PlaceholderQuotation")
        self.assertEqual(status, 1)
        self.assertEqual(report["examples"], 1)
        self.assertEqual(
            {
                issue["line"]
                for issue in report["issues"]
                if issue["kind"] == "placeholder-syntax"
            },
            {3, 4},
        )
        self.assertFalse(
            any(issue["kind"] == "unsupported-axioms" for issue in report["issues"]),
            report,
        )

    def test_repeated_discarded_examples_are_not_deduplicated_by_name(self) -> None:
        status, report = self.source("SorryExamples")
        self.assertEqual(status, 1)
        self.assertEqual(report["examples"], 4)
        bad_lines = {
            issue["line"]
            for issue in report["issues"]
            if issue["kind"] == "placeholder"
        }
        self.assertEqual(bad_lines, {3, 6})

    def test_native_reflection_is_rejected_by_transitive_axiom_policy(self) -> None:
        status, report = self.source("NativeExample")
        self.assertEqual(status, 1)
        dependencies = {
            dep for issue in report["issues"] for dep in issue["dependencies"]
        }
        self.assertTrue(dependencies - set(DRIVER.ALLOWED_AXIOMS), report)
        self.assertEqual(report["examples"], 2)

    def test_per_declaration_dependencies_include_allowed_foundations(self) -> None:
        status, report = self.source("Passing")
        self.assertEqual(status, 0)
        self.assertTrue(report["declarationRecords"])
        axioms = {
            axiom
            for declaration in report["declarationRecords"]
            for axiom in declaration["axioms"]
        }
        self.assertEqual(axioms, set(DRIVER.ALLOWED_AXIOMS))
        self.assertTrue(
            any(
                declaration["privateDeclaration"]
                for declaration in report["declarationRecords"]
            )
        )

    def test_imported_axioms_in_example_proofs_and_types_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lean-integrity-import-") as directory:
            artifacts = Path(directory)
            command = [
                "lean",
                "--root=" + str(FIXTURES),
                "-o",
                str(artifacts / "UntrustedSupport.olean"),
                str(FIXTURES / "UntrustedSupport.lean"),
            ]
            compiled = DRIVER.run(command, project=PROJECT, env=self.env)
            self.assertEqual(compiled.returncode, 0, compiled.stdout + compiled.stderr)
            env = self.env.copy()
            env["LEAN_PATH"] = str(artifacts) + os.pathsep + env["LEAN_PATH"]
            for name, axiom in [
                ("ImportedExample", "ExternalSupport.unsupported"),
                ("ImportedExampleType", "ExternalSupport.unsupportedNumber"),
            ]:
                with self.subTest(fixture=name):
                    status, report = self.source(name, env)
                    self.assertEqual(status, 1)
                    dependencies = {
                        dep
                        for issue in report["issues"]
                        for dep in issue["dependencies"]
                    }
                    self.assertIn(axiom, dependencies)
                    if name == "ImportedExampleType":
                        self.assertEqual(report["examples"], 2)
                        self.assertTrue(
                            any(issue["line"] == 3 for issue in report["issues"]),
                            report,
                        )

    def test_compiled_module_includes_unused_private_declaration(self) -> None:
        for name in ("SorryPrivate", "ModulePrivate"):
            with (
                self.subTest(fixture=name),
                tempfile.TemporaryDirectory(
                    prefix="lean-integrity-private-"
                ) as directory,
            ):
                artifacts = Path(directory)
                command = [
                    "lean",
                    "--root=" + str(FIXTURES),
                    "-o",
                    str(artifacts / f"{name}.olean"),
                    str(FIXTURES / f"{name}.lean"),
                ]
                compiled = DRIVER.run(command, project=PROJECT, env=self.env)
                self.assertEqual(
                    compiled.returncode, 0, compiled.stdout + compiled.stderr
                )
                env = self.env.copy()
                env["LEAN_PATH"] = str(artifacts) + os.pathsep + env["LEAN_PATH"]
                status, report = DRIVER.backend(
                    "module", name, None, project=PROJECT, env=env
                )
                self.assertEqual(status, 1, report)
                self.assertGreaterEqual(report["privateDeclarations"], 1)

    def make_project(self, directory: str) -> Path:
        project = Path(directory)
        (project / "tools/tests/fixtures").mkdir(parents=True)
        shutil.copyfile(
            TOOLS / "CheckProofIntegrity.lean",
            project / "tools/CheckProofIntegrity.lean",
        )
        shutil.copyfile(PROJECT / "lean-toolchain", project / "lean-toolchain")
        (project / "tools/tests/fixtures.json").write_text('{"fixtures": {}}\n')
        return project

    def test_orphan_sources_and_dependencies_are_built_and_audited(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lean-integrity-orphan-") as directory:
            project = self.make_project(directory)
            (project / "Dependency.lean").write_text(
                "theorem independentProof : True := True.intro\n"
            )
            (project / "Orphan.lean").write_text(
                "import Dependency\nprivate theorem unused : True := sorry\n"
            )
            report = DRIVER.audit(
                project, project / "report.json", self.env, verbose=False
            )
            self.assertTrue(report["complete"])
            self.assertEqual(report["coverage"]["discoveredFiles"], 3)
            self.assertEqual(report["coverage"]["compiledTrustedFiles"], 1)
            self.assertEqual(report["coverage"]["auditedFiles"], 2)
            self.assertTrue(report["issues"])
            orphan = next(
                entry for entry in report["sources"] if entry["module"] == "Orphan"
            )
            self.assertTrue(orphan["compiled"])
            self.assertTrue(orphan["issues"])
            self.assertEqual(len(orphan["sha256"]), 64)
            self.assertEqual(orphan["sha256"], orphan["sha256After"])

    def test_fixture_exclusion_is_exact_not_a_directory_skip(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="lean-integrity-exclusion-"
        ) as directory:
            project = self.make_project(directory)
            (project / "tools/tests/fixtures/Known.lean").write_text(
                "axiom knownBad : True\n"
            )
            (project / "tools/tests/fixtures/Unexpected.lean").write_text(
                "axiom newBad : True\n"
            )
            (project / "tools/tests/fixtures.json").write_text(
                '{"fixtures": {"Known": "reject"}}\n'
            )
            sources, excluded = DRIVER.discover(project)
            self.assertNotIn("tools.tests.fixtures.Known", sources)
            self.assertIn("tools.tests.fixtures.Unexpected", sources)
            self.assertEqual(set(excluded), {"tools/tests/fixtures/Known.lean"})

    def test_production_cannot_import_an_excluded_fixture(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="lean-integrity-fixture-import-"
        ) as directory:
            project = self.make_project(directory)
            (project / "tools/tests/fixtures/Known.lean").write_text(
                "axiom knownBad : True\n"
            )
            (project / "tools/tests/fixtures.json").write_text(
                '{"fixtures": {"Known": "reject"}}\n'
            )
            (project / "Production.lean").write_text(
                "import tools.tests.fixtures.Known\n"
            )
            report = DRIVER.audit(
                project, project / "report.json", self.env, verbose=False
            )
            self.assertFalse(report["complete"])
            self.assertIn(
                "excluded-fixture-import", {issue["kind"] for issue in report["issues"]}
            )

    def test_compile_failure_does_not_hide_independent_sources(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix="lean-integrity-compile-error-"
        ) as directory:
            project = self.make_project(directory)
            (project / "AInvalid.lean").write_text(
                "theorem unfinished : True := by exact ?_\n"
            )
            (project / "ZIndependent.lean").write_text(
                "theorem independent : True := True.intro\n"
            )
            report = DRIVER.audit(
                project, project / "report.json", self.env, verbose=False
            )
            self.assertFalse(report["complete"])
            valid = next(
                entry
                for entry in report["sources"]
                if entry["module"] == "ZIndependent"
            )
            self.assertTrue(valid["compiled"])
            self.assertFalse(valid["issues"])

    def test_source_edit_during_audit_invalidates_hash_certificate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lean-integrity-edit-") as directory:
            project = self.make_project(directory)
            source = project / "Mutable.lean"
            source.write_text("theorem frozenProof : True := True.intro\n")
            original = DRIVER.backend

            def editing_backend(mode: str, module: str, path: Path | None, **kwargs):
                checked = original(mode, module, path, **kwargs)
                if mode == "source" and module == "Mutable":
                    source.write_text("theorem differentProof : True := True.intro\n")
                return checked

            with patch.object(DRIVER, "backend", side_effect=editing_backend):
                report = DRIVER.audit(
                    project, project / "report.json", self.env, verbose=False
                )
            self.assertFalse(report["complete"])
            self.assertIn(
                "source-changed-during-audit",
                {issue["kind"] for issue in report["issues"]},
            )

    def test_new_source_during_audit_invalidates_coverage_certificate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="lean-integrity-added-") as directory:
            project = self.make_project(directory)
            (project / "Original.lean").write_text(
                "theorem original : True := True.intro\n"
            )
            original = DRIVER.backend

            def adding_backend(mode: str, module: str, path: Path | None, **kwargs):
                checked = original(mode, module, path, **kwargs)
                if mode == "source" and module == "Original":
                    (project / "New.lean").write_text(
                        "axiom addedAfterDiscovery : True\n"
                    )
                return checked

            with patch.object(DRIVER, "backend", side_effect=adding_backend):
                report = DRIVER.audit(
                    project, project / "report.json", self.env, verbose=False
                )
            self.assertFalse(report["complete"])
            self.assertIn(
                "source-set-changed-during-audit",
                {issue["kind"] for issue in report["issues"]},
            )

    def test_dependency_cycle_is_a_hard_failure(self) -> None:
        with self.assertRaises(DRIVER.AuditError):
            DRIVER.topological_order(
                {"A": Path("A.lean"), "B": Path("B.lean")}, {"A": ["B"], "B": ["A"]}
            )


if __name__ == "__main__":
    unittest.main()
