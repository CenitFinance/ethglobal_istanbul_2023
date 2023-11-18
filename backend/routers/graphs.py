from fastapi import APIRouter
from pydantic import BaseModel
import base64

router = APIRouter(
    prefix="/graphs",
    tags=["graphs"],
)


class Graph(BaseModel):
    image: str


@router.get("/shap/")
def get_full_shap() -> Graph:
    full_shap_file = "mocks/full_shap.png"
    with open(full_shap_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return Graph(
        image=encoded_string.decode("utf-8"),
    )


@router.get("/shap/{address}")
def get_address_shap(address: str) -> Graph:
    return Graph(
        image=address,
    )
