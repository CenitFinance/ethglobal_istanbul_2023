import itertools
from typing import List

import matplotlib.pyplot as plt
import torch
from matplotlib.axes import Axes
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    r2_score,
)


def evaluate_models_bc(
    models: List[torch.nn.Module], test_X: torch.Tensor, test_y: torch.Tensor
) -> None:
    plt.figure(figsize=(6, 6))

    # Plotting Precision-Recall curves for all models
    for i, model in enumerate(models):
        model.eval()  # Set the model to evaluation mode
        with torch.no_grad():
            outputs = torch.sigmoid(model(test_X).squeeze())

        precision, recall, thresholds = precision_recall_curve(test_y, outputs)
        plt.plot(recall, precision, marker=".", label=f"Model {i+1}")

    plt.title("Precision-Recall Curve")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.grid()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.legend()
    plt.show()

    # Confusion matrices
    num_models = len(models)
    fig, axs = plt.subplots(1, num_models, figsize=(6 * num_models, 6))
    if num_models == 1:
        axs = [axs]  # Ensure axs is iterable for a single model

    for i, model in enumerate(models):
        with torch.no_grad():
            outputs = torch.sigmoid(model(test_X).squeeze())
        predictions = (outputs > 0.5).int()
        conf_matrix = confusion_matrix(test_y, predictions)

        ax: Axes = axs[i]
        cax = ax.matshow(conf_matrix, cmap=plt.cm.Blues)
        fig.colorbar(cax, ax=ax)
        ax.set_title(f"Model {i+1}")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("True")

        # Annotate each cell with the numeric value
        for j, k in itertools.product(
            range(conf_matrix.shape[0]), range(conf_matrix.shape[1])
        ):
            ax.text(
                k,
                j,
                f"{conf_matrix[j, k]}",
                ha="center",
                va="center",
                color="white" if conf_matrix[j, k] > conf_matrix.max() / 2 else "black",
                size=40,
            )

    plt.tight_layout()
    plt.show()

    # Print classification reports
    for i, model in enumerate(models):
        with torch.no_grad():
            outputs = torch.sigmoid(model(test_X).squeeze())
        predictions = (outputs > 0.5).int()
        conf_matrix = confusion_matrix(test_y, predictions)
        classification_report_model = classification_report(test_y, predictions)
        print(f"Classification Report for Model {i+1}:")
        print(classification_report_model)


def evaluate_models_regression(
    models: List[torch.nn.Module], test_X: torch.Tensor, test_y: torch.Tensor
) -> None:
    num_models = len(models)
    fig, axs = plt.subplots(1, num_models, figsize=(6 * num_models, 6))

    # Adjust for a single model
    if num_models == 1:
        axs = [axs]

    for i, model in enumerate(models):
        model.eval()  # Set the model to evaluation mode
        with torch.no_grad():
            predictions = model(test_X).squeeze()

        # Calculate metrics
        mse = mean_squared_error(test_y, predictions)
        mae = mean_absolute_error(test_y, predictions)
        r2 = r2_score(test_y, predictions)

        # Plotting Actual vs Predicted values
        ax: Axes = axs[i]
        ax.scatter(test_y, predictions, alpha=0.3)
        ax.plot([test_y.min(), test_y.max()], [test_y.min(), test_y.max()], "k--", lw=2)
        ax.set_title(f"Model {i+1} - MSE: {mse:.2f}, MAE: {mae:.2f}, R²: {r2:.2f}")
        ax.set_xlabel("Actual")
        ax.set_ylabel("Predicted")

        # Print metrics
        print(f"Model {i+1} - MSE: {mse:.2f}, MAE: {mae:.2f}, R²: {r2:.2f}")

    plt.tight_layout()
    plt.show()
