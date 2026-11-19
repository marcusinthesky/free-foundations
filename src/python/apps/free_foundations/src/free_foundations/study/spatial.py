"""The statadic boundary: spatial fits, their covariances and diagnostics as rows.

Every fit is a cross-section or panel on an explicit, row-normalized graph. Rows
carry estimates, standard errors, 95% Wald intervals, likelihood criteria and
validity, so unavailable fits remain explicit results rather than missing rows.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

import jax
import numpy as np

jax.config.update("jax_enable_x64", True)  # noqa: FBT003 -- statadic numerics need float64.

from statadic.estimation.spatial import ML, ObservedPanelML, SpatialIV  # noqa: E402
from statadic.geometry.graph import prepare_spatial_weights  # noqa: E402
from statadic.hypothesis.uncertainty import ModelBased  # noqa: E402
from statadic.observation.data import Observations, PanelLayout  # noqa: E402
from statadic.observation.design import Intercept, Linear  # noqa: E402
from statadic.observation.graph import (  # noqa: E402
    PanelData,
    SpatialData,
    SpatialError,
    SpatialLag,
)
from statadic.regression import Regression  # noqa: E402
from statadic.structure.spatial.cross_section import (  # noqa: E402
    SpatialInformation,
    SpatialMomentCovariance,
)
from statadic.structure.spatial.diagnostics import ResidualMoran, SpatialLM  # noqa: E402

if TYPE_CHECKING:
    from collections.abc import Sequence

    import pandas as pd

    from free_foundations.contracts import FloatArray

type Estimator = Literal["ols", "lag_ml", "error_ml", "lag_iv"]
Z = 1.959963984540054


def _graph(weights: FloatArray, unit_ids: Sequence[int] | None = None) -> Any:  # noqa: ANN401
    isolated = bool(np.any(np.asarray(weights).sum(axis=1) == 0))
    return prepare_spatial_weights(
        np.asarray(weights, dtype=float),
        unit_ids=None if unit_ids is None else np.asarray(unit_ids),
        allow_isolates=isolated,
    )


def _design(columns: dict[str, FloatArray], *, intercept: bool) -> Any:  # noqa: ANN401
    terms = [Linear(name) for name in columns]
    design = terms[0]
    for term in terms[1:]:
        design = design + term
    return Intercept() + design if intercept else design


def _covariance(fit: Any, spec: Any) -> FloatArray:  # noqa: ANN401 -- statadic results.
    """The parameter covariance of a statadic fit under one covariance request."""
    matrix = fit.infer(covariance=spec).uncertainty.covariance
    return np.asarray(getattr(matrix, "values"), dtype=float)  # noqa: B009 -- not pandas.


def _metrics(fit: Any) -> dict[str, float]:  # noqa: ANN401
    return {
        metric.name: float(metric.value)
        for metric in fit.fit_statistics().metrics
        if metric.value is not None
    }


def _row(names: Sequence[str], estimates: FloatArray, covariance: FloatArray) -> dict[str, float]:
    errors = np.sqrt(np.maximum(np.diag(np.asarray(covariance, dtype=float)), 0))
    row: dict[str, float] = {}
    for name, value, error in zip(names, np.asarray(estimates, float), errors, strict=True):
        label = "spatial" if name.startswith(("rho", "lambda")) else name.lower()
        row |= {
            label: float(value),
            f"{label}_se": float(error),
            f"{label}_low": float(value - Z * error),
            f"{label}_high": float(value + Z * error),
        }
    return row


def cross_section(
    outcome: FloatArray,
    regressors: dict[str, FloatArray],
    weights: FloatArray | None,
    estimator: Estimator,
    *,
    intercept: bool,
) -> dict[str, Any]:
    """One fitted cross-section as a flat row; failures become an unavailable row."""
    rows = Observations({**{k: np.asarray(v, float) for k, v in regressors.items()}, "y": outcome})
    design = _design(regressors, intercept=intercept)
    base: dict[str, Any] = {
        "estimator": estimator,
        "with_intercept": intercept,
        "firms": len(outcome),
        "status": "unavailable",
        "reason": "",
    }
    graph = None if weights is None else _graph(weights)
    if estimator != "ols" and graph is None:
        return base | {"reason": "Spatial estimators need a graph."}
    try:
        if estimator == "ols" or graph is None:
            fit = Regression.ols("y", design).estimate(rows)
            covariance = _covariance(fit, ModelBased())
        else:
            data = SpatialData(rows, {"w": graph})
            dependence = SpatialError("w") if estimator == "error_ml" else SpatialLag("w")
            brick = (
                SpatialIV(instrument_columns=(int(intercept),)) if estimator == "lag_iv" else ML()
            )
            fit = Regression("y", design, dependence=dependence, estimator=brick).estimate(data)
            spec = (
                SpatialMomentCovariance("homoskedastic")
                if estimator == "lag_iv"
                else SpatialInformation()
            )
            covariance = _covariance(fit, spec)
    except (
        ValueError,
        TypeError,
        RuntimeError,
        FloatingPointError,
        np.linalg.LinAlgError,
    ) as error:
        return base | {"reason": str(error)}
    names = tuple(fit.parameter_names or ())
    estimates = np.asarray(fit.parameters, dtype=float)
    if not bool(fit.valid) or not np.isfinite(estimates).all():
        return base | {"reason": "statadic reports an invalid or boundary fit"}
    return base | {"status": "available"} | _row(names, estimates, covariance) | _metrics(fit)


def diagnostics(
    outcome: FloatArray, regressors: dict[str, FloatArray], weights: FloatArray
) -> dict[str, Any]:
    """Residual Moran's I and (robust) LM tests of OLS with an intercept on ``W``."""
    rows = Observations({**{k: np.asarray(v, float) for k, v in regressors.items()}, "y": outcome})
    fit = Regression.ols("y", _design(regressors, intercept=True)).estimate(rows)
    graph = _graph(weights)
    tests = fit.diagnose(
        ResidualMoran(graph),
        *(SpatialLM(graph, kind=kind) for kind in ("lag", "error", "robust-lag", "robust-error")),
    )
    result: dict[str, Any] = {}
    for test in tests:
        statistic, pvalue = getattr(test, "statistic", None), getattr(test, "pvalue", None)
        result[test.name] = float(statistic) if statistic is not None else np.nan
        result[f"{test.name}_p"] = float(pvalue) if pvalue is not None else np.nan
    return result


