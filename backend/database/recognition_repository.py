from backend.database.connection import (
    get_connection
)


# =============================================
# CANDIDATOS ACTIVOS PARA RECONOCIMIENTO
# =============================================

def get_recognition_candidates():

    query = """
        SELECT
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,

            b.modelo,
            b.template_path,
            b.cantidad_muestras

        FROM personas p

        JOIN biometria b
            ON b.persona_id = p.id

        WHERE p.activo = TRUE
          AND b.activo = TRUE
          AND p.codigo_biometrico IS NOT NULL

        ORDER BY p.id;
    """


    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query
            )

            return cursor.fetchall()