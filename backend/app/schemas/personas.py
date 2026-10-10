from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


PersonType = Literal[
    "RESIDENTE",
    "TRABAJADOR",
    "SEGURIDAD"
]


# =============================================
# CREAR PERSONA
# =============================================

class PersonCreate(BaseModel):

    nombre_completo: str = Field(
        min_length=3,
        max_length=150
    )

    tipo: PersonType

    email: EmailStr | None = None

    telefono: str | None = Field(
        default=None,
        max_length=30
    )

    vivienda_id: int | None = None

    es_responsable_notificacion: bool = False


# =============================================
# EDITAR PERSONA
# =============================================

class PersonUpdate(BaseModel):

    nombre_completo: str = Field(
        min_length=3,
        max_length=150
    )

    tipo: PersonType

    email: EmailStr | None = None

    telefono: str | None = Field(
        default=None,
        max_length=30
    )

    vivienda_id: int | None = None

    es_responsable_notificacion: bool = False


# =============================================
# CAMBIAR ESTADO
# =============================================

class PersonStatusUpdate(BaseModel):

    activo: bool