# Guia: Usar Supabase como Base de Datos

Supabase ofrece PostgreSQL gratuito con mejor estabilidad que Render PostgreSQL.

## Ventajas de Supabase

- **Datos persistentes**: No se borran con redeploys
- **Dashboard visual**: Ver y editar datos desde el navegador
- **500 MB gratis**: Suficiente para negocios pequeños/medianos
- **Backups automaticos**: Incluso en plan gratuito
- **API REST incluida**: Para futuras integraciones

---

## PASO 1: Crear cuenta en Supabase

1. Ve a [supabase.com](https://supabase.com)
2. Click en **"Start your project"**
3. Registrate con GitHub (recomendado) o email

---

## PASO 2: Crear nuevo proyecto

1. Click en **"New Project"**
2. Completa:

| Campo | Valor |
|-------|-------|
| **Name** | `calzado-db` |
| **Database Password** | (genera una segura y GUARDALA) |
| **Region** | `South America (Sao Paulo)` o la mas cercana |
| **Plan** | `Free` |

3. Click en **"Create new project"**
4. Espera ~2 minutos mientras se crea

---

## PASO 3: Obtener URL de conexion

1. En tu proyecto, ve a **Settings** (icono engranaje)
2. Click en **"Database"** en el menu lateral
3. Busca la seccion **"Connection string"**
4. Selecciona **"URI"**
5. Copia la URL, se ve asi:
   ```
   postgresql://postgres.[tu-proyecto]:[password]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   ```
6. **IMPORTANTE**: Reemplaza `[YOUR-PASSWORD]` con la contraseña que creaste

---

## PASO 4: Configurar en Render

1. Ve a tu Web Service en Render
2. Click en **"Environment"**
3. Busca la variable `DATABASE_URL`
4. **Reemplaza** el valor con la URL de Supabase
5. Click en **"Save Changes"**

Render hara redeploy automaticamente.

---

## PASO 5: Verificar conexion

1. Espera que el deploy termine (~2 min)
2. Abre tu app y prueba crear una variante
3. En Supabase, ve a **"Table Editor"** y verifica que aparezca

---

## Estructura de tablas

La app creara automaticamente estas tablas en Supabase:

| Tabla | Descripcion |
|-------|-------------|
| `variantes_base` | Modelos/plantillas de calzado |
| `productos_producidos` | Productos fabricados |
| `ubicaciones` | Tiendas y almacenes |
| `inventario` | Stock por ubicacion |
| `preparaciones` | Preparaciones de envio |
| `preparaciones_detalle` | Detalle de preparaciones |
| `clientes` | Datos de clientes |
| `ventas_v2` | Ventas realizadas |
| `ventas_detalle` | Detalle de ventas |
| `cuentas_por_cobrar` | Cuentas pendientes |
| `pagos` | Registro de pagos |

---

## Ver y editar datos en Supabase

1. Ve a tu proyecto en Supabase
2. Click en **"Table Editor"** (menu lateral)
3. Selecciona cualquier tabla
4. Puedes:
   - Ver todos los registros
   - Editar directamente
   - Filtrar y buscar
   - Exportar a CSV

---

## Hacer backup manual

### Desde Supabase Dashboard:
1. Ve a **"Table Editor"**
2. Selecciona una tabla
3. Click en **"Export"** > **"Export as CSV"**

### Desde la app (recomendado):
- Usa la funcion **"Carga Masiva"** > **"Descargar Plantilla"**
- Esto descarga un Excel con el formato correcto

---

## Limites del plan gratuito

| Recurso | Limite |
|---------|--------|
| Almacenamiento | 500 MB |
| Transferencia | 2 GB/mes |
| Proyectos | 2 activos |
| Backups | 7 dias |

Para un negocio de calzado pequeño/mediano, estos limites son **mas que suficientes**.

---

## Comparacion: Supabase vs Render PostgreSQL

| Caracteristica | Supabase Free | Render Free |
|----------------|---------------|-------------|
| Almacenamiento | 500 MB | 1 GB |
| Persistencia | Excelente | Puede reiniciarse |
| Dashboard visual | Si | No |
| Backups | 7 dias | No |
| Tiempo de vida | Ilimitado | 90 dias |

**Recomendacion**: Supabase para la base de datos, Render solo para el deploy de la app.

---

## Solucion de problemas

### Error: "password authentication failed"
- Verifica que la contraseña en la URL sea correcta
- No debe tener caracteres especiales sin codificar

### Error: "connection refused"
- Verifica que la URL sea la de "Connection string" > "URI"
- No uses la URL del "API"

### Las tablas no se crean
- Revisa los logs en Render
- Verifica que la URL este bien configurada

### Datos no aparecen en Supabase
- Asegurate de estar viendo el proyecto correcto
- Refresca la pagina del Table Editor

---

## Desarrollo local con Supabase (opcional)

Si quieres desarrollar localmente conectado a Supabase:

1. Crea un archivo `.env` en tu proyecto:
   ```
   DATABASE_URL=postgresql://postgres.[proyecto]:[password]@aws-0-sa-east-1.pooler.supabase.com:6543/postgres
   FLASK_ENV=development
   ```

2. Instala python-dotenv:
   ```bash
   pip install python-dotenv
   ```

3. La app detectara `DATABASE_URL` y usara Supabase

**Nota**: Para desarrollo normal, la app usa SQLite local automaticamente (no necesitas configurar nada).

---

## Migrar datos de Render PostgreSQL a Supabase

Si tienes datos en Render que quieres migrar:

1. Exporta desde Render usando pg_dump
2. Importa en Supabase usando el SQL Editor

O mas simple:
1. Exporta a Excel desde la app
2. Configura Supabase
3. Usa "Carga Masiva" para importar

---

Desarrollado para el Sistema de Gestion de Calzado v2.0
