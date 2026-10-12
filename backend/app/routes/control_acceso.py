from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Request,
    UploadFile
)

from backend.services.access_event_service import (
    process_access_event
)

from backend.services.recognition_service import (
    recognize_face
)


router = APIRouter(
    prefix="/api/control-acceso",
    tags=["Control de acceso"]
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


LOCAL_TERMINAL_HOSTS = {
    "127.0.0.1",
    "::1"
}


# =============================================
# VALIDAR TERMINAL LOCAL
# =============================================

def validate_local_terminal(
    request: Request
):

    client = request.client


    if client is None:

        raise HTTPException(
            status_code=403,
            detail=(
                "No fue posible identificar "
                "el terminal de acceso."
            )
        )


    if (
        client.host
        not in LOCAL_TERMINAL_HOSTS
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "El servicio de control de acceso "
                "solo está disponible para el "
                "terminal local autorizado."
            )
        )


    return client.host


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
            status_code=400,
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
            status_code=400,
            detail=(
                "La imagen está vacía."
            )
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


    return content


# =============================================
# RECONOCIMIENTO PRELIMINAR
# =============================================

@router.post(
    "/reconocer"
)
async def recognize_access_frame(
    imagen: UploadFile = File(...),
    _terminal=
        Depends(
            validate_local_terminal
        )
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
            status_code=400,
            detail=str(error)
        )


    except Exception:

        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible procesar "
                "el reconocimiento facial."
            )
        )


# =============================================
# PROCESAR EVENTO CONFIRMADO
# =============================================

@router.post(
    "/procesar-evento"
)
async def process_confirmed_access(
    imagen: UploadFile = File(...),
    _terminal=
        Depends(
            validate_local_terminal
        )
):

    content = (
        await read_image(
            imagen
        )
    )


    try:

        return (
            process_access_event(
                content
            )
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


    except Exception as error:

        print(
            "ERROR PROCESANDO EVENTO "
            "DE ACCESO:"
        )

        print(error)


        raise HTTPException(
            status_code=500,
            detail=(
                "No fue posible registrar "
                "el evento de acceso."
            )
        )
