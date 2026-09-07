import cv2


CAMERA_INDEX = 0


def main():
    print("Iniciando detección facial...")

    # OpenCV incluye este detector facial básico
    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():
        print("ERROR: No se pudo cargar el detector facial.")
        return

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    print("Cámara iniciada correctamente.")
    print("Presiona Q para salir.")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: No se pudo capturar la imagen.")
            break

        # Convertimos el frame a escala de grises
        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # Buscamos rostros
        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80)
        )

        # Dibujamos un rectángulo por cada rostro
        for (x, y, w, h) in faces:
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Rostro detectado",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2
            )

        # Cantidad de rostros encontrados
        cv2.putText(
            frame,
            f"Rostros: {len(faces)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Control de Acceso Facial - Deteccion",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            print("Cerrando detección facial...")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()