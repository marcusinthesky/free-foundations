"""Publication selectors must reject incomplete or inconsistent study outputs."""

import runpy
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
RENDER = runpy.run_path(str(ROOT / "src/latex/render_results.py"))


def test_a_model_subset_cannot_be_rendered_as_the_study() -> None:
    rows = [
        {"approach": "histories__tabpfn_full__late", "kernel": "matched", "innovation": "diagonal"}
    ]
    with pytest.raises(ValueError, match="Incomplete publication procedures"):
        RENDER["validate_inventory"](rows, [], [])


def test_duplicate_procedures_are_rejected_before_rendering() -> None:
    row = {"approach": "histories__direct", "kernel": "matched", "innovation": "diagonal"}
    with pytest.raises(ValueError, match="Duplicate comparison procedure"):
        RENDER["validate_inventory"]([row, row], [], [])


def test_missing_or_ambiguous_source_rows_are_rejected() -> None:
    with pytest.raises(ValueError, match="found 0"):
        RENDER["select"]([], representation="direct")
    with pytest.raises(ValueError, match="found 2"):
        RENDER["select"]([{"year": "2020"}] * 2, year=2020)


def test_nonfinite_or_unreconciled_scores_are_rejected() -> None:
    for actual in (float("nan"), float("inf"), 2.0):
        with pytest.raises(ValueError, match="saved score"):
            RENDER["close"](actual, 1.0, "saved score")
