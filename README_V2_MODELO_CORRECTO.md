# 📦 Sistema de Gestión de Calzado v2.0 - Modelo Correcto

## 🎯 Qué cambió

### **ANTES (v1.x) - Modelo Incorrecto:**
```
Variante = Código + Cuero + Color + Serie + Stock
```
❌ **Problema:** Mezclaba el diseño base con características de producción

### **AHORA (v2.0) - Modelo Correcto:**
```
Variante Base → Producto Producido → Inventario → Ventas
```
✅ **Solución:** Separación clara de conceptos

---

## 📊 Nuevo Modelo de Datos

### 1. **VARIANTES_BASE** (Catálogo de Modelos)
**Qué es:** Plantillas/moldes de los calzados que produces

**Campos:**
- `codigo_interno`: Tu código (ej: M-CASUAL-01)
- `tipo_calzado`: Casual, Formal, Deportivo, Escolar, etc.
- `tipo_horma`: Americano, Punta Pala, Punta Cuadrada, etc.
- `segmento`: Adulto Caballero, Niño, Dama, etc.
- `descripcion`: Notas sobre el modelo

**Ejemplo:**
```
Código: M-CASUAL-01
Tipo: Casual
Horma: Americana
Segmento: Adulto Caballero
```

### 2. **PRODUCTOS_PRODUCIDOS** (Materializaciones)
**Qué es:** Productos concretos que produces a partir de las variantes base

**Campos:**
- `id_variante_base`: Enlace a la variante base
- `cuero`: Huante, Cuero Natural, Sintético, etc.
- `color_cuero`: Negro, Marrón, Café, etc.
- `suela`: Goma, Cuero, TR, PU, etc.
- `forro`: Con forro alta gama, Sin forro, etc.
- `serie_tallas`: 38(2) 39(3) 40(3) 41(2) 42(2)
- `cantidad_total_pares`: Cantidad producida
- `costo_unitario` y `precio_sugerido`

**Ejemplo:**
```
Variante Base: M-CASUAL-01
Cuero: Huante
Color: Negro
Suela: Goma
Forro: Con forro alta gama
Serie: 38(2) 39(3) 40(3) 41(2) 42(2)
Pares: 60
```

### 3. **INVENTARIO** (Stock Físico)
**Qué es:** Registro de productos en ubicaciones

**Campos:**
- `id_producto`: Enlace al producto
- `id_ubicacion`: Casa, Tienda Principal, etc.
- `tipo_stock`: General o Pedido
- `cantidad_pares`: Stock disponible

---

## 🚀 Instalación y Migración

### **Paso 1: Actualizar código**
```bash
git pull origin claude/check-shoe-app-updates-011X6WgoqVHhh1zUjvBgx3To
```

### **Paso 2: Ejecutar migración**
```bash
python migracion_v2_modelo_correcto.py
```

**⚠️ IMPORTANTE:**
- El script te pedirá confirmación (escribe `SI`)
- Crea backup automático de tu base de datos
- Tablas antiguas se renombran a `_old`
- Sistema inicia LIMPIO (sin datos históricos)

**Salida esperada:**
```
🔧 MIGRACIÓN V2.0: Rediseño completo del modelo de datos
📦 Creando backup: calzado_backup_v2_[timestamp].db
✅ Backup creado exitosamente

FASE 1: Renombrar tablas antiguas como backup
✅ Tabla 'variantes' respaldada como 'variantes_old'
✅ Tabla 'inventario' respaldada como 'inventario_old'
...

FASE 2: Crear nuevas tablas con diseño correcto
✅ Tabla 'variantes_base' creada
✅ Tabla 'productos_producidos' creada
...

✅ MIGRACIÓN COMPLETADA EXITOSAMENTE
```

### **Paso 3: Iniciar aplicación v2**
```bash
python app_v2.py
```

**Verás:**
```
🚀 Sistema de Gestión de Calzado v2.0
📦 Modelo: Variantes Base → Productos → Inventario
🌐 Servidor: http://localhost:5000
```

---

## 📖 Flujo de Trabajo

### **1. Crear Variante Base (Catálogo)**
1. Ve a: http://localhost:5000/catalogo-variantes
2. Click en "Nueva Variante Base"
3. Completa:
   - Código Interno: `M-CASUAL-01`
   - Tipo Calzado: `Casual`
   - Tipo Horma: `Americano`
   - Segmento: `Adulto Caballero`
   - Descripción: `Zapato casual básico`
4. Guardar

