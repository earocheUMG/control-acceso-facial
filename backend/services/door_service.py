import os
import uuid

from pathlib import Path

from dotenv import load_dotenv

import paho.mqtt.publish as publish


# =============================================
# CONFIGURACION
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


MQTT_ENABLED = (
    os.getenv(
        "MQTT_ENABLED",
        "false"
    )
    .strip()
    .lower()
    == "true"
)


MQTT_BROKER = (
    os.getenv(
        "MQTT_BROKER",
        "35.159.8.6"
    )
)


MQTT_PORT = int(
    os.getenv(
        "MQTT_PORT",
        "1883"
    )
)


MQTT_TOPIC = (
    os.getenv(
        "MQTT_TOPIC",
        "umg/control-acceso-facial/7f3c91e2/door"
    )
)


MQTT_QOS = int(
    os.getenv(
        "MQTT_QOS",
        "1"
    )
)


# =============================================
# ENVIAR COMANDO
# =============================================

def send_door_command(
    command: str
):

    if not MQTT_ENABLED:

        return {
            "enviado":
                False,

            "estado":
                "DESHABILITADO",

            "comando":
                command,

            "detalle":
                "MQTT está deshabilitado."
        }


    client_id = (
        "backend-control-facial-"
        + uuid.uuid4().hex[:8]
    )


    try:

        publish.single(
            topic=
                MQTT_TOPIC,

            payload=
                command,

            qos=
                MQTT_QOS,

            retain=
                False,

            hostname=
                MQTT_BROKER,

            port=
                MQTT_PORT,

            client_id=
                client_id,

            keepalive=
                10
        )


        print(
            f"MQTT -> {command} "
            f"enviado a {MQTT_TOPIC}"
        )


        return {
            "enviado":
                True,

            "estado":
                "ENVIADO",

            "comando":
                command,

            "broker":
                MQTT_BROKER,

            "puerto":
                MQTT_PORT,

            "topic":
                MQTT_TOPIC
        }


    except Exception as error:

        print(
            "ERROR enviando comando MQTT:"
        )

        print(
            error
        )


        return {
            "enviado":
                False,

            "estado":
                "ERROR",

            "comando":
                command,

            "detalle":
                str(error)
        }


# =============================================
# ABRIR PUERTA
# =============================================

def open_door():

    return (
        send_door_command(
            "OPEN"
        )
    )