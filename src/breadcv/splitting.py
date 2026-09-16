from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


def grouped_train_validation_test_split(
    frame: pd.DataFrame,
    group_column: str,
    *,
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
    test_fraction: float = 0.15,
    seed: int = 42,
) -> pd.Series:
    total = train_fraction + validation_fraction + test_fraction
    if not np.isclose(total, 1.0):
        raise ValueError("Split fractions must sum to 1")
    if group_column not in frame or frame[group_column].isna().any():
        raise ValueError(f"Valid {group_column!r} is required for every row")
    if frame[group_column].nunique() < 3:
        raise ValueError("At least three physical sample groups are required")
    first = GroupShuffleSplit(n_splits=1, train_size=train_fraction, random_state=seed)
    train_idx, rest_idx = next(first.split(frame, groups=frame[group_column]))
    rest = frame.iloc[rest_idx]
    relative_validation = validation_fraction / (validation_fraction + test_fraction)
    second = GroupShuffleSplit(n_splits=1, train_size=relative_validation, random_state=seed + 1)
    val_local, test_local = next(second.split(rest, groups=rest[group_column]))
    labels = pd.Series(index=frame.index, dtype="object")
    labels.iloc[train_idx] = "train"
    labels.iloc[rest_idx[val_local]] = "validation"
    labels.iloc[rest_idx[test_local]] = "test"
    assert_group_disjoint(frame.assign(split=labels), group_column, "split")
    return labels


def assert_group_disjoint(frame: pd.DataFrame, group_column: str, split_column: str) -> None:
    counts = frame.groupby(group_column, dropna=False)[split_column].nunique()
    leaked = counts[counts > 1]
    if not leaked.empty:
        raise RuntimeError(f"STOP_LEAKAGE: {len(leaked)} groups occur in multiple splits")
