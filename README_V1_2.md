# 🛍️ Sistema de Gestión de Ventas de Calzado v1.2

Sistema web completo para la gestión de inventario, variantes, pedidos y ventas de calzado por mayor.

---

## ✨ NOVEDADES VERSIÓN 1.2

### 🎯 Características Principales

#### 1. **Sistema de Variantes**
- Modelo Base → Variante (Código + Cuero + Color + Serie)
- Cada variante con costo y precio independiente
- Gestión de series de tallas (docenas)
- Cálculo automático de márgenes

#### 2. **Inventario Avanzado**
- **Stock General**: Disponible para venta libre
- **Stock Pedidos**: Reservado con fecha de entrega
- Control por ubicación (almacenes)
- Trazabilidad completa de movimientos

#### 3. **Ubicaciones/Almacenes**
- Casa (producción)
- Tienda Principal (almacén grande)
- Tienda Secundaria (almacén pequeño)
- Traslados entre ubicaciones

#### 4. **Pedidos de Clientes**
- Registro con fecha de entrega
- Estados: Pendiente, En Preparación, Entregado, Cancelado
- Alertas de vencimiento
- Reserva de stock específico

#### 5. **Historial Completo**
- Todos los movimientos registrados
- Tipos: Ingreso, Egreso, Traslado, Ajuste, Venta
- Auditoría de inventario

---

## 🚀 INSTALACIÓN Y USO

### Requisitos
- Python 3.8 o superior
- pip (gestor de paquetes)

### Instalación

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar migración (SOLO LA PRIMERA VEZ)
python migracion_v1_2.py

# 3. Iniciar aplicación v1.2
python app_v1_2.py
```

El sistema estará disponible en: **http://localhost:5000**

### ⚠️ IMPORTANTE
- Ejecuta `migracion_v1_2.py` SOLO UNA VEZ
- Usa `app_v1_2.py` (no el antiguo `app.py`)
- Se creará un respaldo automático de tu BD

---

## 📁 ESTRUCTURA DEL PROYECTO

```
sistema_ventas_calzado/
│
├── app_v1_2.py                 # ⭐ Aplicación Flask v1.2 (USAR ESTE)
├── app.py                       # Legacy (compatibilidad)
├── migracion_v1_2.py           # Script de migración a v1.2
├── import_data.py              # Importador de datos desde Excel
├── requirements.txt            # Dependencias
├── ventas_calzado.db          # Base de datos SQLite
│
├── templates/                  # 🎨 Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── index.html             # Dashboard principal
│   ├── inventario.html        # Módulo de inventario
│   ├── variantes.html         # Gestión de variantes
│   ├── ubicaciones.html       # Gestión de ubicaciones
│   ├── pedidos_cliente.html   # Pedidos de clientes
│   ├── productos_base.html    # Catálogo base
│   ├── analisis.html          # Análisis y reportes
│   └── ventas_historicas.html # Ventas previas
│
├── static/                     # Archivos estáticos
│   └── css/
│       └── style.css          # Estilos personalizados
│
└── docs/                       # 📚 Documentación
    ├── GUIA_MIGRACION_V1_2.md # Guía completa de migración
    ├── README_V1_2.md         # Este archivo
    └── ...
