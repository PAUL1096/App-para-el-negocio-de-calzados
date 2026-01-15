"""
Migración: Permitir id_cliente NULL en cuentas_por_cobrar
=========================================================

Fecha: 2026-01-06
Objetivo: Permitir crear cuentas por cobrar sin cliente (para "Cliente Desconocido")

Problema:
- Al vender a crédito sin seleccionar cliente, el sistema falla con:
  "NOT NULL constraint failed: cuentas_por_cobrar.id_cliente"

Solución:
- Recrear tabla cuentas_por_cobrar permitiendo id_cliente NULL
"""

import sqlite3
from datetime import datetime

def migrar():
    print("=" * 70)
    print("MIGRACIÓN: Permitir id_cliente NULL en cuentas_por_cobrar")
    print("=" * 70)

    conn = sqlite3.connect('calzado.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        print("\n📋 Paso 1: Verificando tabla cuentas_por_cobrar...")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cuentas_por_cobrar'")
        existe_tabla = cursor.fetchone()

        if not existe_tabla:
            print("⚠️  La tabla 'cuentas_por_cobrar' no existe")
            conn.close()
            return

        print("✅ Tabla encontrada")

        print("\n📋 Paso 2: Respaldando datos existentes...")

        # Copiar datos a tabla temporal
        cursor.execute('''
            CREATE TABLE cuentas_por_cobrar_backup AS
            SELECT * FROM cuentas_por_cobrar
        ''')

        registros = cursor.execute('SELECT COUNT(*) FROM cuentas_por_cobrar_backup').fetchone()[0]
        print(f"✅ {registros} registros respaldados")

        print("\n📋 Paso 3: Recreando tabla sin restricción NOT NULL...")

        # Eliminar tabla original
        cursor.execute('DROP TABLE cuentas_por_cobrar')

        # Recrear tabla permitiendo id_cliente NULL
        cursor.execute('''
            CREATE TABLE cuentas_por_cobrar (
                id_cuenta INTEGER PRIMARY KEY AUTOINCREMENT,
                id_cliente INTEGER,  -- Ahora permite NULL
                id_venta INTEGER,
                codigo_cuenta TEXT UNIQUE NOT NULL,
                concepto TEXT,
                monto_total REAL NOT NULL,
                monto_pagado REAL DEFAULT 0,
                saldo_pendiente REAL NOT NULL,
                fecha_emision DATE DEFAULT (DATE('now')),
                fecha_vencimiento DATE,
                estado TEXT DEFAULT 'pendiente',
                observaciones TEXT,
                FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente),
                FOREIGN KEY (id_venta) REFERENCES ventas_v2(id_venta)
            )
        ''')

        print("✅ Tabla recreada con id_cliente nullable")

        print("\n📋 Paso 4: Restaurando datos...")

        # Restaurar datos
        cursor.execute('''
            INSERT INTO cuentas_por_cobrar
            SELECT * FROM cuentas_por_cobrar_backup
        ''')

        print(f"✅ {registros} registros restaurados")

        # Eliminar backup
        cursor.execute('DROP TABLE cuentas_por_cobrar_backup')

        conn.commit()

        print("\n" + "=" * 70)
        print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 70)
        print("\nCambios realizados:")
        print("  • Campo id_cliente ahora permite NULL")
        print("  • Ventas a crédito sin cliente ahora funcionarán")
        print(f"  • {registros} cuentas existentes preservadas")

    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        print("Revertiendo cambios...")
        conn.rollback()

    finally:
        conn.close()

if __name__ == '__main__':
    migrar()
