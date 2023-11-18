import numpy as np
import torch
from sklearn.metrics import accuracy_score
from torch import nn
from torch.utils.data import DataLoader, TensorDataset


def train_cross_validation(
    model_class: nn.Module,
    train_X: torch.Tensor,
    train_y: torch.Tensor,
    group_kfold_splits: list[tuple[np.ndarray, np.ndarray]],
    batch_size: int = 64,
    epochs: int = 30,
    learning_rate: float = 0.03,
    shuffle_batches=True,
):
    models = []
    train_loss_lists = []
    train_accuracy_lists = []
    valid_loss_lists = []
    valid_accuracy_lists = []

    # train in cross validation folds
    for fold_idx, (train_idx, validation_idx) in enumerate(group_kfold_splits):
        fold_model = model_class()
        optimizer = torch.optim.Adam(fold_model.parameters(), lr=learning_rate)
        criterion = nn.BCEWithLogitsLoss()

        print(f"\nFold {fold_idx}")
        # prepare data
        train_x_fold = train_X[train_idx]
        train_y_fold = train_y[train_idx]
        validation_x_fold = train_X[validation_idx]
        validation_y_fold = train_y[validation_idx]

        train_dataset = TensorDataset(train_x_fold, train_y_fold)
        validation_dataset = TensorDataset(validation_x_fold, validation_y_fold)

        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=shuffle_batches
        )

        train_loss_list = []
        train_accuracy_list = []

        valid_loss_list = []
        valid_accuracy_list = []

        for epoch in range(epochs):
            fold_model.train()
            for batch_idx, (data, target) in enumerate(train_loader):
                optimizer.zero_grad()
                output = fold_model(data)
                target = target.to(torch.float32)
                loss = criterion(output, target)
                loss.backward()
                optimizer.step()

            fold_model.eval()
            with torch.no_grad():
                # calculate training logs
                train_pred = fold_model(train_x_fold)
                train_y_fold = train_y_fold.to(torch.float32)
                train_loss = criterion(train_pred, train_y_fold).item()
                train_loss_list.append(train_loss)

                train_pred = torch.sigmoid(train_pred) > 0.5
                train_accuracy = accuracy_score(train_y_fold, train_pred.cpu().numpy())
                train_accuracy_list.append(train_accuracy)

                # calculate validation logs
                valid_pred = fold_model(validation_x_fold)
                validation_y_fold = validation_y_fold.to(torch.float32)

                valid_loss = criterion(valid_pred, validation_y_fold).item()
                valid_loss_list.append(valid_loss)

                valid_pred = torch.sigmoid(valid_pred) > 0.5
                valid_accuracy = accuracy_score(
                    validation_y_fold, valid_pred.cpu().numpy()
                )
                valid_accuracy_list.append(valid_accuracy)

            if epoch % 10 == 0:
                print(
                    f"Epoch: {epoch} Train loss: {train_loss:.4f} Validation loss: {valid_loss:.4f}"
                )

        models.append(fold_model)
        train_loss_lists.append(train_loss_list)
        train_accuracy_lists.append(train_accuracy_list)
        valid_loss_lists.append(valid_loss_list)
        valid_accuracy_lists.append(valid_accuracy_list)

        print(f"Fold {fold_idx} done, metrics:")
        print(f"  Train loss: {train_loss:.4f}")
        print(f"  Validation loss: {valid_loss:.4f}")
        print(f"  Train accuracy: {train_accuracy:.4f}")
        print(f"  Validation accuracy: {valid_accuracy:.4f}")

    return (
        models,
        train_loss_lists,
        train_accuracy_lists,
        valid_loss_lists,
        valid_accuracy_lists,
    )
