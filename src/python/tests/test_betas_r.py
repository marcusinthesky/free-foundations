"""The MM stage-one script ships with the package and behaves as documented."""

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.fernandez.evaluation import SCRIPT, exposure_table, robust_betas

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


@needs_r
def test_mm_recovers_beta_despite_outliers_and_ignores_firm_order(tmp_path: Path) -> None:
    sample = quarters()
    estimates = exposure_table(robust_betas(sample, tmp_path))
    np.testing.assert_allclose(estimates["market"].loc[["A", "B", "C"]], [0.5, 1.2, 0.9], atol=0.05)
    shuffled = sample.sample(frac=1, random_state=3)
    reordered = exposure_table(robust_betas(shuffled.loc[shuffled["ticker"] != "A"], tmp_path))
    np.testing.assert_allclose(reordered.loc[["B", "C"]], estimates.loc[["B", "C"]])


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