```

---

## 🗄️ BASE DE DATOS

### Nuevas Tablas v1.2:

| Tabla | Descripción |
|-------|-------------|
| `ubicaciones` | Almacenes y puntos de producción |
| `productos_base` | Modelos principales de calzado |
| `variantes` | Combinaciones: Código+Cuero+Color+Serie |
| `inventario` | Stock por variante, ubicación y tipo |
| `pedidos_cliente` | Pedidos con fecha de entrega |
| `pedidos_detalle` | Detalle de cada pedido |
| `movimientos_inventario` | Historial de todos los movimientos |

### Tablas Preservadas (Compatibilidad):

| Tabla | Estado |
|-------|--------|
| `productos` | ✅ Mantiene datos históricos |
| `ventas` | ✅ Todas las ventas intactas |
| `logistica` | ✅ Datos de envíos preservados |

---

## 📊 USO DEL SISTEMA

### 🏠 Dashboard Principal
- Estadísticas generales (ventas, ingresos)
- Stock general vs pedidos
- Accesos rápidos a módulos
- Últimas ventas

### 📦 Módulo de Inventario

**Ingresar Stock (Producción):**
1. Inventario → Ingresar Stock
2. Seleccionar variante
3. Ubicación: Casa (producción)
4. Tipo: Stock General
5. Cantidad en pares

**Trasladar entre ubicaciones:**
1. Inventario → Trasladar
2. Variante + Desde → Hacia
3. Cantidad de pares

**Consultar stock:**
- Vista general: todas las variantes
- Vista detallada: click en variante
- Filtros por código, tipo, stock mínimo

### 🎨 Módulo de Variantes

**Crear nueva variante:**
1. Variantes → Nueva Variante
2. Código producto + Cuero + Color
3. Serie de tallas (ej: Serie Normal)
4. Pares por docena (default: 12)
5. Costo unitario + Precio sugerido

**Visualizar:**
- Catálogo completo de variantes
- Márgenes de ganancia automáticos
- Stock disponible por variante

### 📍 Módulo de Ubicaciones

**Gestionar almacenes:**
- Ver ubicaciones activas
- Stock por ubicación
- Crear nuevas ubicaciones
- Activar/desactivar

**Ubicaciones predeterminadas:**
- Casa (producción)
- Tienda Principal
- Tienda Secundaria

### 📋 Módulo de Pedidos

**Crear pedido de cliente:**
1. Pedidos → Nuevo Pedido
2. Cliente + Fecha de entrega
3. Agregar variantes

**Reservar stock:**
1. Inventario → Ingresar Stock
2. Tipo: **Pedido Cliente**
3. Asociar con pedido

**Control:**
- Estados de pedidos
- Alertas de vencimiento
- Cumplimiento de entregas

---

## 🔄 FLUJO DE TRABAJO SEMANAL

### Lunes/Martes: Producción
```
Ingresar nuevas docenas → Ubicación: Casa → Stock General
```

### Miércoles: Preparación
```
Trasladar stock → Casa → Tienda Principal
(Módulo de Preparación: próxima fase)
```

### Jueves/Viernes/Sábado: Ventas
```
Registro de ventas desde preparación
(Funcionalidad completa: próxima fase)
```

---

## 🎯 ARQUITECTURA: PRODUCTO → VARIANTE → INVENTARIO

```
PRODUCTO BASE (Código 101)
    │
    ├─ VARIANTE 1: 101 + huante + negro + Serie Normal
    │   ├─ Inventario Casa: 24 pares (general)
    │   ├─ Inventario Tienda: 36 pares (general)
    │   └─ Inventario Tienda: 12 pares (pedido Cliente A)
    │
    ├─ VARIANTE 2: 101 + cuero + marrón + Serie Normal
    │   └─ Inventario Casa: 12 pares (general)
    │
    └─ VARIANTE 3: 101 + huante + negro + Serie Especial
        └─ Inventario Tienda: 24 pares (pedido Cliente B)
