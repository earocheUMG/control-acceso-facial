import sys
import os
from pathlib import Path

from dotenv import load_dotenv


# =============================================
# RUTA RAIZ DEL PROYECTO
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

sys.path.insert(
    0,
    str(ROOT_DIR)
)

load_dotenv(
    ROOT_DIR / ".env"
)


from backend.services.email_service import (
    send_email
)


# =============================================
# PRUEBA DE CORREO
# =============================================

def main():

    recipient = os.getenv(
        "SECURITY_EMAIL"
    )

    if not recipient:

        print(
            "ERROR: "
            "SECURITY_EMAIL no configurado."
        )

        return

    print(
        "======================================"
    )

    print(
        "       PRUEBA DE CORREO SMTP"
    )

    print(
        "======================================"
    )

    print("")

    print(
        f"Destinatario: {recipient}"
    )

    print("")

    print(
        "Enviando correo de prueba..."
    )

    try:

        send_email(
            recipient=recipient,
            subject=(
                "Prueba - "
                "Control de Acceso Facial"
            ),
            body=(
                "Esta es una prueba del módulo "
                "de notificaciones del Sistema "
                "de Control de Acceso Facial.\n\n"
                "Si recibió este mensaje, "
                "la configuración SMTP funciona "
                "correctamente."
            )
        )

        print("")

        print(
            "CORREO ENVIADO CORRECTAMENTE"
        )

    except Exception as error:

        print("")

        print(
            "ERROR ENVIANDO CORREO:"
        )

        print(
            error
        )


if __name__ == "__main__":
    main()