from backend.database.connection import (
    get_connection
)


def get_houses():

    query = """
        SELECT
            id,
            codigo,
            direccion,
            activa
        FROM viviendas
        WHERE activa = TRUE
        ORDER BY codigo;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()