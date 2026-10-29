"""Require a frozen, complete type contract for every manuscript/blueprint declaration tag."""

import json
import re
import subprocess
from pathlib import Path


def without_comments(text: str) -> str:
    return re.sub(r"(?m)(?<!\\)%.*$", "", text)


def check() -> None:
    project = Path(__file__).resolve().parents[1]
    repository = project.parents[1]
    tagged: set[str] = set()
    for source in (
        repository / "src/latex/main.tex",
        project / "blueprint/src/content.tex",
    ):
        for tag in re.findall(
            r"\\lean\{([^}]*)\}", without_comments(source.read_text())
        ):
            tagged.update(name.strip() for name in tag.split(",") if name.strip())
    # Read elaborated contracts, so a declaration hidden in a comment cannot
    # satisfy coverage. Rebuild first to reject stale project artifacts.
    subprocess.run(["lake", "build", "FreeFoundationsApi"], cwd=project, check=True)
    query = """import FreeFoundationsApi
open Lean Elab Command
run_cmd do
  let names := FreeFoundations.ApiCheck.signatureContracts.getState (← getEnv)
  liftIO <| IO.println ("API_CONTRACTS " ++ Json.compress (toJson (names.map Name.toString)))
"""
    checked = subprocess.run(
        ["lake", "env", "lean", "--stdin"],
        cwd=project,
        input=query,
        text=True,
        capture_output=True,
        check=True,
    )
    reports = [
        line.removeprefix("API_CONTRACTS ")
        for line in checked.stdout.splitlines()
        if line.startswith("API_CONTRACTS ")
    ]
    if len(reports) != 1:
        raise SystemExit("API coverage failed: expected one compiled-contract report")
    contracts = json.loads(reports[0])
    if not tagged:
        raise SystemExit("API coverage failed: no manuscript declarations found")
    duplicates = {name for name in contracts if contracts.count(name) != 1}
    missing = tagged - set(contracts)
    if missing or duplicates:
        raise SystemExit(
            "API coverage failed: "
            + "; ".join(
                [
                    *(f"missing {name}" for name in sorted(missing)),
                    *(f"duplicate {name}" for name in sorted(duplicates)),
                ]
            )
        )
    print(
        f"API coverage: {len(tagged)} tagged declarations, {len(contracts)} frozen contracts"
    )


if __name__ == "__main__":
    check()
