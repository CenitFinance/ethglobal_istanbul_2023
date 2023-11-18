import argparse
import json
from pathlib import Path


def is_nan(x):
    return x != x


args = argparse.ArgumentParser(description="ML Pipeline Arguments")
args.add_argument(
    "--data-file",
    type=str,
    required=True,
    help="Path to the data file",
)

data_file = args.parse_args().data_file
data_file = Path(data_file)
assert data_file.is_file(), f"Data file {data_file} does not exist"

# load
with open(data_file, "r") as fp:
    data = json.load(fp)

new_data = {
    "user_probas": {k: v for k, v in data["user_probas"].items() if not is_nan(v)},
    "user_groups": data["user_groups"],
}

with open(data_file, "w") as fp:
    json.dump(new_data, fp)
