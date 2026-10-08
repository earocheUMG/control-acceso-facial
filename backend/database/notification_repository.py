from backend.database.connection import get_connection


def get_notification_recipients(person_id):
    """
    Busca los responsables de notificación
    de las viviendas asociadas a la persona
    que acaba de ingresar.
    """

    query = """
        SELECT DISTINCT
            responsable.id,
            responsable.nombre_completo,
            responsable.email,
            v.codigo AS vivienda
        FROM persona_vivienda origen

        JOIN viviendas v
            ON v.id = origen.vivienda_id
            AND v.activa = TRUE

        JOIN persona_vivienda destino
            ON destino.vivienda_id = v.id
            AND destino.activo = TRUE
            AND destino.es_responsable_notificacion = TRUE

        JOIN personas responsable
            ON responsable.id = destino.persona_id
            AND responsable.activo = TRUE

        WHERE origen.persona_id = %s
          AND origen.activo = TRUE
          AND responsable.email IS NOT NULL
          AND responsable.email <> '';
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (person_id,)
            )

            return cursor.fetchall()


def create_notification(
    access_id,
    recipient_email,
    notification_type
):
    """
    Registra una nueva notificación
    con estado PENDIENTE.
    """

    query = """
        INSERT INTO notificaciones (
            acceso_id,
            destinatario_email,
            tipo,
            estado
        )
        VALUES (
            %s,
            %s,
            %s,
            'PENDIENTE'
        )
        RETURNING
            id,
            creado_en;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    access_id,
                    recipient_email,
                    notification_type
                )
            )

            notification = cursor.fetchone()

            connection.commit()

            return notification


def mark_notification_sent(notification_id):
    """
    Marca una notificación como ENVIADA.
    """

    query = """
        UPDATE notificaciones
        SET
            estado = 'ENVIADA',
            enviado_en = NOW(),
            error = NULL
        WHERE id = %s;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (notification_id,)
            )

            connection.commit()


def mark_notification_error(
    notification_id,
    error_message
):
    """
    Marca una notificación como ERROR
    y guarda el detalle del problema.
    """

    query = """
        UPDATE notificaciones
        SET
            estado = 'ERROR',
            error = %s
        WHERE id = %s;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    str(error_message),
                    notification_id
                )
            )

            connection.commit()