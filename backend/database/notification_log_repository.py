from backend.database.connection import get_connection


def get_notifications(
    limit=50,
    notification_type=None,
    notification_status=None
):

    conditions = []
    parameters = []


    if notification_type:

        conditions.append(
            "n.tipo = %s"
        )

        parameters.append(
            notification_type
        )


    if notification_status:

        conditions.append(
            "n.estado = %s"
        )

        parameters.append(
            notification_status
        )


    where_clause = ""

    if conditions:

        where_clause = (
            "WHERE "
            + " AND ".join(
                conditions
            )
        )


    query = f"""
        SELECT
            n.id,
            n.acceso_id,
            n.destinatario_email,
            n.tipo,
            n.estado,
            n.creado_en,
            n.enviado_en,
            n.error,

            a.fecha_hora
                AS acceso_fecha,

            a.resultado
                AS acceso_resultado,

            a.similitud,

            p.id
                AS persona_id,

            p.codigo_biometrico,

            p.nombre_completo,

            pa.nombre
                AS punto_acceso

        FROM notificaciones n

        JOIN accesos a
            ON a.id = n.acceso_id

        LEFT JOIN personas p
            ON p.id = a.persona_id

        JOIN puntos_acceso pa
            ON pa.id = a.punto_acceso_id

        {where_clause}

        ORDER BY
            n.creado_en DESC

        LIMIT %s;
    """


    parameters.append(
        limit
    )


    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                tuple(parameters)
            )

            return cursor.fetchall()