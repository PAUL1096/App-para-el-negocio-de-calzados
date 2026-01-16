"""
Script de Limpieza y Re-ejecución de Migración Ventas Multi-Producto
====================================================================
Este script limpia tablas temporales de migraciones anteriores fallidas
y ejecuta la migración correctamente.
"""

import sqlite3
from datetime import datetime
import shutil
import os

DATABASE = 'calzado.db'

def crear_backup():
    """Crear backup de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_limpieza_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error creando backup: {str(e)}")
        return None

def limpiar_tablas_temporales():
    """Eliminar tablas temporales de migraciones anteriores"""
    print("\n" + "="*80)
    print("🧹 LIMPIEZA DE TABLAS TEMPORALES")
    print("="*80 + "\n")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    tablas_temporales = ['ventas_v2_new', 'ventas_v2_old', 'ventas_v2_backup']

    for tabla in tablas_temporales:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}'")
        if cursor.fetchone():
            print(f"🗑️  Eliminando tabla temporal: {tabla}")
            cursor.execute(f'DROP TABLE {tabla}')
            print(f"✅ Tabla {tabla} eliminada")
        else:
            print(f"ℹ️  Tabla {tabla} no existe (OK)")

    conn.commit()
    conn.close()
    print("\n✅ Limpieza completada\n")

def verificar_estado():
    """Verificar estado actual de la base de datos"""
    print("\n" + "="*80)
    print("🔍 VERIFICANDO ESTADO ACTUAL")
    print("="*80 + "\n")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Verificar ventas_v2
    cursor.execute("PRAGMA table_info(ventas_v2)")
    columnas_v2 = {col[1]: col[2] for col in cursor.fetchall()}

    print("📋 Columnas en ventas_v2:")
    for col, tipo in columnas_v2.items():
        print(f"   - {col} ({tipo})")

    tiene_id_producto = 'id_producto' in columnas_v2
    tiene_id_cliente = 'id_cliente' in columnas_v2

    # Verificar ventas_detalle
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_detalle'")
    existe_detalle = cursor.fetchone() is not None

    # Contar registros
    cursor.execute('SELECT COUNT(*) FROM ventas_v2')
    total_ventas = cursor.fetchone()[0]

    if existe_detalle:
        cursor.execute('SELECT COUNT(*) FROM ventas_detalle')
        total_detalle = cursor.fetchone()[0]
    else:
        total_detalle = 0

    conn.close()

    print(f"\n📊 Estado:")
    print(f"   - Ventas en ventas_v2: {total_ventas}")
    print(f"   - Registros en ventas_detalle: {total_detalle}")
    print(f"   - Tabla ventas_detalle existe: {'✅' if existe_detalle else '❌'}")
    print(f"   - Columna id_producto en ventas_v2: {'✅' if tiene_id_producto else '❌'}")
    print(f"   - Columna id_cliente en ventas_v2: {'✅' if tiene_id_cliente else '❌'}")

    return {
        'tiene_id_producto': tiene_id_producto,
        'existe_detalle': existe_detalle,
        'total_ventas': total_ventas,
        'total_detalle': total_detalle
    }

def ejecutar_migracion_completa():
    """Ejecutar migración completa desde cero"""
    print("\n" + "="*80)
    print("🔧 EJECUTANDO MIGRACIÓN COMPLETA")
    print("="*80 + "\n")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Paso 1: Crear ventas_detalle si no existe o está vacía
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_detalle'")
        if not cursor.fetchone():
            print("📋 Paso 1: Creando tabla ventas_detalle...")
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
        else:
            print("ℹ️  Tabla ventas_detalle ya existe")

        # Paso 2: Verificar si ventas_v2 tiene id_producto (necesita migración)
        cursor.execute("PRAGMA table_info(ventas_v2)")
        columnas = {col[1]: True for col in cursor.fetchall()}

        if 'id_producto' in columnas:
            print("\n📋 Paso 2: Migrando datos de ventas_v2 a ventas_detalle...")

            # Migrar ventas existentes a detalle
            cursor.execute('''
                INSERT OR IGNORE INTO ventas_detalle
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
            print(f"✅ {migradas} ventas migradas a ventas_detalle")

            # Actualizar info de productos
            cursor.execute('''
                UPDATE ventas_detalle
                SET
                    codigo_interno = (SELECT codigo_interno FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                    cuero = (SELECT cuero FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                    color_cuero = (SELECT color_cuero FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto),
                    serie_tallas = (SELECT serie_tallas FROM productos_producidos WHERE id_producto = ventas_detalle.id_producto)
                WHERE codigo_interno IS NULL
            ''')
            print("✅ Información de productos actualizada")

            # Paso 3: Recrear ventas_v2 sin columnas de producto
            print("\n📋 Paso 3: Recreando ventas_v2 sin columnas de producto...")

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
            print("✅ Tabla ventas_v2_new creada")

            # Copiar datos
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
            print(f"✅ {cursor.rowcount} ventas copiadas a nueva estructura")

            # Reemplazar tabla
            cursor.execute('DROP TABLE ventas_v2')
            cursor.execute('ALTER TABLE ventas_v2_new RENAME TO ventas_v2')
            print("✅ Tabla ventas_v2 actualizada")
        else:
            print("\nℹ️  ventas_v2 ya tiene la estructura correcta (sin id_producto)")

        # Crear índices
        print("\n📋 Paso 4: Recreando índices...")
        indices = [
            'CREATE INDEX IF NOT EXISTS idx_ventas_v2_preparacion ON ventas_v2(id_preparacion)',
            'CREATE INDEX IF NOT EXISTS idx_ventas_v2_cliente ON ventas_v2(id_cliente)',
            'CREATE INDEX IF NOT EXISTS idx_ventas_v2_fecha ON ventas_v2(fecha_venta)',
            'CREATE INDEX IF NOT EXISTS idx_ventas_v2_estado ON ventas_v2(estado_pago)',
            'CREATE INDEX IF NOT EXISTS idx_ventas_detalle_venta ON ventas_detalle(id_venta)',
            'CREATE INDEX IF NOT EXISTS idx_ventas_detalle_producto ON ventas_detalle(id_producto)'
        ]

        for idx in indices:
            cursor.execute(idx)
        print("✅ Índices recreados")

        conn.commit()

        # Verificar resultado final
        print("\n📋 Verificando resultado final...")
        cursor.execute('SELECT COUNT(*) FROM ventas_v2')
        total_ventas = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM ventas_detalle')
        total_detalle = cursor.fetchone()[0]

        conn.close()

        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print(f"\n📊 Resultado final:")
        print(f"   - {total_ventas} ventas maestro")
        print(f"   - {total_detalle} líneas de detalle")
        print("\n💡 Ya puedes usar el sistema de ventas multi-producto")
        print("\n")

    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

def main():
    """Función principal"""
    print("="*80)
    print("🔧 LIMPIEZA Y MIGRACIÓN DE VENTAS MULTI-PRODUCTO")
    print("="*80)

    # Crear backup
    backup_file = crear_backup()
    if not backup_file:
        print("\n⚠️  No se pudo crear backup. ¿Continuar de todas formas? (SI/NO): ")
        respuesta = input().strip().upper()
        if respuesta != 'SI':
            print("❌ Operación cancelada")
            return

    # Verificar estado inicial
    estado = verificar_estado()

    # Limpiar tablas temporales
    limpiar_tablas_temporales()

    # Ejecutar migración
    ejecutar_migracion_completa()

    print("="*80)
    print("✅ PROCESO COMPLETADO")
    print("="*80)
    print("\n💡 Siguiente paso: Reinicia el servidor Flask (python app_v2.py)")
    print(f"💡 Si algo sale mal, restaura el backup: {backup_file}")
    print("\n")

if __name__ == '__main__':
    main()
