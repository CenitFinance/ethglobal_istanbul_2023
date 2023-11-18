import torch
from torch import nn
from torch.nn import functional as F


class ModelWrapper(nn.Module):
    def __init__(self, model):
        super(ModelWrapper, self).__init__()
        self.model = model

    def forward(self, x):
        logits = self.model(x)
        probabilities = torch.sigmoid(logits)
        return probabilities


class DynamicFCModel(nn.Module):
    def __init__(
        self,
        input_size: int,
        hidden_size: int,
        output_size: int = 1,
        n_layers: int = 3,
        is_classification: bool = True,
    ):
        super(DynamicFCModel, self).__init__()
        self.sizes = (input_size, hidden_size, n_layers, output_size)
        self.is_binary_classification = is_classification and output_size == 1
        self.is_multiclass_classification = is_classification and output_size > 1
        self.is_regression = not is_classification

        self.fc_start = nn.Linear(input_size, hidden_size)
        self.fc_hiddens = nn.Sequential(
            *[nn.Linear(hidden_size, hidden_size) for _ in range(n_layers - 2)]
        )
        self.fc_end = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.fc_start(x))
        for fc in self.fc_hiddens:
            x = F.relu(fc(x))
        x = self.fc_end(x)
        if self.is_binary_classification:
            x = torch.sigmoid(x)
        elif self.is_multiclass_classification:
            x = F.softmax(x, dim=1)
        return x
