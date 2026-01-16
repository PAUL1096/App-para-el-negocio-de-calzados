"""
Script para verificar el estado de la base de datos antes de migrar
"""
import sqlite3

DATABASE = 'calzado.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("="*80)
print("VERIFICACIÓN DE BASE DE DATOS")
print("="*80)

# Verificar si existe ventas_detalle
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ventas_detalle'")
tabla_detalle = cursor.fetchone()

if tabla_detalle:
    print("✅ Tabla 'ventas_detalle' EXISTE")
else:
    print("❌ Tabla 'ventas_detalle' NO EXISTE - NECESITAS EJECUTAR LA MIGRACIÓN")

# Verificar estructura de ventas_v2
print("\n📋 Estructura actual de ventas_v2:")
cursor.execute("PRAGMA table_info(ventas_v2)")
columnas = cursor.fetchall()

tiene_id_cliente = False
tiene_id_producto = False

for col in columnas:
    col_id, name, type_, notnull, default, pk = col
    print(f"  - {name} ({type_})")
    if name == 'id_cliente':
        tiene_id_cliente = True
    if name == 'id_producto':
        tiene_id_producto = True

print("\n" + "="*80)
print("DIAGNÓSTICO:")
print("="*80)

if not tabla_detalle:
    print("❌ CRÍTICO: Falta tabla ventas_detalle")
    print("   Acción: Ejecutar migracion_ventas_multiproducto.py")

if tiene_id_producto:
    print("⚠️  ADVERTENCIA: ventas_v2 tiene columna 'id_producto'")
    print("   Esto indica que la migración NO se ha ejecutado")
    print("   Acción: Ejecutar migracion_ventas_multiproducto.py")

if tiene_id_cliente:
    print("✅ Columna 'id_cliente' existe en ventas_v2")
else:
    print("❌ Falta columna 'id_cliente' en ventas_v2")
    print("   Acción: Ejecutar migracion_integracion_ventas_clientes.py PRIMERO")

conn.close()

print("\n" + "="*80)
print("SIGUIENTE PASO:")
print("="*80)
if not tabla_detalle:
    print("Ejecuta: python migracion_ventas_multiproducto.py")
else:
    print("Tu base de datos está actualizada ✓")
print("="*80)
