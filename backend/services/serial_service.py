import os
import threading
import time

from pathlib import Path

import serial

from dotenv import load_dotenv


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


SERIAL_ENABLED = (
    os.getenv(
        "SERIAL_ENABLED",
        "true"
    )
    .strip()
    .lower()
    in {
        "true",
        "1",
        "yes",
        "si"
    }
)


SERIAL_PORT = (
    os.getenv(
        "SERIAL_PORT",
        "/dev/ttyUSB0"
    )
)


SERIAL_BAUDRATE = int(
    os.getenv(
        "SERIAL_BAUDRATE",
        "115200"
    )
)


SERIAL_TIMEOUT = float(
    os.getenv(
        "SERIAL_TIMEOUT",
        "1"
    )
)


# =============================================
# ESTADO INTERNO
# =============================================

_serial_connection = None

_serial_lock = threading.Lock()


# =============================================
# CERRAR CONEXION
# =============================================

def close_serial_connection():

    global _serial_connection

    if (
        _serial_connection
        is not None
    ):

        try:

            if (
                _serial_connection.is_open
            ):

                _serial_connection.close()

        except Exception:

            pass

    _serial_connection = None


# =============================================
# OBTENER CONEXION SERIAL
# =============================================

def get_serial_connection():

    global _serial_connection

    if not SERIAL_ENABLED:

        raise RuntimeError(
            "La comunicación Serial "
            "con el ESP32 está deshabilitada."
        )


    if (
        _serial_connection
        is not None
        and
        _serial_connection.is_open
    ):

        return _serial_connection


    _serial_connection = (
        serial.Serial(
            port=
                SERIAL_PORT,

            baudrate=
                SERIAL_BAUDRATE,

            timeout=
                SERIAL_TIMEOUT,

            write_timeout=
                SERIAL_TIMEOUT
        )
    )


    # Algunos ESP32 se reinician
    # cuando se abre el puerto Serial.
    time.sleep(2)


    try:

        _serial_connection.reset_input_buffer()
        _serial_connection.reset_output_buffer()

    except Exception:

        pass


    return _serial_connection


# =============================================
# ESPERAR RESPUESTA
# =============================================

def wait_for_response(
    connection,
    expected_response,
    timeout_seconds=2
):

    end_time = (
        time.time()
        + timeout_seconds
    )


    received_lines = []


    while (
        time.time()
        < end_time
    ):

        raw_line = (
            connection.readline()
        )


        if not raw_line:

            continue


        line = (
            raw_line
            .decode(
                "utf-8",
                errors="ignore"
            )
            .strip()
        )


        if not line:

            continue


        received_lines.append(
            line
        )


        if (
            line
            == expected_response
        ):

            return {
                "ok":
                    True,

                "respuesta":
                    line,

                "lineas":
                    received_lines
            }


    return {
        "ok":
            False,

        "respuesta":
            None,

        "lineas":
            received_lines
    }


# =============================================
# PROBAR ESP32
# =============================================

def ping_esp32():

    with _serial_lock:

        try:

            connection = (
                get_serial_connection()
            )


            connection.reset_input_buffer()


            connection.write(
                b"PING\n"
            )


            connection.flush()


            response = (
                wait_for_response(
                    connection=
                        connection,

                    expected_response=
                        "PONG",

                    timeout_seconds=
                        2
                )
            )


            if (
                response["ok"]
            ):

                return {
                    "ok":
                        True,

                    "mensaje":
                        (
                            "ESP32 respondió "
                            "correctamente."
                        ),

                    "respuesta":
                        "PONG",

                    "puerto":
                        SERIAL_PORT
                }


            return {
                "ok":
                    False,

                "mensaje":
                    (
                        "El ESP32 no respondió "
                        "al comando PING."
                    ),

                "respuestas":
                    response["lineas"],

                "puerto":
                    SERIAL_PORT
            }


        except Exception as error:

            close_serial_connection()


            return {
                "ok":
                    False,

                "mensaje":
                    str(error),

                "puerto":
                    SERIAL_PORT
            }


# =============================================
# ABRIR PUERTA
# =============================================

def open_door():

    with _serial_lock:

        try:

            connection = (
                get_serial_connection()
            )


            # Limpiamos cualquier respuesta
            # pendiente de la operación anterior.
            connection.reset_input_buffer()


            connection.write(
                b"OPEN\n"
            )


            connection.flush()


            response = (
                wait_for_response(
                    connection=
                        connection,

                    expected_response=
                        "OPENING",

                    timeout_seconds=
                        2
                )
            )


            if (
                response["ok"]
            ):

                print(
                    "SERIAL -> OPEN enviado "
                    f"a {SERIAL_PORT}"
                )


                return {
                    "ok":
                        True,

                    "mensaje":
                        (
                            "Orden de apertura "
                            "confirmada por el ESP32."
                        ),

                    "respuesta":
                        "OPENING",

                    "puerto":
                        SERIAL_PORT
                }


            return {
                "ok":
                    False,

                "mensaje":
                    (
                        "El ESP32 no confirmó "
                        "la orden de apertura."
                    ),

                "respuestas":
                    response["lineas"],

                "puerto":
                    SERIAL_PORT
            }


        except Exception as error:

            close_serial_connection()


            return {
                "ok":
                    False,

                "mensaje":
                    str(error),

                "puerto":
                    SERIAL_PORT
            }