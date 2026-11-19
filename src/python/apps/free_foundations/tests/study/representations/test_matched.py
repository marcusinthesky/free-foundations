"""Independent T08 state loading and qualification."""

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from free_foundations.artifacts.metadata import write_json
from free_foundations.study.representations.arrays import _save_states
from free_foundations.study.representations.matched import load_cell
from free_foundations.study.spec import file_hash


@pytest.mark.integration
def test_cell_reader_reorders_rows_and_requires_verified_payload(tmp_path: Path) -> None:
    # Arrange
    quarter = pd.Timestamp("2016-03-31")
    destination = tmp_path / str(quarter.date()) / "states.npz"
    destination.parent.mkdir()
    _save_states(destination, {"direct": np.array([[1.0, 3.0], [5.0, 8.0]])})
    write_json(
        tmp_path / "manifest.json",
        {
            "model": "direct",
            "states": [
                {
                    "quarter": str(quarter.date()),
                    "status": "available",
                    "issuer_ids": ["A", "B"],
                    "sha256": file_hash(destination),
                },
                {"quarter": "2017-03-31", "status": "unavailable", "reason": "no dated context"},
            ],
        },
    )

    # Act
    ordered = load_cell(tmp_path, quarter, ("B", "A"))
    unavailable = load_cell(tmp_path, pd.Timestamp("2017-03-31"), ("A",))

    # Assert
    np.testing.assert_array_equal(ordered, [[5, 8], [1, 3]])
    assert unavailable is None
    with pytest.raises(ValueError, match="issuer identity"):
        load_cell(tmp_path, quarter, ("C",))
    with pytest.raises(ValueError, match="Expected one"):
        load_cell(tmp_path, pd.Timestamp("2018-03-31"), ("A",))
    _save_states(destination, {"direct": np.ones((2, 2))})
    with pytest.raises(ValueError, match="checksum"):
        load_cell(tmp_path, quarter, ("B",))
