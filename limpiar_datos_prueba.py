"""
Script para limpiar datos de prueba del sistema
Mantiene la estructura de la base de datos pero elimina todos los registros transaccionales
"""

import sqlite3
import shutil
from datetime import datetime

def limpiar_datos_prueba(limpiar_catalogo=False):
    """
    Limpia todos los datos de prueba del sistema

    Args:
        limpiar_catalogo: Si True, también limpia variantes_base y ubicaciones
    """

    # Crear backup antes de limpiar
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'calzado_backup_antes_limpieza_{timestamp}.db'

    print(f"\n{'='*70}")
    print("🧹 LIMPIEZA DE DATOS DE PRUEBA")
    print(f"{'='*70}\n")

    try:
        # Paso 1: Crear backup
        print("📦 Paso 1: Creando backup de seguridad...")
        shutil.copy2('calzado.db', backup_file)
        print(f"✅ Backup creado: {backup_file}")

        # Paso 2: Conectar a la base de datos
        print("\n🔌 Paso 2: Conectando a la base de datos...")
        conn = sqlite3.connect('calzado.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        print("✅ Conexión establecida")

        # Paso 3: Contar registros ANTES de limpiar
        print("\n📊 Paso 3: Contando registros actuales...")

        tablas_transaccionales = [
            'ventas_detalle',
            'ventas_v2',
            'pagos',
            'cuentas_por_cobrar',
            'preparaciones_detalle',
            'preparaciones',
            'inventario',
            'productos_producidos',
            'clientes'
        ]

        registros_antes = {}
        for tabla in tablas_transaccionales:
            cursor.execute(f'SELECT COUNT(*) as total FROM {tabla}')
            total = cursor.fetchone()['total']
            registros_antes[tabla] = total
            print(f"   - {tabla}: {total} registros")

        if limpiar_catalogo:
            cursor.execute('SELECT COUNT(*) as total FROM variantes_base')
            registros_antes['variantes_base'] = cursor.fetchone()['total']
            print(f"   - variantes_base: {registros_antes['variantes_base']} registros")

            cursor.execute('SELECT COUNT(*) as total FROM ubicaciones')
            registros_antes['ubicaciones'] = cursor.fetchone()['total']
            print(f"   - ubicaciones: {registros_antes['ubicaciones']} registros")

        # Paso 4: Confirmar limpieza
        print("\n⚠️  ADVERTENCIA: Esta operación NO se puede deshacer")
        print("   (excepto restaurando el backup)")
        respuesta = input("\n¿Estás seguro de que deseas limpiar todos los datos? (SI/no): ")

        if respuesta.upper() != 'SI':
            print("\n❌ Limpieza cancelada por el usuario")
            conn.close()
            return

        # Paso 5: Deshabilitar foreign keys temporalmente
        print("\n🔓 Paso 4: Deshabilitando restricciones de foreign keys...")
        cursor.execute('PRAGMA foreign_keys = OFF')

        # Paso 6: Limpiar tablas transaccionales (orden importante por foreign keys)
        print("\n🗑️  Paso 5: Limpiando tablas transaccionales...")

        # Orden de limpieza (de dependiente a principal)
        orden_limpieza = [
            'ventas_detalle',
            'pagos',
            'cuentas_por_cobrar',
            'ventas_v2',
            'preparaciones_detalle',
            'preparaciones',
            'inventario',
            'productos_producidos',
            'clientes'
        ]

        for tabla in orden_limpieza:
            cursor.execute(f'DELETE FROM {tabla}')
            print(f"   ✓ {tabla} limpiada ({registros_antes[tabla]} registros eliminados)")

        # Paso 7: Limpiar catálogo si se solicitó
        if limpiar_catalogo:
            print("\n🗑️  Paso 6: Limpiando catálogo...")
            cursor.execute('DELETE FROM variantes_base')
            print(f"   ✓ variantes_base limpiada ({registros_antes['variantes_base']} registros eliminados)")

            cursor.execute('DELETE FROM ubicaciones')
            print(f"   ✓ ubicaciones limpiada ({registros_antes['ubicaciones']} registros eliminados)")

        # Paso 8: Resetear contadores de autoincremento
        print("\n🔄 Paso 7: Reseteando contadores de ID...")
        cursor.execute('DELETE FROM sqlite_sequence')
        print("   ✓ Contadores reseteados")

        # Paso 9: Reactivar foreign keys
        print("\n🔒 Paso 8: Reactivando restricciones de foreign keys...")
        cursor.execute('PRAGMA foreign_keys = ON')

        # Paso 10: Commit
        print("\n💾 Paso 9: Guardando cambios...")
        conn.commit()

        # Paso 11: Verificar limpieza
        print("\n✅ Paso 10: Verificando limpieza...")
        total_registros = 0
        for tabla in tablas_transaccionales:
            cursor.execute(f'SELECT COUNT(*) as total FROM {tabla}')
            total = cursor.fetchone()['total']
            total_registros += total

        print(f"\n{'='*70}")
        print("✅ LIMPIEZA COMPLETADA EXITOSAMENTE")
        print(f"{'='*70}\n")
        print(f"📊 Total de registros eliminados: {sum(registros_antes.values())}")
        print(f"📊 Total de registros restantes en tablas transaccionales: {total_registros}")
        print(f"\n📦 Backup disponible en: {backup_file}")
        print("\n💡 Para restaurar el backup en caso de error:")
        print(f"   cp {backup_file} calzado.db")

        if not limpiar_catalogo:
            print("\n📝 NOTA: Se mantuvieron los datos de catálogo:")
            cursor.execute('SELECT COUNT(*) FROM variantes_base')
            print(f"   - Variantes base: {cursor.fetchone()[0]} modelos")
            cursor.execute('SELECT COUNT(*) FROM ubicaciones')
            print(f"   - Ubicaciones: {cursor.fetchone()[0]} ubicaciones")

        print("\n🎯 El sistema está listo para empezar desde cero")
        print("   Los próximos códigos serán:")
        print("   - Primer cliente: CLI-000001")
        print("   - Primera venta: VD20260116-001")
        print("   - Primera cuenta: CC-000001")
        print(f"\n{'='*70}\n")

        conn.close()

    except Exception as e:
        print(f"\n❌ ERROR durante la limpieza: {str(e)}")
        print(f"📦 Puedes restaurar el backup con:")
        print(f"   cp {backup_file} calzado.db")
        if conn:
            conn.rollback()
            conn.close()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧹 SCRIPT DE LIMPIEZA DE DATOS DE PRUEBA")
    print("="*70)
    print("\nEste script eliminará TODOS los datos transaccionales:")
    print("  ✓ Ventas")
    print("  ✓ Cuentas por cobrar")
    print("  ✓ Pagos")
    print("  ✓ Clientes")
    print("  ✓ Productos producidos")
    print("  ✓ Inventario")
    print("  ✓ Preparaciones")

    print("\n¿También deseas limpiar el CATÁLOGO?")
    print("  - Variantes base (modelos de calzado)")
    print("  - Ubicaciones (tiendas y almacenes)")

    limpiar_catalogo_input = input("\n¿Limpiar catálogo? (si/NO): ")
    limpiar_catalogo = limpiar_catalogo_input.lower() == 'si'

    limpiar_datos_prueba(limpiar_catalogo)
