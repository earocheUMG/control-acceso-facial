import cv2
import numpy as np
import onnxruntime as ort
import os
from itertools import combinations


MODEL_PATH = "models/mobilefacenet/w600k_mbf.onnx"

PERSON_1_DIR = "data/faces_aligned/001"
PERSON_2_DIR = "data/faces_aligned/002"


def preprocess_face(image_path):

    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(
            f"No se pudo cargar: {image_path}"
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
            "Embedding con norma cero."
        )

    return embedding / norm


def cosine_similarity(embedding_1, embedding_2):

    return float(
        np.dot(
            embedding_1,
            embedding_2
        )
    )


def load_embeddings(session, directory):

    embeddings = []

    files = sorted(
        [
            file
            for file in os.listdir(directory)
            if file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ]
    )

    for file in files:

        path = os.path.join(
            directory,
            file
        )

        embedding = get_embedding(
            session,
            path
        )

        embeddings.append(
            (file, embedding)
        )

    return embeddings


def analyze_same_person(embeddings):

    results = []

    for (
        (file_1, embedding_1),
        (file_2, embedding_2)
    ) in combinations(embeddings, 2):

        similarity = cosine_similarity(
            embedding_1,
            embedding_2
        )

        results.append(
            (
                file_1,
                file_2,
                similarity
            )
        )

    return results


def analyze_different_people(
    embeddings_1,
    embeddings_2
):

    results = []

    for file_1, embedding_1 in embeddings_1:

        for file_2, embedding_2 in embeddings_2:

            similarity = cosine_similarity(
                embedding_1,
                embedding_2
            )

            results.append(
                (
                    file_1,
                    file_2,
                    similarity
                )
            )

    return results


def print_statistics(title, results):

    values = np.array(
        [
            result[2]
            for result in results
        ]
    )

    print("")
    print(title)
    print("-" * len(title))

    print(
        f"Comparaciones: {len(values)}"
    )

    print(
        f"Promedio: {np.mean(values):.4f}"
    )

    print(
        f"Mínimo:   {np.min(values):.4f}"
    )

    print(
        f"Máximo:   {np.max(values):.4f}"
    )

    print(
        f"Desv. est.: {np.std(values):.4f}"
    )

    return values


def main():

    print("======================================")
    print("   ANALISIS DE SIMILITUD FACIAL")
    print("======================================")

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    print("")
    print("Generando embeddings...")

    person_1 = load_embeddings(
        session,
        PERSON_1_DIR
    )

    person_2 = load_embeddings(
        session,
        PERSON_2_DIR
    )

    print(
        f"Persona 001: {len(person_1)} muestras"
    )

    print(
        f"Persona 002: {len(person_2)} muestras"
    )

    same_1 = analyze_same_person(
        person_1
    )

    same_2 = analyze_same_person(
        person_2
    )

    different = analyze_different_people(
        person_1,
        person_2
    )

    values_1 = print_statistics(
        "Persona 001 vs Persona 001",
        same_1
    )

    values_2 = print_statistics(
        "Persona 002 vs Persona 002",
        same_2
    )

    different_values = print_statistics(
        "Persona 001 vs Persona 002",
        different
    )

    genuine_values = np.concatenate(
        [
            values_1,
            values_2
        ]
    )

    min_genuine = np.min(
        genuine_values
    )

    max_impostor = np.max(
        different_values
    )

    print("")
    print("======================================")
    print("   SEPARACION ENTRE IDENTIDADES")
    print("======================================")

    print(
        f"Mínima similitud misma persona: "
        f"{min_genuine:.4f}"
    )

    print(
        f"Máxima similitud personas distintas: "
        f"{max_impostor:.4f}"
    )

    gap = (
        min_genuine
        - max_impostor
    )

    print(
        f"Separación encontrada: "
        f"{gap:.4f}"
    )

    if min_genuine > max_impostor:

        tentative_threshold = (
            min_genuine
            + max_impostor
        ) / 2

        print("")
        print(
            "Existe separación entre los "
            "dos grupos."
        )

        print(
            f"Umbral experimental sugerido: "
            f"{tentative_threshold:.4f}"
        )

        print("")
        print(
            "IMPORTANTE: este umbral todavía "
            "NO debe considerarse definitivo."
        )

    else:

        print("")
        print(
            "Existe superposición entre "
            "las comparaciones."
        )

        print(
            "Se necesitan más pruebas antes "
            "de definir un umbral."
        )


if __name__ == "__main__":
    main()