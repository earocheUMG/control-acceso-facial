import cv2
import numpy as np


MODEL_PATH = "models/yunet/face_detection_yunet_2023mar.onnx"
CAMERA_INDEX = 0


# Posiciones estándar para rostro de 112x112
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

    # YuNet devuelve:
    # ojo derecho
    # ojo izquierdo
    # nariz
    # comisura derecha
    # comisura izquierda
    #
    # Desde la perspectiva de la imagen, este orden
    # coincide con nuestra plantilla de referencia.

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

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    ret, frame = camera.read()

    if not ret:
        print("ERROR: No se pudo obtener imagen.")
        camera.release()
        return

    height, width = frame.shape[:2]

    detector = cv2.FaceDetectorYN.create(
        MODEL_PATH,
        "",
        (width, height),
        score_threshold=0.8,
        nms_threshold=0.3,
        top_k=5000
    )

    print("Alineación facial iniciada.")
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

        aligned_face = None

        if faces is not None:

            face = faces[0]

            # IMPORTANTE:
            # Alineamos antes de dibujar sobre el frame.
            aligned_face = align_face(
                frame.copy(),
                face
            )

            x, y, w, h = face[:4].astype(int)

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            landmarks = face[4:14].reshape(
                (5, 2)
            ).astype(int)

            for point in landmarks:

                cv2.circle(
                    frame,
                    tuple(point),
                    3,
                    (0, 0, 255),
                    -1
                )

        cv2.imshow(
            "YuNet - Original",
            frame
        )

        if aligned_face is not None:

            preview = cv2.resize(
                aligned_face,
                (336, 336),
                interpolation=cv2.INTER_NEAREST
            )

            cv2.imshow(
                "Rostro alineado 112x112",
                preview
            )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()