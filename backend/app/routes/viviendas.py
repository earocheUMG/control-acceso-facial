from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from pydantic import BaseModel

from backend.database.housing_repository import (
    create_house,
    get_house_by_code,
    get_houses,
    get_house_by_id
)


router = APIRouter(
    prefix="/api/viviendas",
    tags=["Viviendas"]
)


# =============================================
# ESQUEMA PARA CREAR VIVIENDA
# =============================================

class CreateHouseRequest(BaseModel):
    codigo: str
    direccion: str | None = None


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
# CREAR VIVIENDA
# =============================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_new_house(
    payload: CreateHouseRequest
):

    code = (
        payload.codigo
        .strip()
        .upper()
    )

    address = (
        payload.direccion.strip()
        if payload.direccion
        else None
    )


    if not code:

        raise HTTPException(
            status_code=400,
            detail=(
                "El código de la vivienda "
                "es obligatorio."
            )
        )


    if address == "":
        address = None


    existing_house = (
        get_house_by_code(
            code
        )
    )


    if existing_house:

        raise HTTPException(
            status_code=409,
            detail=(
                "Ya existe una vivienda "
                f"con el código {code}."
            )
        )


    try:

        house = (
            create_house(
                code=code,
                address=address
            )
        )


        return {
            "mensaje": (
                "Vivienda creada "
                "correctamente."
            ),
            "vivienda": house
        }


    except Exception as error:

        print(
            "ERROR CREANDO VIVIENDA:"
        )

        print(error)


        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible crear "
                "la vivienda."
            )
        )


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
