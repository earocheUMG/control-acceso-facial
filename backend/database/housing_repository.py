from backend.database.connection import get_connection


# =============================================
# LISTAR VIVIENDAS
# =============================================

def get_houses():

    query = """
        SELECT
            v.id,
            v.codigo,
            v.direccion,
            v.activa,

            COUNT(
                DISTINCT CASE
                    WHEN pv.activo = TRUE
                     AND p.activo = TRUE
                    THEN p.id
                END
            ) AS total_personas,

            COUNT(
                DISTINCT CASE
                    WHEN pv.activo = TRUE
                     AND p.activo = TRUE
                     AND pv.relacion = 'RESIDENTE'
                    THEN p.id
                END
            ) AS residentes,

            COUNT(
                DISTINCT CASE
                    WHEN pv.activo = TRUE
                     AND p.activo = TRUE
                     AND pv.relacion = 'TRABAJADOR'
                    THEN p.id
                END
            ) AS trabajadores,

            COUNT(
                DISTINCT CASE
                    WHEN pv.activo = TRUE
                     AND p.activo = TRUE
                     AND pv.es_responsable_notificacion = TRUE
                    THEN p.id
                END
            ) AS responsables_notificacion

        FROM viviendas v

        LEFT JOIN persona_vivienda pv
            ON pv.vivienda_id = v.id

        LEFT JOIN personas p
            ON p.id = pv.persona_id

        WHERE v.activa = TRUE

        GROUP BY
            v.id,
            v.codigo,
            v.direccion,
            v.activa

        ORDER BY
            v.codigo;
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(query)

            return cursor.fetchall()


# =============================================
# BUSCAR VIVIENDA POR CODIGO
# =============================================

def get_house_by_code(
    code
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    codigo,
                    direccion,
                    activa,
                    creado_en
                FROM viviendas
                WHERE UPPER(codigo) = UPPER(%s)
                LIMIT 1;
                """,
                (code,)
            )

            return cursor.fetchone()


# =============================================
# CREAR VIVIENDA
# =============================================

def create_house(
    code,
    address=None
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO viviendas (
                    codigo,
                    direccion,
                    activa
                )
                VALUES (
                    %s,
                    %s,
                    TRUE
                )
                RETURNING
                    id,
                    codigo,
                    direccion,
                    activa,
                    creado_en;
                """,
                (
                    code,
                    address
                )
            )

            return cursor.fetchone()


# =============================================
# DETALLE DE VIVIENDA
# =============================================

def get_house_by_id(
    house_id
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    codigo,
                    direccion,
                    activa,
                    creado_en
                FROM viviendas
                WHERE id = %s;
                """,
                (house_id,)
            )

            house = cursor.fetchone()

            if not house:

                return None

            cursor.execute(
                """
                SELECT
                    p.id,
                    p.codigo_biometrico,
                    p.nombre_completo,
                    p.tipo,
                    p.email,
                    p.telefono,
                    p.activo,

                    pv.relacion,

                    pv.es_responsable_notificacion,

                    CASE
                        WHEN b.id IS NOT NULL
                         AND b.activo = TRUE
                        THEN TRUE
                        ELSE FALSE
                    END AS biometria_configurada

                FROM persona_vivienda pv

                JOIN personas p
                    ON p.id = pv.persona_id

                LEFT JOIN biometria b
                    ON b.persona_id = p.id

                WHERE pv.vivienda_id = %s
                  AND pv.activo = TRUE

                ORDER BY
                    p.tipo,
                    p.nombre_completo;
                """,
                (house_id,)
            )

            people = cursor.fetchall()

            return {
                "vivienda": house,
                "personas": people
            }
