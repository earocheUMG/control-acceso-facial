import sys
from pathlib import Path


# Agregar raíz del proyecto al path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


from backend.database.connection import get_connection


def main():

    print("======================================")
    print("   PRUEBA DE CONEXION POSTGRESQL")
    print("======================================")

    try:

        with get_connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        p.id,
                        p.codigo_biometrico,
                        p.nombre_completo,
                        p.tipo,
                        p.activo,
                        v.codigo AS vivienda,
                        b.modelo,
                        b.template_path
                    FROM personas p

                    LEFT JOIN persona_vivienda pv
                        ON pv.persona_id = p.id
                        AND pv.activo = TRUE

                    LEFT JOIN viviendas v
                        ON v.id = pv.vivienda_id

                    LEFT JOIN biometria b
                        ON b.persona_id = p.id
                        AND b.activo = TRUE

                    ORDER BY p.codigo_biometrico;
                    """
                )

                personas = cursor.fetchall()

                print("")
                print("Conexion exitosa.")
                print(
                    f"Personas encontradas: {len(personas)}"
                )
                print("")

                for persona in personas:

                    print(
                        "----------------------------------"
                    )

                    print(
                        f"ID BD: "
                        f"{persona['id']}"
                    )

                    print(
                        f"Codigo biometrico: "
                        f"{persona['codigo_biometrico']}"
                    )

                    print(
                        f"Nombre: "
                        f"{persona['nombre_completo']}"
                    )

                    print(
                        f"Tipo: "
                        f"{persona['tipo']}"
                    )

                    print(
                        f"Vivienda: "
                        f"{persona['vivienda']}"
                    )

                    print(
                        f"Modelo: "
                        f"{persona['modelo']}"
                    )

                    print(
                        f"Template: "
                        f"{persona['template_path']}"
                    )

    except Exception as error:

        print("")
        print("ERROR DE CONEXION:")
        print(error)


if __name__ == "__main__":
    main()