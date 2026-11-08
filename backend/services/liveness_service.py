import threading

from pathlib import Path

import cv2
import numpy as np


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


YUNET_MODEL = (
    ROOT_DIR
    / "models"
    / "yunet"
    / "face_detection_yunet_2023mar.onnx"
)


# Cuanto menor sea el valor absoluto,
# mas frontal se considera el rostro.
FRONTAL_THRESHOLD = 0.12


# A partir de este desplazamiento relativo
# consideramos que existe un giro real.
TURN_THRESHOLD = 0.18


# =============================================
# DETECTOR
# =============================================

_detector = None

_detector_lock = (
    threading.Lock()
)


# =============================================
# OBTENER DETECTOR
# =============================================

def get_detector(
    width: int,
    height: int
):

    global _detector


    if not YUNET_MODEL.exists():

        raise RuntimeError(
            "No se encontró el modelo "
            f"YuNet en: {YUNET_MODEL}"
        )


    if _detector is None:

        _detector = (
            cv2.FaceDetectorYN.create(
                str(
                    YUNET_MODEL
                ),
                "",
                (
                    width,
                    height
                ),
                score_threshold=
                    0.8,
                nms_threshold=
                    0.3,
                top_k=
                    5000
            )
        )


    _detector.setInputSize(
        (
            width,
            height
        )
    )


    return _detector


# =============================================
# DECODIFICAR IMAGEN
# =============================================

def decode_image(
    image_bytes
):

    image_array = (
        np.frombuffer(
            image_bytes,
            dtype=
                np.uint8
        )
    )


    image = (
        cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )
    )


    if image is None:

        raise ValueError(
            "No fue posible decodificar "
            "la imagen para la prueba "
            "de vida."
        )


    return image


# =============================================
# CALCULAR ORIENTACION
# =============================================

def calculate_yaw_score(
    face
):

    # YuNet devuelve:
    #
    # 0-3   -> bounding box
    # 4-13  -> 5 landmarks
    # 14    -> score
    #
    # Los 5 landmarks son:
    # - dos ojos
    # - nariz
    # - dos comisuras de la boca

    landmarks = (
        face[4:14]
        .reshape(
            (5, 2)
        )
        .astype(
            np.float32
        )
    )


    eye_1 = (
        landmarks[0]
    )

    eye_2 = (
        landmarks[1]
    )

    nose = (
        landmarks[2]
    )

    mouth_1 = (
        landmarks[3]
    )

    mouth_2 = (
        landmarks[4]
    )


    # Ordenamos los puntos horizontalmente.
    eyes = sorted(
        [
            eye_1,
            eye_2
        ],
        key=
            lambda point:
                point[0]
    )


    mouths = sorted(
        [
            mouth_1,
            mouth_2
        ],
        key=
            lambda point:
                point[0]
    )


    left_eye = (
        eyes[0]
    )

    right_eye = (
        eyes[1]
    )


    left_mouth = (
        mouths[0]
    )

    right_mouth = (
        mouths[1]
    )


    eye_distance = float(
        right_eye[0]
        - left_eye[0]
    )


    if (
        abs(
            eye_distance
        )
        < 1.0
    ):

        raise ValueError(
            "No fue posible calcular "
            "la orientación facial."
        )


    eye_mid_x = (
        float(
            left_eye[0]
            +
            right_eye[0]
        )
        / 2.0
    )


    mouth_mid_x = (
        float(
            left_mouth[0]
            +
            right_mouth[0]
        )
        / 2.0
    )


    # Centro facial aproximado.
    face_center_x = (
        eye_mid_x
        +
        mouth_mid_x
    ) / 2.0


    # El desplazamiento horizontal
    # de la nariz respecto al centro
    # cambia al rotar la cabeza.
    yaw_score = (
        float(
            nose[0]
        )
        -
        face_center_x
    ) / abs(
        eye_distance
    )


    return yaw_score


# =============================================
# ANALIZAR PRUEBA DE VIDA
# =============================================

def analyze_liveness(
    image_bytes
):

    image = (
        decode_image(
            image_bytes
        )
    )


    height, width = (
        image.shape[:2]
    )


    with _detector_lock:

        detector = (
            get_detector(
                width,
                height
            )
        )


        _, faces = (
            detector.detect(
                image
            )
        )


    # =========================================
    # SIN ROSTRO
    # =========================================

    if (
        faces is None
        or
        len(faces) == 0
    ):

        return {
            "estado":
                "SIN_ROSTRO",

            "frontal":
                False,

            "giro_detectado":
                False,

            "direccion":
                None,

            "yaw_score":
                None,

            "frontal_threshold":
                FRONTAL_THRESHOLD,

            "turn_threshold":
                TURN_THRESHOLD
        }


    # =========================================
    # MULTIPLES ROSTROS
    # =========================================

    if (
        len(faces)
        > 1
    ):

        return {
            "estado":
                "MULTIPLES_ROSTROS",

            "frontal":
                False,

            "giro_detectado":
                False,

            "direccion":
                None,

            "yaw_score":
                None,

            "frontal_threshold":
                FRONTAL_THRESHOLD,

            "turn_threshold":
                TURN_THRESHOLD
        }


    face = (
        faces[0]
    )


    yaw_score = (
        calculate_yaw_score(
            face
        )
    )


    absolute_yaw = (
        abs(
            yaw_score
        )
    )


    frontal = (
        absolute_yaw
        <=
        FRONTAL_THRESHOLD
    )


    turn_detected = (
        absolute_yaw
        >=
        TURN_THRESHOLD
    )


    direction = (
        "CENTRO"
    )


    if turn_detected:

        if yaw_score < 0:

            direction = (
                "LADO_A"
            )

        else:

            direction = (
                "LADO_B"
            )


    return {
        "estado":
            "OK",

        "frontal":
            frontal,

        "giro_detectado":
            turn_detected,

        "direccion":
            direction,

        "yaw_score":
            round(
                float(
                    yaw_score
                ),
                4
            ),

        "frontal_threshold":
            FRONTAL_THRESHOLD,

        "turn_threshold":
            TURN_THRESHOLD
    }