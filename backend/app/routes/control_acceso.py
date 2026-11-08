from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile
)

from backend.services.access_event_service import (
    process_access_event
)

from backend.services.liveness_service import (
    analyze_liveness
)

from backend.services.recognition_service import (
    recognize_face
)


router = APIRouter(
    prefix=
        "/api/control-acceso",

    tags=[
        "Control de acceso"
    ]
)


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
# LEER Y VALIDAR IMAGEN
# =============================================

async def read_image(
    imagen: UploadFile
):

    if (
        imagen.content_type
        not in ALLOWED_CONTENT_TYPES
    ):

        raise HTTPException(
            status_code=
                400,

            detail=(
                "El archivo enviado "
                "debe ser una imagen."
            )
        )


    content = (
        await imagen.read()
    )


    if not content:

        raise HTTPException(
            status_code=
                400,

            detail=(
                "La imagen está vacía."
            )
        )


    if (
        len(content)
        >
        MAX_IMAGE_SIZE
    ):

        raise HTTPException(
            status_code=
                400,

            detail=(
                "La imagen supera "
                "el límite de 5 MB."
            )
        )


    return content


# =============================================
# RECONOCIMIENTO PRELIMINAR
# =============================================

@router.post(
    "/reconocer"
)
async def recognize_access_frame(
    imagen:
        UploadFile
        =
        File(...)
):

    content = (
        await read_image(
            imagen
        )
    )


    try:

        return (
            recognize_face(
                content
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=
                400,

            detail=
                str(
                    error
                )
        )


    except Exception as error:

        print(
            "ERROR EN RECONOCIMIENTO:"
        )

        print(
            error
        )


        raise HTTPException(
            status_code=
                500,

            detail=(
                "No fue posible procesar "
                "el reconocimiento facial."
            )
        )


# =============================================
# PRUEBA DE VIDA
# =============================================

@router.post(
    "/liveness"
)
async def liveness_check(
    imagen:
        UploadFile
        =
        File(...)
):

    content = (
        await read_image(
            imagen
        )
    )


    try:

        return (
            analyze_liveness(
                content
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=
                400,

            detail=
                str(
                    error
                )
        )


    except Exception as error:

        print(
            "ERROR EN PRUEBA DE VIDA:"
        )

        print(
            error
        )


        raise HTTPException(
            status_code=
                500,

            detail=(
                "No fue posible realizar "
                "la prueba de vida."
            )
        )


# =============================================
# PROCESAR EVENTO CONFIRMADO
# =============================================

@router.post(
    "/procesar-evento"
)
async def process_confirmed_access(
    background_tasks:
        BackgroundTasks,

    imagen:
        UploadFile
        =
        File(...)
):

    content = (
        await read_image(
            imagen
        )
    )


    try:

        return (
            process_access_event(
                content,

                background_tasks=
                    background_tasks
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=
                400,

            detail=
                str(
                    error
                )
        )


    except Exception as error:

        print(
            "ERROR PROCESANDO EVENTO "
            "DE ACCESO:"
        )

        print(
            error
        )


        raise HTTPException(
            status_code=
                500,

            detail=(
                "No fue posible registrar "
                "el evento de acceso."
            )
        )