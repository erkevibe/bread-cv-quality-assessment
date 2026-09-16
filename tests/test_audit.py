from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from breadcv.audit import run_audit


def test_audit_profiles_csv_and_image(tmp_path: Path) -> None:
    data = tmp_path / "raw" / "dataset"
    (data / "size").mkdir(parents=True)
    pd.DataFrame({"sample_id": ["A", "B"], "width": [10.0, 12.0], "height": [5.0, 6.0]}).to_csv(
        data / "Data.csv", index=False
    )
    image = np.full((20, 30, 3), 127, dtype=np.uint8)
    assert cv2.imwrite(str(data / "size" / "A.png"), image)
    output = tmp_path / "reports"
    summary = run_audit(tmp_path / "raw", output)
    assert summary["csv_rows"] == 2
    assert summary["image_count"] == 1
    assert (output / "data_audit.md").is_file()
    inventory = pd.read_csv(output / "files_inventory.csv")
    assert inventory.loc[0, "width"] == 30
    assert inventory.loc[0, "height"] == 20
