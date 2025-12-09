# 🚀 GUÍA DE MIGRACIÓN A VERSIÓN 1.2

**Sistema de Gestión de Ventas de Calzado**

---

## 📋 RESUMEN DE CAMBIOS

La versión 1.2 implementa las siguientes mejoras según tu modelo de negocio:

### ✅ NUEVAS FUNCIONALIDADES

1. **Sistema de VARIANTES**
   - Separación clara entre Producto Base y Variantes
   - Una variante = Código + Cuero + Color + Serie
   - Cada variante tiene su propio costo y precio

2. **INVENTARIO AVANZADO**
   - Stock General (disponible para venta libre)
   - Stock de Pedidos (reservado para clientes con fecha de entrega)
   - Control por ubicación (almacén)
   - Movimientos automáticos de inventario

3. **GESTIÓN DE UBICACIONES**
   - Casa (producción)
   - Tienda Principal
   - Tienda Secundaria
   - Traslados entre ubicaciones

4. **PEDIDOS DE CLIENTES**
   - Registro de pedidos con fecha de entrega
   - Reserva de stock específico
   - Estados: Pendiente, En Preparación, Entregado, Cancelado

5. **HISTORIAL DE MOVIMIENTOS**
   - Registro completo de todos los movimientos de inventario
   - Trazabilidad total del stock

---

## 🔄 PROCESO DE MIGRACIÓN

### PASO 1: Respaldo Automático ✅

El script de migración creará automáticamente un respaldo de tu base de datos:
- Archivo: `ventas_calzado_backup_[fecha].db`
- Ubicación: misma carpeta del proyecto

### PASO 2: Ejecutar Migración

```bash
python migracion_v1_2.py
```

**El script preguntará confirmación antes de proceder.**

### PASO 3: Verificación

El script verificará:
- ✅ Creación de nuevas tablas
- ✅ Migración de productos existentes a variantes
- ✅ Creación de ubicaciones predeterminadas
- ✅ Índices para optimización

### PASO 4: Iniciar Sistema v1.2

```bash
python app_v1_2.py
```

Accede a: **http://localhost:5000**

---

## 🗄️ NUEVA ESTRUCTURA DE BASE DE DATOS

### Tablas Nuevas:

#### 1. `ubicaciones`
```
- id_ubicacion (PK)
- nombre
- tipo (produccion/almacen/tienda)
- descripcion
- activo
```

**Ubicaciones predeterminadas:**
- Casa (producción)
- Tienda Principal (almacén)
- Tienda Secundaria (almacén)

#### 2. `productos_base`
```
- codigo_producto (PK)
- nombre
- tipo
- activo
```

#### 3. `variantes`
```
- id_variante (PK)
- codigo_producto (FK)
- cuero
- color
- serie_tallas
- pares_por_docena (default: 12)
- costo_unitario
- precio_sugerido
- activo
```

**IMPORTANTE:** Tus productos actuales se migran automáticamente a esta estructura.

#### 4. `inventario`
```
- id_inventario (PK)
- id_variante (FK)
- id_ubicacion (FK)
- tipo_stock ('general' o 'pedido')
- cantidad_pares
- id_pedido_cliente (FK, opcional)
```

#### 5. `pedidos_cliente`
```
- id_pedido (PK)
- cliente
- fecha_pedido
- fecha_entrega_estimada
- estado
- total_pares
```

#### 6. `pedidos_detalle`
```
- id_detalle (PK)
- id_pedido (FK)
- id_variante (FK)
- cantidad_pares
- precio_unitario
- subtotal
```

#### 7. `movimientos_inventario`
```
- id_movimiento (PK)
- tipo_movimiento (ingreso/egreso/traslado/ajuste/venta/preparacion)
- id_variante (FK)
- id_ubicacion_origen (FK)
- id_ubicacion_destino (FK)
- cantidad_pares
- tipo_stock
- motivo
- fecha_movimiento
```

### Tablas Preservadas (Compatibilidad):

- ✅ `productos` - Se mantiene para referencia histórica
- ✅ `ventas` - Todas tus ventas históricas intactas
- ✅ `logistica` - Datos de envíos preservados

---

## 📊 FLUJO DE TRABAJO CON V1.2

### 1️⃣ PRODUCCIÓN (Lunes/Martes)

**Ingresar nueva producción:**
1. Ir a **Inventario** → **Ingresar Stock**
2. Seleccionar variante (Código + Cuero + Color + Serie)
3. Seleccionar ubicación: **Casa**
4. Tipo: **Stock General**
5. Ingresar cantidad en pares (ej: 12, 24, 36...)
6. Motivo: "Producción semanal"

**Sistema registra:**
- ✅ Incremento de inventario en Casa
- ✅ Movimiento de tipo "ingreso"

### 2️⃣ TRASLADOS

**Mover stock de Casa a Tienda Principal:**
1. Ir a **Inventario** → **Trasladar**
2. Seleccionar variante
3. Desde: **Casa**
4. Hacia: **Tienda Principal**
5. Cantidad de pares

