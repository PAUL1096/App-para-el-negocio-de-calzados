"""
Script de migración para integrar Ventas con Clientes y Cuentas por Cobrar
Agrega columna id_cliente a ventas_v2 para vincular con tabla clientes
Ejecutar: python migracion_integracion_ventas_clientes.py
"""

import sqlite3
from datetime import datetime
import shutil

DATABASE = 'calzado.db'

def crear_backup():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_integracion_ventas_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error creando backup: {str(e)}")
        return False

def migrar():
    """Ejecutar migración para integrar ventas con clientes"""
    print("\n" + "="*70)
    print("🔧 MIGRACIÓN: Integración Ventas ↔ Clientes ↔ Cuentas por Cobrar")
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

        # Crear tabla temporal con id_cliente
        cursor.execute('''
            CREATE TABLE ventas_v2_new (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_venta TEXT UNIQUE NOT NULL,
                id_preparacion INTEGER,
                id_producto INTEGER NOT NULL,
                id_cliente INTEGER,  -- NUEVO: Vinculación con tabla clientes
                cliente TEXT NOT NULL,  -- Se mantiene para retrocompatibilidad
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
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            )
        ''')
        print("✅ Tabla temporal creada con columna id_cliente")

        print("\n📋 Paso 2: Copiando datos existentes...")

        # Copiar datos (id_cliente será NULL para ventas antiguas)
        cursor.execute('''
            INSERT INTO ventas_v2_new
            (id_venta, codigo_venta, id_preparacion, id_producto, id_cliente, cliente,
             cantidad_pares, cantidad_docenas, precio_unitario, subtotal, descuento,
             total_final, estado_pago, metodo_pago, fecha_venta, hora_venta, observaciones)
            SELECT
                id_venta, codigo_venta, id_preparacion, id_producto, NULL as id_cliente, cliente,
                cantidad_pares, cantidad_docenas, precio_unitario, subtotal, descuento,
                total_final, estado_pago, metodo_pago, fecha_venta, hora_venta, observaciones
            FROM ventas_v2
        ''')

        rows_copied = cursor.rowcount
        print(f"✅ {rows_copied} registros copiados")

        print("\n📋 Paso 3: Intentando vincular ventas con clientes existentes...")

        # Intentar vincular ventas con clientes por nombre
        cursor.execute('''
            UPDATE ventas_v2_new
            SET id_cliente = (
                SELECT id_cliente
                FROM clientes
                WHERE LOWER(TRIM(clientes.nombre || ' ' || COALESCE(clientes.apellido, '')))
                    = LOWER(TRIM(ventas_v2_new.cliente))
                LIMIT 1
            )
            WHERE id_cliente IS NULL
        ''')

        vinculados = cursor.rowcount
        print(f"✅ {vinculados} ventas vinculadas automáticamente con clientes")

        print("\n📋 Paso 4: Eliminando tabla antigua...")
        cursor.execute('DROP TABLE ventas_v2')
        print("✅ Tabla antigua eliminada")

        print("\n📋 Paso 5: Renombrando tabla nueva...")
        cursor.execute('ALTER TABLE ventas_v2_new RENAME TO ventas_v2')
        print("✅ Tabla renombrada")

        print("\n📋 Paso 6: Recreando índices...")

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_preparacion ON ventas_v2(id_preparacion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_producto ON ventas_v2(id_producto)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_cliente ON ventas_v2(id_cliente)')
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

            if name == 'id_cliente':
                print("    ✅ NUEVO: Columna id_cliente agregada para integración")

        # Estadísticas
        cursor.execute('SELECT COUNT(*) FROM ventas_v2 WHERE id_cliente IS NOT NULL')
        ventas_con_cliente = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM ventas_v2')
        total_ventas = cursor.fetchone()[0]

        conn.close()

        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n💡 Cambios realizados:")
        print(f"   ✓ Columna id_cliente agregada a ventas_v2")
        print(f"   ✓ {ventas_con_cliente}/{total_ventas} ventas vinculadas con clientes")
        print(f"   ✓ {total_ventas - ventas_con_cliente} ventas antiguas sin vincular (campo texto preservado)")
        print("\n💡 Próximos pasos:")
        print("   1. Las nuevas ventas se vincularán automáticamente con clientes")
        print("   2. Ventas a crédito crearán automáticamente cuentas por cobrar")
        print("   3. Pagos de cuentas actualizarán el estado de ventas")
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
