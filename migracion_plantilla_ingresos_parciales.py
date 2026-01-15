"""
Migración: Plantilla y Control de Ingresos Parciales
=====================================================

Fecha: 2026-01-06
Objetivo:
1. Agregar campo 'material_plantilla' para registrar el material de la plantilla del calzado
2. Agregar campo 'cantidad_ingresada' para control de ingresos parciales al inventario

Cambios:
1. ALTER TABLE productos_producidos ADD COLUMN material_plantilla
2. ALTER TABLE productos_producidos ADD COLUMN cantidad_ingresada
3. Inicializar cantidad_ingresada con cantidad_pares (productos ya ingresados completamente)
"""

import sqlite3
from datetime import datetime

def migrar():
    print("=" * 70)
    print("MIGRACIÓN: Material de Plantilla + Ingresos Parciales")
    print("=" * 70)

    conn = sqlite3.connect('calzado.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("\n📋 Paso 1: Verificando tabla productos_producidos...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos_producidos'")
        existe_tabla = cursor.fetchone()

        if not existe_tabla:
            print("⚠️  La tabla 'productos_producidos' no existe")
            print("❌ Esta migración requiere que la tabla ya exista")
            conn.close()
            return

        print("✅ Tabla productos_producidos encontrada")

        print("\n📋 Paso 2: Verificando si las columnas ya existen...")

        cursor.execute("PRAGMA table_info(productos_producidos)")
        columnas = cursor.fetchall()
        nombres_columnas = [col['name'] for col in columnas]

        tiene_material_plantilla = 'material_plantilla' in nombres_columnas
        tiene_cantidad_ingresada = 'cantidad_ingresada' in nombres_columnas

        if tiene_material_plantilla and tiene_cantidad_ingresada:
            print("ℹ️  Las columnas ya existen. Migración no necesaria.")
            conn.close()
            return

        print("\n📋 Paso 3: Agregando nuevas columnas...")

        # Agregar material_plantilla si no existe
        if not tiene_material_plantilla:
            cursor.execute('''
                ALTER TABLE productos_producidos
                ADD COLUMN material_plantilla TEXT
            ''')
            print("✅ Columna 'material_plantilla' agregada")
        else:
            print("ℹ️  Columna 'material_plantilla' ya existe")

        # Agregar cantidad_ingresada si no existe
        if not tiene_cantidad_ingresada:
            cursor.execute('''
                ALTER TABLE productos_producidos
                ADD COLUMN cantidad_ingresada INTEGER DEFAULT 0
            ''')
            print("✅ Columna 'cantidad_ingresada' agregada")
        else:
            print("ℹ️  Columna 'cantidad_ingresada' ya existe")

        print("\n📋 Paso 4: Inicializando datos existentes...")

        # Para productos ya existentes, asumir que ya fueron ingresados completamente
        cursor.execute('''
            UPDATE productos_producidos
            SET cantidad_ingresada = cantidad_pares
            WHERE cantidad_ingresada IS NULL OR cantidad_ingresada = 0
        ''')

        filas_actualizadas = cursor.rowcount
        print(f"✅ {filas_actualizadas} productos existentes marcados como completamente ingresados")

        conn.commit()

        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\nCambios realizados:")
        print("  • Campo 'material_plantilla' agregado a productos_producidos")
        print("  • Campo 'cantidad_ingresada' agregado a productos_producidos")
        print(f"  • {filas_actualizadas} productos existentes inicializados")
        print("\nPuedes continuar usando la aplicación normalmente.")

    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        print("La base de datos no fue modificada (rollback automático)")
        conn.rollback()

    finally:
        conn.close()

if __name__ == '__main__':
    migrar()
