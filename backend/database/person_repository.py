from backend.database.connection import get_connection


def get_people():
    """
    Devuelve todas las personas registradas
    con sus viviendas y estado biometrico.
    """

    query = """
        SELECT
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            p.email,
            p.telefono,
            p.activo,

            COALESCE(
                ARRAY_REMOVE(
                    ARRAY_AGG(
                        DISTINCT v.codigo
                    ),
                    NULL
                ),
                ARRAY[]::VARCHAR[]
            ) AS viviendas,

            CASE
                WHEN b.id IS NOT NULL
                THEN TRUE
                ELSE FALSE
            END AS biometria_configurada

        FROM personas p

        LEFT JOIN persona_vivienda pv
            ON pv.persona_id = p.id
            AND pv.activo = TRUE

        LEFT JOIN viviendas v
            ON v.id = pv.vivienda_id
            AND v.activa = TRUE

        LEFT JOIN biometria b
            ON b.persona_id = p.id
            AND b.activo = TRUE

        GROUP BY
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            p.email,
            p.telefono,
            p.activo,
            b.id

        ORDER BY
            p.codigo_biometrico;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()


def get_person_by_id(
    person_id
):
    """
    Obtiene una persona especifica.
    """

    query = """
        SELECT
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            p.email,
            p.telefono,
            p.activo,
            p.fecha_inicio,
            p.fecha_fin,
            p.creado_en,

            COALESCE(
                ARRAY_REMOVE(
                    ARRAY_AGG(
                        DISTINCT v.codigo
                    ),
                    NULL
                ),
                ARRAY[]::VARCHAR[]
            ) AS viviendas,

            CASE
                WHEN b.id IS NOT NULL
                THEN TRUE
                ELSE FALSE
            END AS biometria_configurada

        FROM personas p

        LEFT JOIN persona_vivienda pv
            ON pv.persona_id = p.id
            AND pv.activo = TRUE

        LEFT JOIN viviendas v
            ON v.id = pv.vivienda_id
            AND v.activa = TRUE

        LEFT JOIN biometria b
            ON b.persona_id = p.id
            AND b.activo = TRUE

        WHERE p.id = %s

        GROUP BY
            p.id,
            p.codigo_biometrico,
            p.nombre_completo,
            p.tipo,
            p.email,
            p.telefono,
            p.activo,
            p.fecha_inicio,
            p.fecha_fin,
            p.creado_en,
            b.id;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (person_id,)
            )

            return cursor.fetchone()