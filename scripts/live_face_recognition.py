import cv2
import numpy as np
import onnxruntime as ort
import os
import time
from collections import defaultdict


CAMERA_INDEX = 0

YUNET_MODEL = (
    "models/yunet/"
    "face_detection_yunet_2023mar.onnx"
)

MOBILEFACENET_MODEL = (
    "models/mobilefacenet/"
    "w600k_mbf.onnx"
)

TEMPLATES_DIR = "data/templates"

# Todavía experimental
THRESHOLD = 0.45

# Cantidad de frames consecutivos requeridos
CONFIRMATION_FRAMES = 5

# Evitar registrar repetidamente a la misma persona
ACCESS_COOLDOWN = 10

# Tiempo que mostraremos la puerta abierta
DOOR_OPEN_TIME = 3


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


def load_templates():

    templates = {}

    for file in os.listdir(TEMPLATES_DIR):

        if file.endswith(".npy"):

            person_id = os.path.splitext(file)[0]

            path = os.path.join(
                TEMPLATES_DIR,
                file
            )

            templates[person_id] = np.load(
                path
            )

    return templates


def align_face(frame, face):

    landmarks = face[4:14].reshape(
        (5, 2)
    ).astype(np.float32)

    matrix, _ = cv2.estimateAffinePartial2D(
        landmarks,
        REFERENCE_POINTS,
        method=cv2.LMEDS
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


def preprocess_face(image):

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


def get_embedding(session, face):

    input_info = session.get_inputs()[0]
    output_info = session.get_outputs()[0]

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

    return embedding / norm


def identify_person(
    embedding,
    templates
):

    best_id = None
    best_similarity = -1.0

    for person_id, template in templates.items():

        similarity = float(
            np.dot(
                embedding,
                template
            )
        )

        if similarity > best_similarity:

            best_similarity = similarity
            best_id = person_id

    if best_similarity >= THRESHOLD:

        return (
            best_id,
            best_similarity
        )

    return (
        "DESCONOCIDO",
        best_similarity
    )


def main():

    print("======================================")
    print("      CONTROL DE ACCESO FACIAL")
    print("======================================")

    templates = load_templates()

    if not templates:

        print(
            "ERROR: No existen plantillas."
        )

        return

    recognition_session = ort.InferenceSession(
        MOBILEFACENET_MODEL,
        providers=["CPUExecutionProvider"]
    )

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():

        print(
            "ERROR: No se pudo abrir la cámara."
        )

        return

    ret, frame = camera.read()

    if not ret:

        print(
            "ERROR: No se pudo leer la cámara."
        )

        camera.release()
        return

    height, width = frame.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        YUNET_MODEL,
        "",
        (width, height),
        score_threshold=0.8,
        nms_threshold=0.3,
        top_k=5000
    )

    confirmation_counter = defaultdict(int)

    last_access = defaultdict(
        lambda: 0
    )

    door_open_until = 0

    print("")
    print(
        f"Umbral: {THRESHOLD}"
    )

    print(
        f"Frames de confirmación: "
        f"{CONFIRMATION_FRAMES}"
    )

    print("")
    print("Q = salir")

    while True:

        ret, frame = camera.read()

        if not ret:
            break

        height, width = frame.shape[:2]

        detector.setInputSize(
            (width, height)
        )

        _, faces = detector.detect(
            frame
        )

        visible_ids = set()

        if faces is not None:

            for face in faces:

                aligned = align_face(
                    frame.copy(),
                    face
                )

                if aligned is None:
                    continue

                embedding = get_embedding(
                    recognition_session,
                    aligned
                )

                if embedding is None:
                    continue

                person_id, similarity = (
                    identify_person(
                        embedding,
                        templates
                    )
                )

                visible_ids.add(
                    person_id
                )

                confirmation_counter[person_id] = min(
    confirmation_counter[person_id] + 1,
    CONFIRMATION_FRAMES
)

                x, y, w, h = (
                    face[:4]
                    .astype(int)
                )

                if person_id == "DESCONOCIDO":

                    color = (
                        0,
                        0,
                        255
                    )

                else:

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

                label = (
                    f"{person_id} "
                    f"{similarity:.3f} "
                    f"[{confirmation_counter[person_id]}/"
                    f"{CONFIRMATION_FRAMES}]"
                )

                cv2.putText(
                    frame,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    color,
                    2
                )

                # Identidad confirmada
                if (
                    confirmation_counter[person_id]
                    >= CONFIRMATION_FRAMES
                ):

                    current_time = time.time()

                    if (
                        current_time
                        - last_access[person_id]
                        >= ACCESS_COOLDOWN
                    ):

                        last_access[
                            person_id
                        ] = current_time

                        if (
                            person_id
                            != "DESCONOCIDO"
                        ):

                            print("")
                            print(
                                "=========================="
                            )

                            print(
                                "ACCESO AUTORIZADO"
                            )

                            print(
                                f"Persona: {person_id}"
                            )

                            print(
                                f"Similitud: "
                                f"{similarity:.3f}"
                            )

                            print(
                                "PUERTA ABIERTA"
                            )

                            print(
                                "=========================="
                            )

                            door_open_until = (
                                current_time
                                + DOOR_OPEN_TIME
                            )

                        else:

                            print("")
                            print(
                                "=========================="
                            )

                            print(
                                "ACCESO RECHAZADO"
                            )

                            print(
                                "Persona desconocida"
                            )

                            print(
                                f"Similitud máxima: "
                                f"{similarity:.3f}"
                            )

                            print(
                                "ALERTA A SEGURIDAD"
                            )

                            print(
                                "=========================="
                            )

        # Reiniciar contador de identidades
        # que ya no aparecen en pantalla
        for person_id in list(
            confirmation_counter.keys()
        ):

            if person_id not in visible_ids:

                confirmation_counter[
                    person_id
                ] = 0

        # Indicador visual de puerta
        if time.time() < door_open_until:

            cv2.rectangle(
                frame,
                (10, height - 70),
                (300, height - 15),
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

        cv2.imshow(
            "Sistema de Control de Acceso",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()