# 🛍️ Sistema de Gestión de Ventas de Calzado

Sistema web completo para el registro, análisis y visualización de ventas de calzado, con módulos de logística y reportes interactivos.

## 📋 Características Principales

### Módulo de Registro
- ✅ Registro rápido de ventas semanales
- ✅ Integración con catálogo de productos
- ✅ Gestión de logística y envíos
- ✅ Cálculo automático de totales
- ✅ Múltiples métodos de pago

### Módulo de Análisis
- 📊 Dashboard con indicadores clave
- 📈 Gráficos interactivos de ventas semanales
- 🏆 Ranking de productos más vendidos
- 🗺️ Análisis por destinos
- 🚚 Estadísticas de logística y transporte
- 📅 Filtros por año y período

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Instalar Dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Importar Datos Iniciales

```bash
python import_data.py
```

Este comando importará los datos del archivo Excel a la base de datos SQLite.

### Paso 3: Iniciar la Aplicación

```bash
python app.py
```

El sistema estará disponible en: **http://localhost:5000**

## 📁 Estructura del Proyecto

```
sistema_ventas_calzado/
│
├── app.py                      # Aplicación Flask principal
├── import_data.py              # Script de importación de datos
├── requirements.txt            # Dependencias del proyecto
├── ventas_calzado.db          # Base de datos SQLite (se crea automáticamente)
│
├── templates/                  # Plantillas HTML
│   ├── base.html              # Plantilla base
│   ├── index.html             # Dashboard principal
│   ├── registro_venta.html    # Formulario de registro
│   ├── analisis.html          # Módulo de análisis
│   └── productos.html         # Catálogo de productos
│
└── static/                     # Archivos estáticos
    └── css/
        └── style.css          # Estilos personalizados
```

## 🗄️ Estructura de la Base de Datos

### Tabla: productos
- codigo_calzado (PK)
- tipo
- cuero
- color
- serie_tallas
- costo_unitario
- precio_sugerido
- observaciones

### Tabla: ventas
- id_venta (PK)
- fecha
- cliente
- destino
- codigo_calzado (FK)
- cuero
- color
- calidad
- precio_unitario
- pares
- total_venta
- estado_pago
- metodo_pago
- comentario
- año
- semana
- dia_semana

### Tabla: logistica
- id_envio (PK)
- id_venta (FK)
- costo_envio
- destino
- agencia
- fecha_envio
- observaciones

## 📊 Uso del Sistema

### Dashboard Principal
Accede a **/** para ver:
- Estadísticas generales (total ventas, ingresos, pares vendidos)
- Venta promedio
- Últimas 10 ventas registradas
- Accesos rápidos a módulos

### Registrar Nueva Venta
1. Ir a **Registrar Venta**
2. Completar el formulario:
   - Datos de la venta (fecha, cliente, destino)
   - Seleccionar producto (autocompleta precio y características)
   - Ingresar cantidad de pares
   - Seleccionar método y estado de pago
   - Opcionalmente, agregar información de logística
3. Guardar

### Módulo de Análisis
Accede a **/analisis** para:
- Ver gráficos de ventas semanales por año
- Analizar productos más vendidos
- Revisar distribución por tipo de producto
- Analizar ventas por destino
- Revisar estadísticas de agencias de transporte

### Gestión de Productos
Accede a **/productos** para:
- Ver catálogo completo de productos
- Revisar costos, precios y márgenes
- Obtener estadísticas del catálogo

## 🔌 API Endpoints

### Consultas
- `GET /api/producto/<codigo>` - Obtener información de un producto
- `GET /api/analisis/ventas_semanales?año=2024` - Ventas por semana
- `GET /api/analisis/productos_top?limite=10` - Top productos
- `GET /api/analisis/destinos` - Análisis por destino
- `GET /api/analisis/logistica` - Estadísticas de logística

### Operaciones
- `POST /api/guardar_venta` - Registrar nueva venta

## 🎯 Roadmap de Desarrollo

### ✅ Fase 1 (Completada)
- Sistema de registro de ventas
- Dashboard con estadísticas
- Módulo de análisis con gráficos
- Gestión de productos
- Integración con logística

### 📋 Fase 2 (Próxima)
- Gestión de inventario en tiempo real
- Control de stock por modelo y talla
- Alertas de reabastecimiento
- Registro de proveedores

### 📋 Fase 3 (Futura)
- Módulo de producción
- Seguimiento de materiales
- Costos de producción
- Integración completa de la cadena

### 📋 Fase 4 (Expansión)
- Aplicación móvil
- Reportes avanzados en PDF
- Sistema de notificaciones
- Exportación a Excel/CSV

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3 + Flask
- **Base de Datos**: SQLite
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Gráficos**: Chart.js
- **Iconos**: Bootstrap Icons

## 📱 Acceso desde Otros Dispositivos

Para acceder desde otros dispositivos en la misma red:

1. Obtén tu IP local:
   - Windows: `ipconfig`
   - Linux/Mac: `ifconfig` o `ip addr`

2. Accede desde otro dispositivo usando:
   `http://[TU_IP]:5000`

## 🔒 Seguridad

**Nota**: Esta es una versión de desarrollo. Para producción:
- Cambia `app.secret_key` por una clave segura
- Implementa autenticación de usuarios
- Usa HTTPS
- Migra a una base de datos robusta (PostgreSQL, MySQL)
- Implementa validación exhaustiva de datos

## 🆘 Solución de Problemas

### Error: "No module named flask"
```bash
pip install -r requirements.txt
```

### Error: "Database is locked"
- Cierra todas las instancias de la aplicación
- Reinicia el servidor

### Los gráficos no se muestran
- Verifica tu conexión a internet (Chart.js se carga desde CDN)
- Revisa la consola del navegador (F12)

## 📝 Licencia

Este sistema es de uso interno y privado.

## 👥 Soporte

Para consultas sobre el sistema, contacta al administrador.

---

**Versión**: 1.0  
**Fecha**: Noviembre 2024  
**Desarrollado para**: Optimizar la gestión de ventas de calzado
