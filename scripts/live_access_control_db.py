import sys
import os
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

import cv2
import numpy as np
import onnxruntime as ort
from dotenv import load_dotenv


# =============================================
# RUTA RAIZ DEL PROYECTO
# =============================================

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")


from backend.database.access_repository import (
    get_active_people,
    get_access_point,
    register_access,
)

from backend.database.notification_repository import (
    get_notification_recipients,
    create_notification,
    mark_notification_sent,
    mark_notification_error,
)

from backend.services.email_service import (
    send_authorized_access_email,
    send_security_alert_email,
)


# =============================================
# CONFIGURACION
# =============================================

CAMERA_INDEX = 0

YUNET_MODEL = (
    ROOT_DIR
    / "models"
    / "yunet"
    / "face_detection_yunet_2023mar.onnx"
)

MOBILEFACENET_MODEL = (
    ROOT_DIR
    / "models"
    / "mobilefacenet"
    / "w600k_mbf.onnx"
)

EVIDENCE_DIR = (
    ROOT_DIR
    / "data"
    / "access_evidence"
)

SECURITY_EMAIL = os.getenv(
    "SECURITY_EMAIL"
)

# Umbral experimental
THRESHOLD = 0.45

# Frames necesarios para confirmar identidad
CONFIRMATION_FRAMES = 5

# Frames ausente antes de permitir
# un nuevo evento
REARM_MISSING_FRAMES = 15

# Tiempo visual de puerta abierta
DOOR_OPEN_TIME = 3


# =============================================
# PUNTOS DE REFERENCIA PARA ALINEACION
# =============================================

REFERENCE_POINTS = np.array(
    [
        [38.2946, 51.6963],
        [73.5318, 51.5014],
        [56.0252, 71.7366],
        [41.5493, 92.3655],
        [70.7299, 92.2041],
    ],
    dtype=np.float32,
)


# =============================================
# CARGAR PERSONAS
# =============================================

def load_people():

    db_people = get_active_people()

    templates = {}
    people = {}

    for person in db_people:

        code = person["codigo_biometrico"]

        template_path = (
            ROOT_DIR
            / person["template_path"]
        )

        if not template_path.exists():

            print(
                f"ADVERTENCIA: "
                f"No existe template para {code}: "
                f"{template_path}"
            )

            continue

        template = np.load(
            template_path
        ).astype(
            np.float32
        )

        norm = np.linalg.norm(
            template
        )

        if norm == 0:

            print(
                f"ADVERTENCIA: "
                f"Template invalido para {code}"
            )

            continue

        template = (
            template / norm
        )

        templates[code] = template
        people[code] = person

    return templates, people


# =============================================
# ALINEACION FACIAL
# =============================================

def align_face(
    frame,
    face,
):

    landmarks = (
        face[4:14]
        .reshape((5, 2))
        .astype(np.float32)
    )

    matrix, _ = (
        cv2.estimateAffinePartial2D(
            landmarks,
            REFERENCE_POINTS,
            method=cv2.LMEDS,
        )
    )

    if matrix is None:
        return None

    return cv2.warpAffine(
        frame,
        matrix,
        (112, 112),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0),
    )


# =============================================
# PREPROCESAMIENTO
# =============================================

def preprocess_face(
    image,
):

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB,
    )

    image = image.astype(
        np.float32
    )

    image = (
        image - 127.5
    ) / 127.5

    image = np.transpose(
        image,
        (2, 0, 1),
    )

    image = np.expand_dims(
        image,
        axis=0,
    )

    return image


# =============================================
# GENERAR EMBEDDING
# =============================================

def get_embedding(
    session,
    face,
):

    input_info = (
        session.get_inputs()[0]
    )

    output_info = (
        session.get_outputs()[0]
    )

    processed = (
        preprocess_face(
            face
        )
    )

    result = session.run(
        [output_info.name],
        {
            input_info.name: processed
        },
    )

    embedding = (
        result[0]
        .flatten()
        .astype(np.float32)
    )

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        return None

    return embedding / norm


# =============================================
# IDENTIFICAR PERSONA
# =============================================

def identify_person(
    embedding,
    templates,
):

    best_code = None
    best_similarity = -1.0

    for code, template in (
        templates.items()
    ):

        similarity = float(
            np.dot(
                embedding,
                template,
            )
        )

        if (
            similarity
            > best_similarity
        ):

            best_similarity = (
                similarity
            )

            best_code = code

    if (
        best_similarity
        >= THRESHOLD
    ):

        return (
            best_code,
            best_similarity,
        )

    return (
        "DESCONOCIDO",
        best_similarity,
    )


