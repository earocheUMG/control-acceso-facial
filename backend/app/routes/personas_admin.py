from fastapi import (
    APIRouter,
    HTTPException
)

from backend.app.schemas.personas import (
    PersonStatusUpdate,
    PersonUpdate
)

from backend.database.person_admin_repository import (
    get_person_detail,
    set_person_status,
    update_person
)


router = APIRouter(
    prefix="/api/personas",
    tags=["Administración de personas"]
)


# =============================================
# DETALLE
# =============================================

@router.get(
    "/{person_id}/detalle"
)
def person_detail(
    person_id: int
):

    person = (
        get_person_detail(
            person_id
        )
    )


    if not person:

        raise HTTPException(
            status_code=404,
            detail="Persona no encontrada."
        )


    return person


# =============================================
# EDITAR
# =============================================

@router.put(
    "/{person_id}"
)
def edit_person(
    person_id: int,
    data: PersonUpdate
):

    if (
        data.tipo
        in (
            "RESIDENTE",
            "TRABAJADOR"
        )
        and
        data.vivienda_id
        is None
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

        person = (
            update_person(
                person_id=
                    person_id,

                nombre_completo=
                    data.nombre_completo,

                tipo=
                    data.tipo,

                email=
                    data.email,

                telefono=
                    data.telefono,

                vivienda_id=(
                    None
                    if data.tipo
                    == "SEGURIDAD"
                    else
                    data.vivienda_id
                ),

                es_responsable_notificacion=(
                    data
                    .es_responsable_notificacion
                )
            )
        )


        return {
            "message":
                "Persona actualizada correctamente.",

            "detalle":
                person
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =============================================
# ACTIVAR / INACTIVAR
# =============================================

@router.patch(
    "/{person_id}/estado"
)
def change_person_status(
    person_id: int,
    data: PersonStatusUpdate
):

    try:

        person = (
            set_person_status(
                person_id=
                    person_id,

                active=
                    data.activo
            )
        )


        return {
            "message": (
                "Persona activada correctamente."
                if data.activo
                else
                "Persona inactivada correctamente."
            ),

            "persona":
                person
        }


    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )