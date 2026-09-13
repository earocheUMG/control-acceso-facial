import cv2
import numpy as np
import onnxruntime as ort
import os


MODEL_PATH = "models/mobilefacenet/w600k_mbf.onnx"
IMAGE_PATH = "data/faces/001/sample_01.jpg"


def preprocess_face(image_path):
    """
    Prepara una imagen facial para MobileFaceNet.
    """

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"No se pudo cargar la imagen: {image_path}"
        )

    # MobileFaceNet trabaja con rostros de 112x112
    image = cv2.resize(
        image,
        (112, 112)
    )

    # OpenCV carga BGR; el modelo espera RGB
    image = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    # Convertir a float32
    image = image.astype(np.float32)

    # Normalización
    image = (image - 127.5) / 127.5

    # HWC -> CHW
    image = np.transpose(
        image,
        (2, 0, 1)
    )

    # Agregar dimensión batch
    image = np.expand_dims(
        image,
        axis=0
    )

    return image


def main():

    print("======================================")
    print("     PRUEBA MOBILEFACENET")
    print("======================================")

    if not os.path.exists(MODEL_PATH):
        print(
            f"ERROR: No existe el modelo: {MODEL_PATH}"
        )
        return

    if not os.path.exists(IMAGE_PATH):
        print(
            f"ERROR: No existe la imagen: {IMAGE_PATH}"
        )
        return

    print(f"Modelo: {MODEL_PATH}")
    print(f"Imagen: {IMAGE_PATH}")
    print("")

    # Crear sesión ONNX
    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    input_info = session.get_inputs()[0]
    output_info = session.get_outputs()[0]

    print("Información del modelo:")
    print(f"Entrada: {input_info.name}")
    print(f"Forma de entrada: {input_info.shape}")
    print(f"Salida: {output_info.name}")
    print(f"Forma de salida: {output_info.shape}")
    print("")

    face = preprocess_face(
        IMAGE_PATH
    )

    print(
        f"Forma de la imagen preparada: "
        f"{face.shape}"
    )

    # Ejecutar MobileFaceNet
    result = session.run(
        [output_info.name],
        {
            input_info.name: face
        }
    )

    embedding = result[0].flatten()

    print(
        f"Embedding generado: "
        f"{embedding.shape}"
    )

    # Normalización L2
    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        print(
            "ERROR: El embedding tiene norma cero."
        )
        return

    embedding = embedding / norm

    print("")
    print("Primeros 10 valores:")
    print(embedding[:10])

    print("")
    print(
        f"Norma final: "
        f"{np.linalg.norm(embedding):.6f}"
    )

    print("")
    print(
        "MobileFaceNet ejecutado correctamente."
    )


if __name__ == "__main__":
    main()