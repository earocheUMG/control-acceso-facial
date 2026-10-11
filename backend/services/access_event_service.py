import os

from datetime import datetime
from pathlib import Path

import cv2

from dotenv import load_dotenv


from backend.database.access_repository import (
    get_active_people,
    get_access_point,
    register_access
)

from backend.database.notification_repository import (
    get_notification_recipients,
    create_notification,
    mark_notification_sent,
    mark_notification_error
)

from backend.services.email_service import (
    send_authorized_access_email,
    send_security_alert_email
)

from backend.services.recognition_service import (
    recognize_face_with_artifacts
)


# =============================================
# CONFIGURACION
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)


load_dotenv(
    ROOT_DIR / ".env"
)


EVIDENCE_DIR = (
    ROOT_DIR
    / "data"
    / "access_evidence"
)


SECURITY_EMAIL = (
    os.getenv(
        "SECURITY_EMAIL"
    )
)


DOOR_OPEN_TIME = 3


# =============================================
# BUSCAR PERSONA
# =============================================

def get_person_by_id(
    person_id: int
):

    people = (
        get_active_people()
    )


    for person in people:

        if (
            person["id"]
            == person_id
        ):

            return person


    return None


# =============================================
# GUARDAR EVIDENCIA
# =============================================

def save_unknown_evidence(
    aligned_face
):

    if aligned_face is None:

        return None


    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S_%f"
        )
    )


    filename = (
        f"unknown_{timestamp}.jpg"
    )


    full_path = (
        EVIDENCE_DIR
        / filename
    )


    saved = (
        cv2.imwrite(
            str(
                full_path
            ),
            aligned_face
        )
    )


    if not saved:

        return None


    return str(
        full_path.relative_to(
            ROOT_DIR
        )
    )


# =============================================
# FORMATEAR FECHA
# =============================================

def format_access_date(
    access_date
):

    try:

        return (
            access_date.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )


    except Exception:

        return str(
            access_date
        )


# =============================================
# NOTIFICACION AUTORIZADA
# =============================================

def notify_authorized_access(
    access,
    person,
    access_point
):

    recipients = (
        get_notification_recipients(
            person["id"]
        )
    )


    sent = 0
    errors = 0


    if not recipients:

        return {
            "enviadas": 0,
            "errores": 0
        }


    access_date = (
        format_access_date(
            access["fecha_hora"]
        )
    )


    processed_emails = set()


    for recipient in recipients:

        email = (
            recipient["email"]
        )


        if not email:

            continue


        if (
            email
            in processed_emails
        ):

            continue


        processed_emails.add(
            email
        )


        notification = None


        try:

            notification = (
                create_notification(
                    access_id=
                        access["id"],

                    recipient_email=
                        email,

                    notification_type=
                        "INGRESO"
                )
            )


            send_authorized_access_email(
                recipient=
                    email,

                visitor_name=
                    person[
                        "nombre_completo"
                    ],

                visitor_type=
                    person["tipo"],

                house=
                    recipient[
                        "vivienda"
                    ],

                access_point=
                    access_point[
                        "nombre"
                    ],

                access_date=
                    access_date
            )


            mark_notification_sent(
                notification["id"]
            )


            sent += 1


        except Exception as error:

            errors += 1


            if notification:

                try:

                    mark_notification_error(
                        notification["id"],
                        str(error)
                    )


                except Exception:

                    pass


    return {
        "enviadas":
            sent,

        "errores":
            errors
    }


# =============================================
# ALERTA SEGURIDAD
# =============================================

