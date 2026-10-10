from typing import Literal

from fastapi import (
    APIRouter,
    Query
)

from backend.database.notification_log_repository import (
    get_notifications
)


router = APIRouter(
    prefix="/api/notificaciones",
    tags=["Notificaciones"]
)


@router.get("")
def list_notifications(

    limit: int = Query(
        default=50,
        ge=1,
        le=200
    ),

    tipo: Literal[
        "INGRESO",
        "ALERTA_SEGURIDAD"
    ] | None = None,

    estado: Literal[
        "PENDIENTE",
        "ENVIADA",
        "ERROR"
    ] | None = None

):

    notifications = (
        get_notifications(
            limit=limit,
            notification_type=tipo,
            notification_status=estado
        )
    )


    return {
        "total": len(
            notifications
        ),
        "filtro_tipo": tipo,
        "filtro_estado": estado,
        "notificaciones":
            notifications
    }