import cv2
import numpy as np
import os


CAMERA_INDEX = 0

YUNET_MODEL = (
    "models/yunet/"
    "face_detection_yunet_2023mar.onnx"
)

MAX_SAMPLES = 10


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

    aligned = cv2.warpAffine(
        frame,
        matrix,
        (112, 112),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(0, 0, 0)
    )

    return aligned


def main():

    print("======================================")
    print("  ENROLAMIENTO FACIAL CON YUNET")
    print("======================================")

    person_id = input(
        "Ingrese el ID de la persona: "
    ).strip()

    person_name = input(
        "Ingrese el nombre de la persona: "
    ).strip()

    if not person_id or not person_name:
        print(
            "ERROR: ID y nombre son obligatorios."
        )
        return

    output_dir = (
        f"data/faces_aligned/{person_id}"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
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
            "ERROR: No se pudo obtener imagen."
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

    sample_count = 0

    print("")
    print(f"Persona: {person_name}")
    print(f"ID: {person_id}")

    print("")
    print("Controles:")
    print("  C = capturar muestra")
    print("  Q = cancelar")
    print("")

    while True:

        ret, frame = camera.read()

        if not ret:
            print(
                "ERROR: No se pudo capturar imagen."
            )
            break

        height, width = frame.shape[:2]

        detector.setInputSize(
            (width, height)
        )

        _, faces = detector.detect(
            frame
        )

        aligned_face = None

        face_count = (
            0
            if faces is None
            else len(faces)
        )

        if face_count == 1:

            face = faces[0]

            aligned_face = align_face(
                frame.copy(),
                face
            )

            x, y, w, h = (
                face[:4].astype(int)
            )

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            landmarks = (
                face[4:14]
                .reshape((5, 2))
                .astype(int)
            )

            for point in landmarks:

                cv2.circle(
                    frame,
                    tuple(point),
                    3,
                    (0, 0, 255),
                    -1
                )

            cv2.putText(
                frame,
                "Listo para capturar",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        elif face_count > 1:

            cv2.putText(
                frame,
                "Debe haber solo una persona",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "No se detecta rostro",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

        cv2.putText(
            frame,
            (
                f"Muestras: "
                f"{sample_count}/{MAX_SAMPLES}"
            ),
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Enrolamiento facial - YuNet",
            frame
        )

        if aligned_face is not None:

            preview = cv2.resize(
                aligned_face,
                (336, 336),
                interpolation=cv2.INTER_NEAREST
            )

            cv2.imshow(
                "Vista alineada",
                preview
            )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):

            if face_count != 1:
                print(
                    "No se puede capturar: "
                    "debe haber exactamente un rostro."
                )
                continue

            if aligned_face is None:
                print(
                    "No se pudo alinear el rostro."
                )
                continue

            sample_count += 1

            filename = (
                f"{output_dir}/"
                f"sample_{sample_count:02d}.jpg"
            )

            success = cv2.imwrite(
                filename,
                aligned_face
            )

            if success:

                print(
                    f"Muestra "
                    f"{sample_count}/{MAX_SAMPLES} "
                    f"guardada."
                )

            else:

                print(
                    "ERROR al guardar muestra."
                )

                sample_count -= 1

            if (
                sample_count
                >= MAX_SAMPLES
            ):

                print("")
                print(
                    "Enrolamiento completado."
                )

                break

        elif key == ord("q"):

            print(
                "Enrolamiento cancelado."
            )

            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()