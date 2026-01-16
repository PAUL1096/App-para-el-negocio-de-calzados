"""
Script para limpiar archivos obsoletos del repositorio
Ejecutar DESPUÉS de haber limpiado los datos de prueba
"""

import os
import shutil
from datetime import datetime

def limpiar_repositorio():
    """Elimina archivos obsoletos del repositorio"""

    print("\n" + "="*70)
    print("🧹 LIMPIEZA DE REPOSITORIO")
    print("="*70 + "\n")

    # Archivos a eliminar
    archivos_a_eliminar = [
        # Aplicaciones antiguas
        'app.py',
        'app_v1_2.py',
        'app_v1_3.py',

        # Scripts de migración (ya ejecutados)
        'migracion_v1_2.py',
        'migracion_v2_modelo_correcto.py',
        'migracion_codigo_interno.py',
        'migracion_cuentas_por_cobrar.py',
        'migracion_fase_3_4.py',
        'migracion_integracion_ventas_clientes.py',
        'migracion_permitir_cliente_null.py',
        'migracion_plantilla_ingresos_parciales.py',
        'migracion_preparaciones_destino.py',
        'migracion_ventas_directas.py',
        'migracion_ventas_multiproducto.py',
        'reparar_migracion.py',

        # Scripts temporales/diagnóstico
        'diagnosticar_codigos_venta.py',
        'test_codigo_venta.py',
        'verificar_bd.py',
        'actualizar_nombres_ubicaciones.py',
        'import_data.py',

        # Bases de datos antiguas
        'inventario_calzado.db',
        'ventas_calzado.db',
    ]

    # Archivos de backup (patrón)
    backup_pattern = 'calzado_backup_'

    print("📋 Archivos que se eliminarán:\n")

    archivos_encontrados = []

    # Verificar archivos específicos
    for archivo in archivos_a_eliminar:
        if os.path.exists(archivo):
            size = os.path.getsize(archivo)
            archivos_encontrados.append(archivo)
            print(f"   ✓ {archivo} ({size:,} bytes)")

    # Buscar archivos de backup
    for archivo in os.listdir('.'):
        if archivo.startswith(backup_pattern) and archivo.endswith('.db'):
            if os.path.exists(archivo):
                size = os.path.getsize(archivo)
                archivos_encontrados.append(archivo)
                print(f"   ✓ {archivo} ({size:,} bytes)")

    if not archivos_encontrados:
        print("   ℹ️  No hay archivos obsoletos para eliminar")
        print("\n✅ El repositorio ya está limpio\n")
        return

    print(f"\n📊 Total: {len(archivos_encontrados)} archivo(s) obsoleto(s)")

    # Crear carpeta de respaldo
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'archivos_obsoletos_{timestamp}'

    print(f"\n💡 Los archivos se moverán a: {backup_dir}/")
    print("   (por si necesitas recuperar alguno)")

    respuesta = input("\n¿Continuar con la limpieza? (SI/no): ")

    if respuesta.upper() != 'SI':
        print("\n❌ Limpieza cancelada")
        return

    # Crear directorio de backup
    os.makedirs(backup_dir, exist_ok=True)

    print(f"\n🗂️  Moviendo archivos a {backup_dir}/...\n")

    archivos_movidos = 0
    errores = 0

    for archivo in archivos_encontrados:
        try:
            shutil.move(archivo, os.path.join(backup_dir, archivo))
            print(f"   ✓ {archivo}")
            archivos_movidos += 1
        except Exception as e:
            print(f"   ✗ {archivo}: {str(e)}")
            errores += 1

    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETADA")
    print("="*70 + "\n")

    print(f"📊 Resultados:")
    print(f"   - Archivos movidos: {archivos_movidos}")
    print(f"   - Errores: {errores}")
    print(f"   - Carpeta backup: {backup_dir}/")

    print("\n📂 Archivos que PERMANECEN en el repositorio:\n")
    print("   ✅ app_v2.py - Aplicación principal")
    print("   ✅ limpiar_datos_prueba.py - Limpieza de datos")
    print("   ✅ datos_iniciales.py - Datos iniciales")
    print("   ✅ calzado.db - Base de datos limpia")
    print("   ✅ templates/ - Plantillas HTML")
    print("   ✅ static/ - Archivos estáticos")
    print("   ✅ *.md - Documentación")

    print("\n💡 PRÓXIMOS PASOS:\n")
    print("1. Revisar que el sistema funciona:")
    print("   python app_v2.py")
    print()
    print("2. Commitear los cambios:")
    print("   git add .")
    print("   git commit -m 'chore: Limpiar archivos obsoletos del repositorio'")
    print("   git push")
    print()
    print("3. (Opcional) Eliminar carpeta de backup:")
    print(f"   rm -rf {backup_dir}/")
    print()
    print("🎯 El repositorio estará limpio y listo para entregar\n")


if __name__ == "__main__":
    limpiar_repositorio()