**Sistema registra:**
- ✅ Descuento en ubicación origen
- ✅ Incremento en ubicación destino
- ✅ Movimiento de tipo "traslado"

### 3️⃣ PEDIDOS DE CLIENTES

**Crear pedido reservado:**
1. Ir a **Pedidos Cliente** → **Nuevo Pedido**
2. Ingresar cliente y fecha de entrega
3. Agregar variantes al pedido

**Reservar stock:**
1. Ir a **Inventario** → **Ingresar Stock**
2. Seleccionar variante del pedido
3. Tipo: **Pedido Cliente**
4. Asociar con el pedido creado

**Stock reservado se muestra separado del stock general.**

### 4️⃣ CONSULTAR INVENTARIO

**Vista general:**
- **Inventario** muestra todas las variantes
- Columnas separadas: Stock General | Pedidos | Total
- Códigos de color según nivel de stock

**Vista detallada:**
- Click en variante → Ver distribución por ubicación
- Historial de movimientos
- Stock general vs reservado

---

## 🎯 VENTAJAS DEL NUEVO SISTEMA

### ✅ Control de Variantes
- Cada combinación (cuero + color + serie) es única
- Costos y precios específicos por variante
- Márgenes de ganancia por variante

### ✅ Inventario Real
- Sabes exactamente qué tienes en cada ubicación
- Separación clara entre stock libre y reservado
- No venderás stock comprometido

### ✅ Trazabilidad
- Cada movimiento queda registrado
- Auditoría completa de inventario
- Historial de ingresos, traslados y salidas

### ✅ Pedidos Organizados
- Fechas de entrega visibles
- Alertas de pedidos próximos a vencer
- Control de cumplimiento

---

## 🔧 COMPATIBILIDAD Y DATOS HISTÓRICOS

### ✅ Datos Preservados
- Todas tus ventas históricas permanecen intactas
- Módulo de análisis sigue funcionando con datos previos
- Puedes consultar ventas antiguas en **Ventas Históricas**

### ✅ Migración Automática
- Productos → migrados a productos_base + variantes
- Estructura preservada
- Sin pérdida de información

### ✅ Rollback Posible
Si algo sale mal, puedes restaurar el respaldo:
```bash
# Detener la aplicación
# Renombrar el respaldo
mv ventas_calzado_backup_[fecha].db ventas_calzado.db
```

---

## 📱 INTERFAZ WEB

### Módulos Principales:

1. **Dashboard** (`/`)
   - Estadísticas generales
   - Stock general vs pedidos
   - Ventas recientes

2. **Inventario** (`/inventario`)
   - Vista consolidada
   - Ingresar stock
   - Trasladar entre ubicaciones
   - Ver detalles por variante

3. **Variantes** (`/variantes`)
   - Catálogo completo
   - Crear nueva variante
   - Ver stock por variante
   - Calcular márgenes

4. **Ubicaciones** (`/ubicaciones`)
   - Gestionar almacenes
   - Ver stock por ubicación
   - Activar/desactivar

5. **Pedidos Cliente** (`/pedidos_cliente`)
   - Lista de pedidos
   - Estados y fechas
   - Control de entregas

---

## ⚠️ IMPORTANTE

### Antes de Migrar:
- ✅ Asegúrate de tener Python 3.8+
- ✅ Instala dependencias: `pip install -r requirements.txt`
- ✅ Cierra cualquier aplicación que use la BD
- ✅ Haz un respaldo manual adicional (opcional)

### Después de Migrar:
- ✅ Usa `app_v1_2.py` (no el `app.py` antiguo)
- ✅ Revisa que las ubicaciones estén creadas
- ✅ Verifica que tus productos se migraron correctamente
- ✅ Empieza a usar el sistema nuevo

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "Database is locked"
```bash
# Cierra todas las instancias de la app
# Reinicia la migración
```

### Error: "UNIQUE constraint failed"
```bash
# Ya existe un registro con esa combinación
# Verifica los datos antes de insertar
```

### La migración no termina
```bash
# Verifica que la base de datos no esté en uso
# Revisa permisos de escritura en la carpeta
```

### Quiero volver atrás
```bash
# Restaura el respaldo
mv ventas_calzado_backup_[fecha].db ventas_calzado.db
# Usa app.py (versión antigua)
python app.py
```

---

## 📈 PRÓXIMAS FASES

### Fase 3: PREPARACIÓN DE MERCADERÍA
- Registro de qué llevar a vender
- Días de venta (Jueves, Viernes, Sábado)
- Descuento temporal de inventario

### Fase 4: VENTAS MEJORADAS
- Vincular ventas a preparación
- Registro en docenas
- Actualización automática de inventario
- Entrega automática de pedidos

---

## 📞 SOPORTE

Si encuentras problemas:
1. Revisa esta guía
2. Verifica el respaldo automático
3. Consulta los logs de error
4. Restaura el respaldo si es necesario

---

**¡Estás listo para usar el Sistema v1.2!** 🚀

El sistema ahora refleja tu flujo de trabajo real y te da control total sobre tu inventario.
