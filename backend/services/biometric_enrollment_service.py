from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


# =============================================
# RUTAS DEL PROYECTO
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


MOBILEFACENET_MODEL = (
    ROOT_DIR
    / "models"
    / "mobilefacenet"
    / "w600k_mbf.onnx"
)


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
# VALIDAR MODELOS
# =============================================

if not YUNET_MODEL.exists():

    raise FileNotFoundError(
        f"No se encontró el modelo YuNet: "
        f"{YUNET_MODEL}"
    )


if not MOBILEFACENET_MODEL.exists():

    raise FileNotFoundError(
        f"No se encontró MobileFaceNet: "
        f"{MOBILEFACENET_MODEL}"
    )


# =============================================
# SESION MOBILEFACENET
# =============================================

MOBILEFACENET_SESSION = (
    ort.InferenceSession(
        str(MOBILEFACENET_MODEL),
        providers=[
            "CPUExecutionProvider"
        ]
    )
)


# =============================================
# CONVERTIR BYTES A IMAGEN OPENCV
# =============================================

def decode_image(
    image_bytes
):

    image_array = np.frombuffer(
        image_bytes,
        dtype=np.uint8
    )


    image = cv2.imdecode(
        image_array,
        cv2.IMREAD_COLOR
    )


    if image is None:

        raise ValueError(
            "No fue posible leer la imagen."
        )


    return image


# =============================================
# DETECTAR Y ALINEAR ROSTRO
# =============================================

def detect_and_align_face(
    image
):

    height, width = (
        image.shape[:2]
    )


    detector = (
        cv2.FaceDetectorYN.create(
            str(YUNET_MODEL),
            "",
            (
                width,
                height
            ),
            score_threshold=0.8,
            nms_threshold=0.3,
            top_k=5000
        )
    )


    _, faces = detector.detect(
        image
    )


    # =========================================
    # VALIDAR ROSTROS
    # =========================================

    if (
        faces is None
        or len(faces) == 0
    ):

        raise ValueError(
            "No se detectó ningún rostro."
        )


    if len(faces) > 1:

        raise ValueError(
            "Se detectó más de un rostro."
        )


    face = faces[0]


    # =========================================
    # LANDMARKS YUNET
    # =========================================

    landmarks = (
        face[4:14]
        .reshape(
            (5, 2)
        )
        .astype(
            np.float32
        )
    )


    # =========================================
    # MATRIZ DE ALINEACION
    # =========================================

    matrix, _ = (
        cv2.estimateAffinePartial2D(
            landmarks,
            REFERENCE_POINTS,
            method=cv2.LMEDS
        )
    )


    if matrix is None:

        raise ValueError(
            "No fue posible alinear el rostro."
        )


    aligned_face = (
        cv2.warpAffine(
            image,
            matrix,
            (
                112,
                112
            ),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(
                0,
                0,
                0
            )
        )
    )


    return aligned_face


# =============================================
# PREPROCESAR PARA MOBILEFACENET
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
        (
            2,
            0,
            1
        )
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
    image
):

    input_info = (
        MOBILEFACENET_SESSION
        .get_inputs()[0]
    )


    output_info = (
        MOBILEFACENET_SESSION
        .get_outputs()[0]
    )


    processed_image = (
        preprocess_face(
            image
        )
    )


    result = (
        MOBILEFACENET_SESSION.run(
            [
                output_info.name
            ],
            {
                input_info.name:
                    processed_image
            }
        )
    )


    embedding = (
        result[0]
        .flatten()
        .astype(
            np.float32
        )
    )


    norm = np.linalg.norm(
        embedding
    )


    if norm == 0:

        raise ValueError(
            "El embedding generado es inválido."
        )


    return (
        embedding / norm
    )


# =============================================
# PROCESAR ENROLAMIENTO
# =============================================

def process_enrollment_images(
    images
):

    if len(images) != 10:

        raise ValueError(
            "El enrolamiento requiere "
            "exactamente 10 muestras."
        )


    aligned_faces = []

    embeddings = []


    for index, image_bytes in enumerate(
        images,
        start=1
    ):

        try:

            # =================================
            # DECODIFICAR
            # =================================

            image = decode_image(
                image_bytes
            )


            # =================================
            # DETECTAR Y ALINEAR
            # =================================

            aligned_face = (
                detect_and_align_face(
                    image
                )
            )


            # =================================
            # GENERAR EMBEDDING
            # =================================

            embedding = (
                get_embedding(
                    aligned_face
                )
            )


            aligned_faces.append(
                aligned_face
            )


            embeddings.append(
                embedding
            )


        except ValueError as error:

            raise ValueError(
                f"Muestra {index}: "
                f"{error}"
            )


    # =========================================
    # CREAR TEMPLATE PROMEDIO
    # =========================================

    embeddings_array = np.array(
        embeddings,
        dtype=np.float32
    )


    template = np.mean(
        embeddings_array,
        axis=0
    )


    template_norm = np.linalg.norm(
        template
    )


    if template_norm == 0:

        raise ValueError(
            "No fue posible generar "
            "la plantilla biométrica."
        )


    template = (
        template
        / template_norm
    )


    # =========================================
    # CALCULAR SIMILITUD DE LAS MUESTRAS
    # =========================================

    similarities = (
        embeddings_array
        @ template
    )


    return {
        "template":
            template.astype(
                np.float32
            ),

        "aligned_faces":
            aligned_faces,

        "similarities":
            similarities
    }


# =============================================
# VALIDAR UNA MUESTRA DE ENROLAMIENTO
# =============================================

def validate_enrollment_image(
    image_bytes
):
    """
    Valida que una imagen contenga exactamente
    un rostro detectable y alineable.
    """

    image = decode_image(
        image_bytes
    )

    aligned_face = (
        detect_and_align_face(
            image
        )
    )

    # Generamos también el embedding para
    # comprobar que MobileFaceNet puede
    # procesar correctamente la muestra.
    embedding = (
        get_embedding(
            aligned_face
        )
    )

    return {
        "valid": True,
        "embedding_dimensions":
            int(
                embedding.shape[0]
            )
    }