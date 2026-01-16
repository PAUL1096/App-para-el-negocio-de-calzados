# 🧹 Limpieza Completa del Repositorio

Guía para dejar el repositorio limpio y listo para distribución.

---

## 🎯 Objetivo

Eliminar todos los archivos innecesarios del repositorio Git para que:
- ✅ Solo contenga código actual (v2.0)
- ✅ No tenga archivos obsoletos
- ✅ Esté listo para clonar/distribuir
- ✅ Sea fácil de mantener

---

## 📋 Dos Tipos de Limpieza

### 1️⃣ Limpieza LOCAL (archivos en tu disco)
**Script:** `limpiar_repositorio.py`
- Mueve archivos obsoletos a carpeta de respaldo
- NO elimina de Git (siguen trackeados)

### 2️⃣ Limpieza de GIT (archivos trackeados)
**Script:** `limpiar_git_repositorio.py` ✨ NUEVO
- Elimina archivos del tracking de Git
- Los archivos permanecen en tu disco
- Se eliminan del repositorio cuando hagas push

---

## 🚀 Proceso Completo de Limpieza

### PASO 1: Actualizar Repositorio Local

```bash
git pull origin claude/check-latest-branch-RaeFz
```

Esto descarga los scripts nuevos:
- `limpiar_git_repositorio.py`
- `GUIA_INSTALACION.md`
- `LIMPIEZA_COMPLETA.md`

### PASO 2: Limpiar Archivos del Tracking de Git

```bash
python limpiar_git_repositorio.py
```

**¿Qué hace?**
- Elimina del tracking de Git (git rm --cached):
  - ❌ Base de datos vieja: `ventas_calzado.db`
  - ❌ Apps antiguas: `app.py`, `app_v1_2.py`, `app_v1_3.py`
  - ❌ Scripts de migración (11 archivos)
  - ❌ Scripts temporales (6 archivos)
  - ❌ Templates obsoletos (11 archivos)
  - ❌ Documentación obsoleta (7 archivos)

**Resultado:**
- ~45 archivos eliminados del tracking
- Los archivos físicos permanecen en tu disco
- Git ya no los trackea en commits futuros

### PASO 3: Verificar Cambios

```bash
git status
```

Deberías ver algo como:
```
deleted:    app.py
deleted:    app_v1_2.py
deleted:    ventas_calzado.db
...
```

### PASO 4: Commitear Limpieza

```bash
git add .
git commit -m "chore: Eliminar archivos obsoletos del repositorio

Archivos eliminados:
- Apps antiguas (v1.0, v1.2, v1.3)
- Scripts de migración ejecutados (11 archivos)
- Scripts temporales de diagnóstico (6 archivos)
- Bases de datos antiguas
- Templates obsoletos (11 archivos)
- Documentación de versiones antiguas (7 archivos)

Total: ~45 archivos innecesarios eliminados del tracking

El repositorio ahora solo contiene:
- app_v2.py (aplicación actual)
- Templates activos
- Scripts útiles (limpieza, datos iniciales)
- Documentación relevante (instalación, uso)
"
```

### PASO 5: Push al Repositorio

```bash
git push origin claude/check-latest-branch-RaeFz
```

### PASO 6 (Opcional): Limpiar Archivos Locales

Si quieres también eliminar los archivos físicos de tu disco:

```bash
python limpiar_repositorio.py
```

Esto mueve los archivos físicos a `archivos_obsoletos_*/`

---

## 📊 Antes y Después

### ANTES (73 archivos trackeados):
```
.gitignore
app.py ❌
app_v1_2.py ❌
app_v1_3.py ❌
app_v2.py ✅
ventas_calzado.db ❌
migracion_*.py (11 archivos) ❌
templates/analisis.html ❌
templates/index.html ❌
... (muchos archivos obsoletos)
```

### DESPUÉS (~28 archivos trackeados):
```
.gitignore
app_v2.py ✅
calzado.db ✅ (ignorado por .gitignore, no trackeado)
datos_iniciales.py ✅
limpiar_datos_prueba.py ✅
requirements.txt ✅
templates/base.html ✅
templates/index_v2.html ✅
templates/ventas_v2.html ✅
... (solo archivos necesarios)
GUIA_INSTALACION.md ✅
INICIO_RAPIDO.md ✅
README.md ✅
```

---

## ✅ Archivos que PERMANECEN

### Código Principal:
- `app_v2.py` - Aplicación
- `requirements.txt` - Dependencias

### Scripts Útiles:
- `datos_iniciales.py` - Crear BD inicial
- `limpiar_datos_prueba.py` - Limpiar datos de prueba
- `limpiar_repositorio.py` - Limpiar archivos locales
- `limpiar_git_repositorio.py` - Limpiar tracking de Git