def comovement_panel(
    nodes: pd.DataFrame,
    outcomes: pd.DataFrame,
    graphs: Sequence[tuple[int, FloatArray, Sequence[int]]],
    process: Literal["lag", "error"],
) -> tuple[dict[str, Any], Any]:
    """Unbalanced spatial panel of ``y`` with period effects and one period graph each.

    ``nodes`` lists every active unit-period (columns ``unit``, ``period`` and the
    regressor ``z``); ``outcomes`` the observed subset with ``y``. Missing outcomes
    are marginalized on the full period graph, never imputed.
    """
    layout = PanelLayout("unit", "period")
    data = PanelData(
        Observations({str(name): nodes[name].to_numpy() for name in nodes}),
        layout,
        graphs={"w": tuple((period, _graph(w, ids)) for period, w, ids in graphs)},
        outcomes=Observations(
            {str(name): outcomes[name].to_numpy() for name in outcomes},
            row_ids=outcomes.index.tolist(),
        ),
    )
    dependence = SpatialError("w") if process == "error" else SpatialLag("w")
    fit = Regression(
        "y",
        Linear("z"),
        structure=layout,
        dependence=dependence,
        effects="time",
        estimator=ObservedPanelML(),
    ).estimate(data)
    base: dict[str, Any] = {"process": process, "status": "unavailable", "reason": ""}
    estimates = np.asarray(fit.parameters, dtype=float)
    if not bool(fit.valid) or not np.isfinite(estimates).all():
        return base | {"reason": "statadic reports an invalid or boundary fit"}, fit
    covariance = _covariance(fit, SpatialInformation())
    names = tuple(fit.parameter_names or ())
    return base | {"status": "available"} | _row(names, estimates, covariance) | _metrics(fit), fit