# =============================================
# GUARDAR EVIDENCIA
# =============================================

def save_unknown_evidence(
    aligned_face,
):

    EVIDENCE_DIR.mkdir(
        parents=True,
        exist_ok=True,
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

    saved = cv2.imwrite(
        str(full_path),
        aligned_face,
    )

    if not saved:

        print(
            "ADVERTENCIA: "
            "No se pudo guardar la evidencia."
        )

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
    access_date,
):

    try:

        return access_date.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

    except Exception:

        return str(
            access_date
        )


# =============================================
# NOTIFICAR ACCESO AUTORIZADO
# =============================================

def notify_authorized_access(
    access,
    person,
    access_point,
):

    recipients = (
        get_notification_recipients(
            person["id"]
        )
    )

    if not recipients:

        print(
            "ADVERTENCIA: "
            "No existen responsables "
            "de notificacion con correo "
            "para esta vivienda."
        )

        return

    access_date = (
        format_access_date(
            access["fecha_hora"]
        )
    )

    # Evita enviar dos veces
    # al mismo correo
    processed_emails = set()

    for recipient in recipients:

        email = recipient[
            "email"
        ]

        if not email:
            continue

        if email in processed_emails:
            continue

        processed_emails.add(
            email
        )

        notification = None

        try:

            notification = (
                create_notification(
                    access_id=access["id"],
                    recipient_email=email,
                    notification_type="INGRESO",
                )
            )

            send_authorized_access_email(
                recipient=email,
                visitor_name=person[
                    "nombre_completo"
                ],
                visitor_type=person[
                    "tipo"
                ],
                house=recipient[
                    "vivienda"
                ],
                access_point=access_point[
                    "nombre"
                ],
                access_date=access_date,
            )

            mark_notification_sent(
                notification["id"]
            )

            print(
                f"Correo de ingreso enviado a: "
                f"{email}"
            )

        except Exception as error:

            print(
                f"ERROR enviando correo "
                f"de ingreso a {email}:"
            )

            print(error)

            if notification:

                try:

                    mark_notification_error(
                        notification["id"],
                        str(error),
                    )

                except Exception as db_error:

                    print(
                        "ERROR actualizando "
                        "notificacion:"
                    )

                    print(db_error)


# =============================================
# NOTIFICAR ALERTA A SEGURIDAD
# =============================================

def notify_security_alert(
    access,
    access_point,
    similarity,
    evidence_path,
):

    if not SECURITY_EMAIL:

        print(
            "ADVERTENCIA: "
            "SECURITY_EMAIL no configurado."
        )

        return

    notification = None

    access_date = (
        format_access_date(
            access["fecha_hora"]
        )
    )

    try:

        notification = (
            create_notification(
                access_id=access["id"],
                recipient_email=SECURITY_EMAIL,
                notification_type=(
                    "ALERTA_SEGURIDAD"
                ),
            )
        )

        send_security_alert_email(
            recipient=SECURITY_EMAIL,
            access_point=access_point[
                "nombre"
            ],
            similarity=similarity,
            access_date=access_date,
            evidence_path=evidence_path,
        )

        mark_notification_sent(
            notification["id"]
        )

        print(
            "Alerta de seguridad "
            f"enviada a: {SECURITY_EMAIL}"
        )

    except Exception as error:

        print(
            "ERROR enviando alerta "
            "de seguridad:"
        )

        print(error)

        if notification:

            try:

                mark_notification_error(
                    notification["id"],
                    str(error),
                )

            except Exception as db_error:

                print(
                    "ERROR actualizando "
                    "notificacion:"
                )

                print(db_error)


# =============================================
# PROGRAMA PRINCIPAL
# =============================================

