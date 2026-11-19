"""Profile the Gaussian likelihood of orthonormal within-period contrasts."""

import numpy as np

from free_foundations.methods.spatial_ml import _panel_state


def contrast_loglik(periods, value, process):
    """Evaluate contrasts for row-stochastic graphs without isolates."""
    _, residuals, sizes, logdets = _panel_state(periods, value, process)
    dimensions = int(sizes.sum()) - len(periods)
    variance = float(residuals @ residuals / dimensions)
    determinant = logdets.sum() - len(periods) * np.log1p(-value)
    return float(determinant - dimensions / 2 * (np.log(2 * np.pi * variance) + 1))
