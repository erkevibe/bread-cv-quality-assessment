from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from .data import (
    candidate_id_columns,
    candidate_target_columns,
    find_csv_path,
    find_dataset_root,
    image_inventory,
    read_measurements,
)
from .manifest import (
    EXPECTED_MEASUREMENT_COLUMNS,
    build_size_manifest,
    structured_image_key,
)


def _markdown_table(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "_No rows._"
    return frame.to_markdown(index=False)


def _portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return path.name


def run_audit(data_root: Path, output_dir: Path, csv_name: str = "Data.csv") -> dict[str, object]:
    dataset_root = find_dataset_root(data_root, csv_name)
    csv_path = find_csv_path(data_root, csv_name)
    csv_frame = read_measurements(csv_path)
    inventory = image_inventory(dataset_root)
    output_dir.mkdir(parents=True, exist_ok=True)
    inventory.to_csv(output_dir / "files_inventory.csv", index=False)

    columns = pd.DataFrame(
        {
            "column": csv_frame.columns,
            "dtype": [str(csv_frame[column].dtype) for column in csv_frame.columns],
            "missing": [int(csv_frame[column].isna().sum()) for column in csv_frame.columns],
            "unique": [int(csv_frame[column].nunique(dropna=True)) for column in csv_frame.columns],
        }
    )
    numeric_rows = []
    for column in csv_frame.select_dtypes(include="number").columns:
        numeric_rows.append(
            {
                "column": column,
                "min": csv_frame[column].min(),
                "max": csv_frame[column].max(),
                "mean": csv_frame[column].mean(),
            }
        )
    numeric = pd.DataFrame(numeric_rows)
    folder_summary = (
        inventory.groupby("folder", dropna=False)
        .agg(
            files=("relative_path", "size"),
            readable=("readable", "sum"),
            unique_sizes=(
                "width",
                lambda s: int(len(set(zip(s, inventory.loc[s.index, "height"], strict=True)))),
            ),
            channels=("channels", lambda s: ", ".join(map(str, sorted(s.dropna().unique())))),
            formats=("format", lambda s: ", ".join(sorted(s.dropna().unique()))),
        )
        .reset_index()
    )
    csv_profiles = []
    for other_csv in sorted(dataset_root.rglob("Data.csv")):
        frame = read_measurements(other_csv)
        folder = other_csv.parent.name
        image_columns = [
            column for column in frame.columns if "image" in str(column).strip().casefold()
        ]
        referenced_names = set()
        for column in image_columns:
            referenced_names.update(frame[column].dropna().astype(str).str.strip())
        actual_names = set(inventory.loc[inventory["folder"] == folder, "filename"])
        profile: dict[str, object] = {
            "folder": folder,
            "rows": len(frame),
            "columns": ", ".join(map(str, frame.columns)),
            "missing_cells": int(frame.isna().sum().sum()),
            "duplicate_rows": int(frame.duplicated().sum()),
            "referenced_unique_images": len(referenced_names),
            "raw_exact_references_found": len(referenced_names & actual_names),
            "raw_exact_unreferenced_folder_images": len(actual_names - referenced_names),
            "raw_exact_missing_references": len(referenced_names - actual_names),
            "canonical_references_found": "n/a",
            "canonical_missing_references": "n/a",
        }
        if folder.casefold() == "size":
            canonical_references = {structured_image_key(name) for name in referenced_names}
            canonical_actual = {structured_image_key(name) for name in actual_names}
            profile["canonical_references_found"] = len(canonical_references & canonical_actual)
            profile["canonical_missing_references"] = len(canonical_references - canonical_actual)
        csv_profiles.append(profile)
    csv_profile_frame = pd.DataFrame(csv_profiles)
    mapping_summary: dict[str, object] = {"status": "unsupported_schema"}
    if EXPECTED_MEASUREMENT_COLUMNS <= set(csv_frame.columns):
        manifest = build_size_manifest(csv_frame, inventory)
        exclusions = manifest.loc[~manifest["eligible_width_height"], "exclusion_reason"]
        mapping_summary = {
            "status": "verified_with_exclusions",
            "eligible_width_height_samples": int(manifest["eligible_width_height"].sum()),
            "excluded_rows": int((~manifest["eligible_width_height"]).sum()),
            "exclusion_reasons": exclusions.value_counts().to_dict(),
            "unique_physical_sample_ids": int(
                manifest.loc[manifest["eligible_width_height"], "sample_id"].nunique()
            ),
        }
    summary: dict[str, object] = {
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "dataset_root": _portable_path(dataset_root),
        "csv_path": _portable_path(csv_path),
        "all_csv_paths": [
            str(path.relative_to(dataset_root)) for path in sorted(dataset_root.rglob("Data.csv"))
        ],
        "csv_rows": int(len(csv_frame)),
        "csv_columns": list(map(str, csv_frame.columns)),
        "candidate_id_columns": candidate_id_columns(csv_frame),
        "candidate_targets": candidate_target_columns(csv_frame),
        "image_count": int(len(inventory)),
        "unreadable_images": int((~inventory["readable"]).sum()) if len(inventory) else 0,
        "folders": folder_summary.to_dict(orient="records"),
        "csv_profiles": csv_profiles,
        "size_mapping": mapping_summary,
    }
    (output_dir / "data_audit.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, default=str), encoding="utf-8"
    )
    report = f"""# Dataset audit

Generated automatically at `{summary["generated_at_utc"]}` from Mendeley Data version 1,
DOI `10.17632/f663p7c89m.1`. This report describes observations; it does not infer a valid
CSV-to-image mapping unless that mapping is subsequently verified.

## Data.csv

- Path: `{summary["csv_path"]}`
- All CSV files discovered: `{summary["all_csv_paths"]}`
- Rows: **{len(csv_frame)}**
- Candidate sample-ID columns: `{summary["candidate_id_columns"]}`
- Candidate target columns: `{summary["candidate_targets"]}`

{_markdown_table(columns)}

### Numeric ranges

{_markdown_table(numeric)}

## Images

- Total discovered images: **{len(inventory)}**
- Unreadable images: **{summary["unreadable_images"]}**

{_markdown_table(folder_summary)}

### CSV files by published folder

{_markdown_table(csv_profile_frame)}

The complete per-file inventory, including dimensions, channel count, byte size, format, and
SHA-256, is stored in `reports/files_inventory.csv`.

## CSV ↔ image relationship and leakage gate

Status: **{mapping_summary["status"]}**. Eligible width/height physical samples:
**{mapping_summary.get("eligible_width_height_samples", "n/a")}**. Excluded CSV rows:
**{mapping_summary.get("excluded_rows", "n/a")}** with reasons
`{mapping_summary.get("exclusion_reasons", {})}`. The profile table labels raw exact-name
diagnostics separately from the verified mapping. The verified size mapping parses only the
strict `view batch integer-index` filename structure, so published CSV index `1` maps to file
index `01`; it performs no fuzzy or similarity-based repair. A physical sample ID is the
view-independent `(batch, integer-index)` pair shared by the `E` width/height and `C` thickness
views. Image-level random splitting is prohibited. Derived
`color` crops are excluded from the size experiment and cannot cross sample partitions.
"""
    (output_dir / "data_audit.md").write_text(report, encoding="utf-8")
    return summary