```

---

## 🔌 API ENDPOINTS

### Ubicaciones
- `POST /api/ubicaciones/crear` - Crear ubicación
- `GET /api/ubicaciones/<id>` - Obtener ubicación
- `PUT /api/ubicaciones/<id>/editar` - Editar ubicación

### Variantes
- `POST /api/variantes/crear` - Crear variante
- `GET /api/variantes/<id>` - Obtener variante
- `PUT /api/variantes/<id>/editar` - Editar variante

### Inventario
- `POST /api/inventario/ingresar` - Ingresar stock
- `POST /api/inventario/trasladar` - Trasladar entre ubicaciones

### Pedidos
- `POST /api/pedidos/crear` - Crear pedido cliente

---

## 🛠️ TECNOLOGÍAS

- **Backend**: Python 3 + Flask
- **Base de Datos**: SQLite (con respaldos automáticos)
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **JavaScript**: Vanilla JS
- **Iconos**: Bootstrap Icons

---

## 📈 ROADMAP

### ✅ Fase 1+2 (ACTUAL)
- ✅ Sistema de variantes
- ✅ Inventario (stock general + pedidos)
- ✅ Ubicaciones
- ✅ Movimientos de inventario
- ✅ Pedidos de clientes

### 📋 Fase 3 (Próxima)
- Preparación de mercadería
- Registro de qué llevar a vender
- Días de venta configurables
- Descuento temporal de inventario

### 📋 Fase 4 (Futura)
- Ventas vinculadas a preparación
- Registro en docenas
- Actualización automática de inventario
- Entrega automática de pedidos

### 📋 Fase 5 (Expansión)
- Reportes PDF
- Gráficos avanzados
- Exportación Excel/CSV
- Aplicación móvil

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### La migración falla
```bash
# Verifica permisos de escritura
# Cierra otras apps usando la BD
# Revisa el respaldo automático creado
```

### No puedo iniciar app_v1_2.py
```bash
# Verifica que ejecutaste la migración primero
python migracion_v1_2.py

# Reinstala dependencias
pip install -r requirements.txt
```

### Error "Database is locked"
```bash
# Cierra todas las instancias
# Reinicia el servidor
```

### Quiero restaurar versión anterior
```bash
# Usa el respaldo creado automáticamente
mv ventas_calzado_backup_[fecha].db ventas_calzado.db
python app.py
```

---

## 📞 DOCUMENTACIÓN ADICIONAL

- **GUIA_MIGRACION_V1_2.md**: Guía detallada de migración
- **ARQUITECTURA_TECNICA.md**: Detalles técnicos del sistema
- **PLAN_DESARROLLO.md**: Roadmap y próximas fases

---

## 📝 NOTAS IMPORTANTES

### ⚠️ Migración
- Ejecuta `migracion_v1_2.py` SOLO UNA VEZ
- Se crea respaldo automático
- Datos históricos preservados
- Rollback disponible

### ⚠️ Uso Diario
- Usa `app_v1_2.py` (no app.py)
- Los módulos legacy siguen disponibles
- Ventas históricas consultables

### ⚠️ Seguridad
- Cambia `app.secret_key` en producción
- Implementa autenticación si es necesario
- Usa HTTPS en producción
- Haz respaldos periódicos

---

## 📊 DIFERENCIAS vs v1.0

| Característica | v1.0 | v1.2 |
|----------------|------|------|
| Productos | Un solo nivel | Base + Variantes |
| Inventario | No existe | Stock General + Pedidos |
| Ubicaciones | No | Casa + Tiendas |
| Pedidos Cliente | No | Sí, con fechas |
| Trazabilidad | No | Movimientos completos |
| Series de Tallas | Texto simple | Configuración por variante |
| Costos/Precios | Por producto | Por variante |

---

## ✅ BENEFICIOS v1.2

1. **Control Real**: Sabes exactamente qué tienes y dónde
2. **No Sobrevender**: Stock reservado separado del disponible
3. **Trazabilidad**: Historial de cada movimiento
4. **Precisión**: Costos y precios por variante exacta
5. **Organización**: Flujo de trabajo real del negocio
6. **Escalabilidad**: Preparado para crecimiento

---

**Versión**: 1.2
**Fecha**: Diciembre 2025
**Desarrollado con**: Flask + SQLite
**Modelo de Negocio**: Calzado por Mayor (Docenas)

---

🚀 **¡Sistema listo para gestionar tu negocio de calzado!**
