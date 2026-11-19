"""Check profiled period-effect likelihood against a direct Gaussian calculation."""

import numpy as np
from panel_contrast import contrast_loglik

from free_foundations.methods.spatial_ml import Period, _panel_loglik

w = np.array([[0.0, 0.5, 0.5], [0.5, 0.0, 0.5], [0.5, 0.5, 0.0]])
y = np.array([0.4, -0.2, 0.7])
x = np.array([0.1, 0.8, -0.3])
period = Period.of(y, x, w)
for process in ("error", "lag"):
    for rho in (-0.7, 0.0, 0.7):
        a = np.eye(3) - rho * w
        z = a @ x if process == "error" else x
        design = np.column_stack([np.ones(3), z])
        target = a @ y
        resid = target - design @ np.linalg.lstsq(design, target, rcond=None)[0]
        variance = resid @ resid / len(y)
        direct = np.linalg.slogdet(a)[1] - len(y) / 2 * (np.log(2 * np.pi * variance) + 1)
        actual = _panel_loglik([period], rho, process)
        np.testing.assert_allclose(actual, direct, atol=1e-10)
        contrast_det = np.linalg.slogdet(a)[1] - np.log(1 - rho)
        print(
            process,
            rho,
            "profile",
            round(actual, 8),
            "contrast_minus_profile",
            round(contrast_det - np.linalg.slogdet(a)[1], 8),
        )

# Use unequal sizes and non-symmetric row-stochastic graphs. Construct the
# contrast likelihood directly in an orthonormal basis of each 1-perp space.
adjacencies = [
    np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0]]),
    np.array(
        [[0.0, 1.0, 1.0, 1.0], [1.0, 0.0, 1.0, 0.0], [1.0, 1.0, 0.0, 0.0], [1.0, 0.0, 0.0, 0.0]]
    ),
]
weights = [a / a.sum(axis=1, keepdims=True) for a in adjacencies]
ys = [np.array([0.4, -0.2, 0.7]), np.array([-0.1, 0.3, 0.8, 0.2])]
xs = [np.array([0.1, 0.8, -0.3]), np.array([0.7, -0.5, 0.2, 0.6])]
periods = [Period.of(y, x, w) for y, x, w in zip(ys, xs, weights, strict=True)]
for process in ("error", "lag"):
    for rho in (-0.7, 0.0, 0.7):
        targets, regressors, determinants = [], [], []
        for y, x, w in zip(ys, xs, weights, strict=True):
            n = len(y)
            basis = np.linalg.qr(np.column_stack([np.ones(n), np.eye(n)[:, 1:]]))[0][:, 1:]
            a = np.eye(n) - rho * w
            targets.append(basis.T @ a @ y)
            regressors.append(basis.T @ (a @ x if process == "error" else x))
            determinants.append(np.linalg.slogdet(basis.T @ a @ basis)[1])
        target = np.concatenate(targets)
        regressor = np.concatenate(regressors)
        residual = target - regressor * (regressor @ target / (regressor @ regressor))
        dimension = len(target)
        variance = residual @ residual / dimension
        direct = sum(determinants) - dimension / 2 * (np.log(2 * np.pi * variance) + 1)
        np.testing.assert_allclose(contrast_loglik(periods, rho, process), direct, atol=1e-10)
        print("contrast", process, rho, round(direct, 8))
