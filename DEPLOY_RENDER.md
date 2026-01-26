# Guia de Despliegue en Render con PostgreSQL

Esta guia te ayudara a desplegar el Sistema de Gestion de Calzado en Render con base de datos PostgreSQL persistente.

## Ventajas de esta configuracion

- **Datos persistentes**: PostgreSQL mantiene tus datos aunque la app se reinicie
- **Despliegue automatico**: Cada `git push` actualiza la app
- **SSL gratuito**: HTTPS incluido
- **Plan gratuito generoso**: Suficiente para comenzar

---

## PASO 1: Crear cuenta en Render

1. Ve a [render.com](https://render.com)
2. Click en **"Get Started for Free"**
3. **Recomendado**: Registrate con tu cuenta de GitHub

---

## PASO 2: Crear base de datos PostgreSQL

**IMPORTANTE**: Primero creamos la base de datos, luego la aplicacion.

1. En el Dashboard de Render, click en **"New +"**
2. Selecciona **"PostgreSQL"**
3. Configura:

| Campo | Valor |
|-------|-------|
| **Name** | `calzado-db` |
| **Database** | `calzado` |
| **User** | (dejar por defecto) |
| **Region** | `Oregon (US West)` |
| **Plan** | `Free` |

4. Click en **"Create Database"**
5. **IMPORTANTE**: Espera a que el estado sea "Available" (puede tomar 1-2 minutos)
6. Copia el valor de **"Internal Database URL"** (lo necesitaras despues)
   - Se ve algo como: `postgres://user:password@host/calzado`

---

## PASO 3: Crear Web Service

1. En el Dashboard, click en **"New +"** > **"Web Service"**
2. Conecta tu cuenta de GitHub si no lo hiciste
3. Busca y selecciona: `App-para-el-negocio-de-calzados`
4. Click en **"Connect"**

### Configuracion del servicio:

| Campo | Valor |
|-------|-------|
| **Name** | `sistema-calzado` |
| **Region** | `Oregon (US West)` (misma que la BD) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app_v2:app` |
| **Plan** | `Free` |

---

## PASO 4: Configurar Variables de Entorno

En la seccion **"Environment Variables"**, agrega:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | (pega la Internal Database URL del paso 2) |
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.11.0` |

**Opcional pero recomendado**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | (una clave aleatoria larga) |

Para generar una clave segura:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## PASO 5: Crear el servicio

1. Click en **"Create Web Service"**
2. Espera mientras Render:
   - Clona tu repositorio
   - Instala dependencias (~2-3 minutos)
   - Crea las tablas en PostgreSQL automaticamente
   - Inicia la aplicacion

---

## PASO 6: Verificar despliegue

1. Una vez que el estado sea "Live", tu app estara en:
   ```
   https://sistema-calzado.onrender.com
   ```

2. La primera vez puede tardar ~30 segundos en cargar

3. Verifica que puedas:
   - Ver el dashboard
   - Crear una ubicacion
   - Crear una variante base

---

## Solucion de Problemas

### Error: "relation does not exist"
La base de datos no se inicializo correctamente.
1. Ve a tu Web Service > **"Manual Deploy"** > **"Clear build cache & deploy"**

### Error: "could not connect to server"
La variable `DATABASE_URL` no esta configurada.
1. Verifica que `DATABASE_URL` este en Environment Variables
2. Usa la **Internal Database URL**, no la External

### Error de timeout
El plan gratuito "duerme" la app despues de 15 min.
1. La primera visita tarda ~30 segundos
2. Esto es normal en el plan gratuito

### Ver logs
1. Dashboard > Tu Web Service > **"Logs"**
2. Busca errores en rojo

---

## Actualizaciones

Cada vez que hagas cambios:

```bash
git add .
git commit -m "descripcion del cambio"
git push origin main
```

Render automaticamente:
1. Detecta el push
2. Reconstruye la app
3. Reinicia con los cambios

**Tus datos en PostgreSQL se mantienen intactos.**

---

## Arquitectura Final

```
┌─────────────────────────────────────────────────────────┐
│                      RENDER                              │
│  ┌─────────────────┐      ┌─────────────────────────┐   │
│  │   Web Service   │      │   PostgreSQL Database   │   │
│  │  sistema-calzado│◄────►│      calzado-db         │   │
│  │   (Flask app)   │      │   (datos persistentes)  │   │
│  └─────────────────┘      └─────────────────────────┘   │
│          ▲                                               │
└──────────┼───────────────────────────────────────────────┘
           │
    ┌──────┴──────┐
    │   Usuario   │
    │  (Browser)  │
    └─────────────┘
```

---

## Comparacion de Planes

| Caracteristica | Free | Starter ($7/mes) |
|----------------|------|------------------|
| Web Service | 750 hrs/mes | Ilimitado |
| PostgreSQL | 1 GB, 90 dias | 1 GB, sin limite |
| Sleep | 15 min inactividad | Nunca duerme |
| Custom Domain | Si | Si |
| SSL | Si | Si |

**Nota**: La BD PostgreSQL gratuita expira a los 90 dias. Render te avisara para que hagas backup o upgrades.

---

## Backup de datos

### Exportar desde Render
1. Dashboard > Tu PostgreSQL > **"Connect"**
2. Usa la External Database URL con una herramienta como pgAdmin o DBeaver

### Desde linea de comandos
```bash
pg_dump "tu_external_database_url" > backup.sql
```

---

## Desarrollo Local con PostgreSQL de Render

Si quieres desarrollar localmente conectado a la BD de Render:

1. Copia la **External Database URL**
2. Crea un archivo `.env`:
   ```
   DATABASE_URL=postgres://user:pass@host/calzado
   FLASK_ENV=development
   ```
3. Instala python-dotenv y cargalo en tu app

**Nota**: Para desarrollo local normal, la app usa SQLite automaticamente si no hay `DATABASE_URL`.

---

## Contacto y Soporte

- Documentacion Render: https://render.com/docs
- Estado del servicio: https://status.render.com
- Documentacion PostgreSQL: https://www.postgresql.org/docs/

---

Desarrollado para el Sistema de Gestion de Calzado v2.0
