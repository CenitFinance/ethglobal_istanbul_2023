# Imports
import argparse
import asyncio
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from matplotlib.axes import Axes

from ml_pipeline.evaluation import evaluate_models_bc, evaluate_models_regression
from ml_pipeline.model import ModelWrapper
from ml_pipeline.postprocessing import generate_prod_data
from ml_pipeline.preprocessing import preprocess_data, transform_data
from ml_pipeline.shap_plots import (
    calculate_shap_values,
    display_beeswarm,
    display_waterfall,
)
from ml_pipeline.training import train_cross_validation
from ml_pipeline.zkml import generate_compiled_model


def get_arguments() -> tuple:
    parser = argparse.ArgumentParser(description="ML Pipeline Arguments")
    parser.add_argument(
        "--data-file",
        type=str,
        required=True,
        help="Path to the data file",
    )
    parser.add_argument(
        "--outputs-folder",
        type=str,
        required=True,
        help="Path to the outputs folder",
    )
    parser.add_argument(
        "--is-classification",
        action="store_true",
        help="Flag indicating if the task is classification",
    )
    parser.add_argument(
        "--learning-rate",
        type=float,
        default=0.00001,
        help="Learning rate for the model",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=30,
        help="Number of epochs for training",
    )
    parser.add_argument(
        "--model-selected",
        type=int,
        default=3,
        help="Index of the selected model",
    )
    args = parser.parse_args()
    return (
        Path(args.data_file),
        args.outputs_folder,
        args.is_classification,
        args.learning_rate,
        args.epochs,
        args.model_selected,
    )


(
    data_file,
    outputs_folder,
    is_classification,
    learning_rate,
    epochs,
    model_selected,
) = get_arguments()

assert data_file.is_file(), f"Data file {data_file} does not exist"

learning_rate = float(learning_rate)
epochs = int(epochs)
model_selected = int(model_selected)
outputs_folder = Path(outputs_folder)
zkml_folder = outputs_folder / "zkml/"

zkml_folder.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(data_file)
df["old_target"] = df["target"]
df["target"] = df["target_reg"] < -0.99

feature_renames = {
    "Active Days": "Days with activity",
    "Active Days - past 3 windows": "Days with activity in 3 windows",
    "Active Days - past 6 windows": "Days with activity in 6 windows",
    "Active Weeks": "Weeks with activity",
    "Active Weeks - past 3 windows": "Weeks with activity in 3 windows",
    "Active Weeks - past 6 windows": "Weeks with activity in 6 windows",
    "Active Months": "Months with activity",
    "Active Months - past 3 windows": "Months with activity in 3 windows",
    "Active Months - past 6 windows": "Months with activity in 6 windows",
    "Amount of total transactions ($)": "Transacted value",
    "Amount of total transactions ($) - past 3 windows": "Transacted value in 3 windows",
    "Amount of total transactions ($) - past 6 windows": "Transacted value in 6 windows",
    "Days since first activity": "Days since first activity",
    "Days since last transaction": "Days since last activity",
    "Interacted TX Contracts": "Interacted contracts",
    "Interacted TX Contracts - past 3 windows": "Interacted contracts in 3 windows",
    "Interacted TX Contracts - past 6 windows": "Interacted contracts in 6 windows",
    "Transactions Count": "Transactions",
    "Transactions Count - past 3 windows": "Transactions in 3 windows",
    "Transactions Count - past 6 windows": "Transactions in 6 windows",
    # "Trend_Objetive_next_month": "Transactions trend",
    "Trend Transactions - past 3 windows": "Transactions trend in 3 windows",
    "Trend Transactions - past 6 windows": "Transactions trend in 6 windows",
    "Transaction Points Dollars": "Transaction value tiers",
}


label_name_bc = "target"
label_name_ref = "target_reg"
holdout_month = "2023-09-01"

df = df.rename(columns=feature_renames)

df_to_ml = df[
    ~df["month_start"].isin(["2023-09-01", "2023-10-01", "2023-11-01"])
].fillna(0)
df_to_prod = df[df["month_start"].isin([holdout_month])]

feature_selection = [f for f in feature_renames.values()]

print(df_to_ml["target"].value_counts())

(
    train_X,
    train_y,
    test_X,
    test_y,
    group_kfold_splits,
    (scaler, mean, std),
    train_index_new_order,
    test_index_new_order,
) = preprocess_data(
    data=df_to_ml,
    label_col=label_name_bc if is_classification else label_name_ref,
    grouping_col="User Address",
    n_splits=5,
    test_size=0.1,
    feature_cols=feature_selection,
    do_feature_scaling=True,
    seed=1534,
)


