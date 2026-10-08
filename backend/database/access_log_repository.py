from backend.database.connection import get_connection


# =============================================
# CONSULTAR BITACORA DE ACCESOS
# =============================================

def get_access_logs(
    limit=50,
    result=None
):
    """
    Obtiene la bitacora de accesos.

    result puede ser:
    AUTORIZADO
    RECHAZADO
    REVISION
    None
    """

    base_query = """
        SELECT
            a.id,
            a.fecha_hora,
            a.resultado,
            a.similitud,
            a.puerta_abierta,
            a.metodo,
            a.motivo,
            a.captura_path,

            p.id AS persona_id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo AS tipo_persona,

            pa.id AS punto_acceso_id,
            pa.nombre AS punto_acceso,
            pa.ubicacion AS ubicacion_punto,

            COALESCE(
                (
                    SELECT STRING_AGG(
                        DISTINCT v.codigo,
                        ', '
                    )
                    FROM persona_vivienda pv

                    JOIN viviendas v
                        ON v.id = pv.vivienda_id

                    WHERE pv.persona_id = p.id
                      AND pv.activo = TRUE
                ),
                ''
            ) AS viviendas,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
            ) AS total_notificaciones,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
                  AND n.estado = 'ENVIADA'
            ) AS notificaciones_enviadas,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
                  AND n.estado = 'ERROR'
            ) AS notificaciones_error

        FROM accesos a

        LEFT JOIN personas p
            ON p.id = a.persona_id

        JOIN puntos_acceso pa
            ON pa.id = a.punto_acceso_id
    """

    parameters = []

    # =========================================
    # FILTRO OPCIONAL
    # =========================================

    if result:

        base_query += """
            WHERE a.resultado = %s
        """

        parameters.append(
            result
        )

    # =========================================
    # ORDEN Y LIMITE
    # =========================================

    base_query += """
        ORDER BY
            a.fecha_hora DESC

        LIMIT %s;
    """

    parameters.append(
        limit
    )

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                base_query,
                tuple(parameters)
            )

            return cursor.fetchall()


# =============================================
# CONSULTAR UN ACCESO POR ID
# =============================================

def get_access_log_by_id(
    access_id
):

    query = """
        SELECT
            a.id,
            a.fecha_hora,
            a.resultado,
            a.similitud,
            a.puerta_abierta,
            a.metodo,
            a.motivo,
            a.captura_path,

            p.id AS persona_id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo AS tipo_persona,

            pa.id AS punto_acceso_id,
            pa.nombre AS punto_acceso,
            pa.ubicacion AS ubicacion_punto,

            COALESCE(
                (
                    SELECT STRING_AGG(
                        DISTINCT v.codigo,
                        ', '
                    )
                    FROM persona_vivienda pv

                    JOIN viviendas v
                        ON v.id = pv.vivienda_id

                    WHERE pv.persona_id = p.id
                      AND pv.activo = TRUE
                ),
                ''
            ) AS viviendas,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
            ) AS total_notificaciones,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
                  AND n.estado = 'ENVIADA'
            ) AS notificaciones_enviadas,

            (
                SELECT COUNT(*)
                FROM notificaciones n
                WHERE n.acceso_id = a.id
                  AND n.estado = 'ERROR'
            ) AS notificaciones_error

        FROM accesos a

        LEFT JOIN personas p
            ON p.id = a.persona_id

        JOIN puntos_acceso pa
            ON pa.id = a.punto_acceso_id

        WHERE a.id = %s;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (access_id,)
            )

            return cursor.fetchone()