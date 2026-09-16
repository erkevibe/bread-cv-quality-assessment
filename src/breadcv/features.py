from __future__ import annotations

import math

import cv2
import numpy as np

FEATURE_COLUMNS = [
    "width_px",
    "height_px",
    "area_px2",
    "perimeter_px",
    "aspect_ratio",
    "circularity",
    "solidity",
    "extent",
    "equivalent_diameter_px",
    "major_axis_px",
    "minor_axis_px",
    "eccentricity",
]


def contour_features(contour: np.ndarray) -> dict[str, float]:
    if contour is None or len(contour) < 3:
        raise ValueError("A contour with at least three points is required")
    x, y, width, height = cv2.boundingRect(contour)
    area = float(cv2.contourArea(contour))
    perimeter = float(cv2.arcLength(contour, True))
    hull_area = float(cv2.contourArea(cv2.convexHull(contour)))
    aspect_ratio = width / height if height else math.nan
    circularity = 4.0 * math.pi * area / perimeter**2 if perimeter else math.nan
    solidity = area / hull_area if hull_area else math.nan
    extent = area / (width * height) if width and height else math.nan
    equivalent_diameter = math.sqrt(4.0 * area / math.pi) if area > 0 else math.nan
    major_axis = minor_axis = eccentricity = math.nan
    if len(contour) >= 5:
        _, axes, _ = cv2.fitEllipse(contour)
        minor_axis, major_axis = sorted(map(float, axes))
        if major_axis > 0:
            eccentricity = math.sqrt(max(0.0, 1.0 - (minor_axis / major_axis) ** 2))
    return {
        "width_px": float(width),
        "height_px": float(height),
        "area_px2": area,
        "perimeter_px": perimeter,
        "aspect_ratio": float(aspect_ratio),
        "circularity": float(circularity),
        "solidity": float(solidity),
        "extent": float(extent),
        "equivalent_diameter_px": float(equivalent_diameter),
        "major_axis_px": float(major_axis),
        "minor_axis_px": float(minor_axis),
        "eccentricity": float(eccentricity),
    }
