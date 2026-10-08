from backend.database.connection import get_connection


def get_pending_biometric_people():
    """
    Obtiene personas activas que todavía
    no tienen biometría configurada.
    """

    query = """
        SELECT
            p.id,
            p.nombre_completo,
            p.tipo,
            p.codigo_biometrico,

            COALESCE(
                STRING_AGG(
                    DISTINCT v.codigo,
                    ', '
                ),
                ''
            ) AS viviendas

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

        WHERE p.activo = TRUE
          AND (
                p.codigo_biometrico IS NULL
                OR b.id IS NULL
              )

        GROUP BY
            p.id,
            p.nombre_completo,
            p.tipo,
            p.codigo_biometrico

        ORDER BY p.id;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()


def get_next_biometric_code():
    """
    Genera el siguiente código numérico:
    001, 002, 003...
    """

    query = """
        SELECT
            LPAD(
                (
                    COALESCE(
                        MAX(
                            codigo_biometrico::INTEGER
                        ),
                        0
                    ) + 1
                )::TEXT,
                3,
                '0'
            ) AS codigo

        FROM personas

        WHERE codigo_biometrico
            ~ '^[0-9]+$';
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            result = cursor.fetchone()

            return result["codigo"]


def register_person_biometrics(
    person_id,
    biometric_code,
    template_path,
    sample_count
):
    """
    Asigna el código biométrico y registra
    la plantilla MobileFaceNet.
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # =====================================
            # ASIGNAR CODIGO
            # =====================================

            cursor.execute(
                """
                UPDATE personas
                SET codigo_biometrico = %s
                WHERE id = %s
                  AND activo = TRUE;
                """,
                (
                    biometric_code,
                    person_id
                )
            )

            if cursor.rowcount != 1:

                raise ValueError(
                    "No fue posible actualizar "
                    "la persona."
                )

            # =====================================
            # REGISTRAR BIOMETRIA
            # =====================================

            cursor.execute(
                """
                INSERT INTO biometria (
                    persona_id,
                    modelo,
                    template_path,
                    cantidad_muestras,
                    activo
                )
                VALUES (
                    %s,
                    'MobileFaceNet',
                    %s,
                    %s,
                    TRUE
                )

                ON CONFLICT (persona_id)

                DO UPDATE SET
                    modelo = EXCLUDED.modelo,
                    template_path =
                        EXCLUDED.template_path,
                    cantidad_muestras =
                        EXCLUDED.cantidad_muestras,
                    activo = TRUE;
                """,
                (
                    person_id,
                    template_path,
                    sample_count
                )
            )

            connection.commit()