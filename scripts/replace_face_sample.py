import cv2
import os


CAMERA_INDEX = 0
FACE_SIZE = (160, 160)


def main():
    print("======================================")
    print("   REEMPLAZO DE MUESTRA FACIAL")
    print("======================================")

    person_id = input(
        "Ingrese el ID de la persona: "
    ).strip()

    sample_number = input(
        "Ingrese el número de muestra a reemplazar: "
    ).strip()

    if not person_id or not sample_number:
        print("ERROR: ID y número de muestra son obligatorios.")
        return

    if not sample_number.isdigit():
        print("ERROR: El número de muestra debe ser numérico.")
        return

    sample_number = int(sample_number)

    if sample_number < 1 or sample_number > 99:
        print("ERROR: Número de muestra fuera de rango.")
        return

    person_dir = f"data/faces/{person_id}"

    if not os.path.isdir(person_dir):
        print(
            f"ERROR: No existe la carpeta de la persona: {person_dir}"
        )
        return

    filename = (
        f"{person_dir}/sample_{sample_number:02d}.jpg"
    )

    print("")
    print(f"Persona: {person_id}")
    print(
        f"Muestra objetivo: sample_{sample_number:02d}.jpg"
    )

    if os.path.exists(filename):
        print("La muestra actual será reemplazada.")
    else:
        print(
            "La muestra no existe actualmente; se creará."
        )

    print("")
    print("Controles:")
    print("  C = Capturar y reemplazar")
    print("  Q = Cancelar")
    print("")

    cascade_path = (
        cv2.data.haarcascades
        + "haarcascade_frontalface_default.xml"
    )

    face_detector = cv2.CascadeClassifier(
        cascade_path
    )

    if face_detector.empty():
        print("ERROR: No se pudo cargar el detector facial.")
        return

    camera = cv2.VideoCapture(
        CAMERA_INDEX
    )

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: No se pudo obtener imagen.")
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
            f"Reemplazar: sample_{sample_number:02d}.jpg",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

        cv2.imshow(
            "Control de Acceso Facial - Reemplazar muestra",
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

            face_crop = frame[
                y:y + h,
                x:x + w
            ]

            face_crop = cv2.resize(
                face_crop,
                FACE_SIZE
            )

            success = cv2.imwrite(
                filename,
                face_crop
            )

            if success:
                print("")
                print(
                    f"Muestra reemplazada correctamente: {filename}"
                )
            else:
                print(
                    "ERROR: No se pudo guardar la imagen."
                )

            break

        elif key == ord("q"):
            print("Operación cancelada.")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()