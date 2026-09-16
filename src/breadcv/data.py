from __future__ import annotations

import hashlib
import re
from pathlib import Path

import cv2
import pandas as pd

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def find_csv_path(root: Path, csv_name: str = "Data.csv") -> Path:
    requested = Path(csv_name)
    candidates = sorted(root.rglob(requested.name)) if root.exists() else []
    if requested.parent != Path("."):
        requested_suffix = requested.as_posix().casefold()
        candidates = [
            path for path in candidates if path.as_posix().casefold().endswith(requested_suffix)
        ]
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"Expected exactly one {csv_name!r} under {root}, found {len(candidates)}"
        )
    return candidates[0]


def find_dataset_root(root: Path, csv_name: str = "Data.csv") -> Path:
    csv_path = find_csv_path(root, csv_name)
    parent = csv_path.parent
    expected = {"size", "color", "texture"}
    if parent.name.casefold() in expected:
        siblings = {path.name.casefold() for path in parent.parent.iterdir() if path.is_dir()}
        if len(expected & siblings) >= 2:
            return parent.parent
    return parent


def read_measurements(path: Path) -> pd.DataFrame:
    first_line = path.read_text(encoding="utf-8-sig", errors="replace").splitlines()[0]
    separator = ";" if first_line.count(";") > first_line.count(",") else ","
    decimal = "," if separator == ";" else "."
    return pd.read_csv(path, sep=separator, decimal=decimal, encoding="utf-8-sig")


def image_inventory(dataset_root: Path) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for path in sorted(dataset_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        image = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        relative = path.relative_to(dataset_root)
        if image is None:
            rows.append(
                {
                    "relative_path": relative.as_posix(),
                    "folder": relative.parts[0] if len(relative.parts) > 1 else ".",
                    "filename": path.name,
                    "readable": False,
                    "width": None,
                    "height": None,
                    "channels": None,
                    "format": path.suffix.lower().lstrip("."),
                    "bytes": path.stat().st_size,
                    "sha256": sha256_file(path),
                }
            )
            continue
        channels = 1 if image.ndim == 2 else image.shape[2]
        rows.append(
            {
                "relative_path": relative.as_posix(),
                "folder": relative.parts[0] if len(relative.parts) > 1 else ".",
                "filename": path.name,
                "readable": True,
                "width": int(image.shape[1]),
                "height": int(image.shape[0]),
                "channels": int(channels),
                "format": path.suffix.lower().lstrip("."),
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    return pd.DataFrame(rows)


def normalise_token(value: object) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).casefold())


def filename_tokens(filename: str) -> list[str]:
    stem = Path(filename).stem
    return [token for token in re.split(r"[^A-Za-z0-9]+", stem) if token]


def candidate_id_columns(frame: pd.DataFrame) -> list[str]:
    names = []
    for column in frame.columns:
        normalised = normalise_token(column)
        if normalised in {"id", "sampleid", "sample", "breadid", "code", "name"}:
            names.append(str(column))
    return names


def candidate_target_columns(frame: pd.DataFrame) -> dict[str, list[str]]:
    targets = {"width": [], "height": [], "thickness": []}
    for column in frame.columns:
        token = normalise_token(column)
        for target in targets:
            aliases = {"height", "heigth"} if target == "height" else {target}
            if any(alias in token for alias in aliases) and pd.api.types.is_numeric_dtype(
                frame[column]
            ):
                targets[target].append(str(column))
    return targets


def infer_mapping(inventory: pd.DataFrame, csv_frame: pd.DataFrame, id_column: str) -> pd.DataFrame:
    lookup: dict[str, list[int]] = {}
    for index, value in csv_frame[id_column].items():
        key = normalise_token(value)
        if key:
            lookup.setdefault(key, []).append(index)
    rows: list[dict[str, object]] = []
    for image in inventory.itertuples(index=False):
        stem_key = normalise_token(Path(image.filename).stem)
        matches: set[int] = set()
        for key, indices in lookup.items():
            is_match = stem_key == key or stem_key.startswith(key)
            is_match = is_match or key in filename_tokens(image.filename)
            if key and is_match:
                matches.update(indices)
        status = "unique" if len(matches) == 1 else "unmatched" if not matches else "ambiguous"
        rows.append(
            {
                "relative_path": image.relative_path,
                "filename": image.filename,
                "folder": image.folder,
                "mapping_status": status,
                "csv_row_index": next(iter(matches)) if len(matches) == 1 else None,
                "sample_id": csv_frame.loc[next(iter(matches)), id_column]
                if len(matches) == 1
                else None,
                "mapping_rule": f"normalised filename contains {id_column}",
            }
        )
    return pd.DataFrame(rows)
