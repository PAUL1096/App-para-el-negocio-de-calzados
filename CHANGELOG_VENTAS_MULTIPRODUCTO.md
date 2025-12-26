# 🛒 Changelog: Sistema de Ventas Multi-Producto

**Fecha:** 2025-12-26
**Branch:** `claude/check-latest-branch-RaeFz`
**Commit:** 96bbed1

---

## 🎯 Problemas Resueltos

### 1. ❌ Error SQL en Cuentas por Cobrar
**Error reportado:**
```
sqlite3.OperationalError: no such column: v.id_cliente
```

**Causa:** JOIN incorrecto en línea 992 de `app_v2.py`
```sql
-- INCORRECTO:
JOIN clientes cl ON c.id_cliente = c.id_cliente

-- CORRECTO:
JOIN clientes cl ON c.id_cliente = cl.id_cliente
```

**Estado:** ✅ RESUELTO

---

### 2. ❌ Arquitectura de Ventas Incorrecta

**Problema crítico reportado por el usuario:**
> "un cliente puede comprar no solamente un producto o una cantidad de un solo producto, sino varios"

**Modelo anterior (INCORRECTO):**
```
ventas_v2
├── id_venta
├── id_producto  ❌ Solo 1 producto por venta
├── cantidad_pares
├── precio_unitario
└── total_final
```

**Modelo nuevo (CORRECTO):**
```
ventas_v2 (MAESTRO)              ventas_detalle (DETALLE)
├── id_venta                     ├── id_detalle
├── codigo_venta                 ├── id_venta (FK)
├── id_cliente                   ├── id_producto (FK)
├── descuento_global     <-----> ├── cantidad_pares
├── total_final                  ├── precio_unitario
├── estado_pago                  └── subtotal
└── metodo_pago
```

**Estado:** ✅ RESUELTO - Migración ejecutada

---

## 📦 Migración de Base de Datos

### Script: `migracion_ventas_multiproducto.py`

**Cambios aplicados:**

1. ✅ Tabla `ventas_detalle` creada
   - Soporta múltiples productos por venta
   - Campos: id_detalle, id_venta, id_producto, cantidad_pares, precio_unitario, subtotal

2. ✅ Tabla `ventas_v2` rediseñada
   - Removidas columnas: id_producto, cantidad_pares, precio_unitario, subtotal
   - Agregada: descuento_global
   - Ahora es tabla MAESTRO (sin datos de productos individuales)

3. ✅ Datos migrados
   - Ventas existentes convertidas a nuevo formato
   - Cada venta antigua → 1 registro en ventas_detalle

4. ✅ Índices recreados
   - idx_ventas_detalle_venta
   - idx_ventas_detalle_producto

---

## 🔧 Cambios en API

### `/api/ventas/registrar` (Actualizado)

**Formato anterior:**
```json
{
  "id_producto": 123,
  "cantidad_pares": 24,
  "precio_unitario": 85.00,
  "descuento": 5.00
}
```

**Formato NUEVO:**
```json
{
  "id_cliente": 5,
  "cliente": "Juan Pérez",
  "productos": [
    {
      "id_producto": 123,
      "cantidad_pares": 24,
      "pares_por_docena": 12,
      "precio_unitario": 85.00,
      "descuento_linea": 0
    },
    {
      "id_producto": 456,
      "cantidad_pares": 12,
      "pares_por_docena": 12,
      "precio_unitario": 95.00,
      "descuento_linea": 5.00
    }
  ],
  "descuento_global": 10.00,
  "estado_pago": "credito",
  "metodo_pago": "efectivo",
  "observaciones": "Venta múltiple"
}
```

**Validaciones nuevas:**
- ✅ Debe incluir al menos 1 producto
- ✅ Validación de stock por cada producto
- ✅ Descuentos por línea + descuento global
- ✅ Cálculo automático de total_final

---

### `/api/ventas/registrar-directa` (Actualizado)

