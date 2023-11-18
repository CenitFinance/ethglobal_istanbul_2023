from fastapi import APIRouter
from pydantic import BaseModel
import base64

router = APIRouter(
    prefix="/graphs",
    tags=["graphs"],
)


class Graph(BaseModel):
    image: str


@router.get("/shap/{protocol}")
def get_full_shap(protocol: str) -> Graph:
    path = f"results/{protocol}/beeswarm.png"
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return Graph(
        image=encoded_string.decode("utf-8"),
    )


@router.get("/shap/{protocol}/{address}")
def get_address_shap(protocol: str, address: str) -> Graph:
    idx = hash(address) % 5
    path = f"results/{protocol}/waterfall_{idx}.png"
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return Graph(
        image=encoded_string.decode("utf-8"),
    )
