from fastapi import (
    APIRouter,
    HTTPException
)

from backend.database.person_repository import (
    get_people,
    get_person_by_id
)


router = APIRouter(
    prefix="/api/personas",
    tags=["Personas"]
)


@router.get("")
def list_people():

    people = get_people()

    return {
        "total": len(people),
        "personas": people
    }


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
            detail="Persona no encontrada."
        )

    return person