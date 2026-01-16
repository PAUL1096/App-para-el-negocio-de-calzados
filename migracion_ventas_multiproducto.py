"""
Script de migración CRÍTICA: Rediseño de Ventas para soportar múltiples productos
================================================================
PROBLEMA ACTUAL: ventas_v2 solo permite 1 producto por venta
SOLUCIÓN: Crear tabla ventas_detalle para soportar N productos por venta

Ejecutar: python migracion_ventas_multiproducto.py
"""

import sqlite3
from datetime import datetime
import shutil

DATABASE = 'calzado.db'

def crear_backup():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_multiproducto_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error creando backup: {str(e)}")
        return False

def migrar():
    """Ejecutar migración para soportar múltiples productos por venta"""
    print("\n" + "="*80)
    print("🔧 MIGRACIÓN CRÍTICA: Ventas Multi-Producto (Shopping Cart Model)")
    print("="*80 + "\n")

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
            print("❌ La tabla ventas_v2 no existe.")
            conn.close()
            return

        # Verificar si ya existe ventas_detalle
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_detalle'")
        if cursor.fetchone():
            print("⚠️  La tabla ventas_detalle ya existe. Migración ya ejecutada?")
            respuesta = input("¿Continuar de todas formas? (SI/NO): ").strip().upper()
            if respuesta != 'SI':
                print("❌ Migración cancelada")
                conn.close()
                return
            cursor.execute('DROP TABLE ventas_detalle')
            print("✅ Tabla ventas_detalle anterior eliminada")

        print("\n📋 Paso 1: Creando tabla ventas_detalle (detalle de productos por venta)...")

        cursor.execute('''
            CREATE TABLE ventas_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                codigo_interno TEXT,
                cuero TEXT,
                color_cuero TEXT,
                serie_tallas TEXT,
                cantidad_pares INTEGER NOT NULL,
                cantidad_docenas DECIMAL(10,2),
                precio_unitario DECIMAL(10,2) NOT NULL,
                descuento_linea DECIMAL(10,2) DEFAULT 0,
                subtotal DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (id_venta) REFERENCES ventas_v2(id_venta) ON DELETE CASCADE,
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto)
            )
        ''')
        print("✅ Tabla ventas_detalle creada")

        print("\n📋 Paso 2: Migrando ventas existentes a ventas_detalle...")

        # Contar ventas existentes
        cursor.execute('SELECT COUNT(*) FROM ventas_v2')
        total_ventas = cursor.fetchone()[0]

        if total_ventas > 0:
            # Migrar cada venta existente como una línea de detalle
            cursor.execute('''
                INSERT INTO ventas_detalle
                (id_venta, id_producto, cantidad_pares, cantidad_docenas, precio_unitario, subtotal)
                SELECT
                    v.id_venta,
                    v.id_producto,
                    v.cantidad_pares,
                    v.cantidad_docenas,
                    v.precio_unitario,
                    COALESCE(v.subtotal, v.cantidad_pares * v.precio_unitario) as subtotal
                FROM ventas_v2 v
                WHERE v.id_producto IS NOT NULL
            ''')
            migradas = cursor.rowcount
            print(f"✅ {migradas} líneas de venta migradas a ventas_detalle")
        else:
            print("ℹ️  No hay ventas existentes para migrar")

        print("\n📋 Paso 3: Actualizando datos de productos en ventas_detalle...")

        # Actualizar información de productos en el detalle
        cursor.execute('''
            UPDATE ventas_detalle
            SET
                codigo_interno = (SELECT codigo_interno FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                cuero = (SELECT cuero FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                color_cuero = (SELECT color_cuero FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                serie_tallas = (SELECT serie_tallas FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto)
        ''')
        print("✅ Información de productos actualizada en detalle")

        print("\n📋 Paso 4: Recreando tabla ventas_v2 sin columnas de producto individual...")

        # Crear nueva estructura de ventas_v2 (sin id_producto, cantidad_pares, etc.)
        cursor.execute('''
            CREATE TABLE ventas_v2_new (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_venta TEXT UNIQUE NOT NULL,
                id_preparacion INTEGER,
                id_cliente INTEGER,
                cliente TEXT NOT NULL,
                descuento_global DECIMAL(10,2) DEFAULT 0,
                total_final DECIMAL(10,2) NOT NULL,
                estado_pago TEXT DEFAULT 'pendiente',
                metodo_pago TEXT,
                fecha_venta DATE DEFAULT (DATE('now')),
                hora_venta TIME DEFAULT (TIME('now')),
                observaciones TEXT,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones(id_preparacion),
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
            )
        ''')
        print("✅ Tabla ventas_v2_new creada (estructura maestro)")

        print("\n📋 Paso 5: Migrando datos a nueva estructura...")

        # Copiar datos (sin columnas de producto)
        cursor.execute('''
            INSERT INTO ventas_v2_new
            (id_venta, codigo_venta, id_preparacion, id_cliente, cliente,
             descuento_global, total_final, estado_pago, metodo_pago,
             fecha_venta, hora_venta, observaciones)
            SELECT
                id_venta, codigo_venta, id_preparacion, id_cliente, cliente,
                COALESCE(descuento, 0) as descuento_global,
                total_final, estado_pago, metodo_pago,
                fecha_venta, hora_venta, observaciones
            FROM ventas_v2
        ''')
        print(f"✅ {cursor.rowcount} ventas migradas a nueva estructura")

        print("\n📋 Paso 6: Reemplazando tabla antigua...")
        cursor.execute('DROP TABLE ventas_v2')
        cursor.execute('ALTER TABLE ventas_v2_new RENAME TO ventas_v2')
        print("✅ Tabla ventas_v2 actualizada")

        print("\n📋 Paso 7: Recreando índices...")
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_preparacion ON ventas_v2(id_preparacion)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_cliente ON ventas_v2(id_cliente)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_fecha ON ventas_v2(fecha_venta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_v2_estado ON ventas_v2(estado_pago)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_detalle_venta ON ventas_detalle(id_venta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_ventas_detalle_producto ON ventas_detalle(id_producto)')
        print("✅ Índices recreados")

        # Commit
        conn.commit()

        # Verificar estructura final
        print("\n📋 Verificando estructuras finales...")

        print("\n📊 Estructura de ventas_v2 (MAESTRO):")
        cursor.execute("PRAGMA table_info(ventas_v2)")
        for col in cursor.fetchall():
            col_id, name, type_, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            print(f"  - {name} ({type_}) {nullable}")

        print("\n📊 Estructura de ventas_detalle (DETALLE):")
        cursor.execute("PRAGMA table_info(ventas_detalle)")
        for col in cursor.fetchall():
            col_id, name, type_, notnull, default, pk = col
            nullable = "NOT NULL" if notnull else "NULL"
            print(f"  - {name} ({type_}) {nullable}")

        # Estadísticas
        cursor.execute('SELECT COUNT(*) FROM ventas_v2')
        total_ventas_final = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM ventas_detalle')
        total_lineas = cursor.fetchone()[0]

        conn.close()

        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print("\n💡 Cambios realizados:")
        print(f"   ✓ Tabla ventas_detalle creada para soportar múltiples productos")
        print(f"   ✓ Tabla ventas_v2 rediseñada como maestro (sin columnas de producto)")
        print(f"   ✓ {total_ventas_final} ventas maestro")
        print(f"   ✓ {total_lineas} líneas de detalle")
        print("\n💡 Nuevo modelo:")
        print("   ventas_v2 (maestro) → 1 registro por venta")
        print("   ventas_detalle → N registros por venta (1 por cada producto)")
        print("\n💡 Próximos pasos:")
        print("   1. Actualizar UI para soportar carrito de compras")
        print("   2. Modificar API de registro de ventas")
        print("   3. Actualizar reportes y consultas")
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
