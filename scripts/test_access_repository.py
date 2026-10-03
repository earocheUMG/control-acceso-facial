import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))


from backend.database.access_repository import (
    get_active_people,
    get_access_point
)


def main():

    print("======================================")
    print("     DATOS PARA CONTROL DE ACCESO")
    print("======================================")

    personas = get_active_people()

    print("")
    print(
        f"Personas activas: {len(personas)}"
    )

    for persona in personas:

        print("")
        print(
            "----------------------------------"
        )

        print(
            f"ID BD: {persona['id']}"
        )

        print(
            f"Codigo: "
            f"{persona['codigo_biometrico']}"
        )

        print(
            f"Nombre: "
            f"{persona['nombre_completo']}"
        )

        print(
            f"Tipo: {persona['tipo']}"
        )

        print(
            f"Vivienda(s): "
            f"{persona['viviendas']}"
        )

        print(
            f"Template: "
            f"{persona['template_path']}"
        )

    punto = get_access_point()

    print("")
    print("======================================")
    print("PUNTO DE ACCESO")
    print("======================================")

    if punto:

        print(
            f"ID: {punto['id']}"
        )

        print(
            f"Nombre: {punto['nombre']}"
        )

        print(
            f"Ubicacion: {punto['ubicacion']}"
        )

    else:

        print(
            "No existe un punto de acceso activo."
        )


if __name__ == "__main__":
    main()