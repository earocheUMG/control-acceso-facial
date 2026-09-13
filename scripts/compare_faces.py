import cv2
import numpy as np
import onnxruntime as ort
import os


MODEL_PATH = "models/mobilefacenet/w600k_mbf.onnx"

IMAGE_1 = "data/faces/001/sample_01.jpg"
IMAGE_2 = "data/faces/002/sample_10.jpg"


def preprocess_face(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"No se pudo cargar la imagen: {image_path}"
        )

    image = cv2.resize(
        image,
        (112, 112)
    )

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

    image = np.expand_dims(
        image,
        axis=0
    )

    return image


def get_embedding(session, image_path):
    input_info = session.get_inputs()[0]
    output_info = session.get_outputs()[0]

    face = preprocess_face(
        image_path
    )

    result = session.run(
        [output_info.name],
        {
            input_info.name: face
        }
    )

    embedding = result[0].flatten()

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        raise ValueError(
            "El embedding tiene norma cero."
        )

    embedding = (
        embedding / norm
    )

    return embedding


def cosine_similarity(embedding_1, embedding_2):
    return np.dot(
        embedding_1,
        embedding_2
    )


def euclidean_distance(embedding_1, embedding_2):
    return np.linalg.norm(
        embedding_1 - embedding_2
    )


def main():

    print("======================================")
    print("      COMPARACION FACIAL")
    print("======================================")

    if not os.path.exists(MODEL_PATH):
        print(
            f"ERROR: No existe el modelo: {MODEL_PATH}"
        )
        return

    if not os.path.exists(IMAGE_1):
        print(
            f"ERROR: No existe: {IMAGE_1}"
        )
        return

    if not os.path.exists(IMAGE_2):
        print(
            f"ERROR: No existe: {IMAGE_2}"
        )
        return

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    print("")
    print(f"Imagen 1: {IMAGE_1}")
    print(f"Imagen 2: {IMAGE_2}")

    embedding_1 = get_embedding(
        session,
        IMAGE_1
    )

    embedding_2 = get_embedding(
        session,
        IMAGE_2
    )

    similarity = cosine_similarity(
        embedding_1,
        embedding_2
    )

    distance = euclidean_distance(
        embedding_1,
        embedding_2
    )

    print("")
    print(
        f"Similitud coseno: "
        f"{similarity:.4f}"
    )

    print(
        f"Distancia euclidiana: "
        f"{distance:.4f}"
    )

    print("")
    print("Comparación finalizada.")


if __name__ == "__main__":
    main()