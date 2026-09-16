import numpy as np

from breadcv.calibration import LinearCalibration
from breadcv.evaluation import bland_altman, regression_metrics


def test_linear_calibration_recovers_known_mapping() -> None:
    pixels = np.array([10, 20, 30, 40], dtype=float)
    millimetres = 0.5 * pixels + 3.0
    model = LinearCalibration().fit(pixels, millimetres)
    predicted = model.predict(np.array([50.0]))
    assert np.isclose(model.coefficient, 0.5)
    assert np.isclose(model.intercept, 3.0)
    assert np.isclose(predicted[0], 28.0)


def test_metrics_and_bland_altman_known_values() -> None:
    actual = np.array([10.0, 20.0, 30.0])
    predicted = np.array([11.0, 18.0, 33.0])
    metrics = regression_metrics(actual, predicted)
    agreement = bland_altman(actual, predicted)
    assert np.isclose(metrics["mae"], 2.0)
    assert np.isclose(metrics["rmse"], np.sqrt(14 / 3))
    assert np.isclose(agreement["bias"], 2 / 3)
