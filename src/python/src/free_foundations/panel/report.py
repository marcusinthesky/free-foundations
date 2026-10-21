"""Render the publication from recorded numerical artifacts without model inference."""

import runpy
from pathlib import Path


def main() -> None:
    """Run the paper's standard pandas, Jinja2 and Matplotlib publication renderer."""
    script = Path(__file__).resolve().parents[4] / "latex/render_results.py"
    runpy.run_path(str(script), run_name="__main__")