**Cambios:**
- Acepta array de productos
- Verifica stock para cada producto
- Descuenta inventario por cada producto
- Crea múltiples registros en ventas_detalle

---

## 🎨 Nueva Interfaz de Usuario

### `templates/venta_directa_carrito.html` (NUEVO)

**Características:**

1. **Shopping Cart UI:**
   - ✅ Agregar múltiples productos al carrito
   - ✅ Editar cantidad por producto
   - ✅ Editar precio por producto
   - ✅ Eliminar productos del carrito
   - ✅ Vista en tiempo real del carrito

2. **Cálculos automáticos:**
   - Subtotal por producto
   - Subtotal general
   - Descuento global
   - Total final

3. **Validaciones:**
   - Stock disponible por producto
   - Cantidad mínima/máxima
   - Cliente obligatorio

**Screenshot conceptual:**
```
┌─────────────────────────────────────┐
│ Carrito de Venta                    │
├─────────────────────────────────────┤
│ [Producto 1]           [Eliminar]   │
│ Cantidad: [24] Max: 48              │
│ Precio: [85.00]                     │
│ Subtotal: S/ 2,040.00               │
├─────────────────────────────────────┤
│ [Producto 2]           [Eliminar]   │
│ Cantidad: [12] Max: 36              │
│ Precio: [95.00]                     │
│ Subtotal: S/ 1,140.00               │
├─────────────────────────────────────┤
│ Subtotal:         S/ 3,180.00       │
│ Descuento:        S/    10.00       │
│ ─────────────────────────────────   │
│ TOTAL:            S/ 3,170.00       │
└─────────────────────────────────────┘
```

---

## 📋 Cambios en UI de Ventas

### `templates/ventas_v2.html` (Actualizado)

**Cambios:**

1. ✅ Removido botón "Venta desde Preparación" (confuso)
2. ✅ Simplificado a un solo botón: "Nueva Venta"
3. ✅ Actualizada tabla de ventas:
   - Columna "Productos" muestra cantidad de productos
   - Muestra códigos de todos los productos
   - Total de pares combinado
4. ✅ Banner informativo actualizado

**Antes:**
```
[Venta desde Preparación] [Venta Directa]
```

**Ahora:**
```
[Nueva Venta]  (con carrito multi-producto)
```

---

## 🔄 Flujo de Trabajo Actualizado

### Antes (INCORRECTO):
```
1. Seleccionar UNA preparación
2. Seleccionar UN producto de esa preparación
3. Vender TODO el conjunto preparado
   ❌ No permite vender productos individuales
   ❌ No permite múltiples productos
```

### Ahora (CORRECTO):
```
1. Click en "Nueva Venta"
2. Seleccionar ubicación (Casa/Tienda/etc)
3. Agregar productos al carrito (uno por uno)
   ✅ Editar cantidades independientemente
   ✅ Editar precios independientemente
   ✅ Agregar/quitar productos libremente
4. Seleccionar cliente
5. Aplicar descuento global (opcional)
6. Registrar venta
   ✅ Crea 1 registro maestro
   ✅ Crea N registros detalle
```

---

## 💡 Conceptos Clarificados

### Preparación ≠ Venta

**Preparación:**
- ✅ Alistar mercadería para transportar
- ✅ Organizar productos por día de venta
- ❌ NO es una unidad de venta
- ❌ NO se vende "todo el conjunto"

**Venta:**
- ✅ Puede incluir múltiples productos
- ✅ Productos de diferentes preparaciones
- ✅ Productos del inventario directo
- ✅ Cada cliente compra lo que necesita

---

## 📊 Estructura de Datos

### Ejemplo de venta multi-producto:

**Venta Maestro:**
```sql
INSERT INTO ventas_v2 (
  codigo_venta, id_cliente, cliente,
  descuento_global, total_final, estado_pago
) VALUES (
  'VD20251226-001', 5, 'Juan Pérez',
  10.00, 3170.00, 'credito'
);
```

