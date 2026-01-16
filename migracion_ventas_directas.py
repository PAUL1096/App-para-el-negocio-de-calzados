"""
Script de migración para permitir ventas directas (sin preparación)
Modifica ventas_v2 para permitir id_preparacion NULL
Ejecutar: python migracion_ventas_directas.py
"""

import sqlite3
from datetime import datetime
import shutil

DATABASE = 'calzado.db'

def crear_backup():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_ventas_directas_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error creando backup: {str(e)}")
        return False

def migrar():
    """Ejecutar migración para permitir ventas directas"""
    print("\n" + "="*70)
    print("🔧 MIGRACIÓN: Permitir Ventas Directas (id_preparacion NULL)")
    print("="*70 + "\n")

    # Crear backup
    if not crear_backup():
        print("\n⚠️  ¿Continuar sin backup? (SI/NO): ")
        respuesta = input().strip().upper()
        if respuesta != 'SI':
            print("❌ Migración cancelada")
            return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_v2'")
        if not cursor.fetchone():
            print("❌ La tabla ventas_v2 no existe. Ejecuta primero las migraciones previas.")
            conn.close()
            return

        print("\n📋 Paso 1: Creando tabla temporal con nueva estructura...")

        # Crear tabla temporal con id_preparacion permitiendo NULL
        cursor.execute('''
            CREATE TABLE ventas_v2_new (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_venta TEXT UNIQUE NOT NULL,
                id_preparacion INTEGER,  -- Ahora permite NULL
                id_producto INTEGER NOT NULL,
                cliente TEXT NOT NULL,
                cantidad_pares INTEGER NOT NULL,
                cantidad_docenas DECIMAL(10,2),
                precio_unitario DECIMAL(10,2) NOT NULL,
                subtotal DECIMAL(10,2),
                descuento DECIMAL(10,2) DEFAULT 0,
                total_final DECIMAL(10,2),
                estado_pago TEXT DEFAULT 'pendiente',
                metodo_pago TEXT,
                fecha_venta DATE DEFAULT (DATE('now')),
                hora_venta TIME DEFAULT (TIME('now')),
                observaciones TEXT,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones(id_preparacion),
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto)
            )
        ''')
        print("✅ Tabla temporal creada")

        print("\n📋 Paso 2: Copiando datos existentes...")

        # Copiar todos los datos de la tabla antigua a la nueva
        cursor.execute('''
            INSERT INTO ventas_v2_new
            SELECT * FROM ventas_v2
        ''')

        rows_copied = cursor.rowcount
        print(f"✅ {rows_copied} registros copiados")

        print("\n📋 Paso 3: Eliminando tabla antigua...")
        cursor.execute('DROP TABLE ventas_v2')
        print("✅ Tabla antigua eliminada")

        print("\n📋 Paso 4: Renombrando tabla nueva...")
        cursor.execute('ALTER TABLE ventas_v2_new RENAME TO ventas_v2')
        print("✅ Tabla renombrada")

        print("\n📋 Paso 5: Recreando índices...")

        # Recrear índices si existían
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_preparacion ON ventas_v2(id_preparacion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_producto ON ventas_v2(id_producto)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_fecha ON ventas_v2(fecha_venta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_estado ON ventas_v2(estado_pago)')

        print("✅ Índices recreados")

        # Commit
        conn.commit()

        # Verificar estructura final
        print("\n📋 Verificando estructura final...")
        cursor.execute("PRAGMA table_info(ventas_v2)")
        columns = cursor.fetchall()

        print("\n📊 Estructura de ventas_v2:")
        for col in columns:
            col_id, name, type_, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            print(f"  - {name} ({type_}) {nullable}")

            # Verificar que id_preparacion ahora permite NULL
            if name == 'id_preparacion' and notnull == 0:
                print("    ✅ id_preparacion ahora permite NULL (ventas directas)")

        conn.close()

        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n💡 Cambios realizados:")
        print("   ✓ id_preparacion ahora permite valores NULL")
        print("   ✓ Las ventas directas (sin preparación) ya funcionarán correctamente")
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: python app_v2.py")
        print("   2. Ir a Ventas → Venta Directa")
        print("   3. Registrar una venta desde inventario")
        print("\n")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Restaura el backup si es necesario")

if __name__ == '__main__':
    migrar()
