#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/breadcv-matplotlib")
os.environ.setdefault("TORCH_HOME", "/tmp/breadcv-cache/torch")

from breadcv.config import load_config  # noqa: E402
from breadcv.experiment import run_experiment  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the reproducible bread-CV experiment")
    parser.add_argument("--config", default="configs/experiment.yaml")
    args = parser.parse_args()
    provenance = run_experiment(load_config(args.config))
    print(json.dumps(provenance, indent=2, default=str))


if __name__ == "__main__":
    main()
