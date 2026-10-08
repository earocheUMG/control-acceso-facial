from backend.database.connection import get_connection


def get_dashboard_summary():
    """
    Devuelve indicadores principales
    para el dashboard.
    """

    query = """
        SELECT

            (
                SELECT COUNT(*)
                FROM personas
                WHERE activo = TRUE
            ) AS personas_activas,

            (
                SELECT COUNT(*)
                FROM viviendas
                WHERE activa = TRUE
            ) AS viviendas_activas,

            (
                SELECT COUNT(*)
                FROM accesos
                WHERE fecha_hora::date = CURRENT_DATE
            ) AS accesos_hoy,

            (
                SELECT COUNT(*)
                FROM accesos
                WHERE fecha_hora::date = CURRENT_DATE
                  AND resultado = 'AUTORIZADO'
            ) AS autorizados_hoy,

            (
                SELECT COUNT(*)
                FROM accesos
                WHERE fecha_hora::date = CURRENT_DATE
                  AND resultado = 'RECHAZADO'
            ) AS rechazados_hoy,

            (
                SELECT COUNT(*)
                FROM notificaciones
                WHERE estado = 'ERROR'
            ) AS notificaciones_error;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchone()


def get_recent_accesses(
    limit=5
):
    """
    Devuelve los ultimos accesos
    para mostrarlos en el dashboard.
    """

    query = """
        SELECT
            a.id,
            a.fecha_hora,
            a.resultado,
            a.similitud,

            p.nombre_completo,
            p.tipo AS tipo_persona,

            pa.nombre AS punto_acceso

        FROM accesos a

        LEFT JOIN personas p
            ON p.id = a.persona_id

        JOIN puntos_acceso pa
            ON pa.id = a.punto_acceso_id

        ORDER BY
            a.fecha_hora DESC

        LIMIT %s;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (limit,)
            )

            return cursor.fetchall()