def main():

    print(
        "======================================"
    )

    print(
        " CONTROL DE ACCESO FACIAL + POSTGRESQL"
    )

    print(
        "======================================"
    )

    # =========================================
    # PERSONAS
    # =========================================

    templates, people = (
        load_people()
    )

    if not templates:

        print(
            "ERROR: "
            "No existen personas "
            "biometricas activas."
        )

        return

    print("")

    print(
        f"Personas cargadas: "
        f"{len(people)}"
    )

    for code, person in (
        people.items()
    ):

        print(
            f"  {code} -> "
            f"{person['nombre_completo']}"
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

        print(
            "ERROR: "
            "No existe el punto "
            "'Entrada principal'."
        )

        return

    print("")

    print(
        f"Punto de acceso: "
        f"{access_point['nombre']}"
    )

    print(
        f"ID punto: "
        f"{access_point['id']}"
    )

    print(
        f"Correo seguridad: "
        f"{SECURITY_EMAIL}"
    )

    # =========================================
    # MOBILEFACENET
    # =========================================

    recognition_session = (
        ort.InferenceSession(
            str(
                MOBILEFACENET_MODEL
            ),
            providers=[
                "CPUExecutionProvider"
            ],
        )
    )

    # =========================================
    # CAMARA
    # =========================================

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "ERROR: "
            "No se pudo abrir la camara."
        )

        return

    ret, frame = camera.read()

    if not ret:

        print(
            "ERROR: "
            "No se pudo leer la camara."
        )

        camera.release()

        return

    height, width = (
        frame.shape[:2]
    )

    # =========================================
    # YUNET
    # =========================================

    detector = (
        cv2.FaceDetectorYN.create(
            str(YUNET_MODEL),
            "",
            (width, height),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=5000,
        )
    )

    confirmation_counter = (
        defaultdict(int)
    )

    access_registered = (
        defaultdict(
            lambda: False
        )
    )

    missing_counter = (
        defaultdict(int)
    )

    door_open_until = 0

    print("")

    print(
        f"Umbral: "
        f"{THRESHOLD}"
    )

    print(
        f"Confirmacion: "
        f"{CONFIRMATION_FRAMES} frames"
    )

    print(
        f"Tolerancia ausencia: "
        f"{REARM_MISSING_FRAMES} frames"
    )

    print("")

    print(
        "Q = salir"
    )

    # =========================================
    # LOOP
    # =========================================

    while True:

        ret, frame = (
            camera.read()
        )

        if not ret:
            break

        height, width = (
            frame.shape[:2]
        )

        detector.setInputSize(
            (width, height)
        )

        _, faces = (
            detector.detect(
                frame
            )
        )

        visible_ids = set()

        # =====================================
        # ROSTROS
        # =====================================

        if faces is not None:

            for face in faces:

                aligned = align_face(
                    frame.copy(),
                    face,
                )

                if aligned is None:
                    continue

                embedding = (
                    get_embedding(
                        recognition_session,
                        aligned,
                    )
                )

                if embedding is None:
                    continue

                code, similarity = (
                    identify_person(
                        embedding,
                        templates,
                    )
                )

                visible_ids.add(
                    code
                )

                missing_counter[
                    code
                ] = 0

                confirmation_counter[
                    code
                ] = min(
                    confirmation_counter[
                        code
                    ] + 1,
                    CONFIRMATION_FRAMES,
                )

                x, y, w, h = (
                    face[:4]
                    .astype(int)
                )

                # =============================
                # CONOCIDO
                # =============================

                if (
                    code
                    != "DESCONOCIDO"
                ):

                    person = (
                        people[code]
                    )

                    name = person[
                        "nombre_completo"
                    ]

                    person_type = person[
                        "tipo"
                    ]

                    house = (
                        person["viviendas"]
                        or "SIN VIVIENDA"
                    )

                    color = (
                        0,
                        255,
                        0,
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        color,
                        2,
                    )

                    cv2.putText(
                        frame,
                        name,
                        (x, y - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        color,
                        2,
                    )

                    cv2.putText(
                        frame,
                        (
                            f"{person_type} "
                            f"- {house}"
                        ),
                        (x, y - 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        color,
                        2,
                    )

                    cv2.putText(
                        frame,
                        (
                            f"{similarity:.3f} "
                            f"["
                            f"{confirmation_counter[code]}"
                            f"/"
                            f"{CONFIRMATION_FRAMES}"
                            f"]"
                        ),
                        (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        color,
                        2,
                    )

                # =============================
                # DESCONOCIDO
                # =============================

                else:

                    color = (
                        0,
                        0,
                        255,
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        color,
                        2,
                    )

                    cv2.putText(
                        frame,
                        "DESCONOCIDO",
                        (x, y - 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        color,
                        2,
                    )

                    cv2.putText(
                        frame,
                        (
                            f"{similarity:.3f} "
                            f"["
                            f"{confirmation_counter[code]}"
                            f"/"
                            f"{CONFIRMATION_FRAMES}"
                            f"]"
                        ),
                        (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        color,
                        2,
                    )

                # =============================
                # CONFIRMACION
                # =============================

                if (
                    confirmation_counter[
                        code
                    ]
                    >= CONFIRMATION_FRAMES
                ):

                    if not access_registered[
                        code
                    ]:

                        access_registered[
                            code
                        ] = True

                        current_time = (
                            time.time()
                        )

                        # =====================
                        # AUTORIZADO
                        # =====================

                        if (
                            code
                            != "DESCONOCIDO"
                        ):

                            person = (
                                people[code]
                            )

                            try:

                                access = (
                                    register_access(
                                        persona_id=person[
                                            "id"
                                        ],
                                        punto_acceso_id=access_point[
                                            "id"
                                        ],
                                        resultado="AUTORIZADO",
                                        similitud=similarity,
                                        puerta_abierta=True,
                                        motivo=None,
                                        captura_path=None,
                                    )
                                )

                                print("")

                                print(
                                    "=============================="
                                )

                                print(
                                    "ACCESO AUTORIZADO"
                                )

                                print(
                                    f"Persona: "
                                    f"{person['nombre_completo']}"
                                )

                                print(
                                    f"Codigo: {code}"
                                )

                                print(
                                    f"Tipo: "
                                    f"{person['tipo']}"
                                )

                                print(
                                    f"Vivienda: "
                                    f"{person['viviendas']}"
                                )

                                print(
                                    f"Similitud: "
                                    f"{similarity:.3f}"
                                )

                                print(
                                    f"Acceso BD: "
                                    f"{access['id']}"
                                )

                                print(
                                    "PUERTA ABIERTA"
                                )

                                door_open_until = (
                                    current_time
                                    + DOOR_OPEN_TIME
                                )

                                # =================
                                # NOTIFICACION
                                # =================

                                notify_authorized_access(
                                    access=access,
                                    person=person,
                                    access_point=access_point,
                                )

                                print(
                                    "=============================="
                                )

                            except Exception as error:

                                print(
                                    "ERROR PROCESANDO "
                                    "ACCESO AUTORIZADO:"
                                )

                                print(error)

                        # =====================
                        # RECHAZADO
                        # =====================

                        else:

                            try:

                                evidence_path = (
                                    save_unknown_evidence(
                                        aligned
                                    )
                                )

                                access = (
                                    register_access(
                                        persona_id=None,
                                        punto_acceso_id=access_point[
                                            "id"
                                        ],
                                        resultado="RECHAZADO",
                                        similitud=similarity,
                                        puerta_abierta=False,
                                        motivo=(
                                            "Rostro no registrado"
                                        ),
                                        captura_path=evidence_path,
                                    )
                                )

                                print("")

                                print(
                                    "=============================="
                                )

                                print(
                                    "ACCESO RECHAZADO"
                                )

                                print(
                                    "Persona: DESCONOCIDA"
                                )

                                print(
                                    f"Similitud maxima: "
                                    f"{similarity:.3f}"
                                )

                                print(
                                    f"Acceso BD: "
                                    f"{access['id']}"
                                )

                                print(
                                    f"Evidencia: "
                                    f"{evidence_path}"
                                )

                                print(
                                    "PUERTA CERRADA"
                                )

                                # =================
                                # ALERTA SEGURIDAD
                                # =================

                                notify_security_alert(
                                    access=access,
                                    access_point=access_point,
                                    similarity=similarity,
                                    evidence_path=evidence_path,
                                )

                                print(
                                    "=============================="
                                )

                            except Exception as error:

                                print(
                                    "ERROR PROCESANDO "
                                    "ACCESO RECHAZADO:"
                                )

                                print(error)

        # =====================================
        # TOLERANCIA DE AUSENCIA
        # =====================================

        for code in list(
            confirmation_counter.keys()
        ):

            if code in visible_ids:

                missing_counter[
                    code
                ] = 0

                continue

            missing_counter[
                code
            ] += 1

            if (
                missing_counter[
                    code
                ]
                < REARM_MISSING_FRAMES
            ):

                continue

            confirmation_counter[
                code
            ] = 0

            access_registered[
                code
            ] = False

            missing_counter[
                code
            ] = 0

        # =====================================
        # ESTADO PUERTA
        # =====================================

        if (
            time.time()
            < door_open_until
        ):

            cv2.rectangle(
                frame,
                (10, height - 70),
                (340, height - 15),
                (0, 255, 0),
                -1,
            )

            cv2.putText(
                frame,
                "PUERTA ABIERTA",
                (25, height - 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                2,
            )

        else:

            cv2.putText(
                frame,
                "PUERTA CERRADA",
                (20, height - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2,
            )

        # =====================================
        # VIDEO
        # =====================================

        cv2.imshow(
            "Control de Acceso Facial - PostgreSQL",
            frame,
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        if key == ord("q"):
            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()