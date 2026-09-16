from __future__ import annotations

import numpy as np
from scipy.stats import wilcoxon


def bootstrap_mae_ci(
    actual: np.ndarray,
    predicted: np.ndarray,
    *,
    iterations: int = 2000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    y_true = np.asarray(actual, dtype=float)
    y_pred = np.asarray(predicted, dtype=float)
    rng = np.random.default_rng(seed)
    estimates = []
    for _ in range(iterations):
        indices = rng.integers(0, len(y_true), len(y_true))
        estimates.append(float(np.mean(np.abs(y_true[indices] - y_pred[indices]))))
    alpha = (1.0 - confidence) / 2.0
    return tuple(map(float, np.quantile(estimates, [alpha, 1.0 - alpha])))


def paired_absolute_error_test(
    actual: np.ndarray, prediction_a: np.ndarray, prediction_b: np.ndarray
) -> dict[str, float]:
    errors_a = np.abs(np.asarray(prediction_a) - np.asarray(actual))
    errors_b = np.abs(np.asarray(prediction_b) - np.asarray(actual))
    if np.allclose(errors_a, errors_b):
        return {"statistic": 0.0, "pvalue": 1.0}
    result = wilcoxon(errors_a, errors_b, zero_method="wilcox")
    return {"statistic": float(result.statistic), "pvalue": float(result.pvalue)}
