import cv2
import numpy as np
import onnxruntime as ort
import os


MODEL_PATH = "models/mobilefacenet/w600k_mbf.onnx"
PERSON_DIR = "data/faces/002"


def preprocess_face(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError(f"No se pudo cargar: {image_path}")

    image = cv2.resize(image, (112, 112))
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = image.astype(np.float32)

    image = (image - 127.5) / 127.5

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

    face = preprocess_face(image_path)

    result = session.run(
        [output_info.name],
        {
            input_info.name: face
        }
    )

    embedding = result[0].flatten()

    return embedding / np.linalg.norm(embedding)


def main():
    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    files = sorted([
        file
        for file in os.listdir(PERSON_DIR)
        if file.lower().endswith(
            (".jpg", ".jpeg", ".png")
        )
    ])

    embeddings = {}

    print("Generando embeddings...")

    for file in files:
        path = os.path.join(
            PERSON_DIR,
            file
        )

        embeddings[file] = get_embedding(
            session,
            path
        )

    results = []

    for file_1 in files:

        similarities = []

        for file_2 in files:

            if file_1 == file_2:
                continue

            similarity = float(
                np.dot(
                    embeddings[file_1],
                    embeddings[file_2]
                )
            )

            similarities.append(
                similarity
            )

        average = np.mean(
            similarities
        )

        minimum = np.min(
            similarities
        )

        results.append(
            (
                file_1,
                average,
                minimum
            )
        )

    results.sort(
        key=lambda x: x[1]
    )

    print("")
    print("======================================")
    print("     CALIDAD DE LAS MUESTRAS")
    print("======================================")
    print("")

    for file, average, minimum in results:

        print(
            f"{file:15} "
            f"Promedio: {average:.4f}   "
            f"Mínimo: {minimum:.4f}"
        )

    print("")
    print("======================================")
    print("      PEORES COMPARACIONES")
    print("======================================")

    comparisons = []

    for i in range(len(files)):

        for j in range(i + 1, len(files)):

            similarity = float(
                np.dot(
                    embeddings[files[i]],
                    embeddings[files[j]]
                )
            )

            comparisons.append(
                (
                    similarity,
                    files[i],
                    files[j]
                )
            )

    comparisons.sort(
        key=lambda x: x[0]
    )

    for similarity, file_1, file_2 in comparisons[:10]:

        print(
            f"{file_1} vs {file_2}: "
            f"{similarity:.4f}"
        )


if __name__ == "__main__":
    main()