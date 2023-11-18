import json
from pathlib import Path
from typing import Any

import pandas as pd


def generate_user_groups(
    groups: list[tuple[str, float, float]],
    data: pd.DataFrame,
    prediction_col: str,
    value_col: str,
) -> list[dict[str, Any]]:
    groups_data = []
    for label, lower, higher in groups:
        data_group = data[(data[value_col] >= lower) & (data[value_col] < higher)]
        count = len(data_group)
        mean = data_group[prediction_col].mean()
        median = data_group[prediction_col].median()
        pct25 = data_group[prediction_col].quantile(0.25)
        pct75 = data_group[prediction_col].quantile(0.75)
        pct10 = data_group[prediction_col].quantile(0.1)
        pct90 = data_group[prediction_col].quantile(0.9)
        total_value = data_group[value_col].sum()
        mean_value = data_group[value_col].mean()
        median_value = data_group[value_col].median()
        group_data = {
            "label": label,
            "lower": float(lower),
            "higher": float(higher),
            "count": float(count),
            "mean": float(mean),
            "median": float(median),
            "pct25": float(pct25),
            "pct75": float(pct75),
            "pct10": float(pct10),
            "pct90": float(pct90),
            "value_generated": float(total_value),
            "value_generated_mean": float(mean_value),
            "value_generated_median": float(median_value),
        }
        groups_data.append(group_data)

    while groups_data[-1]["count"] == 0:
        groups_data.pop()

    return groups_data


def generate_user_probas(
    df: pd.DataFrame,
    user_col: str = "User Address",
    prediction_col: str = "prediction",
) -> dict[str, float]:
    return {row[user_col]: float(row[prediction_col]) for _, row in df.iterrows()}


def generate_prod_data(
    df: pd.DataFrame,
    groups: list[tuple[str, float, float]],
    output_path: Path,
    user_col: str = "User Address",
    value_col: str = "Transactions Count",
    prediction_col: str = "prediction",
) -> None:
    user_probas = generate_user_probas(df, user_col, prediction_col)
    user_groups = generate_user_groups(
        groups=groups,
        data=df,
        prediction_col=prediction_col,
        value_col=value_col,
    )

    final_data = {"user_probas": user_probas, "user_groups": user_groups}
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # save final_data to json in the data folder as prod_data.json
    with output_path.open("w") as f:
        json.dump(final_data, f)
