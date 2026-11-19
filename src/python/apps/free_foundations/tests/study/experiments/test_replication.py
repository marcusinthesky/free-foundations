"""The original-sample comparison rejects missing and nonfinite refits."""

import pandas as pd
import pytest

from free_foundations.study.experiments.replication import _parity


@pytest.mark.unit
@pytest.mark.parametrize("refit", [{}, {"lag_ml:premium:without": float("nan")}])
def test_missing_or_nonfinite_refit_fails_parity(refit: dict[str, float]) -> None:
    # Arrange
    estimates = pd.DataFrame(
        [
            {
                "network": "joint",
                "estimator": "lag_ml",
                "status": "available",
                "with_intercept": False,
                "beta": 1.0,
                "spatial": 0.2,
            }
        ]
    )

    # Act / Assert
    with pytest.raises(ValueError, match="joint lag_ml without premium"):
        _parity(estimates, {"joint": refit}, {"joint"})
