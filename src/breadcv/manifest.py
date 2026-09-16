from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

EXPECTED_MEASUREMENT_COLUMNS = {
    "image_w_h",
    "width",
    "heigth",
    "image_thick",
    "thickness",
}

IMAGE_NAME_PATTERN = re.compile(r"^(?P<view>[A-Za-z]+)\s+(?P<batch>[A-Za-z]+\d+)\s+(?P<index>\d+)$")


def structured_image_key(filename: str) -> tuple[str, str, int]:
    """Return a strict, leading-zero-independent key for a dataset image name."""
    stem = Path(str(filename)).stem.strip()
    match = IMAGE_NAME_PATTERN.fullmatch(re.sub(r"\s+", " ", stem))
    if not match:
        raise ValueError(f"Unsupported dataset image name: {filename!r}")
    return (
        match.group("view").upper(),
        match.group("batch").upper(),
        int(match.group("index")),
    )


def physical_sample_id(filename: str) -> str:
    _, batch, index = structured_image_key(filename)
    return f"{batch}:{index}"


def build_size_manifest(measurements: pd.DataFrame, inventory: pd.DataFrame) -> pd.DataFrame:
    missing = EXPECTED_MEASUREMENT_COLUMNS - set(measurements.columns)
    if missing:
        raise ValueError(f"Unsupported Data.csv schema; missing columns: {sorted(missing)}")
    size_images = inventory[inventory["folder"].str.casefold() == "size"].copy()
    if size_images.empty and inventory["folder"].eq(".").all():
        size_images = inventory.copy()
    keyed_images = size_images.assign(image_key=size_images["filename"].map(structured_image_key))
    by_key = keyed_images.groupby("image_key")["relative_path"].apply(list).to_dict()
    width_keys = measurements["image_w_h"].map(structured_image_key)
    duplicated_keys = set(width_keys[width_keys.duplicated(keep=False)])
    rows: list[dict[str, object]] = []
    for csv_row, record in measurements.iterrows():
        width_name = str(record["image_w_h"]).strip()
        thickness_name = str(record["image_thick"]).strip()
        width_key = structured_image_key(width_name)
        width_sample = physical_sample_id(width_name)
        thickness_sample = physical_sample_id(thickness_name)
        paths = by_key.get(width_key, [])
        reasons: list[str] = []
        if width_sample != thickness_sample:
            reasons.append("view_sample_id_mismatch")
        if len(paths) == 0:
            reasons.append("width_height_image_missing")
        elif len(paths) > 1:
            reasons.append("canonical_width_height_key_not_unique")
        if width_key in duplicated_keys:
            reasons.append("ambiguous_duplicate_ground_truth")
        if pd.isna(record["width"]) or pd.isna(record["heigth"]):
            reasons.append("missing_width_or_height_target")
        rows.append(
            {
                "csv_row": int(csv_row),
                "sample_id": width_sample,
                "image_w_h": width_name,
                "image_thickness": thickness_name,
                "canonical_image_key": "|".join(map(str, width_key)),
                "relative_path": paths[0] if len(paths) == 1 else None,
                "target_width": record["width"],
                "target_height": record["heigth"],
                "target_thickness": record["thickness"],
                "eligible_width_height": not reasons,
                "exclusion_reason": ";".join(reasons),
                "target_unit": "mm (unit not encoded in CSV; see limitation)",
            }
        )
    manifest = pd.DataFrame(rows)
    eligible = manifest[manifest["eligible_width_height"]]
    if eligible["sample_id"].duplicated().any():
        raise RuntimeError("STOP_LEAKAGE: eligible physical sample IDs are not unique")
    return manifest
