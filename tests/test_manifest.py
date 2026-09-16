import pandas as pd

from breadcv.manifest import (
    build_size_manifest,
    physical_sample_id,
    structured_image_key,
)


def test_physical_sample_id_removes_view_prefix() -> None:
    assert physical_sample_id("E B1 01.png") == "B1:1"
    assert physical_sample_id("C B1 1.png") == "B1:1"


def test_structured_key_normalises_only_numeric_leading_zeroes() -> None:
    assert structured_image_key("E B1 1.png") == structured_image_key("E B1 01.png")


def test_duplicate_ground_truth_is_excluded() -> None:
    measurements = pd.DataFrame(
        {
            "image_w_h": ["E B1 1.png", "E W2 2.png", "E W2 2.png"],
            "width": [100.0, 98.0, 93.5],
            "heigth": [90.0, 91.4, 87.9],
            "image_thick": ["C B1 1.png", "C W2 2.png", "C W2 2.png"],
            "thickness": [13.0, 13.4, 12.0],
        }
    )
    inventory = pd.DataFrame(
        {
            "folder": ["size", "size"],
            "filename": ["E B1 01.png", "E W2 02.png"],
            "relative_path": ["size/E B1 01.png", "size/E W2 02.png"],
        }
    )
    manifest = build_size_manifest(measurements, inventory)
    assert manifest["eligible_width_height"].sum() == 1
    assert manifest.loc[0, "relative_path"] == "size/E B1 01.png"
    assert manifest.loc[1, "exclusion_reason"] == "ambiguous_duplicate_ground_truth"
    assert manifest.loc[2, "exclusion_reason"] == "ambiguous_duplicate_ground_truth"
