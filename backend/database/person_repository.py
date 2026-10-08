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


def create_person(
    nombre_completo,
    tipo,
    email=None,
    telefono=None,
    vivienda_id=None,
    es_responsable_notificacion=False
):
    """
    Crea una persona.

    La biometria queda pendiente
    hasta realizar el enrolamiento facial.
    """

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # =====================================
            # VALIDAR VIVIENDA
            # =====================================

            if vivienda_id is not None:

                cursor.execute(
                    """
                    SELECT
                        id,
                        codigo
                    FROM viviendas
                    WHERE id = %s
                      AND activa = TRUE;
                    """,
                    (vivienda_id,)
                )

                vivienda = (
                    cursor.fetchone()
                )

                if not vivienda:

                    raise ValueError(
                        "La vivienda indicada "
                        "no existe o está inactiva."
                    )

            # =====================================
            # CREAR PERSONA
            # =====================================

            cursor.execute(
                """
                INSERT INTO personas (
                    codigo_biometrico,
                    nombre_completo,
                    tipo,
                    email,
                    telefono,
                    activo
                )
                VALUES (
                    NULL,
                    %s,
                    %s,
                    %s,
                    %s,
                    TRUE
                )
                RETURNING
                    id,
                    codigo_biometrico,
                    nombre_completo,
                    tipo,
                    email,
                    telefono,
                    activo,
                    creado_en;
                """,
                (
                    nombre_completo,
                    tipo,
                    email,
                    telefono
                )
            )

            person = (
                cursor.fetchone()
            )

            # =====================================
            # VINCULAR CON VIVIENDA
            # =====================================

            if vivienda_id is not None:

                relacion = (
                    "TRABAJADOR"
                    if tipo == "TRABAJADOR"
                    else "RESIDENTE"
                )

                cursor.execute(
                    """
                    INSERT INTO persona_vivienda (
                        persona_id,
                        vivienda_id,
                        relacion,
                        es_responsable_notificacion,
                        activo
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        TRUE
                    );
                    """,
                    (
                        person["id"],
                        vivienda_id,
                        relacion,
                        es_responsable_notificacion
                    )
                )

            connection.commit()

            return person
        