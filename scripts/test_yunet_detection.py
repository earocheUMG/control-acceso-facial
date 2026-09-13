import cv2


MODEL_PATH = "models/yunet/face_detection_yunet_2023mar.onnx"
CAMERA_INDEX = 0


def main():
    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    ret, frame = camera.read()

    if not ret:
        print("ERROR: No se pudo obtener un frame inicial.")
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

    print("YuNet iniciado correctamente.")
    print("Presiona Q para salir.")

    while True:
        ret, frame = camera.read()

        if not ret:
            break

        height, width = frame.shape[:2]

        detector.setInputSize(
            (width, height)
        )

        _, faces = detector.detect(frame)

        if faces is not None:

            for face in faces:

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
            "YuNet - Deteccion y landmarks",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()