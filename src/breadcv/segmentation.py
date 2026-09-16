from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SegmentationResult:
    mask: np.ndarray
    contour: np.ndarray
    inverted: bool
    area_fraction: float
    touches_border: bool


def _largest_contour(mask: np.ndarray) -> np.ndarray | None:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea) if contours else None


def _score_candidate(mask: np.ndarray, min_area_fraction: float) -> tuple[float, np.ndarray | None]:
    contour = _largest_contour(mask)
    if contour is None:
        return float("-inf"), None
    image_area = float(mask.shape[0] * mask.shape[1])
    area_fraction = cv2.contourArea(contour) / image_area
    if area_fraction < min_area_fraction or area_fraction > 0.98:
        return float("-inf"), contour
    x, y, w, h = cv2.boundingRect(contour)
    touches = x == 0 or y == 0 or x + w >= mask.shape[1] or y + h >= mask.shape[0]
    centre = np.array([mask.shape[1] / 2.0, mask.shape[0] / 2.0])
    moments = cv2.moments(contour)
    if moments["m00"]:
        centroid = np.array([moments["m10"] / moments["m00"], moments["m01"] / moments["m00"]])
        centre_penalty = np.linalg.norm((centroid - centre) / centre)
    else:
        centre_penalty = 2.0
    score = area_fraction - 0.35 * float(touches) - 0.1 * centre_penalty
    return score, contour


def segment_bread(
    image: np.ndarray,
    *,
    gaussian_kernel: int = 5,
    morphology_kernel: int = 7,
    morphology_iterations: int = 2,
    min_contour_area_fraction: float = 0.01,
) -> SegmentationResult:
    if image is None or image.size == 0:
        raise ValueError("Image is empty")
    if image.ndim == 2:
        gray = image
    elif image.ndim == 3 and image.shape[2] in (3, 4):
        code = cv2.COLOR_BGRA2GRAY if image.shape[2] == 4 else cv2.COLOR_BGR2GRAY
        gray = cv2.cvtColor(image, code)
    else:
        raise ValueError(f"Unsupported image shape: {image.shape}")
    if gaussian_kernel < 1 or gaussian_kernel % 2 == 0:
        raise ValueError("gaussian_kernel must be a positive odd integer")
    blurred = cv2.GaussianBlur(gray, (gaussian_kernel, gaussian_kernel), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (morphology_kernel, morphology_kernel))
    candidates: list[tuple[float, bool, np.ndarray, np.ndarray | None]] = []
    for inverted, candidate in ((False, binary), (True, cv2.bitwise_not(binary))):
        cleaned = cv2.morphologyEx(
            candidate, cv2.MORPH_OPEN, kernel, iterations=morphology_iterations
        )
        cleaned = cv2.morphologyEx(
            cleaned, cv2.MORPH_CLOSE, kernel, iterations=morphology_iterations
        )
        score, contour = _score_candidate(cleaned, min_contour_area_fraction)
        candidates.append((score, inverted, cleaned, contour))
    _, inverted, mask, contour = max(candidates, key=lambda row: row[0])
    if contour is None or not np.isfinite(max(row[0] for row in candidates)):
        raise ValueError("No valid bread contour found")
    x, y, w, h = cv2.boundingRect(contour)
    touches_border = x == 0 or y == 0 or x + w >= mask.shape[1] or y + h >= mask.shape[0]
    return SegmentationResult(
        mask=mask,
        contour=contour,
        inverted=inverted,
        area_fraction=float(cv2.contourArea(contour) / (mask.shape[0] * mask.shape[1])),
        touches_border=touches_border,
    )
