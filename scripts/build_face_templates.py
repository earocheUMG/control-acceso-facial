import cv2
import numpy as np
import onnxruntime as ort
import os


MODEL_PATH = "models/mobilefacenet/w600k_mbf.onnx"

FACES_DIR = "data/faces_aligned"
TEMPLATES_DIR = "data/templates"


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


def get_embedding(
    session,
    image_path
):

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

    embedding = (
        result[0]
        .flatten()
        .astype(np.float32)
    )

    norm = np.linalg.norm(
        embedding
    )

    if norm == 0:
        raise ValueError(
            f"Embedding inválido: {image_path}"
        )

    return embedding / norm


def create_template(
    session,
    person_dir
):

    files = sorted(
        [
            file
            for file in os.listdir(person_dir)
            if file.lower().endswith(
                (".jpg", ".jpeg", ".png")
            )
        ]
    )

    embeddings = []

    for file in files:

        path = os.path.join(
            person_dir,
            file
        )

        embedding = get_embedding(
            session,
            path
        )

        embeddings.append(
            embedding
        )

    if not embeddings:
        raise ValueError(
            f"No hay imágenes en {person_dir}"
        )

    embeddings = np.array(
        embeddings
    )

    # Centro biométrico de la persona
    template = np.mean(
        embeddings,
        axis=0
    )

    # Normalizar nuevamente el promedio
    template_norm = np.linalg.norm(
        template
    )

    if template_norm == 0:
        raise ValueError(
            "La plantilla resultó inválida."
        )

    template = (
        template / template_norm
    )

    return (
        template.astype(np.float32),
        embeddings,
        files
    )


def main():

    print("======================================")
    print("   CREACION DE PLANTILLAS BIOMETRICAS")
    print("======================================")

    os.makedirs(
        TEMPLATES_DIR,
        exist_ok=True
    )

    session = ort.InferenceSession(
        MODEL_PATH,
        providers=["CPUExecutionProvider"]
    )

    persons = sorted(
        [
            item
            for item in os.listdir(FACES_DIR)
            if os.path.isdir(
                os.path.join(
                    FACES_DIR,
                    item
                )
            )
        ]
    )

    if not persons:

        print(
            "ERROR: No hay personas enroladas."
        )

        return

    for person_id in persons:

        person_dir = os.path.join(
            FACES_DIR,
            person_id
        )

        print("")
        print(
            f"Procesando persona {person_id}..."
        )

        template, embeddings, files = (
            create_template(
                session,
                person_dir
            )
        )

        output_path = os.path.join(
            TEMPLATES_DIR,
            f"{person_id}.npy"
        )

        np.save(
            output_path,
            template
        )

        # Comprobar qué tan bien representa
        # la plantilla a sus muestras
        similarities = (
            embeddings @ template
        )

        print(
            f"Muestras utilizadas: "
            f"{len(files)}"
        )

        print(
            f"Similitud promedio con plantilla: "
            f"{np.mean(similarities):.4f}"
        )

        print(
            f"Similitud mínima con plantilla: "
            f"{np.min(similarities):.4f}"
        )

        print(
            f"Similitud máxima con plantilla: "
            f"{np.max(similarities):.4f}"
        )

        print(
            f"Plantilla guardada: "
            f"{output_path}"
        )

    print("")
    print("======================================")
    print("   PLANTILLAS CREADAS CORRECTAMENTE")
    print("======================================")


if __name__ == "__main__":
    main()