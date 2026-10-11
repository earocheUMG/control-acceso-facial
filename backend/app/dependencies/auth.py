from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)

from backend.database.system_user_repository import (
    get_system_user_by_id
)

from backend.services.auth_service import (
    decode_access_token
)


# =============================================
# BEARER TOKEN
# =============================================

security = HTTPBearer(
    auto_error=False
)


# =============================================
# USUARIO ACTUAL
# =============================================

def get_current_user(
    credentials:
        HTTPAuthorizationCredentials
        | None
        = Depends(security)
):

    if credentials is None:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Autenticación requerida."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )


    token = credentials.credentials


    payload = (
        decode_access_token(
            token
        )
    )


    if not payload:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Token inválido o expirado."
            ),
            headers={
                "WWW-Authenticate":
                    "Bearer"
            }
        )


    try:

        user_id = int(
            payload["sub"]
        )

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido."
        )


    user = (
        get_system_user_by_id(
            user_id
        )
    )


    if not user:

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Usuario no encontrado."
            )
        )


    if not user["activo"]:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,
            detail=(
                "Usuario inactivo."
            )
        )


    return user


# =============================================
# SOLO ADMIN
# =============================================

def require_admin(
    current_user=
        Depends(
            get_current_user
        )
):

    if (
        current_user["rol"]
        != "ADMIN"
    ):

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,
            detail=(
                "Se requiere rol ADMIN."
            )
        )


    return current_user