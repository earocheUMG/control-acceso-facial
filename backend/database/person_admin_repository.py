from backend.database.connection import get_connection


# =============================================
# DETALLE DE PERSONA
# =============================================

def get_person_detail(
    person_id
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # =================================
            # PERSONA
            # =================================

            cursor.execute(
                """
                SELECT
                    id,
                    codigo_biometrico,
                    nombre_completo,
                    tipo,
                    email,
                    telefono,
                    activo,
                    fecha_inicio,
                    fecha_fin,
                    creado_en

                FROM personas

                WHERE id = %s;
                """,
                (person_id,)
            )


            person = cursor.fetchone()


            if not person:

                return None


            # =================================
            # VIVIENDA ACTIVA
            # =================================

            cursor.execute(
                """
                SELECT
                    v.id,
                    v.codigo,
                    v.direccion,

                    pv.relacion,

                    pv.es_responsable_notificacion

                FROM persona_vivienda pv

                JOIN viviendas v
                    ON v.id = pv.vivienda_id

                WHERE pv.persona_id = %s
                  AND pv.activo = TRUE

                ORDER BY pv.id DESC

                LIMIT 1;
                """,
                (person_id,)
            )


            house = cursor.fetchone()


            # =================================
            # BIOMETRIA
            # =================================

            cursor.execute(
                """
                SELECT
                    modelo,
                    template_path,
                    cantidad_muestras,
                    activo,
                    creado_en

                FROM biometria

                WHERE persona_id = %s

                LIMIT 1;
                """,
                (person_id,)
            )


            biometrics = cursor.fetchone()


            return {
                "persona":
                    person,

                "vivienda":
                    house,

                "biometria":
                    biometrics
            }


# =============================================
# ACTUALIZAR PERSONA
# =============================================

def update_person(
    person_id,
    nombre_completo,
    tipo,
    email=None,
    telefono=None,
    vivienda_id=None,
    es_responsable_notificacion=False
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            # =================================
            # VERIFICAR PERSONA
            # =================================

            cursor.execute(
                """
                SELECT id
                FROM personas
                WHERE id = %s;
                """,
                (person_id,)
            )


            if not cursor.fetchone():

                raise ValueError(
                    "Persona no encontrada."
                )


            # =================================
            # VALIDAR VIVIENDA
            # =================================

            if tipo in (
                "RESIDENTE",
                "TRABAJADOR"
            ):

                if vivienda_id is None:

                    raise ValueError(
                        "Debe seleccionar "
                        "una vivienda."
                    )


                cursor.execute(
                    """
                    SELECT id
                    FROM viviendas
                    WHERE id = %s
                      AND activa = TRUE;
                    """,
                    (vivienda_id,)
                )


                if not cursor.fetchone():

                    raise ValueError(
                        "La vivienda indicada "
                        "no existe o está inactiva."
                    )


            # =================================
            # ACTUALIZAR DATOS PERSONALES
            # =================================

            cursor.execute(
                """
                UPDATE personas

                SET
                    nombre_completo = %s,
                    tipo = %s,
                    email = %s,
                    telefono = %s

                WHERE id = %s;
                """,
                (
                    nombre_completo,
                    tipo,
                    email,
                    telefono,
                    person_id
                )
            )


            # =================================
            # DESACTIVAR RELACIONES ANTERIORES
            # =================================

            cursor.execute(
                """
                UPDATE persona_vivienda

                SET
                    activo = FALSE,
                    es_responsable_notificacion = FALSE

                WHERE persona_id = %s;
                """,
                (person_id,)
            )


            # =================================
            # CREAR / REACTIVAR RELACION
            # =================================

            if tipo in (
                "RESIDENTE",
                "TRABAJADOR"
            ):

                relacion = tipo


                responsable = (
                    es_responsable_notificacion
                    if tipo == "RESIDENTE"
                    else False
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
                    )

                    ON CONFLICT (
                        persona_id,
                        vivienda_id,
                        relacion
                    )

                    DO UPDATE SET
                        es_responsable_notificacion =
                            EXCLUDED
                            .es_responsable_notificacion,

                        activo = TRUE;
                    """,
                    (
                        person_id,
                        vivienda_id,
                        relacion,
                        responsable
                    )
                )


            connection.commit()


    return get_person_detail(
        person_id
    )


# =============================================
# ACTIVAR / INACTIVAR
# =============================================

def set_person_status(
    person_id,
    active
):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute(
                """
                UPDATE personas

                SET activo = %s

                WHERE id = %s

                RETURNING
                    id,
                    nombre_completo,
                    activo;
                """,
                (
                    active,
                    person_id
                )
            )


            person = cursor.fetchone()


            if not person:

                raise ValueError(
                    "Persona no encontrada."
                )


            connection.commit()


            return person