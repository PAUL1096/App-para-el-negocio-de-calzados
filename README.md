# 👞 Sistema de Gestión de Calzado v2.0

Sistema completo de gestión empresarial para negocios de fabricación y venta de calzado. Gestiona desde el catálogo de modelos hasta las ventas y cobranzas.

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/PAUL1096/App-para-el-negocio-de-calzados)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-Private-red.svg)](LICENSE)

---

## 📋 Características Principales

### 🎨 Catálogo de Variantes Base
- Gestión de modelos/plantillas de calzado
- Código interno, tipo, horma, segmento
- Base para producción de productos concretos

### 🏭 Producción
- Registro de productos fabricados desde variantes base
- Materiales: cuero, color, suela, forro, **material de plantilla**
- Serie de tallas y cantidad producida
- **Ingreso parcial de inventario** (ej: producir 12, ingresar 6)
- Tracking de pares producidos vs ingresados

### 📦 Inventario
- Stock físico por ubicación (tiendas, almacenes)
- Ingreso total o parcial de productos
- Traslados entre ubicaciones
- Validación de stock en tiempo real
- Transacciones atómicas

### 📍 Ubicaciones
- Gestión de tiendas y almacenes
- Stock por ubicación
- Tipos: almacén, tienda, bodega

### 📋 Preparaciones
- Preparar mercadería para envío
- Multiproducto
- Destino: tienda específica o sin destino
- Validación de stock antes de crear
- Confirmar llegada a destino

### 💰 Ventas
- **Ventas multiproducto** (carrito de compras)
- Venta desde preparación o directa desde inventario
- **Modalidades de pago:**
  - Contado (efectivo, transferencia)
  - Crédito sin pago inicial
  - **Crédito con pago inicial** (parcial)
- **Cliente Desconocido** (ventas sin cliente)
- Descuentos por línea y globales
- Registro de pagos con **fecha personalizable**

### 💳 Cuentas por Cobrar
- Creación automática al hacer venta a crédito
- **Cuentas Vigentes** (pendientes, no vencidas)
- **Cuentas Vencidas** (con días de mora)
- Ventas pendientes sin cuenta formal
- Registro de pagos parciales o totales
- Historial completo de pagos
- Top deudores

### 👥 Clientes
- Gestión completa de clientes
- Días de crédito personalizados
- Historial de cuentas por cobrar
- Estadísticas de deuda

### 📊 Dashboard
- Métricas de negocio en tiempo real
- Ventas hoy y del mes (cantidad + monto)
- Cuentas por cobrar pendientes
- Productos sin ingresar a inventario
- Preparaciones activas
- Flujo completo del sistema visualizado

---

## 🚀 Instalación Rápida

### Requisitos
- Python 3.8 o superior
- pip (gestor de paquetes)

### Opción 1: Desde GitHub

```bash
# Clonar repositorio
git clone https://github.com/PAUL1096/App-para-el-negocio-de-calzados.git
cd App-para-el-negocio-de-calzados

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python datos_iniciales.py

# Iniciar aplicación
python app_v2.py
```

### Opción 2: Desde ZIP

1. Descargar ZIP desde GitHub
2. Extraer archivos
3. Abrir terminal en la carpeta
4. Ejecutar:
```bash
pip install flask
python datos_iniciales.py
python app_v2.py
```

### Abrir en Navegador

```
http://localhost:5000
```

---

## 📖 Documentación

- **[GUIA_INSTALACION.md](GUIA_INSTALACION.md)** - Instalación detallada paso a paso
- **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Guía rápida de uso del sistema
- **[PREPARAR_PARA_PRODUCCION.md](PREPARAR_PARA_PRODUCCION.md)** - Cómo limpiar datos de prueba
- **[REVISION_FINAL.md](REVISION_FINAL.md)** - Checklist completo de funcionalidades
- **[ARQUITECTURA_TECNICA.md](ARQUITECTURA_TECNICA.md)** - Detalles técnicos del sistema

---

## 🎯 Flujo del Sistema

```
1. CATÁLOGO → 2. PRODUCCIÓN → 3. INVENTARIO
                                    ↓
                           4. PREPARACIONES
                                    ↓
                        5. VENTAS (multiproducto)
                                    ↓
                    6. CUENTAS POR COBRAR → 7. PAGOS
```

### Flujo Detallado

1. **Crear Variante Base** (modelo/plantilla)
2. **Producir Producto** (materializar con cuero, color, suela, etc.)
3. **Ingresar a Inventario** (total o parcial)
4. **Preparar Mercadería** (opcional, para envíos)
5. **Realizar Venta** (multiproducto, contado/crédito)
6. **Gestionar Cobranzas** (si es venta a crédito)
7. **Registrar Pagos** (parciales o totales)

---

## 📂 Estructura del Proyecto

```
App-para-el-negocio-de-calzados/
├── app_v2.py                    # Aplicación principal ⭐
├── calzado.db                   # Base de datos SQLite
├── requirements.txt             # Dependencias
│
├── datos_iniciales.py           # Script de inicialización
├── limpiar_datos_prueba.py      # Script de limpieza de datos
│
├── templates/                   # Vistas HTML (18 archivos)
│   ├── base.html                # Plantilla base
│   ├── index_v2.html            # Dashboard
│   ├── catalogo_variantes.html  # Catálogo
│   ├── produccion.html          # Producción
│   ├── inventario.html          # Inventario
│   ├── preparaciones_v2.html    # Preparaciones
│   ├── ventas_v2.html           # Ventas
│   ├── cuentas_por_cobrar.html  # Cuentas por cobrar
│   ├── clientes.html            # Clientes
│   └── ...
│
└── *.md                         # Documentación
```

