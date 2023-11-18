import json
from fastapi import APIRouter
from pydantic import BaseModel
import numpy as np
import random
import string

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


@router.get("/stats/")
def get_stats() -> Stats:
    with open("mocks/user_probas.json") as results_file:
        results = json.load(results_file)
    return Stats(
        **results
        # user_groups=[],
        # user_probas={address: probs for address, probs in zip(addresses, probs)},
    )
