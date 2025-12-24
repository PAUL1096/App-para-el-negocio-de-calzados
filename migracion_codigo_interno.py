"""
Script de Migración: Agregar campo codigo_interno a variantes
Versión: 1.3.1
Fecha: 2025-12-09
Descripción: Agrega campo 'codigo_interno' a la tabla variantes para que el negocio
             pueda manejar sus propios códigos sin afectar el codigo_producto existente.
"""

import sqlite3
import os
from datetime import datetime

def crear_backup(db_path):
    """Crea backup de la base de datos antes de migrar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = db_path.replace('.db', f'_backup_codigo_interno_{timestamp}.db')

    print(f"📦 Creando backup: {backup_path}")

    # Copiar base de datos
    import shutil
    shutil.copy2(db_path, backup_path)

    print(f"✅ Backup creado exitosamente")
    return backup_path

def migrar_codigo_interno(db_path='calzado.db'):
    """Ejecuta la migración para agregar codigo_interno"""

    print("=" * 70)
    print("🔧 MIGRACIÓN: Agregar campo codigo_interno a variantes")
    print("=" * 70)

    if not os.path.exists(db_path):
        print(f"❌ Error: No se encuentra la base de datos en {db_path}")
        return False

    # Crear backup
    backup_path = crear_backup(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(variantes)")
        columnas = [col[1] for col in cursor.fetchall()]

        if 'codigo_interno' in columnas:
            print("⚠️  La columna 'codigo_interno' ya existe en la tabla variantes")
            print("✅ No se requiere migración")
            conn.close()
            return True

        print("\n📋 PASO 1: Agregar columna codigo_interno a tabla variantes")
        cursor.execute('''
            ALTER TABLE variantes
            ADD COLUMN codigo_interno TEXT
        ''')
        print("✅ Columna agregada exitosamente")

        print("\n📋 PASO 2: Crear índice para codigo_interno (opcional, permite búsquedas rápidas)")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_variantes_codigo_interno
            ON variantes(codigo_interno)
        ''')
        print("✅ Índice creado exitosamente")

        print("\n📋 PASO 3: Actualizar variantes existentes (opcional)")
        print("   Puedes llenar los códigos internos manualmente desde la interfaz.")
        print("   Por defecto, este campo quedará vacío (NULL).")

        # Opción: Pre-llenar con el codigo_producto como valor inicial
        # Descomentar la siguiente línea si deseas que codigo_interno inicie igual a codigo_producto
        # cursor.execute("UPDATE variantes SET codigo_interno = codigo_producto WHERE codigo_interno IS NULL")

        conn.commit()

        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print(f"\n📦 Backup disponible en: {backup_path}")
        print("\n📝 CAMBIOS REALIZADOS:")
        print("   • Campo 'codigo_interno' agregado a tabla variantes")
        print("   • Índice de búsqueda creado para codigo_interno")
        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Ejecuta la aplicación: python app_v1_3.py")
        print("   2. Ve al módulo de Variantes")
        print("   3. Edita cada variante para agregar su código interno")
        print("   4. El código interno es opcional y editable")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        print(f"📦 Puedes restaurar desde el backup: {backup_path}")
        return False

if __name__ == '__main__':
    print("\n" + "🚀 INICIANDO MIGRACIÓN" + "\n")

    # Ejecutar migración
    exito = migrar_codigo_interno()

    if exito:
        print("\n✅ Proceso completado exitosamente")
    else:
        print("\n❌ Proceso completado con errores")

    print("\n" + "="*70 + "\n")
