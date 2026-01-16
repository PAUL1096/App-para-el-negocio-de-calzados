"""
Script para insertar datos iniciales mínimos necesarios para el funcionamiento del sistema
Ejecutar DESPUÉS de limpiar_datos_prueba.py
"""

import sqlite3

def insertar_datos_iniciales():
    """Inserta datos mínimos necesarios para que el sistema funcione"""

    print("\n" + "="*70)
    print("📝 INSERCIÓN DE DATOS INICIALES")
    print("="*70 + "\n")

    try:
        conn = sqlite3.connect('calzado.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verificar que no haya ubicaciones
        cursor.execute('SELECT COUNT(*) as total FROM ubicaciones')
        total_ubicaciones = cursor.fetchone()['total']

        if total_ubicaciones > 0:
            print(f"⚠️  Ya existen {total_ubicaciones} ubicación(es) en el sistema")
            print("   No se insertarán datos iniciales")
            conn.close()
            return

        print("📍 Creando ubicación inicial: Almacén Central...")

        # Insertar ubicación por defecto
        cursor.execute('''
            INSERT INTO ubicaciones (nombre, tipo, direccion, activo)
            VALUES (?, ?, ?, ?)
        ''', ('Almacén Central', 'almacen', 'Dirección del almacén principal', 1))

        id_ubicacion = cursor.lastrowid

        conn.commit()

        print(f"✅ Ubicación creada exitosamente (ID: {id_ubicacion})")
        print("\n💡 IMPORTANTE: Puedes crear más ubicaciones desde el módulo /ubicaciones")
        print("   Ejemplos: Tienda 1, Tienda 2, Bodega, etc.")

        print("\n" + "="*70)
        print("✅ DATOS INICIALES INSERTADOS CORRECTAMENTE")
        print("="*70 + "\n")

        print("🎯 El sistema está listo para usar:")
        print("   1. Crear variantes base (modelos) en /catalogo-variantes")
        print("   2. Producir productos en /produccion")
        print("   3. Ingresar a inventario")
        print("   4. Crear clientes (opcional)")
        print("   5. Realizar ventas")
        print("\n")

        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    insertar_datos_iniciales()
