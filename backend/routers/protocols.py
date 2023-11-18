from fastapi import APIRouter
import os

router = APIRouter(prefix="/protocols", tags=["protocols"])


@router.get("/")
def get_available_protocols() -> list[str]:
    return list(os.walk("results"))[0][1]
