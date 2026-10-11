import os

from datetime import (
    datetime,
    timedelta,
    timezone
)

import jwt

from dotenv import load_dotenv
from pwdlib import PasswordHash


# =============================================
# VARIABLES DE ENTORNO
# =============================================

load_dotenv()


JWT_SECRET = os.getenv(
    "JWT_SECRET"
)


JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)


JWT_EXPIRE_MINUTES = int(
    os.getenv(
        "JWT_EXPIRE_MINUTES",
        "480"
    )
)


if not JWT_SECRET:

    raise RuntimeError(
        "JWT_SECRET no está configurado "
        "en el archivo .env."
    )


# =============================================
# HASH DE CONTRASEÑAS
# =============================================

password_hash = (
    PasswordHash.recommended()
)


# =============================================
# CREAR HASH
# =============================================

def hash_password(
    password: str
):

    return password_hash.hash(
        password
    )


# =============================================
# VERIFICAR CONTRASEÑA
# =============================================

def verify_password(
    password: str,
    stored_hash: str
):

    try:

        return password_hash.verify(
            password,
            stored_hash
        )

    except Exception:

        return False


# =============================================
# CREAR JWT
# =============================================

def create_access_token(
    user_id: int,
    username: str,
    role: str
):

    now = datetime.now(
        timezone.utc
    )


    expires = (
        now
        + timedelta(
            minutes=
                JWT_EXPIRE_MINUTES
        )
    )


    payload = {
        "sub":
            str(user_id),

        "usuario":
            username,

        "rol":
            role,

        "iat":
            now,

        "exp":
            expires
    }


    return jwt.encode(
        payload,
        JWT_SECRET,
        algorithm=
            JWT_ALGORITHM
    )


# =============================================
# DECODIFICAR JWT
# =============================================

def decode_access_token(
    token: str
):

    try:

        return jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[
                JWT_ALGORITHM
            ]
        )

    except jwt.ExpiredSignatureError:

        return None

    except jwt.InvalidTokenError:

        return None