def notify_security_alert(
    access,
    access_point,
    similarity,
    evidence_path
):

    if not SECURITY_EMAIL:

        return {
            "enviadas": 0,
            "errores": 1,
            "detalle":
                "SECURITY_EMAIL "
                "no configurado."
        }


    notification = None


    access_date = (
        format_access_date(
            access["fecha_hora"]
        )
    )


    try:

        notification = (
            create_notification(
                access_id=
                    access["id"],

                recipient_email=
                    SECURITY_EMAIL,

                notification_type=
                    "ALERTA_SEGURIDAD"
            )
        )


        send_security_alert_email(
            recipient=
                SECURITY_EMAIL,

            access_point=
                access_point[
                    "nombre"
                ],

            similarity=
                similarity,

            access_date=
                access_date,

            evidence_path=
                evidence_path
        )


        mark_notification_sent(
            notification["id"]
        )


        return {
            "enviadas": 1,
            "errores": 0
        }


    except Exception as error:

        if notification:

            try:

                mark_notification_error(
                    notification["id"],
                    str(error)
                )


            except Exception:

                pass


        return {
            "enviadas": 0,
            "errores": 1,
            "detalle":
                str(error)
        }


# =============================================
# PROCESAR EVENTO
# =============================================

def process_access_event(
    image_bytes
):

    recognition, aligned_face = (
        recognize_face_with_artifacts(
            image_bytes
        )
    )


    # =========================================
    # DEBE EXISTIR UN ROSTRO DECIDIBLE
    # =========================================

    if (
        recognition["estado"]
        not in {
            "RECONOCIDO",
            "DESCONOCIDO"
        }
    ):

        raise ValueError(
            "El frame final no contiene "
            "un rostro válido para registrar "
            "el evento."
        )


    # =========================================
    # PUNTO DE ACCESO
    # =========================================

    access_point = (
        get_access_point(
            "Entrada principal"
        )
    )


    if not access_point:

        raise RuntimeError(
            "No existe el punto de acceso "
            "'Entrada principal'."
        )


    # =========================================
    # AUTORIZADO
    # =========================================

    if (
        recognition["estado"]
        == "RECONOCIDO"
        and
        recognition["persona"]
    ):

        person = (
            get_person_by_id(
                recognition[
                    "persona"
                ]["id"]
            )
        )


        if not person:

            raise RuntimeError(
                "La persona reconocida "
                "ya no se encuentra activa."
            )


        access = (
            register_access(
                persona_id=
                    person["id"],

                punto_acceso_id=
                    access_point["id"],

                resultado=
                    "AUTORIZADO",

                similitud=
                    recognition[
                        "similitud"
                    ],

                puerta_abierta=
                    True,

                motivo=
                    None,

                captura_path=
                    None
            )
        )


        notification_result = (
            notify_authorized_access(
                access=
                    access,

                person=
                    person,

                access_point=
                    access_point
            )
        )


        return {
            "evento_registrado":
                True,

            "acceso_id":
                access["id"],

            "resultado":
                "AUTORIZADO",

            "puerta_abierta":
                True,

            "puerta_abierta_segundos":
                DOOR_OPEN_TIME,

            "evidencia":
                None,

            "reconocimiento":
                recognition,

            "notificaciones":
                notification_result
        }


    # =========================================
    # DESCONOCIDO
    # =========================================

    evidence_path = (
        save_unknown_evidence(
            aligned_face
        )
    )


    access = (
        register_access(
            persona_id=
                None,

            punto_acceso_id=
                access_point["id"],

            resultado=
                "RECHAZADO",

            similitud=
                recognition[
                    "similitud"
                ],

            puerta_abierta=
                False,

            motivo=
                "Rostro no registrado",

            captura_path=
                evidence_path
        )
    )


    notification_result = (
        notify_security_alert(
            access=
                access,

            access_point=
                access_point,

            similarity=
                recognition[
                    "similitud"
                ],

            evidence_path=
                evidence_path
        )
    )


    return {
        "evento_registrado":
            True,

        "acceso_id":
            access["id"],

        "resultado":
            "RECHAZADO",

        "puerta_abierta":
            False,

        "puerta_abierta_segundos":
            0,

        "evidencia":
            evidence_path,

        "reconocimiento":
            recognition,

        "notificaciones":
            notification_result
    }