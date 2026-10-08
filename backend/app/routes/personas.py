from fastapi import (
    APIRouter,
    HTTPException,
    status
)

from backend.app.schemas.personas import (
    PersonCreate
)

from backend.database.person_repository import (
    create_person,
    get_people,
    get_person_by_id
)


router = APIRouter(
    prefix="/api/personas",
    tags=["Personas"]
)


# =============================================
# LISTAR PERSONAS
# =============================================

@router.get("")
def list_people():

    people = get_people()

    return {
        "total": len(people),
        "personas": people
    }


# =============================================
# CREAR PERSONA
# =============================================

@router.post(
    "",
    status_code=status.HTTP_201_CREATED
)
def create_new_person(
    data: PersonCreate
):

    if (
        data.tipo
        in (
            "RESIDENTE",
            "TRABAJADOR"
        )
        and data.vivienda_id is None
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Los residentes y trabajadores "
                "deben estar asociados "
                "a una vivienda."
            )
        )

    try:

        person = create_person(
            nombre_completo=data.nombre_completo,
            tipo=data.tipo,
            email=data.email,
            telefono=data.telefono,
            vivienda_id=data.vivienda_id,
            es_responsable_notificacion=(
                data.es_responsable_notificacion
            )
        )

        return {
            "message": (
                "Persona creada correctamente."
            ),
            "persona": person,
            "biometria": "PENDIENTE"
        }

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =============================================
# CONSULTAR PERSONA
# =============================================

@router.get("/{person_id}")
def get_person(
    person_id: int
):

    person = get_person_by_id(
        person_id
    )

    if not person:

        raise HTTPException(
            status_code=404,
            detail=(
                "Persona no encontrada."
            )
        )

    return person