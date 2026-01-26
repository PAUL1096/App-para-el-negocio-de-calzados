# Guia de Despliegue en Render

Render es una plataforma moderna para desplegar aplicaciones web. El plan gratuito es suficiente para comenzar.

## Ventajas de Render

- Despliegue automatico desde GitHub
- SSL gratuito (HTTPS)
- Plan gratuito generoso
- Instalacion de dependencias sin problemas
- Facil de configurar

## Limitaciones del Plan Gratuito

- La app "duerme" despues de 15 min de inactividad
- Tarda ~30 segundos en "despertar" con la primera visita
- 750 horas gratis por mes (suficiente para 1 app 24/7)

---

## Paso 1: Crear cuenta en Render

1. Ve a [render.com](https://render.com)
2. Click en "Get Started for Free"
3. **Recomendado**: Registrate con tu cuenta de GitHub (facilita el despliegue)

---

## Paso 2: Conectar tu repositorio

1. En el Dashboard, click en **"New +"** > **"Web Service"**
2. Conecta tu cuenta de GitHub si no lo hiciste
3. Busca y selecciona: `App-para-el-negocio-de-calzados`
4. Click en **"Connect"**

---

## Paso 3: Configurar el servicio

Completa los campos:

| Campo | Valor |
|-------|-------|
| **Name** | `sistema-calzado` (o el nombre que prefieras) |
| **Region** | `Oregon (US West)` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python datos_iniciales.py` |
| **Start Command** | `gunicorn app_v2:app` |
| **Plan** | `Free` |

---

## Paso 4: Variables de entorno

En la seccion **"Environment Variables"**, agrega:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.11.0` |

**Opcional** (recomendado para seguridad):
| Key | Value |
|-----|-------|
| `SECRET_KEY` | Una clave aleatoria larga |

Para generar una clave segura, ejecuta en tu terminal:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Paso 5: Crear el servicio

1. Click en **"Create Web Service"**
2. Espera mientras Render:
   - Clona tu repositorio
   - Instala dependencias (~2-3 minutos)
   - Inicia la aplicacion

---

## Paso 6: Acceder a tu aplicacion

Una vez desplegado, tu app estara en:
```
https://sistema-calzado.onrender.com
```
(El nombre exacto depende del nombre que elegiste)

---

## Despliegue Automatico

Cada vez que hagas `git push` a la rama `main`, Render automaticamente:
1. Detecta los cambios
2. Reinstala dependencias si es necesario
3. Reinicia la aplicacion

---

## Solucion de Problemas

### La app tarda en cargar
Normal en plan gratuito. Despues de 15 min sin visitas, la app "duerme". La primera visita tarda ~30 seg en despertar.

### Error de build
1. Ve a tu servicio en Render
2. Click en **"Logs"**
3. Revisa los errores en la seccion de Build

### Error "No module named X"
Verifica que el modulo este en `requirements.txt`

### La base de datos se borra
**IMPORTANTE**: En Render gratuito, el sistema de archivos es efimero. La base de datos SQLite se borrara en cada redeploy.

**Soluciones**:
1. **Para pruebas**: Esta bien, los datos se recrean con `datos_iniciales.py`
2. **Para produccion real**: Usar una base de datos externa (PostgreSQL de Render, por ejemplo)

---

## Upgrade a Base de Datos Persistente (Opcional)

Para datos persistentes, considera:

### Opcion A: PostgreSQL en Render (Recomendado)
1. En Render, crea un nuevo **PostgreSQL** database
2. Modifica el codigo para usar PostgreSQL en vez de SQLite
3. Conecta usando la variable `DATABASE_URL`

### Opcion B: SQLite en un servicio de almacenamiento
- Usar servicios como Supabase, PlanetScale, o Railway

---

## Comandos Utiles

### Ver logs en tiempo real
En el dashboard de Render > Tu servicio > **Logs**

### Reiniciar manualmente
Dashboard > Tu servicio > **Manual Deploy** > **Deploy latest commit**

### Ver metricas
Dashboard > Tu servicio > **Metrics** (CPU, memoria, requests)

---

## Comparacion: Render vs PythonAnywhere

| Caracteristica | Render Free | PythonAnywhere Free |
|----------------|-------------|---------------------|
| Despliegue | Automatico desde Git | Manual |
| SSL (HTTPS) | Incluido | Incluido |
| "Sleep" | 15 min inactividad | 3 meses sin login |
| Build tiempo | Rapido | Lento (pandas) |
| Base de datos | Efimera (SQLite) | Persistente |
| Consola SSH | No | Si |

---

## Estructura del Proyecto para Render

```
App-para-el-negocio-de-calzados/
├── app_v2.py          # Aplicacion principal
├── config.py          # Configuracion
├── requirements.txt   # Dependencias (incluye gunicorn)
├── render.yaml        # Configuracion de Render (opcional)
├── datos_iniciales.py # Script de inicializacion
└── templates/         # Plantillas HTML
```

---

## Contacto y Soporte

- Documentacion Render: https://render.com/docs
- Estado del servicio: https://status.render.com

---

Desarrollado para el Sistema de Gestion de Calzado v2.0
