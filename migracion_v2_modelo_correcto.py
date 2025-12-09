"""
Script de Migración: Rediseño completo del modelo de datos
Versión: 2.0 - Modelo Correcto
Fecha: 2025-12-09
Descripción: Restructura completamente el sistema para separar:
             - Variantes Base (catálogo de modelos)
             - Productos Producidos (materializaciones concretas)
             - Inventario (apuntando a productos)
"""

import sqlite3
import os
from datetime import datetime

def crear_backup(db_path):
    """Crea backup de la base de datos antes de migrar"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = db_path.replace('.db', f'_backup_v2_{timestamp}.db')

    print(f"📦 Creando backup: {backup_path}")

    import shutil
    shutil.copy2(db_path, backup_path)

    print(f"✅ Backup creado exitosamente")
    return backup_path

def migrar_modelo_v2(db_path='calzado.db'):
    """Ejecuta la migración al nuevo modelo v2"""

    print("=" * 80)
    print("🔧 MIGRACIÓN V2.0: Rediseño completo del modelo de datos")
    print("=" * 80)

    if not os.path.exists(db_path):
        print(f"❌ Error: No se encuentra la base de datos en {db_path}")
        return False

    # Crear backup
    backup_path = crear_backup(db_path)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("\n" + "="*80)
        print("FASE 1: Renombrar tablas antiguas como backup")
        print("="*80)

        tablas_a_renombrar = [
            'variantes',
            'inventario',
            'preparaciones_detalle',
            'ventas_v2',
            'pedidos_detalle'
        ]

        for tabla in tablas_a_renombrar:
            try:
                cursor.execute(f"ALTER TABLE {tabla} RENAME TO {tabla}_old")
                print(f"✅ Tabla '{tabla}' respaldada como '{tabla}_old'")
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    print(f"⚠️  Tabla '{tabla}' no existe, continuando...")
                else:
                    raise

        print("\n" + "="*80)
        print("FASE 2: Crear nuevas tablas con diseño correcto")
        print("="*80)

        # Tabla 0: UBICACIONES (tabla base necesaria)
        print("\n📋 Creando tabla: ubicaciones")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id_ubicacion INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                direccion TEXT,
                tipo TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla 'ubicaciones' creada")

        # Insertar ubicaciones por defecto si no existen
        ubicaciones_default = [
            ('Casa', 'Lugar de producción', 'Producción'),
            ('Tienda Principal', 'Tienda principal de ventas', 'Venta'),
            ('Tienda Secundaria', 'Tienda secundaria', 'Venta')
        ]

        for nombre, direccion, tipo in ubicaciones_default:
            try:
                cursor.execute('''
                    INSERT INTO ubicaciones (nombre, direccion, tipo)
                    VALUES (?, ?, ?)
                ''', (nombre, direccion, tipo))
                print(f"   ✅ Ubicación '{nombre}' insertada")
            except sqlite3.IntegrityError:
                print(f"   ⚠️  Ubicación '{nombre}' ya existe")

        # Tabla 1: VARIANTES_BASE (Catálogo de modelos)
        print("\n📋 Creando tabla: variantes_base")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS variantes_base (
                id_variante_base INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_interno TEXT UNIQUE NOT NULL,
                tipo_calzado TEXT NOT NULL,
                tipo_horma TEXT NOT NULL,
                segmento TEXT NOT NULL,
                descripcion TEXT,
                activo INTEGER DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla 'variantes_base' creada")

        # Tabla 2: PRODUCTOS_PRODUCIDOS (Materializaciones concretas)
        print("\n📋 Creando tabla: productos_producidos")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos_producidos (
                id_producto INTEGER PRIMARY KEY AUTOINCREMENT,
                id_variante_base INTEGER NOT NULL,
                cuero TEXT NOT NULL,
                color_cuero TEXT NOT NULL,
                suela TEXT NOT NULL,
                forro TEXT,
                serie_tallas TEXT NOT NULL,
                pares_por_docena INTEGER DEFAULT 12,
                costo_unitario DECIMAL(10,2) NOT NULL,
                precio_sugerido DECIMAL(10,2) NOT NULL,
                fecha_produccion DATE DEFAULT (DATE('now')),
                cantidad_total_pares INTEGER DEFAULT 0,
                observaciones TEXT,
                activo INTEGER DEFAULT 1,
                FOREIGN KEY (id_variante_base) REFERENCES variantes_base(id_variante_base)
            )
        ''')
        print("✅ Tabla 'productos_producidos' creada")

        # Tabla 3: INVENTARIO (actualizado para apuntar a productos)
        print("\n📋 Creando tabla: inventario")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventario (
                id_inventario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_producto INTEGER NOT NULL,
                id_ubicacion INTEGER NOT NULL,
                tipo_stock TEXT CHECK(tipo_stock IN ('general', 'pedido')) DEFAULT 'general',
                cantidad_pares INTEGER DEFAULT 0,
                fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                id_pedido INTEGER,
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto),
                FOREIGN KEY (id_ubicacion) REFERENCES ubicaciones(id_ubicacion),
                FOREIGN KEY (id_pedido) REFERENCES pedidos_cliente(id_pedido)
            )
        ''')
        print("✅ Tabla 'inventario' creada")

        # Tabla 4: PREPARACIONES_DETALLE (actualizado)
        print("\n📋 Creando tabla: preparaciones_detalle")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preparaciones_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_preparacion INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                tipo_stock TEXT CHECK(tipo_stock IN ('general', 'pedido')) DEFAULT 'general',
                id_pedido INTEGER,
                cantidad_pares INTEGER NOT NULL,
                cantidad_vendida INTEGER DEFAULT 0,
                cantidad_devuelta INTEGER DEFAULT 0,
                FOREIGN KEY (id_preparacion) REFERENCES preparaciones(id_preparacion),
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto),
                FOREIGN KEY (id_pedido) REFERENCES pedidos_cliente(id_pedido)
            )
        ''')
        print("✅ Tabla 'preparaciones_detalle' creada")

        # Tabla 5: VENTAS_V2 (actualizado)
        print("\n📋 Creando tabla: ventas_v2")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas_v2 (
                id_venta INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_venta TEXT UNIQUE NOT NULL,
                id_preparacion INTEGER NOT NULL,
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
        print("✅ Tabla 'ventas_v2' creada")

        # Tabla 6: PEDIDOS_DETALLE (actualizado)
        print("\n📋 Creando tabla: pedidos_detalle")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos_detalle (
                id_detalle INTEGER PRIMARY KEY AUTOINCREMENT,
                id_pedido INTEGER NOT NULL,
                id_producto INTEGER NOT NULL,
                cantidad_pares INTEGER NOT NULL,
                precio_acordado DECIMAL(10,2),
                observaciones TEXT,
                FOREIGN KEY (id_pedido) REFERENCES pedidos_cliente(id_pedido),
                FOREIGN KEY (id_producto) REFERENCES productos_producidos(id_producto)
            )
        ''')
        print("✅ Tabla 'pedidos_detalle' creada")

        print("\n" + "="*80)
        print("FASE 3: Crear índices para optimización")
        print("="*80)

        indices = [
            ("idx_variantes_base_codigo", "variantes_base(codigo_interno)"),
            ("idx_productos_variante", "productos_producidos(id_variante_base)"),
            ("idx_inventario_producto", "inventario(id_producto)"),
            ("idx_inventario_ubicacion", "inventario(id_ubicacion)"),
            ("idx_prep_detalle_producto", "preparaciones_detalle(id_producto)"),
            ("idx_ventas_producto", "ventas_v2(id_producto)"),
            ("idx_ventas_fecha", "ventas_v2(fecha_venta)")
        ]

        for nombre_idx, definicion in indices:
            cursor.execute(f"CREATE INDEX IF NOT EXISTS {nombre_idx} ON {definicion}")
            print(f"✅ Índice '{nombre_idx}' creado")

        print("\n" + "="*80)
        print("FASE 4: Insertar datos de ejemplo")
        print("="*80)

        # Insertar variantes base de ejemplo
        print("\n📋 Insertando variantes base de ejemplo...")
        variantes_ejemplo = [
            ('M-CASUAL-01', 'Casual', 'Americano', 'Adulto Caballero', 'Modelo casual básico'),
            ('M-FORMAL-01', 'Formal', 'Punta Pala', 'Adulto Caballero', 'Modelo formal elegante'),
            ('M-DEPORTIVO-01', 'Deportivo', 'Deportiva', 'Adulto Caballero', 'Modelo deportivo'),
        ]

        for codigo, tipo, horma, segmento, desc in variantes_ejemplo:
            try:
                cursor.execute('''
                    INSERT INTO variantes_base
                    (codigo_interno, tipo_calzado, tipo_horma, segmento, descripcion)
                    VALUES (?, ?, ?, ?, ?)
                ''', (codigo, tipo, horma, segmento, desc))
                print(f"✅ Variante base '{codigo}' insertada")
            except sqlite3.IntegrityError:
                print(f"⚠️  Variante '{codigo}' ya existe")

        conn.commit()

        print("\n" + "="*80)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*80)
        print(f"\n📦 Backup disponible en: {backup_path}")
        print("\n📝 RESUMEN DE CAMBIOS:")
        print("   • Tablas antiguas respaldadas con sufijo '_old'")
        print("   • Nueva tabla: variantes_base (catálogo de modelos)")
        print("   • Nueva tabla: productos_producidos (materializaciones)")
        print("   • Tabla inventario actualizada (apunta a productos)")
        print("   • Tablas preparaciones_detalle, ventas_v2, pedidos_detalle actualizadas")
        print("   • 3 variantes base de ejemplo insertadas")

        print("\n🎯 PRÓXIMOS PASOS:")
        print("   1. Ejecutar: python app_v2.py")
        print("   2. Crear variantes base desde el módulo Catálogo")
        print("   3. Producir productos desde el módulo Producción")
        print("   4. Ingresar productos al inventario")
        print("   5. Continuar flujo normal: Preparaciones → Ventas")

        print("\n⚠️  IMPORTANTE:")
        print("   • Sistema inicia LIMPIO (sin datos históricos)")
        print("   • Datos antiguos están en tablas con sufijo '_old'")
        print("   • Puedes eliminar tablas '_old' después de verificar")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        print(f"📦 Puedes restaurar desde el backup: {backup_path}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\n" + "🚀 INICIANDO MIGRACIÓN V2.0" + "\n")
    print("⚠️  ADVERTENCIA:")
    print("   Esta migración restructura COMPLETAMENTE el modelo de datos.")
    print("   Las tablas antiguas se respaldan como '_old'.")
    print("   El sistema iniciará LIMPIO sin datos históricos.")
    print("\n")

    respuesta = input("¿Deseas continuar? (escribe 'SI' para confirmar): ")

    if respuesta.upper() == 'SI':
        exito = migrar_modelo_v2()

        if exito:
            print("\n✅ Proceso completado exitosamente")
        else:
            print("\n❌ Proceso completado con errores")
    else:
        print("\n❌ Migración cancelada por el usuario")

    print("\n" + "="*80 + "\n")
