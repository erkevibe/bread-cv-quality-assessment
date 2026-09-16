from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LinearRegression


@dataclass
class LinearCalibration:
    model: LinearRegression | None = None

    def fit(self, pixels: np.ndarray, millimetres: np.ndarray) -> LinearCalibration:
        x = np.asarray(pixels, dtype=float).reshape(-1, 1)
        y = np.asarray(millimetres, dtype=float)
        if len(x) != len(y) or len(x) < 2:
            raise ValueError("Calibration needs at least two paired observations")
        self.model = LinearRegression().fit(x, y)
        return self

    def predict(self, pixels: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise RuntimeError("Calibration has not been fitted")
        return self.model.predict(np.asarray(pixels, dtype=float).reshape(-1, 1))

    @property
    def coefficient(self) -> float:
        if self.model is None:
            raise RuntimeError("Calibration has not been fitted")
        return float(self.model.coef_[0])

    @property
    def intercept(self) -> float:
        if self.model is None:
            raise RuntimeError("Calibration has not been fitted")
        return float(self.model.intercept_)