class Model(nn.Module):
    def __init__(self):
        super(Model, self).__init__()
        self.fc1 = nn.Linear(len(feature_renames), 40)  # First hidden layer
        self.fc2 = nn.Linear(40, 40)  # Second hidden layer
        self.fc3 = nn.Linear(40, 40)  # Third hidden layer
        self.output = nn.Linear(40, 1)  # Output layer

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.output(x)
        return x


(
    models,
    train_loss_lists,
    train_accuracy_lists,
    valid_loss_lists,
    valid_accuracy_lists,
) = train_cross_validation(
    model_class=Model,
    train_X=train_X,
    train_y=train_y,
    group_kfold_splits=group_kfold_splits,
    batch_size=64,
    epochs=epochs,  # 30,
    learning_rate=learning_rate,  # 0.00001,
    shuffle_batches=False,
    is_classification=is_classification,
)

# Plot the loss evolution for all folds

# First the training loss
fig = plt.figure(figsize=(10, 8))
axes: list[Axes] = fig.subplots(2, 1, sharex=True)
ax = axes[0]
for i, train_loss_list in enumerate(train_loss_lists):
    ax.plot(train_loss_list, label=f"Fold {i}")
ax.set_title("Training loss")
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
ax.legend()
ax.set_ylim(bottom=0)
ax.set_xlim(left=0)
ax.grid()

# Then the validation loss
ax = axes[1]
for i, valid_loss_list in enumerate(valid_loss_lists):
    ax.plot(valid_loss_list, label=f"Fold {i}")
ax.set_title("Validation loss")
ax.set_xlabel("Epoch")
ax.set_ylabel("Loss")
ax.legend()
ax.set_ylim(bottom=0)
ax.set_xlim(left=0)
ax.grid()

plt.savefig(outputs_folder / "losses.png")
plt.close()

if is_classification:
    # Now the accuracy evolution for all folds
    # Plot the loss evolution for all folds

    # First the training loss
    fig = plt.figure(figsize=(10, 8))
    axes: list[Axes] = fig.subplots(2, 1, sharex=True)
    ax = axes[0]
    for i, train_accuracy_list in enumerate(train_accuracy_lists):
        ax.plot(train_accuracy_list, label=f"Fold {i}")
    ax.set_title("Training accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.set_ylim(top=1)
    ax.set_xlim(left=0)
    ax.grid()

    # Then the validation loss
    ax = axes[1]
    for i, valid_accuracy_list in enumerate(valid_accuracy_lists):
        ax.plot(valid_accuracy_list, label=f"Fold {i}")
    ax.set_title("Validation accuracy")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.set_ylim(top=1)
    ax.set_xlim(left=0)
    ax.grid()

    plt.savefig(outputs_folder / "accuracies.png")
    plt.close()


if is_classification:
    evaluate_models_bc(models, test_X, test_y, save_to=outputs_folder)
else:
    evaluate_models_regression(models, test_X, test_y, save_to=outputs_folder)


# select one of the models once you are happy with the results
final_model: nn.Module = models[model_selected]

# save the model
model_scripted = torch.jit.script(final_model)  # Export to TorchScript
model_scripted.save(outputs_folder / "model_scripted.pt")


all_X = torch.cat([train_X, test_X])[:1000]
shap_values = calculate_shap_values(ModelWrapper(final_model), all_X)

display_beeswarm(
    ModelWrapper(final_model),
    all_X,
    feature_selection,
    shap_values,
    save_to=outputs_folder / "beeswarm.png",
)

random_indexes_from_all = np.random.choice(len(all_X), size=5, replace=False).tolist()

for i, idx in enumerate(random_indexes_from_all):
    display_waterfall(
        shap_values,
        ModelWrapper(final_model),
        all_X,
        idx,
        feature_selection,
        max_display=10,
        save_to=outputs_folder / f"waterfall_{i}.png",
    )

X_to_prod = transform_data(df_to_prod, feature_selection, scaler)
prod_predictions = ModelWrapper(final_model)(X_to_prod).detach().numpy().flatten()

df_final = df_to_prod.copy()
df_final["prediction"] = prod_predictions

generate_prod_data(
    df=df_final,
    groups=[
        ("1 - 5", 1, 5),
        ("5 - 20", 5, 20),
        ("20 - 50", 20, 50),
        ("50 - 100", 50, 100),
        ("100+", 100, 10000000000),
    ],
    output_path=outputs_folder / "prod_data.json",
    user_col="User Address",
    prediction_col="prediction",
    value_col="Transactions",
)


asyncio.run(
    generate_compiled_model(
        base_path=zkml_folder,
        model=final_model,
        test_X=test_X,
    )
)
