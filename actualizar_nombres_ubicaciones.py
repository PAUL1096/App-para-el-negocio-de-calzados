"""
Script para actualizar nombres de ubicaciones en la base de datos
Ejecutar: python actualizar_nombres_ubicaciones.py
"""

import sqlite3

DATABASE = 'calzado.db'

def actualizar_nombres():
    """Actualiza los nombres de las ubicaciones"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("🔧 Actualizando nombres de ubicaciones...")
    print("-" * 50)

    # Mostrar ubicaciones actuales
    print("\n📋 Ubicaciones actuales:")
    cursor.execute('SELECT id_ubicacion, nombre, tipo FROM ubicaciones ORDER BY nombre')
    ubicaciones_antes = cursor.fetchall()
    for ub in ubicaciones_antes:
        print(f"  {ub[0]}. {ub[1]} ({ub[2]})")

    # Actualizar Tienda Principal
    cursor.execute('''
        UPDATE ubicaciones
        SET nombre = 'Tienda en Calzaplaza',
            direccion = 'Tienda principal ubicada en Calzaplaza'
        WHERE nombre LIKE '%Tienda Principal%' OR nombre LIKE '%tienda principal%'
    ''')
    print(f"\n✅ Actualizada 'Tienda Principal' → 'Tienda en Calzaplaza' ({cursor.rowcount} filas)")

    # Actualizar Tienda Secundaria
    cursor.execute('''
        UPDATE ubicaciones
        SET nombre = 'Tienda en CalzaPe',
            direccion = 'Tienda secundaria ubicada en CalzaPe'
        WHERE nombre LIKE '%Tienda Secundaria%' OR nombre LIKE '%tienda secundaria%'
    ''')
    print(f"✅ Actualizada 'Tienda Secundaria' → 'Tienda en CalzaPe' ({cursor.rowcount} filas)")

    # Actualizar inventario (referencias al nombre)
    cursor.execute('''
        UPDATE inventario
        SET id_ubicacion = (
            SELECT id_ubicacion FROM ubicaciones WHERE nombre = 'Tienda en Calzaplaza' LIMIT 1
        )
        WHERE id_ubicacion IN (
            SELECT id_ubicacion FROM ubicaciones WHERE nombre = 'Tienda en Calzaplaza'
        )
    ''')

    cursor.execute('''
        UPDATE inventario
        SET id_ubicacion = (
            SELECT id_ubicacion FROM ubicaciones WHERE nombre = 'Tienda en CalzaPe' LIMIT 1
        )
        WHERE id_ubicacion IN (
            SELECT id_ubicacion FROM ubicaciones WHERE nombre = 'Tienda en CalzaPe'
        )
    ''')

    conn.commit()

    # Mostrar ubicaciones actualizadas
    print("\n📋 Ubicaciones actualizadas:")
    cursor.execute('SELECT id_ubicacion, nombre, tipo, direccion FROM ubicaciones ORDER BY nombre')
    ubicaciones_despues = cursor.fetchall()
    for ub in ubicaciones_despues:
        print(f"  {ub[0]}. {ub[1]} ({ub[2]})")
        if ub[3]:
            print(f"      → {ub[3]}")

    conn.close()
    print("\n✅ Actualización completada exitosamente!")
    print("-" * 50)

if __name__ == '__main__':
    try:
        actualizar_nombres()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
