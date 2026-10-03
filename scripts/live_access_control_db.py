import sys
from pathlib import Path
import time
from collections import defaultdict

import cv2
import numpy as np
import onnxruntime as ort


# =============================================
# RUTA RAIZ DEL PROYECTO
# =============================================

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(
    0,
    str(ROOT_DIR)
)


from backend.database.access_repository import (
    get_active_people,
    get_access_point,
    register_access
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

# Umbral experimental
THRESHOLD = 0.45

# Frames consecutivos necesarios
CONFIRMATION_FRAMES = 5

# Segundos que permanece abierta la puerta
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
    dtype=np.float32
)


# =============================================
# CARGAR PERSONAS DESDE POSTGRESQL
# =============================================

def load_people():

    db_people = get_active_people()

    templates = {}
    people = {}

    for person in db_people:

        code = person[
            "codigo_biometrico"
        ]

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
    face
):

    landmarks = face[
        4:14
    ].reshape(
        (5, 2)
    ).astype(
        np.float32
    )

    matrix, _ = (
        cv2.estimateAffinePartial2D(
            landmarks,
            REFERENCE_POINTS,
            method=cv2.LMEDS
        )
    )

    if matrix is None:
        return None

    aligned = cv2.warpAffine(
        frame,
        matrix,
        (112, 112),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    return aligned


# =============================================
# PREPROCESAMIENTO MOBILEFACENET
# =============================================

def preprocess_face(
    image
):

    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    image = image.astype(
        np.float32
    )

    image = (
        image - 127.5
    ) / 127.5

    image = np.transpose(
        image,
        (2, 0, 1)
    )

    image = np.expand_dims(
        image,
        axis=0
    )

    return image


# =============================================
# GENERAR EMBEDDING
# =============================================

def get_embedding(
    session,
    face
):

    input_info = (
        session.get_inputs()[0]
    )

    output_info = (
        session.get_outputs()[0]
    )

    processed = preprocess_face(
        face
    )

    result = session.run(
        [output_info.name],
        {
            input_info.name: processed
        }
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

    return (
        embedding / norm
    )


# =============================================
# IDENTIFICAR PERSONA
# =============================================

def identify_person(
    embedding,
    templates
):

    best_code = None

    best_similarity = -1.0

    for code, template in (
        templates.items()
    ):

        similarity = float(
            np.dot(
                embedding,
                template
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
            best_similarity
        )

    return (
        "DESCONOCIDO",
        best_similarity
    )


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
    # CARGAR PERSONAS
    # =========================================

    templates, people = (
        load_people()
    )

    if not templates:

        print(
            "ERROR: "
            "No existen personas biometricas activas."
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
            ]
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
            top_k=5000
        )
    )

    # Cantidad de frames consecutivos
    confirmation_counter = (
        defaultdict(int)
    )

    # Indica si ya generamos el evento
    # mientras la persona sigue en cámara
    access_registered = (
        defaultdict(
            lambda: False
        )
    )

    # Tiempo hasta el cual mostramos
    # la puerta abierta
    door_open_until = 0

    print("")

    print(
        f"Umbral: {THRESHOLD}"
    )

    print(
        f"Confirmacion: "
        f"{CONFIRMATION_FRAMES} frames"
    )

    print("")

    print(
        "Q = salir"
    )

    # =========================================
    # LOOP PRINCIPAL
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

        # Identidades presentes
        # actualmente en cámara
        visible_ids = set()

        # =====================================
        # PROCESAR ROSTROS
        # =====================================

        if faces is not None:

            for face in faces:

                aligned = (
                    align_face(
                        frame.copy(),
                        face
                    )
                )

                if aligned is None:
                    continue

                embedding = (
                    get_embedding(
                        recognition_session,
                        aligned
                    )
                )

                if embedding is None:
                    continue

                code, similarity = (
                    identify_person(
                        embedding,
                        templates
                    )
                )

                visible_ids.add(
                    code
                )

                # Aumentar contador
                # hasta un máximo de 5
                confirmation_counter[
                    code
                ] = min(
                    confirmation_counter[
                        code
                    ] + 1,
                    CONFIRMATION_FRAMES
                )

                x, y, w, h = (
                    face[:4]
                    .astype(int)
                )

                # =================================
                # PERSONA CONOCIDA
                # =================================

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
                        0
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        color,
                        2
                    )

                    cv2.putText(
                        frame,
                        name,
                        (x, y - 50),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        color,
                        2
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
                        2
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
                        2
                    )

                # =================================
                # PERSONA DESCONOCIDA
                # =================================

                else:

                    color = (
                        0,
                        0,
                        255
                    )

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        color,
                        2
                    )

                    cv2.putText(
                        frame,
                        "DESCONOCIDO",
                        (x, y - 28),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.65,
                        color,
                        2
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
                        2
                    )

                # =================================
                # IDENTIDAD CONFIRMADA
                # =================================

                if (
                    confirmation_counter[
                        code
                    ]
                    >= CONFIRMATION_FRAMES
                ):

                    # Solo registrar una vez
                    # mientras siga visible
                    if not access_registered[
                        code
                    ]:

                        access_registered[
                            code
                        ] = True

                        current_time = (
                            time.time()
                        )

                        # =========================
                        # ACCESO AUTORIZADO
                        # =========================

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
                                        motivo=None
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
                                    f"Codigo: "
                                    f"{code}"
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
                                    f"Fecha BD: "
                                    f"{access['fecha_hora']}"
                                )

                                print(
                                    "PUERTA ABIERTA"
                                )

                                print(
                                    "=============================="
                                )

                                door_open_until = (
                                    current_time
                                    + DOOR_OPEN_TIME
                                )

                            except Exception as error:

                                print("")

                                print(
                                    "ERROR REGISTRANDO ACCESO:"
                                )

                                print(
                                    error
                                )

                        # =========================
                        # ACCESO RECHAZADO
                        # =========================

                        else:

                            try:

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
                                        )
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
                                    f"Fecha BD: "
                                    f"{access['fecha_hora']}"
                                )

                                print(
                                    "PUERTA CERRADA"
                                )

                                print(
                                    "ALERTA A SEGURIDAD"
                                )

                                print(
                                    "=============================="
                                )

                            except Exception as error:

                                print("")

                                print(
                                    "ERROR REGISTRANDO RECHAZO:"
                                )

                                print(
                                    error
                                )

        # =====================================
        # REARMAR IDENTIDADES QUE SALIERON
        # DE LA CAMARA
        # =====================================

        for code in list(
            confirmation_counter.keys()
        ):

            if (
                code
                not in visible_ids
            ):

                confirmation_counter[
                    code
                ] = 0

                access_registered[
                    code
                ] = False

        # =====================================
        # ESTADO DE LA PUERTA
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
                -1
            )

            cv2.putText(
                frame,
                "PUERTA ABIERTA",
                (25, height - 32),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 0),
                2
            )

        else:

            cv2.putText(
                frame,
                "PUERTA CERRADA",
                (20, height - 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 255, 255),
                2
            )

        # =====================================
        # MOSTRAR VIDEO
        # =====================================

        cv2.imshow(
            "Control de Acceso Facial - PostgreSQL",
            frame
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