import cv2


CAMERA_INDEX = 0


def main():
    print("Iniciando prueba de cámara...")
    print(f"Intentando abrir cámara con índice: {CAMERA_INDEX}")

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        print("ERROR: No se pudo abrir la cámara.")
        return

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print("Cámara detectada correctamente.")
    print(f"Resolución detectada: {width}x{height}")
    print("")
    print("Controles:")
    print("  C = Capturar fotografía")
    print("  Q = Salir")

    while True:
        ret, frame = camera.read()

        if not ret:
            print("ERROR: No se pudo obtener una imagen de la cámara.")
            break

        cv2.imshow("Control de Acceso Facial - Prueba de Camara", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord("c"):
            output_path = "data/temp/captura_prueba.jpg"
            cv2.imwrite(output_path, frame)
            print(f"Fotografía guardada en: {output_path}")

        elif key == ord("q"):
            print("Cerrando cámara...")
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
