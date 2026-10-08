from fastapi import APIRouter

from backend.database.connection import get_connection


router = APIRouter(
    prefix="/health",
    tags=["Health"]
)


@router.get("")
def health():
    return {
        "status": "ok",
        "system": "Control de Acceso Facial"
    }


@router.get("/database")
def database_health():

    try:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        current_database()
                        AS database,
                        current_user
                        AS user,
                        NOW()
                        AS server_time;
                    """
                )

                result = cursor.fetchone()

        return {
            "status": "ok",
            "database": result["database"],
            "user": result["user"],
            "server_time": result["server_time"]
        }

    except Exception as error:

        return {
            "status": "error",
            "detail": str(error)
        }