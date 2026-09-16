import pandas as pd
import pytest

from breadcv.splitting import assert_group_disjoint, grouped_train_validation_test_split


def test_grouped_split_never_leaks_samples() -> None:
    frame = pd.DataFrame(
        {"sample_id": [f"sample-{index // 2:02d}" for index in range(40)], "value": range(40)}
    )
    split = grouped_train_validation_test_split(frame, "sample_id", seed=42)
    checked = frame.assign(split=split)
    assert set(split) == {"train", "validation", "test"}
    assert_group_disjoint(checked, "sample_id", "split")


def test_explicit_leakage_raises() -> None:
    frame = pd.DataFrame({"sample_id": ["A", "A"], "split": ["train", "test"]})
    with pytest.raises(RuntimeError, match="STOP_LEAKAGE"):
        assert_group_disjoint(frame, "sample_id", "split")
