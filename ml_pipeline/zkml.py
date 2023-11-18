import asyncio
import json
from pathlib import Path

import ezkl
import torch


async def calibrate(
    cal_data_path: Path,
    model_path: Path,
    settings_path: Path,
) -> bool:
    return await ezkl.calibrate_settings(
        cal_data_path, model_path, settings_path, "resources"
    )


async def generate_compiled_model(
    base_path: Path,
    model: torch.nn.Module,
    test_X: torch.Tensor,
):
    model_path = base_path / "network.onnx"
    compiled_model_path = base_path / "network.ezkl"
    settings_path = base_path / "settings.json"
    data_path = base_path / "input_data.json"
    cal_data_path = base_path / "cal_data.json"
    proof_data_path = base_path / "proof_data.json"

    sample_input = test_X[0].reshape(1, -1)

    data_array = (sample_input.detach().numpy()).reshape([-1]).tolist()

    data = dict(input_data=[data_array])

    # Serialize data into file:
    with data_path.open("w") as f:
        json.dump(data, f)

    # use the test set to calibrate the circuit
    cal_data = dict(input_data=[float(v) for v in test_X[:20].flatten().tolist()])

    # Serialize calibration data into file:
    json.dump(cal_data, open(cal_data_path, "w"))

    model.eval()

    torch.onnx.export(
        model,  # model being run
        sample_input,  # model input (or a tuple for multiple inputs)
        model_path,  # where to save the model (can be a file or file-like object)
        export_params=True,  # store the trained parameter weights inside the model file
        opset_version=10,  # the ONNX version to export the model to
        do_constant_folding=True,  # whether to execute constant folding for optimization
        input_names=["input"],  # the model's input names
        output_names=["output"],  # the model's output names
        dynamic_axes={
            "input": {0: "batch_size"},  # variable length axes
            "output": {0: "batch_size"},
        },
    )

    # concat test_X and train_X
    all_X = test_X

    proof_input = all_X
    proof_data_array = proof_input.detach().numpy().tolist()
    proof_data = dict(input_data=proof_data_array)

    with proof_data_path.open("w") as f:
        json.dump(proof_data, f)

    py_run_args = ezkl.PyRunArgs()
    py_run_args.input_visibility = "public"
    py_run_args.output_visibility = "public"
    py_run_args.param_visibility = "fixed"  # "fixed" for params means that the committed to params are used for all proofs

    res = ezkl.gen_settings(model_path, settings_path, py_run_args=py_run_args)
    assert res == True, "Failed to generate settings"

    res = await ezkl.calibrate_settings(
        cal_data_path, model_path, settings_path, "resources"
    )
    assert res == True, "Failed to calibrate settings"

    res = ezkl.compile_circuit(model_path, compiled_model_path, settings_path)
    assert res == True
    print(f"Compiled model saved to {compiled_model_path}")


def generate_witness(base_path: Path):
    ...


def generate_proof(base_path: Path):
    ...


def verify_proof(base_path: Path):
    ...


def deplot_verification_contract(base_path: Path):
    ...
