#!/usr/bin/env python3
"""Remove generated experiment artefacts while preserving source, config, and references."""

from __future__ import annotations

import shutil

from breadcv.config import project_root


def main() -> None:
    root = project_root()
    targets = [
        root / "results" / "data",
        root / "results" / "metrics",
        root / "results" / "models",
        root / "results" / "predictions",
        root / "results" / "runs",
        root / "paper" / "figures",
        root / "paper" / "article_ru.md",
        root / "paper" / "article_en.md",
        root / "paper" / "article.tex",
        root / "reports" / "files_inventory.csv",
        root / "reports" / "data_audit.json",
        root / "reports" / "data_audit.md",
        root / "reports" / "results.md",
    ]
    for target in targets:
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
    print("Generated artefacts removed; source data, configuration, and references were preserved.")


if __name__ == "__main__":
    main()
