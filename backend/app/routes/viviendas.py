from fastapi import APIRouter

from backend.database.housing_repository import (
    get_houses
)


router = APIRouter(
    prefix="/api/viviendas",
    tags=["Viviendas"]
)


@router.get("")
def list_houses():

    houses = get_houses()

    return {
        "total": len(houses),
        "viviendas": houses
    }