**Venta Detalle (Producto 1):**
```sql
INSERT INTO ventas_detalle (
  id_venta, id_producto, codigo_interno,
  cantidad_pares, precio_unitario, subtotal
) VALUES (
  1, 123, 'BOOT-001',
  24, 85.00, 2040.00
);
```

**Venta Detalle (Producto 2):**
```sql
INSERT INTO ventas_detalle (
  id_venta, id_producto, codigo_interno,
  cantidad_pares, precio_unitario, subtotal
) VALUES (
  1, 456, 'BOOT-002',
  12, 95.00, 1140.00
);
```

---

## 🚀 Cómo Usar el Nuevo Sistema

### Paso 1: Abrir módulo de Ventas
```
/ventas  (muestra lista de ventas)
```

### Paso 2: Click en "Nueva Venta"
```
Redirige a: /ventas/nueva-directa
Template: venta_directa_carrito.html
```

### Paso 3: Seleccionar ubicación
```
- Casa
- Tienda Calzaplaza
- Tienda CalzaPe
```

### Paso 4: Agregar productos al carrito
```
1. Ver lista de inventario disponible
2. Click "Agregar" en cada producto deseado
3. Editar cantidad/precio en el carrito
4. Repetir para más productos
```

### Paso 5: Completar venta
```
1. Seleccionar cliente
2. Aplicar descuento global (opcional)
3. Seleccionar estado de pago
4. Registrar venta
```

### Paso 6: Sistema automático
```
✅ Crea venta maestro
✅ Crea N registros de detalle
✅ Descuenta inventario de cada producto
✅ Si es crédito → crea cuenta por cobrar
```

---

## ⚠️ Notas Importantes

1. **Backward Compatibility:**
   - Ventas antiguas migradas automáticamente
   - Consultas actualizadas con LEFT JOIN a ventas_detalle

2. **Integración con Cuentas por Cobrar:**
   - ✅ Ventas a crédito crean cuenta automáticamente
   - ✅ Vinculación via id_venta
   - ✅ Query actualizado para evitar duplicados

3. **Preparaciones:**
   - Sigue existiendo para organizar mercadería
   - Ya NO se usa para vender
   - Venta toma productos del inventario directo

---

## 📝 Archivos Modificados

```
✅ app_v2.py
   - Línea 992: Fix JOIN en cuentas_por_cobrar
   - Línea 612-751: /api/ventas/registrar (multi-producto)
   - Línea 839-979: /api/ventas/registrar-directa (multi-producto)
   - Línea 517-539: /ventas query con ventas_detalle

✅ migracion_ventas_multiproducto.py (NUEVO)
   - Script de migración ejecutado
   - Backup automático creado

✅ templates/venta_directa_carrito.html (NUEVO)
   - UI de shopping cart
   - JavaScript para carrito dinámico

✅ templates/ventas_v2.html
   - Banner actualizado
   - Tabla de ventas actualizada
   - Removido modal de preparaciones
```

---

## ✅ Checklist de Validación

- [x] Migración de BD ejecutada exitosamente
- [x] Error SQL en cuentas_por_cobrar corregido
- [x] API acepta múltiples productos
- [x] UI de carrito funcional
- [x] Validación de stock por producto
- [x] Cálculos automáticos correctos
- [x] Integración con cuentas por cobrar
- [x] Descuento por línea + global
- [x] Banner informativo claro
- [x] Flujo simplificado

---

## 🎉 Resultado Final

El sistema ahora soporta correctamente:

✅ **Ventas con múltiples productos** (shopping cart)
✅ **Cantidades y precios independientes** por producto
✅ **Descuentos por línea** + descuento global
✅ **Validación de stock** por cada producto
✅ **Vista de carrito** en tiempo real
✅ **Integración con cuentas por cobrar** mantenida
✅ **Conceptos clarificados:** Preparación vs Venta

---

**Autor:** Claude Code
**Fecha:** 2025-12-26
**Commit:** 96bbed1
