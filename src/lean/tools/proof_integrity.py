"""Audit every production Lean source, including private proofs and anonymous examples.

Only the exact checker implementation files and listed regression fixtures are
excluded from the proof policy. The excluded implementations are still compiled.
No source-word search is used: Lean parses headers and elaborates proof terms.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

SCHEMA = 1
PREFIX = "PROOF_INTEGRITY_JSON "
ALLOWED_AXIOMS = ["propext", "Classical.choice", "Quot.sound"]
TRUSTED_TOOLS = {
    "tools/CheckProofIntegrity.lean": "Proof-audit frontend; explicit trusted checker implementation",
    "FreeFoundationsApi/Check.lean": "Manuscript signature metaprogram; expected contracts remain audited",
}


class AuditError(RuntimeError):
    """The driver could not establish complete audit coverage."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(
    command: list[str], *, project: Path, env: dict[str, str]
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command, cwd=project, env=env, text=True, capture_output=True, check=False
    )


def backend(
    mode: str, module: str, source: Path | None, *, project: Path, env: dict[str, str]
) -> tuple[int, dict[str, Any]]:
    command = [
        "lean",
        "--run",
        str(project / "tools/CheckProofIntegrity.lean"),
        mode,
        module,
    ]
    if source is not None:
        command.append(str(source))
    result = run(command, project=project, env=env)
    if "PANIC at " in result.stdout or "PANIC at " in result.stderr:
        raise AuditError(
            f"Lean frontend panicked while checking {module}:\n"
            f"{result.stdout}{result.stderr}"
        )
    lines = [
        line[len(PREFIX) :]
        for line in result.stdout.splitlines()
        if line.startswith(PREFIX)
    ]
    if len(lines) != 1:
        raise AuditError(
            f"Backend did not produce exactly one report for {module}:\n"
            f"{result.stdout}{result.stderr}"
        )
    report = json.loads(lines[0])
    if report.get("schema") != SCHEMA:
        raise AuditError(f"Unsupported backend report schema for {module}")
    if result.returncode not in (0, 1):
        raise AuditError(f"Backend failed for {module}: {result.stdout}{result.stderr}")
    if bool(report["issues"]) != (result.returncode != 0):
        raise AuditError(f"Backend status disagrees with reported issues for {module}")
    return result.returncode, report


def fixture_exclusions(project: Path) -> dict[str, str]:
    manifest = project / "tools/tests/fixtures.json"
    if not manifest.is_file():
        raise AuditError(f"Missing exact fixture exclusion manifest: {manifest}")
    entries = json.loads(manifest.read_text())["fixtures"]
    excluded = {}
    for name in entries:
        relative = f"tools/tests/fixtures/{name}.lean"
        if not (project / relative).is_file():
            raise AuditError(f"Fixture exclusion refers to missing source: {relative}")
        excluded[relative] = "Explicit regression fixture, checked by the fixture suite"
    return excluded


def discover(project: Path) -> tuple[dict[str, Path], dict[str, str]]:
    """Discover source by path, never by namespace or the public import graph."""
    excluded = fixture_exclusions(project)
    sources = {}
    for path in sorted(project.rglob("*.lean")):
        relative = path.relative_to(project)
        if any(part in {".lake", ".git"} for part in relative.parts):
            continue
        key = relative.as_posix()
        if key in excluded:
            continue
        parts = relative.with_suffix("").parts
        if any("." in part for part in parts):
            raise AuditError(f"Ambiguous module path: {key}")
        module = ".".join(parts)
        if module in sources:
            raise AuditError(f"Duplicate module path: {module}")
        sources[module] = path
    if not sources:
        raise AuditError("No Lean sources discovered; refusing an empty audit")
    return sources, excluded


def topological_order(
    sources: dict[str, Path], imports: dict[str, list[str]]
) -> list[str]:
    order: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(module: str) -> None:
        if module in visiting:
            raise AuditError(f"Project import cycle involving {module}")
        if module in visited:
            return
        visiting.add(module)
        for dependency in sorted(set(imports[module])):
            if dependency in sources:
                visit(dependency)
        visiting.remove(module)
        visited.add(module)
        order.append(module)

    for module in sorted(sources):
        visit(module)
    return order


