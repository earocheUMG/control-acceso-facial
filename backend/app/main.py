from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

from backend.app.routes.viviendas import (
    router as viviendas_router
)

from backend.app.routes.notificaciones import (
    router as notificaciones_router
)

from backend.app.routes.enrolamiento import (
    router as enrolamiento_router
)

from backend.app.routes.personas_admin import (
    router as personas_admin_router
)

from backend.app.routes.auth import (
    router as auth_router
)

from backend.app.routes.system_users import (
    router as system_users_router
)

# =============================================
# APLICACION FASTAPI
# =============================================

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
# CORS
# =============================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

app.include_router(
    viviendas_router
)

app.include_router(
    notificaciones_router
)

app.include_router(
    enrolamiento_router
)

app.include_router(
    personas_admin_router
)

app.include_router(
    auth_router
)


app.include_router(
    system_users_router
)

# =============================================
# ENDPOINT RAIZ
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