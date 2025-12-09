"""
Script de Migración FASE 3+4
Sistema de Gestión de Ventas de Calzado

CAMBIOS:
- Tabla de preparaciones (qué llevar a vender)
- Tabla de preparaciones_detalle (variantes y cantidades)
- Tabla de ventas_v2 (vinculadas a preparación)
- Lógica de descuento temporal y actualización automática

REQUISITO: Debe haber ejecutado migracion_v1_2.py previamente

Fecha: 2025-12-09
"""

import sqlite3
import shutil
from datetime import datetime

DATABASE = 'ventas_calzado.db'

def crear_respaldo():
    """Crea una copia de respaldo de la base de datos"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'ventas_calzado_backup_fase34_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Respaldo creado: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"❌ Error al crear respaldo: {e}")
        return None

def verificar_requisitos():
    """Verifica que existan las tablas de v1.2"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    tablas_requeridas = ['ubicaciones', 'variantes', 'inventario']

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tablas_existentes = [row[0] for row in cursor.fetchall()]

    conn.close()

    for tabla in tablas_requeridas:
        if tabla not in tablas_existentes:
            print(f"❌ Error: La tabla '{tabla}' no existe.")
            print("   Debes ejecutar 'migracion_v1_2.py' primero.")
            return False

    return True

def ejecutar_migracion():
    """Ejecuta la migración de Fase 3+4"""

    print("\n" + "="*60)
    print("🔄 INICIANDO MIGRACIÓN FASE 3+4")
    print("PREPARACIÓN DE MERCADERÍA + VENTAS MEJORADAS")
    print("="*60 + "\n")

    # Verificar requisitos
    if not verificar_requisitos():
        return False

    # Crear respaldo
    backup = crear_respaldo()
    if not backup:
        print("❌ No se pudo crear el respaldo. Abortando migración.")
        return False

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    try:
        # ========================================
        # 1. TABLA: preparaciones
        # ========================================
        print("📦 Creando tabla 'preparaciones'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preparaciones (
                id_preparacion INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_preparacion DATE NOT NULL,
                dia_venta TEXT NOT NULL,
                id_ubicacion_origen INTEGER NOT NULL,
                responsable TEXT,
                estado TEXT NOT NULL DEFAULT 'preparada'
                    CHECK(estado IN ('preparada', 'en_venta', 'finalizada', 'cancelada')),
                total_pares INTEGER DEFAULT 0,
                total_variantes INTEGER DEFAULT 0,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_ubicacion_origen) REFERENCES ubicaciones (id_ubicacion)
            )
        ''')
        print("   ✅ Tabla preparaciones creada")

        # ========================================
        # 2. TABLA: preparaciones_detalle
        # ========================================
        print("\n📝 Creando tabla 'preparaciones_detalle'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preparaciones_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_preparacion INTEGER NOT NULL,
                id_variante INTEGER NOT NULL,
                tipo_stock TEXT NOT NULL CHECK(tipo_stock IN ('general', 'pedido')),
                id_pedido_cliente INTEGER,
                cantidad_pares INTEGER NOT NULL,
                cantidad_vendida INTEGER DEFAULT 0,
                cantidad_devuelta INTEGER DEFAULT 0,
                observaciones TEXT,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones (id_preparacion),
                FOREIGN KEY (id_variante) REFERENCES variantes (id_variante),
                FOREIGN KEY (id_pedido_cliente) REFERENCES pedidos_cliente (id_pedido)
            )
        ''')
        print("   ✅ Tabla preparaciones_detalle creada")

        # ========================================
        # 3. TABLA: ventas_v2 (nueva versión)
        # ========================================
        print("\n💰 Creando tabla 'ventas_v2'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas_v2 (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_venta TEXT UNIQUE NOT NULL,
                id_preparacion INTEGER NOT NULL,
                fecha_venta DATE NOT NULL,
                hora_venta TIME,
                cliente TEXT NOT NULL,
                destino TEXT,
                id_variante INTEGER NOT NULL,
                cantidad_pares INTEGER NOT NULL,
                cantidad_docenas REAL,
                precio_unitario REAL NOT NULL,
                total_venta REAL NOT NULL,
                descuento REAL DEFAULT 0,
                total_final REAL NOT NULL,
                metodo_pago TEXT,
                estado_pago TEXT DEFAULT 'pendiente'
                    CHECK(estado_pago IN ('pendiente', 'parcial', 'pagado')),
                monto_pagado REAL DEFAULT 0,
                es_pedido_cliente INTEGER DEFAULT 0,
                id_pedido_cliente INTEGER,
                observaciones TEXT,
                año INTEGER,
                semana INTEGER,
                mes INTEGER,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones (id_preparacion),
                FOREIGN KEY (id_variante) REFERENCES variantes (id_variante),
                FOREIGN KEY (id_pedido_cliente) REFERENCES pedidos_cliente (id_pedido)
            )
        ''')
        print("   ✅ Tabla ventas_v2 creada")

        # ========================================
        # 4. TABLA: configuracion_sistema
        # ========================================
        print("\n⚙️  Creando tabla 'configuracion_sistema'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracion_sistema (
                id_config INTEGER PRIMARY KEY AUTOINCREMENT,
                clave TEXT UNIQUE NOT NULL,
                valor TEXT,
                tipo TEXT,
                descripcion TEXT,
                fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Insertar configuraciones por defecto
        configs_default = [
            ('dias_venta', 'Jueves,Viernes,Sábado', 'text', 'Días de venta semanales'),
            ('pares_por_docena', '12', 'number', 'Pares por docena estándar'),
            ('ubicacion_venta_default', '2', 'number', 'ID de ubicación para ventas (Tienda Principal)'),
            ('alerta_stock_minimo', '12', 'number', 'Cantidad mínima de pares para alerta'),
            ('auto_actualizar_inventario', 'true', 'boolean', 'Actualizar inventario automáticamente en ventas')
        ]

        for clave, valor, tipo, desc in configs_default:
            cursor.execute('''
                INSERT OR IGNORE INTO configuracion_sistema (clave, valor, tipo, descripcion)
                VALUES (?, ?, ?, ?)
            ''', (clave, valor, tipo, desc))

        print("   ✅ Tabla configuracion_sistema creada con valores por defecto")

        # ========================================
        # 5. TABLA: devoluciones
        # ========================================
        print("\n🔄 Creando tabla 'devoluciones'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devoluciones (
                id_devolucion INTEGER PRIMARY KEY AUTOINCREMENT,
                id_preparacion INTEGER NOT NULL,
                id_detalle_preparacion INTEGER NOT NULL,
                fecha_devolucion DATE NOT NULL,
                cantidad_pares INTEGER NOT NULL,
                motivo TEXT,
                id_ubicacion_destino INTEGER,
                procesada INTEGER DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones (id_preparacion),
                FOREIGN KEY (id_detalle_preparacion) REFERENCES preparaciones_detalle (id_detalle),
                FOREIGN KEY (id_ubicacion_destino) REFERENCES ubicaciones (id_ubicacion)
            )
        ''')
        print("   ✅ Tabla devoluciones creada")

        # ========================================
        # 6. ÍNDICES para optimización
        # ========================================
        print("\n⚡ Creando índices para optimización...")

        indices = [
            "CREATE INDEX IF NOT EXISTS idx_preparaciones_fecha ON preparaciones(fecha_preparacion)",
            "CREATE INDEX IF NOT EXISTS idx_preparaciones_estado ON preparaciones(estado)",
            "CREATE INDEX IF NOT EXISTS idx_prep_detalle_preparacion ON preparaciones_detalle(id_preparacion)",
            "CREATE INDEX IF NOT EXISTS idx_prep_detalle_variante ON preparaciones_detalle(id_variante)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_v2_preparacion ON ventas_v2(id_preparacion)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_v2_fecha ON ventas_v2(fecha_venta)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_v2_variante ON ventas_v2(id_variante)",
            "CREATE INDEX IF NOT EXISTS idx_ventas_v2_cliente ON ventas_v2(cliente)",
            "CREATE INDEX IF NOT EXISTS idx_devoluciones_preparacion ON devoluciones(id_preparacion)"
        ]

        for idx in indices:
            cursor.execute(idx)

        print("   ✅ Índices creados")

        # ========================================
        # 7. VISTAS para consultas frecuentes
        # ========================================
        print("\n📊 Creando vistas...")

        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vista_preparaciones_completa AS
            SELECT
                p.*,
                u.nombre as ubicacion_origen,
                COUNT(DISTINCT pd.id_variante) as total_variantes_real,
                SUM(pd.cantidad_pares) as total_pares_real,
                SUM(pd.cantidad_vendida) as total_vendido,
                SUM(pd.cantidad_pares - pd.cantidad_vendida - pd.cantidad_devuelta) as pendiente_vender
            FROM preparaciones p
            LEFT JOIN ubicaciones u ON p.id_ubicacion_origen = u.id_ubicacion
            LEFT JOIN preparaciones_detalle pd ON p.id_preparacion = pd.id_preparacion
            GROUP BY p.id_preparacion
        ''')

        cursor.execute('''
            CREATE VIEW IF NOT EXISTS vista_ventas_detallada AS
            SELECT
                v.*,
                va.codigo_producto,
                va.cuero,
                va.color,
                va.serie_tallas,
                pb.tipo as tipo_producto,
                p.fecha_preparacion,
                p.dia_venta
            FROM ventas_v2 v
            JOIN variantes va ON v.id_variante = va.id_variante
            JOIN productos_base pb ON va.codigo_producto = pb.codigo_producto
            JOIN preparaciones p ON v.id_preparacion = p.id_preparacion
        ''')

        print("   ✅ Vistas creadas")

        # ========================================
        # COMMIT FINAL
        # ========================================
        conn.commit()

        print("\n" + "="*60)
        print("✅ MIGRACIÓN FASE 3+4 COMPLETADA EXITOSAMENTE")
        print("="*60)
        print(f"\n📄 Respaldo disponible en: {backup}")
        print("📊 Nuevas tablas creadas:")
        print("   - preparaciones")
        print("   - preparaciones_detalle")
        print("   - ventas_v2")
        print("   - configuracion_sistema")
        print("   - devoluciones")
        print("\n📈 Nuevas funcionalidades:")
        print("   ✅ Preparación de mercadería por día")
        print("   ✅ Ventas vinculadas a preparación")
        print("   ✅ Actualización automática de inventario")
        print("   ✅ Registro en docenas")
        print("   ✅ Entrega automática de pedidos")
        print("   ✅ Control de devoluciones")
        print("\n⚠️  Próximo paso: Ejecutar app_v1_3.py\n")

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
            'preparaciones',
            'preparaciones_detalle',
            'ventas_v2',
            'configuracion_sistema',
            'devoluciones'
        ]

        print("\n📋 Tablas nuevas:")
        for tabla in tablas_requeridas:
            existe = tabla in tablas
            status = "✅" if existe else "❌"
            print(f"   {status} {tabla}")

        # Contar configuraciones
        cursor.execute("SELECT COUNT(*) FROM configuracion_sistema")
        count_configs = cursor.fetchone()[0]

        print(f"\n📊 Configuraciones del sistema: {count_configs}")

        return True

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

    finally:
        conn.close()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("SISTEMA DE GESTIÓN DE CALZADO - MIGRACIÓN FASE 3+4")
    print("="*60)
    print("\nEste script agregará:")
    print("  ✅ Sistema de Preparación de Mercadería")
    print("  ✅ Ventas vinculadas a Preparación")
    print("  ✅ Actualización automática de Inventario")
    print("  ✅ Control de Devoluciones")
    print("\n⚠️  REQUISITO: Debes haber ejecutado 'migracion_v1_2.py' primero")
    print("Se creará un respaldo automático antes de proceder.\n")

    respuesta = input("¿Deseas continuar? (s/n): ")

    if respuesta.lower() == 's':
        if ejecutar_migracion():
            verificar_migracion()
            print("\n✅ Migración completada. El sistema está listo para Fase 3+4.\n")
        else:
            print("\n❌ La migración falló. Revisa los errores arriba.\n")
    else:
        print("\n❌ Migración cancelada.\n")
