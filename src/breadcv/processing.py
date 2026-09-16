from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .features import contour_features
from .segmentation import SegmentationResult, segment_bread


def resize_for_processing(image: np.ndarray, max_size: int) -> tuple[np.ndarray, float]:
    height, width = image.shape[:2]
    scale = min(1.0, max_size / max(height, width))
    if scale == 1.0:
        return image, scale
    resized = cv2.resize(
        image,
        (max(1, round(width * scale)), max(1, round(height * scale))),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


def draw_overlay(image: np.ndarray, result: SegmentationResult) -> np.ndarray:
    overlay = image.copy()
    cv2.drawContours(overlay, [result.contour], -1, (0, 255, 0), 2)
    x, y, width, height = cv2.boundingRect(result.contour)
    cv2.rectangle(overlay, (x, y), (x + width, y + height), (255, 0, 0), 2)
    cv2.putText(
        overlay,
        f"{width} x {height} px",
        (x, max(20, y - 8)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 0, 0),
        2,
        cv2.LINE_AA,
    )
    return overlay


def extract_features(
    manifest: pd.DataFrame,
    dataset_root: Path,
    image_config: dict[str, object],
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    rows: list[dict[str, object]] = []
    examples: list[dict[str, object]] = []
    max_size = int(image_config.get("max_size", 1024))
    for record in manifest.itertuples(index=False):
        if not record.eligible_width_height:
            continue
        path = dataset_root / record.relative_path
        image = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if image is None:
            rows.append(
                {
                    "sample_id": record.sample_id,
                    "relative_path": record.relative_path,
                    "processing_status": "failed",
                    "processing_error": "image_read_failed",
                }
            )
            continue
        resized, scale = resize_for_processing(image, max_size)
        started = time.perf_counter()
        try:
            result = segment_bread(
                resized,
                gaussian_kernel=int(image_config.get("gaussian_kernel", 5)),
                morphology_kernel=int(image_config.get("morphology_kernel", 7)),
                morphology_iterations=int(image_config.get("morphology_iterations", 2)),
                min_contour_area_fraction=float(
                    image_config.get("min_contour_area_fraction", 0.01)
                ),
            )
            values = contour_features(result.contour)
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            row = {
                "sample_id": record.sample_id,
                "relative_path": record.relative_path,
                "split": record.split,
                "target_width": record.target_width,
                "target_height": record.target_height,
                "processing_status": "ok",
                "processing_error": "",
                "processing_ms": elapsed_ms,
                "original_width_px": image.shape[1],
                "original_height_px": image.shape[0],
                "processing_scale": scale,
                "threshold_inverted": result.inverted,
                "contour_area_fraction": result.area_fraction,
                "contour_touches_border": result.touches_border,
                **values,
            }
            rows.append(row)
            if len(examples) < 6:
                examples.append(
                    {
                        "sample_id": record.sample_id,
                        "original": cv2.cvtColor(resized, cv2.COLOR_BGR2RGB),
                        "mask": result.mask,
                        "overlay": cv2.cvtColor(draw_overlay(resized, result), cv2.COLOR_BGR2RGB),
                    }
                )
        except (ValueError, cv2.error) as error:
            rows.append(
                {
                    "sample_id": record.sample_id,
                    "relative_path": record.relative_path,
                    "split": record.split,
                    "target_width": record.target_width,
                    "target_height": record.target_height,
                    "processing_status": "failed",
                    "processing_error": str(error),
                    "processing_ms": (time.perf_counter() - started) * 1000.0,
                }
            )
    return pd.DataFrame(rows), examples
