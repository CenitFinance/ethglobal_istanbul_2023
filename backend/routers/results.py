import json
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/results",
    tags=["results"],
)


class UserGroup(BaseModel):
    label: str
    lower: float
    higher: float
    count: int
    mean: float
    median: float
    pct25: float
    pct75: float
    pct10: float
    pct90: float
    value_generated: float
    value_generated_mean: float
    value_generated_median: float


class Stats(BaseModel):
    user_groups: list[UserGroup]
    user_probas: dict[str, float]


@router.get("/{protocol}")
def get_stats(protocol: str) -> Stats:
    path = f"results/{protocol}/prod_data.json"
    with open(path) as results_file:
        results = json.load(results_file)
    results["user_probas"] = {
        address: proba
        for address, proba in results["user_probas"].items()
        if proba == proba
    }
    return Stats(**results)
