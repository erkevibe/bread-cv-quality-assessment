#!/usr/bin/env python3
from __future__ import annotations

import argparse

from breadcv.audit import run_audit
from breadcv.config import load_config, resolve_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit the unpacked Mendeley dataset")
    parser.add_argument("--config", default="configs/experiment.yaml")
    args = parser.parse_args()
    config = load_config(args.config)
    summary = run_audit(
        resolve_path(config["dataset"]["root"]),
        resolve_path(config["outputs"]["reports_dir"]),
        config["dataset"].get("csv_name", "size/Data.csv"),
    )
    print(f"Audit complete: {summary['csv_rows']} CSV rows, {summary['image_count']} images")


if __name__ == "__main__":
    main()
