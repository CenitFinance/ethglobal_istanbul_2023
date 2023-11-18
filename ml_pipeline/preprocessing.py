import json
import os
from hashlib import md5
from math import ceil
from typing import Union

import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler


def transform_data(
    data: pd.DataFrame,
    feature_cols: list[str],
    scaler: StandardScaler,
) -> torch.Tensor:
    """
    Transform data to torch tensor and scale features.
    """
    assert all(
        [c in data.columns for c in feature_cols]
    ), f"feature_cols {feature_cols} not in data.columns"

    X = data[feature_cols].values
    X = scaler.transform(X)
    X = torch.tensor(X, dtype=torch.float32)

    assert X.shape[1] == len(feature_cols)

    return X


def preprocess_data(
    data: pd.DataFrame,
    label_col: str,
    grouping_col: str,  # data for GroupKFold, in n_splits groups. Also elements left out for test set
    n_splits: int = 5,
    test_size: float = 0.1,  # Fraction of data to use for test set, outside of all folds
    feature_cols: list[str] = None,  # If None, all columns except label_col are used
    do_feature_scaling: bool = True,  # If True, features are scaled to mean 0 and std 1 with sklearn StandardScaler trained on all but test set
    seed: int = 1534,
) -> tuple[
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    torch.Tensor,
    list[tuple[np.ndarray, np.ndarray]],
    Union[tuple[StandardScaler, float, float], tuple[None, None, None]],
    pd.Index,
    pd.Index,
]:
    """
    Scale data and and split into features and labels as torch tensors.
    The split is grouped and the test set is not used for scaling.
    """
    assert test_size > 0 and test_size < 1, "test_size must be between 0 and 1"
    assert n_splits > 1, "n_splits must be greater than 1"
    assert (
        grouping_col in data.columns
    ), f"grouping_col {grouping_col} not in data.columns"
    assert label_col in data.columns, f"label_col {label_col} not in data.columns"
    if feature_cols is not None:
        assert all(
            [c in data.columns for c in feature_cols]
        ), f"feature_cols {feature_cols} not in raw_data.columns"

    rng = np.random.default_rng(seed=seed)

    groups_values = data[grouping_col].value_counts().to_dict()
    groups_unique = list(groups_values.keys())
    groups_unique_randomized: list = rng.permutation(groups_unique).tolist()
    total_elements = sum(groups_values.values())
    test_elements_min = ceil(total_elements * test_size)

    print(f"Total elements: {total_elements}")
    print(f"Test elements min: {test_elements_min}\n")

    i = 0
    test_groups = []
    while sum(groups_values[g] for g in test_groups) < test_elements_min:
        test_groups.append(groups_unique_randomized[i])
        i += 1
    train_groups = [g for g in groups_unique if g not in test_groups]

    print(
        f"Final train elements: {sum(groups_values[g] for g in train_groups)} across {len(train_groups)} groups"
    )
    print(
        f"Final test elements: {sum(groups_values[g] for g in test_groups)} across {len(test_groups)} groups"
    )

    # Train test split
    train_data = data[data[grouping_col].isin(train_groups)]
    train_groups = train_data[grouping_col].values
    train_index_new_order = train_data.index
    train_X = (
        train_data[feature_cols].values
        if feature_cols is not None
        else train_data.drop(columns=[label_col, grouping_col]).values
    )
    train_y = train_data[label_col].values

    test_data = data[data[grouping_col].isin(test_groups)]
    test_index_new_order = test_data.index
    test_X = (
        test_data[feature_cols].values
        if feature_cols is not None
        else test_data.drop(columns=[label_col, grouping_col]).values
    )
    test_y = test_data[label_col].values

    # GroupKFold
    group_kfold = GroupKFold(n_splits=n_splits)
    group_kfold_splits = list(group_kfold.split(train_X, train_y, groups=train_groups))

    print("\nElements in each fold:")
    for i, (train_index, test_index) in enumerate(group_kfold_splits):
        # format: Fold i: x train elements (n groups), y test elements (n groups)
        print(
            f"Fold {i}: {len(train_index)} ({len(np.unique(train_groups[train_index]))} groups), {len(test_index)} ({len(np.unique(train_groups[test_index]))} groups)"
        )

    # Feature scaling
    if do_feature_scaling:
        scaler = StandardScaler()
        scaler.fit(train_X)
        train_X = scaler.transform(train_X)
        test_X = scaler.transform(test_X)

        mean = scaler.mean_
        std = scaler.scale_
    else:
        scaler = None
        mean = None
        std = None

    # Convert to torch tensors
    train_X = torch.tensor(train_X, dtype=torch.float32)
    train_y = torch.tensor(train_y, dtype=torch.long).unsqueeze(1)
    test_X = torch.tensor(test_X, dtype=torch.float32)
    test_y = torch.tensor(test_y, dtype=torch.long).unsqueeze(1)

    assert train_X.shape[0] == train_y.shape[0]
    assert test_X.shape[0] == test_y.shape[0]
    assert train_X.shape[1] == test_X.shape[1]
    assert (
        train_X.shape[1] == len(feature_cols)
        if feature_cols is not None
        else (data.shape[1] - 2)
    )
    assert train_y.shape[1] == 1
    assert test_y.shape[1] == 1

    # Hash the group_kfold_splits
    group_kfold_splits_hash = md5(
        json.dumps(str(group_kfold_splits)).encode()
    ).hexdigest()
    print(f"\nGroupKFold splits hash: {group_kfold_splits_hash}")

    return (
        train_X,
        train_y,
        test_X,
        test_y,
        group_kfold_splits,
        (scaler, mean, std),
        train_index_new_order,
        test_index_new_order,
    )
