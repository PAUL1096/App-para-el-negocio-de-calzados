"""
Script de Migración a Versión 1.2
Sistema de Gestión de Ventas de Calzado

CAMBIOS PRINCIPALES:
- Separación de PRODUCTO BASE y VARIANTES
- Sistema de INVENTARIO (Stock General + Pedidos Cliente)
- Gestión de UBICACIONES (almacenes)
- Preservación de datos históricos

Fecha: 2025-12-09
"""

import sqlite3
import shutil
from datetime import datetime
import os

DATABASE = 'ventas_calzado.db'

def crear_respaldo():
    """Crea una copia de respaldo de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'ventas_calzado_backup_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Respaldo creado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return None

def ejecutar_migracion():
    """Ejecuta la migración de la base de datos"""

    print("\n" + "="*60)
    print("🔄 INICIANDO MIGRACIÓN A VERSIÓN 1.2")
    print("="*60 + "\n")

    # Crear respaldo
    backup = crear_respaldo()
    if not backup:
        print("❌ No se pudo crear el respaldo. Abortando migración.")
        return False

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # ========================================
        # 1. TABLA: ubicaciones
        # ========================================
        print("📍 Creando tabla 'ubicaciones'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                tipo TEXT NOT NULL,
                descripcion TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insertar ubicaciones predeterminadas
        ubicaciones_default = [
            ('Casa', 'produccion', 'Ubicación de producción'),
            ('Tienda Principal', 'almacen', 'Almacén principal de distribución'),
            ('Tienda Secundaria', 'almacen', 'Almacén secundario')
        ]

        for nombre, tipo, desc in ubicaciones_default:
            cursor.execute('''
                INSERT OR IGNORE INTO ubicaciones (nombre, tipo, descripcion)
                VALUES (?, ?, ?)
            ''', (nombre, tipo, desc))

        print("   ✅ Ubicaciones creadas: Casa, Tienda Principal, Tienda Secundaria")

        # ========================================
        # 2. TABLA: productos_base (nuevo modelo)
        # ========================================
        print("\n📦 Creando tabla 'productos_base'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos_base (
                codigo_producto INTEGER PRIMARY KEY,
                nombre TEXT,
                tipo TEXT NOT NULL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observaciones TEXT
            )
        ''')
        print("   ✅ Tabla productos_base creada")

        # ========================================
        # 3. TABLA: variantes
        # ========================================
        print("\n🎨 Creando tabla 'variantes'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variantes (
                id_variante INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_producto INTEGER NOT NULL,
                cuero TEXT NOT NULL,
                color TEXT NOT NULL,
                serie_tallas TEXT NOT NULL,
                pares_por_docena INTEGER DEFAULT 12,
                costo_unitario REAL NOT NULL,
                precio_sugerido REAL NOT NULL,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observaciones TEXT,
                FOREIGN KEY (codigo_producto) REFERENCES productos_base (codigo_producto),
                UNIQUE(codigo_producto, cuero, color, serie_tallas)
            )
        ''')
        print("   ✅ Tabla variantes creada")

        # ========================================
        # 4. TABLA: inventario
        # ========================================
        print("\n📊 Creando tabla 'inventario'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_variante INTEGER NOT NULL,
                id_ubicacion INTEGER NOT NULL,
                tipo_stock TEXT NOT NULL CHECK(tipo_stock IN ('general', 'pedido')),
                cantidad_pares INTEGER NOT NULL DEFAULT 0,
                id_pedido_cliente INTEGER,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_variante) REFERENCES variantes (id_variante),
                FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones (id_ubicacion),
                FOREIGN KEY (id_pedido_cliente) REFERENCES pedidos_cliente (id_pedido),
                UNIQUE(id_variante, id_ubicacion, tipo_stock, id_pedido_cliente)
            )
        ''')
        print("   ✅ Tabla inventario creada")

        # ========================================
        # 5. TABLA: pedidos_cliente
        # ========================================
        print("\n📋 Creando tabla 'pedidos_cliente'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos_cliente (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT NOT NULL,
                fecha_pedido DATE NOT NULL,
                fecha_entrega_estimada DATE NOT NULL,
                estado TEXT NOT NULL DEFAULT 'pendiente'
                    CHECK(estado IN ('pendiente', 'en_preparacion', 'entregado', 'cancelado')),
                total_pares INTEGER DEFAULT 0,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("   ✅ Tabla pedidos_cliente creada")

        # ========================================
        # 6. TABLA: pedidos_detalle
        # ========================================
        print("\n📝 Creando tabla 'pedidos_detalle'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                id_variante INTEGER NOT NULL,
                cantidad_pares INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (id_pedido) REFERENCES pedidos_cliente (id_pedido),
                FOREIGN KEY (id_variante) REFERENCES variantes (id_variante)
            )
        ''')
        print("   ✅ Tabla pedidos_detalle creada")

        # ========================================
        # 7. TABLA: movimientos_inventario
        # ========================================
        print("\n📦 Creando tabla 'movimientos_inventario'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS movimientos_inventario (
                id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_movimiento TEXT NOT NULL
                    CHECK(tipo_movimiento IN ('ingreso', 'egreso', 'traslado', 'ajuste', 'venta', 'preparacion')),
                id_variante INTEGER NOT NULL,
                id_ubicacion_origen INTEGER,
                id_ubicacion_destino INTEGER,
                cantidad_pares INTEGER NOT NULL,
                tipo_stock TEXT NOT NULL CHECK(tipo_stock IN ('general', 'pedido')),
                id_pedido_cliente INTEGER,
                id_venta TEXT,
                id_preparacion INTEGER,
                usuario TEXT,
                motivo TEXT,
                fecha_movimiento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_variante) REFERENCES variantes (id_variante),
                FOREIGN KEY (id_ubicacion_origen) REFERENCES ubicaciones (id_ubicacion),
                FOREIGN KEY (id_ubicacion_destino) REFERENCES ubicaciones (id_ubicacion),
                FOREIGN KEY (id_pedido_cliente) REFERENCES pedidos_cliente (id_pedido)
            )
        ''')
        print("   ✅ Tabla movimientos_inventario creada")

        # ========================================
        # 8. MIGRAR DATOS: productos → productos_base + variantes
        # ========================================
        print("\n🔄 Migrando datos de productos existentes...")

        cursor.execute('SELECT * FROM productos')
        productos_antiguos = cursor.fetchall()

        if productos_antiguos:
            print(f"   Encontrados {len(productos_antiguos)} productos para migrar")

            for prod in productos_antiguos:
                codigo = prod[0]
                tipo = prod[1]
                cuero = prod[2]
                color = prod[3]
                serie = prod[4]
                costo = prod[5]
                precio = prod[6]
                obs = prod[7]

                # Insertar en productos_base
                cursor.execute('''
                    INSERT OR IGNORE INTO productos_base
                    (codigo_producto, tipo, nombre, observaciones)
                    VALUES (?, ?, ?, ?)
                ''', (codigo, tipo, f"{tipo} {codigo}", obs))

                # Insertar en variantes
                cursor.execute('''
                    INSERT OR IGNORE INTO variantes
                    (codigo_producto, cuero, color, serie_tallas, costo_unitario, precio_sugerido)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (codigo, cuero, color, serie, costo, precio))

            print(f"   ✅ {len(productos_antiguos)} productos migrados a productos_base + variantes")
        else:
            print("   ℹ️  No hay productos para migrar")

        # ========================================
        # 9. CREAR ÍNDICES para optimización
        # ========================================
        print("\n⚡ Creando índices para optimización...")

        indices = [
            "CREATE INDEX IF NOT EXISTS idx_variantes_producto ON variantes(codigo_producto)",
            "CREATE INDEX IF NOT EXISTS idx_inventario_variante ON inventario(id_variante)",
            "CREATE INDEX IF NOT EXISTS idx_inventario_ubicacion ON inventario(id_ubicacion)",
            "CREATE INDEX IF NOT EXISTS idx_movimientos_variante ON movimientos_inventario(id_variante)",
            "CREATE INDEX IF NOT EXISTS idx_movimientos_fecha ON movimientos_inventario(fecha_movimiento)",
            "CREATE INDEX IF NOT EXISTS idx_pedidos_estado ON pedidos_cliente(estado)",
            "CREATE INDEX IF NOT EXISTS idx_pedidos_fecha_entrega ON pedidos_cliente(fecha_entrega_estimada)"
        ]

        for idx in indices:
            cursor.execute(idx)

        print("   ✅ Índices creados")

        # ========================================
        # COMMIT FINAL
        # ========================================
        conn.commit()

        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"\n📄 Respaldo disponible en: {backup}")
        print("📊 Nuevas tablas creadas:")
        print("   - ubicaciones")
        print("   - productos_base")
        print("   - variantes")
        print("   - inventario")
        print("   - pedidos_cliente")
        print("   - pedidos_detalle")
        print("   - movimientos_inventario")
        print("\n⚠️  Nota: La tabla 'productos' original se mantiene para compatibilidad")
        print("   pero el sistema ahora usa productos_base + variantes\n")

        return True

    except Exception as e:
        conn.rollback()
        print(f"\n❌ ERROR durante la migración: {e}")
        print(f"📄 Puedes restaurar desde el respaldo: {backup}")
        return False

    finally:
        conn.close()

def verificar_migracion():
    """Verifica que la migración se haya ejecutado correctamente"""
    print("\n🔍 Verificando migración...")

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # Verificar tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tablas = [row[0] for row in cursor.fetchall()]

        tablas_requeridas = [
            'ubicaciones', 'productos_base', 'variantes',
            'inventario', 'pedidos_cliente', 'pedidos_detalle',
            'movimientos_inventario'
        ]

        print("\n📋 Tablas existentes:")
        for tabla in tablas_requeridas:
            existe = tabla in tablas
            status = "✅" if existe else "❌"
            print(f"   {status} {tabla}")

        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM ubicaciones")
        count_ubicaciones = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM variantes")
        count_variantes = cursor.fetchone()[0]

        print(f"\n📊 Datos migrados:")
        print(f"   - Ubicaciones: {count_ubicaciones}")
        print(f"   - Variantes: {count_variantes}")

        return True

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE GESTIÓN DE CALZADO - MIGRACIÓN V1.2")
    print("="*60)
    print("\nEste script migrará tu base de datos al nuevo esquema.")
    print("Se creará un respaldo automático antes de proceder.\n")

    respuesta = input("¿Deseas continuar? (s/n): ")

    if respuesta.lower() == 's':
        if ejecutar_migracion():
            verificar_migracion()
            print("\n✅ Migración completada. El sistema está listo para usar.\n")
        else:
            print("\n❌ La migración falló. Revisa los errores arriba.\n")
    else:
        print("\n❌ Migración cancelada.\n")
