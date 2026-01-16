"""
Script para limpiar archivos innecesarios del REPOSITORIO GIT
IMPORTANTE: Esto elimina archivos del historial de Git, no solo localmente
"""

import subprocess
import os

def ejecutar_comando(comando, descripcion=""):
    """Ejecuta un comando y muestra el resultado"""
    if descripcion:
        print(f"   {descripcion}...")

    try:
        resultado = subprocess.run(
            comando,
            shell=True,
            capture_output=True,
            text=True,
            check=True
        )
        return True, resultado.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def limpiar_git_repositorio():
    """Elimina archivos innecesarios del repositorio Git"""

    print("\n" + "="*70)
    print("🧹 LIMPIEZA DE REPOSITORIO GIT")
    print("="*70 + "\n")

    print("⚠️  ADVERTENCIA:")
    print("   Este script eliminará archivos del repositorio Git")
    print("   Los archivos se eliminarán del tracking de Git")
    print("   (pero permanecerán en tu disco local)")
    print()

    # Archivos a eliminar del repositorio Git
    archivos_git_rm = [
        # Bases de datos antiguas
        'ventas_calzado.db',

        # Apps antiguas
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

        # Scripts temporales
        'actualizar_nombres_ubicaciones.py',
        'actualizar_nombres_ubicaciones.sql',
        'diagnosticar_codigos_venta.py',
        'test_codigo_venta.py',
        'verificar_bd.py',
        'import_data.py',

        # Datos de ejemplo
        'datos_simulados_calzado.xlsx',

        # Templates obsoletos
        'templates/analisis.html',
        'templates/index.html',
        'templates/index_v13.html',
        'templates/pedidos_cliente.html',
        'templates/preparacion_nueva.html',
        'templates/preparaciones.html',
        'templates/productos_base.html',
        'templates/variantes.html',
        'templates/venta_nueva.html',
        'templates/ventas.html',
        'templates/ventas_historicas.html',

        # Documentación obsoleta (opcional)
        'README_V1_2.md',
        'README_FASE_3_4.md',
        'README_V2_MODELO_CORRECTO.md',
        'GUIA_MIGRACION_V1_2.md',
        'PLAN_DESARROLLO.md',
        'ENTREGA_COMPLETA.md',
        'ESTADO_DESARROLLO.md',
        'CHANGELOG_VENTAS_MULTIPRODUCTO.md',
    ]

    print("📋 Archivos que se eliminarán del repositorio Git:\n")

    archivos_existentes = []
    for archivo in archivos_git_rm:
        # Verificar si el archivo está trackeado en Git
        exito, _ = ejecutar_comando(f'git ls-files --error-unmatch {archivo} 2>/dev/null')
        if exito:
            archivos_existentes.append(archivo)
            print(f"   ✓ {archivo}")

    if not archivos_existentes:
        print("   ℹ️  No hay archivos innecesarios trackeados en Git")
        print("\n✅ El repositorio ya está limpio\n")
        return

    print(f"\n📊 Total: {len(archivos_existentes)} archivo(s) innecesario(s)")
    print("\n💡 IMPORTANTE:")
    print("   - Los archivos se eliminarán del TRACKING de Git")
    print("   - Los archivos PERMANECERÁN en tu disco local")
    print("   - Esto NO afecta el historial de Git (no hay reescritura)")
    print("   - Solo deja de trackear estos archivos a futuro")

    respuesta = input("\n¿Continuar con la limpieza? (SI/no): ")

    if respuesta.upper() != 'SI':
        print("\n❌ Limpieza cancelada")
        return

    print("\n🗑️  Eliminando archivos del repositorio Git...\n")

    archivos_eliminados = 0
    errores = 0

    for archivo in archivos_existentes:
        exito, salida = ejecutar_comando(
            f'git rm --cached "{archivo}"',
            f"Eliminando {archivo}"
        )

        if exito:
            print(f"   ✓ {archivo}")
            archivos_eliminados += 1
        else:
            print(f"   ✗ {archivo}: {salida}")
            errores += 1

    print("\n" + "="*70)
    print("✅ LIMPIEZA COMPLETADA")
    print("="*70 + "\n")

    print(f"📊 Resultados:")
    print(f"   - Archivos eliminados del tracking: {archivos_eliminados}")
    print(f"   - Errores: {errores}")

    print("\n📝 PRÓXIMOS PASOS:\n")
    print("1. Verificar cambios:")
    print("   git status")
    print()
    print("2. Commitear los cambios:")
    print("   git commit -m 'chore: Eliminar archivos obsoletos del repositorio'")
    print()
    print("3. Push al repositorio:")
    print("   git push origin claude/check-latest-branch-RaeFz")
    print()
    print("💡 Los archivos físicos permanecen en tu disco, pero Git ya no los trackea")
    print("   Puedes eliminarlos manualmente si quieres con:")
    print("   python limpiar_repositorio.py  # (el script que ya tienes)")
    print()


if __name__ == "__main__":
    # Verificar que estamos en un repositorio Git
    if not os.path.exists('.git'):
        print("\n❌ ERROR: Este no es un repositorio Git")
        print("   Ejecuta este script desde la raíz del proyecto\n")
        exit(1)

    limpiar_git_repositorio()
