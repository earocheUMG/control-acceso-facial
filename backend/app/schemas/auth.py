from pydantic import (
    BaseModel,
    Field
)


# =============================================
# LOGIN
# =============================================

class LoginRequest(BaseModel):

    usuario: str = Field(
        min_length=3,
        max_length=50
    )

    password: str = Field(
        min_length=8,
        max_length=200
    )


# =============================================
# RESPUESTA TOKEN
# =============================================

class TokenResponse(BaseModel):

    access_token: str

    token_type: str = "bearer"

    usuario: str

    rol: str