import os
import smtplib
from pathlib import Path
from email.message import EmailMessage

from dotenv import load_dotenv


# =============================================
# RUTA RAIZ DEL PROYECTO
# =============================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

load_dotenv(
    ROOT_DIR / ".env"
)


# =============================================
# CONFIGURACION SMTP
# =============================================

SMTP_HOST = os.getenv(
    "SMTP_HOST"
)

SMTP_PORT = int(
    os.getenv(
        "SMTP_PORT",
        "587"
    )
)

SMTP_USER = os.getenv(
    "SMTP_USER"
)

SMTP_PASSWORD = os.getenv(
    "SMTP_PASSWORD"
)

SMTP_FROM = os.getenv(
    "SMTP_FROM",
    SMTP_USER
)

SECURITY_EMAIL = os.getenv(
    "SECURITY_EMAIL"
)


# =============================================
# ENVIO GENERICO DE CORREO
# =============================================

def send_email(
    recipient,
    subject,
    body,
    attachment_path=None,
    bcc=None
):

    if not SMTP_HOST:
        raise ValueError(
            "SMTP_HOST no configurado."
        )

    if not SMTP_USER:
        raise ValueError(
            "SMTP_USER no configurado."
        )

    if not SMTP_PASSWORD:
        raise ValueError(
            "SMTP_PASSWORD no configurado."
        )

    if not recipient:
        raise ValueError(
            "Destinatario no configurado."
        )

    message = EmailMessage()

    message["From"] = SMTP_FROM
    message["To"] = recipient
    message["Subject"] = subject

    # =========================================
    # COPIA OCULTA
    # =========================================

    if bcc:
        message["Bcc"] = bcc

    message.set_content(
        body
    )

    # =========================================
    # ARCHIVO ADJUNTO
    # =========================================

    if attachment_path:

        path = Path(
            attachment_path
        )

        # Si la ruta es relativa,
        # buscar desde la raíz del proyecto
        if not path.is_absolute():

            path = (
                ROOT_DIR
                / path
            )

        if path.exists():

            with open(
                path,
                "rb"
            ) as file:

                image_data = file.read()

            message.add_attachment(
                image_data,
                maintype="image",
                subtype="jpeg",
                filename=path.name
            )

        else:

            print(
                f"ADVERTENCIA: "
                f"No existe el adjunto: {path}"
            )

    # =========================================
    # CONEXION SMTP
    # =========================================

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=20
    ) as smtp:

        smtp.ehlo()

        smtp.starttls()

        smtp.ehlo()

        smtp.login(
            SMTP_USER,
            SMTP_PASSWORD
        )

        smtp.send_message(
            message
        )


# =============================================
# CORREO DE ACCESO AUTORIZADO
# =============================================

def send_authorized_access_email(
    recipient,
    visitor_name,
    visitor_type,
    house,
    access_point,
    access_date
):

    subject = (
        "Acceso autorizado"
    )

    body = f"""
Sistema de Control de Acceso Facial

Se informa que:

{visitor_name}

ha sido autorizado para ingresar.

Tipo: {visitor_type}
Vivienda: {house}
Punto de acceso: {access_point}
Fecha y hora: {access_date}

Este mensaje fue generado automáticamente
por el Sistema de Control de Acceso Facial.
""".strip()

    send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        bcc=SECURITY_EMAIL
    )


# =============================================
# CORREO DE ALERTA A SEGURIDAD
# =============================================

def send_security_alert_email(
    recipient,
    access_point,
    similarity,
    access_date,
    evidence_path=None
):

    subject = (
        "ALERTA DE SEGURIDAD - "
        "Acceso rechazado"
    )

    body = f"""
Sistema de Control de Acceso Facial

Se detectó una persona no registrada.

El acceso fue RECHAZADO.

Punto de acceso: {access_point}
Fecha y hora: {access_date}
Similitud máxima registrada: {similarity:.3f}

Se recomienda verificar el evento.

La evidencia del intento se encuentra
adjunta a este correo.

Este mensaje fue generado automáticamente
por el Sistema de Control de Acceso Facial.
""".strip()

    send_email(
        recipient=recipient,
        subject=subject,
        body=body,
        attachment_path=evidence_path
    )