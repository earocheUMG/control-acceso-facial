from typing import Literal

from fastapi import (
    APIRouter,
    HTTPException,
    Query
)

from backend.database.access_log_repository import (
    get_access_logs,
    get_access_log_by_id
)


router = APIRouter(
    prefix="/api/accesos",
    tags=["Accesos"]
)


@router.get("")
def list_access_logs(
    limit: int = Query(
        default=50,
        ge=1,
        le=200
    ),
    resultado: Literal[
        "AUTORIZADO",
        "RECHAZADO",
        "REVISION"
    ] | None = None
):

    accesses = get_access_logs(
        limit=limit,
        result=resultado
    )

    return {
        "total": len(accesses),
        "filtro_resultado": resultado,
        "accesos": accesses
    }


@router.get("/{access_id}")
def get_access_log(
    access_id: int
):

    access = get_access_log_by_id(
        access_id
    )

    if not access:

        raise HTTPException(
            status_code=404,
            detail="Registro de acceso no encontrado."
        )

    return access