def metadata(project: Path, env: dict[str, str]) -> dict[str, Any]:
    git = run(["git", "rev-parse", "HEAD"], project=project, env=env)
    dirty = run(["git", "status", "--porcelain"], project=project, env=env)
    version = run(["lean", "--version"], project=project, env=env)
    if version.returncode:
        raise AuditError(f"Cannot determine Lean version: {version.stderr}")
    files = [
        "lean-toolchain",
        "lake-manifest.json",
        "tools/CheckProofIntegrity.lean",
        "tools/proof_integrity.py",
        "tools/tests/fixtures.json",
    ]
    manifest = project / "lake-manifest.json"
    packages = (
        json.loads(manifest.read_text()).get("packages", [])
        if manifest.is_file()
        else []
    )
    dependency_revisions = {}
    for package in packages:
        record = {key: package.get(key) for key in ("rev", "inputRev", "url", "type")}
        checkout = project / ".lake/packages" / package["name"]
        if checkout.is_dir() and package.get("type") == "git":
            checked = run(["git", "rev-parse", "HEAD"], project=checkout, env=env)
            record["actualRevision"] = (
                checked.stdout.strip() if checked.returncode == 0 else None
            )
        dependency_revisions[package["name"]] = record
    return {
        "gitRevision": git.stdout.strip() if git.returncode == 0 else None,
        "gitWorkingTreeDirty": bool(dirty.stdout.strip())
        if dirty.returncode == 0
        else None,
        "leanVersion": version.stdout.strip(),
        "leanToolchain": (project / "lean-toolchain").read_text().strip(),
        "dependencyRevisions": dependency_revisions,
        "allowedAxioms": ALLOWED_AXIOMS,
        "policy": "all discovered production declaration types/values, auxiliaries and anonymous examples",
        "hashes": {
            name: digest(project / name) for name in files if (project / name).is_file()
        },
    }


