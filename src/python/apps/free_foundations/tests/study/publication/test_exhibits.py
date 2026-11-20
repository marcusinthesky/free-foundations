"""Broad-input factor exhibits keep controls distinct and reject stale results."""

import pandas as pd
import pytest

from free_foundations.study.publication.exhibits import broad_factor_table


@pytest.fixture
def contrasts() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "cell": "ff5_mom|standard_xbrl:tabpfn_full",
                "reference": "ff5_mom|standard_xbrl:direct",
                "status": "available",
                "total_difference": -70.0,
                "gain_per_observation": -0.007,
                "low_per_observation": -0.012,
                "high_per_observation": -0.002,
            },
            {
                "cell": "standard_xbrl:tabpfn_full",
                "reference": "standard_xbrl:direct",
                "status": "available",
                "total_difference": 200.0,
                "gain_per_observation": 0.02,
                "low_per_observation": 0.01,
                "high_per_observation": 0.03,
            },
            {
                "cell": "ff5|standard_xbrl:tabpfn_full",
                "reference": "ff5|standard_xbrl:direct",
                "status": "available",
                "total_difference": 10.0,
                "gain_per_observation": 0.001,
                "low_per_observation": -0.004,
                "high_per_observation": 0.006,
            },
        ]
    ).set_index(["cell", "reference"], verify_integrity=True)


@pytest.mark.unit
def test_broad_factor_table_uses_each_control_and_per_observation_units(
    contrasts: pd.DataFrame,
) -> None:
    # Arrange: distinct saved contrasts are deliberately out of display order.
    # Act
    table = broad_factor_table(contrasts)

    # Assert
    assert table.to_dict("records") == [
        {"Control": "Market", "Gain": "0.0200", "95% interval": "[0.0100, 0.0300]"},
        {"Control": "FF5", "Gain": "0.0010", "95% interval": "[-0.0040, 0.0060]"},
        {"Control": "FF5 + Momentum", "Gain": "-0.0070", "95% interval": "[-0.0120, -0.0020]"},
    ]


@pytest.mark.unit
def test_broad_factor_table_requires_regenerated_comparisons(contrasts: pd.DataFrame) -> None:
    # Arrange
    older_results = contrasts.loc[["standard_xbrl:tabpfn_full"], :]

    # Act and assert
    with pytest.raises(ValueError, match=r"ff5.*rerun research_matched_encoders"):
        broad_factor_table(older_results)


@pytest.mark.unit
def test_broad_factor_table_keeps_unavailable_fits_visible(contrasts: pd.DataFrame) -> None:
    # Arrange
    key = ("ff5_mom|standard_xbrl:tabpfn_full", "ff5_mom|standard_xbrl:direct")
    contrasts.loc[key, "status"] = "unavailable"
    contrasts.loc[key, "gain_per_observation"] = float("nan")

    # Act
    table = broad_factor_table(contrasts)

    # Assert
    assert table.iloc[-1].to_dict() == {
        "Control": "FF5 + Momentum",
        "Gain": "---",
        "95% interval": "---",
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("column", "value"),
    [
        ("gain_per_observation", float("nan")),
        ("low_per_observation", float("-inf")),
        ("high_per_observation", -0.02),
    ],
)
def test_broad_factor_table_rejects_invalid_available_results(
    contrasts: pd.DataFrame, column: str, value: float
) -> None:
    # Arrange
    key = ("ff5|standard_xbrl:tabpfn_full", "ff5|standard_xbrl:direct")
    contrasts.loc[key, column] = value

    # Act and assert
    with pytest.raises(ValueError, match="Invalid broad-input ff5"):
        broad_factor_table(contrasts)
