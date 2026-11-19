"""Verify that matched quarterly designs share the same ordered observations."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
import pytest

from free_foundations.study.experiments import matched_factors
from free_foundations.study.experiments.inputs import StudyInputs
from free_foundations.study.spec import StudySpec

if TYPE_CHECKING:
    from pathlib import Path


@pytest.mark.integration
def test_saved_sample_requires_every_factor_loading_and_verifies_bytes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Arrange
    params = tmp_path / "params.yaml"
    params.write_text('study:\n  version: crsp-sec-quarterly-v2\n  archive_end: "2011-03-31"\n')
    panel = tmp_path / "panel"
    panel.mkdir()
    (panel / "manifest.json").write_text("{}")
    spec = StudySpec.read(params)
    quarter = spec.panel_calendar[0]
    names = [f"issuer{i:02d}" for i in range(13)]
    observed = pd.DataFrame(
        {
            "issuer_id": names[::-1],
            "quarter": quarter,
            "observed": True,
            "total_return": 0.2,
        }
    )
    factors = pd.DataFrame(
        {
            "quarter": [quarter],
            "RF": [0.05],
            **{column: [0.1] for column in matched_factors.FACTORS.values()},
        }
    )
    inputs = StudyInputs(spec, {"panel": observed, "factors": factors}, None)

    def load_stub(_panel: Path, _representations: Path | None, _params: Path) -> StudyInputs:
        return inputs

    monkeypatch.setattr(matched_factors, "load", load_stub)

    def loading_stub(
        _frame: pd.DataFrame, _work: Path, name: str, terms: tuple[str, ...], _minimum: int
    ) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "ticker": issuer,
                    "term": term,
                    "estimate": 2.0,
                    "converged": not (issuer == "issuer01" and name == "ff5_mom"),
                }
                for issuer in names
                for term in terms
            ]
        )

    monkeypatch.setattr(matched_factors, "_exposure_fit", loading_stub)
    output = tmp_path / "sample"

    # Act
    matched_factors.prepare_sample(panel, output, params)
    sample = matched_factors.load_sample(output, params, panel)

    # Assert
    only_quarter = sample.quarters[0]
    assert only_quarter.issuers == ("issuer00", *names[2:])
    assert all(y == pytest.approx(0.15) for y in only_quarter.outcome)
    assert only_quarter.design["ff5_mom"].shape == (12, 6)
    assert only_quarter.design["market"][0, 0] == pytest.approx(0.2)
    with params.open("a") as handle:
        handle.write("  likelihood_draws: 25\n")
    assert matched_factors.load_sample(output, params, panel).spec.likelihood_draws == 25
    (output / "ledger.parquet").write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="checksum mismatch: ledger"):
        matched_factors.load_sample(output, params, panel)
