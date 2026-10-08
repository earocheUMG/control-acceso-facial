from typing import Literal

from pydantic import (
    BaseModel,
    EmailStr,
    Field
)


class PersonCreate(BaseModel):

    nombre_completo: str = Field(
        min_length=3,
        max_length=150
    )

    tipo: Literal[
        "RESIDENTE",
        "TRABAJADOR",
        "SEGURIDAD"
    ]

    email: EmailStr | None = None

    telefono: str | None = Field(
        default=None,
        max_length=30
    )

    vivienda_id: int | None = None

    es_responsable_notificacion: bool = False