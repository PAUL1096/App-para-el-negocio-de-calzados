# 🚀 Preparar Sistema para Producción

Guía para limpiar datos de prueba y dejar el sistema listo para el negocio.

## 📋 Pasos a Seguir

### 1️⃣ Limpiar Datos de Prueba

Ejecuta el script de limpieza:

```bash
python limpiar_datos_prueba.py
```

**Te preguntará:**
- ¿Limpiar catálogo? (si/NO)
  - **NO**: Mantiene variantes base (modelos) y ubicaciones
  - **SI**: Limpia TODO, incluyendo modelos y tiendas

**Luego confirmará:**
- ¿Estás seguro? (SI/no)
  - Debes escribir **SI** en mayúsculas para confirmar

**Qué hace:**
1. Crea backup automático: `calzado_backup_antes_limpieza_YYYYMMDD_HHMMSS.db`
2. Elimina todos los datos transaccionales:
   - ✓ Ventas
   - ✓ Cuentas por cobrar
   - ✓ Pagos
   - ✓ Clientes
   - ✓ Productos producidos
   - ✓ Inventario
   - ✓ Preparaciones
3. Resetea contadores de ID (empiezan en 1)
4. Opcionalmente limpia catálogo

### 2️⃣ Insertar Datos Iniciales (Opcional)

Si limpiaste el catálogo, necesitas crear al menos una ubicación:

```bash
python datos_iniciales.py
```

**Qué crea:**
- Ubicación: "Almacén Central"

### 3️⃣ Verificar el Sistema

1. Inicia la aplicación:
   ```bash
   python app_v2.py
   ```

2. Abre el navegador: `http://localhost:5000`

3. Verifica el dashboard:
   - Variantes: 0 (o las que mantuviste)
   - Productos: 0
   - Stock: 0
   - Ventas hoy: 0

### 4️⃣ Configurar para el Negocio

**Antes de entregar:**

1. **Crear Ubicaciones** (`/ubicaciones`):
   - Almacén Central
   - Tienda 1
   - Tienda 2
   - etc.

2. **Crear Variantes Base** (`/catalogo-variantes`):
   - Modelos de calzado que producen
   - Códigos internos
   - Tipos, hormas, segmentos

3. **(Opcional) Pre-cargar Clientes** (`/clientes`):
   - Solo si ya tienen clientes registrados

## 🆘 En Caso de Error

Si algo sale mal, puedes restaurar el backup:

```bash
# Ver backups disponibles
ls -la calzado_backup_*

# Restaurar (reemplaza YYYYMMDD_HHMMSS con la fecha del backup)
cp calzado_backup_antes_limpieza_YYYYMMDD_HHMMSS.db calzado.db
```

## ✅ Checklist Final

Antes de entregar el sistema al negocio:

- [ ] Datos de prueba limpiados
- [ ] Ubicaciones reales creadas
- [ ] Variantes base (modelos) creadas
- [ ] Sistema probado (crear producto, ingresar inventario, hacer venta)
- [ ] Dashboard muestra 0 en todo
- [ ] No hay cuentas por cobrar de prueba
- [ ] Backups guardados en lugar seguro

## 📊 Códigos Después de Limpiar

Los primeros registros tendrán estos códigos:

- **Primer cliente**: `CLI-000001`
- **Primera venta directa**: `VD20260116-001` (VD = Venta Directa)
- **Primera venta desde preparación**: `VP20260116-001` (VP = Venta Preparación)
- **Primera cuenta por cobrar**: `CC-000001`
- **Primera preparación**: `PREP-0001`

## 💡 Notas Importantes

1. **Siempre se crea un backup** antes de limpiar
2. **Los backups se guardan** con timestamp en el nombre
3. **La estructura de la base de datos NO se modifica**, solo los datos
4. **El sistema funcionará normalmente** después de la limpieza
5. **Puedes limpiar múltiples veces** si es necesario

## 🎯 ¿Qué Mantener?

### Mantener (responder NO a limpiar catálogo):
- Si ya creaste los modelos de calzado reales
- Si ya tienes las tiendas/almacenes configurados

### Limpiar TODO (responder SI a limpiar catálogo):
- Si TODO es de prueba
- Si vas a empezar completamente desde cero
- Si los modelos y ubicaciones actuales no son reales

---

**¿Dudas?** Revisa los scripts:
- `limpiar_datos_prueba.py` - Script de limpieza
- `datos_iniciales.py` - Script de datos iniciales
