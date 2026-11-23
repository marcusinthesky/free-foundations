# /// script
# requires-python = ">=3.13,<3.14"
# dependencies = ["yalafi==1.5.0"]
# ///
"""Map advisory Vale matches on manuscript prose to the original LaTeX lines."""

import bisect
import json
import re
import subprocess
import sys
from pathlib import Path

from yalafi import defs, parameters, parser, utils
from yalafi.packages import amsmath, amsthm

CONFIG = Path(__file__).resolve().parents[1] / "assets/vale/vale.ini"


def extract(source: str, path: Path) -> tuple[str, list[int]]:
    settings = parameters.Parameters("en")
    packages = [
        ("amsmath", (amsmath.require_packages, amsmath.init_module)),
        ("amsthm", (amsthm.require_packages, amsthm.init_module)),
    ]
    reader = parser.Parser(settings, packages)
    settings.math_text_macros = []
    settings.math_displayed_simple = True
    for name, args in {
        "cite": "OOA",
        "citep": "OOA",
        "citet": "OOA",
        "ffnum": "OA",
        "ffnume": "OA",
        "ffvalue": "A",
        "lean": "A",
        "includegraphics": "OA",
    }.items():
        macro = defs.Macro(settings, "\\" + name, args=args)
        reader.the_macros[macro.name] = macro
    reader.the_environments["tabular"] = defs.Environ(
        settings, "tabular", args="A", remove=True
    )
    plain, positions = utils.get_txt_pos(reader.parse(source, source=str(path)))
    if settings.mark_latex_error in plain:
        raise ValueError(f"{path}: LaTeX extraction failed (see YaLafi diagnostic)")
    # TeX hard wraps and indentation are one space; keep real paragraph breaks.
    chunks = []
    offsets = []
    for run in re.finditer(r"\s+|\S+", plain):
        chunk = run.group()
        if chunk.isspace():
            chunk = "\n\n" if chunk.count("\n") > 1 else " "
        chunks.append(chunk)
        offsets.extend(positions[run.start() : run.start() + len(chunk)])
    return "".join(chunks), offsets


def line_starts(text: str) -> list[int]:
    return [0, *(match.end() for match in re.finditer("\n", text))]


def review(path: Path) -> int:
    if path.suffix != ".tex":
        raise ValueError(f"{path}: expected an authored .tex section")
    source = path.read_text(encoding="utf-8")
    plain, positions = extract(source, path)
    result = subprocess.run(
        [
            "vale",
            "--no-global",
            "--no-exit",
            f"--config={CONFIG}",
            "--output=JSON",
            "--ext=.txt",
        ],
        input=plain,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        raise ValueError(f"{path}: Vale failed: {result.stderr or result.stdout}")
    report = json.loads(result.stdout)
    if "Code" in report:
        raise ValueError(f"{path}: Vale configuration error: {report}")
    starts = line_starts(plain)
    source_starts = line_starts(source)
    alerts = report.get("stdin.txt", [])
    for alert in alerts:
        index = starts[alert["Line"] - 1] + alert["Span"][0] - 1
        matched = alert["Match"]
        if not plain.startswith(matched, index):
            raise ValueError(f"{path}: cannot map Vale excerpt {matched!r} to source")
        offset = positions[index]
        line = bisect.bisect_right(source_starts, offset)
        column = offset - source_starts[line - 1] + 1
        print(f"{path}:{line}:{column}: {alert['Check']}: {matched}")
    return len(alerts)


if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            raise ValueError("expected at least one manuscript section")
        count = sum(review(Path(name)) for name in sys.argv[1:])
        print(f"Reviewed {len(sys.argv) - 1} section(s), {count} advisory match(es).")
    except (OSError, ValueError) as error:
        sys.exit(str(error))
