from pathlib import Path
import shutil

import cv2
import numpy as np

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile
)

from backend.database.biometric_repository import (
    get_next_biometric_code,
    get_person_for_enrollment,
    register_person_biometrics
)

from backend.services.biometric_enrollment_service import (
    process_enrollment_images,
    validate_enrollment_image
)


# =============================================
# ROUTER
# =============================================

router = APIRouter(
    prefix="/api/personas",
    tags=["Enrolamiento biométrico"]
)


# =============================================
# RUTAS DEL PROYECTO
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
    .parent
)


FACES_DIR = (
    ROOT_DIR
    / "data"
    / "faces_aligned"
)


TEMPLATES_DIR = (
    ROOT_DIR
    / "data"
    / "templates"
)


# =============================================
# CONFIGURACION
# =============================================

REQUIRED_SAMPLES = 10


MAX_IMAGE_SIZE = (
    5
    * 1024
    * 1024
)


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp"
}


# =============================================
# VALIDAR MUESTRA INDIVIDUAL
# =============================================

@router.post(
    "/{person_id}/enrolamiento/validar-muestra"
)
async def validate_sample(
    person_id: int,
    muestra: UploadFile = File(...)
):

    # =========================================
    # VALIDAR PERSONA
    # =========================================

    person = (
        get_person_for_enrollment(
            person_id
        )
    )


    if not person:

        raise HTTPException(
            status_code=404,
            detail="Persona no encontrada."
        )


    if not person["activo"]:

        raise HTTPException(
            status_code=400,
            detail=(
                "La persona está inactiva."
            )
        )


    if person["biometria_configurada"]:

        raise HTTPException(
            status_code=409,
            detail=(
                "La persona ya tiene "
                "biometría configurada."
            )
        )


    # =========================================
    # VALIDAR FORMATO
    # =========================================

    if (
        muestra.content_type
        not in ALLOWED_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser "
                "una imagen válida."
            )
        )


    # =========================================
    # LEER ARCHIVO
    # =========================================

    content = (
        await muestra.read()
    )


    if not content:

        raise HTTPException(
            status_code=400,
            detail="La imagen está vacía."
        )


    if (
        len(content)
        > MAX_IMAGE_SIZE
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "La imagen supera "
                "el límite de 5 MB."
            )
        )


    # =========================================
    # VALIDAR CON YUNET + MOBILEFACENET
    # =========================================

    try:

        result = (
            validate_enrollment_image(
                content
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # =========================================
    # RESPUESTA
    # =========================================

    return {
        "valida":
            True,

        "message":
            "Muestra facial válida.",

        "persona_id":
            person_id,

        "embedding_dimensions":
            result[
                "embedding_dimensions"
            ]
    }


# =============================================
# ENROLAR PERSONA
# =============================================

@router.post(
    "/{person_id}/enrolamiento"
)
async def enroll_person(
    person_id: int,
    muestras: list[UploadFile] = File(...)
):

    # =========================================
    # VALIDAR PERSONA
    # =========================================

    person = (
        get_person_for_enrollment(
            person_id
        )
    )


    if not person:

        raise HTTPException(
            status_code=404,
            detail="Persona no encontrada."
        )


    if not person["activo"]:

        raise HTTPException(
            status_code=400,
            detail=(
                "No puede enrolarse "
                "una persona inactiva."
            )
        )


    if person["biometria_configurada"]:

        raise HTTPException(
            status_code=409,
            detail=(
                "La persona ya tiene "
                "biometría configurada."
            )
        )


    # =========================================
    # VALIDAR CANTIDAD DE MUESTRAS
    # =========================================

    if (
        len(muestras)
        != REQUIRED_SAMPLES
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "El enrolamiento requiere "
                "exactamente 10 muestras."
            )
        )


    # =========================================
    # LEER IMAGENES
    # =========================================

    image_bytes_list = []


    for index, sample in enumerate(
        muestras,
        start=1
    ):

        # =====================================
        # VALIDAR FORMATO
        # =====================================

        if (
            sample.content_type
            not in ALLOWED_CONTENT_TYPES
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Muestra {index}: "
                    "formato de imagen "
                    "no permitido."
                )
            )


        # =====================================
        # LEER CONTENIDO
        # =====================================

        content = (
            await sample.read()
        )


        if not content:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Muestra {index}: "
                    "archivo vacío."
                )
            )


        # =====================================
        # VALIDAR TAMAÑO
        # =====================================

        if (
            len(content)
            > MAX_IMAGE_SIZE
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Muestra {index}: "
                    "la imagen supera "
                    "el límite de 5 MB."
                )
            )


        image_bytes_list.append(
            content
        )


    # =========================================
    # PROCESAR CON YUNET + MOBILEFACENET
    # =========================================

    try:

        result = (
            process_enrollment_images(
                image_bytes_list
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    # =========================================
    # DETERMINAR CODIGO BIOMETRICO
    # =========================================

    biometric_code = (
        person["codigo_biometrico"]
        or
        get_next_biometric_code()
    )


    # =========================================
    # PREPARAR RUTAS
    # =========================================

    person_dir = (
        FACES_DIR
        / biometric_code
    )


    template_file = (
        TEMPLATES_DIR
        / f"{biometric_code}.npy"
    )


    # =========================================
    # EVITAR SOBREESCRITURA
    # =========================================

    if person_dir.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                "Ya existen muestras "
                f"para el código "
                f"{biometric_code}."
            )
        )


    if template_file.exists():

        raise HTTPException(
            status_code=409,
            detail=(
                "Ya existe una plantilla "
                f"para el código "
                f"{biometric_code}."
            )
        )


    # =========================================
    # CREAR CARPETAS
    # =========================================

    FACES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    TEMPLATES_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    person_dir.mkdir(
        parents=True,
        exist_ok=False
    )


    # =========================================
    # GUARDAR ARCHIVOS
    # =========================================

    try:

        # =====================================
        # GUARDAR ROSTROS ALINEADOS
        # =====================================

        for index, aligned_face in enumerate(
            result["aligned_faces"],
            start=1
        ):

            sample_file = (
                person_dir
                / f"sample_{index:02d}.jpg"
            )


            saved = cv2.imwrite(
                str(sample_file),
                aligned_face
            )


            if not saved:

                raise RuntimeError(
                    "No fue posible guardar "
                    f"la muestra {index}."
                )


        # =====================================
        # GUARDAR TEMPLATE MOBILEFACENET
        # =====================================

        np.save(
            template_file,
            result["template"]
        )


        relative_template_path = (
            str(
                template_file.relative_to(
                    ROOT_DIR
                )
            )
        )


        # =====================================
        # ACTUALIZAR POSTGRESQL
        # =====================================

        register_person_biometrics(
            person_id=person_id,
            biometric_code=biometric_code,
            template_path=relative_template_path,
            sample_count=REQUIRED_SAMPLES
        )


    except Exception as error:

        # =====================================
        # LIMPIEZA SI ALGO FALLA
        # =====================================

        if person_dir.exists():

            shutil.rmtree(
                person_dir
            )


        if template_file.exists():

            template_file.unlink()


        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible completar "
                "el enrolamiento: "
                f"{error}"
            )
        )


    # =========================================
    # ESTADISTICAS DE CALIDAD
    # =========================================

    similarities = (
        result["similarities"]
    )


    # =========================================
    # RESPUESTA
    # =========================================

    return {
        "message":
            "Enrolamiento completado correctamente.",

        "persona": {
            "id":
                person["id"],

            "nombre_completo":
                person["nombre_completo"],

            "codigo_biometrico":
                biometric_code
        },

        "biometria": {
            "modelo":
                "MobileFaceNet",

            "muestras":
                REQUIRED_SAMPLES,

            "template_path":
                relative_template_path,

            "similitud_promedio":
                round(
                    float(
                        np.mean(
                            similarities
                        )
                    ),
                    4
                ),

            "similitud_minima":
                round(
                    float(
                        np.min(
                            similarities
                        )
                    ),
                    4
                ),

            "similitud_maxima":
                round(
                    float(
                        np.max(
                            similarities
                        )
                    ),
                    4
                )
        }
    }