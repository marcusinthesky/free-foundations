"""Generated-beta premium tables must preserve units, cohorts and uncertainty."""

import runpy
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[3]
RENDER = runpy.run_path(str(ROOT / "src/latex/render_results.py"))
type Row = dict[str, Any]


@pytest.fixture
def premium_records() -> tuple[list[Row], list[Row], dict[str, Row]]:
    cohorts = {
        f"common_{arm}": {
            "firms": firms,
            "tickers": [f"F{index}" for index in range(firms)],
            "characteristics": [f"C{index}" for index in range(characteristics)],
        }
        for arm, firms, characteristics in (("four", 4, 4), ("three", 5, 3))
    }
    estimates: list[Row] = []
    bootstrap: list[Row] = []
    procedures = (
        ("ols", "nonspatial", "none", "ols_premium"),
        ("spatial_lag_iv", "fernandez_joint", "exp", "iv_premium"),
        ("spatial_error_ml", "fernandez_joint", "exp", "sem_premium"),
    )
    for table, cohort in cohorts.items():
        for estimator, network, kernel, parameter in procedures:
            estimates.append(
                {
                    "table": table,
                    "factors": "capm",
                    "network": network,
                    "kernel": kernel,
                    "estimator": estimator,
                    "self_links": "False",
                    "firms": str(cohort["firms"]),
                    "premium_market": "0.02",
                    "se_market": "0.004",
                }
            )
            bootstrap.append(
                {
                    "table": table,
                    "factors": "capm",
                    "network": "fernandez_joint",
                    "parameter": parameter,
                    "lower": "-0.01",
                    "upper": "0.04",
                    "replicates": "199",
                }
            )
    return estimates, bootstrap, cohorts


def test_premium_table_keeps_bootstrap_intervals_distinct_from_conditional_errors(
    premium_records: tuple[list[Row], list[Row], dict[str, Row]],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    estimates, bootstrap, cohorts = premium_records
    # OLS is archived under every network; only the joint-network summary belongs here.
    bootstrap.append(bootstrap[0] | {"network": "another_network", "lower": "-0.9"})
    monkeypatch.setitem(RENDER["write"].__globals__, "OUT", tmp_path)
    RENDER["render_replication_premiums"](estimates, bootstrap, cohorts)
    claims = RENDER["CLAIMS"]["replication_premium_uncertainty"]
    assert len(claims) == 6
    assert [row["firms"] for row in claims] == [4, 4, 4, 5, 5, 5]
    assert claims[0]["premium_percent"] == pytest.approx(2)
    assert claims[0]["conditional_se_percentage_points"] == pytest.approx(0.4)
    assert claims[0]["generated_beta_lower_percent"] == pytest.approx(-1)
    assert claims[0]["generated_beta_upper_percent"] == pytest.approx(4)
    assert claims[0]["valid_draws"] == 199
    table = (tmp_path / "replication-premiums.tex").read_text()
    assert "[-1.00, 4.00]" in table
    assert "0.40" in table
    assert "Four" in table
    assert "Three" in table


@pytest.mark.parametrize(
    ("field", "value"),
    [("lower", "nan"), ("upper", "inf"), ("lower", "0.05"), ("replicates", "198")],
)
def test_invalid_or_incomplete_premium_intervals_cannot_be_published(
    premium_records: tuple[list[Row], list[Row], dict[str, Row]],
    field: str,
    value: str,
) -> None:
    estimates, bootstrap, cohorts = premium_records
    bootstrap[0][field] = value
    with pytest.raises(ValueError, match="Invalid generated-beta premium summary"):
        RENDER["render_replication_premiums"](estimates, bootstrap, cohorts)


def test_premium_table_rejects_cohort_drift_and_negative_conditional_error(
    premium_records: tuple[list[Row], list[Row], dict[str, Row]],
) -> None:
    estimates, bootstrap, cohorts = premium_records
    estimates[0]["firms"] = "3"
    with pytest.raises(ValueError, match="replication cohort common_four"):
        RENDER["render_replication_premiums"](estimates, bootstrap, cohorts)
    estimates[0]["firms"] = "4"
    estimates[0]["se_market"] = "-0.004"
    with pytest.raises(ValueError, match="Invalid generated-beta premium summary"):
        RENDER["render_replication_premiums"](estimates, bootstrap, cohorts)
