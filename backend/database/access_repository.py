from backend.database.connection import get_connection


def get_active_people():

    query = """
        SELECT
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            b.template_path,
            COALESCE(
                STRING_AGG(
                    DISTINCT v.codigo,
                    ', '
                ),
                ''
            ) AS viviendas
        FROM personas p

        JOIN biometria b
            ON b.persona_id = p.id
            AND b.activo = TRUE

        LEFT JOIN persona_vivienda pv
            ON pv.persona_id = p.id
            AND pv.activo = TRUE

        LEFT JOIN viviendas v
            ON v.id = pv.vivienda_id
            AND v.activa = TRUE

        WHERE p.activo = TRUE

        GROUP BY
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            b.template_path

        ORDER BY p.codigo_biometrico;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()


def get_access_point(
    nombre="Entrada principal"
):

    query = """
        SELECT
            id,
            nombre,
            ubicacion
        FROM puntos_acceso
        WHERE nombre = %s
          AND activo = TRUE
        LIMIT 1;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (nombre,)
            )

            return cursor.fetchone()


def register_access(
    persona_id,
    punto_acceso_id,
    resultado,
    similitud,
    puerta_abierta,
    motivo=None
):

    query = """
        INSERT INTO accesos (
            persona_id,
            punto_acceso_id,
            resultado,
            similitud,
            puerta_abierta,
            motivo
        )
        VALUES (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING
            id,
            fecha_hora;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (
                    persona_id,
                    punto_acceso_id,
                    resultado,
                    similitud,
                    puerta_abierta,
                    motivo
                )
            )

            acceso = cursor.fetchone()

            connection.commit()

            return acceso