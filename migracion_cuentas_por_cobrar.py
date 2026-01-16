"""
Script de migración para módulo de Cuentas por Cobrar
Crea tablas: clientes, cuentas_por_cobrar, pagos
Ejecutar: python migracion_cuentas_por_cobrar.py
"""

import sqlite3
from datetime import datetime

DATABASE = 'calzado.db'

def crear_backup():
    """Crear backup de la base de datos"""
    import shutil
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_cuentas_{timestamp}.db'

    try:
        shutil.copy2(DATABASE, backup_file)
        print(f"✅ Backup creado: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ Error creando backup: {str(e)}")
        return False

def migrar():
    """Ejecutar migración completa"""
    print("\n" + "="*70)
    print("🔧 MIGRACIÓN: Módulo de Cuentas por Cobrar")
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
        # =================================================================
        # TABLA: clientes
        # =================================================================
        print("\n📋 Creando tabla 'clientes'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT,
                nombre_comercial TEXT,
                tipo_documento TEXT DEFAULT 'DNI',
                numero_documento TEXT UNIQUE,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                limite_credito REAL DEFAULT 0,
                dias_credito INTEGER DEFAULT 30,
                activo INTEGER DEFAULT 1,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Tabla 'clientes' creada")

        # =================================================================
        # TABLA: cuentas_por_cobrar
        # =================================================================
        print("\n📋 Creando tabla 'cuentas_por_cobrar'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cuentas_por_cobrar (
                id_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER NOT NULL,
                id_venta INTEGER,
                codigo_cuenta TEXT UNIQUE,
                concepto TEXT NOT NULL,
                monto_total REAL NOT NULL,
                monto_pagado REAL DEFAULT 0,
                saldo_pendiente REAL,
                fecha_emision DATE NOT NULL,
                fecha_vencimiento DATE NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                dias_mora INTEGER DEFAULT 0,
                observaciones TEXT,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_venta) REFERENCES ventas_v2(id_venta)
            )
        ''')
        print("✅ Tabla 'cuentas_por_cobrar' creada")

        # =================================================================
        # TABLA: pagos
        # =================================================================
        print("\n📋 Creando tabla 'pagos'...")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pagos (
                id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cuenta INTEGER NOT NULL,
                codigo_pago TEXT UNIQUE,
                monto_pago REAL NOT NULL,
                metodo_pago TEXT DEFAULT 'efectivo',
                fecha_pago DATE NOT NULL,
                numero_comprobante TEXT,
                observaciones TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_cuenta) REFERENCES cuentas_por_cobrar(id_cuenta)
            )
        ''')
        print("✅ Tabla 'pagos' creada")

        # =================================================================
        # ÍNDICES para mejor rendimiento
        # =================================================================
        print("\n📋 Creando índices...")

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clientes_documento ON clientes(numero_documento)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_clientes_nombre ON clientes(nombre)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cuentas_cliente ON cuentas_por_cobrar(id_cliente)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cuentas_estado ON cuentas_por_cobrar(estado)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_cuentas_vencimiento ON cuentas_por_cobrar(fecha_vencimiento)')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_cuenta ON pagos(id_cuenta)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_pagos_fecha ON pagos(fecha_pago)')

        print("✅ Índices creados")

        # =================================================================
        # INSERTAR DATOS DE EJEMPLO (Opcional)
        # =================================================================
        print("\n📋 Insertando clientes de ejemplo...")

        clientes_ejemplo = [
            ('Juan', 'Pérez', 'Calzados Pérez', 'DNI', '12345678', '987654321', 'juan@example.com', 'Av. Principal 123', 5000, 30),
            ('María', 'García', 'Distribuidora García', 'RUC', '20123456789', '987654322', 'maria@example.com', 'Jr. Comercio 456', 10000, 45),
            ('Carlos', 'López', None, 'DNI', '87654321', '987654323', None, 'Calle Los Olivos 789', 3000, 15),
        ]

        for cliente in clientes_ejemplo:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO clientes
                    (nombre, apellido, nombre_comercial, tipo_documento, numero_documento,
                     telefono, email, direccion, limite_credito, dias_credito)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', cliente)
            except:
                pass  # Si ya existe, lo ignoramos

        print("✅ Clientes de ejemplo insertados")

        # =================================================================
        # COMMIT Y FINALIZAR
        # =================================================================
        conn.commit()

        # Verificar tablas creadas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%cliente%' OR name='pagos' OR name='cuentas_por_cobrar' ORDER BY name")
        tablas = cursor.fetchall()

        print("\n📊 Tablas del módulo de Cuentas por Cobrar:")
        for tabla in tablas:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla[0]}")
            count = cursor.fetchone()[0]
            print(f"  ✓ {tabla[0]}: {count} registros")

        conn.close()

        print("\n" + "="*70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("="*70)
        print("\n💡 Próximos pasos:")
        print("   1. Ejecutar: python app_v2.py")
        print("   2. Acceder al módulo de Cuentas por Cobrar")
        print("   3. Registrar clientes y cuentas")
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
