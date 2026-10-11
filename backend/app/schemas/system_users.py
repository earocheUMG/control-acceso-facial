from typing import Literal

from pydantic import (
    BaseModel,
    Field
)


SystemRole = Literal[
    "ADMIN",
    "SEGURIDAD"
]


# =============================================
# CREAR USUARIO
# =============================================

class SystemUserCreate(BaseModel):

    usuario: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=8,
        max_length=200
    )

    rol: SystemRole


# =============================================
# CAMBIAR ESTADO
# =============================================

class SystemUserStatusUpdate(BaseModel):

    activo: bool