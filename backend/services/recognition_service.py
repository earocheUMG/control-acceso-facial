from pathlib import Path

import numpy as np

from backend.database.recognition_repository import (
    get_recognition_candidates
)

from backend.services.biometric_enrollment_service import (
    decode_image,
    detect_and_align_face,
    get_embedding
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


RECOGNITION_THRESHOLD = 0.45


# =============================================
# RESOLVER TEMPLATE
# =============================================

def resolve_template_path(
    template_path: str
):

    path = Path(
        template_path
    )


    if not path.is_absolute():

        path = (
            ROOT_DIR
            / path
        )


    path = (
        path.resolve()
    )


    if (
        path != ROOT_DIR
        and
        ROOT_DIR not in path.parents
    ):

        raise ValueError(
            "Ruta de plantilla "
            "biométrica inválida."
        )


    return path


# =============================================
# CARGAR TEMPLATE
# =============================================

def load_template(
    template_path: str
):

    path = (
        resolve_template_path(
            template_path
        )
    )


    if not path.exists():

        raise ValueError(
            "No existe la plantilla "
            f"biométrica: {template_path}"
        )


    template = (
        np.load(
            path
        )
        .flatten()
        .astype(
            np.float32
        )
    )


    norm = (
        np.linalg.norm(
            template
        )
    )


    if norm == 0:

        raise ValueError(
            "Plantilla biométrica inválida."
        )


    return (
        template
        / norm
    )


# =============================================
# ANALIZAR ROSTRO
# =============================================

def analyze_face(
    image_bytes
):

    # =========================================
    # DECODIFICAR
    # =========================================

    image = (
        decode_image(
            image_bytes
        )
    )


    # =========================================
    # DETECTAR Y ALINEAR
    # =========================================

    try:

        aligned_face = (
            detect_and_align_face(
                image
            )
        )


    except ValueError as error:

        message = str(
            error
        )


        if (
            "No se detectó"
            in message
        ):

            return (
                {
                    "estado":
                        "SIN_ROSTRO",

                    "autorizado":
                        False,

                    "similitud":
                        None,

                    "threshold":
                        RECOGNITION_THRESHOLD,

                    "persona":
                        None
                },
                None
            )


        if (
            "más de un rostro"
            in message
        ):

            return (
                {
                    "estado":
                        "MULTIPLES_ROSTROS",

                    "autorizado":
                        False,

                    "similitud":
                        None,

                    "threshold":
                        RECOGNITION_THRESHOLD,

                    "persona":
                        None
                },
                None
            )


        raise


    # =========================================
    # EMBEDDING
    # =========================================

    embedding = (
        get_embedding(
            aligned_face
        )
    )


    # =========================================
    # CANDIDATOS
    # =========================================

    candidates = (
        get_recognition_candidates()
    )


    if not candidates:

        return (
            {
                "estado":
                    "SIN_BIOMETRIAS",

                "autorizado":
                    False,

                "similitud":
                    None,

                "threshold":
                    RECOGNITION_THRESHOLD,

                "persona":
                    None
            },
            aligned_face
        )


    # =========================================
    # BUSCAR MEJOR COINCIDENCIA
    # =========================================

    best_candidate = None

    best_similarity = -1.0


    for candidate in candidates:

        try:

            template = (
                load_template(
                    candidate[
                        "template_path"
                    ]
                )
            )


        except ValueError:

            continue


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

            best_candidate = (
                candidate
            )


    # =========================================
    # SIN TEMPLATES VALIDOS
    # =========================================

    if best_candidate is None:

        return (
            {
                "estado":
                    "SIN_BIOMETRIAS",

                "autorizado":
                    False,

                "similitud":
                    None,

                "threshold":
                    RECOGNITION_THRESHOLD,

                "persona":
                    None
            },
            aligned_face
        )


    # =========================================
    # RECONOCIDO
    # =========================================

    if (
        best_similarity
        >= RECOGNITION_THRESHOLD
    ):

        return (
            {
                "estado":
                    "RECONOCIDO",

                "autorizado":
                    True,

                "similitud":
                    round(
                        best_similarity,
                        4
                    ),

                "threshold":
                    RECOGNITION_THRESHOLD,

                "persona": {

                    "id":
                        best_candidate[
                            "id"
                        ],

                    "codigo_biometrico":
                        best_candidate[
                            "codigo_biometrico"
                        ],

                    "nombre_completo":
                        best_candidate[
                            "nombre_completo"
                        ],

                    "tipo":
                        best_candidate[
                            "tipo"
                        ]
                }
            },
            aligned_face
        )


    # =========================================
    # DESCONOCIDO
    # =========================================

    return (
        {
            "estado":
                "DESCONOCIDO",

            "autorizado":
                False,

            "similitud":
                round(
                    best_similarity,
                    4
                ),

            "threshold":
                RECOGNITION_THRESHOLD,

            "persona":
                None
        },
        aligned_face
    )


# =============================================
# RECONOCIMIENTO SIMPLE PARA FRONTEND
# =============================================

def recognize_face(
    image_bytes
):

    result, _ = (
        analyze_face(
            image_bytes
        )
    )


    return result


# =============================================
# RECONOCIMIENTO + ROSTRO ALINEADO
# =============================================

def recognize_face_with_artifacts(
    image_bytes
):

    return (
        analyze_face(
            image_bytes
        )
    )