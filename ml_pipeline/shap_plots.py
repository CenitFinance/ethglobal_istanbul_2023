from pathlib import Path
from typing import List, Union

import matplotlib.pyplot as plt
import numpy as np
import shap
import torch
from torch import nn


def calculate_shap_values(model: nn.Module, X: torch.Tensor):
    # Ensure the model is in evaluation mode
    model.eval()

    # Wrap the model with a GradientExplainer
    explainer = shap.GradientExplainer(model, X)

    # Get SHAP values for the specific input sample
    shap_values = explainer.shap_values(X)

    return shap_values


def display_beeswarm(
    model: nn.Module,
    data_X: torch.Tensor,
    feature_names: Union[List[str], None] = None,
    shap_values: Union[np.ndarray, None] = None,
    save_to: Union[str, None] = None,
):
    if shap_values is None:
        shap_values = calculate_shap_values(model, data_X)

    if not feature_names:
        feature_names = [f"Feature_{i}" for i in range(data_X.shape[1])]

    # Plotting the beeswarm plot
    plt.clf()
    shap.summary_plot(
        shap_values,
        features=data_X,
        feature_names=feature_names,
        show=False,
    )
    if save_to is not None:
        plt.savefig(save_to, bbox_inches="tight")
    else:
        plt.show()
    plt.close()


def display_waterfall(
    shap_values: np.ndarray,
    model: nn.Module,
    X: torch.Tensor,
    idx: int,
    feature_names: Union[List[str], None] = None,
    max_display: int = 10,
    save_to: Union[str, None] = None,
):
    # Calculate the expected value (mean model output on train data)
    with torch.no_grad():
        expected_value = model(X).mean().item()

    if not feature_names:
        feature_names = [f"Feature_{i}" for i in range(input_sample.shape[1])]

    input_sample = X[idx].unsqueeze(0)

    # Prepare the SHAP explanation object
    shap_explanation = shap.Explanation(
        values=shap_values[0].squeeze(),  # Adjust based on your output shape
        base_values=expected_value,
        data=input_sample.numpy().squeeze(),  # Adjust as needed
        feature_names=feature_names,
    )

    # Create the waterfall plot
    plt.clf()
    shap.waterfall_plot(
        shap_explanation,
        max_display=max_display,
        show=False,
    )
    if save_to is not None:
        plt.savefig(save_to, bbox_inches="tight")
    else:
        plt.show()

    plt.close()
