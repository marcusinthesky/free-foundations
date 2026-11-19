"""The MM stage-one script ships with the package and behaves as documented."""

import shutil
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.methods.fernandez.evaluation import (
    SCRIPT,
    exposure_table,
    robust_betas,
    runtime_record,
)

needs_r = pytest.mark.skipif(shutil.which("Rscript") is None, reason="devenv supplies Rscript")


def quarters(seed: int = 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2016-03-31", periods=40, freq="QE")
    market = rng.normal(0.02, 0.08, 40)
    rows: list[dict[str, object]] = []
    for ticker, beta in (("A", 0.5), ("B", 1.2), ("C", 0.9)):
        excess = 0.01 + beta * market + rng.normal(0, 0.01, 40)
        excess[5] += 1.5  # One gross outlier per firm.
        rows += [
            {"date": d, "ticker": ticker, "excess": e, "market": m, "smb": s}
            for d, e, m, s in zip(dates, excess, market, rng.normal(0, 0.03, 40), strict=True)
        ]
    return pd.DataFrame(rows)


def test_betas_script_is_present() -> None:
    assert SCRIPT.is_file()
    assert "robustbase::lmrob" in SCRIPT.read_text()
    assert "robust::lmRob" in SCRIPT.read_text()


@needs_r
def test_mm_recovers_beta_despite_outliers_and_ignores_firm_order(tmp_path: Path) -> None:
    sample = quarters()
    estimates = exposure_table(robust_betas(sample, tmp_path))
    np.testing.assert_allclose(estimates["market"].loc[["A", "B", "C"]], [0.5, 1.2, 0.9], atol=0.05)
    shuffled = sample.sample(frac=1, random_state=3)
    reordered = exposure_table(robust_betas(shuffled.loc[shuffled["ticker"] != "A"], tmp_path))
    np.testing.assert_allclose(reordered.loc[["B", "C"]], estimates.loc[["B", "C"]])
    runtime = runtime_record(tmp_path)
    assert all(isinstance(value, str) for value in runtime.values())
    assert runtime["backend"] == "robustbase"


@needs_r
def test_identity_bootstrap_replicate_equals_original_and_terms_extend(tmp_path: Path) -> None:
    sample = quarters()
    original = exposure_table(robust_betas(sample, tmp_path))
    labels = sorted(sample["date"].dt.strftime("%Y-%m-%d").unique())
    indices = pd.DataFrame({"replicate": 1, "position": range(40), "quarter": labels})
    replicated = robust_betas(sample, tmp_path, indices=indices, tag="identity")
    np.testing.assert_allclose(exposure_table(replicated, replicate=1), original)
    two = robust_betas(sample, tmp_path, terms=("market", "smb"), tag="two")
    assert set(two["term"]) == {"intercept", "market", "smb"}


@needs_r
def test_software_lineage_backend_is_seeded_and_records_its_actual_controls(tmp_path: Path) -> None:
    executable = shutil.which("Rscript")
    assert executable is not None
    available = subprocess.run(  # noqa: S603 -- installed Rscript and fixed diagnostic expression.
        [executable, "-e", 'quit(status=!requireNamespace("robust", quietly=TRUE))'],
        check=False,
        capture_output=True,
    )
    if available.returncode:
        pytest.skip("Updated devenv supplies robust")
    sample = quarters()
    rows = robust_betas(sample, tmp_path, backend="robust")
    assert rows["converged"].all()
    assert rows["backend"].eq("robust").all()
    assert {"warning_messages", "iteration_refinement", "iteration_final"} <= set(rows)
    expected = exposure_table(rows)
    np.testing.assert_allclose(expected["market"].loc[["A", "B", "C"]], [0.5, 1.2, 0.9], atol=0.05)
    reordered = exposure_table(
        robust_betas(sample.loc[sample["ticker"].ne("A")], tmp_path, backend="robust")
    )
    np.testing.assert_allclose(reordered.loc[["B", "C"]], expected.loc[["B", "C"]])
    runtime = runtime_record(tmp_path, backend="robust")
    assert runtime["backend"] == "robust"
    assert runtime["control.estim"].lower() == "final"
    assert runtime["control.final.alg"].lower() == "mm"
    assert float(runtime["control.efficiency"]) == 0.9
    assert runtime["control.weight"].lower() == "optimal;optimal"
    assert runtime["control.seed"] == "42"
    assert (tmp_path / "cache/mm-robust-capm-output.csv").is_file()
