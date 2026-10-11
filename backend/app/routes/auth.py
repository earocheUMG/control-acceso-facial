from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from backend.app.dependencies.auth import (
    get_current_user
)

from backend.app.schemas.auth import (
    LoginRequest,
    TokenResponse
)

from backend.database.system_user_repository import (
    get_system_user_by_username
)

from backend.services.auth_service import (
    create_access_token,
    verify_password
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)


# =============================================
# LOGIN
# =============================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    data: LoginRequest
):

    user = (
        get_system_user_by_username(
            data.usuario
        )
    )


    # Mismo error para usuario inexistente
    # o contraseña incorrecta.
    if (
        not user
        or
        not verify_password(
            data.password,
            user["password_hash"]
        )
    ):

        raise HTTPException(
            status_code=
                status.HTTP_401_UNAUTHORIZED,
            detail=(
                "Usuario o contraseña "
                "incorrectos."
            )
        )


    if not user["activo"]:

        raise HTTPException(
            status_code=
                status.HTTP_403_FORBIDDEN,
            detail=(
                "El usuario está inactivo."
            )
        )


    token = (
        create_access_token(
            user_id=
                user["id"],

            username=
                user["usuario"],

            role=
                user["rol"]
        )
    )


    return {
        "access_token":
            token,

        "token_type":
            "bearer",

        "usuario":
            user["usuario"],

        "rol":
            user["rol"]
    }


# =============================================
# USUARIO ACTUAL
# =============================================

@router.get(
    "/me"
)
def get_me(
    current_user=
        Depends(
            get_current_user
        )
):

    return {
        "id":
            current_user["id"],

        "usuario":
            current_user["usuario"],

        "rol":
            current_user["rol"],

        "activo":
            current_user["activo"]
    }