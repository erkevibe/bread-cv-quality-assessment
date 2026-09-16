import cv2
import numpy as np

from breadcv.features import contour_features
from breadcv.segmentation import segment_bread


def test_pipeline_segments_synthetic_bread_shape() -> None:
    image = np.full((240, 320, 3), 245, dtype=np.uint8)
    cv2.ellipse(image, (160, 120), (90, 55), 0, 0, 360, (60, 100, 150), -1)
    result = segment_bread(image, min_contour_area_fraction=0.02)
    features = contour_features(result.contour)
    assert result.mask.shape == image.shape[:2]
    assert result.mask.dtype == np.uint8
    assert 160 <= features["width_px"] <= 190
    assert 95 <= features["height_px"] <= 125
    assert 0 < features["circularity"] <= 1.05
    assert 0 < features["solidity"] <= 1.01


def test_empty_image_is_rejected() -> None:
    with np.testing.assert_raises(ValueError):
        segment_bread(np.array([], dtype=np.uint8))
