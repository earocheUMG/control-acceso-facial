import sys
import shutil
from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


# =============================================
# RUTA RAIZ
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.insert(
    0,
    str(ROOT_DIR)
)


from backend.database.biometric_repository import (
    get_pending_biometric_people,
    get_next_biometric_code,
    register_person_biometrics
)


# =============================================
# CONFIGURACION
# =============================================

CAMERA_INDEX = 0

TOTAL_SAMPLES = 10

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

FACES_DIR = (
    ROOT_DIR
    / "data"
    / "faces_aligned"
)

TEMPLATES_DIR = (
    ROOT_DIR
    / "data"
    / "templates"
)


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
# ALINEACION
# =============================================

def align_face(
    frame,
    face
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
            method=cv2.LMEDS
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
        borderValue=(0, 0, 0)
    )


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
        (2, 0, 1)
    )

    return np.expand_dims(
        image,
        axis=0
    )


# =============================================
# EMBEDDING
# =============================================

def get_embedding(
    session,
    image
):

    input_info = (
        session.get_inputs()[0]
    )

    output_info = (
        session.get_outputs()[0]
    )

    processed = (
        preprocess_face(
            image
        )
    )

    result = session.run(
        [output_info.name],
        {
            input_info.name:
                processed
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

        raise ValueError(
            "Embedding inválido."
        )

    return (
        embedding / norm
    )


# =============================================
# CREAR TEMPLATE
# =============================================

def create_template(
    session,
    images
):

    embeddings = []

    for image in images:

        embedding = (
            get_embedding(
                session,
                image
            )
        )

        embeddings.append(
            embedding
        )

    embeddings = np.array(
        embeddings
    )

    template = np.mean(
        embeddings,
        axis=0
    )

    norm = np.linalg.norm(
        template
    )

    if norm == 0:

        raise ValueError(
            "Template biométrico inválido."
        )

    template = (
        template / norm
    )

    similarities = (
        embeddings @ template
    )

    return (
        template.astype(np.float32),
        similarities
    )


# =============================================
# SELECCIONAR PERSONA
# =============================================

def select_person():

    people = (
        get_pending_biometric_people()
    )

    if not people:

        print("")
        print(
            "No existen personas "
            "pendientes de enrolamiento."
        )

        return None

    print("")
    print(
        "PERSONAS PENDIENTES"
    )

    print(
        "======================================"
    )

    for person in people:

        print(
            f"ID BD: {person['id']} | "
            f"{person['nombre_completo']} | "
            f"{person['tipo']} | "
            f"{person['viviendas']}"
        )

    print(
        "======================================"
    )

    try:

        selected_id = int(
            input(
                "Ingrese el ID BD "
                "de la persona: "
            )
        )

    except ValueError:

        print(
            "ID inválido."
        )

        return None

    for person in people:

        if (
            person["id"]
            == selected_id
        ):

            return person

    print(
        "La persona indicada "
        "no está pendiente "
        "de enrolamiento."
    )

    return None


# =============================================
# CAPTURA
# =============================================

def capture_samples(
    person,
    biometric_code
):

    person_dir = (
        FACES_DIR
        / biometric_code
    )

    if person_dir.exists():

        print(
            "ERROR: Ya existe la carpeta:"
        )

        print(
            person_dir
        )

        return None

    person_dir.mkdir(
        parents=True,
        exist_ok=False
    )

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "ERROR: No se pudo abrir "
            "la cámara."
        )

        shutil.rmtree(
            person_dir
        )

        return None

    ret, frame = (
        camera.read()
    )

    if not ret:

        camera.release()

        shutil.rmtree(
            person_dir
        )

        print(
            "ERROR: No se pudo leer "
            "la cámara."
        )

        return None

    height, width = (
        frame.shape[:2]
    )

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

    samples = []

    print("")
    print(
        "======================================"
    )

    print(
        "       ENROLAMIENTO FACIAL"
    )

    print(
        "======================================"
    )

    print(
        f"Persona: "
        f"{person['nombre_completo']}"
    )

    print(
        f"Codigo asignado: "
        f"{biometric_code}"
    )

    print("")
    print(
        "C = capturar muestra"
    )

    print(
        "Q = cancelar"
    )

    print("")
    print(
        "Realice pequeñas variaciones "
        "de posición entre capturas."
    )

    while (
        len(samples)
        < TOTAL_SAMPLES
    ):

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

        display_frame = (
            frame.copy()
        )

        valid_face = None

        # =====================================
        # EXIGIR EXACTAMENTE UN ROSTRO
        # =====================================

        if (
            faces is not None
            and len(faces) == 1
        ):

            face = faces[0]

            aligned = align_face(
                frame,
                face
            )

            if aligned is not None:

                valid_face = (
                    aligned
                )

                x, y, w, h = (
                    face[:4]
                    .astype(int)
                )

                cv2.rectangle(
                    display_frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                # Landmarks
                landmarks = (
                    face[4:14]
                    .reshape((5, 2))
                    .astype(int)
                )

                for point in landmarks:

                    cv2.circle(
                        display_frame,
                        tuple(point),
                        2,
                        (0, 0, 255),
                        -1
                    )

        # =====================================
        # TEXTO
        # =====================================

        cv2.putText(
            display_frame,
            (
                f"{person['nombre_completo']}"
            ),
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            display_frame,
            (
                f"Muestras: "
                f"{len(samples)}"
                f"/{TOTAL_SAMPLES}"
            ),
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        if valid_face is None:

            cv2.putText(
                display_frame,
                "Debe existir exactamente un rostro",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                display_frame,
                "Presione C para capturar",
                (20, 105),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        cv2.imshow(
            "Enrolamiento Facial",
            display_frame
        )

        key = (
            cv2.waitKey(1)
            & 0xFF
        )

        # =====================================
        # CANCELAR
        # =====================================

        if key == ord("q"):

            camera.release()

            cv2.destroyAllWindows()

            shutil.rmtree(
                person_dir
            )

            print("")
            print(
                "Enrolamiento cancelado."
            )

            return None

        # =====================================
        # CAPTURAR
        # =====================================

        if (
            key == ord("c")
            and valid_face is not None
        ):

            sample_number = (
                len(samples) + 1
            )

            filename = (
                person_dir
                / (
                    f"sample_"
                    f"{sample_number:02d}"
                    f".jpg"
                )
            )

            cv2.imwrite(
                str(filename),
                valid_face
            )

            samples.append(
                valid_face.copy()
            )

            print(
                f"Muestra "
                f"{sample_number:02d} "
                f"capturada."
            )

    camera.release()

    cv2.destroyAllWindows()

    if (
        len(samples)
        != TOTAL_SAMPLES
    ):

        shutil.rmtree(
            person_dir
        )

        print(
            "ERROR: El enrolamiento "
            "no se completó."
        )

        return None

    return (
        samples,
        person_dir
    )


# =============================================
# MAIN
# =============================================

def main():

    print(
        "======================================"
    )

    print(
        " ENROLAMIENTO DE PERSONA REGISTRADA"
    )

    print(
        "======================================"
    )

    person = (
        select_person()
    )

    if not person:
        return

    biometric_code = (
        get_next_biometric_code()
    )

    print("")
    print(
        f"Codigo biometrico "
        f"disponible: {biometric_code}"
    )

    result = (
        capture_samples(
            person,
            biometric_code
        )
    )

    if not result:
        return

    samples, person_dir = (
        result
    )

    # =========================================
    # MOBILEFACENET
    # =========================================

    session = (
        ort.InferenceSession(
            str(
                MOBILEFACENET_MODEL
            ),
            providers=[
                "CPUExecutionProvider"
            ]
        )
    )

    try:

        template, similarities = (
            create_template(
                session,
                samples
            )
        )

        TEMPLATES_DIR.mkdir(
            parents=True,
            exist_ok=True
        )

        template_file = (
            TEMPLATES_DIR
            / (
                f"{biometric_code}.npy"
            )
        )

        np.save(
            template_file,
            template
        )

        relative_template_path = str(
            template_file.relative_to(
                ROOT_DIR
            )
        )

        # =====================================
        # ACTUALIZAR POSTGRESQL
        # =====================================

        register_person_biometrics(
            person_id=person["id"],
            biometric_code=biometric_code,
            template_path=relative_template_path,
            sample_count=TOTAL_SAMPLES
        )

        print("")
        print(
            "======================================"
        )

        print(
            " ENROLAMIENTO COMPLETADO"
        )

        print(
            "======================================"
        )

        print(
            f"Persona: "
            f"{person['nombre_completo']}"
        )

        print(
            f"Codigo biometrico: "
            f"{biometric_code}"
        )

        print(
            f"Muestras: "
            f"{TOTAL_SAMPLES}"
        )

        print(
            f"Template: "
            f"{relative_template_path}"
        )

        print(
            f"Similitud promedio: "
            f"{np.mean(similarities):.4f}"
        )

        print(
            f"Similitud minima: "
            f"{np.min(similarities):.4f}"
        )

        print(
            f"Similitud maxima: "
            f"{np.max(similarities):.4f}"
        )

        print("")
        print(
            "PostgreSQL actualizado "
            "correctamente."
        )

    except Exception as error:

        print("")
        print(
            "ERROR DURANTE EL ENROLAMIENTO:"
        )

        print(
            error
        )

        # Eliminar archivos parciales
        if person_dir.exists():

            shutil.rmtree(
                person_dir
            )

        template_file = (
            TEMPLATES_DIR
            / f"{biometric_code}.npy"
        )

        if template_file.exists():

            template_file.unlink()


if __name__ == "__main__":
    main()