### **2. Producir Producto (Materializar)**
1. Desde catálogo, click en 🔨 (Producir) en la variante
2. Completa detalles de producción:
   - Cuero: `Huante`
   - Color: `Negro`
   - Suela: `Goma`
   - Forro: `Con forro alta gama`
   - Serie Tallas: `38(2) 39(3) 40(3) 41(2) 42(2)`
   - Cantidad: `60 pares`
   - Costos y precios
3. Registrar Producción

### **3. Ingresar a Inventario**
1. Desde producción, click en ⬇️ (Ingresar)
2. Selecciona ubicación (Casa, Tienda, etc.)
3. Define tipo de stock (General/Pedido)
4. Confirmar ingreso

### **4. Preparaciones y Ventas**
_(Mismo flujo que v1.3, pero ahora con productos)_
1. Crear Preparación desde inventario
2. Registrar Ventas desde preparación
3. Procesar devoluciones

---

## 🎨 Interfaz del Sistema

### **Dashboard v2.0**
- Variantes Base: Modelos en catálogo
- Productos: Materializaciones producidas
- Stock Total: Pares en inventario
- Ventas Hoy: Ventas registradas

### **Módulos Disponibles:**
- 📦 **Catálogo de Variantes** - CRUD de modelos base
- 🔨 **Producción** - Crear productos desde variantes
- 📍 **Ubicaciones** - Gestión de ubicaciones
- 📦 **Inventario** - (Pendiente adaptación v2)
- 📋 **Preparaciones** - (Pendiente adaptación v2)
- 🛒 **Ventas** - (Pendiente adaptación v2)

---

## 📝 Ejemplos Prácticos

### **Ejemplo 1: Zapato Casual**
```
1. VARIANTE BASE:
   Código: M-CAS-AMERICANA-01
   Tipo: Casual
   Horma: Americana
   Segmento: Adulto Caballero

2. PRODUCTOS (del mismo modelo):
   a) M-CAS-AMERICANA-01 + Huante Negro + Goma
   b) M-CAS-AMERICANA-01 + Cuero Marrón + Cuero
   c) M-CAS-AMERICANA-01 + Sintético Negro + TR

3. INVENTARIO:
   - Producto (a): 60 pares en Casa
   - Producto (b): 48 pares en Tienda Principal
   - Producto (c): 36 pares en Tienda Secundaria
```

### **Ejemplo 2: Zapato Formal**
```
1. VARIANTE BASE:
   Código: M-FOR-PUNTAPALA-01
   Tipo: Formal
   Horma: Punta Pala
   Segmento: Adulto Caballero

2. PRODUCTOS:
   a) M-FOR-PUNTAPALA-01 + Cuero Negro + Cuero + Forro Alta Gama
   b) M-FOR-PUNTAPALA-01 + Cuero Café + Cuero + Forro Alta Gama
```

---

## ⚠️ Consideraciones Importantes

### **Datos Antiguos:**
- Tablas originales → Respaldadas como `_old`
- Puedes consultarlas si necesitas datos históricos
- Elimínalas después de verificar que todo funciona

### **Estado Actual:**
- ✅ Catálogo de Variantes Base (funcional)
- ✅ Producción de Productos (funcional)
- ⏳ Inventario (pendiente adaptar a productos)
- ⏳ Preparaciones (pendiente adaptar a productos)
- ⏳ Ventas (pendiente adaptar a productos)

### **Próximos Pasos:**
1. Crear variantes base de tus modelos existentes
2. Producir productos para cada combinación
3. Esperar adaptación de Inventario/Preparaciones/Ventas

---

## 🐛 Solución de Problemas

### **Error: Tabla no existe**
```bash
# Ejecutar migración nuevamente
python migracion_v2_modelo_correcto.py
```

### **Puerto 5000 ocupado**
```bash
# Editar app_v2.py y cambiar puerto:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### **Restaurar desde backup**
```bash
# Reemplazar calzado.db con el backup
cp calzado_backup_v2_[timestamp].db calzado.db
```

---

## 📞 Soporte

Si tienes dudas o encuentras problemas, comparte:
1. Mensaje de error completo
2. Captura de pantalla
3. Paso que estabas realizando

---

## ✅ Checklist de Migración

- [ ] Backup creado automáticamente
- [ ] Migración ejecutada exitosamente
- [ ] app_v2.py iniciado
- [ ] Dashboard carga correctamente
- [ ] Variante base de ejemplo creada
- [ ] Producto producido de ejemplo
- [ ] Todo funciona correctamente

---

**¡Listo para usar el sistema correcto!** 🎉
