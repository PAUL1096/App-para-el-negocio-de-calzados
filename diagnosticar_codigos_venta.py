"""
Script para diagnosticar y solucionar problema de códigos de venta duplicados
"""
import sqlite3

DATABASE = 'calzado.db'

conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

print("="*80)
print("🔍 DIAGNÓSTICO DE CÓDIGOS DE VENTA")
print("="*80)

# Ver códigos existentes
cursor.execute('''
    SELECT codigo_venta, fecha_venta, cliente, total_final
    FROM ventas_v2
    ORDER BY fecha_venta DESC, codigo_venta DESC
    LIMIT 20
''')

ventas = cursor.fetchall()

print(f"\n📋 Últimas {len(ventas)} ventas registradas:")
print("-" * 80)
for venta in ventas:
    print(f"  {venta[0]:<20} | {venta[1]} | {venta[2]:<30} | S/ {venta[3]:.2f}")

# Buscar duplicados
cursor.execute('''
    SELECT codigo_venta, COUNT(*) as total
    FROM ventas_v2
    GROUP BY codigo_venta
    HAVING COUNT(*) > 1
''')

duplicados = cursor.fetchall()

if duplicados:
    print("\n❌ CÓDIGOS DUPLICADOS ENCONTRADOS:")
    print("-" * 80)
    for dup in duplicados:
        print(f"  {dup[0]}: {dup[1]} veces")
else:
    print("\n✅ No hay códigos duplicados")

# Ver el patrón de códigos de hoy
from datetime import datetime
fecha_hoy = datetime.now().strftime('%Y%m%d')

cursor.execute('''
    SELECT codigo_venta
    FROM ventas_v2
    WHERE codigo_venta LIKE ?
    ORDER BY codigo_venta DESC
    LIMIT 10
''', (f'VD{fecha_hoy}-%',))

ventas_hoy = cursor.fetchall()

print(f"\n📅 Ventas directas de hoy ({fecha_hoy}):")
print("-" * 80)
if ventas_hoy:
    for v in ventas_hoy:
        print(f"  {v[0]}")

    # Extraer el número más alto
    ultimo_codigo = ventas_hoy[0][0]
    print(f"\n📊 Último código: {ultimo_codigo}")

    try:
        # Extraer número del código VD20251226-XXX
        partes = ultimo_codigo.split('-')
        if len(partes) == 2:
            numero = int(partes[1])
            print(f"📊 Último número: {numero}")
            print(f"📊 Próximo código debería ser: VD{fecha_hoy}-{numero+1:03d}")
    except:
        print("⚠️  No se pudo extraer número del código")
else:
    print(f"  Ninguna venta directa hoy")
    print(f"  Próximo código debería ser: VD{fecha_hoy}-001")

# Ver ventas regulares de hoy
cursor.execute('''
    SELECT codigo_venta
    FROM ventas_v2
    WHERE codigo_venta LIKE ?
    ORDER BY codigo_venta DESC
    LIMIT 10
''', (f'V{fecha_hoy}-%',))

ventas_regulares_hoy = cursor.fetchall()

print(f"\n📅 Ventas regulares de hoy ({fecha_hoy}):")
print("-" * 80)
if ventas_regulares_hoy:
    for v in ventas_regulares_hoy:
        print(f"  {v[0]}")
else:
    print(f"  Ninguna venta regular hoy")

# Contar total de ventas
cursor.execute('SELECT COUNT(*) FROM ventas_v2')
total = cursor.fetchone()[0]

print(f"\n📊 Total de ventas en BD: {total}")

conn.close()

print("\n" + "="*80)
print("💡 SIGUIENTE PASO:")
print("="*80)
print("Si hay problemas, ejecuta: python limpiar_codigos_duplicados.py")
print("="*80)
