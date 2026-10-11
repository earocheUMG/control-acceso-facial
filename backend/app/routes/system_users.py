from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from backend.app.dependencies.auth import (
    require_admin
)

from backend.app.schemas.system_users import (
    SystemUserCreate,
    SystemUserStatusUpdate
)

from backend.database.system_user_repository import (
    create_system_user,
    get_system_users,
    set_system_user_status
)

from backend.services.auth_service import (
    hash_password
)


router = APIRouter(
    prefix="/api/usuarios",
    tags=["Usuarios del sistema"]
)


# =============================================
# LISTAR USUARIOS
# =============================================

@router.get("")
def list_system_users(
    current_user=
        Depends(
            require_admin
        )
):

    users = (
        get_system_users()
    )

    return {
        "total":
            len(users),

        "usuarios":
            users
    }


# =============================================
# CREAR USUARIO
# =============================================

@router.post(
    "",
    status_code=
        status.HTTP_201_CREATED
)
def create_new_system_user(
    data: SystemUserCreate,
    current_user=
        Depends(
            require_admin
        )
):

    username = (
        data.usuario
        .strip()
    )


    if len(username) < 3:

        raise HTTPException(
            status_code=400,
            detail=(
                "El usuario debe tener "
                "al menos 3 caracteres."
            )
        )


    try:

        encrypted_password = (
            hash_password(
                data.password
            )
        )


        user = (
            create_system_user(
                username=
                    username,

                password_hash=
                    encrypted_password,

                role=
                    data.rol
            )
        )


        return {
            "message":
                "Usuario creado correctamente.",

            "usuario":
                user
        }


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# =============================================
# ACTIVAR / INACTIVAR
# =============================================

@router.patch(
    "/{user_id}/estado"
)
def change_system_user_status(
    user_id: int,
    data: SystemUserStatusUpdate,
    current_user=
        Depends(
            require_admin
        )
):

    # Evitar que un administrador
    # se bloquee a sí mismo.
    if (
        current_user["id"]
        == user_id
        and
        data.activo is False
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "No puede inactivar "
                "su propia cuenta."
            )
        )


    try:

        user = (
            set_system_user_status(
                user_id=
                    user_id,

                active=
                    data.activo
            )
        )


        return {
            "message": (
                "Usuario activado correctamente."
                if data.activo
                else
                "Usuario inactivado correctamente."
            ),

            "usuario":
                user
        }


    except ValueError as error:

        raise HTTPException(
            status_code=404,
            detail=str(error)
        )