---

## 🗄️ Modelo de Datos

### Concepto Clave: Separación entre Modelo y Producto

**Variante Base** = Modelo/Plantilla (Código, Tipo, Horma)
**Producto** = Materialización (Variante + Cuero + Color + Suela + Forro + Plantilla)
**Inventario** = Stock físico de productos en ubicaciones

### Principales Tablas

- `variantes_base` - Modelos/plantillas de calzado
- `productos_producidos` - Productos fabricados concretos
- `inventario` - Stock físico por ubicación
- `ubicaciones` - Tiendas y almacenes
- `preparaciones` + `preparaciones_detalle` - Mercadería preparada
- `ventas_v2` + `ventas_detalle` - Ventas multiproducto
- `cuentas_por_cobrar` - Cuentas a crédito
- `pagos` - Historial de pagos
- `clientes` - Datos de clientes

---

## ✨ Funcionalidades Destacadas

### Ingreso Parcial de Inventario
Si produces 12 pares pero solo 6 pasan control de calidad, puedes ingresar parcialmente:
- Total producido: 12 pares
- Ingresado: 6 pares
- Pendiente: 6 pares (aparece como alerta)

### Ventas Multiproducto
Carrito de compras que permite:
- Agregar múltiples productos a una sola venta
- Descuentos por línea y descuento global
- Pago: contado, crédito total, o crédito con pago inicial

### Cliente Desconocido
Permite registrar ventas sin necesidad de crear cliente (ej: ventas al público general), útil para ventas a crédito ocasionales.

### Cuentas por Cobrar Inteligente
- Creación automática al vender a crédito
- Cálculo automático de fecha de vencimiento según días de crédito del cliente
- Secciones: Vigentes, Vencidas, sin cuenta formal
- Registro de pagos con fecha personalizable (pagos diferidos)

---

## 🛠️ Tecnologías

- **Backend**: Python 3.8+ con Flask 3.0
- **Base de Datos**: SQLite (producción: migrar a PostgreSQL/MySQL)
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Iconos**: Bootstrap Icons

---

## 🌐 Acceso en Red Local

Para acceder desde otras computadoras en la misma red:

1. Obtener IP del servidor:
   ```bash
   # Windows
   ipconfig

   # Linux/Mac
   ifconfig
   ```

2. En `app_v2.py`, verificar que tenga:
   ```python
   app.run(debug=False, host='0.0.0.0', port=5000)
   ```

3. Configurar firewall para permitir puerto 5000

4. Acceder desde otro dispositivo:
   ```
   http://192.168.1.X:5000
   ```

---

## 💾 Respaldo de Datos

**IMPORTANTE**: Respalda regularmente `calzado.db`

```bash
# Respaldo manual
cp calzado.db respaldo_calzado_2026-01-16.db
```

Para respaldo automático, consulta [GUIA_INSTALACION.md](GUIA_INSTALACION.md)

---

## 🆘 Solución de Problemas

### "No module named 'flask'"
```bash
pip install flask
# o
python -m pip install flask
```

### "Address already in use (puerto 5000)"
```bash
# Windows: Encontrar proceso
netstat -ano | findstr :5000
taskkill /PID [número] /F

# Linux/Mac
lsof -i :5000
kill -9 [PID]
```

### "Database is locked"
1. Cerrar todas las instancias de la aplicación
2. Eliminar archivos `*.db-journal` y `*.db-wal` si existen
3. Reiniciar

### Error al crear venta a crédito
Verificar que la migración de cliente NULL se haya ejecutado correctamente.

---

## 🔒 Notas de Seguridad

Esta es una versión para **uso interno**. Para ambiente de producción externa:

- [ ] Implementar autenticación de usuarios
- [ ] Usar HTTPS
- [ ] Sanitizar todos los inputs (prevenir SQL injection)
- [ ] Migrar a base de datos robusta (PostgreSQL)
- [ ] Implementar backups automáticos
- [ ] Control de acceso por roles
- [ ] Logs de auditoría

---

## 📝 Changelog

### v2.0.0 (Enero 2026)
- ✨ Rediseño completo del sistema
- ✨ Ventas multiproducto con carrito
- ✨ Cuentas por cobrar con secciones vigentes/vencidas
- ✨ Ingreso parcial de inventario
- ✨ Cliente Desconocido para ventas sin cliente
- ✨ Dashboard con métricas de negocio
- ✨ Material de plantilla en productos
- 🐛 42 archivos obsoletos eliminados del repositorio
- 📚 Documentación completa agregada

### v1.0.0 (Noviembre 2024)
- 🎉 Versión inicial del sistema

---

## 👥 Contribución

Este es un proyecto privado de uso interno.

---

## 📄 Licencia

Uso privado y propietario.

---

## 🎓 Soporte

Para soporte técnico o consultas, contacta al desarrollador del sistema.

---

**Versión**: 2.0.0
**Última Actualización**: Enero 2026
**Estado**: ✅ Producción
**Desarrollado para**: Optimizar la gestión completa de negocios de calzado