### Templates Activos:
- `templates/base.html`
- `templates/index_v2.html`
- `templates/catalogo_variantes.html`
- `templates/produccion.html`
- `templates/produccion_nueva.html`
- `templates/inventario.html`
- `templates/inventario_ingresar.html`
- `templates/ubicaciones.html`
- `templates/preparacion_nueva_v2.html`
- `templates/preparaciones_v2.html`
- `templates/venta_directa_nueva.html`
- `templates/venta_directa_carrito.html`
- `templates/venta_nueva_v2.html`
- `templates/ventas_v2.html`
- `templates/venta_detalle.html`
- `templates/clientes.html`
- `templates/cliente_detalle.html`
- `templates/cuentas_por_cobrar.html`

### Documentación Relevante:
- `README.md` - Descripción general
- `GUIA_INSTALACION.md` - Cómo instalar ✨ NUEVO
- `INICIO_RAPIDO.md` - Guía rápida de uso
- `PREPARAR_PARA_PRODUCCION.md` - Cómo limpiar datos
- `REVISION_FINAL.md` - Funcionalidades completas
- `FLUJO_POST_DESARROLLO.md` - Proceso de entrega
- `ARQUITECTURA_TECNICA.md` - Detalles técnicos

---

## 🗑️ Archivos ELIMINADOS del Tracking

### Apps Antiguas (3):
- `app.py`
- `app_v1_2.py`
- `app_v1_3.py`

### Scripts de Migración (11):
- `migracion_v1_2.py`
- `migracion_v2_modelo_correcto.py`
- `migracion_codigo_interno.py`
- `migracion_cuentas_por_cobrar.py`
- `migracion_fase_3_4.py`
- `migracion_integracion_ventas_clientes.py`
- `migracion_permitir_cliente_null.py`
- `migracion_plantilla_ingresos_parciales.py`
- `migracion_preparaciones_destino.py`
- `migracion_ventas_directas.py`
- `migracion_ventas_multiproducto.py`
- `reparar_migracion.py`

### Scripts Temporales (6):
- `actualizar_nombres_ubicaciones.py`
- `actualizar_nombres_ubicaciones.sql`
- `diagnosticar_codigos_venta.py`
- `test_codigo_venta.py`
- `verificar_bd.py`
- `import_data.py`

### Datos de Ejemplo (1):
- `datos_simulados_calzado.xlsx`

### Bases de Datos Antiguas (1):
- `ventas_calzado.db`

### Templates Obsoletos (11):
- `templates/analisis.html`
- `templates/index.html`
- `templates/index_v13.html`
- `templates/pedidos_cliente.html`
- `templates/preparacion_nueva.html`
- `templates/preparaciones.html`
- `templates/productos_base.html`
- `templates/variantes.html`
- `templates/venta_nueva.html`
- `templates/ventas.html`
- `templates/ventas_historicas.html`

### Documentación Obsoleta (7):
- `README_V1_2.md`
- `README_FASE_3_4.md`
- `README_V2_MODELO_CORRECTO.md`
- `GUIA_MIGRACION_V1_2.md`
- `PLAN_DESARROLLO.md`
- `ENTREGA_COMPLETA.md`
- `ESTADO_DESARROLLO.md`
- `CHANGELOG_VENTAS_MULTIPRODUCTO.md`

**Total eliminados:** ~45 archivos

---

## 💡 Beneficios de la Limpieza

### Para Usuarios que Clonan el Repo:
- ✅ Descarga más rápida (menos archivos)
- ✅ Solo ven código relevante
- ✅ No se confunden con archivos viejos
- ✅ Instalación más simple

### Para Mantenimiento:
- ✅ Repositorio más limpio
- ✅ Fácil identificar qué archivos son importantes
- ✅ Menos desorden
- ✅ Mejor organización

### Para Distribución:
- ✅ Profesional y organizado
- ✅ Solo contiene lo necesario
- ✅ Fácil de documentar

---

## 🆘 Troubleshooting

### Problema: "git rm failed"

**Solución:**
Algunos archivos pueden no existir. Es normal, el script continúa.

### Problema: "Cannot commit empty"

**Solución:**
Significa que no había archivos innecesarios. El repo ya estaba limpio.

### Problema: Eliminé algo por error

**Solución:**
Los archivos físicos están en tu disco. Puedes volver a agregarlos:
```bash
git add archivo.py
git commit -m "Restaurar archivo"
```

---

## 📝 Checklist de Limpieza Completa

- [ ] Pull del repositorio actualizado
- [ ] Ejecutar `python limpiar_git_repositorio.py`
- [ ] Responder "SI" para confirmar
- [ ] Ejecutar `git status` para verificar
- [ ] Ejecutar `git add .`
- [ ] Ejecutar `git commit -m "chore: Eliminar archivos obsoletos"`
- [ ] Ejecutar `git push`
- [ ] (Opcional) Ejecutar `python limpiar_repositorio.py` para limpiar disco local
- [ ] Verificar que `python app_v2.py` funciona
- [ ] Verificar en GitHub que los archivos se eliminaron

---

**Última actualización:** 2026-01-16
**Script creado:** `limpiar_git_repositorio.py`
