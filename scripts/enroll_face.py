import cv2
import os


CAMERA_INDEX = 0
MAX_SAMPLES = 10
FACE_SIZE = (160, 160)


def main():
    print("======================================")
    print("   ENROLAMIENTO FACIAL")
    print("======================================")

    person_id = input("Ingrese un identificador para la persona: ").strip()
    person_name = input("Ingrese el nombre de la persona: ").strip()

    if not person_id or not person_name:
        print("ERROR: El identificador y el nombre son obligatorios.")
        return

    # Carpeta donde guardaremos los rostros
    output_dir = f"data/faces/{person_id}"

    os.makedirs(output_dir, exist_ok=True)

    print("")
    print(f"Persona: {person_name}")
    print(f"ID: {person_id}")
    print(f"Carpeta: {output_dir}")
    print("")
    print("Controles:")
    print("  C = Capturar rostro")
    print("  Q = Cancelar / salir")
    print("")
    print(f"Se deben capturar {MAX_SAMPLES} muestras.")

    # Detector Haar provisional
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

    sample_count = 0

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: No se pudo obtener imagen de la cámara.")
            break

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = face_detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )

        # Solo permitiremos enrolamiento si hay exactamente un rostro
        if len(faces) == 1:

            x, y, w, h = faces[0]

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
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

        elif len(faces) > 1:

            cv2.putText(
                frame,
                "Debe haber solo una persona",
                (20, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )

            for x, y, w, h in faces:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
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
            f"Muestras: {sample_count}/{MAX_SAMPLES}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Control de Acceso Facial - Enrolamiento",
            frame
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):

            if len(faces) != 1:
                print(
                    "No se puede capturar: debe existir exactamente un rostro."
                )
                continue

            x, y, w, h = faces[0]

            # Recortar únicamente el rostro
            face_crop = frame[
                y:y + h,
                x:x + w
            ]

            # Normalizar tamaño
            face_crop = cv2.resize(
                face_crop,
                FACE_SIZE
            )

            sample_count += 1

            filename = (
                f"{output_dir}/"
                f"sample_{sample_count:02d}.jpg"
            )

            cv2.imwrite(
                filename,
                face_crop
            )

            print(
                f"Muestra {sample_count}/{MAX_SAMPLES} "
                f"guardada: {filename}"
            )

            if sample_count >= MAX_SAMPLES:
                print("")
                print("Enrolamiento completado.")
                break

        elif key == ord("q"):
            print("Enrolamiento cancelado.")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()