def audit(
    project: Path, report_path: Path, env: dict[str, str], *, verbose: bool = True
) -> dict[str, Any]:
    sources, excluded = discover(project)
    result: dict[str, Any] = {
        "schema": SCHEMA,
        **metadata(project, env),
        "sources": [],
        "excluded": excluded,
        "trustedTools": TRUSTED_TOOLS,
        "issues": [],
        "complete": False,
    }
    source_hashes = {module: digest(path) for module, path in sources.items()}
    for package, revision in result["dependencyRevisions"].items():
        if (
            revision.get("actualRevision") is not None
            and revision["actualRevision"] != revision["rev"]
        ):
            result["issues"].append(
                {
                    "kind": "dependency-revision-mismatch",
                    "package": package,
                    "expected": revision["rev"],
                    "actual": revision["actualRevision"],
                }
            )
    with tempfile.TemporaryDirectory(prefix="lean-proof-integrity-") as scratch:
        artifacts = Path(scratch)
        audit_env = env.copy()
        audit_env["LEAN_PATH"] = str(artifacts) + os.pathsep + env.get("LEAN_PATH", "")
        imports = {}
        excluded_modules = {
            path.removesuffix(".lean").replace("/", ".") for path in excluded
        }
        for module, path in sources.items():
            status, header = backend(
                "header", module, path, project=project, env=audit_env
            )
            if status:
                result["issues"].append(
                    {"source": str(path), "kind": "invalid-header", "report": header}
                )
                continue
            forbidden = sorted(set(header["imports"]) & excluded_modules)
            if forbidden:
                result["issues"].append(
                    {
                        "source": str(path),
                        "kind": "excluded-fixture-import",
                        "imports": forbidden,
                    }
                )
                continue
            imports[module] = header["imports"]
        if len(imports) == len(sources):
            for module in topological_order(sources, imports):
                path = sources[module]
                relative = path.relative_to(project).as_posix()
                artifact = artifacts.joinpath(*module.split(".")).with_suffix(".olean")
                artifact.parent.mkdir(parents=True, exist_ok=True)
                command = [
                    "lean",
                    "--root=" + str(project),
                    "-o",
                    str(artifact),
                    str(path),
                ]
                compiled = run(command, project=project, env=audit_env)
                entry: dict[str, Any] = {
                    "module": module,
                    "source": relative,
                    "sha256": source_hashes[module],
                    "compiled": compiled.returncode == 0,
                    "command": [
                        "lean",
                        "--root=<project>",
                        "-o",
                        "<audit-artifacts>/" + module.replace(".", "/") + ".olean",
                        relative,
                    ],
                }
                if compiled.returncode:
                    entry["issues"] = [
                        {
                            "kind": "compile-error",
                            "detail": compiled.stdout + compiled.stderr,
                        }
                    ]
                    result["sources"].append(entry)
                    result["issues"].append(
                        {"source": relative, "kind": "compile-error"}
                    )
                    continue
                if relative in TRUSTED_TOOLS:
                    entry.update(
                        {
                            "trustedTool": True,
                            "reason": TRUSTED_TOOLS[relative],
                            "issues": [],
                        }
                    )
                else:
                    _, checked = backend(
                        "source", module, path, project=project, env=audit_env
                    )
                    entry.update(checked)
                    entry["source"] = relative
                    if checked["issues"]:
                        result["issues"].append(
                            {"source": relative, "kind": "proof-integrity"}
                        )
                result["sources"].append(entry)
                if verbose:
                    print(
                        f"proof audit: {relative}: {'FAIL' if entry['issues'] else 'ok'}",
                        flush=True,
                    )
            result["complete"] = len(result["sources"]) == len(sources) and all(
                entry["compiled"] for entry in result["sources"]
            )
    for entry in result["sources"]:
        path = project / entry["source"]
        entry["sha256After"] = digest(path) if path.is_file() else None
        if entry["sha256After"] != entry["sha256"]:
            entry["issues"].append({"kind": "source-changed-during-audit"})
            result["issues"].append(
                {"source": entry["source"], "kind": "source-changed-during-audit"}
            )
            result["complete"] = False
    after_sources, after_excluded = discover(project)
    if set(after_sources) != set(sources) or after_excluded != excluded:
        result["issues"].append(
            {
                "kind": "source-set-changed-during-audit",
                "added": sorted(set(after_sources) - set(sources)),
                "removed": sorted(set(sources) - set(after_sources)),
            }
        )
        result["complete"] = False
    result["hashesAfter"] = {
        name: digest(project / name) if (project / name).is_file() else None
        for name in result["hashes"]
    }
    if result["hashesAfter"] != result["hashes"]:
        result["issues"].append({"kind": "audit-input-changed-during-audit"})
        result["complete"] = False
    if not result["complete"]:
        result["issues"].append({"kind": "incomplete-coverage"})
    result["coverage"] = {
        "discoveredFiles": len(sources),
        "processedFiles": len(result["sources"]),
        "auditedFiles": sum(
            not entry.get("trustedTool", False) and entry.get("compiled", False)
            for entry in result["sources"]
        ),
        "compiledTrustedFiles": sum(
            entry.get("trustedTool", False) for entry in result["sources"]
        ),
        "declarations": sum(
            entry.get("declarations", 0) for entry in result["sources"]
        ),
        "privateDeclarations": sum(
            entry.get("privateDeclarations", 0) for entry in result["sources"]
        ),
        "examples": sum(entry.get("examples", 0) for entry in result["sources"]),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--report", type=Path)
    parser.add_argument("--in-lake-env", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    project = args.project.resolve()
    if args.self_test:
        return subprocess.run(
            [
                sys.executable,
                "-m",
                "unittest",
                "discover",
                "-s",
                str(Path(__file__).resolve().parent / "tests"),
                "-v",
            ],
            check=False,
        ).returncode
    if not args.in_lake_env:
        command = [
            "lake",
            "env",
            sys.executable,
            str(Path(__file__).resolve()),
            "--project",
            str(project),
            "--in-lake-env",
        ]
        if args.report is not None:
            command.extend(["--report", str(args.report.resolve())])
        return subprocess.run(command, cwd=project, check=False).returncode
    report = (
        args.report.resolve()
        if args.report
        else project / ".lake/build/proof-integrity.json"
    )
    try:
        result = audit(project, report, os.environ.copy())
    except (AuditError, OSError, ValueError) as exc:
        print(f"proof audit failed: {exc}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "coverage": result["coverage"],
                "complete": result["complete"],
                "report": str(report),
                "ok": not result["issues"],
            },
            sort_keys=True,
        )
    )
    return 0 if not result["issues"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
