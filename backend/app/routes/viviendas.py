from fastapi import (
    APIRouter,
    HTTPException
)

from backend.database.housing_repository import (
    get_houses,
    get_house_by_id
)


router = APIRouter(
    prefix="/api/viviendas",
    tags=["Viviendas"]
)


# =============================================
# LISTAR VIVIENDAS
# =============================================

@router.get("")
def list_houses():

    houses = get_houses()

    return {
        "total": len(houses),
        "viviendas": houses
    }


# =============================================
# DETALLE DE VIVIENDA
# =============================================

@router.get("/{house_id}")
def get_house(
    house_id: int
):

    house = get_house_by_id(
        house_id
    )

    if not house:

        raise HTTPException(
            status_code=404,
            detail="Vivienda no encontrada."
        )

    return house