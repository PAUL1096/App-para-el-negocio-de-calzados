"""
Script para inicializar la base de datos y datos iniciales
Compatible con SQLite (desarrollo) y PostgreSQL (produccion/Render)
"""

from database import init_database, insert_initial_data, is_postgres
from config import get_config

config = get_config()


def main():
    """Inicializa la base de datos y datos iniciales"""

    print("\n" + "="*70)
    print(" INICIALIZACION DE BASE DE DATOS")
    print("="*70 + "\n")

    # Mostrar tipo de base de datos
    if is_postgres():
        print("Tipo: PostgreSQL (produccion)")
        print(f"URL: {config.DATABASE_URL[:50]}..." if len(config.DATABASE_URL) > 50 else f"URL: {config.DATABASE_URL}")
    else:
        print("Tipo: SQLite (desarrollo)")
        print(f"Archivo: {config.SQLITE_PATH}")

    print("\n" + "-"*70)

    try:
        # Crear tablas
        print("\n1. Creando tablas...")
        init_database()

        # Insertar datos iniciales
        print("\n2. Insertando datos iniciales...")
        insert_initial_data()

        print("\n" + "="*70)
        print(" INICIALIZACION COMPLETADA")
        print("="*70)

        print("\nEl sistema esta listo para usar:")
        print("  1. Crear variantes base (modelos) en /catalogo-variantes")
        print("  2. Producir productos en /produccion")
        print("  3. Ingresar a inventario")
        print("  4. Crear clientes (opcional)")
        print("  5. Realizar ventas")
        print("\n")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        raise


if __name__ == "__main__":
    main()
