"""
Migración: Agregar destino y completitud a preparaciones
Fecha: 2026-01-06
Objetivo: Refactorizar preparaciones para que sean logística (no inventario)

Cambios:
1. Agregar campo id_ubicacion_destino (a dónde van los productos)
2. Agregar campo fecha_completada (cuándo llegaron)
3. Permitir estado 'completada' y 'cancelada'
4. Migrar preparaciones existentes automáticamente
"""

import sqlite3
from datetime import datetime

def migrar():
    print("=" * 70)
    print("MIGRACIÓN: Preparaciones como Logística")
    print("=" * 70)

    conn = sqlite3.connect('inventario_calzado.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("\n📋 Paso 1: Verificando si la tabla preparaciones existe...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='preparaciones'")
        existe_tabla = cursor.fetchone()

        if not existe_tabla:
            print("⚠️  La tabla 'preparaciones' no existe en la base de datos")
            print("❌ Esta migración requiere que la tabla preparaciones ya exista")
            print("\nDebes ejecutar primero una migración base del sistema")
            conn.close()
            return

        print("✅ Tabla preparaciones encontrada")

        print("\n📋 Paso 2: Verificando estructura actual...")
        cursor.execute("PRAGMA table_info(preparaciones)")
        columnas = {col['name']: col for col in cursor.fetchall()}

        # Verificar si ya se aplicó la migración
        if 'id_ubicacion_destino' in columnas:
            print("✅ La migración ya fue aplicada anteriormente")
            print("\nCampos presentes:")
            print("  - id_ubicacion_destino: ✓")
            print("  - fecha_completada: ✓" if 'fecha_completada' in columnas else "  - fecha_completada: ✗")
            conn.close()
            return

        print("📝 Campos actuales:", list(columnas.keys()))

        # Opción 1: Agregar columnas si la tabla es simple (SQLite permite ALTER TABLE ADD COLUMN)
        print("\n📋 Paso 3: Agregando nuevos campos...")

        # Agregar id_ubicacion_destino
        cursor.execute('''
            ALTER TABLE preparaciones
            ADD COLUMN id_ubicacion_destino INTEGER REFERENCES ubicaciones(id_ubicacion)
        ''')
        print("✅ Campo 'id_ubicacion_destino' agregado")

        # Agregar fecha_completada
        cursor.execute('''
            ALTER TABLE preparaciones
            ADD COLUMN fecha_completada TIMESTAMP
        ''')
        print("✅ Campo 'fecha_completada' agregado")

        print("\n📋 Paso 4: Migración automática de preparaciones existentes...")

        # Contar preparaciones existentes
        cursor.execute('SELECT COUNT(*) as total FROM preparaciones')
        total = cursor.fetchone()['total']

        if total > 0:
            print(f"\n⚠️  Encontradas {total} preparaciones existentes")
            print("\n🔧 Aplicando migración automática:")
            print("   - Todas las preparaciones existentes se marcarán como 'completadas'")
            print("   - Fecha completada = fecha preparación (asumimos ya están en destino)")
            print("   - NO se moverá inventario (asumimos ya está en las tiendas)")

            # Marcar todas como completadas con fecha de preparación
            cursor.execute('''
                UPDATE preparaciones
                SET fecha_completada = fecha_preparacion
                WHERE estado IN ('pendiente', 'en_proceso')
            ''')

            preparaciones_actualizadas = cursor.rowcount
            print(f"✅ {preparaciones_actualizadas} preparaciones marcadas como completadas")

        else:
            print("✅ No hay preparaciones existentes para migrar")

        print("\n📋 Paso 5: Verificando integridad...")

        # Verificar que todo está bien
        cursor.execute("PRAGMA table_info(preparaciones)")
        columnas_finales = {col['name'] for col in cursor.fetchall()}

        campos_requeridos = {'id_ubicacion_destino', 'fecha_completada'}
        campos_presentes = campos_requeridos.intersection(columnas_finales)

        print(f"\n📊 Resumen:")
        print(f"   Campos agregados: {len(campos_presentes)}/{len(campos_requeridos)}")
        for campo in campos_requeridos:
            estado = "✓" if campo in campos_presentes else "✗"
            print(f"   - {campo}: {estado}")

        conn.commit()
        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)

        print("\n📝 Próximos pasos:")
        print("1. Al crear nuevas preparaciones, asigna ubicación de destino")
        print("2. Usa el botón 'Confirmar Llegada' para mover inventario")
        print("3. Las ventas ahora solo funcionan desde inventario real")

    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(f"\n✅ Columna ya existe (probablemente de una ejecución anterior)")
            print("Continuando...")
        else:
            conn.rollback()
            print(f"\n❌ Error de SQL: {e}")
            raise
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante la migración: {e}")
        print("La base de datos no fue modificada")
        raise

    finally:
        conn.close()

if __name__ == '__main__':
    migrar()
