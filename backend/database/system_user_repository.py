from backend.database.connection import (
    get_connection
)


# =============================================
# LISTAR USUARIOS
# =============================================

def get_system_users():

    query = """
        SELECT
            id,
            usuario,
            rol,
            activo

        FROM usuarios_sistema

        ORDER BY
            usuario;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()


# =============================================
# BUSCAR POR USUARIO
# =============================================

def get_system_user_by_username(
    username
):

    query = """
        SELECT
            id,
            usuario,
            password_hash,
            rol,
            activo

        FROM usuarios_sistema

        WHERE LOWER(usuario)
            = LOWER(%s)

        LIMIT 1;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (username,)
            )

            return cursor.fetchone()


# =============================================
# BUSCAR POR ID
# =============================================

def get_system_user_by_id(
    user_id
):

    query = """
        SELECT
            id,
            usuario,
            rol,
            activo

        FROM usuarios_sistema

        WHERE id = %s

        LIMIT 1;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (user_id,)
            )

            return cursor.fetchone()


# =============================================
# CREAR USUARIO
# =============================================

def create_system_user(
    username,
    password_hash,
    role
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # =================================
            # VERIFICAR DUPLICADO
            # =================================

            cursor.execute(
                """
                SELECT id

                FROM usuarios_sistema

                WHERE LOWER(usuario)
                    = LOWER(%s)

                LIMIT 1;
                """,
                (username,)
            )


            if cursor.fetchone():

                raise ValueError(
                    "El usuario ya existe."
                )


            # =================================
            # CREAR
            # =================================

            cursor.execute(
                """
                INSERT INTO usuarios_sistema (
                    usuario,
                    password_hash,
                    rol,
                    activo
                )

                VALUES (
                    %s,
                    %s,
                    %s,
                    TRUE
                )

                RETURNING
                    id,
                    usuario,
                    rol,
                    activo;
                """,
                (
                    username,
                    password_hash,
                    role
                )
            )


            user = cursor.fetchone()

            connection.commit()

            return user


# =============================================
# ACTIVAR / INACTIVAR USUARIO
# =============================================

def set_system_user_status(
    user_id,
    active
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE usuarios_sistema

                SET activo = %s

                WHERE id = %s

                RETURNING
                    id,
                    usuario,
                    rol,
                    activo;
                """,
                (
                    active,
                    user_id
                )
            )


            user = cursor.fetchone()


            if not user:

                raise ValueError(
                    "Usuario no encontrado."
                )


            connection.commit()

            return user