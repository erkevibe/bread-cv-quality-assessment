#!/usr/bin/env python3
"""Download and safely extract the official Mendeley Data v1 archive.

The public Download All endpoint is the same endpoint used by the official dataset page. The
server does not reliably support byte-range resume, so downloads are atomic and always start
from byte zero. Source data remains ignored by Git.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import tempfile
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from breadcv.config import project_root

DATASET_ID = "f663p7c89m"
DATASET_VERSION = 1
DATASET_DOI = "10.17632/f663p7c89m.1"
DOWNLOAD_URL = f"https://data.mendeley.com/public-api/zip/{DATASET_ID}/download/{DATASET_VERSION}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def safe_extract(archive: Path, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    destination_real = destination.resolve()
    with zipfile.ZipFile(archive) as zipped:
        bad = zipped.testzip()
        if bad is not None:
            raise zipfile.BadZipFile(f"CRC failure in archive member: {bad}")
        total_uncompressed = sum(info.file_size for info in zipped.infolist())
        if total_uncompressed > 20 * 1024**3:
            raise ValueError("Refusing archive larger than 20 GiB after extraction")
        for info in zipped.infolist():
            target = (destination / info.filename).resolve()
            if destination_real not in target.parents and target != destination_real:
                raise ValueError(f"Unsafe archive member: {info.filename}")
        zipped.extractall(destination)


def download(destination: Path) -> dict[str, object]:
    destination.mkdir(parents=True, exist_ok=True)
    archive_path = destination / f"{DATASET_ID}-{DATASET_VERSION}.zip"
    with tempfile.NamedTemporaryFile(dir=destination, suffix=".part", delete=False) as temporary:
        temporary_path = Path(temporary.name)
        request = urllib.request.Request(
            DOWNLOAD_URL,
            headers={"User-Agent": "bread-cv-quality-assessment/0.1 (+research reproducibility)"},
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                shutil.copyfileobj(response, temporary, length=1024 * 1024)
            os.replace(temporary_path, archive_path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
    with zipfile.ZipFile(archive_path) as zipped:
        bad = zipped.testzip()
        if bad is not None:
            raise zipfile.BadZipFile(f"CRC failure in archive member: {bad}")
    provenance = {
        "dataset_id": DATASET_ID,
        "version": DATASET_VERSION,
        "doi": DATASET_DOI,
        "official_download_url": DOWNLOAD_URL,
        "downloaded_at_utc": datetime.now(UTC).isoformat(),
        "archive_bytes": archive_path.stat().st_size,
        "archive_sha256": sha256_file(archive_path),
    }
    (destination / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, default=project_root() / "data" / "raw")
    parser.add_argument("--extract", action="store_true", help="Safely extract after download")
    args = parser.parse_args()
    provenance = download(args.destination)
    archive = args.destination / f"{DATASET_ID}-{DATASET_VERSION}.zip"
    if args.extract:
        safe_extract(archive, args.destination / "dataset")
    print(json.dumps(provenance, indent=2))


if __name__ == "__main__":
    main()
