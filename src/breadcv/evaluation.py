from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regression_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(actual, dtype=float)
    y_pred = np.asarray(predicted, dtype=float)
    if y_true.shape != y_pred.shape or y_true.size == 0:
        raise ValueError("Actual and predicted arrays must be non-empty and have equal shape")
    metrics = {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred) ** 0.5),
        "r2": float(r2_score(y_true, y_pred)),
    }
    nonzero = y_true != 0
    metrics["mape"] = (
        float(np.mean(np.abs((y_true[nonzero] - y_pred[nonzero]) / y_true[nonzero])) * 100)
        if nonzero.all()
        else float("nan")
    )
    return metrics


def bland_altman(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float | np.ndarray]:
    y_true = np.asarray(actual, dtype=float)
    y_pred = np.asarray(predicted, dtype=float)
    differences = y_pred - y_true
    means = (y_pred + y_true) / 2.0
    bias = float(np.mean(differences))
    sd = float(np.std(differences, ddof=1)) if len(differences) > 1 else 0.0
    return {
        "means": means,
        "differences": differences,
        "bias": bias,
        "lower_loa": bias - 1.96 * sd,
        "upper_loa": bias + 1.96 * sd,
    }
