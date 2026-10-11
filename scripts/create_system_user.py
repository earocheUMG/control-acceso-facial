import sys

from getpass import getpass
from pathlib import Path


# =============================================
# RUTA RAIZ
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


sys.path.insert(
    0,
    str(ROOT_DIR)
)


from backend.database.system_user_repository import (
    create_system_user
)

from backend.services.auth_service import (
    hash_password
)


# =============================================
# SELECCIONAR ROL
# =============================================

def select_role():

    print("")
    print("Seleccione el rol:")
    print("")
    print("1. ADMIN")
    print("2. SEGURIDAD")
    print("")


    option = input(
        "Opción: "
    ).strip()


    if option == "1":

        return "ADMIN"


    if option == "2":

        return "SEGURIDAD"


    return None


# =============================================
# MAIN
# =============================================

def main():

    print("")
    print(
        "======================================"
    )

    print(
        "    CREAR USUARIO DEL SISTEMA"
    )

    print(
        "======================================"
    )


    username = input(
        "Usuario: "
    ).strip()


    if len(username) < 3:

        print(
            "ERROR: El usuario debe tener "
            "al menos 3 caracteres."
        )

        return


    role = select_role()


    if role is None:

        print(
            "ERROR: Rol inválido."
        )

        return


    password = getpass(
        "Contraseña: "
    )


    password_confirmation = getpass(
        "Confirmar contraseña: "
    )


    if password != password_confirmation:

        print(
            "ERROR: Las contraseñas "
            "no coinciden."
        )

        return


    if len(password) < 8:

        print(
            "ERROR: La contraseña debe tener "
            "al menos 8 caracteres."
        )

        return


    try:

        encrypted_password = (
            hash_password(
                password
            )
        )


        user = (
            create_system_user(
                username=
                    username,

                password_hash=
                    encrypted_password,

                role=
                    role
            )
        )


        print("")
        print(
            "======================================"
        )

        print(
            " USUARIO CREADO CORRECTAMENTE"
        )

        print(
            "======================================"
        )

        print(
            f"ID: {user['id']}"
        )

        print(
            f"Usuario: {user['usuario']}"
        )

        print(
            f"Rol: {user['rol']}"
        )

        print(
            f"Activo: {user['activo']}"
        )


    except ValueError as error:

        print(
            f"ERROR: {error}"
        )


if __name__ == "__main__":
    main()