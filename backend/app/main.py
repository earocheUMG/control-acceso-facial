from fastapi import FastAPI

from backend.app.routes.health import (
    router as health_router
)

from backend.app.routes.personas import (
    router as personas_router
)

from backend.app.routes.accesos import (
    router as accesos_router
)

from backend.app.routes.dashboard import (
    router as dashboard_router
)


app = FastAPI(
    title="Sistema de Control de Acceso Facial",
    description=(
        "API para la administracion del sistema "
        "de control de acceso mediante "
        "reconocimiento facial."
    ),
    version="1.0.0"
)


# =============================================
# ROUTERS
# =============================================

app.include_router(
    health_router
)

app.include_router(
    personas_router
)

app.include_router(
    accesos_router
)

app.include_router(
    dashboard_router
)


# =============================================
# ROOT
# =============================================

@app.get("/")
def root():

    return {
        "system": (
            "Sistema de Control "
            "de Acceso Facial"
        ),
        "status": "running",
        "api_version": "1.0.0"
    }