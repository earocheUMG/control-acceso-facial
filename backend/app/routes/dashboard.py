from fastapi import APIRouter

from backend.database.dashboard_repository import (
    get_dashboard_summary,
    get_recent_accesses
)


router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/resumen")
def dashboard_summary():

    summary = (
        get_dashboard_summary()
    )

    recent_accesses = (
        get_recent_accesses(
            limit=5
        )
    )

    return {
        "resumen": summary,
        "ultimos_accesos": recent_accesses
    }